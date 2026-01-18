from fastapi import APIRouter, HTTPException
from typing import List
from controller.dependencies import schema_service, schema_converter
from core.model.schema_models import SchemaRequest, SchemaVO

router = APIRouter(prefix="/schema", tags=["Schema Management"])

@router.post("", response_model=SchemaVO)
def add_or_update_schema(request_data: SchemaRequest):
    paramCheck(request=request_data)
    schema_core = schema_converter.request_to_core(request_data)
    return schema_service.add_or_update_schema(schema_core)

@router.get("/all/{current_user}", response_model=List[SchemaVO])
def get_all_schemas(current_user: str):
    return schema_service.get_all_schemas(operator=current_user)

@router.delete("/{table_name}/{current_user}")
def delete_schema(table_name: str, current_user: str):
    try:
        return schema_service.delete_schema(table_name, operator=current_user)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
def paramCheck(request: SchemaRequest):
    try: 
        assert request.operator != None and request.operator != "", "operator cannot be empty or null"
        assert request.table_name != None and request.table_name != "", "table name cannot be empty or null"
        assert request.ddl_context != None and request.ddl_context != "", "ddl context cannot be empty or null"
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
