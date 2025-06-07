# utils/formula_database_manager.py
"""
수식 데이터베이스 관리 모듈
수식 저장, 조회, 실행, 백업 등 관리
"""

import sqlite3
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import shutil
import hashlib

logger = logging.getLogger(__name__)

class FormulaDatabaseManager:
    """수식 데이터베이스 매니저"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 데이터베이스 초기화
        self._init_database()
        
    def _init_database(self):
        """데이터베이스 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 1. 수식 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS formulas (
                id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL,
                page_number INTEGER,
                formula_latex TEXT NOT NULL,
                formula_python TEXT NOT NULL,
                formula_image BLOB,
                variables TEXT,  -- JSON
                formula_type TEXT,
                confidence REAL,
                context TEXT,  -- JSON
                bbox TEXT,  -- JSON [x1, y1, x2, y2]
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES documents(id)
            )
        ''')
        
        # 2. 변수 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS formula_variables (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                formula_id TEXT NOT NULL,
                variable_name TEXT NOT NULL,
                variable_description TEXT,
                variable_type TEXT,
                default_value TEXT,
                constraints TEXT,  -- JSON
                FOREIGN KEY (formula_id) REFERENCES formulas(id),
                UNIQUE(formula_id, variable_name)
            )
        ''')
        
        # 3. 수식 실행 이력
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS formula_executions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                formula_id TEXT NOT NULL,
                inputs TEXT NOT NULL,  -- JSON
                result TEXT,
                success BOOLEAN,
                error_message TEXT,
                execution_time REAL,
                executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (formula_id) REFERENCES formulas(id)
            )
        ''')
        
        # 4. 문서 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                file_path TEXT,
                total_pages INTEGER,
                metadata TEXT,  -- JSON
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 5. 수식 관계 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS formula_dependencies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                formula_id TEXT NOT NULL,
                depends_on_formula_id TEXT NOT NULL,
                dependency_type TEXT,  -- 'uses', 'extends', 'related'
                FOREIGN KEY (formula_id) REFERENCES formulas(id),
                FOREIGN KEY (depends_on_formula_id) REFERENCES formulas(id),
                UNIQUE(formula_id, depends_on_formula_id)
            )
        ''')
        
        # 인덱스 생성
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_formulas_document ON formulas(document_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_formulas_type ON formulas(formula_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_variables_formula ON formula_variables(formula_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_executions_formula ON formula_executions(formula_id)')
        
        conn.commit()
        conn.close()
        
        logger.info(f"데이터베이스 초기화 완료: {self.db_path}")
    
    def save_document(self, document_id: str, filename: str, 
                     total_pages: int, metadata: Dict[str, Any]) -> bool:
        """문서 정보 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO documents 
                (id, filename, total_pages, metadata)
                VALUES (?, ?, ?, ?)
            ''', (
                document_id,
                filename,
                total_pages,
                json.dumps(metadata, ensure_ascii=False)
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"문서 저장 완료: {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"문서 저장 실패: {e}")
            return False
    
    def save_formula(self, formula_data: Dict[str, Any]) -> bool:
        """수식 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 수식 저장
            cursor.execute('''
                INSERT OR REPLACE INTO formulas
                (id, document_id, page_number, formula_latex, formula_python,
                 formula_image, variables, formula_type, confidence, context, bbox)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                formula_data['id'],
                formula_data['document_id'],
                formula_data.get('page_number', 0),
                formula_data['latex'],
                formula_data['python_code'],
                formula_data.get('image_data'),
                json.dumps(formula_data.get('variables', {}), ensure_ascii=False),
                formula_data.get('type', 'unknown'),
                formula_data.get('confidence', 0),
                json.dumps(formula_data.get('context', {}), ensure_ascii=False),
                json.dumps(formula_data.get('bbox', []), ensure_ascii=False)
            ))
            
            # 변수 정보 저장
            if 'variables' in formula_data:
                for var_name, var_info in formula_data['variables'].items():
                    if isinstance(var_info, dict):
                        cursor.execute('''
                            INSERT OR REPLACE INTO formula_variables
                            (formula_id, variable_name, variable_description, 
                             variable_type, default_value, constraints)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', (
                            formula_data['id'],
                            var_name,
                            var_info.get('description', ''),
                            var_info.get('type', 'float'),
                            var_info.get('default_value', ''),
                            json.dumps(var_info.get('constraints', {}), ensure_ascii=False)
                        ))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            logger.error(f"수식 저장 실패: {e}")
            return False
    
    def save_formulas_batch(self, formulas: List[Dict[str, Any]]) -> int:
        """여러 수식 일괄 저장"""
        saved_count = 0
        
        for formula in formulas:
            if self.save_formula(formula):
                saved_count += 1
        
        logger.info(f"총 {len(formulas)}개 중 {saved_count}개 수식 저장 완료")
        return saved_count
    
    def get_formula(self, formula_id: str) -> Optional[Dict[str, Any]]:
        """수식 조회"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM formulas WHERE id = ?
        ''', (formula_id,))
        
        row = cursor.fetchone()
        
        if row:
            formula = dict(row)
            
            # JSON 필드 파싱
            formula['variables'] = json.loads(formula['variables'])
            formula['context'] = json.loads(formula['context'])
            formula['bbox'] = json.loads(formula['bbox'])
            
            # 변수 상세 정보 조회
            cursor.execute('''
                SELECT * FROM formula_variables WHERE formula_id = ?
            ''', (formula_id,))
            
            variables_detail = {}
            for var_row in cursor.fetchall():
                var_data = dict(var_row)
                var_name = var_data['variable_name']
                variables_detail[var_name] = {
                    'description': var_data['variable_description'],
                    'type': var_data['variable_type'],
                    'default_value': var_data['default_value'],
                    'constraints': json.loads(var_data['constraints'])
                }
            
            if variables_detail:
                formula['variables_detail'] = variables_detail
            
            conn.close()
            return formula
        
        conn.close()
        return None
    
    def search_formulas(self, **kwargs) -> List[Dict[str, Any]]:
        """수식 검색"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 기본 쿼리
        query = "SELECT * FROM formulas WHERE 1=1"
        params = []
        
        # 검색 조건 추가
        if 'document_id' in kwargs:
            query += " AND document_id = ?"
            params.append(kwargs['document_id'])
        
        if 'formula_type' in kwargs:
            query += " AND formula_type = ?"
            params.append(kwargs['formula_type'])
        
        if 'min_confidence' in kwargs:
            query += " AND confidence >= ?"
            params.append(kwargs['min_confidence'])
        
        if 'latex_pattern' in kwargs:
            query += " AND formula_latex LIKE ?"
            params.append(f"%{kwargs['latex_pattern']}%")
        
        # 정렬
        query += " ORDER BY created_at DESC"
        
        cursor.execute(query, params)
        
        formulas = []
        for row in cursor.fetchall():
            formula = dict(row)
            formula['variables'] = json.loads(formula['variables'])
            formula['context'] = json.loads(formula['context'])
            formula['bbox'] = json.loads(formula['bbox'])
            formulas.append(formula)
        
        conn.close()
        return formulas
    
    def execute_formula(self, formula_id: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """수식 실행"""
        import time
        
        # 수식 조회
        formula = self.get_formula(formula_id)
        if not formula:
            return {
                'success': False,
                'error': f"수식을 찾을 수 없습니다: {formula_id}"
            }
        
        # 실행 시작
        start_time = time.time()
        result = {'formula_id': formula_id, 'inputs': inputs}
        
        try:
            # Python 코드 실행
            namespace = {'__builtins__': __builtins__}
            
            # 필요한 모듈 import
            exec("""
import numpy as np
from math import *
from decimal import Decimal, getcontext
getcontext().prec = 10
            """, namespace)
            
            # 함수 정의
            exec(formula['formula_python'], namespace)
            
            # 함수 찾기
            func_name = None
            for name, obj in namespace.items():
                if callable(obj) and not name.startswith('_'):
                    func_name = name
                    break
            
            if not func_name:
                raise ValueError("실행 가능한 함수를 찾을 수 없습니다")
            
            # 함수 실행
            func = namespace[func_name]
            output = func(**inputs)
            
            execution_time = time.time() - start_time
            
            result.update({
                'success': True,
                'result': float(output),
                'execution_time': execution_time
            })
            
        except Exception as e:
            execution_time = time.time() - start_time
            result.update({
                'success': False,
                'error': str(e),
                'execution_time': execution_time
            })
        
        # 실행 이력 저장
        self._save_execution_history(formula_id, inputs, result)
        
        return result
    
    def _save_execution_history(self, formula_id: str, inputs: Dict[str, Any], 
                              result: Dict[str, Any]):
        """실행 이력 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO formula_executions
                (formula_id, inputs, result, success, error_message, execution_time)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                formula_id,
                json.dumps(inputs, ensure_ascii=False),
                str(result.get('result', '')),
                result['success'],
                result.get('error', ''),
                result.get('execution_time', 0)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"실행 이력 저장 실패: {e}")
    
    def get_execution_history(self, formula_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """실행 이력 조회"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM formula_executions 
            WHERE formula_id = ?
            ORDER BY executed_at DESC
            LIMIT ?
        ''', (formula_id, limit))
        
        history = []
        for row in cursor.fetchall():
            record = dict(row)
            record['inputs'] = json.loads(record['inputs'])
            history.append(record)
        
        conn.close()
        return history
    
    def add_formula_dependency(self, formula_id: str, depends_on: str, 
                             dependency_type: str = 'uses') -> bool:
        """수식 의존성 추가"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR IGNORE INTO formula_dependencies
                (formula_id, depends_on_formula_id, dependency_type)
                VALUES (?, ?, ?)
            ''', (formula_id, depends_on, dependency_type))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            logger.error(f"의존성 추가 실패: {e}")
            return False
    
    def get_formula_dependencies(self, formula_id: str) -> List[Dict[str, Any]]:
        """수식 의존성 조회"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 이 수식이 의존하는 것들
        cursor.execute('''
            SELECT fd.*, f.formula_latex, f.formula_type
            FROM formula_dependencies fd
            JOIN formulas f ON fd.depends_on_formula_id = f.id
            WHERE fd.formula_id = ?
        ''', (formula_id,))
        
        dependencies = []
        for row in cursor.fetchall():
            dependencies.append(dict(row))
        
        conn.close()
        return dependencies
    
    def get_dependent_formulas(self, formula_id: str) -> List[Dict[str, Any]]:
        """이 수식에 의존하는 수식들 조회"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT fd.*, f.formula_latex, f.formula_type
            FROM formula_dependencies fd
            JOIN formulas f ON fd.formula_id = f.id
            WHERE fd.depends_on_formula_id = ?
        ''', (formula_id,))
        
        dependents = []
        for row in cursor.fetchall():
            dependents.append(dict(row))
        
        conn.close()
        return dependents
    
    def export_formulas(self, output_path: Path, document_id: Optional[str] = None):
        """수식 내보내기"""
        formulas = self.search_formulas(document_id=document_id) if document_id else self.search_formulas()
        
        export_data = {
            'export_date': datetime.now().isoformat(),
            'total_formulas': len(formulas),
            'formulas': formulas
        }
        
        # JSON으로 저장
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"수식 {len(formulas)}개를 {output_path}로 내보내기 완료")
    
    def import_formulas(self, import_path: Path) -> int:
        """수식 가져오기"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            formulas = import_data.get('formulas', [])
            imported_count = self.save_formulas_batch(formulas)
            
            logger.info(f"{imported_count}개 수식 가져오기 완료")
            return imported_count
            
        except Exception as e:
            logger.error(f"수식 가져오기 실패: {e}")
            return 0
    
    def backup_database(self, backup_dir: Path):
        """데이터베이스 백업"""
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = backup_dir / f"formula_db_backup_{timestamp}.db"
        
        shutil.copy2(self.db_path, backup_path)
        logger.info(f"데이터베이스 백업 완료: {backup_path}")
        
        return backup_path
    
    def get_statistics(self) -> Dict[str, Any]:
        """통계 정보 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # 총 수식 수
        cursor.execute("SELECT COUNT(*) FROM formulas")
        stats['total_formulas'] = cursor.fetchone()[0]
        
        # 문서 수
        cursor.execute("SELECT COUNT(*) FROM documents")
        stats['total_documents'] = cursor.fetchone()[0]
        
        # 타입별 수식 수
        cursor.execute('''
            SELECT formula_type, COUNT(*) 
            FROM formulas 
            GROUP BY formula_type
        ''')
        stats['formulas_by_type'] = dict(cursor.fetchall())
        
        # 평균 신뢰도
        cursor.execute("SELECT AVG(confidence) FROM formulas")
        stats['average_confidence'] = cursor.fetchone()[0] or 0
        
        # 실행 통계
        cursor.execute("SELECT COUNT(*) FROM formula_executions")
        stats['total_executions'] = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT COUNT(*) FROM formula_executions WHERE success = 1
        ''')
        stats['successful_executions'] = cursor.fetchone()[0]
        
        conn.close()
        return stats
    
    def validate_database(self) -> Dict[str, Any]:
        """데이터베이스 무결성 검증"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        issues = []
        
        # 1. 고아 수식 확인 (문서가 없는 수식)
        cursor.execute('''
            SELECT COUNT(*) FROM formulas f
            LEFT JOIN documents d ON f.document_id = d.id
            WHERE d.id IS NULL
        ''')
        orphan_formulas = cursor.fetchone()[0]
        if orphan_formulas > 0:
            issues.append(f"{orphan_formulas}개의 고아 수식 발견")
        
        # 2. 잘못된 의존성 확인
        cursor.execute('''
            SELECT COUNT(*) FROM formula_dependencies fd
            LEFT JOIN formulas f1 ON fd.formula_id = f1.id
            LEFT JOIN formulas f2 ON fd.depends_on_formula_id = f2.id
            WHERE f1.id IS NULL OR f2.id IS NULL
        ''')
        invalid_deps = cursor.fetchone()[0]
        if invalid_deps > 0:
            issues.append(f"{invalid_deps}개의 잘못된 의존성 발견")
        
        # 3. 변수 정보 확인
        cursor.execute('''
            SELECT COUNT(*) FROM formula_variables fv
            LEFT JOIN formulas f ON fv.formula_id = f.id
            WHERE f.id IS NULL
        ''')
        orphan_vars = cursor.fetchone()[0]
        if orphan_vars > 0:
            issues.append(f"{orphan_vars}개의 고아 변수 발견")
        
        conn.close()
        
        return {
            'valid': len(issues) == 0,
            'issues': issues
        }
    
    def cleanup_database(self):
        """데이터베이스 정리"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 고아 레코드 삭제
        cursor.execute('''
            DELETE FROM formula_variables 
            WHERE formula_id NOT IN (SELECT id FROM formulas)
        ''')
        
        cursor.execute('''
            DELETE FROM formula_executions
            WHERE formula_id NOT IN (SELECT id FROM formulas)
        ''')
        
        cursor.execute('''
            DELETE FROM formula_dependencies
            WHERE formula_id NOT IN (SELECT id FROM formulas)
            OR depends_on_formula_id NOT IN (SELECT id FROM formulas)
        ''')
        
        # VACUUM으로 공간 정리
        cursor.execute("VACUUM")
        
        conn.commit()
        conn.close()
        
        logger.info("데이터베이스 정리 완료")