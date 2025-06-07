# src/processors/pdf_processor.py

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import fitz  # PyMuPDF
import numpy as np
from PIL import Image
from dataclasses import dataclass
import tempfile

logger = logging.getLogger(__name__)

@dataclass
class PageInfo:
    """페이지 정보를 담는 데이터 클래스"""
    page_num: int
    width: float
    height: float
    image_path: str
    text_content: str
    blocks: List[Dict]

class PDFProcessor:
    """PDF 파일을 처리하고 이미지로 변환하는 클래스"""
    
    def __init__(self, config_path: str = "config/config.json"):
        """
        PDFProcessor 초기화
        
        Args:
            config_path: 설정 파일 경로
        """
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.dpi = self.config['pdf_processing']['dpi']
        self.image_format = self.config['pdf_processing']['image_format']
        self.temp_dir = Path(self.config['pdf_processing']['temp_dir'])
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
    def process_pdf(self, pdf_path: str, output_dir: str = None) -> List[PageInfo]:
        """
        PDF 파일을 처리하여 페이지별 정보 추출
        
        Args:
            pdf_path: PDF 파일 경로
            output_dir: 출력 디렉토리 (None이면 temp_dir 사용)
            
        Returns:
            페이지별 정보 리스트
        """
        if output_dir is None:
            output_dir = self.temp_dir
        else:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
        
        page_infos = []
        
        try:
            # PDF 문서 열기
            doc = fitz.open(pdf_path)
            pdf_name = Path(pdf_path).stem
            
            logger.info(f"Processing PDF: {pdf_path}, Total pages: {len(doc)}")
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # 페이지를 이미지로 변환
                image_path = self._page_to_image(page, page_num, pdf_name, output_dir)
                
                # 텍스트 및 블록 정보 추출
                text_content = page.get_text()
                blocks = self._extract_blocks(page)
                
                # 페이지 정보 생성
                page_info = PageInfo(
                    page_num=page_num,
                    width=page.rect.width,
                    height=page.rect.height,
                    image_path=str(image_path),
                    text_content=text_content,
                    blocks=blocks
                )
                
                page_infos.append(page_info)
                logger.debug(f"Processed page {page_num + 1}/{len(doc)}")
            
            doc.close()
            logger.info(f"Successfully processed {len(page_infos)} pages")
            
        except Exception as e:
            logger.error(f"Error processing PDF: {e}")
            raise
        
        return page_infos
    
    def _page_to_image(self, page: fitz.Page, page_num: int, 
                      pdf_name: str, output_dir: Path) -> Path:
        """
        PDF 페이지를 이미지로 변환
        
        Args:
            page: PyMuPDF 페이지 객체
            page_num: 페이지 번호
            pdf_name: PDF 파일명
            output_dir: 출력 디렉토리
            
        Returns:
            생성된 이미지 파일 경로
        """
        # 렌더링 매트릭스 생성
        zoom = self.dpi / 72.0  # 72 DPI가 기본값
        mat = fitz.Matrix(zoom, zoom)
        
        # 페이지를 픽스맵으로 렌더링
        pix = page.get_pixmap(matrix=mat, alpha=False)
        
        # 이미지 파일 경로
        image_filename = f"{pdf_name}_page_{page_num + 1:03d}.{self.image_format.lower()}"
        image_path = output_dir / image_filename
        
        # 이미지 저장
        if self.image_format.upper() == "PNG":
            pix.save(str(image_path))
        else:
            # PIL을 사용하여 다른 형식으로 변환
            img_data = pix.tobytes("ppm")
            img = Image.open(io.BytesIO(img_data))
            img.save(str(image_path), self.image_format)
        
        return image_path
    
    def _extract_blocks(self, page: fitz.Page) -> List[Dict]:
        """
        페이지에서 텍스트 블록 정보 추출
        
        Args:
            page: PyMuPDF 페이지 객체
            
        Returns:
            블록 정보 리스트
        """
        blocks = []
        
        # 텍스트 블록 추출
        text_blocks = page.get_text("dict")
        
        for block in text_blocks.get("blocks", []):
            if block.get("type") == 0:  # 텍스트 블록
                block_info = {
                    "type": "text",
                    "bbox": list(block.get("bbox", [])),
                    "lines": []
                }
                
                for line in block.get("lines", []):
                    line_info = {
                        "bbox": list(line.get("bbox", [])),
                        "spans": []
                    }
                    
                    for span in line.get("spans", []):
                        span_info = {
                            "text": span.get("text", ""),
                            "font": span.get("font", ""),
                            "size": span.get("size", 0),
                            "flags": span.get("flags", 0),
                            "bbox": list(span.get("bbox", []))
                        }
                        line_info["spans"].append(span_info)
                    
                    block_info["lines"].append(line_info)
                
                blocks.append(block_info)
            
            elif block.get("type") == 1:  # 이미지 블록
                block_info = {
                    "type": "image",
                    "bbox": list(block.get("bbox", [])),
                    "width": block.get("width", 0),
                    "height": block.get("height", 0)
                }
                blocks.append(block_info)
        
        return blocks
    
    def extract_formula_regions(self, page_info: PageInfo) -> List[Dict]:
        """
        페이지에서 수식 가능 영역 추출 (규칙 기반)
        
        Args:
            page_info: 페이지 정보
            
        Returns:
            수식 가능 영역 리스트
        """
        formula_regions = []
        
        # 수식 관련 키워드
        formula_keywords = [
            '=', '∑', '∏', '∫', '√', '∞', 'Σ', 'Π',
            'sin', 'cos', 'tan', 'log', 'ln', 'exp',
            'lim', 'max', 'min', 'sup', 'inf',
            '×', '÷', '±', '≤', '≥', '≠', '≈',
            'α', 'β', 'γ', 'δ', 'θ', 'λ', 'μ', 'σ', 'ω'
        ]
        
        # 보험 관련 수식 키워드
        insurance_keywords = [
            'P', 'V', 'M', 'N', 'D', 'q', 'i',  # 보험 기호
            '보험료', '준비금', '현가', '위험률', '이율',
            'COI', 'MD', '월대체보험료'
        ]
        
        all_keywords = formula_keywords + insurance_keywords
        
        for block in page_info.blocks:
            if block["type"] == "text":
                block_text = ""
                
                # 블록의 모든 텍스트 수집
                for line in block["lines"]:
                    for span in line["spans"]:
                        block_text += span["text"]
                
                # 수식 키워드 확인
                has_formula = any(keyword in block_text for keyword in all_keywords)
                
                # 수식 패턴 확인 (정규식 사용 가능)
                import re
                formula_patterns = [
                    r'\b[A-Za-z]+_\{?[0-9a-zA-Z]+\}?',  # 첨자 패턴
                    r'\b[A-Za-z]+\^?\{?[0-9a-zA-Z]+\}?',  # 지수 패턴
                    r'\\frac\{[^}]+\}\{[^}]+\}',  # 분수 패턴
                    r'\([^)]*[+\-*/][^)]*\)',  # 괄호 내 연산
                ]
                
                for pattern in formula_patterns:
                    if re.search(pattern, block_text):
                        has_formula = True
                        break
                
                if has_formula:
                    formula_regions.append({
                        "bbox": block["bbox"],
                        "text": block_text,
                        "confidence": 0.8,  # 규칙 기반 신뢰도
                        "type": "rule_based"
                    })
        
        return formula_regions
    
    def merge_regions(self, regions: List[Dict], threshold: float = 0.1) -> List[Dict]:
        """
        겹치거나 인접한 영역 병합
        
        Args:
            regions: 영역 리스트
            threshold: 병합 임계값
            
        Returns:
            병합된 영역 리스트
        """
        if not regions:
            return []
        
        # bbox 기준으로 정렬
        sorted_regions = sorted(regions, key=lambda r: (r["bbox"][1], r["bbox"][0]))
        merged = []
        
        current = sorted_regions[0].copy()
        
        for region in sorted_regions[1:]:
            # 영역 간 거리 계산
            distance = self._calculate_distance(current["bbox"], region["bbox"])
            
            if distance < threshold * min(
                current["bbox"][3] - current["bbox"][1],
                region["bbox"][3] - region["bbox"][1]
            ):
                # 병합
                current["bbox"] = [
                    min(current["bbox"][0], region["bbox"][0]),
                    min(current["bbox"][1], region["bbox"][1]),
                    max(current["bbox"][2], region["bbox"][2]),
                    max(current["bbox"][3], region["bbox"][3])
                ]
                current["confidence"] = max(current["confidence"], region["confidence"])
                if "text" in current and "text" in region:
                    current["text"] += " " + region["text"]
            else:
                merged.append(current)
                current = region.copy()
        
        merged.append(current)
        return merged
    
    def _calculate_distance(self, bbox1: List[float], bbox2: List[float]) -> float:
        """두 bbox 간의 최소 거리 계산"""
        x1_min, y1_min, x1_max, y1_max = bbox1
        x2_min, y2_min, x2_max, y2_max = bbox2
        
        # 수평 거리
        if x1_max < x2_min:
            dx = x2_min - x1_max
        elif x2_max < x1_min:
            dx = x1_min - x2_max
        else:
            dx = 0
        
        # 수직 거리
        if y1_max < y2_min:
            dy = y2_min - y1_max
        elif y2_max < y1_min:
            dy = y1_min - y2_max
        else:
            dy = 0
        
        return (dx ** 2 + dy ** 2) ** 0.5