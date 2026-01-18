from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Optional

# --- Enums ---
class StatusEnum(str, Enum):
    """
    Defines the possible status outcomes for an API response.
    """
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


# --- Context Models ---
class ErrorContext(BaseModel):
    """
    Provides detailed context when an API request fails.
    """
    error_message: str = Field(..., description="A detailed message explaining the error.")
    error_type: Optional[str] = Field(None, description="The category or type of the error (e.g., 'DatabaseError', 'IntentRecognitionError').")
    traceback: Optional[str] = Field(None, description="Optional stack trace or internal details for debugging.")
    suggested_action: Optional[str] = Field(None, description="A suggested action for the user or client (e.g., 'Try rephrasing the question').")

# New Request Model for Step 1
class UsernameRequest(BaseModel):
    username: str

# New Response Model for Step 1
class RecoveryQuestionsResponse(BaseModel):
    questions: List[str]