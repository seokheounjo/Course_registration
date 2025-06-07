# -*- coding: utf-8 -*-
"""
파일 존재 확인 및 생성 스크립트
"""

from pathlib import Path
import sys

def check_and_create_files():
    """필요한 파일들의 존재 여부 확인"""
    
    print("="*60)
    print("금융 PDF 분석기 파일 확인")
    print("="*60)
    
    # 필요한 파일 목록
    required_files = {
        "main.py": "메인 실행 파일",
        "core/__init__.py": "Core 모듈 초기화",
        "core/config.py": "설정 클래스",
        "core/document_analyzer.py": "문서 분석기",
        "core/result.py": "결과 클래스",
        "processors/__init__.py": "Processors 모듈 초기화",
        "processors/text_processor.py": "텍스트 처리기",
        "processors/table_processor.py": "테이블 처리기",
        "processors/formula_processor.py": "수식 처리기",
        "processors/term_processor.py": "용어 처리기",
        "processors/layout_processor.py": "레이아웃 처리기",
        "processors/csv_exporter.py": "CSV 내보내기",
        "ocr_engines/__init__.py": "OCR 엔진 모듈 초기화",
        "ocr_engines/base_ocr.py": "OCR 베이스 클래스",
        "ocr_engines/tesseract_ocr.py": "Tesseract OCR",
        "ocr_engines/easyocr_engine.py": "EasyOCR 엔진",
        "ocr_engines/paddleocr_engine.py": "PaddleOCR 엔진",
        "ocr_engines/trocr_engine.py": "TrOCR 엔진",
        "utils/__init__.py": "Utils 모듈 초기화",
        "utils/file_utils.py": "파일 유틸리티",
        "utils/image_utils.py": "이미지 유틸리티",
        "utils/logging_utils.py": "로깅 유틸리티",
        "utils/validator.py": "검증기"
    }
    
    missing_files = []
    existing_files = []
    
    print("\n파일 확인 중...")
    for file_path, description in required_files.items():
        path = Path(file_path)
        if path.exists():
            existing_files.append(file_path)
            print(f"  ✅ {file_path} - {description}")
        else:
            missing_files.append(file_path)
            print(f"  ❌ {file_path} - {description} (없음)")
    
    print(f"\n결과: {len(existing_files)}개 존재, {len(missing_files)}개 누락")
    
    if missing_files:
        print("\n" + "="*60)
        print("누락된 파일 목록:")
        print("="*60)
        for file_path in missing_files:
            print(f"  - {file_path}")
        
        print("\n핵심 파일들이 누락되어 있습니다.")
        print("다음 옵션 중 하나를 선택하세요:")
        print("\n1. create_all_files.py 실행 (모든 파일 자동 생성)")
        print("   python create_all_files.py")
        print("\n2. 개별 파일 수동 생성")
        print("   각 artifact를 파일로 저장해주세요")
        
        return False
    else:
        print("\n✅ 모든 필수 파일이 존재합니다!")
        print("\n이제 프로그램을 실행할 수 있습니다:")
        print("  python main.py documents/ --ocr-engine easyocr")
        return True

def check_directory_structure():
    """디렉토리 구조 확인"""
    print("\n" + "="*60)
    print("디렉토리 구조 확인")
    print("="*60)
    
    required_dirs = [
        "core",
        "processors",
        "ocr_engines",
        "utils",
        "documents",
        "output",
        "output/csv",
        "output/individual",
        "output/logs",
        "cache",
        "data",
        "data/terms"
    ]
    
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists():
            print(f"  ✅ {dir_path}/")
        else:
            print(f"  ❌ {dir_path}/ (없음)")
            path.mkdir(parents=True, exist_ok=True)
            print(f"     → 생성됨")

def main():
    # 디렉토리 구조 확인
    check_directory_structure()
    
    # 파일 확인
    all_files_exist = check_and_create_files()
    
    if not all_files_exist:
        print("\n⚠️  일부 파일이 누락되어 프로그램을 실행할 수 없습니다.")
        print("\ncreate_all_files.py를 실행하여 모든 파일을 생성하세요.")
        sys.exit(1)

if __name__ == "__main__":
    main()