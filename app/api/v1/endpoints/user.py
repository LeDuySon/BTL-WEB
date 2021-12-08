from fastapi import APIRouter, Body, Depends, Request, HTTPException
from pydantic.networks import EmailStr
from pymongo import MongoClient 
from uuid import uuid4

from ....core.jwt import validate_token
from ....core.authorization import validate_role_authorization_on_create
from ....db.mongodb import get_database
from ....models.user import User, UserInLogin, UserInCreate
from ....models.auth import AuthToken
from ....crud.user import create_new_user

router = APIRouter()

@router.post("/user/create", tags=["User"])
def create_user(
    user: UserInCreate,
    db: MongoClient = Depends(get_database),
    auth: AuthToken = Depends(validate_token)
    ):
    if(validate_role_authorization_on_create(auth.role, user.role, db)):
        create_new_user(user, auth.username, db)
    else:
        raise HTTPException(
            status_code=401,
            detail=f"User is not authorized to create a new user with role {user.role}",
        )
    
    return {
        "success": True,
        "messages": {}
    }
    


