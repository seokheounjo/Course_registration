# -*- coding: utf-8 -*-
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
