from fastapi import APIRouter, Depends, status, HTTPException
from pymongo import MongoClient

from ....core.config import ACCESS_TOKEN_EXPIRE_MINUTES
from ....core.jwt import generate_token
from ....db.mongodb import get_database
from ....models.user import User, UserInLogin
from ....crud.user import authenticate_user

router = APIRouter()

@router.post("/login", tags=["Authentication"])
def login(user_login: UserInLogin, db: MongoClient = Depends(get_database)):
    user = authenticate_user(user_login, db)
    print(user)
    if(not user):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = generate_token(
        user.username, user.role, ACCESS_TOKEN_EXPIRE_MINUTES
        )
    return {
        "messages": {
            "token": access_token,
            "username": user.username,
            "role": user.role,
            "active": user.active,
            "avtConfig": user.avtConfig,
            "token_type": "bearer"
        },
        "success": True
    }
    
        
