"""
설정 관리 모듈 - GPU 지원 및 진행 상황 표시 개선
"""

import os
import json
import logging
import torch
import platform
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from tqdm import tqdm
import psutil

class OCREngine(Enum):
    """OCR 엔진 종류"""
    PADDLEOCR = "paddleocr"
    EASYOCR = "easyocr"
    TESSERACT = "tesseract"
    TROCR = "trocr"

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
    RULE_BASED = "rule_based"

@dataclass
class Config:
    """전체 설정 클래스"""
    
    # 경로 설정
    project_root: Path = field(default_factory=lambda: Path(__file__).parent.parent)
    output_dir: Path = field(default_factory=lambda: Path("output"))
    cache_dir: Path = field(default_factory=lambda: Path("cache"))
    data_dir: Path = field(default_factory=lambda: Path("data"))
    
    # OCR 설정
    ocr_engine: OCREngine = OCREngine.EASYOCR
    ocr_languages: List[str] = field(default_factory=lambda: ["ko", "en"])
    
    # 레이아웃 분석 설정
    layout_model: LayoutModel = LayoutModel.RULE_BASED
    
    # 처리 설정
    dpi: int = 200
    batch_size: int = 5
    max_workers: int = 1
    device: str = "auto"  # "auto", "cuda", "cpu"
    gpu_memory_fraction: float = 0.8  # GPU 메모리 사용 비율
    
    # 기능 설정
    extract_tables: bool = True
    extract_formulas: bool = True
    extract_financial_terms: bool = True
    detect_korean_formulas: bool = True
    korean_nlp_enabled: bool = True
    
    # 출력 설정
    output_formats: List[OutputFormat] = field(default_factory=lambda: [OutputFormat.CSV, OutputFormat.JSON])
    save_intermediate: bool = False
    compress_output: bool = False
    
    # 로깅 설정
    log_level: str = "INFO"
    log_file: Optional[Path] = None
    show_progress: bool = True  # 진행 상황 표시
    
    # 캐시 설정
    use_cache: bool = True
    cache_expiry_days: int = 7
    
    # 금융 용어 및 수식 패턴
    _financial_terms: Optional[Dict[str, Any]] = None
    _korean_formula_patterns: Optional[Dict[str, Any]] = None
    
    # GPU 정보
    _gpu_info: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """초기화 후 처리"""
        # 절대 경로로 변환
        self.output_dir = self.project_root / self.output_dir
        self.cache_dir = self.project_root / self.cache_dir
        self.data_dir = self.project_root / self.data_dir
        
        # 디렉토리 생성
        self.output_dir.mkdir(exist_ok=True)
        self.cache_dir.mkdir(exist_ok=True)
        self.data_dir.mkdir(exist_ok=True)
        
        # 하위 디렉토리 생성
        (self.output_dir / "csv").mkdir(exist_ok=True)
        (self.output_dir / "individual").mkdir(exist_ok=True)
        (self.output_dir / "logs").mkdir(exist_ok=True)
        
        # 로그 파일 설정
        if self.log_file is None:
            self.log_file = self.output_dir / "logs" / "analysis.log"
        
        # GPU 설정
        self._setup_gpu()
        
        # 시스템 정보 출력
        self._print_system_info()
    
    def _setup_gpu(self):
        """GPU 설정 및 확인"""
        if self.device == "auto":
            if torch.cuda.is_available():
                self.device = "cuda"
                # GPU 메모리 설정
                torch.cuda.set_per_process_memory_fraction(self.gpu_memory_fraction)
            else:
                self.device = "cpu"
        
        # GPU 정보 수집
        if self.device == "cuda" and torch.cuda.is_available():
            self._gpu_info = {
                "available": True,
                "device_count": torch.cuda.device_count(),
                "device_name": torch.cuda.get_device_name(0),
                "memory_total": torch.cuda.get_device_properties(0).total_memory / (1024**3),  # GB
                "memory_allocated": torch.cuda.memory_allocated(0) / (1024**3),  # GB
                "memory_reserved": torch.cuda.memory_reserved(0) / (1024**3),  # GB
            }
        else:
            self._gpu_info = {"available": False}
    
    def _print_system_info(self):
        """시스템 정보 출력"""
        print("\n" + "="*60)
        print("🖥️  시스템 정보")
        print("="*60)
        
        # OS 정보
        print(f"운영체제: {platform.system()} {platform.release()}")
        print(f"Python 버전: {platform.python_version()}")
        
        # CPU 정보
        print(f"CPU 코어: {psutil.cpu_count(logical=False)}개 (논리: {psutil.cpu_count(logical=True)}개)")
        
        # 메모리 정보
        memory = psutil.virtual_memory()
        print(f"시스템 메모리: {memory.total / (1024**3):.1f}GB (사용 가능: {memory.available / (1024**3):.1f}GB)")
        
        # GPU 정보
        if self._gpu_info and self._gpu_info["available"]:
            print(f"\n🎮 GPU 정보")
            print(f"GPU 장치: {self._gpu_info['device_name']}")
            print(f"GPU 메모리: {self._gpu_info['memory_total']:.1f}GB")
            print(f"사용 설정: {self.device.upper()} (메모리 {self.gpu_memory_fraction*100:.0f}% 할당)")
            print("✅ GPU 가속이 활성화되었습니다!")
        else:
            print(f"\n⚠️  GPU를 사용할 수 없습니다. CPU 모드로 실행됩니다.")
            print("💡 팁: CUDA 지원 GPU와 PyTorch CUDA를 설치하면 처리 속도가 크게 향상됩니다.")
        
        print("="*60 + "\n")
    
    @property
    def financial_terms(self) -> Dict[str, Any]:
        """금융 용어 사전 로드"""
        if self._financial_terms is None:
            terms_file = self.data_dir / "financial_terms.json"
            if terms_file.exists():
                with open(terms_file, 'r', encoding='utf-8') as f:
                    self._financial_terms = json.load(f)
            else:
                self._financial_terms = {}
        return self._financial_terms
    
    @property
    def korean_formula_patterns(self) -> Dict[str, Any]:
        """한글 수식 패턴 로드"""
        if self._korean_formula_patterns is None:
            patterns_file = self.data_dir / "korean_formula_patterns.json"
            if patterns_file.exists():
                with open(patterns_file, 'r', encoding='utf-8') as f:
                    self._korean_formula_patterns = json.load(f)
            else:
                self._korean_formula_patterns = {}
        return self._korean_formula_patterns
    
    def get_output_path(self, document_id: str, output_type: str, filename: str) -> Path:
        """출력 파일 경로 생성"""
        if output_type == "csv":
            return self.output_dir / "csv" / f"{document_id}_{filename}"
        elif output_type == "individual":
            return self.output_dir / "individual" / document_id / filename
        else:
            return self.output_dir / filename
    
    def setup_logging(self) -> logging.Logger:
        """로깅 설정"""
        from utils.logging_utils import LoggingUtils
        
        # 로그 파일 디렉토리 확인
        if self.log_file:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        logger = LoggingUtils.setup_logger(
            name="financial_pdf_analyzer",
            log_file=self.log_file,
            level=self.log_level
        )
        
        return logger
    
    def get_gpu_memory_info(self) -> Dict[str, float]:
        """현재 GPU 메모리 상태"""
        if self.device == "cuda" and torch.cuda.is_available():
            return {
                "allocated": torch.cuda.memory_allocated(0) / (1024**3),
                "reserved": torch.cuda.memory_reserved(0) / (1024**3),
                "free": (torch.cuda.get_device_properties(0).total_memory - torch.cuda.memory_allocated(0)) / (1024**3)
            }
        return {"allocated": 0, "reserved": 0, "free": 0}
    
    def create_progress_bar(self, total: int, desc: str, unit: str = "pages") -> tqdm:
        """진행 상황 표시 바 생성"""
        if self.show_progress:
            return tqdm(
                total=total,
                desc=desc,
                unit=unit,
                ncols=100,
                bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}{postfix}]'
            )
        else:
            # 진행 상황 표시 없음
            class DummyProgress:
                def update(self, n=1): pass
                def set_postfix(self, **kwargs): pass
                def close(self): pass
            return DummyProgress()
    
    def to_dict(self) -> Dict[str, Any]:
        """설정을 딕셔너리로 변환"""
        return {
            "project_root": str(self.project_root),
            "output_dir": str(self.output_dir),
            "cache_dir": str(self.cache_dir),
            "ocr_engine": self.ocr_engine.value,
            "ocr_languages": self.ocr_languages,
            "layout_model": self.layout_model.value,
            "dpi": self.dpi,
            "batch_size": self.batch_size,
            "max_workers": self.max_workers,
            "device": self.device,
            "gpu_memory_fraction": self.gpu_memory_fraction,
            "extract_tables": self.extract_tables,
            "extract_formulas": self.extract_formulas,
            "extract_financial_terms": self.extract_financial_terms,
            "output_formats": [fmt.value for fmt in self.output_formats],
            "log_level": self.log_level,
            "show_progress": self.show_progress,
            "gpu_info": self._gpu_info
        }
    
    def save(self, filepath: Path):
        """설정 저장"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load(cls, filepath: Path) -> 'Config':
        """설정 로드"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Enum 변환
        if 'ocr_engine' in data:
            data['ocr_engine'] = OCREngine(data['ocr_engine'])
        if 'layout_model' in data:
            data['layout_model'] = LayoutModel(data['layout_model'])
        if 'output_formats' in data:
            data['output_formats'] = [OutputFormat(fmt) for fmt in data['output_formats']]
        
        # Path 변환
        for key in ['project_root', 'output_dir', 'cache_dir', 'data_dir', 'log_file']:
            if key in data and data[key]:
                data[key] = Path(data[key])
        
        # GPU 정보는 로드하지 않음 (재검사 필요)
        data.pop('gpu_info', None)
        
        return cls(**data)