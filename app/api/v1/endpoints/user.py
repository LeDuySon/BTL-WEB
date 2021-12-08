from fastapi import APIRouter, Body, Depends, Request, HTTPException
from pydantic.networks import EmailStr
from pymongo import MongoClient 
from uuid import uuid4

from ....core.jwt import validate_token
from ....db.mongodb import get_database
from ....models.user import User, UserInLogin, UserInCreate
from ....models.auth import AuthToken

router = APIRouter()

@router.post("/user/create", tags=["User"])
def create_user(
    user: UserInCreate,
    db: MongoClient = Depends(get_database),
    auth: AuthToken = Depends(validate_token)
    ):
    
    
    return user
    


