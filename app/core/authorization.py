from pymongo import MongoClient
from ..crud.user import get_child_role

def validate_role_authorization_on_create(user_role: str, created_role: str,  db: MongoClient):
    """Check if current user is authorized to create new user with specified role"""
    valid_roles = get_child_role(user_role, db)
    print(valid_roles)
    return (created_role in valid_roles)
    
    