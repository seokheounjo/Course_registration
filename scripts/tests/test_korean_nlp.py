# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
한국어 NLP 테스트
"""

def test_konlpy():
    """KoNLPy 테스트"""
    try:
        from konlpy.tag import Okt, Hannanum
        
        print("✅ KoNLPy 설치 확인")
        
        # 테스트 문장
        text = "보험료 및 책임준비금 산출방법서의 내용을 분석합니다."
        
        # Okt 테스트
        okt = Okt()
        print(f"\nOkt 형태소 분석: {okt.morphs(text)}")
        print(f"Okt 품사 태깅: {okt.pos(text)}")
        
        # Hannanum 테스트
        hannanum = Hannanum()
        print(f"\nHannanum 명사 추출: {hannanum.nouns(text)}")
        
        return True
        
    except ImportError as e:
        print(f"❌ KoNLPy 테스트 실패: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("한국어 NLP 테스트")
    print("="*60)
    
    if test_konlpy():
        print("\n✅ 한국어 NLP 기능이 정상 작동합니다!")
    else:
        print("\n⚠️  한국어 NLP를 사용하려면 KoNLPy를 설치하세요.")
        print("설치 방법: python scripts/setup/install_konlpy.py")
