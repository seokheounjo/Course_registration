# -*- coding: utf-8 -*-
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
