"""
OCR Engines 모듈
"""

# 각 엔진을 개별적으로 import
try:
    from .base_ocr import BaseOCR
except ImportError:
    BaseOCR = None

try:
    from .tesseract_ocr import TesseractOCR
except ImportError:
    TesseractOCR = None

try:
    from .easyocr_engine import EasyOCREngine
except ImportError:
    EasyOCREngine = None

try:
    from .paddleocr_engine import PaddleOCREngine
except ImportError:
    PaddleOCREngine = None

try:
    from .trocr_engine import TrOCREngine
except ImportError:
    TrOCREngine = None

__all__ = [
    'BaseOCR',
    'TesseractOCR',
    'EasyOCREngine',
    'PaddleOCREngine',
    'TrOCREngine'
]
