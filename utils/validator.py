"""
문서 검증 유틸리티
"""

import logging
from pathlib import Path
from typing import Dict, Any, List
from typing import Dict, Any, List, TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Dict, Any, List, TYPE_CHECKING

if TYPE_CHECKING:
    from core.result import AnalysisResult

logger = logging.getLogger(__name__)

class DocumentValidator:
    """문서 검증기"""
    
    def __init__(self, config):
        self.config = config
        
        # 검증 규칙
        self.min_text_length = 10
        self.max_page_errors = 5
        self.min_extraction_rate = 0.1  # 최소 10% 페이지에서 내용 추출
    
    def validate_pdf(self, pdf_path: Path) -> Dict[str, Any]:
        """PDF 파일 검증"""
        result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # 파일 존재 확인
        if not pdf_path.exists():
            result['valid'] = False
            result['errors'].append(f"파일이 존재하지 않습니다: {pdf_path}")
            return result
        
        # 파일 크기 확인
        file_size = pdf_path.stat().st_size
        if file_size == 0:
            result['valid'] = False
            result['errors'].append("빈 파일입니다")
        elif file_size > 500 * 1024 * 1024:  # 500MB
            result['warnings'].append(f"파일 크기가 큽니다: {file_size / 1024 / 1024:.1f}MB")
        
        # 확장자 확인
        if pdf_path.suffix.lower() != '.pdf':
            result['valid'] = False
            result['errors'].append(f"PDF 파일이 아닙니다: {pdf_path.suffix}")
        
        return result
    
    def validate_result(self, result: 'AnalysisResult') -> Dict[str, Any]:
        """분석 결과 검증"""
        validation = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'statistics': {}
        }
        
        # 기본 검증
        if not result.pages:
            validation['errors'].append("분석된 페이지가 없습니다")
            validation['valid'] = False
            return validation
        
        # 페이지별 검증
        empty_pages = 0
        error_pages = 0
        total_text_length = 0
        
        for page in result.pages:
            # 빈 페이지 확인
            if len(page.text) < self.min_text_length:
                empty_pages += 1
            
            # 오류 페이지 확인
            if page.errors:
                error_pages += 1
            
            total_text_length += len(page.text)
        
        # 통계
        validation['statistics'] = {
            'total_pages': result.total_pages,
            'empty_pages': empty_pages,
            'error_pages': error_pages,
            'avg_text_length': total_text_length / result.total_pages if result.total_pages > 0 else 0,
            'extraction_rate': (result.total_pages - empty_pages) / result.total_pages if result.total_pages > 0 else 0
        }
        
        # 경고 생성
        if empty_pages > result.total_pages * 0.5:
            validation['warnings'].append(f"빈 페이지가 너무 많습니다: {empty_pages}/{result.total_pages}")
        
        if error_pages > self.max_page_errors:
            validation['warnings'].append(f"오류 페이지가 많습니다: {error_pages}")
        
        if validation['statistics']['extraction_rate'] < self.min_extraction_rate:
            validation['warnings'].append(f"텍스트 추출률이 낮습니다: {validation['statistics']['extraction_rate']:.1%}")
        
        # 테이블 검증
        if result.tables:
            invalid_tables = sum(1 for t in result.tables if not t.get('data'))
            if invalid_tables > 0:
                validation['warnings'].append(f"데이터가 없는 테이블: {invalid_tables}개")
        
        # 수식 검증
        if result.formulas:
            invalid_formulas = sum(1 for f in result.formulas if not f.get('latex'))
            if invalid_formulas > 0:
                validation['warnings'].append(f"변환되지 않은 수식: {invalid_formulas}개")
        
        return validation
    
    def validate_extraction_quality(self, text: str, expected_language: str = 'ko') -> Dict[str, Any]:
        """추출 품질 검증"""
        import re
        
        quality = {
            'score': 1.0,
            'issues': []
        }
        
        # 깨진 문자 검출
        broken_chars = len(re.findall(r'[�□?]{3,}', text))
        if broken_chars > 0:
            quality['score'] *= 0.8
            quality['issues'].append(f"깨진 문자 감지: {broken_chars}개 블록")
        
        # 언어 비율 확인
        if expected_language == 'ko':
            korean_chars = len(re.findall(r'[가-힣]', text))
            total_chars = len(text)
            korean_ratio = korean_chars / total_chars if total_chars > 0 else 0
            
            if korean_ratio < 0.3 and total_chars > 100:
                quality['score'] *= 0.9
                quality['issues'].append(f"한글 비율이 낮음: {korean_ratio:.1%}")
        
        # 반복 패턴 검출
        repeated_patterns = re.findall(r'(.{10,}){3,}', text)
        if repeated_patterns:
            quality['score'] *= 0.7
            quality['issues'].append("반복 패턴 감지")
        
        return quality
