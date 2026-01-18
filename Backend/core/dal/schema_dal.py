from core.dal.database.db_manager import DBManager
from core.model.schema_models import SchemaDO
from typing import List, Optional
from core.dal.database.db_config import SCHEMA_TABLE_NAME 

class SchemaDAL:
    def __init__(self, db_manager: DBManager):
        self._db_manager = db_manager

    # --- C: Create ---
    def add_schema(self, table_name: str, ddl_context: str, operator: str) -> int:
        sql = f"""
        INSERT INTO {SCHEMA_TABLE_NAME} (table_name, ddl_context, operator)
        VALUES (%s, %s, %s)
        """
        data = (table_name, ddl_context, operator)
        return self._db_manager.execute_and_commit(sql, data)

    # --- R: Read (All) ---
    def get_all_schemas_by_operator(self, operator: str) -> List[SchemaDO]:
        # MODIFIED: Filter by operator
        sql = f"SELECT id, gmt_create, table_name, ddl_context, operator FROM {SCHEMA_TABLE_NAME} WHERE operator = %s ORDER BY gmt_create DESC"
        rows = self._db_manager.execute_and_fetch(sql, (operator,))
        return [SchemaDO.model_validate(row) for row in rows]

    # --- R: Read (Single by Name and Operator) ---
    def get_schema_by_name_and_operator(self, table_name: str, operator: str) -> Optional[SchemaDO]:
        # MODIFIED: Filter by BOTH table_name and operator
        sql = f"SELECT id, gmt_create, table_name, ddl_context, operator FROM {SCHEMA_TABLE_NAME} WHERE table_name = %s AND operator = %s"
        rows = self._db_manager.execute_and_fetch(sql, (table_name, operator))
        if rows:
            return SchemaDO.model_validate(rows[0])
        return None

    # --- U: Update ---
    def update_schema(self, table_name: str, new_ddl_context: str, operator: str) -> bool:
        # MODIFIED: Use operator in the WHERE clause
        sql = f"UPDATE {SCHEMA_TABLE_NAME} SET ddl_context = %s WHERE table_name = %s AND operator = %s"
        return self._db_manager.execute_and_commit(sql, (new_ddl_context, table_name, operator)) is not None

    # --- D: Delete ---
    def delete_schema(self, table_name: str, operator: str) -> bool:
        # MODIFIED: Use operator in the WHERE clause
        sql = f"DELETE FROM {SCHEMA_TABLE_NAME} WHERE table_name = %s AND operator = %s"
        return self._db_manager.execute_and_commit(sql, (table_name, operator)) is not None