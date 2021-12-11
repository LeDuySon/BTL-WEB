from pydantic import EmailStr, BaseModel
from typing import Optional
from odmantic import ObjectId

class LocationInCreate(BaseModel):
    name: str 
    code: str 
    
