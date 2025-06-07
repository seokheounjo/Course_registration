# -*- coding: utf-8 -*-
"""
JSON 직렬화 헬퍼
NumPy 타입 등 특수 타입 처리
"""

import json
import numpy as np
from datetime import datetime, date
from pathlib import Path
from typing import Any

def convert_to_serializable(obj: Any) -> Any:
    """객체를 JSON 직렬화 가능한 형태로 변환"""
    
    # NumPy 타입 처리
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.bool_):
        return bool(obj)
    
    # 날짜/시간 타입
    elif isinstance(obj, (datetime, date)):
        return obj.isoformat()
    
    # 경로 타입
    elif isinstance(obj, Path):
        return str(obj)
    
    # 바이트 타입
    elif isinstance(obj, bytes):
        return obj.decode('utf-8', errors='ignore')
    
    # 컬렉션 타입 재귀 처리
    elif isinstance(obj, dict):
        return {k: convert_to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_serializable(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_to_serializable(item) for item in obj)
    elif isinstance(obj, set):
        return list(convert_to_serializable(item) for item in obj)
    
    # 기타 타입
    else:
        return obj

def save_json(data: Any, filepath: str, **kwargs):
    """JSON 파일 저장 (NumPy 타입 자동 변환)"""
    converted_data = convert_to_serializable(data)
    
    default_kwargs = {
        'ensure_ascii': False,
        'indent': 2,
        'sort_keys': False
    }
    default_kwargs.update(kwargs)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(converted_data, f, **default_kwargs)

def load_json(filepath: str) -> Any:
    """JSON 파일 로드"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

class NumpyEncoder(json.JSONEncoder):
    """NumPy 타입을 처리하는 JSON Encoder"""
    
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif isinstance(obj, Path):
            return str(obj)
        elif isinstance(obj, bytes):
            return obj.decode('utf-8', errors='ignore')
        
        return json.JSONEncoder.default(self, obj)
