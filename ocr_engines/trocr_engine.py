# -*- coding: utf-8 -*-
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
