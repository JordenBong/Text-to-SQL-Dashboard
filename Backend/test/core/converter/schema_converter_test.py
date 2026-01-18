import pytest
from core.converter.schema_converter import SchemaConverter
from core.model.schema_models import SchemaDO, SchemaCore, SchemaRequest, SchemaVO

class TestSchemaConverter:

    @pytest.fixture
    def converter(self):
        return SchemaConverter()

    def test_core_to_do(self, converter):
        core = SchemaCore(id=10, table_name="users", ddl_context="CREATE...", operator="sys")
        result = converter.core_to_do(core)
        
        assert result.id == 10
        assert result.table_name == "users"

    def test_do_to_core(self, converter):
        do_obj = SchemaDO(id=5, table_name="logs", ddl_context="CTX", operator="admin")
        result = converter.do_to_core(do_obj)
        
        assert isinstance(result, SchemaCore)
        assert result.table_name == "logs"

    def test_core_to_vo_success(self, converter):
        core = SchemaCore(id=1, table_name="test", ddl_context="...", operator="op")
        # Passing required gmt_create timestamp as per method signature
        result = converter.core_to_vo(core, created_at="2023-01-01")
        
        assert isinstance(result, SchemaVO)
        assert result.id == 1

    def test_core_to_vo_missing_id_raises_error(self, converter):
        core = SchemaCore(id=None, table_name="fail", ddl_context="...", operator="op")
        with pytest.raises(ValueError, match="Cannot convert incomplete SchemaCore"):
            converter.core_to_vo(core, created_at="now")

    def test_request_to_core(self, converter):
        req = SchemaRequest(table_name="req_table", ddl_context="DDL", operator="user_from_jwt")
        result = converter.request_to_core(req)
        
        assert result.id is None
        assert result.operator == "user_from_jwt"