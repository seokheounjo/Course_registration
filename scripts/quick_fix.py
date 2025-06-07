"""
빠른 수정 스크립트 - __init__.py 파일 생성
"""

from pathlib import Path

# __init__.py 파일 내용
init_contents = {
    "core": '''"""
Core 모듈
"""

from .config import Config, OCREngine, OutputFormat
from .document_analyzer import DocumentAnalyzer
from .result import AnalysisResult

__all__ = [
    'Config',
    'OCREngine', 
    'OutputFormat',
    'DocumentAnalyzer',
    'AnalysisResult'
]
''',
    "processors": '''"""
Processors 모듈
"""

from .text_processor import TextProcessor
from .table_processor import TableProcessor
from .formula_processor import FormulaProcessor
from .term_processor import FinancialTermProcessor
from .layout_processor import LayoutProcessor
from .csv_exporter import CSVExporter

__all__ = [
    'TextProcessor',
    'TableProcessor', 
    'FormulaProcessor',
    'FinancialTermProcessor',
    'LayoutProcessor',
    'CSVExporter'
]
''',
    "ocr_engines": '''"""
OCR Engines 모듈
"""

from .base_ocr import BaseOCR
from .tesseract_ocr import TesseractOCR
from .easyocr_engine import EasyOCREngine
from .paddleocr_engine import PaddleOCREngine
from .trocr_engine import TrOCREngine

__all__ = [
    'BaseOCR',
    'TesseractOCR',
    'EasyOCREngine',
    'PaddleOCREngine',
    'TrOCREngine'
]
''',
    "utils": '''"""
Utils 모듈
"""

from .file_utils import FileUtils
from .image_utils import ImageUtils
from .logging_utils import LoggingUtils
from .validator import DocumentValidator

__all__ = [
    'FileUtils',
    'ImageUtils',
    'LoggingUtils',
    'DocumentValidator'
]
'''
}

def create_init_files():
    """모든 __init__.py 파일 생성"""
    
    print("__init__.py 파일 생성 중...")
    
    for dir_name, content in init_contents.items():
        dir_path = Path(dir_name)
        
        # 디렉토리 생성
        dir_path.mkdir(exist_ok=True)
        
        # __init__.py 파일 생성
        init_file = dir_path / "__init__.py"
        init_file.write_text(content, encoding='utf-8')
        
        print(f"✅ {init_file} 생성 완료")
    
    # 필요한 디렉토리 생성
    dirs_to_create = [
        "documents",
        "output",
        "output/csv",
        "output/individual", 
        "output/logs",
        "cache",
        "data",
        "data/terms"
    ]
    
    for dir_name in dirs_to_create:
        Path(dir_name).mkdir(parents=True, exist_ok=True)
        print(f"✅ {dir_name}/ 디렉토리 생성")
    
    print("\n✅ 모든 파일 생성 완료!")
    print("\n이제 다음 명령어를 실행하세요:")
    print("  python main.py documents/ --ocr-engine easyocr")

if __name__ == "__main__":
    create_init_files()