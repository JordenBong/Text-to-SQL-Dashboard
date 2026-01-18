from fastapi import APIRouter, HTTPException
from typing import List
from controller.dependencies import query_service, query_history_converter
from core.model.query_models import QueryHistoryVO, QueryRequest, QueryResponse, QueryHistoryCore

router = APIRouter(tags=["SQL Generation & History"])

@router.post("/generate_sql", response_model=QueryResponse)
def generate_sql_query(request: QueryRequest) -> QueryResponse:
    paramCheck(request=request)
    return query_service.process_and_generate_sql(request)

@router.delete("/history/{operator}", response_model=None)
def delete_sql_qeury(operator: str) -> QueryResponse:
    return query_service.delete_all_history(operator)

@router.get("/history/{operator}", response_model=List[QueryHistoryVO])
def get_history(operator: str) -> List[QueryHistoryVO]:
    try:
        history_core_list: List[QueryHistoryCore] = query_service.get_query_history(operator)
        return [query_history_converter.core_to_vo(core) for core in history_core_list]
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to retrieve history for operator '{operator}': {str(e)}"
        )
    
def paramCheck(request: QueryRequest):
    try:
        assert request != None, "request cannot be null."
        assert request.question != None and request.question != "", "question cannot be null."
        assert request.need_predict_intent != None,  "need_predict_intent cannot be null."
        assert request.operator != None and request.operator != "", "operator cannot be null."
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
