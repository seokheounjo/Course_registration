# processors/formula_processor.py
"""
한글 수식 처리 모듈
"""

import logging
import re
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

class FormulaProcessor:
    """한글 수식 처리기"""
    
    def __init__(self, config):
        self.config = config
        
        # 한글 수식 패턴 로드
        self.patterns = config.korean_formula_patterns
        
        # 한글 숫자 변환 테이블
        self.korean_numbers = self.patterns.get("number_patterns", {}).get("korean_numbers", {})
        
        # 수학 용어 변환 테이블
        self.math_terms = self.patterns.get("mathematical_terms", {}).get("korean_to_latex", {})
        
        # 금융 용어 변환 테이블
        self.financial_terms = self.patterns.get("financial_terms", {}).get("korean_to_symbol", {})
    
    def extract_korean_formulas(self, text: str, 
                              korean_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """한글 텍스트에서 수식 추출"""
        formulas = []
        
        # 수식 컨텍스트 찾기
        formula_contexts = self._find_formula_contexts(text)
        
        for context in formula_contexts:
            # 한글 수식을 LaTeX로 변환
            latex_formula = self._convert_to_latex(context['text'])
            
            if latex_formula:
                formula_info = {
                    "original_text": context['text'],
                    "latex": latex_formula,
                    "type": self._classify_formula(latex_formula),
                    "position": context['position'],
                    "confidence": context['confidence'],
                    "is_korean": True,
                    "financial_context": self._check_financial_context(context['text'])
                }
                
                formulas.append(formula_info)
        
        return formulas
    
    def _find_formula_contexts(self, text: str) -> List[Dict[str, Any]]:
        """수식 컨텍스트 찾기"""
        contexts = []
        
        # 수식 시작 표시자
        formula_indicators = self.patterns.get("contextual_indicators", {}).get("formula_start", [])
        
        # 각 표시자로 수식 찾기
        for indicator in formula_indicators:
            pattern = rf'{indicator}\s*([^.!?]+)[.!?]'
            matches = re.finditer(pattern, text)
            
            for match in matches:
                formula_text = match.group(1).strip()
                
                # 수식 특징 확인
                if self._has_formula_characteristics(formula_text):
                    contexts.append({
                        'text': formula_text,
                        'position': (match.start(1), match.end(1)),
                        'confidence': 0.8,
                        'indicator': indicator
                    })
        
        # 패턴 기반 수식 찾기
        pattern_contexts = self._find_pattern_based_formulas(text)
        contexts.extend(pattern_contexts)
        
        # 중복 제거
        contexts = self._remove_overlapping_contexts(contexts)
        
        return contexts
    
    def _has_formula_characteristics(self, text: str) -> bool:
        """텍스트가 수식 특징을 가지는지 확인"""
        # 수학 기호나 용어 포함 여부
        math_indicators = ['=', '+', '-', '×', '÷', '/', '%'] + list(self.math_terms.keys())
        
        for indicator in math_indicators:
            if indicator in text:
                return True
        
        # 숫자 포함 여부
        if re.search(r'\d', text):
            return True
        
        # 한글 숫자 포함 여부
        for korean_num in self.korean_numbers:
            if korean_num in text:
                return True
        
        return False
    
    def _find_pattern_based_formulas(self, text: str) -> List[Dict[str, Any]]:
        """패턴 기반 수식 찾기"""
        contexts = []
        
        # 정의된 수식 패턴들
        formula_patterns = self.patterns.get("formula_patterns", {})
        
        for formula_name, pattern_info in formula_patterns.items():
            patterns = pattern_info.get("patterns", [])
            
            for pattern in patterns:
                try:
                    matches = re.finditer(pattern, text, re.IGNORECASE)
                    
                    for match in matches:
                        contexts.append({
                            'text': match.group(),
                            'position': (match.start(), match.end()),
                            'confidence': 0.9,
                            'formula_type': formula_name,
                            'standard_form': pattern_info.get("standard_form", "")
                        })
                except re.error:
                    continue
        
        return contexts
    
    def _convert_to_latex(self, korean_formula: str) -> str:
        """한글 수식을 LaTeX로 변환"""
        latex = korean_formula
        
        # 1. 한글 숫자 변환
        latex = self._convert_korean_numbers(latex)
        
        # 2. 수학 용어 변환
        for korean, latex_term in sorted(self.math_terms.items(), 
                                       key=lambda x: len(x[0]), reverse=True):
            latex = latex.replace(korean, f" {latex_term} ")
        
        # 3. 금융 용어 변환
        for korean, symbol in sorted(self.financial_terms.items(), 
                                   key=lambda x: len(x[0]), reverse=True):
            latex = latex.replace(korean, symbol)
        
        # 4. 연산자 변환
        operators = self.patterns.get("operator_patterns", {}).get("korean_operators", {})
        for korean, latex_op in operators.items():
            latex = latex.replace(korean, f" {latex_op} ")
        
        # 5. 분수 패턴 변환
        latex = self._convert_fractions(latex)
        
        # 6. 지수/첨자 변환
        latex = self._convert_superscripts_subscripts(latex)
        
        # 7. 전처리 규칙 적용
        latex = self._apply_preprocessing_rules(latex)
        
        # 8. 정리
        latex = self._clean_latex(latex)
        
        return latex
    
    def _convert_korean_numbers(self, text: str) -> str:
        """한글 숫자를 아라비아 숫자로 변환"""
        result = text
        
        # 큰 단위부터 변환
        units = [
            ("조", 1000000000000),
            ("억", 100000000),
            ("만", 10000),
            ("천", 1000),
            ("백", 100),
            ("십", 10)
        ]
        
        for unit_name, unit_value in units:
            pattern = rf'(\d*)\s*{unit_name}'
            
            def replace_unit(match):
                num_str = match.group(1)
                num = int(num_str) if num_str else 1
                return str(num * unit_value)
            
            result = re.sub(pattern, replace_unit, result)
        
        # 기본 숫자 변환
        for korean, arabic in self.korean_numbers.items():
            if korean in ["십", "백", "천", "만", "억", "조"]:
                continue  # 이미 처리됨
            result = result.replace(korean, arabic)
        
        return result
    
    def _convert_fractions(self, text: str) -> str:
        """분수 표현 변환"""
        # "X분의 Y" 형태
        pattern = r'(\d+)\s*분의\s*(\d+)'
        text = re.sub(pattern, r'\\frac{\2}{\1}', text)
        
        # "Y/X" 형태 (이미 수식 형태)
        pattern = r'(\d+)\s*/\s*(\d+)'
        text = re.sub(pattern, r'\\frac{\1}{\2}', text)
        
        return text
    
    def _convert_superscripts_subscripts(self, text: str) -> str:
        """지수와 첨자 변환"""
        # 제곱, 세제곱 등
        text = re.sub(r'(\w+)\s*제곱', r'\1^2', text)
        text = re.sub(r'(\w+)\s*세제곱', r'\1^3', text)
        text = re.sub(r'(\w+)\s*의\s*(\d+)\s*제곱', r'\1^{\2}', text)
        
        # 첨자 (예: X1, X2)
        text = re.sub(r'([A-Za-z]+)(\d+)', r'\1_{\2}', text)
        
        return text
    
    def _apply_preprocessing_rules(self, text: str) -> str:
        """전처리 규칙 적용"""
        rules = self.patterns.get("preprocessing_rules", [])
        
        for rule in rules:
            pattern = rule.get("pattern", "")
            replacement = rule.get("replacement", "")
            
            try:
                text = re.sub(pattern, replacement, text)
            except re.error:
                continue
        
        return text
    
    def _clean_latex(self, latex: str) -> str:
        """LaTeX 정리"""
        # 연속된 공백 제거
        latex = re.sub(r'\s+', ' ', latex)
        
        # 불필요한 공백 제거
        latex = re.sub(r'\s*([+\-*/=])\s*', r' \1 ', latex)
        
        # 중복된 백슬래시 제거
        latex = re.sub(r'\\+', r'\\', latex)
        
        return latex.strip()
    
    def _remove_overlapping_contexts(self, contexts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """겹치는 컨텍스트 제거"""
        if not contexts:
            return contexts
        
        # 위치로 정렬
        contexts.sort(key=lambda x: x['position'][0])
        
        # 겹치지 않는 컨텍스트만 선택
        result = [contexts[0]]
        
        for context in contexts[1:]:
            last_end = result[-1]['position'][1]
            current_start = context['position'][0]
            
            if current_start >= last_end:
                result.append(context)
            elif context['confidence'] > result[-1]['confidence']:
                # 더 높은 신뢰도를 가진 것으로 교체
                result[-1] = context
        
        return result
    
    def _classify_formula(self, latex: str) -> str:
        """수식 분류"""
        if '\\int' in latex:
            return 'integral'
        elif '\\sum' in latex:
            return 'summation'
        elif '\\frac' in latex:
            return 'fraction'
        elif any(term in latex for term in ['PV', 'FV', 'PMT', 'NPV', 'IRR']):
            return 'financial'
        elif '=' in latex:
            return 'equation'
        else:
            return 'expression'
    
    def _check_financial_context(self, text: str) -> bool:
        """금융 관련 수식인지 확인"""
        financial_keywords = [
            '현재가치', '미래가치', '이자율', '할인율', '수익률',
            '투자', '복리', '연금', '원금', '이자'
        ] + list(self.financial_terms.keys())
        
        return any(keyword in text for keyword in financial_keywords)