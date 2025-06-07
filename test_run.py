# test_run.py
from pathlib import Path
from core.config import Config
from core.enhanced_document_analyzer import EnhancedDocumentAnalyzer

# 설정
config = Config()
config.ocr_engine = "easyocr"  # 또는 설치한 엔진
config.detect_korean_formulas = True

# 분석기 생성
analyzer = EnhancedDocumentAnalyzer(config)

# PDF 파일 경로 (실제 파일 경로로 변경)
pdf_path = Path("your_document.pdf")

# 분석 실행
print("분석 시작...")
result = analyzer.analyze_document(pdf_path)

if result.success:
    print(f"성공! 수식 {len(result.formulas)}개 추출")
    for i, formula in enumerate(result.formulas[:3]):
        print(f"{i+1}. {formula.latex}")
else:
    print(f"실패: {result.error_message}")