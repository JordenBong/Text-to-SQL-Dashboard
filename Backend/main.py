from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.ai_model.text_to_sql_system import TextToSQLSystem

from controller import user_auth_controller, schema_manager_controller, sql_query_controller

app = FastAPI(
    title="Text-to-SQL API",
    description="Refactored API for SQL generation and management."
)

text_to_sql_system = TextToSQLSystem()

@app.on_event("startup")
async def startup_event():
    # Load models AFTER server starts
    text_to_sql_system._lazy_load_model()

# CORS Configuration
origins = [
    "http://localhost:8000",
    "http://localhost:3000",
    "https://text-to-sql-dashboard.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(user_auth_controller.router)
app.include_router(schema_manager_controller.router)
app.include_router(sql_query_controller.router)

@app.get("/")
def read_root():
    return {"status": "Text-to-SQL API is running."}

