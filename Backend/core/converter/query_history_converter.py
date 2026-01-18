from core.model.query_models import QueryHistoryCore, QueryHistoryDO, QueryHistoryVO

class QueryHistoryConverter:
    """
    Handles the conversion between Core, DO, and VO models for query history.
    Since the model parameters are standardized, conversion largely involves
    passing the data between model types.
    """

    @staticmethod
    def core_to_do(core: QueryHistoryCore) -> QueryHistoryDO:
        """
        Converts the Core Model (business logic) to the Data Object Model (for DB insert).
        """
        if core is None:
            return None
        
        return QueryHistoryDO(
            question=core.question,
            generated_sql=core.generated_sql,
            intent_recognized=core.intent_recognized,
            operator=core.operator,
            status=core.status,
            error_message=core.error_message,
            table_name=core.table_name,
            ddl_context=core.ddl_context
        )

    @staticmethod
    def do_to_core(db_object: QueryHistoryDO) -> QueryHistoryCore:
        """
        Converts the Data Object Model (retrieved from DB) to the Core Model.
        """
        if db_object is None:
            return None
        
        return QueryHistoryCore(
            id=db_object.id,
            gmt_create=db_object.gmt_create,
            question=db_object.question,
            generated_sql=db_object.generated_sql,
            intent_recognized=db_object.intent_recognized,
            operator=db_object.operator,
            status=db_object.status,
            error_message=db_object.error_message,
            table_name=db_object.table_name,
            ddl_context=db_object.ddl_context
        )

    @staticmethod
    def core_to_vo(core_object: QueryHistoryCore) -> QueryHistoryVO:
        """
        Converts the Data Object Model (retrieved from DB) to the Value Object Model (for API output).
        """
        if core_object is None:
            return None
        
        return QueryHistoryVO(
            id=core_object.id,
            gmt_create=core_object.gmt_create,
            question=core_object.question,
            generated_sql=core_object.generated_sql,
            intent_recognized=core_object.intent_recognized,
            operator=core_object.operator,
            status=core_object.status,
            error_message=core_object.error_message,
            table_name=core_object.table_name,
            ddl_context=core_object.ddl_context
        )