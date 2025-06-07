# src/extractors/formula_extractor.py

import os
import json
import logging
from typing import List, Dict, Optional
from pathlib import Path
from tqdm import tqdm
import concurrent.futures
from dataclasses import dataclass
import cv2
import numpy as np

from ..processors.pdf_processor import PDFProcessor, PageInfo
from .formula_recognizer import FormulaRecognizer, FormulaResult
from ..database.db_manager import DatabaseManager, FormulaData
from ..utils.logger import setup_logger

logger = logging.getLogger(__name__)

@dataclass
class ExtractionResult:
    """추출 결과를 담는 클래스"""
    document_id: str
    total_pages: int
    total_formulas: int
    successful_extractions: int
    failed_extractions: int
    formulas: List[FormulaResult]
    errors: List[Dict]

class FormulaExtractor:
    """통합 수식 추출기 클래스"""
    
    def __init__(self, config_path: str = "config/config.json"):
        """
        FormulaExtractor 초기화
        
        Args:
            config_path: 설정 파일 경로
        """
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        # 컴포넌트 초기화
        self.pdf_processor = PDFProcessor(config_path)
        self.formula_recognizer = FormulaRecognizer(config_path)
        self.db_manager = DatabaseManager(config_path)
        
        # 설정
        self.max_workers = int(os.getenv('MAX_WORKERS', '4'))
        self.batch_size = int(os.getenv('BATCH_SIZE', '32'))
        
        # ML 모델 기반 수식 검출기 (옵션)
        self.use_ml_detection = 'yolo' in self.config['formula_detection']['detection_models']
        self.detection_model = None
        
        if self.use_ml_detection:
            self._initialize_detection_model()
    
    def _initialize_detection_model(self):
        """ML 기반 수식 검출 모델 초기화"""
        # YOLO 또는 다른 객체 검출 모델 초기화
        # 여기서는 간단한 예시만 제공
        logger.info("ML detection model initialized (placeholder)")
    
    def extract_from_pdf(self, pdf_path: str, save_to_db: bool = True) -> ExtractionResult:
        """
        PDF 파일에서 수식 추출
        
        Args:
            pdf_path: PDF 파일 경로
            save_to_db: 데이터베이스 저장 여부
            
        Returns:
            추출 결과
        """
        document_id = Path(pdf_path).stem
        logger.info(f"Starting formula extraction from: {pdf_path}")
        
        # 데이터베이스 초기화
        if save_to_db:
            self.db_manager.initialize()
        
        # PDF 처리
        page_infos = self.pdf_processor.process_pdf(pdf_path)
        
        # 결과 초기화
        all_formulas = []
        errors = []
        successful_count = 0
        failed_count = 0
        
        # 페이지별 처리
        for page_info in tqdm(page_infos, desc="Processing pages"):
            try:
                # 수식 영역 검출
                formula_regions = self._detect_formula_regions(page_info)
                
                # 각 영역에서 수식 인식
                for region in formula_regions:
                    try:
                        # 수식 인식
                        formula_result = self.formula_recognizer.recognize_formula(
                            page_info.image_path,
                            region['bbox']
                        )
                        
                        # 검증
                        if self.formula_recognizer.validate_formula(formula_result):
                            # 컨텍스트 추출
                            context = self._extract_context(page_info, region['bbox'])
                            
                            # 데이터베이스 저장
                            if save_to_db and formula_result.latex:
                                formula_data = FormulaData(
                                    document_id=document_id,
                                    page_number=page_info.page_num,
                                    formula_latex=formula_result.latex,
                                    formula_python=formula_result.python_code or "",
                                    formula_image_path=self._save_formula_image(
                                        page_info.image_path,
                                        region['bbox'],
                                        document_id,
                                        page_info.page_num,
                                        len(all_formulas)
                                    ),
                                    variables=formula_result.variables or [],
                                    formula_type=self._classify_formula_type(formula_result.latex),
                                    confidence=formula_result.confidence,
                                    context_before=context.get('before', ''),
                                    context_after=context.get('after', ''),
                                    section_title=context.get('section', '')
                                )
                                
                                formula_id = self.db_manager.save_formula(formula_data)
                                formula_result.formula_id = formula_id
                            
                            all_formulas.append(formula_result)
                            successful_count += 1
                        else:
                            failed_count += 1
                            
                    except Exception as e:
                        logger.error(f"Error recognizing formula: {e}")
                        errors.append({
                            'page': page_info.page_num,
                            'bbox': region['bbox'],
                            'error': str(e)
                        })
                        failed_count += 1
                        
            except Exception as e:
                logger.error(f"Error processing page {page_info.page_num}: {e}")
                errors.append({
                    'page': page_info.page_num,
                    'error': str(e)
                })
        
        # 결과 생성
        result = ExtractionResult(
            document_id=document_id,
            total_pages=len(page_infos),
            total_formulas=len(all_formulas),
            successful_extractions=successful_count,
            failed_extractions=failed_count,
            formulas=all_formulas,
            errors=errors
        )
        
        logger.info(f"Extraction completed: {successful_count} formulas extracted")
        
        return result
    
    def _detect_formula_regions(self, page_info: PageInfo) -> List[Dict]:
        """
        페이지에서 수식 영역 검출
        
        Args:
            page_info: 페이지 정보
            
        Returns:
            수식 영역 리스트
        """
        regions = []
        
        # 1. 규칙 기반 검출
        rule_based_regions = self.pdf_processor.extract_formula_regions(page_info)
        regions.extend(rule_based_regions)
        
        # 2. ML 기반 검출 (옵션)
        if self.use_ml_detection and self.detection_model:
            ml_regions = self._detect_with_ml(page_info.image_path)
            regions.extend(ml_regions)
        
        # 3. 영역 병합
        merged_regions = self.pdf_processor.merge_regions(
            regions, 
            threshold=self.config['formula_detection']['merge_threshold']
        )
        
        return merged_regions
    
    def _detect_with_ml(self, image_path: str) -> List[Dict]:
        """ML 모델을 사용한 수식 영역 검출"""
        # 여기서는 간단한 예시만 제공
        # 실제로는 YOLO, Detectron2 등을 사용
        return []
    
    def _extract_context(self, page_info: PageInfo, bbox: List[float]) -> Dict[str, str]:
        """
        수식 주변 컨텍스트 추출
        
        Args:
            page_info: 페이지 정보
            bbox: 수식 영역 좌표
            
        Returns:
            컨텍스트 정보
        """
        context = {
            'before': '',
            'after': '',
            'section': ''
        }
        
        # bbox 위치 찾기
        formula_y = (bbox[1] + bbox[3]) / 2
        
        # 이전/이후 텍스트 찾기
        for block in page_info.blocks:
            if block['type'] == 'text':
                block_y = (block['bbox'][1] + block['bbox'][3]) / 2
                
                # 수식 위의 텍스트
                if block_y < formula_y - 20:
                    text = self._extract_block_text(block)
                    if text and len(text) > 10:
                        context['before'] = text[-200:]  # 마지막 200자
                
                # 수식 아래의 텍스트
                elif block_y > formula_y + 20:
                    text = self._extract_block_text(block)
                    if text and len(text) > 10:
                        context['after'] = text[:200]  # 처음 200자
                        break
        
        # 섹션 제목 찾기 (간단한 휴리스틱)
        for block in page_info.blocks:
            if block['type'] == 'text':
                text = self._extract_block_text(block)
                if text and self._is_section_title(text, block):
                    context['section'] = text
                    break
        
        return context
    
    def _extract_block_text(self, block: Dict) -> str:
        """블록에서 텍스트 추출"""
        text = ""
        for line in block.get('lines', []):
            for span in line.get('spans', []):
                text += span.get('text', '')
            text += " "
        return text.strip()
    
    def _is_section_title(self, text: str, block: Dict) -> bool:
        """섹션 제목인지 판단"""
        # 간단한 휴리스틱
        if len(text) > 100:
            return False
        
        # 폰트 크기가 큰 경우
        for line in block.get('lines', []):
            for span in line.get('spans', []):
                if span.get('size', 0) > 12:
                    return True
        
        # 번호로 시작하는 경우
        import re
        if re.match(r'^\d+\.', text):
            return True
        
        return False
    
    def _save_formula_image(self, page_image_path: str, bbox: List[float],
                           document_id: str, page_num: int, formula_idx: int) -> str:
        """수식 이미지 저장"""
        # 출력 디렉토리
        output_dir = Path("data/output") / document_id / "formulas"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 이미지 로드 및 영역 추출
        image = cv2.imread(page_image_path)
        x1, y1, x2, y2 = map(int, bbox)
        
        # 패딩 추가
        padding = 10
        x1 = max(0, x1 - padding)
        y1 = max(0, y1 - padding)
        x2 = min(image.shape[1], x2 + padding)
        y2 = min(image.shape[0], y2 + padding)
        
        # 수식 이미지 추출
        formula_image = image[y1:y2, x1:x2]
        
        # 파일명 생성
        filename = f"formula_p{page_num:03d}_f{formula_idx:03d}.png"
        filepath = output_dir / filename
        
        # 저장
        cv2.imwrite(str(filepath), formula_image)
        
        return str(filepath)
    
    def _classify_formula_type(self, latex: str) -> str:
        """수식 타입 분류"""
        # 보험 수식 패턴
        insurance_patterns = {
            'premium': r'P\s*=',
            'reserve': r'V\s*=',
            'coi': r'COI\s*=',
            'annuity': r'[aä]\s*=',
            'present_value': r'[ND]\s*=',
            'mortality': r'q[_x]?\s*='
        }
        
        import re
        for type_name, pattern in insurance_patterns.items():
            if re.search(pattern, latex):
                return type_name
        
        # 일반 수식 타입
        if '\\frac' in latex or '/' in latex:
            return 'fraction'
        elif '\\sum' in latex or 'Σ' in latex:
            return 'summation'
        elif '\\int' in latex or '∫' in latex:
            return 'integral'
        else:
            return 'general'
    
    def generate_report(self, result: ExtractionResult, output_path: str = None):
        """추출 결과 리포트 생성"""
        if output_path is None:
            output_path = f"data/output/{result.document_id}_report.json"
        
        report = {
            'document_id': result.document_id,
            'summary': {
                'total_pages': result.total_pages,
                'total_formulas': result.total_formulas,
                'successful_extractions': result.successful_extractions,
                'failed_extractions': result.failed_extractions,
                'success_rate': result.successful_extractions / max(1, result.successful_extractions + result.failed_extractions)
            },
            'formulas': [
                {
                    'latex': f.latex,
                    'confidence': f.confidence,
                    'type': self._classify_formula_type(f.latex),
                    'variables': f.variables,
                    'has_python_code': f.python_code is not None
                }
                for f in result.formulas
            ],
            'errors': result.errors
        }
        
        # 통계 추가
        if hasattr(self.db_manager, 'get_statistics'):
            report['database_statistics'] = self.db_manager.get_statistics()
        
        # 저장
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Report saved to: {output_path}")