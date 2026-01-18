import mysql.connector
from .db_config import MYSQL_CONFIG 


class DBManager:
    """
    Low-level class to manage MySQL connections and execute generic SQL commands.
    Does NOT interact with business models (DO, Core, VO).
    """

    def __init__(self):
        # Database connection parameters
        self.config = MYSQL_CONFIG

    def _get_connection(self):
        """Establishes a connection to the MySQL database."""
        try:
            conn = mysql.connector.connect(**self.config)
            return conn
        except mysql.connector.Error as err:
            print(f"Error connecting to MySQL: {err}")
            raise err

    def execute_and_fetch(self, sql: str, params: tuple = None) -> list[dict]:
        """
        Executes a SELECT query and returns results as a list of dictionaries.
        """
        conn = None
        try:
            conn = self._get_connection()
            # Use dictionary=True to return results as dictionaries (column_name: value)
            cursor = conn.cursor(dictionary=True) 
            cursor.execute(sql, params or ())
            results = cursor.fetchall()
            cursor.close()
            return results
            
        except mysql.connector.Error as err:
            print(f"Error executing fetch query: {err}")
            raise err
            
        finally:
            if conn and conn.is_connected():
                conn.close()

    def execute_and_commit(self, sql: str, params: tuple = None) -> int:
        """
        Executes an INSERT, UPDATE, or DELETE query and returns the last row ID (for INSERT).
        """
        conn = None
        last_row_id = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute(sql, params or ())
            conn.commit()
            last_row_id = cursor.lastrowid
            cursor.close()
            return last_row_id

        except mysql.connector.Error as err:
            print(f"Error executing commit query: {err}")
            conn.rollback()
            raise err
            
        finally:
            if conn and conn.is_connected():
                conn.close()