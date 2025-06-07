# processors/korean_text_processor.py
"""
한국어 텍스트 처리 모듈
"""

import logging
import re
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

# KoNLPy 선택적 import
try:
    from konlpy.tag import Okt, Kkma, Hannanum
    KONLPY_AVAILABLE = True
except ImportError:
    KONLPY_AVAILABLE = False
    logger.warning("KoNLPy가 설치되지 않았습니다. 기본 처리만 가능합니다.")

class KoreanTextProcessor:
    """한국어 텍스트 처리기"""
    
    def __init__(self, config):
        self.config = config
        
        # 형태소 분석기 초기화
        self.pos_tagger = None
        if KONLPY_AVAILABLE and config.korean_nlp_enabled:
            try:
                self.pos_tagger = Okt()  # 가장 빠른 분석기
                logger.info("한국어 형태소 분석기 초기화 완료")
            except Exception as e:
                logger.error(f"형태소 분석기 초기화 실패: {e}")
        
        # 한국어 패턴
        self.korean_patterns = {
            'date': [
                r'(\d{4})\s*년\s*(\d{1,2})\s*월\s*(\d{1,2})\s*일',
                r'(\d{4})\.(\d{1,2})\.(\d{1,2})',
                r'(\d{2,4})-(\d{1,2})-(\d{1,2})'
            ],
            'money': [
                r'(\d{1,3}(?:,\d{3})*)\s*원',
                r'(\d{1,3}(?:,\d{3})*)\s*만\s*원',
                r'(\d{1,3}(?:,\d{3})*)\s*억\s*원'
            ],
            'percentage': [
                r'(\d+(?:\.\d+)?)\s*%',
                r'(\d+(?:\.\d+)?)\s*퍼센트',
                r'(\d+(?:\.\d+)?)\s*프로'
            ],
            'company': [
                r'([가-힣]+)\s*(?:주식회사|㈜|주\)|회사)',
                r'(?:주식회사|㈜|주\))\s*([가-힣]+)'
            ]
        }
    
    def process_korean_text(self, text: str) -> Dict[str, Any]:
        """한국어 텍스트 처리"""
        result = {
            'original_text': text,
            'processed_text': text,
            'entities': [],
            'pos_tags': [],
            'keywords': [],
            'sentences': [],
            'statistics': {}
        }
        
        # 기본 전처리
        processed_text = self._preprocess_text(text)
        result['processed_text'] = processed_text
        
        # 문장 분리
        sentences = self._split_sentences(processed_text)
        result['sentences'] = sentences
        
        # 개체명 인식
        entities = self._extract_entities(processed_text)
        result['entities'] = entities
        
        # 형태소 분석
        if self.pos_tagger:
            pos_tags = self._pos_tagging(processed_text)
            result['pos_tags'] = pos_tags
            
            # 키워드 추출
            keywords = self._extract_keywords(pos_tags)
            result['keywords'] = keywords
        
        # 통계 정보
        statistics = self._calculate_statistics(processed_text, sentences)
        result['statistics'] = statistics
        
        return result
    
    def _preprocess_text(self, text: str) -> str:
        """텍스트 전처리"""
        # 불필요한 공백 정리
        text = re.sub(r'\s+', ' ', text)
        
        # 특수문자 정규화
        text = text.replace('「', '"').replace('」', '"')
        text = text.replace('『', '"').replace('』', '"')
        text = text.replace('〈', '<').replace('〉', '>')
        
        # 줄바꿈 정리
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        return text.strip()
    
    def _split_sentences(self, text: str) -> List[str]:
        """문장 분리"""
        # 기본 문장 분리 패턴
        sentence_endings = r'[.!?]\s+'
        
        # 약어 등 예외 처리
        abbreviations = ['Mr.', 'Dr.', 'Prof.', 'Sr.', 'Jr.']
        
        # 임시 치환
        temp_text = text
        for i, abbr in enumerate(abbreviations):
            temp_text = temp_text.replace(abbr, f'__ABBR{i}__')
        
        # 문장 분리
        sentences = re.split(sentence_endings, temp_text)
        
        # 원래대로 복원
        result_sentences = []
        for sent in sentences:
            for i, abbr in enumerate(abbreviations):
                sent = sent.replace(f'__ABBR{i}__', abbr)
            if sent.strip():
                result_sentences.append(sent.strip())
        
        return result_sentences
    
    def _extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """개체명 인식"""
        entities = []
        
        # 날짜 추출
        for pattern in self.korean_patterns['date']:
            matches = re.finditer(pattern, text)
            for match in matches:
                entities.append({
                    'text': match.group(),
                    'type': 'date',
                    'position': (match.start(), match.end()),
                    'value': self._parse_date(match)
                })
        
        # 금액 추출
        for pattern in self.korean_patterns['money']:
            matches = re.finditer(pattern, text)
            for match in matches:
                entities.append({
                    'text': match.group(),
                    'type': 'money',
                    'position': (match.start(), match.end()),
                    'value': self._parse_money(match.group())
                })
        
        # 백분율 추출
        for pattern in self.korean_patterns['percentage']:
            matches = re.finditer(pattern, text)
            for match in matches:
                entities.append({
                    'text': match.group(),
                    'type': 'percentage',
                    'position': (match.start(), match.end()),
                    'value': float(match.group(1))
                })
        
        # 회사명 추출
        for pattern in self.korean_patterns['company']:
            matches = re.finditer(pattern, text)
            for match in matches:
                company_name = match.group(1) if match.group(1) else match.group()
                entities.append({
                    'text': match.group(),
                    'type': 'company',
                    'position': (match.start(), match.end()),
                    'value': company_name
                })
        
        # 중복 제거
        entities = self._remove_overlapping_entities(entities)
        
        return entities
    
    def _parse_date(self, match) -> str:
        """날짜 파싱"""
        groups = match.groups()
        if len(groups) >= 3:
            year = groups[0]
            month = groups[1].zfill(2)
            day = groups[2].zfill(2)
            return f"{year}-{month}-{day}"
        return match.group()
    
    def _parse_money(self, money_str: str) -> float:
        """금액 파싱"""
        # 쉼표 제거
        money_str = money_str.replace(',', '')
        
        # 숫자 추출
        numbers = re.findall(r'\d+', money_str)
        if not numbers:
            return 0
        
        amount = float(numbers[0])
        
        # 단위 처리
        if '억' in money_str:
            amount *= 100000000
        elif '만' in money_str:
            amount *= 10000
        
        return amount
    
    def _pos_tagging(self, text: str) -> List[Tuple[str, str]]:
        """형태소 분석"""
        if not self.pos_tagger:
            return []
        
        try:
            return self.pos_tagger.pos(text)
        except Exception as e:
            logger.error(f"형태소 분석 실패: {e}")
            return []
    
    def _extract_keywords(self, pos_tags: List[Tuple[str, str]]) -> List[str]:
        """키워드 추출"""
        keywords = []
        
        # 명사류 태그
        noun_tags = ['Noun', 'NNG', 'NNP', 'NNB']  # 일반명사, 고유명사, 의존명사
        
        for word, tag in pos_tags:
            if any(t in tag for t in noun_tags) and len(word) > 1:
                keywords.append(word)
        
        # 빈도수 계산
        from collections import Counter
        keyword_counts = Counter(keywords)
        
        # 상위 키워드 반환
        return [word for word, count in keyword_counts.most_common(20)]
    
    def _remove_overlapping_entities(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """겹치는 개체 제거"""
        if not entities:
            return entities
        
        # 위치로 정렬
        entities.sort(key=lambda x: x['position'][0])
        
        result = [entities[0]]
        
        for entity in entities[1:]:
            last_end = result[-1]['position'][1]
            current_start = entity['position'][0]
            
            if current_start >= last_end:
                result.append(entity)
        
        return result
    
    def _calculate_statistics(self, text: str, sentences: List[str]) -> Dict[str, Any]:
        """텍스트 통계 계산"""
        # 한글, 영어, 숫자 비율
        korean_chars = len(re.findall(r'[가-힣]', text))
        english_chars = len(re.findall(r'[a-zA-Z]', text))
        digit_chars = len(re.findall(r'\d', text))
        total_chars = len(text)
        
        statistics = {
            'total_characters': total_chars,
            'total_sentences': len(sentences),
            'korean_ratio': korean_chars / total_chars if total_chars > 0 else 0,
            'english_ratio': english_chars / total_chars if total_chars > 0 else 0,
            'digit_ratio': digit_chars / total_chars if total_chars > 0 else 0,
            'avg_sentence_length': sum(len(s) for s in sentences) / len(sentences) if sentences else 0
        }
        
        return statistics
    
    def extract_financial_sentences(self, text: str) -> List[str]:
        """금융 관련 문장 추출"""
        sentences = self._split_sentences(text)
        
        financial_keywords = [
            '투자', '수익', '손실', '이자', '금리', '대출', '예금', '자산',
            '부채', '자본', '매출', '영업이익', '당기순이익', '주가', '배당'
        ]
        
        financial_sentences = []
        
        for sent in sentences:
            if any(keyword in sent for keyword in financial_keywords):
                financial_sentences.append(sent)
        
        return financial_sentences