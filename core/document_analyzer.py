"""
문서 분석기 - 메인 처리 클래스
"""

import logging
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime

from core.config import Config, OutputFormat
from core.result import AnalysisResult, PageResult
# 선택적 import (없는 모듈은 None으로 처리)
try:
    from processors.pdf_processor import PDFProcessor
except ImportError:
    print("⚠️  PDFProcessor를 import할 수 없습니다.")
    from processors.pdf_processor_fallback import PDFProcessor  # 폴백

try:
    from processors.ocr_processor import OCRProcessor
except ImportError:
    print("⚠️  OCRProcessor를 import할 수 없습니다.")
    OCRProcessor = None

try:
    from processors.layout_analyzer import LayoutAnalyzer
except ImportError:
    print("⚠️  LayoutAnalyzer를 import할 수 없습니다.")
    LayoutAnalyzer = None

try:
    from processors.korean_text_processor import KoreanTextProcessor
except ImportError:
    print("⚠️  KoreanTextProcessor를 import할 수 없습니다.")
    KoreanTextProcessor = None

try:
    from processors.formula_processor import FormulaProcessor
except ImportError:
    print("⚠️  FormulaProcessor를 import할 수 없습니다.")
    FormulaProcessor = None

try:
    from processors.formula_extractor import FormulaExtractor
except ImportError:
    print("⚠️  FormulaExtractor를 import할 수 없습니다.")
    FormulaExtractor = None

try:
    from processors.table_extractor import TableExtractor
except ImportError:
    print("⚠️  TableExtractor를 import할 수 없습니다.")
    TableExtractor = None

try:
    from processors.financial_term_processor import FinancialTermProcessor
except ImportError:
    print("⚠️  FinancialTermProcessor를 import할 수 없습니다.")
    FinancialTermProcessor = None

try:
    from processors.csv_exporter import CSVExporter
except ImportError:
    print("⚠️  CSVExporter를 import할 수 없습니다.")
    CSVExporter = None

try:
    from utils.validator import DocumentValidator
except ImportError:
    print("⚠️  DocumentValidator를 import할 수 없습니다.")
    DocumentValidator = None

logger = logging.getLogger(__name__)

class DocumentAnalyzer:
    """문서 분석 메인 클래스"""
    
    def __init__(self, config: Config):
        self.config = config
        
        # 프로세서 초기화 (사용 가능한 것만)
        self.pdf_processor = PDFProcessor(config) if PDFProcessor else None
        self.ocr_processor = OCRProcessor(config) if OCRProcessor else None
        self.layout_analyzer = LayoutAnalyzer(config) if LayoutAnalyzer else None
        self.korean_processor = KoreanTextProcessor(config) if KoreanTextProcessor else None
        self.formula_processor = FormulaProcessor(config) if FormulaProcessor else None
        self.formula_extractor = FormulaExtractor(config) if FormulaExtractor else None
        self.table_extractor = TableExtractor(config) if TableExtractor else None
        self.term_processor = FinancialTermProcessor(config) if FinancialTermProcessor else None
        self.csv_exporter = CSVExporter(config) if CSVExporter else None
        self.validator = DocumentValidator(config) if DocumentValidator else None
        
        logger.info("문서 분석기 초기화 완료")
    
    def analyze_document(self, pdf_path: Path) -> AnalysisResult:
        """단일 문서 분석"""
        start_time = time.time()
        
        # 문서 ID 생성
        document_id = pdf_path.stem
        
        # 결과 객체 생성
        result = AnalysisResult(
            document_id=document_id,
            file_path=pdf_path,
            start_time=datetime.now()
        )
        
        try:
            logger.info(f"문서 분석 시작: {pdf_path.name}")
            
            # 1. PDF 전처리
            logger.info("PDF 전처리 중...")
            pdf_result = self.pdf_processor.process_pdf(pdf_path)
            
            if not pdf_result.success:
                raise Exception(f"PDF 처리 실패: {pdf_result.error_message}")
            
            result.total_pages = len(pdf_result.page_images)
            result.metadata.update(pdf_result.metadata)
            
            # 2. 페이지별 분석
            for page_num, page_image in enumerate(pdf_result.page_images):
                logger.info(f"페이지 {page_num + 1}/{result.total_pages} 분석 중...")
                
                page_result = self._analyze_page(page_image, page_num + 1)
                result.add_page_result(page_result)
                
                # 진행 상황 로깅
                if (page_num + 1) % 10 == 0:
                    logger.info(f"진행률: {(page_num + 1) / result.total_pages * 100:.1f}%")
            
            # 3. 후처리
            logger.info("후처리 중...")
            self._post_process_results(result)
            
            # 4. 결과 내보내기
            logger.info("결과 저장 중...")
            self._export_results(result)
            
            result.success = True
            logger.info(f"문서 분석 완료: {time.time() - start_time:.2f}초")
            
        except Exception as e:
            logger.error(f"문서 분석 실패: {e}")
            result.success = False
            result.error_message = str(e)
        
        finally:
            result.finalize()
        
        return result
    
    def _analyze_page(self, page_image_path: Path, page_num: int) -> PageResult:
        """단일 페이지 분석"""
        page_start_time = time.time()
        
        page_result = PageResult(page_num=page_num)
        
        try:
            # 1. 레이아웃 분석
            if self.config.layout_model:
                layout_regions = self.layout_analyzer.analyze_layout(page_image_path)
                page_result.layout_regions = layout_regions
            else:
                layout_regions = []
            
            # 2. 텍스트 추출 (OCR)
            if layout_regions:
                text = self.ocr_processor.extract_text_with_layout(
                    page_image_path, layout_regions
                )
            else:
                text = self.ocr_processor.extract_text(page_image_path)
            
            page_result.text = text
            
            # 3. 한글 텍스트 처리
            if self.config.korean_nlp_enabled and text:
                korean_analysis = self.korean_processor.process_korean_text(text)
                page_result.korean_analysis = korean_analysis
            
            # 4. 테이블 추출
            if self.config.extract_tables:
                tables = self.table_extractor.extract_tables(page_image_path)
                page_result.tables = tables
            
            # 5. 수식 추출
            if self.config.extract_formulas:
                # 이미지에서 수식 추출
                formulas = self.formula_extractor.extract_formulas(
                    page_image_path, layout_regions
                )
                
                # 한글 텍스트에서 수식 추출
                if self.config.detect_korean_formulas and text:
                    korean_formulas = self.formula_processor.extract_korean_formulas(
                        text, page_result.korean_analysis
                    )
                    formulas.extend(korean_formulas)
                
                page_result.formulas = formulas
            
            # 6. 금융 용어 추출
            if self.config.extract_financial_terms and text:
                terms = self.term_processor.extract_terms(text)
                page_result.financial_terms = terms
            
        except Exception as e:
            logger.error(f"페이지 {page_num} 분석 실패: {e}")
            page_result.errors.append(str(e))
        
        page_result.processing_time = time.time() - page_start_time
        
        return page_result
    
    def _post_process_results(self, result: AnalysisResult):
        """결과 후처리"""
        # 1. 테이블 후처리
        if result.tables:
            result.tables = self.table_extractor.post_process_tables(result.tables)
        
        # 2. 금융 용어 정규화
        if result.financial_terms:
            # 중복 제거
            unique_terms = {}
            for term in result.financial_terms:
                key = (term['text'], term['page_num'])
                if key not in unique_terms:
                    unique_terms[key] = term
            result.financial_terms = list(unique_terms.values())
            
            # 카테고리별 정렬
            result.financial_terms.sort(key=lambda x: (x.get('category', ''), x.get('page_num', 0)))
        
        # 3. 검증
        validation_result = self.validator.validate_result(result)
        if validation_result['warnings']:
            result.warnings.extend(validation_result['warnings'])
    
    def _export_results(self, result: AnalysisResult):
        """결과 내보내기"""
        from utils.file_utils import FileUtils
        import pandas as pd
        
        # 1. CSV 내보내기
        if OutputFormat.CSV in self.config.output_formats:
            csv_files = self.csv_exporter.export_to_csv(result)
            result.output_files.update(csv_files)
        
        # 2. JSON 내보내기
        if OutputFormat.JSON in self.config.output_formats:
            json_path = self.config.get_output_path(
                result.document_id, "individual", "analysis_result.json"
            )
            json_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 전체 데이터 저장
            export_data = {
                'metadata': result.metadata,
                'summary': result.to_dict(),
                'pages': [
                    {
                        'page_num': page.page_num,
                        'text': page.text,
                        'tables': page.tables,
                        'formulas': page.formulas,
                        'financial_terms': page.financial_terms,
                        'korean_analysis': page.korean_analysis
                    }
                    for page in result.pages
                ],
                'all_tables': result.tables,
                'all_formulas': result.formulas,
                'all_financial_terms': result.financial_terms
            }
            
            FileUtils.save_json(export_data, json_path)
            result.output_files['json'] = json_path
        
        # 3. Excel 내보내기
        if OutputFormat.EXCEL in self.config.output_formats:
            excel_path = self.config.get_output_path(
                result.document_id, "individual", "analysis_result.xlsx"
            )
            excel_path.parent.mkdir(parents=True, exist_ok=True)
            
            with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                # 요약 시트
                summary_df = pd.DataFrame([result.to_dict()['summary']])
                summary_df.to_excel(writer, sheet_name='요약', index=False)
                
                # 페이지별 텍스트
                if result.page_texts:
                    text_df = pd.DataFrame({
                        '페이지': range(1, len(result.page_texts) + 1),
                        '텍스트': result.page_texts
                    })
                    text_df.to_excel(writer, sheet_name='텍스트', index=False)
                
                # 테이블
                if result.tables:
                    tables_df = pd.DataFrame(result.tables)
                    tables_df.to_excel(writer, sheet_name='테이블', index=False)
                
                # 수식
                if result.formulas:
                    formulas_df = pd.DataFrame(result.formulas)
                    formulas_df.to_excel(writer, sheet_name='수식', index=False)
                
                # 금융 용어
                if result.financial_terms:
                    terms_df = pd.DataFrame(result.financial_terms)
                    terms_df.to_excel(writer, sheet_name='금융용어', index=False)
            
            result.output_files['excel'] = excel_path
        
        # 4. HTML 내보내기
        if OutputFormat.HTML in self.config.output_formats:
            html_path = self.config.get_output_path(
                result.document_id, "individual", "analysis_result.html"
            )
            html_path.parent.mkdir(parents=True, exist_ok=True)
            
            # HTML 생성 (간단한 버전)
            html_content = self._generate_html_report(result)
            
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            result.output_files['html'] = html_path
    
    def _generate_html_report(self, result: AnalysisResult) -> str:
        """HTML 보고서 생성"""
        html = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>{result.document_id} - 분석 결과</title>
    <style>
        body {{ font-family: 'Malgun Gothic', sans-serif; margin: 20px; }}
        .summary {{ background: #f0f0f0; padding: 15px; border-radius: 5px; }}
        table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
        .section {{ margin: 20px 0; }}
    </style>
</head>
<body>
    <h1>{result.document_id} 분석 결과</h1>
    
    <div class="summary">
        <h2>요약</h2>
        <p>총 페이지: {result.total_pages}</p>
        <p>추출된 텍스트: {sum(len(t) for t in result.page_texts):,} 문자</p>
        <p>추출된 테이블: {len(result.tables)}개</p>
        <p>추출된 수식: {len(result.formulas)}개</p>
        <p>추출된 금융 용어: {len(result.financial_terms)}개</p>
        <p>처리 시간: {result.processing_time:.2f}초</p>
    </div>
    
    <div class="section">
        <h2>페이지별 요약</h2>
        <table>
            <tr>
                <th>페이지</th>
                <th>텍스트 길이</th>
                <th>테이블</th>
                <th>수식</th>
                <th>금융 용어</th>
            </tr>
"""
        
        for page in result.pages:
            html += f"""
            <tr>
                <td>{page.page_num}</td>
                <td>{len(page.text):,}</td>
                <td>{len(page.tables)}</td>
                <td>{len(page.formulas)}</td>
                <td>{len(page.financial_terms)}</td>
            </tr>
"""
        
        html += """
        </table>
    </div>
</body>
</html>
"""
        return html
    
    def analyze_batch(self, pdf_files: List[Path]) -> Dict[str, AnalysisResult]:
        """배치 문서 분석"""
        results = {}
        total_files = len(pdf_files)
        
        logger.info(f"배치 분석 시작: {total_files}개 파일")
        
        if self.config.max_workers > 1:
            # 멀티프로세싱
            with ProcessPoolExecutor(max_workers=self.config.max_workers) as executor:
                future_to_file = {
                    executor.submit(self.analyze_document, pdf_file): pdf_file 
                    for pdf_file in pdf_files
                }
                
                for i, future in enumerate(as_completed(future_to_file)):
                    pdf_file = future_to_file[future]
                    try:
                        result = future.result()
                        results[result.document_id] = result
                        logger.info(f"완료: {i+1}/{total_files} - {pdf_file.name}")
                    except Exception as e:
                        logger.error(f"실패: {pdf_file.name} - {e}")
                        # 실패한 결과도 기록
                        result = AnalysisResult(
                            document_id=pdf_file.stem,
                            file_path=pdf_file,
                            success=False,
                            error_message=str(e)
                        )
                        results[result.document_id] = result
        else:
            # 순차 처리
            for i, pdf_file in enumerate(pdf_files):
                logger.info(f"처리 중: {i+1}/{total_files} - {pdf_file.name}")
                result = self.analyze_document(pdf_file)
                results[result.document_id] = result
        
        logger.info(f"배치 분석 완료: 성공 {sum(1 for r in results.values() if r.success)}/{total_files}")
        
        return results
