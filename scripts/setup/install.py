"""
설치 도우미 스크립트
"""

import subprocess
import sys
import platform
import os

def print_header(text):
    print("\n" + "="*60)
    print(text)
    print("="*60 + "\n")

def run_command(command):
    """명령어 실행"""
    try:
        subprocess.run(command, shell=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def install_minimal():
    """최소 패키지 설치"""
    print_header("최소 필수 패키지 설치 중...")
    
    # 기본 패키지 설치
    if run_command(f"{sys.executable} -m pip install -r requirements-minimal.txt"):
        print("✅ 최소 패키지 설치 완료")
    else:
        print("❌ 최소 패키지 설치 실패")
        return False
    
    return True

def install_optional():
    """선택적 패키지 설치"""
    print_header("선택적 패키지 설치")
    
    # PaddleOCR (권장)
    print("\n1. PaddleOCR 설치를 시도합니다...")
    try:
        if platform.system() == "Windows":
            run_command(f"{sys.executable} -m pip install paddlepaddle -i https://pypi.tuna.tsinghua.edu.cn/simple")
        else:
            run_command(f"{sys.executable} -m pip install paddlepaddle")
        run_command(f"{sys.executable} -m pip install paddleocr")
        print("✅ PaddleOCR 설치 완료")
    except:
        print("⚠️  PaddleOCR 설치 실패 (선택적)")
    
    # EasyOCR
    print("\n2. EasyOCR 설치를 시도합니다...")
    try:
        run_command(f"{sys.executable} -m pip install easyocr")
        print("✅ EasyOCR 설치 완료")
    except:
        print("⚠️  EasyOCR 설치 실패 (선택적)")
    
    # KoNLPy (한국어 처리)
    print("\n3. KoNLPy 설치 정보")
    print("한국어 형태소 분석을 위해서는 KoNLPy가 필요합니다.")
    print("설치 방법:")
    print("1) Java 설치 필요")
    print("2) pip install konlpy JPype1")
    
    # Detectron2
    print("\n4. Detectron2 설치 정보")
    print("고급 레이아웃 분석을 위해서는 Detectron2가 필요합니다.")
    print("설치 방법:")
    if platform.system() == "Windows":
        print("Windows: https://github.com/facebookresearch/detectron2/blob/main/INSTALL.md#install-pre-built-detectron2-windows-only")
    else:
        print(f"Linux/Mac: {sys.executable} -m pip install 'git+https://github.com/facebookresearch/detectron2.git'")

def check_tesseract():
    """Tesseract 설치 확인"""
    print_header("Tesseract OCR 확인")
    
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
        print("✅ Tesseract가 설치되어 있습니다.")
    except:
        print("⚠️  Tesseract가 설치되지 않았습니다.")
        print("\n설치 방법:")
        if platform.system() == "Windows":
            print("Windows: https://github.com/UB-Mannheim/tesseract/wiki")
            print("설치 후 시스템 PATH에 추가하거나")
            print("pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'")
        elif platform.system() == "Darwin":
            print("Mac: brew install tesseract")
        else:
            print("Linux: sudo apt-get install tesseract-ocr tesseract-ocr-kor")

def main():
    print_header("금융 PDF 분석기 설치 도우미")
    
    print("Python 버전:", sys.version)
    print("운영체제:", platform.system())
    
    # 최소 패키지 설치
    if not install_minimal():
        print("\n❌ 설치 실패! 최소 패키지를 설치할 수 없습니다.")
        return
    
    # 선택적 패키지 설치
    install_optional()
    
    # Tesseract 확인
    check_tesseract()
    
    print_header("설치 완료!")
    print("✅ 기본 기능을 사용할 준비가 되었습니다.")
    print("\n사용 방법:")
    print(f"  {sys.executable} main.py [PDF 파일 또는 폴더]")
    print("\n예시:")
    print(f"  {sys.executable} main.py document.pdf")
    print(f"  {sys.executable} main.py documents/")

if __name__ == "__main__":
    main()