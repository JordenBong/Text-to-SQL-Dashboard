import pytest
from unittest.mock import MagicMock, patch
from core.model.models import StatusEnum
from core.model.query_models import QueryRequest, QueryHistoryCore
from core.service.sql_manager.query_service import QueryService, WARNING_MESSAGE 

@pytest.fixture
def mock_tts():
    return MagicMock()

@pytest.fixture
def mock_repo():
    return MagicMock()

@pytest.fixture
def service(mock_tts, mock_repo):
    return QueryService(mock_tts, mock_repo)

@pytest.fixture
def sample_request():
    return QueryRequest(
        question="How many users?",
        operator="admin",
        table_name="users",
        ddl_context="CREATE TABLE users...",
        need_predict_intent=True
    )

class TestQueryService:

    def test_process_success(self, service, mock_tts, mock_repo, sample_request):
        """Test a successful SQL generation flow."""
        # Arrange
        generated_sql = "SELECT count(*) FROM users;"
        mock_tts.generate_sql.return_value = generated_sql

        # Act
        response = service.process_and_generate_sql(sample_request)

        # Assert
        assert response.status == StatusEnum.SUCCESS
        assert response.result_data == generated_sql
        
        # Verify history saving
        mock_repo.save_query_history.assert_called_once()
        saved_history = mock_repo.save_query_history.call_args[0][0]
        assert saved_history.status == StatusEnum.SUCCESS
        assert saved_history.generated_sql == generated_sql
        assert saved_history.intent_recognized is True

    def test_process_warning_illegal_question(self, service, mock_tts, mock_repo, sample_request):
        """Test when the AI determines the question is not DB-related."""
        # Arrange
        mock_tts.generate_sql.return_value = WARNING_MESSAGE

        # Act
        response = service.process_and_generate_sql(sample_request)

        # Assert
        assert response.status == StatusEnum.FAILED
        assert response.error_context.error_type == "ILLEGAL_QUESTION"
        
        # Verify history reflects failure
        saved_history = mock_repo.save_query_history.call_args[0][0]
        assert saved_history.status == StatusEnum.FAILED
        assert saved_history.intent_recognized is False
        assert saved_history.error_message == "Not Database-Related Questions"

    def test_process_exception_handling(self, service, mock_tts, mock_repo, sample_request):
        """Test when the TTS system raises a technical exception."""
        # Arrange
        mock_tts.generate_sql.side_effect = Exception("Model Timeout")

        # Act
        response = service.process_and_generate_sql(sample_request)

        # Assert
        assert response.status == StatusEnum.FAILED
        assert response.error_context.error_message == "Model Timeout"
        
        # Verify history was still saved
        mock_repo.save_query_history.assert_called_once()
        saved_history = mock_repo.save_query_history.call_args[0][0]
        assert saved_history.status == StatusEnum.FAILED

    def test_history_repo_failure_does_not_crash_app(self, service, mock_tts, mock_repo, sample_request):
        """Verify the 'finally' block handles DB save failures gracefully."""
        # Arrange
        mock_tts.generate_sql.return_value = "SELECT 1"
        mock_repo.save_query_history.side_effect = Exception("DB Down")

        # Act
        # This should NOT raise an exception because of the internal try-except in 'finally'
        response = service.process_and_generate_sql(sample_request)

        # Assert
        assert response.status == StatusEnum.SUCCESS
        mock_repo.save_query_history.assert_called_once()

    def test_get_query_history(self, service, mock_repo):
        """Test simple retrieval of history."""
        # Arrange
        mock_repo.get_history_by_operator.return_value = ["history1", "history2"]

        # Act
        result = service.get_query_history("admin")

        # Assert
        assert result == ["history1", "history2"]
        mock_repo.get_history_by_operator.assert_called_once_with("admin")