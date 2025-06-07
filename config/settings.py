# config/settings.py
"""
금융 PDF 분석기 설정 파일
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from enum import Enum
import json
import logging

class ModelType(Enum):
    """레이아웃 분석 모델 타입"""
    LAYOUTLMV3 = "layoutlmv3"
    DONUT = "donut"
    DIT = "dit"

class OCREngine(Enum):
    """OCR 엔진 타입"""
    TROCR = "trocr"
    PADDLEOCR = "paddleocr"
    EASYOCR = "easyocr"
    TESSERACT = "tesseract"

class OutputFormat(Enum):
    """출력 형식"""
    JSON = "json"
    CSV = "csv"
    EXCEL = "excel"
    DATABASE = "database"
    ALL = "all"

@dataclass
class Config:
    """통합 설정 클래스"""
    # 기본 경로
    project_root: Path = field(default_factory=lambda: Path(__file__).parent.parent)
    data_dir: Path = field(init=False)
    output_dir: Path = field(init=False)
    cache_dir: Path = field(init=False)
    log_dir: Path = field(init=False)
    resources_dir: Path = field(init=False)
    
    # 모델 설정
    layout_model: ModelType = ModelType.LAYOUTLMV3
    ocr_engine: OCREngine = OCREngine.PADDLEOCR
    device: str = "cuda"  # "cuda" or "cpu"
    
    # 처리 설정
    dpi: int = 300
    batch_size: int = 4
    max_workers: int = 4
    use_cache: bool = True
    cache_expiry_days: int = 7
    
    # 한국어 처리 설정
    korean_nlp_enabled: bool = True
    detect_korean_formulas: bool = True
    extract_financial_terms: bool = True
    
    # 출력 설정
    output_format: OutputFormat = OutputFormat.ALL
    save_intermediate_results: bool = True
    generate_visualization: bool = True
    
    # 데이터베이스 설정
    db_enabled: bool = False
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "financial_docs"
    db_user: str = "postgres"
    db_password: str = ""
    
    # 로깅 설정
    log_level: str = "INFO"
    log_to_file: bool = True
    
    # 금융 문서 특화 설정
    financial_patterns: Dict[str, Any] = field(default_factory=dict)
    korean_formula_patterns: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """초기화 후 처리"""
        # 디렉토리 설정
        self.data_dir = self.project_root / "data"
        self.output_dir = self.project_root / "output"
        self.cache_dir = self.project_root / "cache"
        self.log_dir = self.project_root / "logs"
        self.resources_dir = self.project_root / "resources"
        
        # 디렉토리 생성
        for dir_path in [self.data_dir, self.output_dir, self.cache_dir, 
                        self.log_dir, self.resources_dir]:
            dir_path.mkdir(exist_ok=True)
        
        # 출력 하위 디렉토리 생성
        (self.output_dir / "csv").mkdir(exist_ok=True)
        (self.output_dir / "individual").mkdir(exist_ok=True)
        (self.output_dir / "db_postgresql").mkdir(exist_ok=True)
        
        # 리소스 파일 로드
        self._load_resources()
    
    def _load_resources(self):
        """리소스 파일 로드"""
        # 한글 수식 패턴 로드
        formula_pattern_file = self.resources_dir / "korean_formula_patterns.json"
        if formula_pattern_file.exists():
            with open(formula_pattern_file, 'r', encoding='utf-8') as f:
                self.korean_formula_patterns = json.load(f)
        
        # 금융 용어 패턴 로드
        financial_terms_file = self.resources_dir / "financial_terms.json"
        if financial_terms_file.exists():
            with open(financial_terms_file, 'r', encoding='utf-8') as f:
                self.financial_patterns = json.load(f)
    
    def get_output_path(self, doc_id: str, file_type: str, extension: str) -> Path:
        """출력 파일 경로 생성"""
        if file_type == "csv":
            return self.output_dir / "csv" / f"{doc_id}.{extension}"
        elif file_type == "individual":
            doc_dir = self.output_dir / "individual" / doc_id
            doc_dir.mkdir(exist_ok=True)
            return doc_dir / f"{doc_id}.{extension}"
        else:
            return self.output_dir / f"{doc_id}.{extension}"
    
    def setup_logging(self) -> logging.Logger:
        """로깅 설정"""
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        handlers = []
        
        # 콘솔 핸들러
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(log_format))
        handlers.append(console_handler)
        
        # 파일 핸들러
        if self.log_to_file:
            from datetime import datetime
            log_file = self.log_dir / f"financial_analyzer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(logging.Formatter(log_format))
            handlers.append(file_handler)
        
        # 로거 설정
        logging.basicConfig(
            level=getattr(logging, self.log_level),
            handlers=handlers
        )
        
        # 외부 라이브러리 로깅 레벨 조정
        for lib in ['transformers', 'torch', 'PIL']:
            logging.getLogger(lib).setLevel(logging.WARNING)
        
        return logging.getLogger('financial_pdf_analyzer')
    
    def to_dict(self) -> Dict[str, Any]:
        """설정을 딕셔너리로 변환"""
        return {
            "layout_model": self.layout_model.value,
            "ocr_engine": self.ocr_engine.value,
            "device": self.device,
            "dpi": self.dpi,
            "batch_size": self.batch_size,
            "max_workers": self.max_workers,
            "korean_nlp_enabled": self.korean_nlp_enabled,
            "output_format": self.output_format.value,
            "db_enabled": self.db_enabled
        }
    
    @classmethod
    def from_env(cls) -> 'Config':
        """환경 변수에서 설정 로드"""
        from dotenv import load_dotenv
        load_dotenv()
        
        config = cls()
        
        # 환경 변수 오버라이드
        if os.getenv('DB_HOST'):
            config.db_host = os.getenv('DB_HOST')
        if os.getenv('DB_PORT'):
            config.db_port = int(os.getenv('DB_PORT'))
        if os.getenv('DB_NAME'):
            config.db_name = os.getenv('DB_NAME')
        if os.getenv('DB_USER'):
            config.db_user = os.getenv('DB_USER')
        if os.getenv('DB_PASSWORD'):
            config.db_password = os.getenv('DB_PASSWORD')
        
        return config