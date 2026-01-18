from typing import List
from core.dal.user_dal import UserDAL
from core.model.user_models import UserRegister, UserLogin, Token, PasswordReset, RecoveryQuestionSet, UserDO
from core.dal.security import verify_password, get_password_hash, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from fastapi import HTTPException
from datetime import timedelta

class AuthService:
    def __init__(self, user_dal: UserDAL):
        self._user_dal = user_dal

    # 1. Register Account
    def register_user(self, user_data: UserRegister, recovery_set: RecoveryQuestionSet) -> UserDO:
        if self._user_dal.get_user_by_username(user_data.username):
            raise HTTPException(status_code=400, detail="Username already exists")

        new_user = self._user_dal.create_user(user_data)
        self._user_dal.save_recovery_info(new_user.id, recovery_set)
        
        return new_user

    # 2. Login Account
    def login_for_access_token(self, user_data: UserLogin) -> Token:
        user = self._user_dal.get_user_by_username(user_data.username)
        
        if not user or not verify_password(user_data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Incorrect username or password")
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        return Token(access_token=access_token)

    # 3. Reset Password
    def reset_password(self, reset_data: PasswordReset):
        user = self._user_dal.get_user_by_username(reset_data.username)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        recovery_info = self._user_dal.get_recovery_info(user.id)
        if not recovery_info:
            raise HTTPException(status_code=400, detail="Recovery questions not set up")

        # Verify all three recovery answers
        if not (verify_password(reset_data.recovery_set.answer_1, recovery_info.answer_1_hash) and
                verify_password(reset_data.recovery_set.answer_2, recovery_info.answer_2_hash) and
                verify_password(reset_data.recovery_set.answer_3, recovery_info.answer_3_hash)):
            raise HTTPException(status_code=401, detail="One or more recovery answers are incorrect")

        new_password_hash = get_password_hash(reset_data.new_password)
        self._user_dal.update_password(user.id, new_password_hash)
        return {"message": "Password reset successful"}
    
    # Get recovery questions
    def get_recovery_questions(self, username: str) -> List[str]:
        user = self._user_dal.get_user_by_username(username)
        if not user:
            # Raise a generic error to avoid exposing user existence
            raise HTTPException(status_code=400, detail="Invalid username") 

        recovery_info = self._user_dal.get_recovery_info(user.id)
        if not recovery_info:
            raise HTTPException(status_code=400, detail="Recovery not set up for this user")
            
        return [recovery_info.question_1, recovery_info.question_2, recovery_info.question_3]