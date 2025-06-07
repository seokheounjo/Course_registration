# processors/insurance_formula_processor.py
"""
보험 특화 수식 처리 모듈
보험료, 책임준비금 등 보험 수식을 정확하게 처리
"""

import logging
import re
import json
from typing import List, Dict, Any, Optional, Tuple, Callable
from pathlib import Path
import numpy as np
from decimal import Decimal, getcontext
from dataclasses import dataclass, field
import sqlite3
from datetime import datetime

logger = logging.getLogger(__name__)

# 정밀도 설정
getcontext().prec = 10

@dataclass
class InsuranceFormula:
    """보험 수식 데이터 클래스"""
    formula_id: str
    name: str
    description: str
    category: str  # premium, reserve, mortality, interest, annuity
    latex: str
    python_function: str
    variables: Dict[str, Dict[str, Any]]  # {var_name: {description, type, constraints}}
    dependencies: List[str] = field(default_factory=list)  # 다른 수식 의존성
    test_cases: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class InsuranceFormulaProcessor:
    """보험 특화 수식 처리기"""
    
    def __init__(self, config):
        self.config = config
        
        # 보험 수식 템플릿
        self.formula_templates = self._load_formula_templates()
        
        # 보험 기호 정의
        self.insurance_symbols = {
            # 기본 기호
            'P': {'name': '보험료', 'type': 'premium'},
            'G': {'name': '영업보험료', 'type': 'premium'},
            'P^{(*)}': {'name': '순보험료', 'type': 'premium'},
            'V': {'name': '책임준비금', 'type': 'reserve'},
            'W': {'name': '해지환급금', 'type': 'surrender'},
            
            # 계산기수
            'l_x': {'name': '생존자수', 'type': 'commutation'},
            'd_x': {'name': '사망자수', 'type': 'commutation'},
            'D_x': {'name': '현가', 'type': 'commutation'},
            'N_x': {'name': '연금현가', 'type': 'commutation'},
            'C_x': {'name': '사망보험금현가', 'type': 'commutation'},
            'M_x': {'name': '사망보험금현가누계', 'type': 'commutation'},
            
            # 이율/할인
            'i': {'name': '이율', 'type': 'interest'},
            'v': {'name': '할인율', 'type': 'discount'},
            'd': {'name': '할인률', 'type': 'discount'},
            
            # 위험률
            'q_x': {'name': '사망률', 'type': 'mortality'},
            'p_x': {'name': '생존률', 'type': 'mortality'},
            'q_x^{(j)}': {'name': 'j번째 탈퇴율', 'type': 'decrement'},
            
            # 연금
            'a_x': {'name': '종신연금현가', 'type': 'annuity'},
            'ä_x': {'name': '기시연금현가', 'type': 'annuity'},
            'a_{x:n}': {'name': '유기연금현가', 'type': 'annuity'},
            'ä_{x:n}': {'name': '유기기시연금현가', 'type': 'annuity'},
            
            # 보험
            'A_x': {'name': '종신보험현가', 'type': 'insurance'},
            'A_{x:n}': {'name': '정기보험현가', 'type': 'insurance'},
            'A_{x:n}^1': {'name': '생존보험현가', 'type': 'insurance'},
            
            # 사업비
            'α': {'name': '신계약비율', 'type': 'expense'},
            'β': {'name': '유지비율', 'type': 'expense'},
            'γ': {'name': '수금비율', 'type': 'expense'}
        }
        
        # 수식 검증 규칙
        self.validation_rules = self._init_validation_rules()
        
    def _load_formula_templates(self) -> Dict[str, InsuranceFormula]:
        """보험 수식 템플릿 로드"""
        templates = {}
        
        # 1. 순보험료 계산
        templates['net_premium_whole_life'] = InsuranceFormula(
            formula_id='NPR001',
            name='종신보험 순보험료',
            description='종신보험의 순보험료 계산',
            category='premium',
            latex=r'P_x^{*} = \frac{M_x}{N_x}',
            python_function="""
def net_premium_whole_life(M_x, N_x):
    '''종신보험 순보험료 계산
    
    Parameters:
    -----------
    M_x : float - 사망보험금현가누계
    N_x : float - 연금현가
    
    Returns:
    --------
    float : 순보험료
    '''
    if N_x == 0:
        raise ValueError("N_x는 0이 될 수 없습니다")
    
    return M_x / N_x
""",
            variables={
                'M_x': {
                    'description': '사망보험금현가누계',
                    'type': 'float',
                    'constraints': {'min': 0}
                },
                'N_x': {
                    'description': '연금현가',
                    'type': 'float',
                    'constraints': {'min': 0.001}
                }
            },
            test_cases=[
                {'inputs': {'M_x': 1000, 'N_x': 10000}, 'expected': 0.1}
            ]
        )
        
        # 2. 책임준비금 계산
        templates['reserve_prospective'] = InsuranceFormula(
            formula_id='RSV001',
            name='장래법 책임준비금',
            description='장래법에 의한 책임준비금 계산',
            category='reserve',
            latex=r'_tV_x = \frac{M_{x+t} - N_{x+t} \cdot P_x^*}{D_{x+t}}',
            python_function="""
def reserve_prospective(M_x_t, N_x_t, P_star, D_x_t, t):
    '''장래법 책임준비금 계산
    
    Parameters:
    -----------
    M_x_t : float - x+t세의 사망보험금현가누계
    N_x_t : float - x+t세의 연금현가
    P_star : float - 순보험료
    D_x_t : float - x+t세의 현가
    t : int - 경과연수
    
    Returns:
    --------
    float : t년도말 책임준비금
    '''
    if D_x_t == 0:
        raise ValueError("D_x_t는 0이 될 수 없습니다")
    
    return (M_x_t - N_x_t * P_star) / D_x_t
""",
            variables={
                'M_x_t': {'description': 'x+t세의 사망보험금현가누계', 'type': 'float', 'constraints': {'min': 0}},
                'N_x_t': {'description': 'x+t세의 연금현가', 'type': 'float', 'constraints': {'min': 0}},
                'P_star': {'description': '순보험료', 'type': 'float', 'constraints': {'min': 0}},
                'D_x_t': {'description': 'x+t세의 현가', 'type': 'float', 'constraints': {'min': 0.001}},
                't': {'description': '경과연수', 'type': 'int', 'constraints': {'min': 0}}
            }
        )
        
        # 3. 영업보험료 계산
        templates['gross_premium'] = InsuranceFormula(
            formula_id='GPR001',
            name='영업보험료',
            description='사업비를 포함한 영업보험료 계산',
            category='premium',
            latex=r'P = \frac{P^* + \beta}{1 - \alpha \cdot D_x / N_x - \gamma}',
            python_function="""
def gross_premium(P_star, alpha, beta, gamma, D_x, N_x):
    '''영업보험료 계산
    
    Parameters:
    -----------
    P_star : float - 순보험료
    alpha : float - 신계약비율
    beta : float - 유지비율  
    gamma : float - 수금비율
    D_x : float - 현가
    N_x : float - 연금현가
    
    Returns:
    --------
    float : 영업보험료
    '''
    denominator = 1 - alpha * D_x / N_x - gamma
    
    if denominator <= 0:
        raise ValueError("분모가 0 이하가 될 수 없습니다")
    
    return (P_star + beta) / denominator
""",
            variables={
                'P_star': {'description': '순보험료', 'type': 'float', 'constraints': {'min': 0}},
                'alpha': {'description': '신계약비율', 'type': 'float', 'constraints': {'min': 0, 'max': 1}},
                'beta': {'description': '유지비율', 'type': 'float', 'constraints': {'min': 0}},
                'gamma': {'description': '수금비율', 'type': 'float', 'constraints': {'min': 0, 'max': 0.5}},
                'D_x': {'description': '현가', 'type': 'float', 'constraints': {'min': 0.001}},
                'N_x': {'description': '연금현가', 'type': 'float', 'constraints': {'min': 0.001}}
            }
        )
        
        # 4. 해지환급금 계산
        templates['surrender_value'] = InsuranceFormula(
            formula_id='SRV001',
            name='해지환급금',
            description='해지환급금 계산',
            category='surrender',
            latex=r'W_t = \max(V_t^{적용} - \alpha_t, V_t^{해약}))',
            python_function="""
def surrender_value(V_t_applied, V_t_surrender, alpha_t):
    '''해지환급금 계산
    
    Parameters:
    -----------
    V_t_applied : float - 적용기초율 책임준비금
    V_t_surrender : float - 해약기초율 책임준비금
    alpha_t : float - 해지공제액
    
    Returns:
    --------
    float : 해지환급금
    '''
    return max(V_t_applied - alpha_t, V_t_surrender)
""",
            variables={
                'V_t_applied': {'description': '적용기초율 책임준비금', 'type': 'float', 'constraints': {'min': 0}},
                'V_t_surrender': {'description': '해약기초율 책임준비금', 'type': 'float', 'constraints': {'min': 0}},
                'alpha_t': {'description': '해지공제액', 'type': 'float', 'constraints': {'min': 0}}
            }
        )
        
        # 5. 현가 계산
        templates['discount_factor'] = InsuranceFormula(
            formula_id='DSC001',
            name='할인계수',
            description='현가 계산을 위한 할인계수',
            category='interest',
            latex=r'v = \frac{1}{1 + i}',
            python_function="""
def discount_factor(i):
    '''할인계수 계산
    
    Parameters:
    -----------
    i : float - 이율
    
    Returns:
    --------
    float : 할인계수
    '''
    if i <= -1:
        raise ValueError("이율은 -100% 초과여야 합니다")
    
    return 1 / (1 + i)
""",
            variables={
                'i': {'description': '이율', 'type': 'float', 'constraints': {'min': -0.99, 'max': 1}}
            }
        )
        
        return templates
    
    def _init_validation_rules(self) -> Dict[str, Callable]:
        """검증 규칙 초기화"""
        rules = {
            'positive': lambda x: x >= 0,
            'probability': lambda x: 0 <= x <= 1,
            'interest_rate': lambda x: -1 < x < 1,
            'non_zero': lambda x: x != 0,
            'integer': lambda x: isinstance(x, int) or x.is_integer()
        }
        
        return rules
    
    def process_insurance_formula(self, formula_data: Dict[str, Any]) -> InsuranceFormula:
        """보험 수식 처리"""
        # 1. 수식 분류
        category = self._classify_formula(formula_data['latex'])
        
        # 2. 변수 분석
        variables = self._analyze_variables(formula_data['latex'], formula_data.get('context', {}))
        
        # 3. Python 코드 생성
        python_code = self._generate_insurance_python_code(
            formula_data['latex'],
            variables,
            category
        )
        
        # 4. 테스트 케이스 생성
        test_cases = self._generate_test_cases(category, variables)
        
        # 5. InsuranceFormula 객체 생성
        formula = InsuranceFormula(
            formula_id=formula_data.get('id', ''),
            name=self._generate_formula_name(formula_data['latex'], category),
            description=formula_data.get('description', ''),
            category=category,
            latex=formula_data['latex'],
            python_function=python_code,
            variables=variables,
            test_cases=test_cases,
            metadata={
                'confidence': formula_data.get('confidence', 0),
                'page_num': formula_data.get('page_num', 0),
                'created_at': datetime.now().isoformat()
            }
        )
        
        # 6. 검증
        validation_result = self._validate_formula(formula)
        if not validation_result['valid']:
            logger.warning(f"수식 검증 실패: {validation_result['errors']}")
            formula.metadata['validation_errors'] = validation_result['errors']
        
        return formula
    
    def _classify_formula(self, latex: str) -> str:
        """수식 분류"""
        # 패턴 매칭으로 분류
        patterns = {
            'premium': [r'P\s*=', r'P_[^=]*=', r'보험료'],
            'reserve': [r'V\s*=', r'_\d*V', r'준비금'],
            'mortality': [r'q_', r'p_', r'l_', r'd_'],
            'interest': [r'i\s*=', r'v\s*=', r'd\s*='],
            'annuity': [r'a_', r'ä_', r'N_'],
            'insurance': [r'A_', r'M_', r'C_'],
            'surrender': [r'W\s*=', r'해지', r'환급']
        }
        
        for category, category_patterns in patterns.items():
            for pattern in category_patterns:
                if re.search(pattern, latex):
                    return category
        
        return 'general'
    
    def _analyze_variables(self, latex: str, context: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """변수 분석"""
        variables = {}
        
        # LaTeX에서 변수 추출
        # 1. 일반 변수 (x, i, n, m, t 등)
        simple_vars = re.findall(r'\b([a-zA-Z])\b(?!_)', latex)
        
        # 2. 첨자 변수 (x_t, q_x 등)
        subscript_vars = re.findall(r'([a-zA-Z])_\{?([^}]+)\}?', latex)
        
        # 3. 특수 기호
        special_vars = re.findall(r'([α-ωΑ-Ω])', latex)
        
        # 변수 정보 생성
        all_vars = set(simple_vars + [v[0] for v in subscript_vars] + special_vars)
        
        for var in all_vars:
            var_info = self._get_variable_info(var, latex, context)
            variables[var] = var_info
        
        # 첨자 변수 추가 처리
        for base, subscript in subscript_vars:
            full_var = f"{base}_{{{subscript}}}"
            var_info = self._get_variable_info(full_var, latex, context)
            variables[full_var] = var_info
        
        return variables
    
    def _get_variable_info(self, var: str, latex: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """변수 정보 획득"""
        # 기본 정보
        info = {
            'description': '',
            'type': 'float',
            'constraints': {}
        }
        
        # 보험 기호 사전에서 찾기
        if var in self.insurance_symbols:
            symbol_info = self.insurance_symbols[var]
            info['description'] = symbol_info['name']
            
            # 타입별 제약사항
            if symbol_info['type'] == 'mortality':
                info['constraints'] = {'min': 0, 'max': 1}
            elif symbol_info['type'] == 'interest':
                info['constraints'] = {'min': -0.99, 'max': 1}
            elif symbol_info['type'] in ['premium', 'reserve', 'annuity']:
                info['constraints'] = {'min': 0}
        
        # 컨텍스트에서 추가 정보
        if 'variables' in context and var in context['variables']:
            info['description'] = context['variables'][var]
        
        # 특수 변수 처리
        if var in ['x', 'y', 'z']:
            info['description'] = '연령' if var == 'x' else '변수'
            info['type'] = 'int' if var == 'x' else 'float'
            if var == 'x':
                info['constraints'] = {'min': 0, 'max': 120}
        elif var in ['n', 'm', 't', 'k']:
            info['description'] = {
                'n': '보험기간',
                'm': '납입기간',
                't': '경과기간',
                'k': '이연기간'
            }.get(var, '기간')
            info['type'] = 'int'
            info['constraints'] = {'min': 0}
        elif var == 'i':
            info['description'] = '이율'
            info['constraints'] = {'min': -0.99, 'max': 1}
        
        return info
    
    def _generate_insurance_python_code(self, latex: str, 
                                      variables: Dict[str, Dict[str, Any]], 
                                      category: str) -> str:
        """보험 특화 Python 코드 생성"""
        # 함수명 생성
        func_name = f"insurance_{category}_{hash(latex) & 0x7FFFFFFF}"
        
        # 변수 파라미터
        params = []
        param_docs = []
        validations = []
        
        for var_name, var_info in variables.items():
            # 파라미터명 정리
            clean_name = var_name.replace('_', '').replace('{', '').replace('}', '')
            params.append(clean_name)
            
            # 문서화
            param_docs.append(
                f"    {clean_name} : {var_info['type']} - {var_info['description']}"
            )
            
            # 검증 코드
            constraints = var_info.get('constraints', {})
            if 'min' in constraints:
                validations.append(
                    f"    if {clean_name} < {constraints['min']}:\n"
                    f"        raise ValueError('{clean_name}는 {constraints['min']} 이상이어야 합니다')"
                )
            if 'max' in constraints:
                validations.append(
                    f"    if {clean_name} > {constraints['max']}:\n"
                    f"        raise ValueError('{clean_name}는 {constraints['max']} 이하여야 합니다')"
                )
        
        # LaTeX를 Python 표현식으로 변환
        python_expr = self._latex_to_python_expression(latex, variables)
        
        # 완전한 함수 생성
        code = f'''
def {func_name}({', '.join(params)}):
    """
    {category.upper()} 계산
    LaTeX: {latex}
    
    Parameters:
    -----------
{chr(10).join(param_docs)}
    
    Returns:
    --------
    float : 계산 결과
    """
    import numpy as np
    from math import *
    from decimal import Decimal, getcontext
    
    # 정밀도 설정
    getcontext().prec = 10
    
    # 입력값 검증
{chr(10).join(validations) if validations else '    pass'}
    
    try:
        # 계산 수행
        result = {python_expr}
        
        # 결과 검증
        if not isinstance(result, (int, float, Decimal)):
            raise ValueError("계산 결과가 숫자가 아닙니다")
        
        # 카테고리별 추가 검증
        {self._get_category_validation(category)}
        
        return float(result)
        
    except ZeroDivisionError:
        raise ValueError("0으로 나누기 오류가 발생했습니다")
    except Exception as e:
        raise ValueError(f"계산 오류: {{str(e)}}")
'''
        
        return code
    
    def _latex_to_python_expression(self, latex: str, variables: Dict[str, Dict[str, Any]]) -> str:
        """LaTeX를 Python 표현식으로 변환"""
        expr = latex
        
        # = 제거 (수식의 좌변 제거)
        if '=' in expr:
            expr = expr.split('=', 1)[1].strip()
        
        # 기본 변환
        replacements = {
            r'\\frac\{([^}]+)\}\{([^}]+)\}': r'((\1) / (\2))',
            r'\\sqrt\{([^}]+)\}': r'np.sqrt(\1)',
            r'\\times': '*',
            r'\\div': '/',
            r'\\cdot': '*',
            r'\^': '**',
            r'\\sum': 'sum',
            r'\\prod': 'np.prod',
            r'\\max': 'max',
            r'\\min': 'min',
            r'\\exp': 'np.exp',
            r'\\ln': 'np.log',
            r'\\log': 'np.log10'
        }
        
        for pattern, replacement in replacements.items():
            expr = re.sub(pattern, replacement, expr)
        
        # 첨자 처리
        expr = re.sub(r'([a-zA-Z])_\{([^}]+)\}', r'\1_\2', expr)
        expr = re.sub(r'([a-zA-Z])_([a-zA-Z0-9])', r'\1_\2', expr)
        
        # 변수명 정리
        for var_name in variables:
            clean_name = var_name.replace('_', '').replace('{', '').replace('}', '')
            if var_name != clean_name:
                expr = expr.replace(var_name, clean_name)
        
        # 특수 보험 기호 처리
        expr = expr.replace('α', 'alpha')
        expr = expr.replace('β', 'beta')
        expr = expr.replace('γ', 'gamma')
        
        return expr
    
    def _get_category_validation(self, category: str) -> str:
        """카테고리별 결과 검증 코드"""
        validations = {
            'premium': '''
        if result < 0:
            raise ValueError("보험료는 음수가 될 수 없습니다")''',
            
            'reserve': '''
        if result < 0:
            logger.warning("책임준비금이 음수입니다. 검토가 필요합니다.")''',
            
            'mortality': '''
        if not 0 <= result <= 1:
            raise ValueError("위험률은 0과 1 사이여야 합니다")''',
            
            'interest': '''
        if result <= -1:
            raise ValueError("이율은 -100% 초과여야 합니다")''',
            
            'annuity': '''
        if result < 0:
            raise ValueError("연금현가는 음수가 될 수 없습니다")'''
        }
        
        return validations.get(category, '')
    
    def _generate_formula_name(self, latex: str, category: str) -> str:
        """수식 이름 생성"""
        # 카테고리별 기본 이름
        base_names = {
            'premium': '보험료',
            'reserve': '책임준비금',
            'mortality': '위험률',
            'interest': '이율',
            'annuity': '연금',
            'insurance': '보험금',
            'surrender': '해지환급금'
        }
        
        base_name = base_names.get(category, '수식')
        
        # LaTeX에서 추가 정보 추출
        if 'frac' in latex:
            base_name += ' 계산식'
        elif '_t' in latex or '_\{t\}' in latex:
            base_name = f't년도 {base_name}'
        elif '_x' in latex:
            base_name = f'x세 {base_name}'
        
        return base_name
    
    def _generate_test_cases(self, category: str, variables: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """테스트 케이스 생성"""
        test_cases = []
        
        # 카테고리별 기본 테스트 케이스
        if category == 'premium':
            test_cases.append({
                'description': '정상 케이스',
                'inputs': self._generate_normal_inputs(variables),
                'expected_range': {'min': 0, 'max': 1}
            })
        elif category == 'mortality':
            test_cases.append({
                'description': '젊은 연령',
                'inputs': {'x': 30, **self._generate_normal_inputs(variables)},
                'expected_range': {'min': 0, 'max': 0.01}
            })
            test_cases.append({
                'description': '고령',
                'inputs': {'x': 80, **self._generate_normal_inputs(variables)},
                'expected_range': {'min': 0, 'max': 0.2}
            })
        
        # 경계값 테스트
        test_cases.append({
            'description': '최소값 테스트',
            'inputs': self._generate_min_inputs(variables),
            'expected_range': {'min': 0}
        })
        
        return test_cases
    
    def _generate_normal_inputs(self, variables: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """정상 입력값 생성"""
        inputs = {}
        
        for var_name, var_info in variables.items():
            clean_name = var_name.replace('_', '').replace('{', '').replace('}', '')
            
            if var_info['type'] == 'int':
                if 'x' in var_name:
                    inputs[clean_name] = 40
                elif var_name in ['n', 'm']:
                    inputs[clean_name] = 20
                elif var_name == 't':
                    inputs[clean_name] = 10
                else:
                    inputs[clean_name] = 1
            else:  # float
                if 'q' in var_name:  # 위험률
                    inputs[clean_name] = 0.001
                elif var_name == 'i':  # 이율
                    inputs[clean_name] = 0.025
                elif 'P' in var_name:  # 보험료
                    inputs[clean_name] = 0.1
                else:
                    inputs[clean_name] = 1.0
        
        return inputs
    
    def _generate_min_inputs(self, variables: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """최소 입력값 생성"""
        inputs = {}
        
        for var_name, var_info in variables.items():
            clean_name = var_name.replace('_', '').replace('{', '').replace('}', '')
            constraints = var_info.get('constraints', {})
            
            if 'min' in constraints:
                inputs[clean_name] = constraints['min'] + 0.001
            else:
                inputs[clean_name] = 0.001
        
        return inputs
    
    def _validate_formula(self, formula: InsuranceFormula) -> Dict[str, Any]:
        """수식 검증"""
        errors = []
        warnings = []
        
        # 1. LaTeX 구조 검증
        if not self._validate_latex_structure(formula.latex):
            errors.append("LaTeX 구조가 올바르지 않습니다")
        
        # 2. Python 코드 검증
        try:
            compile(formula.python_function, '<string>', 'exec')
        except SyntaxError as e:
            errors.append(f"Python 문법 오류: {e}")
        
        # 3. 테스트 케이스 실행
        if formula.test_cases:
            test_results = self._run_test_cases(formula)
            if not all(r['passed'] for r in test_results):
                warnings.append("일부 테스트 케이스 실패")
        
        # 4. 변수 검증
        if not formula.variables:
            warnings.append("변수 정보가 없습니다")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def _validate_latex_structure(self, latex: str) -> bool:
        """LaTeX 구조 검증"""
        # 괄호 균형
        if latex.count('{') != latex.count('}'):
            return False
        if latex.count('(') != latex.count(')'):
            return False
        if latex.count('[') != latex.count(']'):
            return False
        
        # 기본 구조
        if not latex.strip():
            return False
        
        return True
    
    def _run_test_cases(self, formula: InsuranceFormula) -> List[Dict[str, Any]]:
        """테스트 케이스 실행"""
        results = []
        
        # 함수 준비
        namespace = {}
        exec(formula.python_function, namespace)
        func_name = next(k for k in namespace if k.startswith('insurance_'))
        func = namespace[func_name]
        
        for test_case in formula.test_cases:
            try:
                result = func(**test_case['inputs'])
                
                passed = True
                if 'expected' in test_case:
                    passed = abs(result - test_case['expected']) < 0.0001
                elif 'expected_range' in test_case:
                    range_info = test_case['expected_range']
                    if 'min' in range_info:
                        passed &= result >= range_info['min']
                    if 'max' in range_info:
                        passed &= result <= range_info['max']
                
                results.append({
                    'test_case': test_case['description'],
                    'passed': passed,
                    'result': result
                })
                
            except Exception as e:
                results.append({
                    'test_case': test_case['description'],
                    'passed': False,
                    'error': str(e)
                })
        
        return results
    
    def save_to_database(self, formula: InsuranceFormula, db_path: Path):
        """데이터베이스에 저장"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 테이블 생성
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS insurance_formulas (
                formula_id TEXT PRIMARY KEY,
                name TEXT,
                description TEXT,
                category TEXT,
                latex TEXT,
                python_function TEXT,
                variables TEXT,
                dependencies TEXT,
                test_cases TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 데이터 저장
        cursor.execute('''
            INSERT OR REPLACE INTO insurance_formulas
            (formula_id, name, description, category, latex, python_function,
             variables, dependencies, test_cases, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            formula.formula_id,
            formula.name,
            formula.description,
            formula.category,
            formula.latex,
            formula.python_function,
            json.dumps(formula.variables, ensure_ascii=False),
            json.dumps(formula.dependencies, ensure_ascii=False),
            json.dumps(formula.test_cases, ensure_ascii=False),
            json.dumps(formula.metadata, ensure_ascii=False)
        ))
        
        conn.commit()
        conn.close()
    
    def load_from_database(self, formula_id: str, db_path: Path) -> Optional[InsuranceFormula]:
        """데이터베이스에서 로드"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM insurance_formulas WHERE formula_id = ?
        ''', (formula_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return InsuranceFormula(
                formula_id=row[0],
                name=row[1],
                description=row[2],
                category=row[3],
                latex=row[4],
                python_function=row[5],
                variables=json.loads(row[6]),
                dependencies=json.loads(row[7]),
                test_cases=json.loads(row[8]),
                metadata=json.loads(row[9])
            )
        
        return None
    
    def execute_formula(self, formula: InsuranceFormula, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """수식 실행"""
        try:
            # 함수 준비
            namespace = {}
            exec(formula.python_function, namespace)
            func_name = next(k for k in namespace if k.startswith('insurance_'))
            func = namespace[func_name]
            
            # 입력값 검증
            for var_name, var_info in formula.variables.items():
                clean_name = var_name.replace('_', '').replace('{', '').replace('}', '')
                
                if clean_name not in inputs:
                    raise ValueError(f"필수 입력값 누락: {clean_name}")
                
                # 타입 검증
                value = inputs[clean_name]
                if var_info['type'] == 'int' and not isinstance(value, int):
                    inputs[clean_name] = int(value)
            
            # 실행
            result = func(**inputs)
            
            return {
                'success': True,
                'result': result,
                'formula_id': formula.formula_id,
                'inputs': inputs
            }
            
        except Exception as e:
            logger.error(f"수식 실행 오류: {e}")
            return {
                'success': False,
                'error': str(e),
                'formula_id': formula.formula_id,
                'inputs': inputs
            }
    
    def generate_formula_report(self, formulas: List[InsuranceFormula]) -> str:
        """수식 보고서 생성"""
        report = []
        report.append("# 보험 수식 분석 보고서\n")
        report.append(f"생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report.append(f"총 수식 수: {len(formulas)}\n")
        
        # 카테고리별 통계
        categories = {}
        for formula in formulas:
            categories[formula.category] = categories.get(formula.category, 0) + 1
        
        report.append("\n## 카테고리별 분포\n")
        for category, count in sorted(categories.items()):
            report.append(f"- {category}: {count}개\n")
        
        # 수식 상세
        report.append("\n## 수식 상세\n")
        for i, formula in enumerate(formulas, 1):
            report.append(f"\n### {i}. {formula.name}\n")
            report.append(f"- ID: {formula.formula_id}\n")
            report.append(f"- 카테고리: {formula.category}\n")
            report.append(f"- LaTeX: `{formula.latex}`\n")
            report.append(f"- 변수: {', '.join(formula.variables.keys())}\n")
            
            if formula.test_cases:
                report.append(f"- 테스트 케이스: {len(formula.test_cases)}개\n")
            
            if 'validation_errors' in formula.metadata:
                report.append(f"- ⚠️ 검증 오류: {formula.metadata['validation_errors']}\n")
        
        return ''.join(report)