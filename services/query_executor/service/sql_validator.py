import re
import logging
from typing import List, Tuple
from schemas import ValidationResult
from config import settings

logger = logging.getLogger(__name__)

class SQLValidator:
    
    def __init__(self):
        self.allowed_keywords = [kw.upper() for kw in settings.allowed_sql_keywords]
        self.blocked_keywords = [kw.upper() for kw in settings.blocked_sql_keywords]
    
    def validate_query(self, sql_query: str) -> ValidationResult:

        errors = []
        warnings = []
        
        cleaned_query = self._clean_query(sql_query)
        
        blocked_found = self._check_blocked_keywords(cleaned_query)
        if blocked_found:
            errors.extend([f"Blocked keyword found: {kw}" for kw in blocked_found])
        
        if not self._check_allowed_keywords(cleaned_query):
            errors.append("Query must start with allowed keywords: " + ", ".join(self.allowed_keywords))
        
        injection_warnings = self._check_sql_injection_patterns(cleaned_query)
        warnings.extend(injection_warnings)
        
        dangerous_patterns = self._check_dangerous_patterns(cleaned_query)
        if dangerous_patterns:
            errors.extend([f"Dangerous pattern detected: {pattern}" for pattern in dangerous_patterns])
        
        safety_warnings = self._check_safety_patterns(cleaned_query)
        warnings.extend(safety_warnings)
        
        is_valid = len(errors) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            sanitized_query=cleaned_query if is_valid else None
        )
    
    def _clean_query(self, sql_query: str) -> str:
        cleaned = re.sub(r'\s+', ' ', sql_query.strip())
        
        cleaned = re.sub(r'--.*?$', '', cleaned, flags=re.MULTILINE)
        cleaned = re.sub(r'/\*.*?\*/', '', cleaned, flags=re.DOTALL)
        
        return cleaned.strip()
    
    def _check_blocked_keywords(self, sql_query: str) -> List[str]:
        query_upper = sql_query.upper()
        found_blocked = []
        
        for keyword in self.blocked_keywords:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, query_upper):
                found_blocked.append(keyword)
        
        return found_blocked
    
    def _check_allowed_keywords(self, sql_query: str) -> bool:
        query_upper = sql_query.upper().strip()
        
        for keyword in self.allowed_keywords:
            if query_upper.startswith(keyword):
                return True
        
        return False
    
    def _check_sql_injection_patterns(self, sql_query: str) -> List[str]:
        warnings = []
        query_upper = sql_query.upper()
        
        injection_patterns = [
            r"UNION\s+SELECT",
            r"OR\s+1\s*=\s*1",
            r"AND\s+1\s*=\s*1",
            r"'\s*OR\s+'",
            r";\s*DROP",
            r"EXEC\s*\(",
            r"EXECUTE\s*\(",
        ]
        
        for pattern in injection_patterns:
            if re.search(pattern, query_upper):
                warnings.append(f"Potential SQL injection pattern: {pattern}")
        
        return warnings
    
    def _check_dangerous_patterns(self, sql_query: str) -> List[str]:
        dangerous = []
        query_upper = sql_query.upper()
        
        dangerous_patterns = [
            (r'\bXP_CMDSHELL\b', "xp_cmdshell usage"),
            (r'\bSP_EXECUTESQL\b', "sp_executesql usage"),
            (r'INTO\s+OUTFILE', "file writing"),
            (r'LOAD_FILE\s*\(', "file reading"),
            (r'DUMPFILE', "file dumping"),
            (r'INFORMATION_SCHEMA\.\w+', "information schema access"),
            (r'PG_SLEEP\s*\(', "sleep injection"),
            (r'WAITFOR\s+DELAY', "delay injection"),
        ]
        
        for pattern, description in dangerous_patterns:
            if re.search(pattern, query_upper):
                dangerous.append(description)
        
        return dangerous
    
    def _check_safety_patterns(self, sql_query: str) -> List[str]:
        warnings = []
        query_upper = sql_query.upper()
        
        safety_patterns = [
            (r'SELECT\s+\*\s+FROM\s+\w+\s*;?\s*$', "SELECT * without WHERE clause - might return large dataset"),
            (r'LIMIT\s+\d{4,}', "Very high LIMIT - might return large dataset"),
            (r'JOIN\s+\w+\s+ON\s+1\s*=\s*1', "Cartesian join detected"),
        ]
        
        for pattern, description in safety_patterns:
            if re.search(pattern, query_upper):
                warnings.append(description)
        
        return warnings
    
    def sanitize_query(self, sql_query: str) -> str:
        cleaned = self._clean_query(sql_query)
        
        if cleaned.upper().startswith('SELECT') and 'LIMIT' not in cleaned.upper():
            if cleaned.endswith(';'):
                cleaned = cleaned[:-1]
            
            cleaned += f' LIMIT {settings.max_rows};'
        
        return cleaned