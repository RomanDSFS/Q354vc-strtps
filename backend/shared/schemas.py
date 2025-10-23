from pydantic import BaseModel
from uuid import UUID

class CurrentUser(BaseModel):
    user_id: UUID
    #email:str
    role: str
