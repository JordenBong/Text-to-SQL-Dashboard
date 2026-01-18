from pydantic import BaseModel, Field
from typing import Optional

# --- JWT/Token Models ---
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None

# --- User Database Model (DO) ---
class UserDO(BaseModel):
    id: Optional[int] = None
    username: str
    hashed_password: str
    full_name: Optional[str] = None
    disabled: bool = False

# --- API Request Models ---
class UserRegister(BaseModel):
    username: str = Field(..., min_length=4)
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None
    
class UserLogin(BaseModel):
    username: str
    password: str

# --- Recovery Models ---
class RecoveryQuestionSet(BaseModel):
    question_1: str
    answer_1: str
    question_2: str
    answer_2: str
    question_3: str
    answer_3: str

class PasswordReset(BaseModel):
    username: str
    new_password: str = Field(..., min_length=6)
    recovery_set: RecoveryQuestionSet

# --- User Recovery DO (Database Object) ---
class UserRecoveryDO(BaseModel):
    user_id: int
    question_1: str
    answer_1_hash: str
    question_2: str
    answer_2_hash: str
    question_3: str
    answer_3_hash: str