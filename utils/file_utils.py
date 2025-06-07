# utils/file_utils.py
"""
파일 유틸리티 함수들
"""

import json
import pickle
import shutil
from pathlib import Path
from typing import Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class FileUtils:
    """파일 관련 유틸리티"""
    
    @staticmethod
    def save_json(data: Any, filepath: Path, indent: int = 2):
        """JSON 파일 저장"""
        try:
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=indent)
                
            logger.debug(f"JSON 저장 완료: {filepath}")
            
        except Exception as e:
            logger.error(f"JSON 저장 실패: {filepath}, {e}")
            raise
    
    @staticmethod
    def load_json(filepath: Path) -> Any:
        """JSON 파일 로드"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            logger.error(f"JSON 로드 실패: {filepath}, {e}")
            raise
    
    @staticmethod
    def save_pickle(data: Any, filepath: Path):
        """Pickle 파일 저장"""
        try:
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            with open(filepath, 'wb') as f:
                pickle.dump(data, f)
                
            logger.debug(f"Pickle 저장 완료: {filepath}")
            
        except Exception as e:
            logger.error(f"Pickle 저장 실패: {filepath}, {e}")
            raise
    
    @staticmethod
    def load_pickle(filepath: Path) -> Any:
        """Pickle 파일 로드"""
        try:
            with open(filepath, 'rb') as f:
                return pickle.load(f)
                
        except Exception as e:
            logger.error(f"Pickle 로드 실패: {filepath}, {e}")
            raise
    
    @staticmethod
    def find_files(directory: Path, pattern: str) -> List[Path]:
        """디렉토리에서 파일 찾기"""
        try:
            return list(directory.glob(pattern))
        except Exception as e:
            logger.error(f"파일 검색 실패: {directory}, {pattern}, {e}")
            return []
    
    @staticmethod
    def copy_file(source: Path, destination: Path):
        """파일 복사"""
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            logger.debug(f"파일 복사 완료: {source} -> {destination}")
            
        except Exception as e:
            logger.error(f"파일 복사 실패: {source} -> {destination}, {e}")
            raise
    
    @staticmethod
    def move_file(source: Path, destination: Path):
        """파일 이동"""
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source), str(destination))
            logger.debug(f"파일 이동 완료: {source} -> {destination}")
            
        except Exception as e:
            logger.error(f"파일 이동 실패: {source} -> {destination}, {e}")
            raise
    
    @staticmethod
    def delete_file(filepath: Path):
        """파일 삭제"""
        try:
            if filepath.exists():
                filepath.unlink()
                logger.debug(f"파일 삭제 완료: {filepath}")
                
        except Exception as e:
            logger.error(f"파일 삭제 실패: {filepath}, {e}")
            raise
    
    @staticmethod
    def create_directory(directory: Path):
        """디렉토리 생성"""
        try:
            directory.mkdir(parents=True, exist_ok=True)
            logger.debug(f"디렉토리 생성 완료: {directory}")
            
        except Exception as e:
            logger.error(f"디렉토리 생성 실패: {directory}, {e}")
            raise
    
    @staticmethod
    def get_file_size(filepath: Path) -> int:
        """파일 크기 반환 (바이트)"""
        try:
            return filepath.stat().st_size
        except Exception:
            return 0
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """파일 크기 포맷팅"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f}{unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f}TB"