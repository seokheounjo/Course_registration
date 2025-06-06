# -*- coding: utf-8 -*-
"""
텍스트 처리기 - 한글 금융 문서 텍스트 처리
"""

import re
import logging
from typing import List, Dict, Optional, Tuple
from collections import Counter

# KoNLPy import (optional)
try:
    from konlpy.tag import Okt, Hannanum
    KONLPY_AVAILABLE = True
except ImportError:
    KONLPY_AVAILABLE = False

class TextProcessor:
    """텍스트 처리 클래스"""
    
    def __init__(self, enable_korean_nlp: bool = True):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.enable_korean_nlp = enable_korean_nlp and KONLPY_AVAILABLE
        
        if self.enable_korean_nlp:
            try:
                self.okt = Okt()
                self.hannanum = Hannanum()
                self.logger.info("KoNLPy 초기화 완료")
            except Exception as e:
                self.logger.warning(f"KoNLPy 초기화 실패: {e}")
                self.enable_korean_nlp = False
        
        # 정규식 패턴
        self.patterns = {
            'amount': r'[\d,]+(?:\.\d+)?(?:\s*(?:원|달러|USD|KRW|백만|천만|억))',
            'percentage': r'\d+(?:\.\d+)?(?:\s*%)',
            'date': r'\d{4}[-./년]\s*\d{1,2}[-./월]\s*\d{1,2}(?:일)?',
            'account': r'[0-9]{3,4}-[0-9]{2,4}-[0-9]{4,}',
            'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            'phone': r'(?:02|0\d{1,2})[-.\s]?\d{3,4}[-.\s]?\d{4}',
            'business_number': r'\d{3}-\d{2}-\d{5}'
        }
    
    def process_text(self, text: str) -> Dict[str, any]:
        """텍스트 종합 처리"""
        result = {
            'original': text,
            'cleaned': self.clean_text(text),
            'entities': self.extract_entities(text),
            'keywords': self.extract_keywords(text),
            'sentences': self.split_sentences(text)
        }
        
        if self.enable_korean_nlp:
            result['morphs'] = self.analyze_morphology(text)
            result['nouns'] = self.extract_nouns(text)
        
        return result
    
    def clean_text(self, text: str) -> str:
        """텍스트 정리"""
        # 특수문자 정리
        text = re.sub(r'[ --]', '', text)
        
        # 중복 공백 제거
        text = re.sub(r'\s+', ' ', text)
        
        # 줄바꿈 정리
        text = re.sub(r'
\s*
', '

', text)
        
        return text.strip()
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """개체명 추출"""
        entities = {}
        
        for entity_type, pattern in self.patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                entities[entity_type] = list(set(matches))
        
        return entities
    
    def extract_keywords(self, text: str, top_n: int = 10) -> List[Tuple[str, int]]:
        """키워드 추출"""
        if self.enable_korean_nlp:
            # 명사 기반 키워드 추출
            nouns = self.extract_nouns(text)
            counter = Counter(nouns)
            
            # 불용어 제거
            stopwords = {'것', '등', '수', '이', '그', '저', '때', '년', '월', '일'}
            keywords = [
                (word, count) for word, count in counter.most_common(top_n * 2)
                if word not in stopwords and len(word) > 1
            ]
            
            return keywords[:top_n]
        else:
            # 단순 단어 빈도
            words = text.split()
            words = [w for w in words if len(w) > 2]
            counter = Counter(words)
            return counter.most_common(top_n)
    
    def split_sentences(self, text: str) -> List[str]:
        """문장 분리"""
        # 한국어 문장 종결 패턴
        sentence_endings = r'[.!?]\s*'
        
        # 예외 처리 (소수점, 약어 등)
        text = re.sub(r'(\d)\.(\d)', r'<DOT>', text)
        text = re.sub(r'([A-Z])\.([A-Z])', r'<DOT>', text)
        
        sentences = re.split(sentence_endings, text)
        sentences = [s.replace('<DOT>', '.').strip() 
                    for s in sentences if s.strip()]
        
        return sentences
    
    def analyze_morphology(self, text: str) -> List[Tuple[str, str]]:
        """형태소 분석"""
        if not self.enable_korean_nlp:
            return []
        
        try:
            return self.okt.pos(text)
        except Exception as e:
            self.logger.error(f"형태소 분석 실패: {e}")
            return []
    
    def extract_nouns(self, text: str) -> List[str]:
        """명사 추출"""
        if not self.enable_korean_nlp:
            return []
        
        try:
            return self.hannanum.nouns(text)
        except Exception as e:
            self.logger.error(f"명사 추출 실패: {e}")
            return []
    
    def normalize_numbers(self, text: str) -> str:
        """숫자 정규화"""
        # 한글 숫자를 아라비아 숫자로
        korean_nums = {
            '일': '1', '이': '2', '삼': '3', '사': '4', '오': '5',
            '육': '6', '칠': '7', '팔': '8', '구': '9', '십': '10',
            '백': '100', '천': '1000', '만': '10000', '억': '100000000'
        }
        
        for kor, num in korean_nums.items():
            text = text.replace(kor, num)
        
        return text
    
    def extract_financial_numbers(self, text: str) -> List[Dict[str, str]]:
        """금융 관련 숫자 추출"""
        numbers = []
        
        # 금액 패턴
        amount_pattern = r'([\d,]+(?:\.\d+)?)\s*(원|달러|USD|KRW|백만원|천만원|억원)'
        for match in re.finditer(amount_pattern, text):
            numbers.append({
                'value': match.group(1),
                'unit': match.group(2),
                'type': 'amount',
                'position': match.span()
            })
        
        # 백분율 패턴
        percent_pattern = r'([\d.]+)\s*(%|퍼센트|프로)'
        for match in re.finditer(percent_pattern, text):
            numbers.append({
                'value': match.group(1),
                'unit': '%',
                'type': 'percentage',
                'position': match.span()
            })
        
        return numbers
