# processors/table_extractor.py
"""
테이블 추출 모듈
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from PIL import Image
import cv2
import pandas as pd

logger = logging.getLogger(__name__)

class TableExtractor:
    """테이블 추출기"""
    
    def __init__(self, config):
        self.config = config
        self.min_table_area = 10000  # 최소 테이블 영역 크기
        self.min_rows = 2
        self.min_cols = 2
        
    def extract_tables(self, image_path: Path) -> List[Dict[str, Any]]:
        """이미지에서 테이블 추출"""
        tables = []
        
        try:
            # 이미지 로드
            image = cv2.imread(str(image_path))
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 테이블 영역 검출
            table_regions = self._detect_table_regions(gray)
            
            # 각 테이블 처리
            for i, region in enumerate(table_regions):
                table_data = self._extract_table_data(gray, region, i)
                if table_data:
                    tables.append(table_data)
            
            return tables
            
        except Exception as e:
            logger.error(f"테이블 추출 실패: {e}")
            return []
    
    def _detect_table_regions(self, gray_image: np.ndarray) -> List[Dict[str, Any]]:
        """테이블 영역 검출"""
        regions = []
        
        # 이진화
        _, binary = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # 수평/수직 선 검출
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
        
        horizontal = cv2.morphologyEx(binary, cv2.MORPH_OPEN, horizontal_kernel)
        vertical = cv2.morphologyEx(binary, cv2.MORPH_OPEN, vertical_kernel)
        
        # 테이블 구조 결합
        table_mask = cv2.add(horizontal, vertical)
        
        # 윤곽선 찾기
        contours, _ = cv2.findContours(table_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            
            # 크기 필터링
            if area > self.min_table_area:
                # 격자 구조 확인
                if self._has_grid_structure(binary[y:y+h, x:x+w]):
                    regions.append({
                        'bbox': [x, y, x+w, y+h],
                        'area': area,
                        'confidence': 0.8
                    })
        
        return regions
    
    def _has_grid_structure(self, region: np.ndarray) -> bool:
        """격자 구조 확인"""
        h, w = region.shape
        
        # 수평/수직 선 검출
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (w//4, 1))
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, h//4))
        
        horizontal = cv2.morphologyEx(region, cv2.MORPH_OPEN, horizontal_kernel)
        vertical = cv2.morphologyEx(region, cv2.MORPH_OPEN, vertical_kernel)
        
        # 선 개수 계산
        h_contours, _ = cv2.findContours(horizontal, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        v_contours, _ = cv2.findContours(vertical, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        return len(h_contours) >= self.min_rows and len(v_contours) >= self.min_cols
    
    def _extract_table_data(self, image: np.ndarray, 
                          region: Dict[str, Any], 
                          table_id: int) -> Optional[Dict[str, Any]]:
        """테이블 데이터 추출"""
        try:
            x1, y1, x2, y2 = region['bbox']
            table_img = image[y1:y2, x1:x2]
            
            # 셀 검출
            cells = self._detect_cells(table_img)
            
            if not cells:
                return None
            
            # 행과 열 구조 분석
            structure = self._analyze_table_structure(cells)
            
            # OCR로 셀 내용 추출
            cell_contents = self._extract_cell_contents(table_img, cells)
            
            # 데이터프레임 생성
            df = self._create_dataframe(cell_contents, structure)
            
            return {
                'id': table_id,
                'bbox': region['bbox'],
                'rows': structure['rows'],
                'columns': structure['columns'],
                'cells': len(cells),
                'confidence': region['confidence'],
                'data': df.to_dict('records') if df is not None else [],
                'csv': df.to_csv(index=False) if df is not None else "",
                'html': df.to_html(index=False) if df is not None else ""
            }
            
        except Exception as e:
            logger.error(f"테이블 데이터 추출 실패: {e}")
            return None
    
    def _detect_cells(self, table_img: np.ndarray) -> List[Dict[str, Any]]:
        """테이블 셀 검출"""
        cells = []
        
        # 이진화
        _, binary = cv2.threshold(table_img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # 수평/수직 선으로 그리드 검출
        horizontal = self._detect_lines(binary, 'horizontal')
        vertical = self._detect_lines(binary, 'vertical')
        
        # 교차점 찾기
        h_lines = self._get_line_positions(horizontal, 'horizontal')
        v_lines = self._get_line_positions(vertical, 'vertical')
        
        # 셀 생성
        for i in range(len(h_lines) - 1):
            for j in range(len(v_lines) - 1):
                cell = {
                    'row': i,
                    'col': j,
                    'bbox': [v_lines[j], h_lines[i], v_lines[j+1], h_lines[i+1]]
                }
                cells.append(cell)
        
        return cells
    
    def _detect_lines(self, binary: np.ndarray, direction: str) -> np.ndarray:
        """선 검출"""
        if direction == 'horizontal':
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (binary.shape[1]//20, 1))
        else:
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, binary.shape[0]//20))
        
        lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        return lines
    
    def _get_line_positions(self, lines_img: np.ndarray, direction: str) -> List[int]:
        """선 위치 추출"""
        positions = []
        
        if direction == 'horizontal':
            projection = np.sum(lines_img, axis=1)
            threshold = lines_img.shape[1] * 0.5
        else:
            projection = np.sum(lines_img, axis=0)
            threshold = lines_img.shape[0] * 0.5
        
        in_line = False
        for i, val in enumerate(projection):
            if val > threshold and not in_line:
                positions.append(i)
                in_line = True
            elif val <= threshold:
                in_line = False
        
        # 마지막 위치 추가
        if direction == 'horizontal':
            positions.append(lines_img.shape[0])
        else:
            positions.append(lines_img.shape[1])
        
        return sorted(set(positions))
    
    def _analyze_table_structure(self, cells: List[Dict[str, Any]]) -> Dict[str, Any]:
        """테이블 구조 분석"""
        if not cells:
            return {'rows': 0, 'columns': 0}
        
        max_row = max(cell['row'] for cell in cells) + 1
        max_col = max(cell['col'] for cell in cells) + 1
        
        return {
            'rows': max_row,
            'columns': max_col
        }
    
    def _extract_cell_contents(self, table_img: np.ndarray, 
                             cells: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """셀 내용 추출"""
        from processors.ocr_processor import OCRProcessor
        ocr = OCRProcessor(self.config)
        
        cell_contents = []
        
        for cell in cells:
            x1, y1, x2, y2 = cell['bbox']
            
            # 셀 이미지 크롭
            cell_img = table_img[y1:y2, x1:x2]
            
            # 패딩 추가 (OCR 성능 향상)
            cell_img_padded = cv2.copyMakeBorder(
                cell_img, 5, 5, 5, 5, 
                cv2.BORDER_CONSTANT, value=255
            )
            
            # OCR 실행
            cell_img_pil = Image.fromarray(cell_img_padded)
            text = ocr.extract_text(cell_img_pil)
            
            cell_contents.append({
                'row': cell['row'],
                'col': cell['col'],
                'text': text.strip()
            })
        
        return cell_contents
    
    def _create_dataframe(self, cell_contents: List[Dict[str, Any]], 
                        structure: Dict[str, Any]) -> Optional[pd.DataFrame]:
        """데이터프레임 생성"""
        try:
            rows = structure['rows']
            cols = structure['columns']
            
            # 빈 테이블 생성
            data = [['' for _ in range(cols)] for _ in range(rows)]
            
            # 셀 내용 채우기
            for cell in cell_contents:
                row = cell['row']
                col = cell['col']
                if row < rows and col < cols:
                    data[row][col] = cell['text']
            
            # 데이터프레임 생성
            df = pd.DataFrame(data)
            
            # 첫 행을 헤더로 사용 (선택적)
            if rows > 1 and all(data[0]):  # 첫 행이 모두 채워져 있으면
                df.columns = data[0]
                df = df[1:].reset_index(drop=True)
            
            return df
            
        except Exception as e:
            logger.error(f"데이터프레임 생성 실패: {e}")
            return None
    
    def post_process_tables(self, tables: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """테이블 후처리"""
        processed = []
        
        for table in tables:
            # 빈 테이블 제거
            if table['rows'] < self.min_rows or table['columns'] < self.min_cols:
                continue
            
            # 데이터 정리
            if 'data' in table and table['data']:
                # 빈 행/열 제거
                df = pd.DataFrame(table['data'])
                
                # 빈 행 제거
                df = df.dropna(how='all')
                
                # 빈 열 제거
                df = df.dropna(axis=1, how='all')
                
                if not df.empty:
                    table['data'] = df.to_dict('records')
                    table['csv'] = df.to_csv(index=False)
                    table['html'] = df.to_html(index=False)
                    table['rows'] = len(df)
                    table['columns'] = len(df.columns)
                    
                    processed.append(table)
        
        return processed