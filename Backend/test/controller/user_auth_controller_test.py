import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

# Import the app or router. 
# Assuming your FastAPI app is created in a main.py that includes this router.
from main import app 
from controller.dependencies import auth_service

client = TestClient(app)

class TestAuthRouter:

    def test_register_user_success(self):
        # Arrange
        # We patch the auth_service instance where it's used in the router
        with patch("controller.user_auth_controller.auth_service") as mock_service:
            mock_service.login_for_access_token.return_value = {"access_token": "fake_token", "token_type": "bearer"}
            
            payload = {
                "user": {
                    "username": "testuser",
                    "password": "password123",
                    "email": "test@example.com"
                },
                "recovery": {
                    "question_1": "Q1", "answer_1": "A1",
                    "question_2": "Q2", "answer_2": "A2",
                    "question_3": "Q3", "answer_3": "A3"
                }
            }

            # Act
            response = client.post("/auth/register", json=payload)

            # Assert
            assert response.status_code == 200
            assert response.json()["access_token"] == "fake_token"
            mock_service.register_user.assert_called_once()

    def test_login_success(self):
        # Arrange
        with patch("controller.user_auth_controller.auth_service") as mock_service:
            mock_service.login_for_access_token.return_value = {"access_token": "login_token", "token_type": "bearer"}
            
            payload = {"username": "testuser", "password": "password123"}

            # Act
            response = client.post("/auth/token", json=payload)

            # Assert
            assert response.status_code == 200
            assert response.json()["access_token"] == "login_token"
            mock_service.login_for_access_token.assert_called_once()

    def test_reset_password_success(self):
        # Arrange
        with patch("controller.user_auth_controller.auth_service") as mock_service:
            mock_service.reset_password.return_value = {"message": "success"}
            
            payload = {
                "username": "testuser",
                "new_password": "newpassword",
                "recovery_set": {
                    "question_1": "Q1", 
                    "answer_1": "A1", 
                    "question_2": "Q2", 
                    "answer_2": "A2", 
                    "question_3": "Q3", 
                    "answer_3": "A3"
                }
            }

            # Act
            response = client.post("/auth/reset-password", json=payload)

            # Assert
            assert response.status_code == 200
            assert response.json()["message"] == "success"

    def test_get_reset_questions_success(self):
        # Arrange
        with patch("controller.user_auth_controller.auth_service") as mock_service:
            mock_service.get_recovery_questions.return_value = ["Q1", "Q2", "Q3"]
            
            payload = {"username": "testuser"}

            # Act
            response = client.post("/auth/reset-password/questions", json=payload)

            # Assert
            assert response.status_code == 200
            assert response.json()["questions"] == ["Q1", "Q2", "Q3"]
            mock_service.get_recovery_questions.assert_called_once_with("testuser")

    def test_login_failure_service_exception(self):
        # Arrange
        from fastapi import HTTPException
        with patch("controller.user_auth_controller.auth_service") as mock_service:
            # Simulate the service raising a 401
            mock_service.login_for_access_token.side_effect = HTTPException(status_code=401, detail="Invalid credentials")
            
            # Act
            response = client.post("/auth/token", json={"username": "wrong", "password": "bad"})

            # Assert
            assert response.status_code == 401
            assert response.json()["detail"] == "Invalid credentials"