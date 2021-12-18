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
    createAt: datetime.datetime

class UserInDelete(BaseModel):
    username: str
    
class UserInAuthorize(BaseModel):
    username: str 
    start_time: str
    end_time: str
    
class UserState(BaseModel):
    username: str 
    is_active: bool
