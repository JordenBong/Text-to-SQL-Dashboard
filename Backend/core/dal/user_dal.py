from typing import Optional
from core.dal.database.db_manager import DBManager
from core.dal.database.db_config import USERS_TABLE_NAME, USER_RECOVERY_TABLE_NAME 
from core.model.user_models import RecoveryQuestionSet, UserDO, UserRecoveryDO, UserRegister
from core.dal.security import get_password_hash # Import the hashing utility

class UserDAL:
    def __init__(self, db_manager: DBManager):
        self._db_manager = db_manager

    def get_user_by_username(self, username: str) -> Optional[UserDO]:
        sql = f"SELECT id, username, hashed_password, full_name, disabled FROM {USERS_TABLE_NAME} WHERE username = %s"
        row = self._db_manager.execute_and_fetch(sql, (username,))
        if row:
            return UserDO.model_validate(row[0])
        return None

    def create_user(self, user: UserRegister) -> UserDO:
        hashed_password = get_password_hash(user.password)
        sql = f"""
        INSERT INTO  {USERS_TABLE_NAME} (username, hashed_password, full_name) 
        VALUES (%s, %s, %s)
        """
        user_id = self._db_manager.execute_and_commit(sql, (user.username, hashed_password, user.full_name))
        
        # Return the created user object (can fetch from DB, but for simplicity, we mock)
        return UserDO(id=user_id, username=user.username, hashed_password=hashed_password, full_name=user.full_name)

    # 1. Register: Save recovery questions/answers
    def save_recovery_info(self, user_id: int, recovery_set: RecoveryQuestionSet):
        # Hash answers before saving
        hash_1 = get_password_hash(recovery_set.answer_1)
        hash_2 = get_password_hash(recovery_set.answer_2)
        hash_3 = get_password_hash(recovery_set.answer_3)
        
        sql = f"""
        INSERT INTO {USER_RECOVERY_TABLE_NAME}  (user_id, question_1, answer_1_hash, question_2, answer_2_hash, question_3, answer_3_hash) 
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        params = (user_id, recovery_set.question_1, hash_1, recovery_set.question_2, hash_2, recovery_set.question_3, hash_3)
        self._db_manager.execute_and_commit(sql, params)

    # 3. Reset Password: Get recovery hashes
    def get_recovery_info(self, user_id: int) -> Optional[UserRecoveryDO]:
        sql = f"SELECT * FROM {USER_RECOVERY_TABLE_NAME} WHERE user_id = %s"
        row = self._db_manager.execute_and_fetch(sql, (user_id,))
        if row:
            return UserRecoveryDO.model_validate(row[0])
        return None

    # 3. Reset Password: Update user's password
    def update_password(self, user_id: int, new_password_hash: str):
        sql = f"UPDATE {USERS_TABLE_NAME} SET hashed_password = %s WHERE id = %s"
        self._db_manager.execute_and_commit(sql, (new_password_hash, user_id))