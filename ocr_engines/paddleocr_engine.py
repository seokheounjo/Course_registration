# -*- coding: utf-8 -*-
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
