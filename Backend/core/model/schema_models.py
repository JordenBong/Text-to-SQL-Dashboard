from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

# ---------------------------------------------
# 1. Data Object (DO) - Database Representation
# ---------------------------------------------
class SchemaDO(BaseModel):
    """Matches the database table structure."""
    id: Optional[int] = None
    gmt_create: Optional[datetime] = None
    table_name: str = Field(..., max_length=128)
    ddl_context: str = Field(..., description="The SQL DDL context.")
    operator: str = Field(..., max_length=50)

# ---------------------------------------------
# 2. Core Business Object (Core) - Business Logic Layer
# ---------------------------------------------
class SchemaCore(BaseModel):
    """Used within the Service/Repository layers."""
    id: Optional[int] = None
    gmt_create: Optional[datetime] = None
    table_name: str = Field(..., max_length=128)
    ddl_context: str
    operator: str
    
# ---------------------------------------------
# 3. View Object (VO) - API Presentation Layer
# ---------------------------------------------
class SchemaVO(BaseModel):
    """Used for the final API response."""
    id: int
    table_name: str
    ddl_context: str
    operator: str

class SchemaRequest(BaseModel):
    """Model used for incoming POST/PUT requests from the API client."""
    table_name: str = Field(..., max_length=128)
    ddl_context: str = Field(..., description="The SQL DDL statement.")
    operator: str = Field(..., description="Current user")
