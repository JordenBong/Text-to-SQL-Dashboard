import pytest
from unittest.mock import MagicMock
from core.service.sql_manager.query_history_repository import QueryHistoryRepository  

@pytest.fixture
def mock_dal():
    return MagicMock()

@pytest.fixture
def mock_converter():
    return MagicMock()

@pytest.fixture
def repository(mock_dal, mock_converter):
    return QueryHistoryRepository(mock_dal, mock_converter)

class TestQueryHistoryRepository:

    def test_save_query_history(self, repository, mock_dal, mock_converter):
        # Arrange
        input_core = MagicMock()
        input_core.id = None  # Initially no ID
        
        mock_do = MagicMock()
        generated_id = 999
        
        # Setup mocks to return specific values
        mock_converter.core_to_do.return_value = mock_do
        mock_dal.insert_query_history.return_value = generated_id

        # Act
        result_core = repository.save_query_history(input_core)

        # Assert
        # 1. Verify Core -> DO conversion
        mock_converter.core_to_do.assert_called_once_with(input_core)
        
        # 2. Verify DAL interaction with the DO
        mock_dal.insert_query_history.assert_called_once_with(mock_do)
        
        # 3. Verify ID assignment and return
        assert result_core.id == generated_id
        assert result_core == input_core

    def test_get_history_by_operator(self, repository, mock_dal, mock_converter):
        # Arrange
        operator_name = "test_user"
        do_list = [MagicMock(), MagicMock()]
        core_list = ["CoreObj1", "CoreObj2"]
        
        mock_dal.queryHistory.return_value = do_list
        # side_effect allows the mock to return different values for sequential calls
        mock_converter.do_to_core.side_effect = core_list

        # Act
        results = repository.get_history_by_operator(operator_name)

        # Assert
        # 1. Verify DAL was queried with correct operator
        mock_dal.queryHistory.assert_called_once_with(operator_name)
        
        # 2. Verify converter was called for each DO in the list
        assert mock_converter.do_to_core.call_count == 2
        
        # 3. Verify final list matches converted objects
        assert results == core_list
        assert results[0] == "CoreObj1"