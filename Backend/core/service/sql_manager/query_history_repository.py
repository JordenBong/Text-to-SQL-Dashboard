from core.dal.query_history_dal import QueryHistoryDAL
from core.converter.query_history_converter import QueryHistoryConverter
from core.model.query_models import QueryHistoryCore, QueryHistoryDO
from typing import List

class QueryHistoryRepository:
    """
    Repository Layer: Acts as an intermediary between the business logic (Service Layer) 
    and the data persistence mechanism (DAL). 
    
    It accepts and returns only Core models, handling all conversion to/from DO models.
    """

    def __init__(self, dal: QueryHistoryDAL, converter: QueryHistoryConverter):
        # Dependency Injection for DAL and Converter
        self._dal = dal
        self._converter = converter

    def save_query_history(self, core_model: QueryHistoryCore) -> QueryHistoryCore:
        """
        Accepts a Core model, converts it to DO, passes it to the DAL for insertion,
        and returns the resulting Core model (now with the generated ID and Timestamp).
        """
        # 1. Convert Core to DO
        history_do: QueryHistoryDO = self._converter.core_to_do(core_model)
        
        # 2. Pass DO to DAL for processing (insertion)
        generated_id: int = self._dal.insert_query_history(history_do)
        
        # 3. Retrieve the full DO object (or update the original Core model manually)
        # For simplicity and efficiency, nned update the original core_model with the new ID.
        core_model.id = generated_id
        
        # To get the timestamp, need to read the record back from the DB,
        # but for this flow, assume the ID is sufficient for immediate return.
        
        return core_model

    def get_history_by_operator(self, operator: str) -> List[QueryHistoryCore]:
        """
        Calls the DAL to retrieve records (DO models), converts them to Core models, 
        and returns the list of Core models to the Service layer.
        """
        # 1. Get list of DO models from DAL
        list_do: List[QueryHistoryDO] = self._dal.queryHistory(operator)
        
        # 2. Convert each DO model to a Core model and return the list
        list_core: List[QueryHistoryCore] = [
            self._converter.do_to_core(do_model) for do_model in list_do
        ]
        
        return list_core
    
    def delete_all_history_by_operator(self, operator: str) -> bool:
        """
        Calls the DAL to delete records (DO models),
        """
        # Delete operation
        delete_result = self._dal.delete_all(operator)
        if delete_result != None:
            return True
        return False