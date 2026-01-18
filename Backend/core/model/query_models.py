from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from core.model.models import StatusEnum, ErrorContext

# --- A. Data Object (DO) Model ---
class QueryHistoryDO(BaseModel):
    """
    Data Object Model: Directly represents the structure of the row in the
    'query_history' database table.
    """
    id: Optional[int] = Field(None, description="Primary key of the database record.")
    question: str
    generated_sql: Optional[str]
    intent_recognized: bool
    operator: Optional[str]
    status: str # Stored as string in DB, corresponds to StatusEnum
    error_message: Optional[str]
    gmt_create: Optional[datetime] = Field(None, description="Database insertion time.")
    table_name: Optional[str] = None 
    ddl_context: Optional[str] = None


# --- B. Core Model ---
class QueryHistoryCore(BaseModel):
    """
    Core Business Model: Represents the business entity. It encapsulates the data
    and logic used within the backend system.
    """
    id: Optional[int] = Field(None, description="Primary key of the database record.")
    question: str = Field(..., description="The user's natural language question.")
    generated_sql: Optional[str] = Field(None, description="The output (SQL query or error message).")
    intent_recognized: bool = Field(..., description="True if Query Intent Recognizer predicted 1.")
    operator: Optional[str] = Field(None, description="The optional operator from the API request.")
    status: str = Field(..., description="The status of the request (SUCCESS/FAILED).")
    error_message: Optional[str] = Field(None, description="Only set if query_status is FAILED.")
    gmt_create: Optional[datetime] = Field(None, description="Database insertion time.")
    table_name: Optional[str] = None 
    ddl_context: Optional[str] = None


# --- C. Value Object (VO) Model ---
class QueryHistoryVO(BaseModel):
    """
    Value Object Model: Represents the data structure exposed to the external
    world (e.g., in an API response for fetching history).
    """
    id: Optional[int] = Field(None, description="Primary key of the database record.")
    question: str = Field(..., description="The user's natural language question.")
    generated_sql: Optional[str] = Field(None, description="The output (SQL query or error message).")
    intent_recognized: bool = Field(..., description="True if Query Intent Recognizer predicted 1.")
    operator: Optional[str] = Field(None, description="The optional operator from the API request.")
    status: str = Field(..., description="The status of the request (SUCCESS/FAILED).")
    error_message: Optional[str] = Field(None, description="Only set if query_status is FAILED.")
    gmt_create: Optional[datetime] = Field(None, description="Database insertion time.")
    table_name: Optional[str] = None 
    ddl_context: Optional[str] = None

    class Config:
        """
        Configuration for Pydantic model, used primarily for documentation.
        """
        schema_extra = {
            "example": {
                "id": 101,
                "question": "How many employees are in the finance department?",
                "generated_sql": "SELECT COUNT(*) FROM employees WHERE dept = 'Finance'",
                "intent_recognized": True,
                "operator": "COUNT",
                "status": "SUCCESS",
                "context_error": None,
                "gmt_create": "2025-12-13T18:30:00"
            }
        }


# --- Request Model ---
class QueryRequest(BaseModel):
    """
    Model for the incoming request body for the Text-to-SQL endpoint.
    """
    question: str = Field(..., description="The natural language question to be converted to SQL.")
    need_predict_intent: bool = Field(True, description="Flag to determine if the query intent recognizer should be run before generating SQL.")
    operator: Optional[str] = Field(None, description="An optional parameter indicating a specific database operator or context (e.g., 'SUM', 'COUNT').")
    table_name: Optional[str] = None 
    ddl_context: Optional[str] = None

    class Config:
        # Example schema for the automatically generated documentation
        schema_extra = {
            "example": {
                "question": "What is the name of the youngest employee?",
                "need_predict_intent": True,
                "operator": "tester",
                "table_name": "department",
                "ddl_context": "CREATE TABLE department (id INT, name VARCHAR, jobscope VARCHAR ....)"
            }
        }


# --- Response Model ---
class QueryResponse(BaseModel):
    """
    Model for the outgoing response body from the Text-to-SQL endpoint.
    """
    status: StatusEnum = Field(..., description="The overall status of the API request (SUCCESS or FAILED).")
    result_data: Optional[str] = Field(None, description="The output data. On success, this is the generated SQL query or the result of executing the query. On failure, this may be None.")
    error_context: Optional[ErrorContext] = Field(None, description="Detailed error information, only present if status is FAILED.")

    class Config:
        # Example schema for the automatically generated documentation
        schema_extra = {
            "example": {
                "status": "SUCCESS",
                "result_data": "SELECT name FROM employees ORDER BY age ASC LIMIT 1",
                "error_context": None
            }
        }