import pytest
from unittest.mock import MagicMock
from core.service.schema_manager.schema_repository import SchemaRepository  

@pytest.fixture
def mock_dal():
    return MagicMock()

@pytest.fixture
def mock_converter():
    return MagicMock()

@pytest.fixture
def repository(mock_dal, mock_converter):
    return SchemaRepository(mock_dal, mock_converter)

class TestSchemaRepository:

    def test_find_by_table_name_and_operator(self, repository, mock_dal, mock_converter):
        # Arrange
        mock_dal.get_schema_by_name_and_operator.return_value = {"id": 1}
        mock_converter.do_to_core.return_value = "ConvertedObject"

        # Act
        result = repository.find_by_table_name_and_operator("users", "admin")

        # Assert
        mock_dal.get_schema_by_name_and_operator.assert_called_once_with("users", "admin")
        mock_converter.do_to_core.assert_called_once_with({"id": 1})
        assert result == "ConvertedObject"

    def test_find_all_by_operator(self, repository, mock_dal, mock_converter):
        # Arrange
        mock_dal.get_all_schemas_by_operator.return_value = [{"id": 1}, {"id": 2}]
        mock_converter.do_to_core.side_effect = ["Obj1", "Obj2"]

        # Act
        results = repository.find_all_by_operator("admin")

        # Assert
        assert len(results) == 2
        assert results == ["Obj1", "Obj2"]
        assert mock_dal.get_all_schemas_by_operator.call_count == 1

    def test_save_performs_update_when_exists(self, repository, mock_dal, mock_converter):
        # Arrange
        schema_input = MagicMock(table_name="users", operator="admin", ddl_context="SQL")
        
        # 1. Mock the internal method call
        repository.find_by_table_name_and_operator = MagicMock(side_effect=["ExistingRecord", "RefreshedRecord"])
        
        # 2. Mock the converter to return the "RefreshedRecord" when called
        mock_converter.do_to_core.side_effect = lambda x: x 

        # Act
        result = repository.save(schema_input)

        # Assert
        mock_dal.update_schema.assert_called_once_with("users", "SQL", "admin")
        assert result == "RefreshedRecord"

    def test_save_performs_insert_when_new(self, repository, mock_dal, mock_converter):
        # Arrange
        schema_input = MagicMock(table_name="users", operator="admin", ddl_context="SQL")
        
        # 1. Mock the internal method call
        repository.find_by_table_name_and_operator = MagicMock(side_effect=[None, "NewRecord"])
        
        # 2. Mock the converter to return the "NewRecord" when called
        mock_converter.do_to_core.side_effect = lambda x: x

        # Act
        result = repository.save(schema_input)

        # Assert
        mock_dal.add_schema.assert_called_once_with("users", "SQL", "admin")
        assert result == "NewRecord"

    def test_delete_returns_status(self, repository, mock_dal):
        # Arrange
        mock_dal.delete_schema.return_value = True

        # Act
        result = repository.delete("users", "admin")

        # Assert
        mock_dal.delete_schema.assert_called_once_with("users", "admin")
        assert result is True