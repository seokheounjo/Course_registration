# -*- coding: utf-8 -*-
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
