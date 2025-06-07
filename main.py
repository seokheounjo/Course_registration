# main.py

import os
import sys
import argparse
import json
from pathlib import Path
from datetime import datetime
import traceback

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from src.extractors.formula_extractor import FormulaExtractor
from src.database.db_manager import DatabaseManager
from src.utils.logger import setup_logger

# 로거 설정
logger = setup_logger(
    name="main",
    log_file="logs/formula_extractor.log",
    level="INFO"
)

def process_single_pdf(pdf_path: str, args: argparse.Namespace):
    """단일 PDF 파일 처리"""
    logger.info(f"Processing PDF: {pdf_path}")
    
    try:
        # 수식 추출기 생성
        extractor = FormulaExtractor(args.config)
        
        # 수식 추출
        result = extractor.extract_from_pdf(
            pdf_path,
            save_to_db=not args.no_db
        )
        
        # 리포트 생성
        if args.generate_report:
            output_dir = Path(args.output_dir) / Path(pdf_path).stem
            output_dir.mkdir(parents=True, exist_ok=True)
            
            report_path = output_dir / "extraction_report.json"
            extractor.generate_report(result, str(report_path))
            logger.info(f"Report saved to: {report_path}")
        
        # 결과 출력
        print(f"\n{'='*60}")
        print(f"Extraction Results for: {Path(pdf_path).name}")
        print(f"{'='*60}")
        print(f"Total Pages: {result.total_pages}")
        print(f"Total Formulas Found: {result.total_formulas}")
        print(f"Successful Extractions: {result.successful_extractions}")
        print(f"Failed Extractions: {result.failed_extractions}")
        print(f"Success Rate: {result.successful_extractions / max(1, result.successful_extractions + result.failed_extractions):.2%}")
        
        if args.show_formulas and result.formulas:
            print(f"\n{'='*60}")
            print("Extracted Formulas:")
            print(f"{'='*60}")
            for i, formula in enumerate(result.formulas[:10]):  # 처음 10개만 표시
                print(f"\n{i+1}. LaTeX: {formula.latex}")
                print(f"   Confidence: {formula.confidence:.2f}")
                print(f"   Variables: {formula.variables}")
                if formula.python_code:
                    print(f"   Python code: Available")
            
            if len(result.formulas) > 10:
                print(f"\n... and {len(result.formulas) - 10} more formulas")
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        logger.error(traceback.format_exc())
        return None

def process_directory(directory: str, args: argparse.Namespace):
    """디렉토리의 모든 PDF 파일 처리"""
    pdf_dir = Path(directory)
    pdf_files = list(pdf_dir.glob("*.pdf"))
    
    if not pdf_files:
        logger.warning(f"No PDF files found in: {directory}")
        return
    
    logger.info(f"Found {len(pdf_files)} PDF files")
    
    results = []
    for pdf_path in pdf_files:
        result = process_single_pdf(str(pdf_path), args)
        if result:
            results.append(result)
    
    # 전체 통계
    if results:
        total_formulas = sum(r.total_formulas for r in results)
        total_successful = sum(r.successful_extractions for r in results)
        total_failed = sum(r.failed_extractions for r in results)
        
        print(f"\n{'='*60}")
        print("Overall Statistics")
        print(f"{'='*60}")
        print(f"Total PDFs Processed: {len(results)}")
        print(f"Total Formulas Found: {total_formulas}")
        print(f"Total Successful Extractions: {total_successful}")
        print(f"Total Failed Extractions: {total_failed}")
        print(f"Overall Success Rate: {total_successful / max(1, total_successful + total_failed):.2%}")

def test_formula_execution(args: argparse.Namespace):
    """수식 실행 테스트"""
    logger.info("Testing formula execution")
    
    try:
        # 데이터베이스 매니저 생성
        db_manager = DatabaseManager(args.config)
        db_manager.initialize()
        
        # 수식 검색
        formulas = db_manager.search_formulas(
            formula_type=args.formula_type,
            min_confidence=args.min_confidence
        )
        
        if not formulas:
            print("No formulas found")
            return
        
        print(f"\nFound {len(formulas)} formulas")
        
        # 첫 번째 수식 테스트
        formula = formulas[0]
        formula_info = db_manager.get_formula_by_id(formula['id'])
        
        print(f"\nTesting formula ID: {formula['id']}")
        print(f"LaTeX: {formula_info['formula_latex']}")
        print(f"Variables: {formula_info['variables']}")
        
        # 테스트 변수값
        test_variables = {}
        for var in formula_info['variables']:
            test_variables[var] = float(input(f"Enter value for {var}: "))
        
        # 실행
        result = db_manager.execute_formula(formula['id'], test_variables)
        
        if result is not None:
            print(f"\nResult: {result}")
        else:
            print("\nFormula execution failed")
            
    except Exception as e:
        logger.error(f"Test execution error: {e}")
        logger.error(traceback.format_exc())

def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description="Insurance Formula Extractor - Extract mathematical formulas from insurance PDF documents"
    )
    
    parser.add_argument(
        "input",
        help="Input PDF file or directory path"
    )
    
    parser.add_argument(
        "-o", "--output-dir",
        default="data/output",
        help="Output directory for results (default: data/output)"
    )
    
    parser.add_argument(
        "-c", "--config",
        default="config/config.json",
        help="Configuration file path (default: config/config.json)"
    )
    
    parser.add_argument(
        "--no-db",
        action="store_true",
        help="Do not save to database"
    )
    
    parser.add_argument(
        "-r", "--generate-report",
        action="store_true",
        help="Generate extraction report"
    )
    
    parser.add_argument(
        "-s", "--show-formulas",
        action="store_true",
        help="Show extracted formulas in console"
    )
    
    parser.add_argument(
        "--test-execution",
        action="store_true",
        help="Test formula execution from database"
    )
    
    parser.add_argument(
        "--formula-type",
        help="Filter formulas by type (for test execution)"
    )
    
    parser.add_argument(
        "--min-confidence",
        type=float,
        default=0.8,
        help="Minimum confidence threshold (default: 0.8)"
    )
    
    args = parser.parse_args()
    
    # 로고 표시
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║          Insurance Formula Extractor v1.0                 ║
    ║                                                           ║
    ║  Extract mathematical formulas from insurance PDFs with   ║
    ║  high accuracy using Pix2Text and advanced OCR           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    # 설정 파일 확인
    if not Path(args.config).exists():
        logger.error(f"Configuration file not found: {args.config}")
        sys.exit(1)
    
    # 테스트 모드
    if args.test_execution:
        test_formula_execution(args)
        return
    
    # 입력 경로 확인
    input_path = Path(args.input)
    
    if not input_path.exists():
        logger.error(f"Input path not found: {args.input}")
        sys.exit(1)
    
    # 처리 시작
    start_time = datetime.now()
    
    if input_path.is_file() and input_path.suffix.lower() == '.pdf':
        # 단일 PDF 파일 처리
        process_single_pdf(str(input_path), args)
    elif input_path.is_dir():
        # 디렉토리 처리
        process_directory(str(input_path), args)
    else:
        logger.error("Input must be a PDF file or directory")
        sys.exit(1)
    
    # 처리 시간 출력
    end_time = datetime.now()
    duration = end_time - start_time
    print(f"\nProcessing completed in: {duration}")
    
    logger.info("All processing completed")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)