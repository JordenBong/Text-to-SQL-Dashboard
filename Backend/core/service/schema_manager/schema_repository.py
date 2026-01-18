from typing import List, Optional
from core.dal.schema_dal import SchemaDAL
from core.model.schema_models import SchemaCore
from core.converter.schema_converter import SchemaConverter

class SchemaRepository:
    """
    Coordinates data access between the Service layer and the DAL.
    The Repository handles the mapping between Domain/Core models and 
    the Data Objects used by the database.
    """
    def __init__(self, schema_dal: SchemaDAL, converter: SchemaConverter):
        self._dal = schema_dal
        self._converter = converter

    def find_by_table_name_and_operator(self, table_name: str, operator: str) -> Optional[SchemaCore]:
        """Retrieves a single schema record."""
        return self._converter.do_to_core(self._dal.get_schema_by_name_and_operator(table_name, operator))

    def find_all_by_operator(self, operator: str) -> List[SchemaCore]:
        """Retrieves all schema records for a specific operator."""
        return [self._converter.do_to_core(data_object) for data_object in self._dal.get_all_schemas_by_operator(operator)]

    def save(self, schema: SchemaCore) -> SchemaCore:
        """
        Handles the logic of 'Upsert' (Update or Insert).
        Returns the latest state of the record from the database.
        """
        existing = self.find_by_table_name_and_operator(schema.table_name, schema.operator)
        
        if existing:
            self._dal.update_schema(schema.table_name, schema.ddl_context, schema.operator)
        else:
            self._dal.add_schema(schema.table_name, schema.ddl_context, schema.operator)
            
        # Return the refreshed record from the DB
        return self._converter.do_to_core(self.find_by_table_name_and_operator(schema.table_name, schema.operator))

    def delete(self, table_name: str, operator: str) -> bool:
        """Deletes a schema record and returns success status."""
        return self._dal.delete_schema(table_name, operator)