from typing import Optional
from core.model.schema_models import SchemaDO, SchemaCore, SchemaRequest, SchemaVO

class SchemaConverter:
    """Handles conversion between Schema Data Object (DO), Core, and View Object (VO)."""

    # ------------------
    # Core <-> DO
    # ------------------

    def core_to_do(self, core: SchemaCore) -> SchemaDO:
        """Converts SchemaCore to SchemaDO."""
        if core is None:
            return None
        
        return SchemaDO(
            id=core.id,
            table_name=core.table_name,
            ddl_context=core.ddl_context,
            operator=core.operator,
            gmt_create=core.gmt_create
        )

    def do_to_core(self, data_object: SchemaDO) -> SchemaCore:
        """Converts SchemaDO to SchemaCore."""
        if data_object is None:
            return None
        
        return SchemaCore(
            id=data_object.id,
            table_name=data_object.table_name,
            ddl_context=data_object.ddl_context,
            operator=data_object.operator,
            gmt_create=data_object.gmt_create
        )

    # ------------------
    # Core -> VO
    # ------------------
    
    def core_to_vo(self, core: SchemaCore) -> SchemaVO:
        """Converts SchemaCore to SchemaVO, requiring the creation timestamp."""
        if core.id is None:
            raise ValueError("Cannot convert incomplete SchemaCore (missing ID) to SchemaVO.")
            
        return SchemaVO(
            id=core.id,
            table_name=core.table_name,
            ddl_context=core.ddl_context,
            operator=core.operator,
        )
    
    # ------------------
    # Request -> Core
    # ------------------

    def request_to_core(self, request: SchemaRequest) -> SchemaCore:
        """Converts SchemaRequest to SchemaCore, adding the operator from the JWT."""
        return SchemaCore(
            id=None,
            table_name=request.table_name,
            ddl_context=request.ddl_context,
            operator=request.operator 
        )
    
