from core.dal.database.db_manager import DBManager
from core.dal.database.db_config import HISTORY_TABLE_NAME 
from core.model.query_models import QueryHistoryDO



class QueryHistoryDAL:
    """
    Data Access Layer (DAL) specific to the query_history table.
    Interacts with QueryHistoryDO models and uses DBManager for execution.
    """

    def __init__(self, db_manager: DBManager):
        # Dependency Injection: The DAL depends on the generic DBManager
        self._db_manager = db_manager

    def _map_row_to_do(self, row: dict) -> QueryHistoryDO:
        """Helper to map a database dictionary row to a QueryHistoryDO model."""
        return QueryHistoryDO(
            id=row['id'],
            gmt_create=row['gmt_create'],
            question=row['question'],
            generated_sql=row['generated_sql'],
            # Ensure conversion of MySQL's BOOLEAN/TINYINT(1) to Python bool
            intent_recognized=bool(row['intent_recognized']),
            operator=row['operator'],
            status=row['status'],
            error_message=row['error_message'],
            table_name=row['table_name'],
            ddl_context=row['ddl_context']
        )
        
    def insert_query_history(self, history_do: QueryHistoryDO) -> int:
        """
        Inserts a QueryHistoryDO record into the database.
        Returns the ID of the new record.
        """
        sql = f"""
        INSERT INTO {HISTORY_TABLE_NAME} 
        (question, generated_sql, intent_recognized, operator, status, error_message, table_name, ddl_context)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        # Prepare the data tuple
        data = (
            history_do.question,
            history_do.generated_sql,
            history_do.intent_recognized,
            history_do.operator,
            history_do.status,
            history_do.error_message,
            history_do.table_name,
            history_do.ddl_context
        )
        
        # Use the DBManager to execute the commit operation
        return self._db_manager.execute_and_commit(sql, data)

    def queryHistory(self, operator: str) -> list[QueryHistoryDO]:
        """
        Retrieves the last 20 query history records filtered by a specific operator,
        ordered by timestamp descending.
        """
        sql = f"""
        SELECT id, gmt_create, question, generated_sql, intent_recognized, operator, status, error_message, table_name, ddl_context
        FROM {HISTORY_TABLE_NAME} 
        WHERE operator = %s AND status = 'SUCCESS'
        ORDER BY gmt_create DESC 
        LIMIT 20
        """
        
        # Use the DBManager to execute the fetch operation
        rows = self._db_manager.execute_and_fetch(sql, (operator,))
        
        # Convert dictionary rows to QueryHistoryDO models
        return [self._map_row_to_do(row) for row in rows]
    
    def delete_all(self, operator: str) -> bool:
        """
        Delete all records in the query history table with a specific operator.
        """
        sql = f"""
        DELETE FROM {HISTORY_TABLE_NAME} WHERE operator = %s
        """
        
        # Use the DBManager to execute the delete operation
        result = self._db_manager.execute_and_commit(sql, (operator,))

        # Return
        return result

