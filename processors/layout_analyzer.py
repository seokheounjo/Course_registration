# processors/layout_analyzer.py
"""
레이아웃 분석 모듈
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from PIL import Image
import torch
from transformers import LayoutLMv3Processor, LayoutLMv3ForTokenClassification
import cv2

logger = logging.getLogger(__name__)

class LayoutAnalyzer:
    """문서 레이아웃 분석기"""
    
    def __init__(self, config):
        self.config = config
        self.device = torch.device(config.device if torch.cuda.is_available() else "cpu")
        
        # 모델 초기화
        self._init_model()
        
        # 레이아웃 클래스 정의
        self.layout_classes = {
            0: "text", 1: "title", 2: "list", 3: "table", 4: "figure",
            5: "formula", 6: "caption", 7: "footnote", 8: "header",
            9: "footer", 10: "section_header", 11: "page_number"
        }
        
    def _init_model(self):
        """레이아웃 분석 모델 초기화"""
        try:
            if self.config.layout_model.value == "layoutlmv3":
                model_name = "microsoft/layoutlmv3-base"
                self.processor = LayoutLMv3Processor.from_pretrained(model_name)
                self.model = LayoutLMv3ForTokenClassification.from_pretrained(
                    model_name,
                    num_labels=len(self.layout_classes)
                ).to(self.device)
                self.model.eval()
                logger.info("LayoutLMv3 모델 로드 완료")
            else:
                # 다른 모델들은 간단한 규칙 기반으로 대체
                self.model = None
                logger.info("규칙 기반 레이아웃 분석 사용")
                
        except Exception as e:
            logger.error(f"모델 초기화 실패: {e}")
            self.model = None
    
    def analyze_layout(self, image_path: Path) -> List[Dict[str, Any]]:
        """이미지의 레이아웃 분석"""
        try:
            # 이미지 로드
            image = Image.open(image_path).convert("RGB")
            
            if self.model:
                return self._analyze_with_model(image)
            else:
                return self._analyze_with_rules(image)
                
        except Exception as e:
            logger.error(f"레이아웃 분석 실패: {e}")
            return []
    
    def _analyze_with_model(self, image: Image.Image) -> List[Dict[str, Any]]:
        """딥러닝 모델을 사용한 분석"""
        regions = []
        
        try:
            # 이미지 전처리
            encoding = self.processor(
                image, 
                return_tensors="pt",
                truncation=True,
                padding=True
            )
            
            # GPU로 이동
            for k, v in encoding.items():
                if isinstance(v, torch.Tensor):
                    encoding[k] = v.to(self.device)
            
            # 추론
            with torch.no_grad():
                outputs = self.model(**encoding)
                predictions = outputs.logits.argmax(-1).squeeze()
                scores = torch.softmax(outputs.logits, dim=-1).max(-1).values.squeeze()
            
            # 바운딩 박스 생성 (간단한 그리드 방식)
            width, height = image.size
            grid_size = 50
            
            idx = 0
            for y in range(0, height - grid_size, grid_size // 2):
                for x in range(0, width - grid_size, grid_size // 2):
                    if idx < len(predictions):
                        label_id = predictions[idx].item() if predictions.dim() > 0 else predictions.item()
                        confidence = scores[idx].item() if scores.dim() > 0 else scores.item()
                        
                        if confidence > 0.5:
                            regions.append({
                                "bbox": [x, y, x + grid_size, y + grid_size],
                                "label": self.layout_classes.get(label_id, "unknown"),
                                "confidence": confidence,
                                "area": grid_size * grid_size
                            })
                        idx += 1
            
            # 영역 병합
            regions = self._merge_regions(regions)
            
        except Exception as e:
            logger.error(f"모델 추론 실패: {e}")
            return self._analyze_with_rules(image)
        
        return regions
    
    def _analyze_with_rules(self, image: Image.Image) -> List[Dict[str, Any]]:
        """규칙 기반 레이아웃 분석"""
        regions = []
        
        # numpy 배열로 변환
        img_array = np.array(image)
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        # 이진화
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # 컨투어 찾기
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        height, width = gray.shape
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            # 너무 작은 영역 무시
            if w < 20 or h < 10:
                continue
            
            # 영역 분류
            label = self._classify_region(x, y, w, h, width, height, gray[y:y+h, x:x+w])
            
            regions.append({
                "bbox": [x, y, x + w, y + h],
                "label": label,
                "confidence": 0.7,
                "area": w * h
            })
        
        # 영역 정렬 및 필터링
        regions = sorted(regions, key=lambda r: (r["bbox"][1], r["bbox"][0]))
        
        return regions
    
    def _classify_region(self, x: int, y: int, w: int, h: int, 
                        page_width: int, page_height: int, 
                        region_img: np.ndarray) -> str:
        """영역 분류"""
        # 위치 기반 분류
        relative_y = y / page_height
        relative_x = x / page_width
        aspect_ratio = w / h if h > 0 else 0
        
        # 헤더/푸터
        if relative_y < 0.1:
            return "header"
        elif relative_y > 0.9:
            return "footer"
        
        # 페이지 번호 (작고 모서리에 위치)
        if w < 100 and h < 50 and (relative_x < 0.1 or relative_x > 0.9):
            return "page_number"
        
        # 제목 (상단, 중앙 정렬, 큰 텍스트)
        if relative_y < 0.3 and 0.2 < relative_x < 0.8 and h > 30:
            return "title"
        
        # 테이블 (격자 구조 감지)
        if self._has_grid_structure(region_img):
            return "table"
        
        # 수식 (특정 종횡비, 중간 크기)
        if 0.5 < aspect_ratio < 5 and 50 < w < 400 and 20 < h < 100:
            if self._has_formula_characteristics(region_img):
                return "formula"
        
        # 그림 (큰 영역, 적은 텍스트)
        if w > 200 and h > 200:
            text_density = self._estimate_text_density(region_img)
            if text_density < 0.1:
                return "figure"
        
        # 기본: 텍스트
        return "text"
    
    def _has_grid_structure(self, img: np.ndarray) -> bool:
        """격자 구조 감지"""
        try:
            # 수평/수직 선 감지
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
            vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
            
            horizontal_lines = cv2.morphologyEx(img, cv2.MORPH_OPEN, horizontal_kernel)
            vertical_lines = cv2.morphologyEx(img, cv2.MORPH_OPEN, vertical_kernel)
            
            # 선의 개수 계산
            h_lines = cv2.findContours(horizontal_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
            v_lines = cv2.findContours(vertical_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
            
            return len(h_lines) > 2 and len(v_lines) > 2
            
        except:
            return False
    
    def _has_formula_characteristics(self, img: np.ndarray) -> bool:
        """수식 특성 감지"""
        try:
            # 수식은 보통 특별한 기호나 구조를 포함
            # 간단한 휴리스틱: 중앙 정렬, 특정 밀도
            h, w = img.shape[:2]
            
            # 좌우 여백 확인
            left_margin = 0
            right_margin = 0
            
            for i in range(w // 4):
                if np.sum(img[:, i]) < 255 * h * 0.1:
                    left_margin = i
                if np.sum(img[:, -(i+1)]) < 255 * h * 0.1:
                    right_margin = i
            
            # 중앙 정렬 확인
            is_centered = left_margin > w * 0.1 and right_margin > w * 0.1
            
            return is_centered
            
        except:
            return False
    
    def _estimate_text_density(self, img: np.ndarray) -> float:
        """텍스트 밀도 추정"""
        try:
            # 흰색이 아닌 픽셀의 비율
            non_white_pixels = np.sum(img < 200)
            total_pixels = img.size
            
            return non_white_pixels / total_pixels
            
        except:
            return 0.5
    
    def _merge_regions(self, regions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """인접한 동일 레이블 영역 병합"""
        if not regions:
            return regions
        
        merged = []
        used = set()
        
        for i, region1 in enumerate(regions):
            if i in used:
                continue
            
            # 병합할 영역들 찾기
            to_merge = [region1]
            
            for j, region2 in enumerate(regions[i+1:], i+1):
                if j in used:
                    continue
                
                if (region1["label"] == region2["label"] and 
                    self._are_adjacent(region1["bbox"], region2["bbox"])):
                    to_merge.append(region2)
                    used.add(j)
            
            # 병합
            if len(to_merge) > 1:
                merged_region = self._merge_bboxes(to_merge)
                merged.append(merged_region)
            else:
                merged.append(region1)
        
        return merged
    
    def _are_adjacent(self, bbox1: List[int], bbox2: List[int], 
                     threshold: int = 30) -> bool:
        """두 바운딩 박스가 인접한지 확인"""
        x1_1, y1_1, x2_1, y2_1 = bbox1
        x1_2, y1_2, x2_2, y2_2 = bbox2
        
        # 수평 거리
        h_dist = max(0, max(x1_1, x1_2) - min(x2_1, x2_2))
        # 수직 거리
        v_dist = max(0, max(y1_1, y1_2) - min(y2_1, y2_2))
        
        return h_dist < threshold and v_dist < threshold
    
    def _merge_bboxes(self, regions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """여러 영역을 하나로 병합"""
        all_x1 = [r["bbox"][0] for r in regions]
        all_y1 = [r["bbox"][1] for r in regions]
        all_x2 = [r["bbox"][2] for r in regions]
        all_y2 = [r["bbox"][3] for r in regions]
        
        merged_bbox = [
            min(all_x1), min(all_y1),
            max(all_x2), max(all_y2)
        ]
        
        avg_confidence = sum(r["confidence"] for r in regions) / len(regions)
        total_area = (merged_bbox[2] - merged_bbox[0]) * (merged_bbox[3] - merged_bbox[1])
        
        return {
            "bbox": merged_bbox,
            "label": regions[0]["label"],
            "confidence": avg_confidence,
            "area": total_area,
            "merged_count": len(regions)
        }