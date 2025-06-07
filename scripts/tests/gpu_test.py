# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
GPU 성능 테스트 및 최적화 확인
"""

import sys
import time
import torch
import numpy as np
from pathlib import Path

def print_gpu_info():
    """GPU 정보 출력"""
    print("\n🎮 GPU 정보")
    print("="*60)
    
    if not torch.cuda.is_available():
        print("❌ CUDA를 사용할 수 없습니다.")
        return False
    
    device_count = torch.cuda.device_count()
    print(f"GPU 개수: {device_count}개")
    
    for i in range(device_count):
        props = torch.cuda.get_device_properties(i)
        print(f"\nGPU {i}: {torch.cuda.get_device_name(i)}")
        print(f"  • 컴퓨트 능력: {props.major}.{props.minor}")
        print(f"  • 전체 메모리: {props.total_memory / (1024**3):.1f}GB")
        print(f"  • 멀티프로세서: {props.multi_processor_count}개")
        print(f"  • CUDA 코어: ~{props.multi_processor_count * 64}개 (추정)")
        
        # 현재 메모리 사용량
        allocated = torch.cuda.memory_allocated(i) / (1024**3)
        reserved = torch.cuda.memory_reserved(i) / (1024**3)
        print(f"  • 할당된 메모리: {allocated:.1f}GB")
        print(f"  • 예약된 메모리: {reserved:.1f}GB")
        print(f"  • 사용 가능: {(props.total_memory / (1024**3) - allocated):.1f}GB")
    
    print(f"\nCUDA 버전: {torch.version.cuda}")
    print(f"cuDNN 버전: {torch.backends.cudnn.version()}")
    print(f"PyTorch 버전: {torch.__version__}")
    
    return True

def test_gpu_performance():
    """GPU 성능 테스트"""
    print("\n⚡ GPU 성능 테스트")
    print("="*60)
    
    device = torch.device('cuda')
    
    # 테스트 크기들
    test_sizes = [
        (1000, 1000),
        (5000, 5000),
        (10000, 10000)
    ]
    
    for size in test_sizes:
        print(f"\n행렬 크기: {size[0]}x{size[1]}")
        
        # CPU 테스트
        cpu_matrix1 = torch.randn(size)
        cpu_matrix2 = torch.randn(size)
        
        start = time.time()
        cpu_result = torch.matmul(cpu_matrix1, cpu_matrix2)
        cpu_time = time.time() - start
        
        # GPU 테스트
        gpu_matrix1 = cpu_matrix1.to(device)
        gpu_matrix2 = cpu_matrix2.to(device)
        
        # 워밍업
        _ = torch.matmul(gpu_matrix1, gpu_matrix2)
        torch.cuda.synchronize()
        
        start = time.time()
        gpu_result = torch.matmul(gpu_matrix1, gpu_matrix2)
        torch.cuda.synchronize()
        gpu_time = time.time() - start
        
        speedup = cpu_time / gpu_time
        
        print(f"  • CPU 시간: {cpu_time:.4f}초")
        print(f"  • GPU 시간: {gpu_time:.4f}초")
        print(f"  • 속도 향상: {speedup:.1f}배")
        
        # 메모리 정리
        del cpu_matrix1, cpu_matrix2, cpu_result
        del gpu_matrix1, gpu_matrix2, gpu_result
        torch.cuda.empty_cache()

def test_ocr_engines():
    """OCR 엔진 GPU 지원 테스트"""
    print("\n🔤 OCR 엔진 GPU 지원 확인")
    print("="*60)
    
    # EasyOCR
    try:
        import easyocr
        print("\n✅ EasyOCR 설치됨")
        print("   GPU 지원: 예")
    except ImportError:
        print("\n❌ EasyOCR 미설치")
        print("   설치: pip install easyocr")
    
    # PaddleOCR
    try:
        import paddleocr
        print("\n✅ PaddleOCR 설치됨")
        print("   GPU 지원: 예")
    except ImportError:
        print("\n❌ PaddleOCR 미설치")
        print("   설치: pip install paddlepaddle paddleocr")
    
    # Tesseract
    try:
        import pytesseract
        print("\n✅ Tesseract 설치됨")
        print("   GPU 지원: 아니오 (CPU 전용)")
    except ImportError:
        print("\n❌ Tesseract 미설치")
        print("   설치: pip install pytesseract")
    
    # TrOCR
    try:
        import transformers
        print("\n✅ Transformers 설치됨 (TrOCR)")
        print("   GPU 지원: 예")
    except ImportError:
        print("\n❌ Transformers 미설치")
        print("   설치: pip install transformers")

def benchmark_image_processing():
    """이미지 처리 성능 벤치마크"""
    print("\n📸 이미지 처리 성능 테스트")
    print("="*60)
    
    try:
        import cv2
        import numpy as np
        from PIL import Image
        
        # 테스트 이미지 생성
        sizes = [(1920, 1080), (3840, 2160), (7680, 4320)]  # HD, 4K, 8K
        
        for width, height in sizes:
            print(f"\n이미지 크기: {width}x{height}")
            
            # 랜덤 이미지 생성
            img_array = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
            
            # OpenCV 처리 시간
            start = time.time()
            gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            _, binary = cv2.threshold(blurred, 127, 255, cv2.THRESH_BINARY)
            cv_time = time.time() - start
            
            print(f"  • 처리 시간: {cv_time:.4f}초")
            print(f"  • 처리 속도: {width*height/cv_time/1e6:.1f} 메가픽셀/초")
            
    except ImportError:
        print("OpenCV가 설치되지 않았습니다.")

def optimize_tips():
    """최적화 팁"""
    print("\n💡 GPU 최적화 팁")
    print("="*60)
    
    if torch.cuda.is_available():
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        
        print(f"\n현재 GPU 메모리: {gpu_memory:.1f}GB")
        
        if gpu_memory < 4:
            print("\n⚠️  메모리가 부족합니다. 다음을 권장합니다:")
            print("  • 배치 크기를 2-3으로 설정")
            print("  • EasyOCR 사용 (메모리 효율적)")
            print("  • --workers 1 사용")
        elif gpu_memory < 8:
            print("\n✅ 적당한 메모리입니다. 다음을 권장합니다:")
            print("  • 배치 크기를 5-8로 설정")
            print("  • PaddleOCR 또는 EasyOCR 사용")
            print("  • --workers 2 사용")
        else:
            print("\n🎉 충분한 메모리입니다. 다음을 권장합니다:")
            print("  • 배치 크기를 10-20으로 설정")
            print("  • PaddleOCR 사용 (가장 빠름)")
            print("  • --workers 4 사용")
        
        print("\n추가 최적화:")
        print("  • 고해상도 PDF는 --dpi 150 사용")
        print("  • 대량 처리 시 --no-cache 옵션 고려")
        print("  • 메모리 부족 시 주기적으로 재시작")

def main():
    print("="*60)
    print("🔬 GPU 테스트 및 최적화 확인")
    print("="*60)
    
    # GPU 정보
    if not print_gpu_info():
        print("\n💡 GPU를 사용하려면:")
        print("1. NVIDIA GPU가 필요합니다")
        print("2. CUDA 드라이버를 설치하세요")
        print("3. PyTorch GPU 버전을 설치하세요:")
        print("   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118")
        sys.exit(1)
    
    # 성능 테스트
    try:
        test_gpu_performance()
    except Exception as e:
        print(f"\n⚠️  성능 테스트 실패: {e}")
    
    # OCR 엔진 확인
    test_ocr_engines()
    
    # 이미지 처리 벤치마크
    benchmark_image_processing()
    
    # 최적화 팁
    optimize_tips()
    
    print("\n" + "="*60)
    print("✅ 테스트 완료!")
    print("\n🚀 GPU 가속 실행:")
    print("   python run_gpu.py documents/")
    print("\n📊 일반 실행:")
    print("   python main.py documents/ --gpu --extract-all")
    print("="*60)

if __name__ == "__main__":
    main()