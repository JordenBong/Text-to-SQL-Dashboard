import core.ai_model.text_to_sql_system as text_to_sql_system 
from core.service.sql_manager.query_history_repository import QueryHistoryRepository
from core.model.models import StatusEnum, ErrorContext
from core.model.query_models import QueryHistoryCore, QueryRequest, QueryResponse
from typing import List

WARNING_MESSAGE = "Please ask something related to query data from database."

class QueryService:
    """
    Service Layer: Orchestrates the Text-to-SQL process, handles business logic, 
    and manages history persistence.
    """
    def __init__(self, tts_system: text_to_sql_system.TextToSQLSystem, history_repo: QueryHistoryRepository):
        self._tts_system = tts_system
        self._history_repo = history_repo

    def process_and_generate_sql(self, request: QueryRequest) -> QueryResponse:
        """
        Processes the user question, generates SQL, saves history, and returns the API response.
        """
        # Initialize Core model fields from request
        history_core = QueryHistoryCore(
            question=request.question,
            operator=request.operator,
            intent_recognized=False,  # Will be updated by generate_sql
            generated_sql=None,
            status=StatusEnum.FAILED, # Default to FAILED, update on SUCCESS
            error_message=None,
            table_name=request.table_name,
            ddl_context=request.ddl_context
        )
        
        try:
            # 1. Generate SQL (Intent recognition is handled inside this call)
            # The result is either the SQL query or a non-database related message.
            sql_or_response = self._tts_system.generate_sql(
                question=request.question,
                needPredictIntent=request.need_predict_intent,
                ddl_context=request.ddl_context
            )

            # Check if the response is warning message 
            if sql_or_response == WARNING_MESSAGE:
                response = QueryResponse(
                    status=StatusEnum.FAILED,
                    result_data=sql_or_response,
                    error_context=ErrorContext(
                        error_message="Not Database-Related Questions",
                        error_type="ILLEGAL_QUESTION",
                        suggested_action="Please rephrase the question."
                    )
                )

                history_core.status = StatusEnum.FAILED
                history_core.error_message = "Not Database-Related Questions"
                history_core.generated_sql = None
                history_core.intent_recognized = False
            else :
                # 2. Assume success for API response
                response = QueryResponse(
                    status=StatusEnum.SUCCESS,
                    result_data=sql_or_response,
                    error_context=None
                )
            
                # 3. Update History Core Model for success
                history_core.status = StatusEnum.SUCCESS
                history_core.generated_sql = sql_or_response
                history_core.intent_recognized = True
              
        except Exception as e:
            # 2. Handle failure for API response
            error_context = ErrorContext(
                error_message=str(e),
                error_type=type(e).__name__,
                suggested_action="Check the model paths or rephrase the question."
            )
            response = QueryResponse(
                status=StatusEnum.FAILED,
                result_data=None,
                error_context=error_context
            )
            
            # 3. Update History Core Model for failure
            history_core.status = StatusEnum.FAILED
            history_core.error_message = error_context.error_message
            # Hardcoded
            history_core.intent_recognized = False
            
        finally:
            # 4. Save history regardless of success/failure
            try:
                self._history_repo.save_query_history(history_core)
            except Exception as history_e:
                print(f"CRITICAL: Failed to save history: {history_e}")
                pass          
        return response

    def get_query_history(self, operator: str) -> List[QueryHistoryCore]:
        """
        Retrieves history using the repository.
        """
        return self._history_repo.get_history_by_operator(operator)
    
    def delete_all_history(self, operator: str) -> bool:
        """
        Deletes all history for a given operator. 
        """
        return self._history_repo.delete_all_history_by_operator(operator=operator)
    
    
