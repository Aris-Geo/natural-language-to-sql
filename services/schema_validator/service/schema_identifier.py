from sqlalchemy import create_engine, inspect, text
from typing import Dict, List, Any
import logging

from schemas import DatabaseConnection, DatabaseSchema, TableInfo, ColumnInfo, ForeignKey

logger = logging.getLogger(__name__)

class SchemaIntrospector:
    def __init__(self):
        self.connections = {} # cache the open connections
    
    async def get_schema(self, db_config: DatabaseConnection, include_sample_data: bool = True, max_sample_rows: int = 3) -> DatabaseSchema:
        connection_string = db_config.get_connection_string()
        
        try:
            engine = create_engine(connection_string)
            inspector = inspect(engine)
            
            # retrieve the very basic db information
            with engine.connect() as conn:
                db_name = conn.execute(text("SELECT current_database()")).scalar()
            
            tables = {}
            total_columns = 0
            relationships = []
            
            # iterate through each table and identify its schema
            for table_name in inspector.get_table_names():
                table_info = await self._get_table_info(
                    inspector, engine, table_name, include_sample_data, max_sample_rows
                )
                tables[table_name] = table_info
                total_columns += len(table_info.columns)
                
                # collect all the table connections (foreign keys)
                # we are following the pattern table x linked to table y via key = z
                for fk in table_info.foreign_keys:
                    relationships.append({
                        "from_table": table_name,
                        "from_column": fk.column,
                        "to_table": fk.references_table,
                        "to_column": fk.references_column
                    })
            
            engine.dispose()
            
            return DatabaseSchema(
                database_name=db_name,
                tables=tables,
                total_tables=len(tables),
                total_columns=total_columns,
                relationships=relationships
            )
            
        except Exception as e:
            logger.error(f"Schema introspection failed: {str(e)}")
            raise
    
    async def _get_table_info(self, inspector, engine, table_name: str, include_sample_data: bool, max_sample_rows: int) -> TableInfo:
        
        # iterate through every column and inspect its ddata
        columns = []
        for col in inspector.get_columns(table_name):
            columns.append(ColumnInfo(
                name=col["name"],
                type=str(col["type"]),
                nullable=col.get("nullable", True),
                primary_key=col.get("primary_key", False),
                default=str(col.get("default")) if col.get("default") is not None else None
            ))
        
        # pick the priomarey keys per table
        pk_constraint = inspector.get_pk_constraint(table_name)
        primary_keys = pk_constraint.get("constrained_columns", [])
        
        foreign_keys = []
        for fk in inspector.get_foreign_keys(table_name):
            if fk["constrained_columns"] and fk["referred_columns"]:
                foreign_keys.append(ForeignKey(
                    column=fk["constrained_columns"][0],
                    references_table=fk["referred_table"],
                    references_column=fk["referred_columns"][0]
                ))
        
        sample_data = []
        row_count = None
        
        if include_sample_data:
            try:
                with engine.connect() as conn:
                    result = conn.execute(text(f'SELECT * FROM "{table_name}" LIMIT {max_sample_rows}'))
                    for row in result:
                        row_dict = {col: (str(val) if val is not None else None) for col, val in zip(result.keys(), row)}
                        sample_data.append(row_dict)
                    
                    count_result = conn.execute(text(f'SELECT COUNT(*) FROM "{table_name}"'))
                    row_count = count_result.scalar()
                    
            except Exception as e:
                logger.warning(f"Could not get sample data for {table_name}: {str(e)}")
        
        return TableInfo(
            columns=columns,
            foreign_keys=foreign_keys,
            primary_keys=primary_keys,
            sample_data=sample_data,
            row_count=row_count
        )