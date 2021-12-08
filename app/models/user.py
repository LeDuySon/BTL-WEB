from pydantic import EmailStr, BaseModel
from typing import Optional

class User(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    password: str
    manage_location: str
    manager_id: str
    role: str

class UserInLogin(BaseModel):
    username: str
    password: str
    
class UserInCreate(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    password: str
    manage_location: str
    role: str
    
# class UserInUpdate(BaseModel):
#     password: Optional[str] = None
#     firstName: Optional[str] = None
#     lastName: Optional[str] = None
#     gender: Optional[str] = None