from fastapi import APIRouter, HTTPException
from controller.dependencies import auth_service
from core.model.user_models import UserRegister, UserLogin, Token, PasswordReset, RecoveryQuestionSet
from core.model.models import UsernameRequest, RecoveryQuestionsResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=Token)
def register_user(user: UserRegister, recovery: RecoveryQuestionSet):
    validate_user_register(request=user, recovery=recovery)
    auth_service.register_user(user, recovery)
    return auth_service.login_for_access_token(UserLogin(username=user.username, password=user.password))

@router.post("/token", response_model=Token)
def login(user: UserLogin):
    validate_user_login(user)
    return auth_service.login_for_access_token(user)

@router.post("/reset-password")
def reset_password(reset_data: PasswordReset):
    validate_password_reset(request=reset_data)
    return auth_service.reset_password(reset_data)

@router.post("/reset-password/questions", response_model=RecoveryQuestionsResponse)
def get_reset_questions(request: UsernameRequest):
    validate_username(request=request)
    questions = auth_service.get_recovery_questions(request.username)
    return RecoveryQuestionsResponse(questions=questions)


def validate_user_register(request: UserRegister, recovery: RecoveryQuestionSet):
    try:
        assert request != None, "request cannot be null."
        assert request.username != None and request.username != "", "username cannot be null."
        assert request.password != None and request.password != "", "password cannot be null."
        assert len(request.password) >= 6, "String length must be at least 6 characters"
        assert recovery != None, "recovery question request cannot be null."
        assert recovery.question_1 != None and recovery.question_1 != "", "question_1 cannot be null."
        assert recovery.answer_1 != None and recovery.answer_1 != "", "answer_1 cannot be null."
        assert recovery.question_2 != None and recovery.question_2 != "", "question_2 cannot be null."
        assert recovery.answer_2 != None and recovery.answer_2 != "", "answer_2 cannot be null."
        assert recovery.question_3 != None and recovery.question_3 != "", "question_3 cannot be null."
        assert recovery.answer_3 != None and recovery.answer_3 != "", "answer_3 cannot be null."
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

def validate_user_login(request: UserLogin):
    try:
        assert request != None, "request cannot be null."
        assert request.username != None and request.username != "", "username cannot be null."
        assert request.password != None and request.password != "", "password cannot be null."
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    
def validate_username(request: UsernameRequest):
    try:
        assert request != None, "request cannot be null."
        assert request.username != None and request.username != "", "username cannot be null."
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    

def validate_password_reset(request: PasswordReset):
    try:
        assert request != None, "request cannot be null."
        assert request.username != None and request.username != "", "username cannot be null."
        assert request.new_password != None and request.new_password != "", "new password cannot be null."
        assert len(request.new_password) >= 6, "String length must be at least 6 characters"
        assert request.recovery_set.answer_1 != None and request.recovery_set.answer_1 != "", "answer 1 cannot be null."
        assert request.recovery_set.answer_2 != None and request.recovery_set.answer_2 != "", "answer 2 cannot be null."
        assert request.recovery_set.answer_3 != None and request.recovery_set.answer_3 != "", "answer 3 cannot be null."

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )