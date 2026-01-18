from core.ai_model.text_to_sql_system import TextToSQLSystem
from core.dal.database.db_manager import DBManager
from core.dal.query_history_dal import QueryHistoryDAL
from core.converter.query_history_converter import QueryHistoryConverter
from core.service.sql_manager.query_history_repository import QueryHistoryRepository
from core.service.sql_manager.query_service import QueryService
from core.dal.user_dal import UserDAL 
from core.service.user_auth.auth_service import AuthService
from core.dal.schema_dal import SchemaDAL
from core.service.schema_manager.schema_repository import SchemaRepository
from core.service.schema_manager.schema_service import SchemaService
from core.converter.schema_converter import SchemaConverter

# Core Components
db_manager = DBManager()
tts_system = TextToSQLSystem()

# Services & Repositories
query_history_converter = QueryHistoryConverter()
query_history_dal = QueryHistoryDAL(db_manager=db_manager)
query_history_repo = QueryHistoryRepository(dal=query_history_dal, converter=query_history_converter)
query_service = QueryService(tts_system=tts_system, history_repo=query_history_repo)

user_dal = UserDAL(db_manager=db_manager)
auth_service = AuthService(user_dal=user_dal)

schema_dal = SchemaDAL(db_manager=db_manager)
schema_converter = SchemaConverter() 
schema_repository = SchemaRepository(schema_dal=schema_dal, converter=schema_converter)
schema_service = SchemaService(schema_repository=schema_repository, converter=schema_converter)