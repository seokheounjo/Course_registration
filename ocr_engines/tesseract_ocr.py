# -*- coding: utf-8 -*-
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
                    r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                    r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
                    r'C:\Users\%s\AppData\Local\Tesseract-OCR\tesseract.exe' % os.environ.get('USERNAME', '')
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
