import datetime
from pydantic import EmailStr, BaseModel
from typing import Optional
from odmantic import ObjectId
from bson.timestamp import Timestamp


class User(BaseModel):
    id: ObjectId
    username: str
    email: Optional[EmailStr] = None
    password: str
    manage_location: str
    manager_id: ObjectId
    role: str
    avtConfig: Optional[dict] = {}
    survey_time: Optional[dict] = {}
    is_finish: Optional[bool] = False


class UserInLogin(BaseModel):
    username: str
    password: str
    
class UserInCreate(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    password: str
    manage_location: str
    manager_id: Optional[ObjectId] = None
    role: str
    active: Optional[bool] = False
    createAt: Optional[datetime.datetime] = datetime.datetime.now()
    avtConfig: Optional[dict] = {}
    is_finish: Optional[bool] = False
    
    class Config:
        schema_extra = {
            "example": {
            "username": "lam",
            "email": "lam@example.com",
            "password": "lam",
            "manage_location": "03",
            "role": "A2",
            "active": False,
            "avtConfig": {}
            }
        }

class UserInDelete(BaseModel):
    username: str


class UserInAuthorize(BaseModel):
    username: str
    start_time: str
    end_time: str


class UserState(BaseModel):
    username: str
    is_active: bool
