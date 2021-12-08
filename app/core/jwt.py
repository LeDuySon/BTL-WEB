from fastapi.security import HTTPBearer
from fastapi import Depends, HTTPException
from datetime import datetime, timedelta
from pydantic import ValidationError
from typing import Optional
import jwt

from .config import SECRET_KEY, ALGORITHM
from ..models.auth import AuthToken

access_token_jwt_subject = "access"

auth_method = HTTPBearer(scheme_name="Authentication")

def generate_token(username: str, role: str, expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + timedelta(minutes=expires_delta)
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)  
    
    to_encode = {
        "token_expire": datetime.timestamp(expire), "username": username, "role": role
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def validate_token(http_authorization_credentials=Depends(auth_method)) -> AuthToken:
    try:
        payload = jwt.decode(http_authorization_credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        exp = payload.get('token_expire') 
        if datetime.fromtimestamp(exp) < datetime.now():
            raise HTTPException(status_code=403, detail="Token expired")
        return AuthToken(**payload) 
    except(jwt.PyJWTError, ValidationError):
        raise HTTPException(
            status_code=403,
            detail=f"Could not validate credentials",
        )
