import time
import logging
from typing import Tuple, Optional

from service.ollama_client import OllamaClient
from schemas import DatabaseSchema
from config import settings

logger = logging.getLogger(__name__)

# generates an sql query based on the incoming text (natural language), 
# the class returns a tuple of the sql query, a logical explanation of the generated query and the time it took to generate it

class TextToSQLService:
    def __init__(self):
        self.ollama_client = OllamaClient()
    
    async def generate_sql(self, question: str, schema: DatabaseSchema, include_explanation: bool = False) -> Tuple[Optional[str], Optional[str], float]:
        start_time = time.time()
        
        try:
            prompt = self._build_prompt(question, schema, include_explanation)
            
            response = await self.ollama_client.generate(prompt)
            
            sql_query, explanation = self._parse_response(response, include_explanation)
            
            generation_time = time.time() - start_time
            
            return sql_query, explanation, generation_time
            
        except Exception as e:
            generation_time = time.time() - start_time
            logger.error(f"SQL generation failed: {str(e)}")
            raise Exception(f"Failed to generate SQL: {str(e)}")
    
    def _build_prompt(self, question: str, schema: DatabaseSchema, include_explanation: bool) -> str:
        schema_context = self._build_schema_context(schema)
        
        # instruct the llm
        explanation_instruction = ""
        if include_explanation:
            explanation_instruction = "\nAlso provide a brief explanation of what the query does."
        
        prompt = f"""You are an SQL expert. Convert the incoming text to an POSTGRES SQL query following the given rules.

Database Schema:
{schema_context}

Rules:
1. Generate ONLY valid PostgreSQL SELECT queries
2. Use proper table aliases for readability
3. Include appropriate WHERE clauses for filtering
4. Use JOINs when accessing multiple tables
5. Use aggregate functions (COUNT, SUM, AVG) when appropriate
6. Always end queries with semicolon
7. Do not include any explanatory text unless requested
8. Use CTEs ONLY when required

Question: {question}

Generate the SQL query:{explanation_instruction}

SQL:"""

        return prompt
    
    def _build_schema_context(self, schema: DatabaseSchema) -> str:
        context = f"Database: {schema.database_name}\n\n"
        
        for table_name, table_info in schema.tables.items():
            context += f"Table: {table_name}\n"
            
           
            columns = table_info.get("columns", [])
            for col in columns[:10]:  # configure the column limit based on the context tokens used
                col_info = f"  - {col['name']}: {col['type']}"
                if col.get('primary_key'):
                    col_info += " (PK)"
                context += col_info + "\n"
            
            foreign_keys = table_info.get("foreign_keys", [])
            if foreign_keys:
                context += "  Foreign Keys:\n"
                for fk in foreign_keys[:5]:
                    context += f"    - {fk['column']} -> {fk['references_table']}.{fk['references_column']}\n"
            
            if settings.include_sample_data and table_info.get("sample_data"):
                context += "  Sample Data:\n"
                for i, sample in enumerate(table_info["sample_data"][:2]):
                    context += f"    {sample}\n"
            
            context += "\n"
        
        if schema.relationships:
            context += "Key Relationships:\n"
            for rel in schema.relationships[:5]:
                context += f"  {rel['from_table']}.{rel['from_column']} -> {rel['to_table']}.{rel['to_column']}\n"
        
        if len(context) > settings.max_context_length:
            context = context[:settings.max_context_length] + "\n... (truncated)"
        
        return context
    
    def _parse_response(self, response: str, include_explanation: bool) -> Tuple[Optional[str], Optional[str]]:

        response = response.strip()
        
        sql_query = None
        explanation = None
        
        lines = response.split('\n')
        sql_lines = []
        explanation_lines = []
        
        in_sql = False
        for line in lines:
            line = line.strip()
            
            if not line:
                continue
            
            if any(keyword in line.upper() for keyword in ['SELECT', 'FROM', 'WHERE', 'JOIN', 'GROUP BY', 'ORDER BY']): # ensure this is sql like
                in_sql = True
                sql_lines.append(line)
            elif in_sql and line.endswith(';'):
                sql_lines.append(line)
                break
            elif in_sql:
                sql_lines.append(line)
            elif include_explanation and not in_sql:
                explanation_lines.append(line)
        
        if sql_lines:
            sql_query = ' '.join(sql_lines)
            if not sql_query.endswith(';'):
                sql_query += ';'
        
        if include_explanation and explanation_lines:
            explanation = ' '.join(explanation_lines)
        
        return sql_query, explanation
    
    async def check_service_health(self) -> dict:
        return await self.ollama_client.check_model_status()