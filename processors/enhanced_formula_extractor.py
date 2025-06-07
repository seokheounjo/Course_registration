# processors/enhanced_formula_extractor.py
"""
향상된 수식 추출 모듈 - 90% 이상 정확도 목표
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import cv2
import re
from dataclasses import dataclass
import json
import hashlib

logger = logging.getLogger(__name__)

# Pix2Text 설치 확인
try:
    from pix2text import Pix2Text
    PIX2TEXT_AVAILABLE = True
except ImportError:
    PIX2TEXT_AVAILABLE = False
    logger.warning("Pix2Text가 설치되지 않았습니다. 기본 OCR 사용")

# SymPy 설치 확인
try:
    import sympy
    from sympy.parsing.latex import parse_latex
    SYMPY_AVAILABLE = True
except ImportError:
    SYMPY_AVAILABLE = False
    logger.warning("SymPy가 설치되지 않았습니다. 수식 파싱 제한")

@dataclass
class FormulaData:
    """수식 데이터 클래스"""
    id: str
    page_num: int
    bbox: List[int]
    latex: str
    python_code: str
    variables: Dict[str, str]
    confidence: float
    type: str
    context: Dict[str, str]
    image_data: Optional[bytes] = None
    
class EnhancedFormulaExtractor:
    """향상된 수식 추출기"""
    
    def __init__(self, config):
        self.config = config
        self.device = config.device
        
        # 수식 인식 모델 초기화
        self._init_models()
        
        # 보험 수식 패턴
        self.insurance_patterns = {
            'premium': [
                r'P\s*=', r'보험료\s*=', r'영업보험료\s*=',
                r'순보험료\s*=', r'P_\{.*\}\s*='
            ],
            'reserve': [
                r'V\s*=', r'책임준비금\s*=', r'준비금\s*=',
                r'V_\{.*\}\s*=', r'적립금\s*='
            ],
            'mortality': [
                r'q_\{?x', r'위험률\s*=', r'사망률\s*=',
                r'발생률\s*='
            ],
            'interest': [
                r'i\s*=', r'이율\s*=', r'이자율\s*=',
                r'할인율\s*='
            ],
            'annuity': [
                r'a_\{.*\}', r'연금\s*=', r'N_\{?x', r'D_\{?x'
            ]
        }
        
    def _init_models(self):
        """모델 초기화"""
        # Pix2Text 모델
        if PIX2TEXT_AVAILABLE:
            try:
                self.pix2text = Pix2Text(
                    analyzer_config={'model_name': 'mfd'},
                    formula_config={'model_name': 'mfr'}
                )
                logger.info("Pix2Text 모델 로드 완료")
            except Exception as e:
                logger.error(f"Pix2Text 초기화 실패: {e}")
                self.pix2text = None
        else:
            self.pix2text = None
            
        # 추가 모델 초기화 가능
        
    def extract_formulas(self, image_path: Path, 
                        layout_regions: List[Dict[str, Any]],
                        page_text: str = "") -> List[FormulaData]:
        """이미지에서 수식 추출"""
        formulas = []
        
        try:
            # 1. 다중 방법으로 수식 영역 검출
            all_regions = self._detect_all_formula_regions(
                image_path, layout_regions, page_text
            )
            
            # 2. 각 영역에서 수식 추출
            for i, region in enumerate(all_regions):
                formula = self._extract_single_formula(
                    image_path, region, i, page_text
                )
                if formula and formula.confidence > 0.5:
                    formulas.append(formula)
            
            # 3. 중복 제거 및 병합
            formulas = self._merge_duplicate_formulas(formulas)
            
            # 4. 후처리 및 검증
            formulas = self._post_process_formulas(formulas)
            
            logger.info(f"총 {len(formulas)}개 수식 추출 완료")
            
        except Exception as e:
            logger.error(f"수식 추출 실패: {e}")
            
        return formulas
    
    def _detect_all_formula_regions(self, image_path: Path,
                                  layout_regions: List[Dict[str, Any]],
                                  page_text: str) -> List[Dict[str, Any]]:
        """다양한 방법으로 수식 영역 검출"""
        all_regions = []
        
        # 1. 레이아웃 분석 결과 활용
        layout_formulas = [r for r in layout_regions if r.get("label") == "formula"]
        all_regions.extend(layout_formulas)
        
        # 2. 컴퓨터 비전 기반 검출
        cv_regions = self._detect_formula_regions_cv(image_path)
        all_regions.extend(cv_regions)
        
        # 3. 텍스트 기반 검출 (수식 표시자 찾기)
        text_regions = self._detect_formula_regions_text(image_path, page_text)
        all_regions.extend(text_regions)
        
        # 4. 병합 및 중복 제거
        merged_regions = self._merge_overlapping_regions(all_regions)
        
        return merged_regions
    
    def _detect_formula_regions_cv(self, image_path: Path) -> List[Dict[str, Any]]:
        """컴퓨터 비전 기반 수식 영역 검출"""
        regions = []
        
        try:
            # 이미지 로드
            image = cv2.imread(str(image_path))
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 전처리
            # 1. 노이즈 제거
            denoised = cv2.fastNlMeansDenoising(gray)
            
            # 2. 적응적 이진화
            binary = cv2.adaptiveThreshold(
                denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY_INV, 11, 2
            )
            
            # 3. 수식 특징 강화
            # 수평선 제거 (테이블 선 제거)
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
            remove_horizontal = cv2.morphologyEx(binary, cv2.MORPH_OPEN, horizontal_kernel)
            binary = binary - remove_horizontal
            
            # 수직선 제거
            vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
            remove_vertical = cv2.morphologyEx(binary, cv2.MORPH_OPEN, vertical_kernel)
            binary = binary - remove_vertical
            
            # 4. 수식 영역 찾기
            # 연결 요소 분석
            num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
                binary, connectivity=8
            )
            
            for i in range(1, num_labels):
                x, y, w, h = stats[i, :4]
                area = stats[i, 4]
                
                # 수식 가능성 평가
                if self._is_likely_formula_region(binary[y:y+h, x:x+w], w, h, area):
                    regions.append({
                        'bbox': [x, y, x+w, y+h],
                        'confidence': self._calculate_formula_confidence(
                            binary[y:y+h, x:x+w], w, h
                        ),
                        'method': 'cv'
                    })
            
        except Exception as e:
            logger.error(f"CV 기반 수식 검출 실패: {e}")
            
        return regions
    
    def _is_likely_formula_region(self, region: np.ndarray, 
                                width: int, height: int, area: int) -> bool:
        """수식 영역 가능성 평가"""
        # 크기 필터
        if width < 20 or height < 10 or area < 200:
            return False
            
        # 종횡비 확인
        aspect_ratio = width / height
        if aspect_ratio < 0.5 or aspect_ratio > 10:
            return False
            
        # 밀도 확인
        density = np.sum(region > 0) / (width * height)
        if density < 0.05 or density > 0.8:
            return False
            
        # 수식 특징 확인
        # 1. 특수 기호 포함 여부 (분수선, 루트 등)
        horizontal_lines = self._count_horizontal_lines(region)
        if horizontal_lines > 0:
            return True
            
        # 2. 복잡도 확인
        contours, _ = cv2.findContours(region, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) > 3:  # 여러 구성요소
            return True
            
        return False
    
    def _count_horizontal_lines(self, region: np.ndarray) -> int:
        """수평선 개수 계산 (분수선 등)"""
        h, w = region.shape
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (w//3, 1))
        horizontal = cv2.morphologyEx(region, cv2.MORPH_OPEN, horizontal_kernel)
        
        # 수평선 개수
        projection = np.sum(horizontal, axis=1)
        lines = np.where(projection > w * 0.3)[0]
        
        return len(lines)
    
    def _calculate_formula_confidence(self, region: np.ndarray, 
                                    width: int, height: int) -> float:
        """수식 신뢰도 계산"""
        confidence = 0.5  # 기본값
        
        # 크기 점수
        size_score = min(width * height / 10000, 1.0)
        confidence += size_score * 0.2
        
        # 복잡도 점수
        contours, _ = cv2.findContours(region, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        complexity_score = min(len(contours) / 10, 1.0)
        confidence += complexity_score * 0.2
        
        # 밀도 점수
        density = np.sum(region > 0) / (width * height)
        density_score = 1.0 - abs(density - 0.3) / 0.3
        confidence += density_score * 0.1
        
        return min(confidence, 1.0)
    
    def _detect_formula_regions_text(self, image_path: Path, 
                                   page_text: str) -> List[Dict[str, Any]]:
        """텍스트 기반 수식 영역 검출"""
        regions = []
        
        # 수식 지시자 패턴
        formula_indicators = [
            r'식\s*\d+', r'수식\s*\d+', r'공식\s*\d+',
            r'다음과\s*같이', r'아래와\s*같이', r'다음\s*식',
            r'=\s*[A-Za-z가-힣]', r'여기서', r'단,',
            r'[A-Z]\s*=', r'[가-힣]+\s*='
        ]
        
        # 텍스트에서 수식 위치 힌트 찾기
        for pattern in formula_indicators:
            matches = list(re.finditer(pattern, page_text))
            if matches:
                # 이미지에서 해당 영역 찾기 (OCR 역매핑 필요)
                # 여기서는 간단히 처리
                logger.debug(f"텍스트 패턴 발견: {pattern}, {len(matches)}개")
                
        return regions
    
    def _merge_overlapping_regions(self, regions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """겹치는 영역 병합"""
        if not regions:
            return []
            
        # bbox 기준으로 정렬
        regions.sort(key=lambda r: (r['bbox'][1], r['bbox'][0]))
        
        merged = []
        current = regions[0].copy()
        
        for region in regions[1:]:
            if self._is_overlapping(current['bbox'], region['bbox']):
                # 병합
                current['bbox'] = self._merge_bboxes(current['bbox'], region['bbox'])
                current['confidence'] = max(current['confidence'], 
                                          region.get('confidence', 0.5))
            else:
                merged.append(current)
                current = region.copy()
                
        merged.append(current)
        
        return merged
    
    def _is_overlapping(self, bbox1: List[int], bbox2: List[int], 
                       threshold: float = 0.3) -> bool:
        """두 영역이 겹치는지 확인"""
        x1_1, y1_1, x2_1, y2_1 = bbox1
        x1_2, y1_2, x2_2, y2_2 = bbox2
        
        # 교집합 계산
        x1_i = max(x1_1, x1_2)
        y1_i = max(y1_1, y1_2)
        x2_i = min(x2_1, x2_2)
        y2_i = min(y2_1, y2_2)
        
        if x2_i < x1_i or y2_i < y1_i:
            return False
            
        # 교집합 면적
        intersection = (x2_i - x1_i) * (y2_i - y1_i)
        
        # 합집합 면적
        area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
        area2 = (x2_2 - x1_2) * (y2_2 - y1_2)
        union = area1 + area2 - intersection
        
        # IoU
        iou = intersection / union if union > 0 else 0
        
        return iou > threshold
    
    def _merge_bboxes(self, bbox1: List[int], bbox2: List[int]) -> List[int]:
        """두 bbox 병합"""
        x1 = min(bbox1[0], bbox2[0])
        y1 = min(bbox1[1], bbox2[1])
        x2 = max(bbox1[2], bbox2[2])
        y2 = max(bbox1[3], bbox2[3])
        
        return [x1, y1, x2, y2]
    
    def _extract_single_formula(self, image_path: Path,
                              region: Dict[str, Any],
                              formula_id: int,
                              page_text: str) -> Optional[FormulaData]:
        """단일 수식 추출"""
        try:
            # 이미지 크롭
            image = Image.open(image_path)
            formula_img = image.crop(region['bbox'])
            
            # 전처리
            processed_img = self._preprocess_formula_image(formula_img)
            
            # 수식 인식 (여러 방법 시도)
            latex_results = []
            
            # 1. Pix2Text
            if self.pix2text:
                try:
                    result = self.pix2text.recognize(
                        np.array(processed_img),
                        resized_shape=600
                    )
                    if 'formula' in result:
                        latex_results.append({
                            'latex': result['formula'],
                            'confidence': 0.9,
                            'method': 'pix2text'
                        })
                except Exception as e:
                    logger.warning(f"Pix2Text 인식 실패: {e}")
            
            # 2. 기본 OCR + 후처리
            from processors.formula_processor import FormulaProcessor
            processor = FormulaProcessor(self.config)
            basic_result = processor._formula_to_latex(processed_img)
            if basic_result:
                latex_results.append({
                    'latex': basic_result,
                    'confidence': 0.7,
                    'method': 'ocr'
                })
            
            # 최적 결과 선택
            if not latex_results:
                return None
                
            best_result = max(latex_results, key=lambda x: x['confidence'])
            
            # 컨텍스트 추출
            context = self._extract_formula_context(
                region['bbox'], page_text, image.size
            )
            
            # 수식 타입 분류
            formula_type = self._classify_formula_type(best_result['latex'], context)
            
            # 변수 추출 및 Python 코드 변환
            conversion_result = self._convert_to_python(
                best_result['latex'], formula_type
            )
            
            # FormulaData 생성
            formula_id_str = hashlib.md5(
                f"{formula_id}_{best_result['latex']}".encode()
            ).hexdigest()[:8]
            
            # 이미지 데이터 저장
            import io
            img_buffer = io.BytesIO()
            formula_img.save(img_buffer, format='PNG')
            img_data = img_buffer.getvalue()
            
            return FormulaData(
                id=formula_id_str,
                page_num=0,  # 나중에 설정
                bbox=region['bbox'],
                latex=best_result['latex'],
                python_code=conversion_result['python_code'],
                variables=conversion_result['variables'],
                confidence=best_result['confidence'],
                type=formula_type,
                context=context,
                image_data=img_data
            )
            
        except Exception as e:
            logger.error(f"단일 수식 추출 실패: {e}")
            return None
    
    def _preprocess_formula_image(self, image: Image.Image) -> Image.Image:
        """수식 이미지 전처리"""
        # 1. 크기 조정 (너무 작으면 확대)
        width, height = image.size
        if width < 100 or height < 50:
            scale = max(100/width, 50/height)
            new_size = (int(width * scale), int(height * scale))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        # 2. 그레이스케일 변환
        if image.mode != 'L':
            image = image.convert('L')
        
        # 3. 대비 향상
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.5)
        
        # 4. 선명도 향상
        image = image.filter(ImageFilter.SHARPEN)
        
        # 5. 패딩 추가
        width, height = image.size
        new_image = Image.new('L', (width + 20, height + 20), 255)
        new_image.paste(image, (10, 10))
        
        return new_image
    
    def _extract_formula_context(self, bbox: List[int], 
                               page_text: str,
                               page_size: Tuple[int, int]) -> Dict[str, str]:
        """수식 주변 컨텍스트 추출"""
        context = {
            'before': '',
            'after': '',
            'section': '',
            'variables': {}
        }
        
        # 텍스트에서 위치 추정 (간단한 구현)
        # 실제로는 OCR 결과의 위치 정보를 활용해야 함
        
        # 변수 설명 찾기
        variable_patterns = [
            r'([A-Za-z])\s*:\s*([가-힣\s]+)',
            r'([A-Za-z])\s*=\s*([가-힣\s]+)',
            r'여기서\s*([A-Za-z])\s*는\s*([가-힣\s]+)',
            r'단,\s*([A-Za-z])\s*=\s*([가-힣\s]+)'
        ]
        
        for pattern in variable_patterns:
            matches = re.finditer(pattern, page_text)
            for match in matches:
                var_name = match.group(1)
                var_desc = match.group(2).strip()
                context['variables'][var_name] = var_desc
        
        return context
    
    def _classify_formula_type(self, latex: str, context: Dict[str, str]) -> str:
        """수식 타입 분류"""
        latex_lower = latex.lower()
        
        # 보험 수식 패턴 매칭
        for formula_type, patterns in self.insurance_patterns.items():
            for pattern in patterns:
                if re.search(pattern, latex, re.IGNORECASE):
                    return formula_type
        
        # 일반 수식 타입
        if '\\frac' in latex:
            return 'fraction'
        elif '\\int' in latex:
            return 'integral'
        elif '\\sum' in latex:
            return 'summation'
        elif '=' in latex:
            return 'equation'
        else:
            return 'expression'
    
    def _convert_to_python(self, latex: str, 
                         formula_type: str) -> Dict[str, Any]:
        """LaTeX를 Python 코드로 변환"""
        result = {
            'python_code': '',
            'variables': {},
            'sympy_expr': ''
        }
        
        try:
            if SYMPY_AVAILABLE:
                # SymPy로 파싱
                # 전처리
                preprocessed = self._preprocess_latex_for_sympy(latex)
                
                try:
                    expr = parse_latex(preprocessed)
                except:
                    # 수동 파싱
                    expr = self._manual_parse_latex(preprocessed)
                
                # 변수 추출
                variables = list(expr.free_symbols)
                var_names = [str(v) for v in variables]
                
                # Python 함수 생성
                func_name = f"formula_{hashlib.md5(latex.encode()).hexdigest()[:8]}"
                
                # 보험 특화 처리
                if formula_type in ['premium', 'reserve']:
                    python_code = self._generate_insurance_function(
                        func_name, expr, var_names, latex
                    )
                else:
                    python_code = f"""
def {func_name}({', '.join(var_names)}):
    '''
    원본 LaTeX: {latex}
    수식 타입: {formula_type}
    '''
    import numpy as np
    from math import *
    
    try:
        result = {expr}
        return result
    except Exception as e:
        raise ValueError(f"수식 계산 오류: {{e}}")
"""
                
                result['python_code'] = python_code
                result['variables'] = {v: f'{v} 변수' for v in var_names}
                result['sympy_expr'] = str(expr)
                
            else:
                # SymPy 없이 기본 변환
                result = self._basic_latex_to_python(latex)
                
        except Exception as e:
            logger.error(f"Python 변환 실패: {e}")
            # 기본 변환 시도
            result = self._basic_latex_to_python(latex)
            
        return result
    
    def _preprocess_latex_for_sympy(self, latex: str) -> str:
        """SymPy 파싱을 위한 LaTeX 전처리"""
        # 일반적인 수정
        latex = latex.replace('\\times', '*')
        latex = latex.replace('\\div', '/')
        latex = latex.replace('\\cdot', '*')
        
        # 첨자 처리
        latex = re.sub(r'([A-Za-z])_\{([^}]+)\}', r'\1_{\2}', latex)
        latex = re.sub(r'([A-Za-z])_([A-Za-z0-9])', r'\1_{\2}', latex)
        
        # 보험 기호 처리
        latex = latex.replace('\\ddot{a}', 'a_ddot')
        latex = latex.replace('\\bar{a}', 'a_bar')
        
        return latex
    
    def _manual_parse_latex(self, latex: str):
        """수동 LaTeX 파싱"""
        # 간단한 수식만 처리
        if SYMPY_AVAILABLE:
            import sympy as sp
            
            # 변수 찾기
            var_pattern = r'[A-Za-z](?:_\{[^}]+\})?'
            variables = list(set(re.findall(var_pattern, latex)))
            
            # SymPy 심볼 생성
            symbols = {}
            for var in variables:
                clean_var = var.replace('_', '').replace('{', '').replace('}', '')
                symbols[var] = sp.Symbol(clean_var)
            
            # 수식 변환
            expr_str = latex
            for var, sym in symbols.items():
                expr_str = expr_str.replace(var, str(sym))
            
            # 기본 연산자 변환
            expr_str = expr_str.replace('\\frac', '/')
            
            try:
                expr = sp.sympify(expr_str)
                return expr
            except:
                # 실패시 기본 표현식
                return sp.Symbol('undefined')
        else:
            return None
    
    def _generate_insurance_function(self, func_name: str, expr, 
                                   var_names: List[str], 
                                   latex: str) -> str:
        """보험 특화 함수 생성"""
        # 보험 계산에 필요한 추가 import
        imports = """
    import numpy as np
    from math import *
    from decimal import Decimal, getcontext
    
    # 보험 계산 정밀도 설정
    getcontext().prec = 10
"""
        
        # 변수 검증 코드
        validations = []
        for var in var_names:
            if var.startswith('q'):  # 위험률
                validations.append(f"    assert 0 <= {var} <= 1, '{var}는 0과 1 사이여야 합니다'")
            elif var == 'i':  # 이율
                validations.append(f"    assert -1 < {var} < 1, '이율은 -100%~100% 사이여야 합니다'")
            elif var in ['n', 'm', 't']:  # 기간
                validations.append(f"    assert {var} >= 0, '{var}는 0 이상이어야 합니다'")
        
        validation_code = '\n'.join(validations) if validations else "    pass"
        
        return f"""
def {func_name}({', '.join(var_names)}):
    '''
    보험 수식: {latex}
    
    Parameters:
    -----------
    {chr(10).join(f'    {var} : float' for var in var_names)}
    
    Returns:
    --------
    float : 계산 결과
    '''
{imports}
    
    # 입력값 검증
{validation_code}
    
    try:
        # 수식 계산
        result = {expr}
        
        # 결과 검증
        if not isinstance(result, (int, float, Decimal)):
            raise ValueError("계산 결과가 숫자가 아닙니다")
            
        return float(result)
        
    except Exception as e:
        raise ValueError(f"보험 수식 계산 오류: {{e}}")
"""
    
    def _basic_latex_to_python(self, latex: str) -> Dict[str, Any]:
        """기본 LaTeX → Python 변환"""
        # 변수 찾기
        var_pattern = r'[A-Za-z](?:_\{?[^}]+\}?)?'
        variables = list(set(re.findall(var_pattern, latex)))
        
        # Python 코드로 변환
        python_expr = latex
        
        # 기본 변환 규칙
        replacements = {
            r'\\frac\{([^}]+)\}\{([^}]+)\}': r'((\1) / (\2))',
            r'\\sqrt\{([^}]+)\}': r'sqrt(\1)',
            r'\\times': '*',
            r'\\div': '/',
            r'\\cdot': '*',
            r'\^': '**',
            r'_\{([^}]+)\}': r'_\1',
            r'\\sum': 'sum',
            r'\\prod': 'prod'
        }
        
        for pattern, replacement in replacements.items():
            python_expr = re.sub(pattern, replacement, python_expr)
        
        # 함수 생성
        func_name = f"formula_{hashlib.md5(latex.encode()).hexdigest()[:8]}"
        clean_vars = [v.replace('_', '').replace('{', '').replace('}', '') 
                     for v in variables]
        
        python_code = f"""
def {func_name}({', '.join(clean_vars)}):
    '''
    원본 LaTeX: {latex}
    '''
    import numpy as np
    from math import *
    
    try:
        # 주의: 자동 변환된 코드입니다. 검증이 필요합니다.
        result = {python_expr}
        return result
    except Exception as e:
        raise ValueError(f"수식 계산 오류: {{e}}")
"""
        
        return {
            'python_code': python_code,
            'variables': {v: f'{v} 변수' for v in clean_vars},
            'sympy_expr': python_expr
        }
    
    def _merge_duplicate_formulas(self, formulas: List[FormulaData]) -> List[FormulaData]:
        """중복 수식 제거"""
        if not formulas:
            return []
        
        unique_formulas = []
        seen_latex = set()
        
        for formula in formulas:
            # LaTeX 정규화
            normalized = self._normalize_latex(formula.latex)
            
            if normalized not in seen_latex:
                seen_latex.add(normalized)
                unique_formulas.append(formula)
            else:
                # 같은 수식이면 신뢰도가 높은 것 선택
                for i, uf in enumerate(unique_formulas):
                    if self._normalize_latex(uf.latex) == normalized:
                        if formula.confidence > uf.confidence:
                            unique_formulas[i] = formula
                        break
        
        return unique_formulas
    
    def _normalize_latex(self, latex: str) -> str:
        """LaTeX 정규화"""
        # 공백 제거
        normalized = re.sub(r'\s+', '', latex)
        
        # 중괄호 정규화
        normalized = re.sub(r'\{([a-zA-Z0-9])\}', r'\1', normalized)
        
        return normalized
    
    def _post_process_formulas(self, formulas: List[FormulaData]) -> List[FormulaData]:
        """수식 후처리"""
        processed = []
        
        for formula in formulas:
            # LaTeX 검증 및 수정
            formula.latex = self._validate_and_fix_latex(formula.latex)
            
            # 보험 수식 특화 처리
            if formula.type in ['premium', 'reserve', 'mortality']:
                formula = self._process_insurance_formula(formula)
            
            # 신뢰도 재계산
            formula.confidence = self._recalculate_confidence(formula)
            
            processed.append(formula)
        
        return processed
    
    def _validate_and_fix_latex(self, latex: str) -> str:
        """LaTeX 검증 및 수정"""
        # 괄호 균형 확인
        latex = self._balance_brackets(latex)
        
        # 일반적인 OCR 오류 수정
        corrections = {
            r'\\t[il]mes': r'\\times',  # times 오타
            r'\\d[il]v': r'\\div',      # div 오타
            r'\\[il]nt': r'\\int',      # int 오타
            r'\\sum_\{([^}]+)\}\^\{([^}]+)\}': r'\\sum_{\\1}^{\\2}',  # sum 표기
            r'([a-zA-Z])(\d)': r'\1_{\2}',  # 첨자 추가
        }
        
        for pattern, replacement in corrections.items():
            latex = re.sub(pattern, replacement, latex)
        
        return latex
    
    def _balance_brackets(self, latex: str) -> str:
        """괄호 균형 맞추기"""
        # 중괄호
        open_braces = latex.count('{')
        close_braces = latex.count('}')
        
        if open_braces > close_braces:
            latex += '}' * (open_braces - close_braces)
        elif close_braces > open_braces:
            latex = '{' * (close_braces - open_braces) + latex
        
        # 일반 괄호
        open_parens = latex.count('(')
        close_parens = latex.count(')')
        
        if open_parens > close_parens:
            latex += ')' * (open_parens - close_parens)
        elif close_parens > open_parens:
            latex = '(' * (close_parens - open_parens) + latex
        
        return latex
    
    def _process_insurance_formula(self, formula: FormulaData) -> FormulaData:
        """보험 수식 특화 처리"""
        # 보험 기호 정규화
        insurance_symbols = {
            'P': '보험료',
            'V': '책임준비금',
            'M': '순보험료',
            'N': '연금현가',
            'D': '현가',
            'q': '위험률',
            'i': '이율',
            'x': '연령',
            'n': '보험기간',
            'm': '납입기간',
            't': '경과기간'
        }
        
        # 변수 설명 업데이트
        for var, desc in insurance_symbols.items():
            if var in formula.latex:
                formula.variables[var] = desc
        
        # 특수 보험 기호 처리
        if 'a_' in formula.latex or '\\ddot{a}' in formula.latex:
            formula.variables['a'] = '연금현가계수'
        
        return formula
    
    def _recalculate_confidence(self, formula: FormulaData) -> float:
        """신뢰도 재계산"""
        confidence = formula.confidence
        
        # LaTeX 구조 완성도
        if self._is_valid_latex_structure(formula.latex):
            confidence += 0.1
        
        # Python 코드 실행 가능성
        if self._is_executable_python(formula.python_code):
            confidence += 0.1
        
        # 변수 설명 완성도
        if len(formula.variables) > 0:
            confidence += 0.05
        
        return min(confidence, 1.0)
    
    def _is_valid_latex_structure(self, latex: str) -> bool:
        """LaTeX 구조 유효성 확인"""
        # 기본 검사
        if not latex:
            return False
        
        # 균형 잡힌 괄호
        if latex.count('{') != latex.count('}'):
            return False
        
        if latex.count('(') != latex.count(')'):
            return False
        
        # 필수 명령어 형식
        command_pattern = r'\\[a-zA-Z]+(?:\{[^}]*\})*'
        commands = re.findall(command_pattern, latex)
        
        for cmd in commands:
            if cmd.startswith('\\') and '{' in cmd:
                if cmd.count('{') != cmd.count('}'):
                    return False
        
        return True
    
    def _is_executable_python(self, python_code: str) -> bool:
        """Python 코드 실행 가능성 확인"""
        try:
            # 문법 검사
            compile(python_code, '<string>', 'exec')
            return True
        except SyntaxError:
            return False
        
    def save_formulas_to_db(self, formulas: List[FormulaData], 
                           db_path: Path, document_id: str):
        """수식을 데이터베이스에 저장"""
        import sqlite3
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 테이블 생성
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS formulas (
                id TEXT PRIMARY KEY,
                document_id TEXT,
                page_number INTEGER,
                formula_latex TEXT,
                formula_python TEXT,
                variables TEXT,
                formula_type TEXT,
                confidence REAL,
                context TEXT,
                image_data BLOB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 수식 저장
        for formula in formulas:
            cursor.execute('''
                INSERT OR REPLACE INTO formulas 
                (id, document_id, page_number, formula_latex, formula_python,
                 variables, formula_type, confidence, context, image_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                formula.id,
                document_id,
                formula.page_num,
                formula.latex,
                formula.python_code,
                json.dumps(formula.variables, ensure_ascii=False),
                formula.type,
                formula.confidence,
                json.dumps(formula.context, ensure_ascii=False),
                formula.image_data
            ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"{len(formulas)}개 수식을 DB에 저장 완료")