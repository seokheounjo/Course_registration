# -*- coding: utf-8 -*-
"""Result classes"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

@dataclass
class PageResult:
    """Page result"""
    page_num: int
    text: str = ""
    tables: List[Dict[str, Any]] = field(default_factory=list)
    formulas: List[Dict[str, Any]] = field(default_factory=list)
    financial_terms: List[Dict[str, Any]] = field(default_factory=list)
    layout_elements: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    korean_analysis: Dict[str, Any] = field(default_factory=dict)
    layout_regions: List[Dict[str, Any]] = field(default_factory=list)
    processing_time: float = 0.0

@dataclass
class AnalysisResult:
    """Analysis result"""
    document_id: str
    file_path: Path
    total_pages: int = 0
    pages: List[PageResult] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    summary: Dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0
    success: bool = True
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    warnings: List[str] = field(default_factory=list)
    output_files: Dict[str, Path] = field(default_factory=dict)
    
    @property
    def page_texts(self):
        return [page.text for page in self.pages]
    
    @property
    def tables(self):
        tables = []
        for page in self.pages:
            for table in page.tables:
                table_copy = table.copy()
                table_copy['page_num'] = page.page_num
                tables.append(table_copy)
        return tables
    
    @property
    def formulas(self):
        formulas = []
        for page in self.pages:
            for formula in page.formulas:
                formula_copy = formula.copy()
                formula_copy['page_num'] = page.page_num
                formulas.append(formula_copy)
        return formulas
    
    @property
    def financial_terms(self):
        terms = []
        for page in self.pages:
            for term in page.financial_terms:
                term_copy = term.copy()
                term_copy['page_num'] = page.page_num
                terms.append(term_copy)
        return terms
    
    @property
    def korean_texts(self):
        return [page.korean_analysis for page in self.pages if page.korean_analysis]
    
    def add_page_result(self, page_result):
        self.pages.append(page_result)
    
    def finalize(self):
        if not self.end_time:
            self.end_time = datetime.now()
        if self.start_time and self.end_time:
            self.processing_time = (self.end_time - self.start_time).total_seconds()
    
    def to_dict(self):
        def convert_value(obj):
            if isinstance(obj, Path):
                return str(obj)
            elif isinstance(obj, datetime):
                return obj.isoformat()
            elif hasattr(obj, 'to_dict'):
                return obj.to_dict()
            elif hasattr(obj, '__dict__'):
                result = {}
                for k, v in obj.__dict__.items():
                    if not k.startswith('_'):
                        result[k] = convert_value(v)
                return result
            elif isinstance(obj, dict):
                return {k: convert_value(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_value(item) for item in obj]
            else:
                return obj
        
        return convert_value({
            'document_id': self.document_id,
            'file_path': self.file_path,
            'total_pages': self.total_pages,
            'pages': self.pages,
            'metadata': self.metadata,
            'summary': self.summary,
            'processing_time': self.processing_time,
            'success': self.success,
            'error_message': self.error_message,
            'created_at': self.created_at,
            'warnings': self.warnings,
            'output_files': self.output_files
        })
    
    def save(self, output_dir):
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        json_path = output_dir / f"{self.document_id}_result.json"
        
        try:
            from utils.json_helper import save_json
            save_json(self.to_dict(), str(json_path))
        except:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, ensure_ascii=False, indent=2, default=str)
        
        return json_path
