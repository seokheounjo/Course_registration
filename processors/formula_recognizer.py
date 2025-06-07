# src/extractors/formula_recognizer.py

import os
import json
import logging
from typing import List, Dict, Tuple, Optional
import numpy as np
from PIL import Image
import cv2
from dataclasses import dataclass
from pathlib import Path
import re
import difflib

# Pix2Text import
try:
    from pix2text import Pix2Text
    PIX2TEXT_AVAILABLE = True
except ImportError:
    PIX2TEXT_AVAILABLE = False
    logging.warning("Pix2Text not available")

# SymPy for LaTeX parsing
import sympy
from latex2sympy2 import latex2sympy

logger = logging.getLogger(__name__)

@dataclass
class FormulaResult:
    """수식 인식 결과를 담는 클래스"""
    latex: str
    confidence: float
    bbox: List[float]
    image_path: str
    method: str
    python_code: Optional[str] = None
    variables: Optional[List[str]] = None
    error: Optional[str] = None

class FormulaRecognizer:
    """수식 인식을 담당하는 클래스"""
    
    def __init__(self, config_path: str = "config/config.json"):
        """
        FormulaRecognizer 초기화
        
        Args:
            config_path: 설정 파일 경로
        """
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.ocr_config = self.config['ocr_settings']
        self.min_confidence = self.config['formula_detection']['min_confidence']
        
        # Pix2Text 초기화
        self.pix2text = None
        if PIX2TEXT_AVAILABLE:
            try:
                model_path = self.ocr_config['pix2text'].get('model_path', None)
                device = self.ocr_config['pix2text'].get('device', 'cpu')
                
                if model_path and os.path.exists(model_path):
                    self.pix2text = Pix2Text(
                        analyzer_model_fp=f"{model_path}/analyzer",
                        text_formula_ocr_model_fp=f"{model_path}/text_formula_ocr",
                        device=device
                    )
                else:
                    # 기본 모델 사용
                    self.pix2text = Pix2Text(device=device)
                    
                logger.info("Pix2Text initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Pix2Text: {e}")
                self.pix2text = None
        
        # 앙상블 가중치
        self.ensemble_weights = self.ocr_config.get('ensemble_weights', {
            'pix2text': 0.6,
            'latex_ocr': 0.4
        })
        
        # 보험 수식 패턴
        self.insurance_patterns = self._load_insurance_patterns()
    
    def _load_insurance_patterns(self) -> Dict:
        """보험 관련 수식 패턴 로드"""
        return {
            'premium': {
                'pattern': r'P\s*=.*',
                'variables': ['P', 'M', 'N', 'i'],
                'description': '보험료 계산'
            },
            'reserve': {
                'pattern': r'V\s*=.*',
                'variables': ['V', 'P', 'S', 'W'],
                'description': '책임준비금 계산'
            },
            'coi': {
                'pattern': r'COI\s*=.*',
                'variables': ['COI', 'S', 'q', 'v'],
                'description': '위험보험료 계산'
            },
            'annuity': {
                'pattern': r'[aä]\s*=.*',
                'variables': ['a', 'N', 'D', 'i'],
                'description': '연금현가 계산'
            }
        }
    
    def recognize_formula(self, image_path: str, bbox: List[float]) -> FormulaResult:
        """
        이미지에서 수식 인식
        
        Args:
            image_path: 이미지 파일 경로
            bbox: 수식 영역 좌표 [x1, y1, x2, y2]
            
        Returns:
            수식 인식 결과
        """
        # 이미지 로드 및 영역 추출
        image = cv2.imread(image_path)
        if image is None:
            return FormulaResult(
                latex="",
                confidence=0.0,
                bbox=bbox,
                image_path=image_path,
                method="error",
                error="Failed to load image"
            )
        
        # bbox 영역 추출
        x1, y1, x2, y2 = map(int, bbox)
        formula_image = image[y1:y2, x1:x2]
        
        # 이미지 전처리
        processed_image = self._preprocess_image(formula_image)
        
        # 여러 방법으로 인식
        results = []
        
        # 1. Pix2Text 사용
        if self.pix2text:
            pix2text_result = self._recognize_with_pix2text(processed_image)
            if pix2text_result:
                results.append(pix2text_result)
        
        # 2. 규칙 기반 인식 (간단한 수식)
        rule_based_result = self._recognize_with_rules(processed_image)
        if rule_based_result:
            results.append(rule_based_result)
        
        # 3. 결과 앙상블
        if results:
            final_result = self._ensemble_results(results)
            final_result.bbox = bbox
            final_result.image_path = image_path
            
            # LaTeX를 Python 코드로 변환
            python_code, variables = self._latex_to_python(final_result.latex)
            final_result.python_code = python_code
            final_result.variables = variables
            
            return final_result
        
        # 인식 실패
        return FormulaResult(
            latex="",
            confidence=0.0,
            bbox=bbox,
            image_path=image_path,
            method="failed",
            error="No formula recognized"
        )
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        수식 인식을 위한 이미지 전처리
        
        Args:
            image: 원본 이미지
            
        Returns:
            전처리된 이미지
        """
        # 그레이스케일 변환
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # 노이즈 제거
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # 대비 향상
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)
        
        # 이진화
        _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # 모폴로지 연산으로 텍스트 연결
        kernel = np.ones((2, 2), np.uint8)
        morph = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        # 패딩 추가
        padded = cv2.copyMakeBorder(morph, 10, 10, 10, 10, cv2.BORDER_CONSTANT, value=255)
        
        return padded
    
    def _recognize_with_pix2text(self, image: np.ndarray) -> Optional[Dict]:
        """Pix2Text를 사용한 수식 인식"""
        if not self.pix2text:
            return None
        
        try:
            # numpy array를 PIL Image로 변환
            pil_image = Image.fromarray(image)
            
            # Pix2Text 인식
            result = self.pix2text.recognize_formula(pil_image)
            
            if result and 'text' in result:
                latex = result['text']
                confidence = result.get('score', 0.8)
                
                return {
                    'latex': latex,
                    'confidence': confidence,
                    'method': 'pix2text'
                }
        except Exception as e:
            logger.error(f"Pix2Text recognition failed: {e}")
        
        return None
    
    def _recognize_with_rules(self, image: np.ndarray) -> Optional[Dict]:
        """규칙 기반 간단한 수식 인식"""
        # OCR을 사용한 텍스트 추출 (Tesseract 대신 간단한 패턴 매칭)
        # 실제 구현에서는 Tesseract나 다른 OCR을 사용할 수 있음
        
        # 여기서는 간단한 예시만 제공
        # 실제로는 더 정교한 규칙 기반 인식이 필요
        
        return None
    
    def _ensemble_results(self, results: List[Dict]) -> FormulaResult:
        """여러 인식 결과를 앙상블"""
        if len(results) == 1:
            result = results[0]
            return FormulaResult(
                latex=result['latex'],
                confidence=result['confidence'],
                bbox=[],
                image_path="",
                method=result['method']
            )
        
        # 가중 평균으로 최종 결과 선택
        best_result = None
        best_score = 0
        
        for result in results:
            method = result['method']
            weight = self.ensemble_weights.get(method, 0.5)
            score = result['confidence'] * weight
            
            if score > best_score:
                best_score = score
                best_result = result
        
        if best_result:
            return FormulaResult(
                latex=best_result['latex'],
                confidence=best_score,
                bbox=[],
                image_path="",
                method='ensemble'
            )
        
        return FormulaResult(
            latex="",
            confidence=0.0,
            bbox=[],
            image_path="",
            method='failed'
        )
    
    def _latex_to_python(self, latex: str) -> Tuple[Optional[str], Optional[List[str]]]:
        """
        LaTeX 수식을 Python 코드로 변환
        
        Args:
            latex: LaTeX 수식
            
        Returns:
            (Python 코드, 변수 리스트)
        """
        if not latex:
            return None, None
        
        try:
            # LaTeX 전처리
            cleaned_latex = self._clean_latex(latex)
            
            # SymPy로 파싱
            sympy_expr = latex2sympy(cleaned_latex)
            
            # 변수 추출
            variables = [str(var) for var in sympy_expr.free_symbols]
            
            # Python 함수 생성
            func_name = f"formula_{hash(latex) & 0xFFFFFF}"
            
            python_code = f'''
def {func_name}({', '.join(variables)}):
    """
    원본 LaTeX: {latex}
    """
    import numpy as np
    from math import *
    
    result = {sympy_expr}
    return result
'''
            
            return python_code.strip(), variables
            
        except Exception as e:
            logger.error(f"Failed to convert LaTeX to Python: {e}")
            
            # 폴백: 간단한 변환 시도
            try:
                python_code = self._simple_latex_to_python(latex)
                variables = self._extract_variables(latex)
                return python_code, variables
            except:
                return None, None
    
    def _clean_latex(self, latex: str) -> str:
        """LaTeX 수식 정리"""
        # 일반적인 OCR 오류 수정
        corrections = {
            r'\\times': '*',
            r'\\div': '/',
            r'\\cdot': '*',
            r'\\pm': '±',
            r'\\leq': '<=',
            r'\\geq': '>=',
            r'\\neq': '!=',
            r'\\approx': '≈',
            r'\\sum': 'sum',
            r'\\prod': 'prod',
            r'\\int': 'integral',
            r'\\frac': 'frac'
        }
        
        cleaned = latex
        for old, new in corrections.items():
            cleaned = cleaned.replace(old, new)
        
        # 보험 수식 특화 처리
        insurance_corrections = {
            r'([PVMNDq])(\d+)': r'\1_\2',  # 첨자 수정
            r'a\s*\[(\d+)\]': r'a_{\1}',  # 연금 기호
        }
        
        for pattern, replacement in insurance_corrections.items():
            cleaned = re.sub(pattern, replacement, cleaned)
        
        return cleaned
    
    def _simple_latex_to_python(self, latex: str) -> str:
        """간단한 LaTeX to Python 변환"""
        # 기본적인 변환 규칙
        python = latex
        
        # 분수 변환
        python = re.sub(r'\\frac\{([^}]+)\}\{([^}]+)\}', r'(\1) / (\2)', python)
        
        # 지수 변환
        python = re.sub(r'\^([0-9]+)', r'**\1', python)
        python = re.sub(r'\^\{([^}]+)\}', r'**(\1)', python)
        
        # 첨자 제거 (변수명으로 변환)
        python = re.sub(r'_\{([^}]+)\}', r'_\1', python)
        python = re.sub(r'_([0-9]+)', r'_\1', python)
        
        # 함수명 생성
        func_name = f"formula_{hash(latex) & 0xFFFFFF}"
        variables = self._extract_variables(latex)
        
        return f'''
def {func_name}({', '.join(variables)}):
    """원본 LaTeX: {latex}"""
    return {python}
'''
    
    def _extract_variables(self, latex: str) -> List[str]:
        """LaTeX 수식에서 변수 추출"""
        # 영문자로 시작하는 변수명 패턴
        pattern = r'\b[A-Za-z][A-Za-z0-9_]*'
        
        # 함수명 제외
        functions = ['sin', 'cos', 'tan', 'log', 'ln', 'exp', 'sqrt', 'sum', 'prod']
        
        variables = set()
        for match in re.finditer(pattern, latex):
            var = match.group()
            if var not in functions:
                variables.add(var)
        
        return sorted(list(variables))
    
    def validate_formula(self, formula_result: FormulaResult) -> bool:
        """수식 검증"""
        if not formula_result.latex or formula_result.confidence < self.min_confidence:
            return False
        
        # 보험 수식 패턴 확인
        for pattern_name, pattern_info in self.insurance_patterns.items():
            if re.match(pattern_info['pattern'], formula_result.latex):
                logger.info(f"Detected insurance formula type: {pattern_name}")
                return True
        
        # 일반 수식 검증
        # 괄호 균형 확인
        if not self._check_bracket_balance(formula_result.latex):
            return False
        
        # Python 코드 실행 가능 여부 확인
        if formula_result.python_code:
            try:
                compile(formula_result.python_code, '<string>', 'exec')
                return True
            except:
                return False
        
        return True
    
    def _check_bracket_balance(self, text: str) -> bool:
        """괄호 균형 확인"""
        brackets = {
            '(': ')',
            '[': ']',
            '{': '}'
        }
        
        stack = []
        for char in text:
            if char in brackets:
                stack.append(char)
            elif char in brackets.values():
                if not stack:
                    return False
                last = stack.pop()
                if brackets[last] != char:
                    return False
        
        return len(stack) == 0