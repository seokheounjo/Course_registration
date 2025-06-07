#!/usr/bin/env python3
"""
가상환경 설정 및 필요한 패키지 설치
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def create_venv():
    """가상환경 생성"""
    venv_name = "pdf_analyzer_env"
    
    print(f"1. 가상환경 '{venv_name}' 생성 중...")
    subprocess.run([sys.executable, "-m", "venv", venv_name], check=True)
    
    # 가상환경 활성화 명령어
    if platform.system() == "Windows":
        activate_cmd = f"{venv_name}\\Scripts\\activate"
        python_exe = f"{venv_name}\\Scripts\\python.exe"
    else:
        activate_cmd = f"source {venv_name}/bin/activate"
        python_exe = f"{venv_name}/bin/python"
    
    print(f"\n✅ 가상환경 생성 완료!")
    print(f"활성화 명령어: {activate_cmd}")
    
    return python_exe, activate_cmd

def install_requirements(python_exe):
    """필수 패키지 설치"""
    print("\n2. 필수 패키지 설치 중...")
    
    # requirements.txt 생성
    requirements = """# Core dependencies
numpy>=1.21.0
pandas>=1.3.0
Pillow>=9.0.0
opencv-python>=4.5.0
pdf2image>=1.16.0
PyPDF2>=3.0.0
pdfplumber>=0.7.0
python-magic-bin>=0.4.14; sys_platform == 'win32'
python-magic>=0.4.27; sys_platform != 'win32'
tqdm>=4.62.0

# OCR engines
easyocr>=1.6.0
paddlepaddle>=2.5.0
paddleocr>=2.7.0
pytesseract>=0.3.10

# Deep learning
torch>=2.0.0
torchvision>=0.15.0
transformers>=4.25.0

# Korean NLP (optional)
# konlpy>=0.6.0
# jpype1>=1.4.0

# Math and formula detection
sympy>=1.11.0
matplotlib>=3.5.0

# Data export
openpyxl>=3.0.0
xlsxwriter>=3.0.0

# Utilities
python-dateutil>=2.8.0
typing-extensions>=4.0.0
"""
    
    req_file = Path("requirements.txt")
    req_file.write_text(requirements)
    print("✅ requirements.txt 생성 완료")
    
    # pip 업그레이드
    print("\n3. pip 업그레이드 중...")
    subprocess.run([python_exe, "-m", "pip", "install", "--upgrade", "pip"], 
                   check=False)
    
    # 패키지 설치
    print("\n4. 패키지 설치 중 (시간이 걸릴 수 있습니다)...")
    
    # 기본 패키지 먼저 설치
    basic_packages = [
        "numpy", "pandas", "Pillow", "opencv-python", 
        "pdf2image", "PyPDF2", "pdfplumber", "tqdm"
    ]
    
    for package in basic_packages:
        print(f"   설치 중: {package}")
        subprocess.run([python_exe, "-m", "pip", "install", package], 
                      check=False, capture_output=True)
    
    # PyTorch 설치 (GPU 지원)
    print("\n5. PyTorch 설치 중 (GPU 지원)...")
    if platform.system() == "Windows":
        # Windows + CUDA 12.1
        torch_cmd = [python_exe, "-m", "pip", "install", 
                    "torch", "torchvision", "torchaudio", 
                    "--index-url", "https://download.pytorch.org/whl/cu121"]
    else:
        torch_cmd = [python_exe, "-m", "pip", "install", 
                    "torch", "torchvision"]
    
    subprocess.run(torch_cmd, check=False)
    
    # OCR 엔진 설치
    print("\n6. OCR 엔진 설치 중...")
    ocr_packages = ["easyocr", "paddlepaddle", "paddleocr", "pytesseract"]
    
    for package in ocr_packages:
        print(f"   설치 중: {package}")
        subprocess.run([python_exe, "-m", "pip", "install", package], 
                      check=False, capture_output=True)
    
    # 나머지 패키지 설치
    print("\n7. 나머지 패키지 설치 중...")
    subprocess.run([python_exe, "-m", "pip", "install", "-r", "requirements.txt"], 
                  check=False)
    
    print("\n✅ 모든 패키지 설치 완료!")

def create_run_scripts(activate_cmd):
    """실행 스크립트 생성"""
    print("\n8. 실행 스크립트 생성 중...")
    
    if platform.system() == "Windows":
        # Windows 배치 파일
        bat_content = f"""@echo off
call {activate_cmd}
echo.
echo ===== PDF Analyzer 가상환경 활성화됨 =====
echo.
echo 사용 예시:
echo   python main.py documents/ --ocr-engine paddleocr --detect-formulas --extract-terms
echo.
echo JSON 오류 수정:
echo   python fix_json_error.py
echo.
echo GPU 테스트:
echo   python check_gpu_ocr.py
echo.
cmd /k
"""
        script_file = Path("run_analyzer.bat")
        script_file.write_text(bat_content)
        print(f"✅ 실행 스크립트 생성: {script_file}")
        
    else:
        # Linux/Mac 쉘 스크립트
        sh_content = f"""#!/bin/bash
{activate_cmd}
echo ""
echo "===== PDF Analyzer 가상환경 활성화됨 ====="
echo ""
echo "사용 예시:"
echo "  python main.py documents/ --ocr-engine paddleocr --detect-formulas --extract-terms"
echo ""
exec bash
"""
        script_file = Path("run_analyzer.sh")
        script_file.write_text(sh_content)
        script_file.chmod(0o755)
        print(f"✅ 실행 스크립트 생성: {script_file}")

def main():
    print("="*60)
    print("📦 PDF Analyzer 가상환경 설정")
    print("="*60)
    
    try:
        # 가상환경 생성
        python_exe, activate_cmd = create_venv()
        
        # 패키지 설치
        install_requirements(python_exe)
        
        # 실행 스크립트 생성
        create_run_scripts(activate_cmd)
        
        print("\n" + "="*60)
        print("✅ 설정 완료!")
        print("="*60)
        
        print("\n실행 방법:")
        if platform.system() == "Windows":
            print("1. run_analyzer.bat 실행")
            print("   또는")
            print(f"2. {activate_cmd} 실행 후 python 명령어 사용")
        else:
            print("1. ./run_analyzer.sh 실행")
            print("   또는")
            print(f"2. {activate_cmd} 실행 후 python 명령어 사용")
        
        print("\n가상환경에서 실행할 명령어:")
        print("  python fix_json_error.py  # JSON 오류 수정")
        print("  python main.py documents/ --ocr-engine paddleocr --detect-formulas --extract-terms")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        print("\n수동으로 가상환경을 만들어보세요:")
        print("  python -m venv pdf_analyzer_env")
        if platform.system() == "Windows":
            print("  pdf_analyzer_env\\Scripts\\activate")
        else:
            print("  source pdf_analyzer_env/bin/activate")
        print("  pip install -r requirements.txt")

if __name__ == "__main__":
    main()