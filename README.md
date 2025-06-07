# 한글 금융 PDF 문서 분석 시스템

보험 및 금융 PDF 문서에서 수식을 90% 이상의 정확도로 추출하고 실행 가능한 형태로 변환하는 시스템입니다.

## 주요 기능

### 1. 고정확도 수식 추출 (90%+ 목표)
- 다중 방법 앙상블 (컴퓨터 비전, 레이아웃 분석, 텍스트 패턴)
- Pix2Text, OCR, 규칙 기반 방법 통합
- 한글 수식 특화 처리

### 2. 보험 수식 특화 처리
- 보험료, 책임준비금, 해지환급금 등 보험 수식 인식
- 자동 변수 의미 추출 및 검증
- 테스트 케이스 자동 생성

### 3. 실행 가능한 Python 코드 변환
- LaTeX → Python 자동 변환
- 변수 타입 및 제약사항 관리
- 즉시 실행 가능한 함수 생성

### 4. 데이터베이스 관리
- SQLite 기반 수식 저장
- 실행 이력 추적
- 수식 간 의존성 관리

### 5. REST API 서버
- FastAPI 기반 웹 API
- 수식 추출, 조회, 실행 엔드포인트
- 배치 처리 지원

## 시스템 구조

```
korean-finance-pdf-analyzer/
├── core/
│   ├── config.py                    # 설정 관리
│   ├── enhanced_config.py           # 향상된 설정
│   ├── document_analyzer.py         # 기본 문서 분석기
│   └── enhanced_document_analyzer.py # 향상된 문서 분석기
├── processors/
│   ├── pdf_processor.py             # PDF 처리
│   ├── layout_analyzer.py           # 레이아웃 분석
│   ├── ocr_processor.py             # OCR 처리
│   ├── enhanced_formula_extractor.py # 향상된 수식 추출
│   ├── insurance_formula_processor.py # 보험 수식 처리
│   ├── korean_text_processor.py     # 한국어 처리
│   ├── financial_term_processor.py  # 금융 용어 처리
│   ├── table_extractor.py           # 테이블 추출
│   └── csv_exporter.py              # CSV 내보내기
├── utils/
│   ├── formula_database_manager.py  # DB 관리
│   └── logging_utils.py             # 로깅 유틸
├── api/
│   └── formula_api_server.py        # API 서버
├── resources/
│   ├── financial_terms.json         # 금융 용어 사전
│   └── korean_formula_patterns.json # 한글 수식 패턴
├── main.py                          # 기본 실행 파일
├── enhanced_main.py                 # 향상된 실행 파일
├── requirements.txt                 # 패키지 의존성
└── README.md                        # 이 파일
```

## 설치 방법

### 1. 시스템 요구사항
- Python 3.8 이상
- 최소 8GB RAM (권장 16GB)
- GPU (선택사항, CUDA 지원)

### 2. 패키지 설치

```bash
# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt

# 한국어 처리를 위한 추가 설정 (KoNLPy)
# Ubuntu/Debian
sudo apt-get install g++ openjdk-8-jdk python3-dev python3-pip curl

# macOS
brew install java
```

### 3. 모델 다운로드 (선택사항)

```bash
# Pix2Text 모델
python -c "from pix2text import Pix2Text; Pix2Text()"

# PaddleOCR 모델
python -c "from paddleocr import PaddleOCR; PaddleOCR(use_angle_cls=True, lang='korean')"
```

## 사용 방법

### 1. 기본 사용법

```bash
# 단일 PDF 분석
python enhanced_main.py document.pdf

# 디렉토리 내 모든 PDF 분석
python enhanced_main.py /path/to/pdfs/

# 옵션 지정
python enhanced_main.py document.pdf \
    --output results/ \
    --ocr-engine paddleocr \
    --formula-confidence 0.7 \
    --extract-terms
```

### 2. 수식 테스트

```bash
# 추출된 수식 테스트
python enhanced_main.py document.pdf --test-formulas

# 특정 수식 실행
python enhanced_main.py --execute-formula FORMULA_ID \
    --formula-inputs '{"x": 40, "n": 20, "i": 0.025}'
```

### 3. 데이터베이스 관리

```bash
# DB 통계 보기
python enhanced_main.py --db-stats

# 수식 내보내기
python enhanced_main.py --export-formulas formulas.json

# 수식 가져오기
python enhanced_main.py --import-formulas formulas.json

# DB 백업
python enhanced_main.py --backup-db
```

### 4. API 서버 실행

```bash
# API 서버 시작
cd api/
uvicorn formula_api_server:app --reload

# 또는
python formula_api_server.py
```

API 문서는 http://localhost:8000/docs 에서 확인할 수 있습니다.

## API 엔드포인트

### 문서 분석
```http
POST /analyze
Content-Type: multipart/form-data

file: PDF 파일
extract_formulas: true (수식 추출 여부)
min_confidence: 0.5 (최소 신뢰도)
```

### 수식 조회
```http
GET /formulas?document_id=DOC_ID&formula_type=premium
```

### 수식 실행
```http
POST /execute
Content-Type: application/json

{
    "formula_id": "DOC_20240101_abc_p1_001",
    "inputs": {
        "M_x": 1000,
        "N_x": 10000
    }
}
```

### 통계 정보
```http
GET /statistics
```

## 수식 추출 정확도 향상 전략

### 1. 멀티스테이지 검출
- 1차: 넓은 범위로 가능한 모든 수식 영역 검출
- 2차: 신뢰도 기반 필터링
- 3차: 수식 구조 분석으로 최종 확인

### 2. 앙상블 방법
- Pix2Text (딥러닝 기반)
- PaddleOCR/EasyOCR (일반 OCR)
- 규칙 기반 패턴 매칭
- 결과 투표 및 가중 평균

### 3. 한글 수식 특화 처리
- "분의", "제곱" 등 한글 표현 인식
- 한글 숫자 변환 (일, 이, 삼 → 1, 2, 3)
- 보험/금융 특화 용어 처리

### 4. 후처리 및 검증
- LaTeX 구문 검증
- 괄호 균형 확인
- 변수 일관성 검사
- Python 코드 컴파일 테스트

## 데이터베이스 스키마

### formulas 테이블
- id: 수식 고유 ID
- document_id: 문서 ID
- page_number: 페이지 번호
- formula_latex: LaTeX 수식
- formula_python: Python 코드
- variables: 변수 정보 (JSON)
- confidence: 신뢰도
- created_at: 생성 시간

### formula_executions 테이블
- formula_id: 수식 ID
- inputs: 입력값 (JSON)
- result: 실행 결과
- success: 성공 여부
- execution_time: 실행 시간

## 성능 최적화

### 1. 배치 처리
```bash
python enhanced_main.py folder/ --batch-size 10 --workers 4
```

### 2. GPU 가속
```python
# config.json
{
    "use_gpu": true,
    "device": "cuda"
}
```

### 3. 캐싱
- 이미지 변환 결과 캐싱
- OCR 결과 캐싱
- 수식 인식 결과 캐싱

## 문제 해결

### 1. OCR 정확도 낮음
- DPI 증가: `--dpi 300`
- 다른 OCR 엔진 시도: `--ocr-engine easyocr`

### 2. 수식 추출 실패
- 신뢰도 임계값 조정: `--formula-confidence 0.3`
- 디버그 모드: `--debug`

### 3. 메모리 부족
- 배치 크기 감소: `--batch-size 1`
- 페이지 제한: 설정 파일에서 `max_pages` 설정

### 4. 실행 오류
```bash
# 데이터베이스 검증
python enhanced_main.py --validate-db

# 로그 확인
tail -f output/analysis_*.log
```

## 예제 출력

### 수식 추출 결과
```json
{
    "id": "DOC_20240101_abc_p2_001",
    "latex": "P = \\frac{M_x}{N_x}",
    "python_code": "def formula_12345678(M_x, N_x):\n    ...",
    "variables": {
        "M_x": "사망보험금현가누계",
        "N_x": "연금현가"
    },
    "type": "premium",
    "confidence": 0.92
}
```

### 실행 결과
```json
{
    "success": true,
    "result": 0.1,
    "execution_time": 0.002,
    "formula_id": "DOC_20240101_abc_p2_001"
}
```

## 향후 개선 사항

1. **웹 인터페이스**
   - React 기반 프론트엔드
   - 실시간 수식 편집 및 실행

2. **클라우드 배포**
   - Docker 컨테이너화
   - Kubernetes 오케스트레이션

3. **성능 개선**
   - 분산 처리
   - 모델 경량화

4. **기능 확장**
   - 그래프/차트 추출
   - 다국어 지원
   - 수식 시각화

## 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.

## 기여 방법

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 문의

문제가 있거나 개선 제안이 있으시면 Issues 탭에서 새 이슈를 만들어주세요.