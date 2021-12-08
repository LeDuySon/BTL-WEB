from pymongo import MongoClient

from ..models.user import UserInLogin, User
from ..core.config import database_name, user_collection_name
from ..core.security import verify_password

def authenticate_user(user_login: UserInLogin, db: MongoClient):
    """Check user exists and validate password"""
    user = get_user_by_username(user_login.username, db)
    if(not user):
        return False 
    if(not verify_password(user_login.password, user.password)):
        return False 
    return user
        
def get_user_by_username(username: str, db: MongoClient) -> User: 
    """Get all user info from database by username"""
    data = db[database_name][user_collection_name].find({"username": username})
    user_data = list(data)
    if(len(user_data) > 0):
        return User(**user_data[0])
    