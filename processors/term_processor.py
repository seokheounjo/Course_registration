# -*- coding: utf-8 -*-
"""
금융 용어 처리기
"""

import re
import json
from typing import List, Dict, Set, Optional
from pathlib import Path
import logging

class FinancialTermProcessor:
    """금융 용어 추출 및 분류"""
    
    def __init__(self, terms_file: Optional[Path] = None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.terms = self._load_default_terms()
        
        if terms_file and terms_file.exists():
            self._load_custom_terms(terms_file)
    
    def _load_default_terms(self) -> Dict[str, List[str]]:
        """기본 금융 용어 사전 로드"""
        return {
            "accounting": [
                "자산", "부채", "자본", "매출", "매출액", "영업이익", "당기순이익",
                "총자산", "총부채", "자기자본", "이익잉여금", "자본잉여금",
                "유동자산", "비유동자산", "유동부채", "비유동부채",
                "매출채권", "재고자산", "현금및현금성자산", "단기차입금", "장기차입금",
                "감가상각비", "대손상각비", "영업활동현금흐름", "투자활동현금흐름",
                "재무활동현금흐름", "EBITDA", "EBIT"
            ],
            "financial_ratios": [
                "ROE", "ROA", "ROI", "ROIC", "자기자본이익률", "총자산이익률",
                "부채비율", "유동비율", "당좌비율", "이자보상배율",
                "총자산회전율", "재고자산회전율", "매출채권회전율",
                "영업이익률", "순이익률", "매출총이익률",
                "PER", "PBR", "PSR", "PCR", "EV/EBITDA",
                "배당수익률", "배당성향", "주당순이익", "주당순자산"
            ],
            "insurance": [
                "보험료", "보험금", "책임준비금", "지급준비금", "미경과보험료",
                "손해율", "사업비율", "합산비율", "지급여력비율",
                "기본보험료", "위험보험료", "저축보험료", "부가보험료",
                "환급금", "해약환급금", "만기환급금", "중도환급금",
                "담보", "특약", "주계약", "갱신", "자동갱신",
                "면책기간", "면책사유", "보장개시일", "보험기간"
            ],
            "investment": [
                "수익률", "변동성", "샤프지수", "정보비율", "추적오차",
                "벤치마크", "초과수익", "알파", "베타", "상관계수",
                "포트폴리오", "자산배분", "리밸런싱", "헤지", "레버리지",
                "선물", "옵션", "스왑", "파생상품", "기초자산",
                "콜옵션", "풋옵션", "행사가격", "만기일", "내재가치"
            ],
            "banking": [
                "예금", "적금", "대출", "여신", "수신",
                "이자율", "금리", "기준금리", "대출금리", "예금금리",
                "원금", "이자", "연체이자", "중도상환수수료",
                "담보대출", "신용대출", "전세자금대출", "주택담보대출",
                "한도", "대출한도", "마이너스통장", "신용등급", "연체"
            ],
            "securities": [
                "주식", "채권", "증권", "유가증권", "주권",
                "보통주", "우선주", "신주", "구주", "자사주",
                "회사채", "국채", "지방채", "특수채", "전환사채",
                "액면가", "시가", "종가", "고가", "저가",
                "거래량", "거래대금", "시가총액", "호가", "매수호가"
            ],
            "tax": [
                "법인세", "소득세", "부가가치세", "양도소득세", "증여세",
                "세전이익", "세후이익", "과세표준", "세율", "공제",
                "이연법인세", "당기법인세", "법인세비용", "유효세율",
                "손금산입", "손금불산입", "익금산입", "익금불산입",
                "세무조정", "세무신고", "세무조사", "가산세", "환급"
            ],
            "general": [
                "재무제표", "손익계산서", "재무상태표", "현금흐름표",
                "사업보고서", "감사보고서", "분기보고서", "반기보고서",
                "연결재무제표", "별도재무제표", "주석", "감사의견",
                "회계연도", "사업연도", "결산", "배당", "유상증자"
            ]
        }
    
    def _load_custom_terms(self, terms_file: Path):
        """사용자 정의 용어 로드"""
        try:
            with open(terms_file, 'r', encoding='utf-8') as f:
                custom_terms = json.load(f)
                
            # 기존 용어에 추가
            for category, terms in custom_terms.items():
                if category in self.terms:
                    self.terms[category].extend(terms)
                else:
                    self.terms[category] = terms
                    
            self.logger.info(f"사용자 정의 용어 {len(custom_terms)} 카테고리 로드")
            
        except Exception as e:
            self.logger.error(f"사용자 정의 용어 로드 실패: {e}")
    
    def extract_terms(self, text: str) -> Dict[str, List[str]]:
        """텍스트에서 금융 용어 추출"""
        found_terms = {}
        
        for category, terms in self.terms.items():
            matches = []
            for term in terms:
                # 정확한 매칭을 위한 정규식
                pattern = r'' + re.escape(term) + r''
                if re.search(pattern, text):
                    matches.append(term)
            
            if matches:
                found_terms[category] = list(set(matches))  # 중복 제거
        
        return found_terms
    
    def get_term_context(self, text: str, term: str, window: int = 50) -> List[str]:
        """용어 주변 문맥 추출"""
        contexts = []
        pattern = r'' + re.escape(term) + r''
        
        for match in re.finditer(pattern, text):
            start = max(0, match.start() - window)
            end = min(len(text), match.end() + window)
            
            context = text[start:end]
            # 문장 경계에서 자르기
            if start > 0:
                context = '...' + context[context.find(' ')+1:]
            if end < len(text):
                context = context[:context.rfind(' ')] + '...'
            
            contexts.append(context)
        
        return contexts
    
    def analyze_term_frequency(self, text: str) -> Dict[str, Dict[str, int]]:
        """용어 빈도 분석"""
        frequency = {}
        
        for category, terms in self.terms.items():
            term_freq = {}
            for term in terms:
                pattern = r'' + re.escape(term) + r''
                count = len(re.findall(pattern, text))
                if count > 0:
                    term_freq[term] = count
            
            if term_freq:
                frequency[category] = term_freq
        
        return frequency
    
    def get_term_definition(self, term: str) -> Optional[str]:
        """용어 정의 반환 (간단한 예시)"""
        definitions = {
            "ROE": "자기자본이익률. 당기순이익을 자기자본으로 나눈 비율",
            "ROA": "총자산이익률. 당기순이익을 총자산으로 나눈 비율",
            "EBITDA": "이자, 세금, 감가상각비 차감 전 영업이익",
            "PER": "주가수익비율. 주가를 주당순이익으로 나눈 비율",
            "부채비율": "총부채를 자기자본으로 나눈 비율",
            "유동비율": "유동자산을 유동부채로 나눈 비율",
            "손해율": "지급보험금을 수입보험료로 나눈 비율",
            "합산비율": "손해율과 사업비율을 합한 비율"
        }
        
        return definitions.get(term)
    
    def classify_document(self, text: str) -> str:
        """문서 유형 분류"""
        term_counts = {}
        
        for category, terms in self.terms.items():
            count = 0
            for term in terms:
                pattern = r'' + re.escape(term) + r''
                count += len(re.findall(pattern, text))
            term_counts[category] = count
        
        # 가장 많이 나타난 카테고리
        if term_counts:
            return max(term_counts, key=term_counts.get)
        
        return "general"
