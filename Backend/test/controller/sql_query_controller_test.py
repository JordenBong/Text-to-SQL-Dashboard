import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from fastapi import HTTPException

# Assuming your FastAPI app is created in main.py
from main import app 

client = TestClient(app)

# PATH CONFIGURATION:
# Adjust these strings to match the actual name of your router file
ROUTER_SERVICE_PATH = "controller.sql_query_controller.query_service"
ROUTER_CONVERTER_PATH = "controller.sql_query_controller.query_history_converter"

class TestQueryRouter:

    # --- SQL Generation Tests ---

    def test_generate_sql_success(self):
        """Tests successful POST request to generate_sql."""
        with patch(ROUTER_SERVICE_PATH) as mock_service:
            # Arrange
            mock_service.process_and_generate_sql.return_value = {
                "status": "SUCCESS",
                "result_data": "SELECT * FROM users;",
                "error_context": None
            }
            
            payload = {
                "question": "Show all users",
                "operator": "admin",
                "table_name": "users",
                "ddl_context": "CREATE TABLE users...",
                "need_predict_intent": True
            }

            # Act
            response = client.post("/generate_sql", json=payload)

            # Assert
            assert response.status_code == 200
            assert response.json()["result_data"] == "SELECT * FROM users;"
            mock_service.process_and_generate_sql.assert_called_once()

    # --- History Retrieval Tests ---

    def test_get_history_success(self):
        """Tests successful GET request for history mapping Core to VO."""
        with patch(ROUTER_SERVICE_PATH) as mock_service, \
             patch(ROUTER_CONVERTER_PATH) as mock_converter:
            
            # Arrange
            mock_core = MagicMock()
            mock_service.get_query_history.return_value = [mock_core]
            mock_converter.core_to_vo.return_value = {
                "question": "test question",
                "intent_recognized": True,
                "generated_sql": "SELECT 1",
                "status": "SUCCESS",
                "gmt_create": "2023-01-01"
            }

            # Act
            response = client.get("/history/admin")

            # Assert
            assert response.status_code == 200
            assert isinstance(response.json(), list)
            assert response.json()[0]["question"] == "test question"
            mock_service.get_query_history.assert_called_once_with("admin")
            mock_converter.core_to_vo.assert_called_once_with(mock_core)

    def test_get_history_server_error(self):
        """Tests that a service exception is converted to a 500 HTTPException."""
        with patch(ROUTER_SERVICE_PATH) as mock_service:
            # Arrange
            mock_service.get_query_history.side_effect = Exception("Database connection lost")

            # Act
            response = client.get("/history/admin")

            # Assert
            assert response.status_code == 500
            assert "Failed to retrieve history" in response.json()["detail"]
            assert "Database connection lost" in response.json()["detail"]

    def test_generate_sql_validation_error(self):
        """Tests that an incomplete payload returns 422 Unprocessable Entity."""
        # Act: Missing required 'question' field
        payload = {"operator": "admin"}
        response = client.post("/generate_sql", json=payload)

        # Assert
        assert response.status_code == 422