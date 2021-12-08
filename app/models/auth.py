from pydantic import BaseModel
from typing import Optional

class AuthToken(BaseModel):
    username: str
    role: str 
    token_expire: str