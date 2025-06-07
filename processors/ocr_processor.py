# processors/ocr_processor.py
"""
OCR 처리 모듈
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Tuple
import numpy as np
from PIL import Image
import cv2

logger = logging.getLogger(__name__)

class OCRProcessor:
    """다중 OCR 엔진 통합 처리기"""
    
    def __init__(self, config):
        self.config = config
        self.engine_type = config.ocr_engine
        self.engine = None
        self.processor = None
        
        # OCR 엔진 초기화
        self._init_engine()
        
    def _init_engine(self):
        """OCR 엔진 초기화"""
        engine_name = self.engine_type.value
        
        try:
            if engine_name == "paddleocr":
                self._init_paddleocr()
            elif engine_name == "easyocr":
                self._init_easyocr()
            elif engine_name == "tesseract":
                self._init_tesseract()
            elif engine_name == "trocr":
                self._init_trocr()
            else:
                logger.warning(f"알 수 없는 OCR 엔진: {engine_name}, PaddleOCR로 대체")
                self._init_paddleocr()
                
        except Exception as e:
            logger.error(f"OCR 엔진 초기화 실패: {e}")
            # 폴백: Tesseract
            try:
                self._init_tesseract()
            except:
                logger.error("모든 OCR 엔진 초기화 실패")
                self.engine = None
    
    def _init_paddleocr(self):
        """PaddleOCR 초기화"""
        try:
            from paddleocr import PaddleOCR
            
            self.engine = PaddleOCR(
                use_angle_cls=True,
                lang='korean',
                use_gpu=self.config.device == "cuda",
                show_log=False
            )
            
            logger.info("PaddleOCR 초기화 완료")
            
        except ImportError:
            logger.error("PaddleOCR가 설치되지 않았습니다")
            raise
    
    def _init_easyocr(self):
        """EasyOCR 초기화"""
        try:
            import easyocr
            
            self.engine = easyocr.Reader(
                ['ko', 'en'],
                gpu=self.config.device == "cuda"
            )
            
            logger.info("EasyOCR 초기화 완료")
            
        except ImportError:
            logger.error("EasyOCR가 설치되지 않았습니다")
            raise
    
    def _init_tesseract(self):
        """Tesseract OCR 초기화"""
        try:
            import pytesseract
            
            # Tesseract 실행 파일 경로 설정 (Windows)
            import platform
            if platform.system() == "Windows":
                pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            
            self.engine = pytesseract
            logger.info("Tesseract OCR 초기화 완료")
            
        except ImportError:
            logger.error("pytesseract가 설치되지 않았습니다")
            raise
    
    def _init_trocr(self):
        """TrOCR 초기화"""
        try:
            import torch
            from transformers import TrOCRProcessor, VisionEncoderDecoderModel
            
            model_name = "microsoft/trocr-base-printed"
            self.processor = TrOCRProcessor.from_pretrained(model_name)
            self.engine = VisionEncoderDecoderModel.from_pretrained(model_name)
            
            if self.config.device == "cuda" and torch.cuda.is_available():
                self.engine = self.engine.cuda()
            
            self.engine.eval()
            logger.info("TrOCR 초기화 완료")
            
        except ImportError:
            logger.error("transformers가 설치되지 않았습니다")
            raise
    
    def extract_text(self, image_path: Path, bbox: Optional[List[int]] = None) -> str:
        """이미지에서 텍스트 추출"""
        if self.engine is None:
            logger.error("OCR 엔진이 초기화되지 않았습니다")
            return ""
        
        try:
            # 이미지 로드
            if isinstance(image_path, Path):
                image = Image.open(image_path)
            else:
                image = image_path
            
            # 영역 크롭
            if bbox:
                image = image.crop(bbox)
            
            # OCR 실행
            text = self._run_ocr(image)
            
            # 후처리
            text = self._post_process_text(text)
            
            return text
            
        except Exception as e:
            logger.error(f"텍스트 추출 실패: {e}")
            return ""
    
    def extract_text_with_layout(self, image_path: Path, 
                               layout_regions: List[Dict[str, Any]]) -> str:
        """레이아웃 정보를 활용한 텍스트 추출"""
        if not layout_regions:
            return self.extract_text(image_path)
        
        # 텍스트 영역만 필터링
        text_regions = [
            r for r in layout_regions 
            if r["label"] in ["text", "title", "section_header", "caption", "list"]
        ]
        
        # 위치 순서로 정렬 (위에서 아래, 왼쪽에서 오른쪽)
        text_regions.sort(key=lambda r: (r["bbox"][1], r["bbox"][0]))
        
        # 각 영역에서 텍스트 추출
        extracted_texts = []
        
        for region in text_regions:
            text = self.extract_text(image_path, region["bbox"])
            
            if text.strip():
                # 레이블에 따른 포맷팅
                if region["label"] == "title":
                    text = f"# {text}\n"
                elif region["label"] == "section_header":
                    text = f"## {text}\n"
                elif region["label"] == "list":
                    text = f"- {text}"
                
                extracted_texts.append(text)
        
        # 텍스트 조합
        return "\n".join(extracted_texts)
    
    def _run_ocr(self, image: Image.Image) -> str:
        """실제 OCR 실행"""
        engine_name = self.engine_type.value
        
        if engine_name == "paddleocr":
            return self._run_paddleocr(image)
        elif engine_name == "easyocr":
            return self._run_easyocr(image)
        elif engine_name == "tesseract":
            return self._run_tesseract(image)
        elif engine_name == "trocr":
            return self._run_trocr(image)
        else:
            return ""
    
    def _run_paddleocr(self, image: Image.Image) -> str:
        """PaddleOCR 실행"""
        # numpy 배열로 변환
        img_array = np.array(image)
        
        # OCR 실행
        result = self.engine.ocr(img_array, cls=True)
        
        # 텍스트 추출
        texts = []
        if result and result[0]:
            for line in result[0]:
                if line[1]:
                    text = line[1][0]
                    confidence = line[1][1]
                    
                    if confidence > 0.5:  # 신뢰도 필터링
                        texts.append(text)
        
        return " ".join(texts)
    
    def _run_easyocr(self, image: Image.Image) -> str:
        """EasyOCR 실행"""
        # numpy 배열로 변환
        img_array = np.array(image)
        
        # OCR 실행
        result = self.engine.readtext(img_array)
        
        # 텍스트 추출
        texts = []
        for (bbox, text, confidence) in result:
            if confidence > 0.5:
                texts.append(text)
        
        return " ".join(texts)
    
    def _run_tesseract(self, image: Image.Image) -> str:
        """Tesseract OCR 실행"""
        # 전처리
        processed_image = self._preprocess_for_ocr(image)
        
        # OCR 실행
        custom_config = r'--oem 3 --psm 6 -l kor+eng'
        text = self.engine.image_to_string(processed_image, config=custom_config)
        
        return text
    
    def _run_trocr(self, image: Image.Image) -> str:
        """TrOCR 실행"""
        import torch
        
        # 전처리
        pixel_values = self.processor(image, return_tensors="pt").pixel_values
        
        if self.config.device == "cuda" and torch.cuda.is_available():
            pixel_values = pixel_values.cuda()
        
        # 생성
        with torch.no_grad():
            generated_ids = self.engine.generate(pixel_values)
        
        # 디코딩
        generated_text = self.processor.batch_decode(
            generated_ids, skip_special_tokens=True
        )[0]
        
        return generated_text
    
    def _preprocess_for_ocr(self, image: Image.Image) -> Image.Image:
        """OCR을 위한 이미지 전처리"""
        # numpy 배열로 변환
        img_array = np.array(image)
        
        # 그레이스케일 변환
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        # 노이즈 제거
        denoised = cv2.medianBlur(gray, 3)
        
        # 대비 향상
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)
        
        # 이진화
        _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # PIL 이미지로 변환
        return Image.fromarray(binary)
    
    def _post_process_text(self, text: str) -> str:
        """추출된 텍스트 후처리"""
        if not text:
            return ""
        
        # 기본 정리
        text = text.strip()
        
        # 연속된 공백 제거
        import re
        text = re.sub(r'\s+', ' ', text)
        
        # 잘못된 문자 제거
        text = re.sub(r'[^\w\s가-힣.,!?;:\-()[\]{}"\'/=%+*@#$&]', '', text)
        
        # 줄바꿈 정리
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        return text
    
    def batch_extract(self, image_paths: List[Path], 
                     regions: Optional[List[List[Dict]]] = None) -> List[str]:
        """배치 텍스트 추출"""
        results = []
        
        for i, image_path in enumerate(image_paths):
            if regions and i < len(regions):
                text = self.extract_text_with_layout(image_path, regions[i])
            else:
                text = self.extract_text(image_path)
            
            results.append(text)
            
            if (i + 1) % 10 == 0:
                logger.info(f"OCR 진행률: {i + 1}/{len(image_paths)}")
        
        return results