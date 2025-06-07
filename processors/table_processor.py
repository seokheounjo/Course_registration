# -*- coding: utf-8 -*-
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
