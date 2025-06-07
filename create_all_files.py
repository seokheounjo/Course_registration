#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
모든 누락된 파일을 생성하는 스크립트
Unicode 인코딩 문제 해결 포함
"""

import os
import sys
from pathlib import Path

# UTF-8 인코딩 설정
if sys.platform == 'win32':
    import locale
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')

def create_file(filepath, content):
    """파일 생성 헬퍼"""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')
    print(f"✅ {filepath} 생성 완료")

def fix_encoding_in_files():
    """기존 파일들의 인코딩 문제 수정"""
    files_to_fix = [
        "scripts/check_files.py",
        "scripts/tests/test_ocr.py", 
        "scripts/tests/gpu_test.py",
        "scripts/tests/test_korean_nlp.py"
    ]
    
    for filepath in files_to_fix:
        if Path(filepath).exists():
            try:
                content = Path(filepath).read_text(encoding='utf-8')
                # 파일 시작 부분에 인코딩 선언 추가
                if not content.startswith('# -*- coding: utf-8 -*-'):
                    content = '# -*- coding: utf-8 -*-\n' + content
                Path(filepath).write_text(content, encoding='utf-8')
                print(f"✅ {filepath} 인코딩 수정")
            except Exception as e:
                print(f"⚠️  {filepath} 수정 실패: {e}")

# 1. OCR 엔진 베이스 클래스
base_ocr_content = '''# -*- coding: utf-8 -*-
"""
OCR 엔진 베이스 클래스
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from PIL import Image
import logging

class BaseOCR(ABC):
    """OCR 엔진 베이스 클래스"""
    
    def __init__(self, languages: List[str] = None, device: str = 'cpu'):
        """
        Args:
            languages: 지원 언어 리스트
            device: 'cpu' 또는 'cuda'
        """
        self.languages = languages or ['ko', 'en']
        self.device = device
        self.logger = logging.getLogger(self.__class__.__name__)
        
    @abstractmethod
    def initialize(self) -> bool:
        """OCR 엔진 초기화"""
        pass
    
    @abstractmethod
    def extract_text(self, image: np.ndarray) -> str:
        """이미지에서 텍스트 추출"""
        pass
    
    @abstractmethod
    def extract_with_bbox(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """바운딩 박스와 함께 텍스트 추출"""
        pass
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """이미지 전처리"""
        # 그레이스케일 변환 여부 확인
        if len(image.shape) == 2:
            return image
            
        # 기본 전처리
        return image
    
    def postprocess_text(self, text: str) -> str:
        """추출된 텍스트 후처리"""
        # 기본 정리
        text = text.strip()
        text = ' '.join(text.split())  # 중복 공백 제거
        
        return text
    
    def detect_text_regions(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """텍스트 영역 검출"""
        # 서브클래스에서 구현
        return []
    
    def get_confidence_threshold(self) -> float:
        """신뢰도 임계값"""
        return 0.5
'''

# 2. Tesseract OCR 엔진
tesseract_ocr_content = '''# -*- coding: utf-8 -*-
"""
Tesseract OCR 엔진
"""

import numpy as np
from typing import List, Dict, Any
import pytesseract
from PIL import Image
import cv2
import platform
from pathlib import Path

from .base_ocr import BaseOCR

class TesseractOCR(BaseOCR):
    """Tesseract OCR 엔진"""
    
    def __init__(self, languages: List[str] = None, device: str = 'cpu'):
        super().__init__(languages, device)
        self.lang_map = {
            'ko': 'kor',
            'en': 'eng',
            'ja': 'jpn',
            'zh': 'chi_sim'
        }
        
    def initialize(self) -> bool:
        """Tesseract 초기화"""
        try:
            # Windows에서 Tesseract 경로 설정
            if platform.system() == 'Windows':
                tesseract_paths = [
                    r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe',
                    r'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe',
                    r'C:\\Users\\%s\\AppData\\Local\\Tesseract-OCR\\tesseract.exe' % os.environ.get('USERNAME', '')
                ]
                
                for path in tesseract_paths:
                    if Path(path).exists():
                        pytesseract.pytesseract.tesseract_cmd = path
                        break
            
            # 버전 확인
            version = pytesseract.get_tesseract_version()
            self.logger.info(f"Tesseract 버전: {version}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Tesseract 초기화 실패: {e}")
            return False
    
    def extract_text(self, image: np.ndarray) -> str:
        """이미지에서 텍스트 추출"""
        try:
            # 언어 설정
            lang_str = '+'.join([
                self.lang_map.get(lang, lang) 
                for lang in self.languages
            ])
            
            # PIL Image로 변환
            if isinstance(image, np.ndarray):
                image = Image.fromarray(image)
            
            # OCR 실행
            text = pytesseract.image_to_string(
                image,
                lang=lang_str,
                config='--psm 3'  # 자동 페이지 분할
            )
            
            return self.postprocess_text(text)
            
        except Exception as e:
            self.logger.error(f"텍스트 추출 실패: {e}")
            return ""
    
    def extract_with_bbox(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """바운딩 박스와 함께 텍스트 추출"""
        try:
            # 언어 설정
            lang_str = '+'.join([
                self.lang_map.get(lang, lang) 
                for lang in self.languages
            ])
            
            # PIL Image로 변환
            if isinstance(image, np.ndarray):
                pil_image = Image.fromarray(image)
            else:
                pil_image = image
            
            # 상세 정보 추출
            data = pytesseract.image_to_data(
                pil_image,
                lang=lang_str,
                output_type=pytesseract.Output.DICT
            )
            
            results = []
            n_boxes = len(data['level'])
            
            for i in range(n_boxes):
                if int(data['conf'][i]) > 0:  # 신뢰도가 있는 경우만
                    x, y, w, h = (
                        data['left'][i],
                        data['top'][i],
                        data['width'][i],
                        data['height'][i]
                    )
                    
                    text = data['text'][i].strip()
                    if text:  # 텍스트가 있는 경우만
                        results.append({
                            'text': text,
                            'bbox': [x, y, x + w, y + h],
                            'confidence': float(data['conf'][i]) / 100,
                            'level': data['level'][i]
                        })
            
            return results
            
        except Exception as e:
            self.logger.error(f"바운딩 박스 추출 실패: {e}")
            return []
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """이미지 전처리"""
        # 그레이스케일 변환
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image
        
        # 이진화
        _, binary = cv2.threshold(
            gray, 0, 255, 
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
        
        # 노이즈 제거
        denoised = cv2.medianBlur(binary, 3)
        
        return denoised
'''

# 3. EasyOCR 엔진
easyocr_engine_content = '''# -*- coding: utf-8 -*-
"""
EasyOCR 엔진
"""

import numpy as np
from typing import List, Dict, Any
import easyocr
import torch
import cv2
import logging

from .base_ocr import BaseOCR

class EasyOCREngine(BaseOCR):
    """EasyOCR 엔진"""
    
    def __init__(self, languages: List[str] = None, device: str = 'cpu'):
        super().__init__(languages, device)
        self.reader = None
        
    def initialize(self) -> bool:
        """EasyOCR 초기화"""
        try:
            # GPU 사용 여부 결정
            gpu = False
            if self.device == 'cuda' and torch.cuda.is_available():
                gpu = True
                self.logger.info(f"GPU 사용: {torch.cuda.get_device_name(0)}")
            
            # Reader 생성
            self.reader = easyocr.Reader(
                self.languages,
                gpu=gpu,
                verbose=False
            )
            
            self.logger.info("EasyOCR 초기화 완료")
            return True
            
        except Exception as e:
            self.logger.error(f"EasyOCR 초기화 실패: {e}")
            return False
    
    def extract_text(self, image: np.ndarray) -> str:
        """이미지에서 텍스트 추출"""
        try:
            if self.reader is None:
                self.initialize()
            
            # OCR 실행
            results = self.reader.readtext(
                image,
                paragraph=True,  # 문단 단위로 병합
                width_ths=0.7,
                height_ths=0.7
            )
            
            # 텍스트만 추출
            texts = []
            for (bbox, text, prob) in results:
                if prob > self.get_confidence_threshold():
                    texts.append(text)
            
            return self.postprocess_text(' '.join(texts))
            
        except Exception as e:
            self.logger.error(f"텍스트 추출 실패: {e}")
            return ""
    
    def extract_with_bbox(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """바운딩 박스와 함께 텍스트 추출"""
        try:
            if self.reader is None:
                self.initialize()
            
            # OCR 실행
            results = self.reader.readtext(
                image,
                paragraph=False  # 개별 텍스트 박스
            )
            
            extracted = []
            for (bbox, text, prob) in results:
                if prob > self.get_confidence_threshold():
                    # bbox 형식 변환
                    x_coords = [point[0] for point in bbox]
                    y_coords = [point[1] for point in bbox]
                    
                    extracted.append({
                        'text': text,
                        'bbox': [
                            min(x_coords),
                            min(y_coords),
                            max(x_coords),
                            max(y_coords)
                        ],
                        'confidence': float(prob),
                        'polygon': bbox
                    })
            
            return extracted
            
        except Exception as e:
            self.logger.error(f"바운딩 박스 추출 실패: {e}")
            return []
    
    def get_confidence_threshold(self) -> float:
        """EasyOCR은 기본적으로 높은 정확도"""
        return 0.3
    
    def detect_text_regions(self, image: np.ndarray) -> List[tuple]:
        """텍스트 영역 검출"""
        try:
            if self.reader is None:
                self.initialize()
            
            # 텍스트 검출만 수행
            horizontal_list, free_list = self.reader.detect(
                image,
                min_size=20,
                text_threshold=0.7,
                low_text=0.4
            )
            
            regions = []
            for bbox in horizontal_list[0]:
                x_min, x_max, y_min, y_max = bbox
                regions.append((
                    int(x_min), 
                    int(y_min), 
                    int(x_max), 
                    int(y_max)
                ))
            
            return regions
            
        except Exception as e:
            self.logger.error(f"텍스트 영역 검출 실패: {e}")
            return []
'''

# 4. PaddleOCR 엔진
paddleocr_engine_content = '''# -*- coding: utf-8 -*-
"""
PaddleOCR 엔진
"""

import numpy as np
from typing import List, Dict, Any
import logging

from .base_ocr import BaseOCR

try:
    from paddleocr import PaddleOCR
    PADDLEOCR_AVAILABLE = True
except ImportError:
    PADDLEOCR_AVAILABLE = False
    logging.warning("PaddleOCR not installed")

class PaddleOCREngine(BaseOCR):
    """PaddleOCR 엔진"""
    
    def __init__(self, languages: List[str] = None, device: str = 'cpu'):
        super().__init__(languages, device)
        self.ocr = None
        
    def initialize(self) -> bool:
        """PaddleOCR 초기화"""
        if not PADDLEOCR_AVAILABLE:
            self.logger.error("PaddleOCR가 설치되지 않았습니다")
            return False
            
        try:
            # 언어 매핑
            lang_map = {
                'ko': 'korean',
                'en': 'en',
                'ja': 'japan',
                'zh': 'ch'
            }
            
            # 첫 번째 언어 사용
            lang = lang_map.get(self.languages[0], 'korean')
            
            # GPU 설정
            use_gpu = self.device == 'cuda'
            
            # OCR 객체 생성
            self.ocr = PaddleOCR(
                use_angle_cls=True,
                lang=lang,
                use_gpu=use_gpu,
                show_log=False
            )
            
            self.logger.info(f"PaddleOCR 초기화 완료 (언어: {lang}, GPU: {use_gpu})")
            return True
            
        except Exception as e:
            self.logger.error(f"PaddleOCR 초기화 실패: {e}")
            return False
    
    def extract_text(self, image: np.ndarray) -> str:
        """이미지에서 텍스트 추출"""
        try:
            if self.ocr is None:
                if not self.initialize():
                    return ""
            
            # OCR 실행
            result = self.ocr.ocr(image, cls=True)
            
            # 텍스트 추출
            texts = []
            if result and result[0]:
                for line in result[0]:
                    if line[1]:
                        text = line[1][0]
                        confidence = line[1][1]
                        if confidence > self.get_confidence_threshold():
                            texts.append(text)
            
            return self.postprocess_text(' '.join(texts))
            
        except Exception as e:
            self.logger.error(f"텍스트 추출 실패: {e}")
            return ""
    
    def extract_with_bbox(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """바운딩 박스와 함께 텍스트 추출"""
        try:
            if self.ocr is None:
                if not self.initialize():
                    return []
            
            # OCR 실행
            result = self.ocr.ocr(image, cls=True)
            
            extracted = []
            if result and result[0]:
                for line in result[0]:
                    if line[1]:
                        bbox = line[0]
                        text = line[1][0]
                        confidence = line[1][1]
                        
                        if confidence > self.get_confidence_threshold():
                            # bbox 좌표 변환
                            x_coords = [point[0] for point in bbox]
                            y_coords = [point[1] for point in bbox]
                            
                            extracted.append({
                                'text': text,
                                'bbox': [
                                    min(x_coords),
                                    min(y_coords),
                                    max(x_coords),
                                    max(y_coords)
                                ],
                                'confidence': float(confidence),
                                'polygon': bbox
                            })
            
            return extracted
            
        except Exception as e:
            self.logger.error(f"바운딩 박스 추출 실패: {e}")
            return []
    
    def get_confidence_threshold(self) -> float:
        """PaddleOCR 신뢰도 임계값"""
        return 0.5
'''

# 5. TrOCR 엔진
trocr_engine_content = '''# -*- coding: utf-8 -*-
"""
TrOCR (Transformer OCR) 엔진
"""

import numpy as np
from typing import List, Dict, Any
import torch
from PIL import Image
import logging

from .base_ocr import BaseOCR

try:
    from transformers import TrOCRProcessor, VisionEncoderDecoderModel
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logging.warning("Transformers library not installed")

class TrOCREngine(BaseOCR):
    """TrOCR 엔진 - Transformer 기반 OCR"""
    
    def __init__(self, languages: List[str] = None, device: str = 'cpu'):
        super().__init__(languages, device)
        self.processor = None
        self.model = None
        
    def initialize(self) -> bool:
        """TrOCR 초기화"""
        if not TRANSFORMERS_AVAILABLE:
            self.logger.error("Transformers 라이브러리가 설치되지 않았습니다")
            return False
            
        try:
            # 모델 선택 (한국어 지원 모델이 제한적)
            model_name = "microsoft/trocr-base-printed"
            if 'ko' in self.languages:
                # 한국어는 별도 fine-tuning 필요
                self.logger.warning("TrOCR은 한국어를 기본 지원하지 않습니다")
            
            # 프로세서와 모델 로드
            self.processor = TrOCRProcessor.from_pretrained(model_name)
            self.model = VisionEncoderDecoderModel.from_pretrained(model_name)
            
            # 디바이스 설정
            if self.device == 'cuda' and torch.cuda.is_available():
                self.model = self.model.cuda()
                self.logger.info("TrOCR GPU 모드로 실행")
            
            self.model.eval()
            self.logger.info("TrOCR 초기화 완료")
            return True
            
        except Exception as e:
            self.logger.error(f"TrOCR 초기화 실패: {e}")
            return False
    
    def extract_text(self, image: np.ndarray) -> str:
        """이미지에서 텍스트 추출"""
        try:
            if self.model is None:
                if not self.initialize():
                    return ""
            
            # PIL Image로 변환
            if isinstance(image, np.ndarray):
                pil_image = Image.fromarray(image)
            else:
                pil_image = image
            
            # RGB로 변환
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # 이미지 처리
            pixel_values = self.processor(
                images=pil_image, 
                return_tensors="pt"
            ).pixel_values
            
            # 디바이스로 이동
            if self.device == 'cuda' and torch.cuda.is_available():
                pixel_values = pixel_values.cuda()
            
            # 텍스트 생성
            with torch.no_grad():
                generated_ids = self.model.generate(pixel_values)
            
            # 디코딩
            generated_text = self.processor.batch_decode(
                generated_ids, 
                skip_special_tokens=True
            )[0]
            
            return self.postprocess_text(generated_text)
            
        except Exception as e:
            self.logger.error(f"텍스트 추출 실패: {e}")
            return ""
    
    def extract_with_bbox(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """TrOCR은 바운딩 박스를 지원하지 않음"""
        self.logger.warning("TrOCR은 바운딩 박스 추출을 지원하지 않습니다")
        
        # 전체 이미지에서 텍스트만 추출
        text = self.extract_text(image)
        if text:
            h, w = image.shape[:2]
            return [{
                'text': text,
                'bbox': [0, 0, w, h],
                'confidence': 1.0
            }]
        
        return []
    
    def detect_text_regions(self, image: np.ndarray) -> List[tuple]:
        """TrOCR은 텍스트 영역 검출을 지원하지 않음"""
        self.logger.warning("TrOCR은 텍스트 영역 검출을 지원하지 않습니다")
        return []
'''

# 6. 텍스트 처리기
text_processor_content = '''# -*- coding: utf-8 -*-
"""
텍스트 처리기 - 한글 금융 문서 텍스트 처리
"""

import re
import logging
from typing import List, Dict, Optional, Tuple
from collections import Counter

# KoNLPy import (optional)
try:
    from konlpy.tag import Okt, Hannanum
    KONLPY_AVAILABLE = True
except ImportError:
    KONLPY_AVAILABLE = False

class TextProcessor:
    """텍스트 처리 클래스"""
    
    def __init__(self, enable_korean_nlp: bool = True):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.enable_korean_nlp = enable_korean_nlp and KONLPY_AVAILABLE
        
        if self.enable_korean_nlp:
            try:
                self.okt = Okt()
                self.hannanum = Hannanum()
                self.logger.info("KoNLPy 초기화 완료")
            except Exception as e:
                self.logger.warning(f"KoNLPy 초기화 실패: {e}")
                self.enable_korean_nlp = False
        
        # 정규식 패턴
        self.patterns = {
            'amount': r'[\d,]+(?:\.\d+)?(?:\s*(?:원|달러|USD|KRW|백만|천만|억))',
            'percentage': r'\d+(?:\.\d+)?(?:\s*%)',
            'date': r'\d{4}[-./년]\s*\d{1,2}[-./월]\s*\d{1,2}(?:일)?',
            'account': r'[0-9]{3,4}-[0-9]{2,4}-[0-9]{4,}',
            'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            'phone': r'(?:02|0\d{1,2})[-.\s]?\d{3,4}[-.\s]?\d{4}',
            'business_number': r'\d{3}-\d{2}-\d{5}'
        }
    
    def process_text(self, text: str) -> Dict[str, any]:
        """텍스트 종합 처리"""
        result = {
            'original': text,
            'cleaned': self.clean_text(text),
            'entities': self.extract_entities(text),
            'keywords': self.extract_keywords(text),
            'sentences': self.split_sentences(text)
        }
        
        if self.enable_korean_nlp:
            result['morphs'] = self.analyze_morphology(text)
            result['nouns'] = self.extract_nouns(text)
        
        return result
    
    def clean_text(self, text: str) -> str:
        """텍스트 정리"""
        # 특수문자 정리
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        
        # 중복 공백 제거
        text = re.sub(r'\s+', ' ', text)
        
        # 줄바꿈 정리
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        return text.strip()
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """개체명 추출"""
        entities = {}
        
        for entity_type, pattern in self.patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                entities[entity_type] = list(set(matches))
        
        return entities
    
    def extract_keywords(self, text: str, top_n: int = 10) -> List[Tuple[str, int]]:
        """키워드 추출"""
        if self.enable_korean_nlp:
            # 명사 기반 키워드 추출
            nouns = self.extract_nouns(text)
            counter = Counter(nouns)
            
            # 불용어 제거
            stopwords = {'것', '등', '수', '이', '그', '저', '때', '년', '월', '일'}
            keywords = [
                (word, count) for word, count in counter.most_common(top_n * 2)
                if word not in stopwords and len(word) > 1
            ]
            
            return keywords[:top_n]
        else:
            # 단순 단어 빈도
            words = text.split()
            words = [w for w in words if len(w) > 2]
            counter = Counter(words)
            return counter.most_common(top_n)
    
    def split_sentences(self, text: str) -> List[str]:
        """문장 분리"""
        # 한국어 문장 종결 패턴
        sentence_endings = r'[.!?]\s*'
        
        # 예외 처리 (소수점, 약어 등)
        text = re.sub(r'(\d)\.(\d)', r'\1<DOT>\2', text)
        text = re.sub(r'([A-Z])\.([A-Z])', r'\1<DOT>\2', text)
        
        sentences = re.split(sentence_endings, text)
        sentences = [s.replace('<DOT>', '.').strip() 
                    for s in sentences if s.strip()]
        
        return sentences
    
    def analyze_morphology(self, text: str) -> List[Tuple[str, str]]:
        """형태소 분석"""
        if not self.enable_korean_nlp:
            return []
        
        try:
            return self.okt.pos(text)
        except Exception as e:
            self.logger.error(f"형태소 분석 실패: {e}")
            return []
    
    def extract_nouns(self, text: str) -> List[str]:
        """명사 추출"""
        if not self.enable_korean_nlp:
            return []
        
        try:
            return self.hannanum.nouns(text)
        except Exception as e:
            self.logger.error(f"명사 추출 실패: {e}")
            return []
    
    def normalize_numbers(self, text: str) -> str:
        """숫자 정규화"""
        # 한글 숫자를 아라비아 숫자로
        korean_nums = {
            '일': '1', '이': '2', '삼': '3', '사': '4', '오': '5',
            '육': '6', '칠': '7', '팔': '8', '구': '9', '십': '10',
            '백': '100', '천': '1000', '만': '10000', '억': '100000000'
        }
        
        for kor, num in korean_nums.items():
            text = text.replace(kor, num)
        
        return text
    
    def extract_financial_numbers(self, text: str) -> List[Dict[str, str]]:
        """금융 관련 숫자 추출"""
        numbers = []
        
        # 금액 패턴
        amount_pattern = r'([\d,]+(?:\.\d+)?)\s*(원|달러|USD|KRW|백만원|천만원|억원)'
        for match in re.finditer(amount_pattern, text):
            numbers.append({
                'value': match.group(1),
                'unit': match.group(2),
                'type': 'amount',
                'position': match.span()
            })
        
        # 백분율 패턴
        percent_pattern = r'([\d.]+)\s*(%|퍼센트|프로)'
        for match in re.finditer(percent_pattern, text):
            numbers.append({
                'value': match.group(1),
                'unit': '%',
                'type': 'percentage',
                'position': match.span()
            })
        
        return numbers
'''

# 7. 테이블 처리기
table_processor_content = '''# -*- coding: utf-8 -*-
"""
테이블 처리기 - PDF에서 테이블 추출 및 구조화
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Optional, Tuple, Any
import cv2
import logging
from dataclasses import dataclass

@dataclass
class Table:
    """테이블 데이터 클래스"""
    data: pd.DataFrame
    bbox: Tuple[int, int, int, int]
    confidence: float
    headers: List[str]
    title: Optional[str] = None
    
class TableProcessor:
    """테이블 처리 클래스"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def detect_tables(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """이미지에서 테이블 영역 검출"""
        # 그레이스케일 변환
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image.copy()
        
        # 이진화
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # 수평/수직 라인 검출
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
        
        horizontal_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, horizontal_kernel)
        vertical_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, vertical_kernel)
        
        # 라인 결합
        table_mask = cv2.add(horizontal_lines, vertical_lines)
        
        # 컨투어 찾기
        contours, _ = cv2.findContours(
            table_mask, 
            cv2.RETR_EXTERNAL, 
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        # 테이블 영역 추출
        tables = []
        min_table_area = 10000  # 최소 테이블 크기
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > min_table_area:
                x, y, w, h = cv2.boundingRect(contour)
                tables.append((x, y, x + w, y + h))
        
        return tables
    
    def extract_table_structure(self, image: np.ndarray, bbox: Tuple[int, int, int, int]) -> Dict[str, Any]:
        """테이블 구조 추출"""
        x1, y1, x2, y2 = bbox
        table_img = image[y1:y2, x1:x2]
        
        # 셀 검출
        cells = self._detect_cells(table_img)
        
        # 행과 열 구조 파악
        rows, cols = self._organize_cells(cells)
        
        return {
            'cells': cells,
            'rows': rows,
            'cols': cols,
            'shape': (len(rows), len(cols))
        }
    
    def _detect_cells(self, table_img: np.ndarray) -> List[Dict[str, Any]]:
        """테이블 내 셀 검출"""
        # 그레이스케일 변환
        if len(table_img.shape) == 3:
            gray = cv2.cvtColor(table_img, cv2.COLOR_RGB2GRAY)
        else:
            gray = table_img.copy()
        
        # 이진화
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # 컨투어 찾기
        contours, _ = cv2.findContours(
            binary, 
            cv2.RETR_TREE, 
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        cells = []
        min_cell_area = 100
        
        for i, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            if area > min_cell_area:
                x, y, w, h = cv2.boundingRect(contour)
                cells.append({
                    'id': i,
                    'bbox': (x, y, x + w, y + h),
                    'center': (x + w // 2, y + h // 2),
                    'area': area
                })
        
        return cells
    
    def _organize_cells(self, cells: List[Dict[str, Any]]) -> Tuple[List[int], List[int]]:
        """셀을 행과 열로 정리"""
        if not cells:
            return [], []
        
        # Y 좌표로 행 구분
        y_coords = sorted(set(cell['center'][1] for cell in cells))
        rows = self._cluster_coordinates(y_coords, threshold=20)
        
        # X 좌표로 열 구분
        x_coords = sorted(set(cell['center'][0] for cell in cells))
        cols = self._cluster_coordinates(x_coords, threshold=20)
        
        return rows, cols
    
    def _cluster_coordinates(self, coords: List[int], threshold: int = 20) -> List[int]:
        """좌표 클러스터링"""
        if not coords:
            return []
        
        clusters = []
        current_cluster = [coords[0]]
        
        for coord in coords[1:]:
            if coord - current_cluster[-1] <= threshold:
                current_cluster.append(coord)
            else:
                clusters.append(sum(current_cluster) // len(current_cluster))
                current_cluster = [coord]
        
        clusters.append(sum(current_cluster) // len(current_cluster))
        
        return clusters
    
    def build_table_dataframe(
        self, 
        cells_text: Dict[Tuple[int, int], str], 
        shape: Tuple[int, int]
    ) -> pd.DataFrame:
        """셀 텍스트로부터 DataFrame 생성"""
        rows, cols = shape
        
        # 2D 배열 생성
        data = [['' for _ in range(cols)] for _ in range(rows)]
        
        # 셀 텍스트 채우기
        for (row, col), text in cells_text.items():
            if 0 <= row < rows and 0 <= col < cols:
                data[row][col] = text
        
        # DataFrame 생성
        df = pd.DataFrame(data)
        
        # 첫 행을 헤더로 사용 (옵션)
        if self._is_header_row(df.iloc[0]):
            df.columns = df.iloc[0]
            df = df[1:].reset_index(drop=True)
        
        return df
    
    def _is_header_row(self, row: pd.Series) -> bool:
        """헤더 행인지 판단"""
        # 모든 셀이 텍스트이고 숫자가 없으면 헤더로 간주
        non_empty = row[row != '']
        if len(non_empty) == 0:
            return False
        
        for value in non_empty:
            try:
                float(str(value).replace(',', ''))
                return False
            except ValueError:
                continue
        
        return True
    
    def merge_cells(self, df: pd.DataFrame) -> pd.DataFrame:
        """병합된 셀 처리"""
        # 빈 셀이 연속되면 병합된 것으로 간주
        for i in range(len(df)):
            row = df.iloc[i]
            for j in range(1, len(row)):
                if row[j] == '' and row[j-1] != '':
                    # 이전 셀 값으로 채우기 (병합된 셀)
                    df.iloc[i, j] = df.iloc[i, j-1]
        
        return df
    
    def validate_table(self, df: pd.DataFrame) -> float:
        """테이블 유효성 검증 및 신뢰도 계산"""
        if df.empty:
            return 0.0
        
        # 신뢰도 계산 요소
        scores = []
        
        # 1. 비어있지 않은 셀 비율
        non_empty_ratio = (df != '').sum().sum() / (df.shape[0] * df.shape[1])
        scores.append(non_empty_ratio)
        
        # 2. 일관된 열 구조
        col_consistency = 1.0
        for col in df.columns:
            non_empty = df[col][df[col] != '']
            if len(non_empty) > 0:
                # 데이터 타입 일관성 체크
                types = set(self._infer_type(val) for val in non_empty)
                col_consistency *= (1.0 / len(types))
        scores.append(col_consistency)
        
        # 3. 행과 열 수의 적절성
        shape_score = min(1.0, 1.0 / (1 + abs(df.shape[0] - df.shape[1]) / 10))
        scores.append(shape_score)
        
        return sum(scores) / len(scores)
    
    def _infer_type(self, value: str) -> str:
        """값의 타입 추론"""
        value_str = str(value).strip()
        
        # 숫자 체크
        try:
            float(value_str.replace(',', ''))
            return 'number'
        except ValueError:
            pass
        
        # 날짜 체크
        if any(sep in value_str for sep in ['-', '/', '.']):
            parts = re.split(r'[-/.]', value_str)
            if all(part.isdigit() for part in parts):
                return 'date'
        
        # 백분율 체크
        if '%' in value_str:
            return 'percentage'
        
        return 'text'
'''

# 8. 금융 용어 처리기
term_processor_content = '''# -*- coding: utf-8 -*-
"""
금융 용어 처리기
"""

import re
import json
from typing import List, Dict, Set, Optional
from pathlib import Path
import logging

class FinancialTermProcessor:
    """금융 용어 추출 및 분류"""
    
    def __init__(self, terms_file: Optional[Path] = None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.terms = self._load_default_terms()
        
        if terms_file and terms_file.exists():
            self._load_custom_terms(terms_file)
    
    def _load_default_terms(self) -> Dict[str, List[str]]:
        """기본 금융 용어 사전 로드"""
        return {
            "accounting": [
                "자산", "부채", "자본", "매출", "매출액", "영업이익", "당기순이익",
                "총자산", "총부채", "자기자본", "이익잉여금", "자본잉여금",
                "유동자산", "비유동자산", "유동부채", "비유동부채",
                "매출채권", "재고자산", "현금및현금성자산", "단기차입금", "장기차입금",
                "감가상각비", "대손상각비", "영업활동현금흐름", "투자활동현금흐름",
                "재무활동현금흐름", "EBITDA", "EBIT"
            ],
            "financial_ratios": [
                "ROE", "ROA", "ROI", "ROIC", "자기자본이익률", "총자산이익률",
                "부채비율", "유동비율", "당좌비율", "이자보상배율",
                "총자산회전율", "재고자산회전율", "매출채권회전율",
                "영업이익률", "순이익률", "매출총이익률",
                "PER", "PBR", "PSR", "PCR", "EV/EBITDA",
                "배당수익률", "배당성향", "주당순이익", "주당순자산"
            ],
            "insurance": [
                "보험료", "보험금", "책임준비금", "지급준비금", "미경과보험료",
                "손해율", "사업비율", "합산비율", "지급여력비율",
                "기본보험료", "위험보험료", "저축보험료", "부가보험료",
                "환급금", "해약환급금", "만기환급금", "중도환급금",
                "담보", "특약", "주계약", "갱신", "자동갱신",
                "면책기간", "면책사유", "보장개시일", "보험기간"
            ],
            "investment": [
                "수익률", "변동성", "샤프지수", "정보비율", "추적오차",
                "벤치마크", "초과수익", "알파", "베타", "상관계수",
                "포트폴리오", "자산배분", "리밸런싱", "헤지", "레버리지",
                "선물", "옵션", "스왑", "파생상품", "기초자산",
                "콜옵션", "풋옵션", "행사가격", "만기일", "내재가치"
            ],
            "banking": [
                "예금", "적금", "대출", "여신", "수신",
                "이자율", "금리", "기준금리", "대출금리", "예금금리",
                "원금", "이자", "연체이자", "중도상환수수료",
                "담보대출", "신용대출", "전세자금대출", "주택담보대출",
                "한도", "대출한도", "마이너스통장", "신용등급", "연체"
            ],
            "securities": [
                "주식", "채권", "증권", "유가증권", "주권",
                "보통주", "우선주", "신주", "구주", "자사주",
                "회사채", "국채", "지방채", "특수채", "전환사채",
                "액면가", "시가", "종가", "고가", "저가",
                "거래량", "거래대금", "시가총액", "호가", "매수호가"
            ],
            "tax": [
                "법인세", "소득세", "부가가치세", "양도소득세", "증여세",
                "세전이익", "세후이익", "과세표준", "세율", "공제",
                "이연법인세", "당기법인세", "법인세비용", "유효세율",
                "손금산입", "손금불산입", "익금산입", "익금불산입",
                "세무조정", "세무신고", "세무조사", "가산세", "환급"
            ],
            "general": [
                "재무제표", "손익계산서", "재무상태표", "현금흐름표",
                "사업보고서", "감사보고서", "분기보고서", "반기보고서",
                "연결재무제표", "별도재무제표", "주석", "감사의견",
                "회계연도", "사업연도", "결산", "배당", "유상증자"
            ]
        }
    
    def _load_custom_terms(self, terms_file: Path):
        """사용자 정의 용어 로드"""
        try:
            with open(terms_file, 'r', encoding='utf-8') as f:
                custom_terms = json.load(f)
                
            # 기존 용어에 추가
            for category, terms in custom_terms.items():
                if category in self.terms:
                    self.terms[category].extend(terms)
                else:
                    self.terms[category] = terms
                    
            self.logger.info(f"사용자 정의 용어 {len(custom_terms)} 카테고리 로드")
            
        except Exception as e:
            self.logger.error(f"사용자 정의 용어 로드 실패: {e}")
    
    def extract_terms(self, text: str) -> Dict[str, List[str]]:
        """텍스트에서 금융 용어 추출"""
        found_terms = {}
        
        for category, terms in self.terms.items():
            matches = []
            for term in terms:
                # 정확한 매칭을 위한 정규식
                pattern = r'\b' + re.escape(term) + r'\b'
                if re.search(pattern, text):
                    matches.append(term)
            
            if matches:
                found_terms[category] = list(set(matches))  # 중복 제거
        
        return found_terms
    
    def get_term_context(self, text: str, term: str, window: int = 50) -> List[str]:
        """용어 주변 문맥 추출"""
        contexts = []
        pattern = r'\b' + re.escape(term) + r'\b'
        
        for match in re.finditer(pattern, text):
            start = max(0, match.start() - window)
            end = min(len(text), match.end() + window)
            
            context = text[start:end]
            # 문장 경계에서 자르기
            if start > 0:
                context = '...' + context[context.find(' ')+1:]
            if end < len(text):
                context = context[:context.rfind(' ')] + '...'
            
            contexts.append(context)
        
        return contexts
    
    def analyze_term_frequency(self, text: str) -> Dict[str, Dict[str, int]]:
        """용어 빈도 분석"""
        frequency = {}
        
        for category, terms in self.terms.items():
            term_freq = {}
            for term in terms:
                pattern = r'\b' + re.escape(term) + r'\b'
                count = len(re.findall(pattern, text))
                if count > 0:
                    term_freq[term] = count
            
            if term_freq:
                frequency[category] = term_freq
        
        return frequency
    
    def get_term_definition(self, term: str) -> Optional[str]:
        """용어 정의 반환 (간단한 예시)"""
        definitions = {
            "ROE": "자기자본이익률. 당기순이익을 자기자본으로 나눈 비율",
            "ROA": "총자산이익률. 당기순이익을 총자산으로 나눈 비율",
            "EBITDA": "이자, 세금, 감가상각비 차감 전 영업이익",
            "PER": "주가수익비율. 주가를 주당순이익으로 나눈 비율",
            "부채비율": "총부채를 자기자본으로 나눈 비율",
            "유동비율": "유동자산을 유동부채로 나눈 비율",
            "손해율": "지급보험금을 수입보험료로 나눈 비율",
            "합산비율": "손해율과 사업비율을 합한 비율"
        }
        
        return definitions.get(term)
    
    def classify_document(self, text: str) -> str:
        """문서 유형 분류"""
        term_counts = {}
        
        for category, terms in self.terms.items():
            count = 0
            for term in terms:
                pattern = r'\b' + re.escape(term) + r'\b'
                count += len(re.findall(pattern, text))
            term_counts[category] = count
        
        # 가장 많이 나타난 카테고리
        if term_counts:
            return max(term_counts, key=term_counts.get)
        
        return "general"
'''

# 9. 레이아웃 처리기
layout_processor_content = '''# -*- coding: utf-8 -*-
"""
레이아웃 처리기 - 문서 구조 분석
"""

import cv2
import numpy as np
from typing import List, Dict, Tuple, Optional
from enum import Enum
import logging

class LayoutType(Enum):
    """레이아웃 요소 타입"""
    TEXT = "text"
    TABLE = "table"
    IMAGE = "image"
    HEADER = "header"
    FOOTER = "footer"
    TITLE = "title"
    PARAGRAPH = "paragraph"
    LIST = "list"
    CHART = "chart"

class LayoutProcessor:
    """문서 레이아웃 분석"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def analyze_layout(self, image: np.ndarray) -> Dict[str, Any]:
        """전체 레이아웃 분석"""
        # 전처리
        preprocessed = self._preprocess_image(image)
        
        # 텍스트 블록 검출
        text_blocks = self._detect_text_blocks(preprocessed)
        
        # 레이아웃 요소 분류
        elements = self._classify_elements(image, text_blocks)
        
        # 읽기 순서 결정
        reading_order = self._determine_reading_order(elements)
        
        return {
            'elements': elements,
            'reading_order': reading_order,
            'structure': self._analyze_structure(elements)
        }
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """이미지 전처리"""
        # 그레이스케일 변환
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image.copy()
        
        # 노이즈 제거
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # 이진화
        _, binary = cv2.threshold(
            denoised, 0, 255, 
            cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
        )
        
        return binary
    
    def _detect_text_blocks(self, binary_image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """텍스트 블록 검출"""
        # 형태학적 연산으로 텍스트 영역 연결
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 5))
        dilated = cv2.dilate(binary_image, kernel, iterations=1)
        
        # 컨투어 찾기
        contours, _ = cv2.findContours(
            dilated, 
            cv2.RETR_EXTERNAL, 
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        blocks = []
        min_area = 1000
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > min_area:
                x, y, w, h = cv2.boundingRect(contour)
                blocks.append((x, y, x + w, y + h))
        
        return blocks
    
    def _classify_elements(
        self, 
        image: np.ndarray, 
        blocks: List[Tuple[int, int, int, int]]
    ) -> List[Dict[str, Any]]:
        """레이아웃 요소 분류"""
        elements = []
        height, width = image.shape[:2]
        
        for i, (x1, y1, x2, y2) in enumerate(blocks):
            element = {
                'id': i,
                'bbox': (x1, y1, x2, y2),
                'type': self._classify_block_type(
                    image, (x1, y1, x2, y2), (height, width)
                ),
                'confidence': 0.0
            }
            
            elements.append(element)
        
        return elements
    
    def _classify_block_type(
        self, 
        image: np.ndarray, 
        bbox: Tuple[int, int, int, int],
        page_size: Tuple[int, int]
    ) -> LayoutType:
        """블록 타입 분류"""
        x1, y1, x2, y2 = bbox
        height, width = page_size
        block_height = y2 - y1
        block_width = x2 - x1
        
        # 위치 기반 분류
        if y1 < height * 0.1:  # 상단 10%
            if block_width > width * 0.5:
                return LayoutType.HEADER
            else:
                return LayoutType.TITLE
        
        if y2 > height * 0.9:  # 하단 10%
            return LayoutType.FOOTER
        
        # 크기 기반 분류
        aspect_ratio = block_width / block_height if block_height > 0 else 0
        
        if aspect_ratio > 3:  # 가로로 긴 블록
            return LayoutType.TABLE
        
        # 내용 기반 분류 (간단한 휴리스틱)
        block_img = image[y1:y2, x1:x2]
        if self._is_likely_table(block_img):
            return LayoutType.TABLE
        elif self._is_likely_image(block_img):
            return LayoutType.IMAGE
        elif self._is_likely_list(block_img):
            return LayoutType.LIST
        else:
            return LayoutType.PARAGRAPH
    
    def _is_likely_table(self, block_img: np.ndarray) -> bool:
        """테이블 가능성 판단"""
        if len(block_img.shape) == 3:
            gray = cv2.cvtColor(block_img, cv2.COLOR_RGB2GRAY)
        else:
            gray = block_img
        
        # 수평/수직 라인 검출
        edges = cv2.Canny(gray, 50, 150)
        lines = cv2.HoughLinesP(
            edges, 1, np.pi/180, 100, 
            minLineLength=50, maxLineGap=10
        )
        
        if lines is not None and len(lines) > 10:
            # 수평/수직 라인이 많으면 테이블
            horizontal = 0
            vertical = 0
            
            for line in lines:
                x1, y1, x2, y2 = line[0]
                angle = np.abs(np.arctan2(y2-y1, x2-x1))
                
                if angle < np.pi/6:  # 수평
                    horizontal += 1
                elif angle > np.pi/3:  # 수직
                    vertical += 1
            
            return horizontal > 3 and vertical > 3
        
        return False
    
    def _is_likely_image(self, block_img: np.ndarray) -> bool:
        """이미지 가능성 판단"""
        # 엣지 밀도가 낮으면 이미지
        if len(block_img.shape) == 3:
            gray = cv2.cvtColor(block_img, cv2.COLOR_RGB2GRAY)
        else:
            gray = block_img
        
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size
        
        return edge_density < 0.1
    
    def _is_likely_list(self, block_img: np.ndarray) -> bool:
        """리스트 가능성 판단"""
        # 왼쪽 정렬된 짧은 라인들
        # 간단한 휴리스틱
        return False
    
    def _determine_reading_order(self, elements: List[Dict[str, Any]]) -> List[int]:
        """읽기 순서 결정"""
        # 간단한 좌->우, 위->아래 순서
        sorted_elements = sorted(
            elements,
            key=lambda e: (e['bbox'][1], e['bbox'][0])  # (y, x) 순서
        )
        
        return [e['id'] for e in sorted_elements]
    
    def _analyze_structure(self, elements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """문서 구조 분석"""
        structure = {
            'num_columns': self._detect_columns(elements),
            'has_header': any(e['type'] == LayoutType.HEADER for e in elements),
            'has_footer': any(e['type'] == LayoutType.FOOTER for e in elements),
            'num_tables': sum(1 for e in elements if e['type'] == LayoutType.TABLE),
            'num_images': sum(1 for e in elements if e['type'] == LayoutType.IMAGE),
            'layout_type': 'single_column'  # 기본값
        }
        
        if structure['num_columns'] > 1:
            structure['layout_type'] = 'multi_column'
        
        return structure
    
    def _detect_columns(self, elements: List[Dict[str, Any]]) -> int:
        """컬럼 수 검출"""
        if not elements:
            return 1
        
        # X 좌표 분포 분석
        x_positions = []
        for element in elements:
            if element['type'] in [LayoutType.PARAGRAPH, LayoutType.TEXT]:
                x1, _, x2, _ = element['bbox']
                x_positions.append((x1 + x2) / 2)
        
        if not x_positions:
            return 1
        
        # 클러스터링으로 컬럼 검출
        x_positions.sort()
        gaps = []
        
        for i in range(1, len(x_positions)):
            gap = x_positions[i] - x_positions[i-1]
            if gap > 50:  # 임계값
                gaps.append(gap)
        
        # 큰 갭의 수 + 1이 컬럼 수
        significant_gaps = sum(1 for gap in gaps if gap > 100)
        
        return significant_gaps + 1
'''

# 10. JSON 헬퍼 유틸리티
json_helper_content = '''# -*- coding: utf-8 -*-
"""
JSON 직렬화 헬퍼
NumPy 타입 등 특수 타입 처리
"""

import json
import numpy as np
from datetime import datetime, date
from pathlib import Path
from typing import Any

def convert_to_serializable(obj: Any) -> Any:
    """객체를 JSON 직렬화 가능한 형태로 변환"""
    
    # NumPy 타입 처리
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.bool_):
        return bool(obj)
    
    # 날짜/시간 타입
    elif isinstance(obj, (datetime, date)):
        return obj.isoformat()
    
    # 경로 타입
    elif isinstance(obj, Path):
        return str(obj)
    
    # 바이트 타입
    elif isinstance(obj, bytes):
        return obj.decode('utf-8', errors='ignore')
    
    # 컬렉션 타입 재귀 처리
    elif isinstance(obj, dict):
        return {k: convert_to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_serializable(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_to_serializable(item) for item in obj)
    elif isinstance(obj, set):
        return list(convert_to_serializable(item) for item in obj)
    
    # 기타 타입
    else:
        return obj

def save_json(data: Any, filepath: str, **kwargs):
    """JSON 파일 저장 (NumPy 타입 자동 변환)"""
    converted_data = convert_to_serializable(data)
    
    default_kwargs = {
        'ensure_ascii': False,
        'indent': 2,
        'sort_keys': False
    }
    default_kwargs.update(kwargs)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(converted_data, f, **default_kwargs)

def load_json(filepath: str) -> Any:
    """JSON 파일 로드"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

class NumpyEncoder(json.JSONEncoder):
    """NumPy 타입을 처리하는 JSON Encoder"""
    
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif isinstance(obj, Path):
            return str(obj)
        elif isinstance(obj, bytes):
            return obj.decode('utf-8', errors='ignore')
        
        return json.JSONEncoder.default(self, obj)
'''

def main():
    print("="*60)
    print("📝 모든 누락 파일 생성")
    print("="*60)
    
    # UTF-8 인코딩 문제 수정
    print("\n1. 인코딩 문제 수정 중...")
    fix_encoding_in_files()
    
    # OCR 엔진 파일 생성
    print("\n2. OCR 엔진 파일 생성 중...")
    create_file("ocr_engines/base_ocr.py", base_ocr_content)
    create_file("ocr_engines/tesseract_ocr.py", tesseract_ocr_content)
    create_file("ocr_engines/easyocr_engine.py", easyocr_engine_content)
    create_file("ocr_engines/paddleocr_engine.py", paddleocr_engine_content)
    create_file("ocr_engines/trocr_engine.py", trocr_engine_content)
    
    # 프로세서 파일 생성
    print("\n3. 프로세서 파일 생성 중...")
    create_file("processors/text_processor.py", text_processor_content)
    create_file("processors/table_processor.py", table_processor_content)
    create_file("processors/term_processor.py", term_processor_content)
    create_file("processors/layout_processor.py", layout_processor_content)
    
    # 유틸리티 파일 생성
    print("\n4. 유틸리티 파일 생성 중...")
    create_file("utils/json_helper.py", json_helper_content)
    
    print("\n" + "="*60)
    print("✅ 모든 파일 생성 완료!")
    print("="*60)
    
    print("\n다음 단계:")
    print("1. python scripts/check_files.py  # 파일 구조 확인")
    print("2. python main.py documents/      # 실행")

if __name__ == "__main__":
    main()