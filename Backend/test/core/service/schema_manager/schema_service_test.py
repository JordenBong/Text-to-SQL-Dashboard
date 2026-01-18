import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from core.service.schema_manager.schema_service import SchemaService 

@pytest.fixture
def mock_repo():
    return MagicMock()

@pytest.fixture
def mock_converter():
    return MagicMock()

@pytest.fixture
def service(mock_converter, mock_repo):
    return SchemaService(mock_converter, mock_repo)

class TestSchemaService:

    def test_add_or_update_schema(self, service, mock_repo, mock_converter):
        # Arrange
        input_core = MagicMock()
        saved_do = MagicMock()
        saved_do.gmt_create = "2023-01-01"
        
        mock_repo.save.return_value = saved_do
        mock_converter.do_to_core.return_value = "CoreObj"
        mock_converter.core_to_vo.return_value = "FinalVO"

        # Act
        result = service.add_or_update_schema(input_core)

        # Assert
        mock_repo.save.assert_called_once_with(input_core)
        mock_converter.do_to_core.assert_called_once_with(saved_do)
        mock_converter.core_to_vo.assert_called_once_with("CoreObj")
        assert result == "FinalVO"

    def test_get_all_schemas(self, service, mock_repo, mock_converter):
        # Arrange
        do1 = MagicMock(gmt_create="time1")
        do2 = MagicMock(gmt_create="time2")
        mock_repo.find_all_by_operator.return_value = [do1, do2]
        
        mock_converter.do_to_core.side_effect = ["Core1", "Core2"]
        mock_converter.core_to_vo.side_effect = ["VO1", "VO2"]

        # Act
        results = service.get_all_schemas("admin")

        # Assert
        assert len(results) == 2
        assert results == ["VO1", "VO2"]
        mock_repo.find_all_by_operator.assert_called_once_with("admin")

    def test_delete_schema_success(self, service, mock_repo):
        # Arrange
        mock_repo.find_by_table_name_and_operator.return_value = MagicMock()
        mock_repo.delete.return_value = True

        # Act
        result = service.delete_schema("users", "admin")

        # Assert
        mock_repo.delete.assert_called_once_with("users", "admin")
        assert "deleted successfully" in result["message"]

    def test_delete_schema_not_found_raises_404(self, service, mock_repo):
        # Arrange
        mock_repo.find_by_table_name_and_operator.return_value = None

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.delete_schema("unknown_table", "admin")
        
        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail
        # Ensure delete was never even called
        mock_repo.delete.assert_not_called()