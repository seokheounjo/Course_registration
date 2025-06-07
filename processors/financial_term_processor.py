# processors/financial_term_processor.py
"""
한글 금융 문서에서 금융 용어 추출 및 정규화
"""

import re
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

class FinancialTermProcessor:
    """금융 용어 처리 클래스"""
    
    def __init__(self, config):
        self.config = config
        
        # 금융 용어 사전 로드
        self.financial_terms = self._load_financial_terms()
        
        # 한글 금융 용어 패턴
        self.korean_patterns = {
            # 기본 금융 용어
            "investment": [
                "투자", "투자금", "투자액", "투자수익", "투자손실", "투자자",
                "투자포트폴리오", "투자전략", "투자위험", "투자기간"
            ],
            "finance": [
                "금융", "금융기관", "금융상품", "금융시장", "금융위기",
                "금융서비스", "금융회사", "금융업", "금융산업"
            ],
            "banking": [
                "은행", "예금", "적금", "대출", "이자", "이자율", "금리",
                "예금자", "대출자", "신용", "신용도", "신용등급"
            ],
            "securities": [
                "증권", "주식", "채권", "펀드", "파생상품", "옵션", "선물",
                "주가", "채권가격", "수익률", "배당", "배당금"
            ],
            "insurance": [
                "보험", "보험료", "보험금", "보장", "보험가입자", "피보험자",
                "보험회사", "보험상품", "생명보험", "손해보험"
            ],
            "risk": [
                "위험", "리스크", "위험관리", "위험평가", "신용위험", "시장위험",
                "운영위험", "유동성위험", "변동성", "불확실성"
            ],
            "ratios": [
                "비율", "비", "배수", "지수", "지표", "수익률", "손익률",
                "자기자본비율", "부채비율", "유동비율", "당좌비율"
            ],
            "analysis": [
                "분석", "평가", "진단", "검토", "조사", "연구", "측정",
                "계산", "산출", "산정", "추정", "예측"
            ]
        }
        
        # 영문 약어 패턴
        self.english_abbreviations = {
            "ROI": "투자수익률", "ROE": "자기자본수익률", "ROA": "총자산수익률",
            "PER": "주가수익비율", "PBR": "주가순자산비율", "EPS": "주당순이익",
            "BPS": "주당순자산", "DPS": "주당배당금", "NPV": "순현재가치",
            "IRR": "내부수익률", "WACC": "가중평균자본비용", "EVA": "경제적부가가치",
            "EBITDA": "법인세·이자·감가상각비 차감전 영업이익", "CAPM": "자본자산가격모형",
            "VaR": "위험가치", "GDP": "국내총생산", "CPI": "소비자물가지수",
            "PPI": "생산자물가지수", "KRW": "원화", "USD": "달러", "EUR": "유로"
        }
        
        # 숫자 + 단위 패턴
        self.unit_patterns = [
            (r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*원', "currency_krw"),
            (r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*달러', "currency_usd"),
            (r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:퍼센트|%)', "percentage"),
            (r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:베이시스포인트|bp)', "basis_points"),
            (r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:억|만)', "amount_korean"),
            (r'(\d{4})\s*년\s*(\d{1,2})\s*월', "date_korean"),
            (r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:배|번)', "multiple")
        ]
        
        # 복합 표현 패턴
        self.compound_patterns = [
            # 수식과 함께 나오는 표현
            (r'([가-힣]+)\s*=\s*(\d+(?:\.\d+)?)', "formula_variable"),
            # 비율 표현
            (r'(\d+(?:\.\d+)?)\s*:\s*(\d+(?:\.\d+)?)', "ratio"),
            # 기간 표현
            (r'(\d+)\s*년\s*(\d+)\s*개월', "period"),
            # 등급 표현
            (r'([가-힣]+)\s*등급', "rating"),
        ]
    
    def _load_financial_terms(self) -> Dict[str, Any]:
        """금융 용어 사전 로드"""
        terms_file = self.config.project_root / "resources" / "financial_terms.json"
        
        # 기본 금융 용어 사전
        default_terms = {
            "banking": [
                "예금", "적금", "대출", "신용", "이자", "원금", "만기", "연체",
                "담보", "보증", "한도", "잔액", "입금", "출금", "이체"
            ],
            "investment": [
                "투자", "수익", "손실", "위험", "포트폴리오", "분산투자",
                "자산배분", "리밸런싱", "벤치마크", "추적오차"
            ],
            "securities": [
                "주식", "채권", "펀드", "상장", "상장폐지", "공모", "사모",
                "시가총액", "거래량", "체결", "호가", "매수", "매도"
            ],
            "derivatives": [
                "파생상품", "옵션", "선물", "스왑", "포워드", "콜옵션", "풋옵션",
                "행사가격", "만기일", "프리미엄", "델타", "감마", "베가", "세타"
            ],
            "risk_management": [
                "위험관리", "헤지", "포지션", "익스포저", "스트레스테스트",
                "시나리오분석", "몬테카를로", "백테스팅", "리스크예산"
            ],
            "analysis": [
                "재무분석", "기술분석", "기본분석", "밸류에이션", "DCF",
                "멀티플", "동종업체", "동일업종", "업종평균", "시장평균"
            ]
        }
        
        try:
            if terms_file.exists():
                with open(terms_file, 'r', encoding='utf-8') as f:
                    loaded_terms = json.load(f)
                    # 기본 사전과 병합
                    for category, terms in loaded_terms.items():
                        if category in default_terms:
                            default_terms[category].extend(terms)
                        else:
                            default_terms[category] = terms
            else:
                # 기본 사전 파일 생성
                terms_file.parent.mkdir(exist_ok=True)
                with open(terms_file, 'w', encoding='utf-8') as f:
                    json.dump(default_terms, f, ensure_ascii=False, indent=2)
                    
        except Exception as e:
            logger.warning(f"금융 용어 사전 로드 실패: {e}")
        
        return default_terms
    
    def extract_terms(self, text: str) -> List[Dict[str, Any]]:
        """텍스트에서 금융 용어 추출"""
        if not text:
            return []
        
        extracted_terms = []
        
        # 1. 한글 금융 용어 추출
        korean_terms = self._extract_korean_terms(text)
        extracted_terms.extend(korean_terms)
        
        # 2. 영문 약어 추출
        english_terms = self._extract_english_abbreviations(text)
        extracted_terms.extend(english_terms)
        
        # 3. 숫자+단위 패턴 추출
        unit_terms = self._extract_unit_patterns(text)
        extracted_terms.extend(unit_terms)
        
        # 4. 복합 표현 추출
        compound_terms = self._extract_compound_patterns(text)
        extracted_terms.extend(compound_terms)
        
        # 5. 중복 제거 및 정렬
        unique_terms = self._deduplicate_terms(extracted_terms)
        
        return unique_terms
    
    def _extract_korean_terms(self, text: str) -> List[Dict[str, Any]]:
        """한글 금융 용어 추출"""
        terms = []
        
        for category, term_list in self.korean_patterns.items():
            for term in term_list:
                pattern = rf'\b{re.escape(term)}\b'
                matches = re.finditer(pattern, text)
                
                for match in matches:
                    terms.append({
                        "text": match.group(),
                        "category": category,
                        "type": "korean_term",
                        "position": (match.start(), match.end()),
                        "confidence": 0.9,
                        "normalized": term
                    })
        
        return terms
    
    def _extract_english_abbreviations(self, text: str) -> List[Dict[str, Any]]:
        """영문 약어 추출"""
        terms = []
        
        for abbrev, korean_meaning in self.english_abbreviations.items():
            # 정확한 매칭 (단어 경계 고려)
            pattern = rf'\b{re.escape(abbrev)}\b'
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                terms.append({
                    "text": match.group().upper(),
                    "category": "abbreviation",
                    "type": "english_abbrev",
                    "position": (match.start(), match.end()),
                    "confidence": 0.95,
                    "normalized": abbrev.upper(),
                    "korean_meaning": korean_meaning
                })
        
        return terms
    
    def _extract_unit_patterns(self, text: str) -> List[Dict[str, Any]]:
        """숫자+단위 패턴 추출"""
        terms = []
        
        for pattern, unit_type in self.unit_patterns:
            matches = re.finditer(pattern, text)
            
            for match in matches:
                value = match.group(1) if match.groups() else match.group()
                
                terms.append({
                    "text": match.group(),
                    "category": "amount",
                    "type": unit_type,
                    "position": (match.start(), match.end()),
                    "confidence": 0.85,
                    "normalized": value,
                    "value": self._parse_numeric_value(value)
                })
        
        return terms
    
    def _extract_compound_patterns(self, text: str) -> List[Dict[str, Any]]:
        """복합 표현 추출"""
        terms = []
        
        for pattern, compound_type in self.compound_patterns:
            matches = re.finditer(pattern, text)
            
            for match in matches:
                terms.append({
                    "text": match.group(),
                    "category": "compound",
                    "type": compound_type,
                    "position": (match.start(), match.end()),
                    "confidence": 0.8,
                    "normalized": match.group(),
                    "components": list(match.groups()) if match.groups() else [match.group()]
                })
        
        return terms
    
    def _parse_numeric_value(self, value_str: str) -> Optional[float]:
        """숫자 문자열을 float로 변환"""
        try:
            # 쉼표 제거
            cleaned = value_str.replace(',', '')
            return float(cleaned)
        except (ValueError, AttributeError):
            return None
    
    def _deduplicate_terms(self, terms: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """중복 용어 제거"""
        if not terms:
            return []
        
        # 위치 기준으로 정렬
        terms.sort(key=lambda x: x["position"][0])
        
        unique_terms = []
        seen_positions = set()
        
        for term in terms:
            pos = term["position"]
            
            # 겹치는 위치 확인
            overlapping = False
            for seen_start, seen_end in seen_positions:
                if not (pos[1] <= seen_start or pos[0] >= seen_end):
                    overlapping = True
                    break
            
            if not overlapping:
                unique_terms.append(term)
                seen_positions.add(pos)
        
        return unique_terms
    
    def normalize_term(self, term: str, context: str = "") -> Dict[str, Any]:
        """용어 정규화"""
        normalized_info = {
            "original": term,
            "normalized": term,
            "category": "unknown",
            "confidence": 0.5,
            "alternatives": []
        }
        
        # 영문 약어 정규화
        if term.upper() in self.english_abbreviations:
            normalized_info.update({
                "normalized": term.upper(),
                "category": "abbreviation",
                "confidence": 0.95,
                "korean_meaning": self.english_abbreviations[term.upper()]
            })
        
        # 한글 용어 정규화
        else:
            for category, term_list in self.korean_patterns.items():
                if term in term_list:
                    normalized_info.update({
                        "category": category,
                        "confidence": 0.9
                    })
                    break
                
                # 유사 용어 찾기
                similar_terms = [t for t in term_list if term in t or t in term]
                if similar_terms:
                    normalized_info["alternatives"] = similar_terms
        
        return normalized_info
    
    def categorize_financial_context(self, text: str) -> Dict[str, Any]:
        """금융 컨텍스트 분류"""
        context_scores = {}
        
        for category, keywords in self.korean_patterns.items():
            score = 0
            found_keywords = []
            
            for keyword in keywords:
                if keyword in text:
                    score += 1
                    found_keywords.append(keyword)
            
            if score > 0:
                context_scores[category] = {
                    "score": score,
                    "keywords": found_keywords,
                    "weight": score / len(keywords)
                }
        
        # 영문 약어도 확인
        abbrev_score = 0
        found_abbrevs = []
        for abbrev in self.english_abbreviations:
            if abbrev in text.upper():
                abbrev_score += 1
                found_abbrevs.append(abbrev)
        
        if abbrev_score > 0:
            context_scores["abbreviation"] = {
                "score": abbrev_score,
                "keywords": found_abbrevs,
                "weight": abbrev_score / len(self.english_abbreviations)
            }
        
        # 주요 카테고리 결정
        primary_category = "general"
        max_weight = 0
        
        for category, info in context_scores.items():
            if info["weight"] > max_weight:
                max_weight = info["weight"]
                primary_category = category
        
        return {
            "primary_category": primary_category,
            "confidence": max_weight,
            "all_categories": context_scores,
            "is_financial": len(context_scores) > 0
        }
    
    def extract_financial_relationships(self, text: str) -> List[Dict[str, Any]]:
        """금융 용어 간 관계 추출"""
        relationships = []
        
        # 간단한 관계 패턴들
        relation_patterns = [
            # "A는 B보다 높다/낮다"
            (r'([가-힣A-Z]+)\s*(?:는|이)\s*([가-힣A-Z]+)\s*보다\s*(높다|낮다|크다|작다)', "comparison"),
            # "A와 B의 비율"
            (r'([가-힣A-Z]+)\s*(?:와|과)\s*([가-힣A-Z]+)\s*(?:의\s*)?비율', "ratio_relationship"),
            # "A에 따른 B"
            (r'([가-힣A-Z]+)\s*에\s*따른\s*([가-힣A-Z]+)', "causation"),
            # "A 대비 B"
            (r'([가-힣A-Z]+)\s*대비\s*([가-힣A-Z]+)', "relative_comparison"),
        ]
        
        for pattern, relation_type in relation_patterns:
            matches = re.finditer(pattern, text)
            
            for match in matches:
                if len(match.groups()) >= 2:
                    relationships.append({
                        "type": relation_type,
                        "entity1": match.group(1),
                        "entity2": match.group(2),
                        "modifier": match.group(3) if len(match.groups()) > 2 else None,
                        "full_text": match.group(),
                        "position": (match.start(), match.end())
                    })
        
        return relationships
    
    def generate_term_summary(self, terms: List[Dict[str, Any]]) -> Dict[str, Any]:
        """추출된 용어들의 요약 정보 생성"""
        if not terms:
            return {"total": 0, "categories": {}, "types": {}}
        
        # 카테고리별 집계
        categories = {}
        types = {}
        
        for term in terms:
            category = term.get("category", "unknown")
            term_type = term.get("type", "unknown")
            
            categories[category] = categories.get(category, 0) + 1
            types[term_type] = types.get(term_type, 0) + 1
        
        # 가장 많이 나온 용어들
        term_frequency = {}
        for term in terms:
            text = term.get("normalized", term.get("text", ""))
            term_frequency[text] = term_frequency.get(text, 0) + 1
        
        top_terms = sorted(term_frequency.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "total": len(terms),
            "categories": categories,
            "types": types,
            "top_terms": top_terms,
            "avg_confidence": sum(t.get("confidence", 0) for t in terms) / len(terms)
        }
    
    def save_extracted_terms(self, terms: List[Dict[str, Any]], output_path: Path):
        """추출된 용어를 파일로 저장"""
        try:
            # JSON 형태로 저장
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(terms, f, ensure_ascii=False, indent=2)
            
            # CSV 형태로도 저장
            csv_path = output_path.with_suffix('.csv')
            
            import pandas as pd
            
            # 용어 데이터를 DataFrame에 맞게 변환
            csv_data = []
            for term in terms:
                csv_row = {
                    "term_text": term.get("text", ""),
                    "category": term.get("category", ""),
                    "type": term.get("type", ""),
                    "confidence": term.get("confidence", 0),
                    "normalized": term.get("normalized", ""),
                    "position_start": term.get("position", (0, 0))[0],
                    "position_end": term.get("position", (0, 0))[1]
                }
                
                # 추가 정보가 있으면 포함
                if "korean_meaning" in term:
                    csv_row["korean_meaning"] = term["korean_meaning"]
                if "value" in term:
                    csv_row["numeric_value"] = term["value"]
                
                csv_data.append(csv_row)
            
            df = pd.DataFrame(csv_data)
            df.to_csv(csv_path, index=False, encoding='utf-8-sig')
            
            logger.info(f"금융 용어 저장 완료: {output_path}")
            
        except Exception as e:
            logger.error(f"금융 용어 저장 실패: {e}")
    
    def get_processor_info(self) -> Dict[str, Any]:
        """처리기 정보 반환"""
        return {
            "total_term_categories": len(self.korean_patterns),
            "total_abbreviations": len(self.english_abbreviations),
            "pattern_count": len(self.unit_patterns) + len(self.compound_patterns),
            "financial_terms_loaded": len(self.financial_terms)
        }