from fastapi import Depends, HTTPException, status, FastAPI
from fastapi.security import OAuth2PasswordBearer
from core.ai_model.text_to_sql_system import TextToSQLSystem
from core.dal.database.db_manager import DBManager
from core.dal.query_history_dal import QueryHistoryDAL
from core.converter.query_history_converter import QueryHistoryConverter
from core.service.sql_manager.query_history_repository import QueryHistoryRepository
from core.service.sql_manager.query_service import QueryService
from core.model.query_models import QueryHistoryCore, QueryHistoryVO, QueryRequest, QueryResponse
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from core.dal.user_dal import UserDAL 
from core.service.user_auth.auth_service import AuthService
from core.model.user_models import UserRegister, UserLogin, Token, PasswordReset, RecoveryQuestionSet
from core.dal.schema_dal import SchemaDAL
from core.service.schema_manager.schema_service import SchemaService
from core.model.schema_models import SchemaRequest
from core.converter.schema_converter import SchemaConverter # NEW IMPORT
from core.model.schema_models import SchemaVO
from core.model.models import UsernameRequest, RecoveryQuestionsResponse


# --- Dependency Initialization ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# Placeholder for user retrieval (needs actual implementation based on your auth setup)
def get_current_user(token: str = Depends(oauth2_scheme)):
    # In a real app, this function would decode the JWT, look up the user, 
    # and verify their status. For now, we just ensure a token is present.
    try:
        # Example using the security module's JWT verification (you need to implement this)
        # payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # username: str = payload.get("sub")
        # if username is None: raise HTTPException(...)
        return {"username": "authenticated_user"}
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


# 1. Core Components
tts_system = TextToSQLSystem()
db_manager = DBManager()
converter = QueryHistoryConverter()

# 2. Persistence Components
query_history_dal = QueryHistoryDAL(db_manager=db_manager)
query_history_repo = QueryHistoryRepository(dal=query_history_dal, converter=converter)

# 3. Service Layer
query_service = QueryService(tts_system=tts_system, history_repo=query_history_repo)

# 4. User Authentication Components
user_dal = UserDAL(db_manager=db_manager)
auth_service = AuthService(user_dal=user_dal)

# NEW: Schema Management Components
schema_dal = SchemaDAL(db_manager=db_manager)
# NEW: Schema Converter
schema_converter = SchemaConverter() 
# NEW: Schema Service (now takes the converter)
schema_service = SchemaService(schema_dal=schema_dal, converter=schema_converter)


# --- FastAPI App Setup ---
app = FastAPI(
    title="Text-to-SQL API",
    description="API for converting natural language questions into SQL queries and retrieving history."
)

# ADD THIS CORS BLOCK BELOW app = FastAPI(...)
origins = [
    "http://localhost:8000",       # Default localhost
    "http://localhost:3000",  # Your React development server
    # Add other frontend URLs as needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],    # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],    # Allow all headers
)

# --- SQL Generation Endpoints ---

@app.post("/generate_sql", response_model=QueryResponse)
def generate_sql_query(request: QueryRequest) -> QueryResponse:
    """
    Accepts a natural language question, generates SQL, and saves the process to history.
    """
    # Delegate the entire business process to the service layer
    return query_service.process_and_generate_sql(request)


# 2. History Retrieval Endpoint (New Feature)
@app.get("/history/{operator}", response_model=List[QueryHistoryVO])
def get_history(operator: str) -> List[QueryHistoryVO]:
    """
    Retrieves the last 200 query records filtered by the given operator.
    """
    try:
        # Get Core models from the service layer
        history_core_list: List[QueryHistoryCore] = query_service.get_query_history(operator)
        
        # Convert Core models to VO models for external API response
        history_vo_list: List[QueryHistoryVO] = [
            converter.core_to_vo(core_model) for core_model in history_core_list
        ]
        
        return history_vo_list
    
    except Exception as e:
        # Handle database or service errors for history retrieval
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to retrieve history for operator '{operator}': {str(e)}"
        )


# --- Authentication Endpoints ---

# 2. Register Account
@app.post("/auth/register", response_model=Token)
def register_user(user: UserRegister, recovery: RecoveryQuestionSet):
    # This endpoint assumes you provide the recovery questions/answers on registration
    auth_service.register_user(user, recovery)
    return auth_service.login_for_access_token(UserLogin(username=user.username, password=user.password))

# 1. Login Account
@app.post("/auth/token", response_model=Token)
def login(user: UserLogin):
    return auth_service.login_for_access_token(user)

# 3. Reset Password
@app.post("/auth/reset-password")
def reset_password(reset_data: PasswordReset):
    return auth_service.reset_password(reset_data)

# New Endpoint for Step 1: Get Questions
@app.post("/auth/reset-password/questions", response_model=RecoveryQuestionsResponse)
def get_reset_questions(request: UsernameRequest):
    questions = auth_service.get_recovery_questions(request.username)
    return RecoveryQuestionsResponse(questions=questions)


# --- New API Endpoints for Schema Management (Protected) ---

# Use SchemaCore for input (client doesn't provide ID/timestamp)
# Use SchemaVO for output (client expects presentation data)
@app.post("/schema", response_model=SchemaVO)
def add_or_update_schema(request_data: SchemaRequest):
    """Adds or updates a schema, scoped to the current operator."""
    
    # 1. Convert Request (VO) to Core (Business Object)
    schema_core = schema_converter.request_to_core(request_data)
    
    # 2. Pass Core model to the Service layer for processing
    return schema_service.add_or_update_schema(schema_core)

@app.get("/schema/all/{current_user}", response_model=List[SchemaVO])
def get_all_schemas(current_user: str):
    """Retrieves all stored table schemas for the current operator."""
    return schema_service.get_all_schemas(operator=current_user)

@app.delete("/schema/{table_name}/{current_user}")
def delete_schema(table_name: str, current_user: str):
    """Deletes a table schema by its table_name, scoped to the current operator."""
    try:
        return schema_service.delete_schema(table_name, operator=current_user)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

# --- Health Check Endpoints ---

# Health Check Endpoint
@app.get("/")
def read_root():
    return {"status": "Text-to-SQL API is running."}