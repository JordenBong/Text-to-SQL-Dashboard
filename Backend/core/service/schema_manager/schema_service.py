from core.converter.schema_converter import SchemaConverter 
from core.model.schema_models import SchemaCore, SchemaVO, SchemaDO 
from core.service.schema_manager.schema_repository import SchemaRepository
from fastapi import HTTPException
from typing import List

class SchemaService:
    """
    Coordinates CRUD oeprations upon schema information between users and database
    """
    def __init__(self, converter: SchemaConverter, schema_repository: SchemaRepository): 
        self._schema_repository = schema_repository
        self._converter = converter

    def _map_do_to_vo(self, schema_do: SchemaDO) -> SchemaVO:
        """ Helper to map DO to VO """
        core = self._converter.do_to_core(schema_do)
        return self._converter.core_to_vo(core)

    def add_or_update_schema(self, schema: SchemaCore) -> SchemaVO:
        """ insert or update schema """
        schema_do = self._schema_repository.save(schema)
        return self._map_do_to_vo(schema_do)

    def get_all_schemas(self, operator: str) -> List[SchemaVO]:
        """ query all schema """
        schemas_do = self._schema_repository.find_all_by_operator(operator)
        return [self._map_do_to_vo(s) for s in schemas_do]

    def delete_schema(self, table_name: str, operator: str):
        """ delete schema """
        if not self._schema_repository.find_by_table_name_and_operator(table_name, operator):
            raise HTTPException(status_code=404, detail=f"Table schema '{table_name}' not found for operator '{operator}'.")
        
        self._schema_repository.delete(table_name, operator)
        return {"message": f"Table schema '{table_name}' deleted successfully."}