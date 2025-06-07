#!/usr/bin/env python3
"""
JSON 직렬화 오류를 수정하는 패치 파일
main.py의 save_results 메서드를 수정합니다.
"""

import os
import shutil
from pathlib import Path

def apply_json_fix():
    """JSON 직렬화 수정 적용"""
    
    print("JSON 직렬화 오류 수정 중...")
    
    # 1. utils 디렉토리 생성
    utils_dir = Path("utils")
    utils_dir.mkdir(exist_ok=True)
    
    # __init__.py 생성
    init_file = utils_dir / "__init__.py"
    if not init_file.exists():
        init_file.write_text("")
    
    # 2. main.py 백업
    main_file = Path("main.py")
    backup_file = Path("main_backup_json.py")
    
    if main_file.exists() and not backup_file.exists():
        shutil.copy(main_file, backup_file)
        print(f"백업 생성: {backup_file}")
    
    # 3. main.py 수정
    if main_file.exists():
        content = main_file.read_text(encoding='utf-8')
        
        # import 추가
        import_section = """import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union

import numpy as np
import pandas as pd
from tqdm import tqdm

# JSON 직렬화 헬퍼 추가
try:
    from utils.json_helper import save_json, convert_to_serializable
except ImportError:
    def save_json(data, filepath, **kwargs):
        import json
        import numpy as np
        
        def convert_np(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {k: convert_np(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_np(item) for item in obj]
            return obj
        
        converted_data = convert_np(data)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(converted_data, f, ensure_ascii=False, indent=2)"""
        
        # import 섹션 교체
        if "import argparse" in content:
            # 기존 import 섹션 찾기
            import_end = content.find("\nfrom core.")
            if import_end > 0:
                content = import_section + "\n" + content[import_end:]
            else:
                content = import_section + "\n" + content.split("\n", 20)[-1]
        
        # save_results 메서드 수정
        save_results_start = content.find("def save_results(")
        if save_results_start > 0:
            # JSON 저장 부분 찾기
            json_save_pattern = "with open(json_path, 'w', encoding='utf-8') as f:"
            json_save_start = content.find(json_save_pattern, save_results_start)
            
            if json_save_start > 0:
                # json.dump 라인 찾기
                json_dump_start = content.find("json.dump(", json_save_start)
                json_dump_end = content.find("\n", json_dump_start)
                
                if json_dump_start > 0 and json_dump_end > 0:
                    # 새로운 코드로 교체
                    indent = " " * 16  # 적절한 들여쓰기
                    new_code = f"{indent}save_json(result, json_path)"
                    content = (content[:json_save_start] + 
                             f"{indent}# JSON 저장 (NumPy 타입 자동 변환)\n" +
                             f"{indent}save_json(result, json_path)\n" +
                             content[json_dump_end + 1:])
        
        # 파일 저장
        main_file.write_text(content, encoding='utf-8')
        print("✅ main.py 수정 완료")
        
    print("\n수정 완료! 다시 실행해보세요:")
    print("python main.py documents/ --ocr-engine paddleocr --detect-formulas --extract-terms")

if __name__ == "__main__":
    apply_json_fix()