# core/enhanced_config.py
"""
향상된 설정 관리 모듈
"""

import logging
from pathlib import Path
from enum import Enum
from typing import List, Dict, Any, Optional
import json
import os
from datetime import datetime

class OCREngine(Enum):
    """OCR 엔진 종류"""
    TROCR = "trocr"
    PADDLEOCR = "paddleocr"
    EASYOCR = "easyocr"
    TESSERACT = "tesseract"

class OutputFormat(Enum):
    """출력 형식"""
    JSON = "json"
    CSV = "csv"
    EXCEL = "excel"
    HTML = "html"

class LayoutModel(Enum):
    """레이아웃 분석 모델"""
    LAYOUTLMV3 = "layoutlmv3"
    DETECTRON2 = "detectron2"
    YOLO = "yolo"
    RULE_BASED = "rule_based"

class Config:
    """향상된 설정 클래스"""
    
    def __init__(self, config_file: Optional[Path] = None):
        # 기본 경로
        self.project_root = Path(__file__).parent.parent
        self.output_dir = self.project_root / "output"
        self.cache_dir = self.project_root / "cache"
        self.model_dir = self.project_root / "models"
        self.resource_dir = self.project_root / "resources"
        
        # 디렉토리 생성
        for dir_path in [self.output_dir, self.cache_dir, self.model_dir, self.resource_dir]:
            dir_path.mkdir(exist_ok=True)
        
        # 기본 설정
        self._set_defaults()
        
        # 설정 파일 로드
        if config_file and config_file.exists():
            self._load_config(config_file)
        else:
            # 기본 설정 파일 확인
            default_config = self.project_root / "config.json"
            if default_config.exists():
                self._load_config(default_config)
    
    def _set_defaults(self):
        """기본 설정값"""
        # PDF 처리
        self.dpi = 200
        self.pdf_password = None
        self.max_pages = None  # None이면 모든 페이지
        
        # OCR 설정
        self.ocr_engine = OCREngine.PADDLEOCR
        self.ocr_languages = ["ko", "en"]
        self.ocr_confidence_threshold = 0.5
        
        # 레이아웃 분석
        self.layout_model = LayoutModel.RULE_BASED
        self.layout_confidence_threshold = 0.5
        
        # 수식 추출
        self.detect_korean_formulas = True
        self.formula_confidence_threshold = 0.5
        self.use_pix2text = True
        self.formula_extraction_methods = ["cv", "layout", "text"]
        
        # 보험 수식 처리
        self.process_insurance_formulas = True
        self.validate_formulas = True
        self.generate_test_cases = True
        
        # 한국어 처리
        self.korean_nlp_enabled = True
        self.korean_nlp_backend = "okt"  # okt, kkma, hannanum
        
        # 금융 용어
        self.extract_financial_terms = True
        self.financial_terms_file = self.resource_dir / "financial_terms.json"
        
        # 테이블 추출
        self.extract_tables = True
        self.min_table_area = 10000
        self.min_table_rows = 2
        self.min_table_cols = 2
        
        # 출력 설정
        self.output_formats = [OutputFormat.JSON, OutputFormat.CSV]
        self.save_intermediate_images = False
        self.compress_output = False
        
        # 성능 설정
        self.batch_size = 5
        self.max_workers = 1
        self.use_gpu = True
        self.device = "cuda" if self.use_gpu else "cpu"
        self.memory_limit_gb = 8
        
        # 캐시 설정
        self.use_cache = True
        self.cache_expiry_days = 30
        
        # 로깅 설정
        self.log_level = "INFO"
        self.log_file = self.output_dir / f"analysis_{datetime.now().strftime('%Y%m%d')}.log"
        self.log_to_file = True
        self.log_to_console = True
        
        # 한글 수식 패턴
        self.korean_formula_patterns = self._load_korean_formula_patterns()
        
        # API 설정
        self.api_host = "0.0.0.0"
        self.api_port = 8000
        self.api_workers = 4
        self.api_cors_enabled = True
        
        # 데이터베이스 설정
        self.db_path = self.output_dir / "formula_database.db"
        self.db_backup_enabled = True
        self.db_backup_interval_days = 7
    
    def _load_korean_formula_patterns(self) -> Dict[str, Any]:
        """한글 수식 패턴 로드"""
        patterns = {
            "contextual_indicators": {
                "formula_start": [
                    "다음과 같이", "아래와 같이", "다음 식", "다음의 식",
                    "식은 다음과", "계산식은", "산출식은", "공식은"
                ],
                "formula_end": ["이다", "입니다", "됩니다", "된다"],
                "variable_definition": ["여기서", "단,", "여기에서", "이때"],
            },
            "operator_patterns": {
                "korean_operators": {
                    "더하기": "+", "플러스": "+", "빼기": "-", "마이너스": "-",
                    "곱하기": "*", "곱셈": "*", "나누기": "/", "나눗셈": "/",
                    "제곱": "^", "루트": "sqrt", "제곱근": "sqrt"
                }
            },
            "number_patterns": {
                "korean_numbers": {
                    "영": "0", "일": "1", "이": "2", "삼": "3", "사": "4",
                    "오": "5", "육": "6", "칠": "7", "팔": "8", "구": "9",
                    "십": "10", "백": "100", "천": "1000", "만": "10000",
                    "억": "100000000", "조": "1000000000000"
                }
            },
            "formula_patterns": {
                "premium_calculation": {
                    "patterns": [
                        r"보험료\s*=",
                        r"P\s*=",
                        r"영업보험료\s*=",
                        r"순보험료\s*="
                    ],
                    "standard_form": "P = (formula)"
                },
                "reserve_calculation": {
                    "patterns": [
                        r"책임준비금\s*=",
                        r"V\s*=",
                        r"준비금\s*=",
                        r"적립금\s*="
                    ],
                    "standard_form": "V = (formula)"
                }
            },
            "mathematical_terms": {
                "korean_to_latex": {
                    "분의": "\\frac",
                    "루트": "\\sqrt",
                    "시그마": "\\sum",
                    "인테그랄": "\\int",
                    "파이": "\\pi",
                    "세타": "\\theta",
                    "알파": "\\alpha",
                    "베타": "\\beta",
                    "감마": "\\gamma"
                }
            },
            "financial_terms": {
                "korean_to_symbol": {
                    "현재가치": "PV",
                    "미래가치": "FV",
                    "이자율": "i",
                    "할인율": "d",
                    "기간": "n",
                    "납입기간": "m",
                    "보험기간": "n"
                }
            },
            "preprocessing_rules": [
                {
                    "pattern": r"(\d+)\s*분의\s*(\d+)",
                    "replacement": r"\\frac{\2}{\1}",
                    "description": "한글 분수 표현을 LaTeX로"
                }
            ]
        }
        
        # 패턴 파일이 있으면 로드
        patterns_file = self.resource_dir / "korean_formula_patterns.json"
        if patterns_file.exists():
            try:
                with open(patterns_file, 'r', encoding='utf-8') as f:
                    loaded_patterns = json.load(f)
                    patterns.update(loaded_patterns)
            except Exception as e:
                logging.warning(f"패턴 파일 로드 실패: {e}")
        
        return patterns
    
    def _load_config(self, config_file: Path):
        """설정 파일 로드"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # 설정 업데이트
            for key, value in config_data.items():
                if hasattr(self, key):
                    # Enum 처리
                    if key == 'ocr_engine':
                        setattr(self, key, OCREngine[value.upper()])
                    elif key == 'layout_model':
                        setattr(self, key, LayoutModel[value.upper()])
                    elif key == 'output_formats':
                        formats = [OutputFormat[fmt.upper()] for fmt in value]
                        setattr(self, key, formats)
                    else:
                        setattr(self, key, value)
            
            logging.info(f"설정 파일 로드 완료: {config_file}")
            
        except Exception as e:
            logging.error(f"설정 파일 로드 실패: {e}")
    
    def save_config(self, config_file: Optional[Path] = None):
        """설정 저장"""
        if config_file is None:
            config_file = self.project_root / "config.json"
        
        config_data = {}
        
        # 저장할 속성들
        save_attrs = [
            'dpi', 'ocr_confidence_threshold', 'formula_confidence_threshold',
            'korean_nlp_enabled', 'extract_financial_terms', 'extract_tables',
            'batch_size', 'max_workers', 'use_gpu', 'use_cache',
            'log_level', 'api_port'
        ]
        
        for attr in save_attrs:
            if hasattr(self, attr):
                value = getattr(self, attr)
                # Enum 처리
                if isinstance(value, Enum):
                    value = value.value
                elif isinstance(value, list) and value and isinstance(value[0], Enum):
                    value = [v.value for v in value]
                elif isinstance(value, Path):
                    value = str(value)
                
                config_data[attr] = value
        
        # 저장
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
        
        logging.info(f"설정 저장 완료: {config_file}")
    
    def setup_logging(self) -> logging.Logger:
        """로깅 설정"""
        # 로거 설정
        logger = logging.getLogger()
        logger.setLevel(getattr(logging, self.log_level))
        
        # 기존 핸들러 제거
        logger.handlers = []
        
        # 포맷터
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # 콘솔 핸들러
        if self.log_to_console:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        # 파일 핸들러
        if self.log_to_file:
            file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        return logger
    
    def get_output_path(self, document_id: str, extension: str, 
                       filename: Optional[str] = None) -> Path:
        """출력 파일 경로 생성"""
        # 문서별 디렉토리
        doc_dir = self.output_dir / document_id
        doc_dir.mkdir(exist_ok=True)
        
        if filename:
            return doc_dir / filename
        else:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            return doc_dir / f"{document_id}_{timestamp}.{extension}"
    
    def validate_environment(self) -> Dict[str, Any]:
        """환경 검증"""
        validation = {
            'valid': True,
            'issues': [],
            'warnings': []
        }
        
        # GPU 확인
        if self.use_gpu:
            try:
                import torch
                if not torch.cuda.is_available():
                    validation['warnings'].append("GPU를 사용하도록 설정되었지만 CUDA를 사용할 수 없습니다")
                    self.device = "cpu"
            except ImportError:
                validation['warnings'].append("PyTorch가 설치되지 않았습니다")
        
        # OCR 엔진 확인
        if self.ocr_engine == OCREngine.PADDLEOCR:
            try:
                import paddleocr
            except ImportError:
                validation['issues'].append("PaddleOCR가 설치되지 않았습니다")
                validation['valid'] = False
        
        # 디렉토리 쓰기 권한
        for dir_path in [self.output_dir, self.cache_dir]:
            if not os.access(dir_path, os.W_OK):
                validation['issues'].append(f"디렉토리에 쓰기 권한이 없습니다: {dir_path}")
                validation['valid'] = False
        
        # 메모리 확인
        try:
            import psutil
            available_memory = psutil.virtual_memory().available / (1024**3)  # GB
            if available_memory < 2:
                validation['warnings'].append(f"사용 가능한 메모리가 부족합니다: {available_memory:.1f}GB")
        except ImportError:
            pass
        
        return validation
    
    def __repr__(self):
        return (
            f"Config(ocr_engine={self.ocr_engine.value}, "
            f"formula_confidence={self.formula_confidence_threshold}, "
            f"output_dir={self.output_dir})"
        )