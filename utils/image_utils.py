"""
이미지 처리 유틸리티
"""

import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from pathlib import Path
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class ImageUtils:
    """이미지 처리 유틸리티"""
    
    @staticmethod
    def load_image(image_path: Path) -> np.ndarray:
        """이미지 로드"""
        try:
            if image_path.suffix.lower() in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']:
                # OpenCV로 로드
                image = cv2.imread(str(image_path))
                if image is None:
                    # PIL로 재시도
                    pil_image = Image.open(image_path)
                    image = np.array(pil_image)
                    if len(image.shape) == 2:
                        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
                    elif image.shape[2] == 4:
                        image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)
                return image
            else:
                raise ValueError(f"지원하지 않는 이미지 형식: {image_path.suffix}")
        except Exception as e:
            logger.error(f"이미지 로드 실패: {image_path}, {e}")
            raise
    
    @staticmethod
    def convert_to_grayscale(image: np.ndarray) -> np.ndarray:
        """그레이스케일 변환"""
        if len(image.shape) == 3:
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return image
    
    @staticmethod
    def enhance_image(image: np.ndarray, 
                     contrast: float = 1.2,
                     brightness: float = 1.0,
                     sharpness: float = 1.1) -> np.ndarray:
        """이미지 개선"""
        # PIL Image로 변환
        pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        
        # 대비 조정
        if contrast != 1.0:
            enhancer = ImageEnhance.Contrast(pil_image)
            pil_image = enhancer.enhance(contrast)
        
        # 밝기 조정
        if brightness != 1.0:
            enhancer = ImageEnhance.Brightness(pil_image)
            pil_image = enhancer.enhance(brightness)
        
        # 선명도 조정
        if sharpness != 1.0:
            enhancer = ImageEnhance.Sharpness(pil_image)
            pil_image = enhancer.enhance(sharpness)
        
        # numpy 배열로 변환
        enhanced = np.array(pil_image)
        return cv2.cvtColor(enhanced, cv2.COLOR_RGB2BGR)
    
    @staticmethod
    def remove_noise(image: np.ndarray, method: str = 'median') -> np.ndarray:
        """노이즈 제거"""
        if method == 'median':
            return cv2.medianBlur(image, 3)
        elif method == 'gaussian':
            return cv2.GaussianBlur(image, (3, 3), 0)
        elif method == 'bilateral':
            return cv2.bilateralFilter(image, 9, 75, 75)
        else:
            return image
    
    @staticmethod
    def binarize(image: np.ndarray, method: str = 'otsu') -> np.ndarray:
        """이진화"""
        gray = ImageUtils.convert_to_grayscale(image)
        
        if method == 'otsu':
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        elif method == 'adaptive':
            binary = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY, 11, 2
            )
        else:
            _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        
        return binary
    
    @staticmethod
    def deskew(image: np.ndarray) -> np.ndarray:
        """이미지 기울기 보정"""
        gray = ImageUtils.convert_to_grayscale(image)
        
        # 엣지 검출
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        
        # 허프 변환으로 선 검출
        lines = cv2.HoughLines(edges, 1, np.pi/180, 200)
        
        if lines is not None:
            # 각도 계산
            angles = []
            for line in lines:
                rho, theta = line[0]
                angle = (theta * 180 / np.pi) - 90
                if -45 <= angle <= 45:
                    angles.append(angle)
            
            if angles:
                # 중앙값 각도
                median_angle = np.median(angles)
                
                # 회전
                if abs(median_angle) > 0.5:
                    h, w = image.shape[:2]
                    center = (w // 2, h // 2)
                    M = cv2.getRotationMatrix2D(center, median_angle, 1.0)
                    rotated = cv2.warpAffine(
                        image, M, (w, h),
                        flags=cv2.INTER_CUBIC,
                        borderMode=cv2.BORDER_REPLICATE
                    )
                    return rotated
        
        return image
    
    @staticmethod
    def resize_image(image: np.ndarray, 
                    target_size: Optional[Tuple[int, int]] = None,
                    scale_factor: Optional[float] = None) -> np.ndarray:
        """이미지 크기 조정"""
        if target_size:
            return cv2.resize(image, target_size, interpolation=cv2.INTER_AREA)
        elif scale_factor:
            h, w = image.shape[:2]
            new_h = int(h * scale_factor)
            new_w = int(w * scale_factor)
            return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
        else:
            return image
    
    @staticmethod
    def crop_image(image: np.ndarray, bbox: Tuple[int, int, int, int]) -> np.ndarray:
        """이미지 크롭"""
        x1, y1, x2, y2 = bbox
        return image[y1:y2, x1:x2]
    
    @staticmethod
    def save_image(image: np.ndarray, output_path: Path):
        """이미지 저장"""
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(output_path), image)
            logger.debug(f"이미지 저장: {output_path}")
        except Exception as e:
            logger.error(f"이미지 저장 실패: {output_path}, {e}")
            raise
