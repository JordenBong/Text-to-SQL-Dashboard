import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from main import app # Assuming your FastAPI app is created in main.py

client = TestClient(app)

# PATH CONFIGURATION: Update 'schema_router' to match your actual filename
ROUTER_SERVICE_PATH = "controller.schema_manager_controller.schema_service"
ROUTER_CONVERTER_PATH = "controller.schema_manager_controller.schema_converter"

class TestSchemaRouter:

    # --- Add/Update Schema Tests ---

    def test_add_or_update_schema_success(self):
        """Tests successful schema upsert."""
        with patch(ROUTER_SERVICE_PATH) as mock_service, \
             patch(ROUTER_CONVERTER_PATH) as mock_converter:
            
            # Arrange
            mock_core = MagicMock()
            mock_converter.request_to_core.return_value = mock_core
            mock_service.add_or_update_schema.return_value = {
                "table_name": "users",
                "operator": "admin",
                "ddl_context": "CREATE TABLE...",
                "id": "1"
            }
            
            payload = {
                "table_name": "users",
                "operator": "admin",
                "ddl_context": "CREATE TABLE..."
            }

            # Act
            response = client.post("/schema", json=payload)

            # Assert
            assert response.status_code == 200
            assert response.json()["table_name"] == "users"
            mock_converter.request_to_core.assert_called_once()
            mock_service.add_or_update_schema.assert_called_once_with(mock_core)

    # --- Get All Schemas Tests ---

    def test_get_all_schemas_success(self):
        """Tests retrieving all schemas for a specific user."""
        with patch(ROUTER_SERVICE_PATH) as mock_service:
            # Arrange
            mock_service.get_all_schemas.return_value = [
                {"id": "1", "table_name": "t1", "operator": "admin", "ddl_context": "CREATE TABLE department (position)"},
                {"id": "2", "table_name": "t2", "operator": "admin", "ddl_context": "CREATE TABLE department (position)"}
            ]

            # Act
            response = client.get("/schema/all/admin")

            # Assert
            assert response.status_code == 200
            assert len(response.json()) == 2
            mock_service.get_all_schemas.assert_called_once_with(operator="admin")

    # --- Delete Schema Tests ---

    def test_delete_schema_success(self):
        """Tests successful schema deletion."""
        with patch(ROUTER_SERVICE_PATH) as mock_service:
            # Arrange
            mock_service.delete_schema.return_value = {"message": "deleted"}

            # Act
            response = client.delete("/schema/users/admin")

            # Assert
            assert response.status_code == 200
            assert response.json()["message"] == "deleted"
            mock_service.delete_schema.assert_called_once_with("users", operator="admin")

    def test_delete_schema_not_found(self):
        """Tests 404 error when schema doesn't exist."""
        with patch(ROUTER_SERVICE_PATH) as mock_service:
            # Arrange: Simulate the service raising a 404 HTTPException
            mock_service.delete_schema.side_effect = HTTPException(status_code=404, detail="Not found")

            # Act
            response = client.delete("/schema/unknown/admin")

            # Assert
            assert response.status_code == 404
            assert response.json()["detail"] == "Not found"

    def test_delete_schema_unexpected_error(self):
        """Tests 500 error for unexpected service exceptions."""
        with patch(ROUTER_SERVICE_PATH) as mock_service:
            # Arrange
            mock_service.delete_schema.side_effect = Exception("Database crash")

            # Act
            response = client.delete("/schema/users/admin")

            # Assert
            assert response.status_code == 500
            assert response.json()["detail"] == "Database crash"