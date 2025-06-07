#!/usr/bin/env python3
"""
KoNLPy 설치 도우미
Windows에서 KoNLPy와 JPype1을 올바르게 설치
"""

import os
import sys
import subprocess
import platform

def check_java():
    """Java 설치 확인"""
    try:
        result = subprocess.run(['java', '-version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Java가 설치되어 있습니다.")
            print(result.stderr)
            return True
    except:
        pass
    
    print("❌ Java가 설치되어 있지 않습니다.")
    return False

def install_konlpy():
    """KoNLPy 설치"""
    print("\n=== KoNLPy 설치 시작 ===")
    
    # 1. Java 확인
    if not check_java():
        print("\nJava가 필요합니다. 이미 설치되어 있다면 PATH를 확인하세요.")
        return False
    
    # 2. 시스템 정보
    print(f"\n시스템 정보:")
    print(f"OS: {platform.system()}")
    print(f"Python: {sys.version}")
    print(f"아키텍처: {platform.machine()}")
    
    # 3. JPype1 설치 (Windows용 특별 처리)
    print("\n1. JPype1 설치 중...")
    if platform.system() == "Windows":
        # Windows에서는 미리 빌드된 wheel 사용
        py_version = f"{sys.version_info.major}{sys.version_info.minor}"
        arch = "amd64" if platform.machine().endswith('64') else "win32"
        
        jpype_wheel = f"JPype1-1.4.1-cp{py_version}-cp{py_version}-win_{arch}.whl"
        
        print(f"JPype1 wheel 다운로드 시도: {jpype_wheel}")
        subprocess.run([sys.executable, "-m", "pip", "install", 
                       "--upgrade", "JPype1"], check=False)
    else:
        subprocess.run([sys.executable, "-m", "pip", "install", 
                       "--upgrade", "JPype1"], check=False)
    
    # 4. KoNLPy 설치
    print("\n2. KoNLPy 설치 중...")
    result = subprocess.run([sys.executable, "-m", "pip", "install", 
                           "--upgrade", "konlpy"], check=False)
    
    # 5. 설치 확인
    print("\n3. 설치 확인 중...")
    try:
        import jpype
        print(f"✅ JPype1 버전: {jpype.__version__}")
        
        import konlpy
        print(f"✅ KoNLPy 버전: {konlpy.__version__}")
        
        # 형태소 분석기 테스트
        from konlpy.tag import Hannanum
        hannanum = Hannanum()
        test_result = hannanum.morphs("테스트 문장입니다.")
        print(f"✅ 형태소 분석 테스트 성공: {test_result}")
        
        print("\n🎉 KoNLPy 설치 성공!")
        return True
        
    except ImportError as e:
        print(f"\n❌ 설치 실패: {e}")
        print("\n문제 해결 방법:")
        print("1. Java 환경 변수 확인:")
        print("   - JAVA_HOME이 설정되어 있는지 확인")
        print("   - PATH에 Java bin 디렉토리가 있는지 확인")
        print("\n2. 수동 설치 시도:")
        print("   pip uninstall jpype1 konlpy")
        print("   pip install jpype1==1.4.1")
        print("   pip install konlpy")
        
        return False

def main():
    print("="*60)
    print("KoNLPy 설치 도우미")
    print("="*60)
    
    # Java 환경 변수 출력
    print("\n환경 변수:")
    java_home = os.environ.get('JAVA_HOME', '설정되지 않음')
    print(f"JAVA_HOME: {java_home}")
    
    # 설치 진행
    if install_konlpy():
        print("\n✅ 모든 설치가 완료되었습니다!")
        print("\n이제 프로그램을 다시 실행하면 한국어 처리가 개선됩니다:")
        print("python main.py documents/ --ocr-engine paddleocr --detect-formulas --extract-terms")
    else:
        print("\n⚠️  KoNLPy 설치에 실패했습니다.")
        print("하지만 프로그램은 기본 한국어 처리로 동작합니다.")

if __name__ == "__main__":
    main()