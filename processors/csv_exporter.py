# processors/csv_exporter.py
"""
CSV 내보내기 모듈
"""

import logging
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class CSVExporter:
    """CSV 내보내기 처리기"""
    
    def __init__(self, config):
        self.config = config
        self.encoding = 'utf-8-sig'  # BOM 포함 (Excel 한글 호환)
    
    def export_to_csv(self, analysis_result) -> Dict[str, Path]:
        """분석 결과를 CSV로 내보내기"""
        csv_files = {}
        
        try:
            # 1. 메타데이터 CSV
            metadata_csv = self._export_metadata(analysis_result)
            if metadata_csv:
                csv_files['metadata'] = metadata_csv
            
            # 2. 텍스트 CSV
            text_csv = self._export_texts(analysis_result)
            if text_csv:
                csv_files['texts'] = text_csv
            
            # 3. 수식 CSV
            if analysis_result.formulas:
                formula_csv = self._export_formulas(analysis_result)
                if formula_csv:
                    csv_files['formulas'] = formula_csv
            
            # 4. 테이블 CSV
            if analysis_result.tables:
                table_csvs = self._export_tables(analysis_result)
                csv_files.update(table_csvs)
            
            # 5. 금융 용어 CSV
            if analysis_result.financial_terms:
                terms_csv = self._export_financial_terms(analysis_result)
                if terms_csv:
                    csv_files['financial_terms'] = terms_csv
            
            # 6. 통합 요약 CSV
            summary_csv = self._export_summary(analysis_result)
            if summary_csv:
                csv_files['summary'] = summary_csv
            
            logger.info(f"CSV 내보내기 완료: {len(csv_files)}개 파일")
            
        except Exception as e:
            logger.error(f"CSV 내보내기 실패: {e}")
        
        return csv_files
    
    def _export_metadata(self, result) -> Optional[Path]:
        """메타데이터 CSV 내보내기"""
        try:
            metadata_list = []
            
            for key, value in result.metadata.items():
                metadata_list.append({
                    '항목': key,
                    '값': str(value)
                })
            
            df = pd.DataFrame(metadata_list)
            
            output_path = self.config.get_output_path(
                result.document_id, "csv", "metadata.csv"
            )
            
            df.to_csv(output_path, index=False, encoding=self.encoding)
            
            return output_path
            
        except Exception as e:
            logger.error(f"메타데이터 CSV 저장 실패: {e}")
            return None
    
    def _export_texts(self, result) -> Optional[Path]:
        """텍스트 CSV 내보내기"""
        try:
            text_data = []
            
            for i, text in enumerate(result.page_texts):
                # 한국어 분석 결과 포함
                korean_info = result.korean_texts[i] if i < len(result.korean_texts) else {}
                
                text_data.append({
                    '페이지': i + 1,
                    '텍스트': text[:500],  # 처음 500자
                    '전체길이': len(text),
                    '문장수': len(korean_info.get('sentences', [])),
                    '한글비율': korean_info.get('statistics', {}).get('korean_ratio', 0),
                    '키워드': ', '.join(korean_info.get('keywords', [])[:10])
                })
            
            df = pd.DataFrame(text_data)
            
            output_path = self.config.get_output_path(
                result.document_id, "csv", "texts.csv"
            )
            
            df.to_csv(output_path, index=False, encoding=self.encoding)
            
            return output_path
            
        except Exception as e:
            logger.error(f"텍스트 CSV 저장 실패: {e}")
            return None
    
    def _export_formulas(self, result) -> Optional[Path]:
        """수식 CSV 내보내기"""
        try:
            formula_data = []
            
            for formula in result.formulas:
                formula_data.append({
                    '페이지': formula.get('page_num', 0),
                    '수식ID': formula.get('id', ''),
                    'LaTeX': formula.get('latex', ''),
                    '원본텍스트': formula.get('original_text', ''),
                    '타입': formula.get('type', ''),
                    '신뢰도': formula.get('confidence', 0),
                    '한글수식': formula.get('is_korean', False),
                    '금융관련': formula.get('financial_context', False)
                })
            
            df = pd.DataFrame(formula_data)
            
            output_path = self.config.get_output_path(
                result.document_id, "csv", "formulas.csv"
            )
            
            df.to_csv(output_path, index=False, encoding=self.encoding)
            
            return output_path
            
        except Exception as e:
            logger.error(f"수식 CSV 저장 실패: {e}")
            return None
    
    def _export_tables(self, result) -> Dict[str, Path]:
        """테이블 CSV 내보내기"""
        table_files = {}
        
        # 테이블 요약 정보
        try:
            table_summary = []
            
            for table in result.tables:
                table_summary.append({
                    '테이블ID': table.get('id', 0),
                    '페이지': table.get('page_num', 0),
                    '행수': table.get('rows', 0),
                    '열수': table.get('columns', 0),
                    '셀수': table.get('cells', 0),
                    '신뢰도': table.get('confidence', 0)
                })
            
            df = pd.DataFrame(table_summary)
            
            summary_path = self.config.get_output_path(
                result.document_id, "csv", "table_summary.csv"
            )
            
            df.to_csv(summary_path, index=False, encoding=self.encoding)
            table_files['table_summary'] = summary_path
            
        except Exception as e:
            logger.error(f"테이블 요약 CSV 저장 실패: {e}")
        
        # 개별 테이블 데이터
        for i, table in enumerate(result.tables):
            try:
                # 이미 CSV 형태로 되어 있으면 직접 저장
                if 'csv' in table and table['csv']:
                    table_path = self.config.get_output_path(
                        result.document_id, "csv", f"table_{i+1}.csv"
                    )
                    
                    with open(table_path, 'w', encoding=self.encoding) as f:
                        f.write(table['csv'])
                    
                    table_files[f'table_{i+1}'] = table_path
                
                # 데이터가 있으면 DataFrame으로 변환
                elif 'data' in table and table['data']:
                    df = pd.DataFrame(table['data'])
                    
                    table_path = self.config.get_output_path(
                        result.document_id, "csv", f"table_{i+1}.csv"
                    )
                    
                    df.to_csv(table_path, index=False, encoding=self.encoding)
                    table_files[f'table_{i+1}'] = table_path
                    
            except Exception as e:
                logger.error(f"테이블 {i+1} CSV 저장 실패: {e}")
        
        return table_files
    
    def _export_financial_terms(self, result) -> Optional[Path]:
        """금융 용어 CSV 내보내기"""
        try:
            term_data = []
            
            for term in result.financial_terms:
                term_data.append({
                    '페이지': term.get('page_num', 0),
                    '용어': term.get('text', ''),
                    '카테고리': term.get('category', ''),
                    '타입': term.get('type', ''),
                    '정규화': term.get('normalized', ''),
                    '한글의미': term.get('korean_meaning', ''),
                    '신뢰도': term.get('confidence', 0),
                    '위치시작': term.get('position', [0, 0])[0],
                    '위치끝': term.get('position', [0, 0])[1]
                })
            
            df = pd.DataFrame(term_data)
            
            # 카테고리별 정렬
            df = df.sort_values(['카테고리', '페이지', '위치시작'])
            
            output_path = self.config.get_output_path(
                result.document_id, "csv", "financial_terms.csv"
            )
            
            df.to_csv(output_path, index=False, encoding=self.encoding)
            
            return output_path
            
        except Exception as e:
            logger.error(f"금융 용어 CSV 저장 실패: {e}")
            return None
    
    def _export_summary(self, result) -> Optional[Path]:
        """통합 요약 CSV 내보내기"""
        try:
            summary_data = {
                '문서ID': result.document_id,
                '총페이지': result.total_pages,
                '처리시간(초)': result.processing_time,
                '총문자수': sum(len(text) for text in result.page_texts),
                '추출된수식': len(result.formulas),
                '추출된테이블': len(result.tables),
                '금융용어수': len(result.financial_terms),
                '처리성공': result.success
            }
            
            # 페이지별 통계
            page_stats = []
            for i in range(result.total_pages):
                page_stat = {
                    '페이지': i + 1,
                    '텍스트길이': len(result.page_texts[i]) if i < len(result.page_texts) else 0,
                    '수식수': sum(1 for f in result.formulas if f.get('page_num') == i + 1),
                    '테이블수': sum(1 for t in result.tables if t.get('page_num') == i + 1),
                    '금융용어수': sum(1 for term in result.financial_terms if term.get('page_num') == i + 1)
                }
                page_stats.append(page_stat)
            
            # 요약 정보 DataFrame
            summary_df = pd.DataFrame([summary_data])
            summary_path = self.config.get_output_path(
                result.document_id, "csv", "summary.csv"
            )
            summary_df.to_csv(summary_path, index=False, encoding=self.encoding)
            
            # 페이지별 통계 DataFrame
            page_df = pd.DataFrame(page_stats)
            page_stats_path = self.config.get_output_path(
                result.document_id, "csv", "page_statistics.csv"
            )
            page_df.to_csv(page_stats_path, index=False, encoding=self.encoding)
            
            return summary_path
            
        except Exception as e:
            logger.error(f"요약 CSV 저장 실패: {e}")
            return None