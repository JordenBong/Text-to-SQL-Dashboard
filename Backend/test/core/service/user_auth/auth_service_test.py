import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from datetime import timedelta
from core.service.user_auth.auth_service import AuthService  

@pytest.fixture
def mock_dal():
    return MagicMock()

@pytest.fixture
def auth_service(mock_dal):
    return AuthService(mock_dal)

class TestAuthService:

    # --- Register User Tests ---

    def test_register_user_success(self, auth_service, mock_dal):
        # Arrange
        user_data = MagicMock(username="new_user")
        recovery_set = MagicMock()
        mock_dal.get_user_by_username.return_value = None
        new_user = MagicMock(id=1)
        mock_dal.create_user.return_value = new_user

        # Act
        result = auth_service.register_user(user_data, recovery_set)

        # Assert
        mock_dal.create_user.assert_called_once_with(user_data)
        mock_dal.save_recovery_info.assert_called_once_with(new_user.id, recovery_set)
        assert result == new_user

    def test_register_user_already_exists(self, auth_service, mock_dal):
        # Arrange
        user_data = MagicMock(username="existing_user")
        mock_dal.get_user_by_username.return_value = MagicMock()

        # Act & Assert
        with pytest.raises(HTTPException) as exc:
            auth_service.register_user(user_data, MagicMock())
        assert exc.value.status_code == 400

    # --- Login Tests ---

    @patch("core.service.user_auth.auth_service.verify_password")
    @patch("core.service.user_auth.auth_service.create_access_token")
    def test_login_success(self, mock_create_token, mock_verify, auth_service, mock_dal):
        # Arrange
        user_login = MagicMock(username="testuser", password="plain_password")
        db_user = MagicMock(username="testuser", hashed_password="hashed_password")
        mock_dal.get_user_by_username.return_value = db_user
        mock_verify.return_value = True
        mock_create_token.return_value = "fake_jwt_token"

        # Act
        result = auth_service.login_for_access_token(user_login)

        # Assert
        assert result.access_token == "fake_jwt_token"
        mock_verify.assert_called_once_with("plain_password", "hashed_password")

    def test_login_invalid_user(self, auth_service, mock_dal):
        # Arrange
        mock_dal.get_user_by_username.return_value = None
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc:
            auth_service.login_for_access_token(MagicMock())
        assert exc.value.status_code == 401

    # --- Reset Password Tests ---

    @patch("core.service.user_auth.auth_service.verify_password")
    @patch("core.service.user_auth.auth_service.get_password_hash")
    def test_reset_password_success(self, mock_hash, mock_verify, auth_service, mock_dal):
        # Arrange
        reset_data = MagicMock(username="user1", new_password="new_pass")
        db_user = MagicMock(id=10)
        recovery_info = MagicMock(answer_1_hash="h1", answer_2_hash="h2", answer_3_hash="h3")
        
        mock_dal.get_user_by_username.return_value = db_user
        mock_dal.get_recovery_info.return_value = recovery_info
        mock_verify.return_value = True # Simulate all 3 answers correct
        mock_hash.return_value = "new_hashed_pass"

        # Act
        response = auth_service.reset_password(reset_data)

        # Assert
        mock_dal.update_password.assert_called_once_with(10, "new_hashed_pass")
        assert response["message"] == "Password reset successful"

    @patch("core.service.user_auth.auth_service.verify_password")
    def test_reset_password_wrong_answers(self, mock_verify, auth_service, mock_dal):
        # Arrange
        mock_dal.get_user_by_username.return_value = MagicMock(id=10)
        mock_dal.get_recovery_info.return_value = MagicMock()
        mock_verify.side_effect = [True, False, True] # Second answer fails

        # Act & Assert
        with pytest.raises(HTTPException) as exc:
            auth_service.reset_password(MagicMock())
        assert exc.value.status_code == 401

    # --- Recovery Questions Tests ---

    def test_get_recovery_questions_success(self, auth_service, mock_dal):
        # Arrange
        mock_dal.get_user_by_username.return_value = MagicMock(id=1)
        mock_dal.get_recovery_info.return_value = MagicMock(
            question_1="Q1", question_2="Q2", question_3="Q3"
        )

        # Act
        questions = auth_service.get_recovery_questions("user1")

        # Assert
        assert questions == ["Q1", "Q2", "Q3"]

    def test_get_recovery_questions_user_not_found(self, auth_service, mock_dal):
        # Arrange
        mock_dal.get_user_by_username.return_value = None

        # Act & Assert
        with pytest.raises(HTTPException) as exc:
            auth_service.get_recovery_questions("fake")
        assert exc.value.status_code == 400
        assert exc.value.detail == "Invalid username"