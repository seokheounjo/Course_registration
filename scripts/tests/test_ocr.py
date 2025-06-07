# -*- coding: utf-8 -*-
"""
OCR 엔진 테스트 스크립트
"""

import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np

def create_test_image():
    """테스트용 이미지 생성"""
    # 이미지 생성
    width, height = 800, 600
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # 텍스트 추가
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()
    
    # 영어 텍스트
    draw.text((50, 50), "Financial Report 2024", fill='black', font=font)
    draw.text((50, 150), "Revenue: $1,234,567", fill='black', font=font)
    draw.text((50, 250), "ROE = 15.5%", fill='black', font=font)
    
    # 한글 텍스트 (기본 폰트로)
    draw.text((50, 350), "매출액: 1,234,567원", fill='black')
    draw.text((50, 400), "영업이익률: 15.5%", fill='black')
    
    # 테이블 그리기
    table_x, table_y = 50, 450
    draw.rectangle([table_x, table_y, table_x+300, table_y+100], outline='black')
    draw.line([table_x+100, table_y, table_x+100, table_y+100], fill='black')
    draw.line([table_x+200, table_y, table_x+200, table_y+100], fill='black')
    draw.line([table_x, table_y+30, table_x+300, table_y+30], fill='black')
    
    # 이미지 저장
    test_img_path = Path("test_ocr_image.png")
    img.save(test_img_path)
    
    return test_img_path

def test_tesseract():
    """Tesseract OCR 테스트"""
    print("\n" + "="*60)
    print("Tesseract OCR 테스트")
    print("="*60)
    
    try:
        import pytesseract
        
        # Windows에서 Tesseract 경로 설정
        import platform
        if platform.system() == "Windows":
            tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            if Path(tesseract_path).exists():
                pytesseract.pytesseract.tesseract_cmd = tesseract_path
        
        # 버전 확인
        version = pytesseract.get_tesseract_version()
        print(f"✅ Tesseract 버전: {version}")
        
        # 테스트 이미지로 OCR
        test_img = create_test_image()
        # 파일 경로를 문자열로 전달
        text = pytesseract.image_to_string(str(test_img), lang='eng+kor')
        
        print("\n추출된 텍스트:")
        print("-" * 40)
        print(text[:200] + "..." if len(text) > 200 else text)
        print("-" * 40)
        
        return True
        
    except Exception as e:
        print(f"❌ Tesseract 테스트 실패: {e}")
        return False

def test_easyocr():
    """EasyOCR 테스트"""
    print("\n" + "="*60)
    print("EasyOCR 테스트")
    print("="*60)
    
    try:
        import easyocr
        
        print("EasyOCR 초기화 중... (첫 실행 시 모델 다운로드로 시간이 걸릴 수 있습니다)")
        reader = easyocr.Reader(['ko', 'en'], gpu=False)  # GPU 없이도 작동
        print("✅ EasyOCR 초기화 완료")
        
        # 테스트 이미지로 OCR
        test_img = create_test_image()
        result = reader.readtext(str(test_img))
        
        print("\n추출된 텍스트:")
        print("-" * 40)
        for (bbox, text, prob) in result[:5]:  # 처음 5개만
            print(f"{text} (신뢰도: {prob:.2f})")
        if len(result) > 5:
            print(f"... 외 {len(result)-5}개")
        print("-" * 40)
        
        return True
        
    except Exception as e:
        print(f"❌ EasyOCR 테스트 실패: {e}")
        return False

def test_system_info():
    """시스템 정보 확인"""
    print("\n" + "="*60)
    print("시스템 정보")
    print("="*60)
    
    print(f"Python 버전: {sys.version}")
    
    # GPU 확인
    try:
        import torch
        cuda_available = torch.cuda.is_available()
        print(f"CUDA 사용 가능: {cuda_available}")
        if cuda_available:
            print(f"GPU: {torch.cuda.get_device_name(0)}")
    except:
        print("PyTorch가 설치되지 않았습니다.")
    
    # 메모리 확인
    try:
        import psutil
        memory = psutil.virtual_memory()
        print(f"시스템 메모리: {memory.total / (1024**3):.1f}GB")
        print(f"사용 가능 메모리: {memory.available / (1024**3):.1f}GB")
    except:
        pass

def main():
    print("🔍 금융 PDF 분석기 OCR 테스트")
    
    # 시스템 정보
    test_system_info()
    
    # Tesseract 테스트
    tesseract_ok = test_tesseract()
    
    # EasyOCR 테스트
    easyocr_ok = test_easyocr()
    
    # 결과 요약
    print("\n" + "="*60)
    print("테스트 결과 요약")
    print("="*60)
    
    if tesseract_ok and easyocr_ok:
        print("✅ 모든 OCR 엔진이 정상 작동합니다!")
        print("\n권장 사용법:")
        print("- 빠른 처리: python main.py documents/ --ocr-engine tesseract")
        print("- 정확한 한글: python main.py documents/ --ocr-engine easyocr")
    elif tesseract_ok:
        print("✅ Tesseract가 정상 작동합니다!")
        print("\n사용법: python main.py documents/ --ocr-engine tesseract")
    elif easyocr_ok:
        print("✅ EasyOCR이 정상 작동합니다!")
        print("\n사용법: python main.py documents/ --ocr-engine easyocr")
    else:
        print("❌ OCR 엔진이 정상 작동하지 않습니다.")
        print("설치 가이드를 참고하세요.")
    
    # 테스트 이미지 정리
    try:
        Path("test_ocr_image.png").unlink()
    except:
        pass

if __name__ == "__main__":
    main()