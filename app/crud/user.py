from pymongo import MongoClient
from bson import ObjectId

from fastapi.encoders import jsonable_encoder

from ..models.user import UserInLogin, User, UserInCreate
from ..core.config import database_name, user_collection_name, role_collection_name
from ..core.security import verify_password, get_password_hash

def authenticate_user(user_login: UserInLogin, db: MongoClient):
    """Check user exists and validate password"""
    user = get_user_by_username(user_login.username, db)
    if(not user):
        return False 
    if(not verify_password(user_login.password, user.password)):
        return False 
    return user

"""
CRUD GET 
"""   

def get_user_by_username(username: str, db: MongoClient) -> User: 
    """Get all user info from database by username"""
    data = db[database_name][user_collection_name].find({"username": username})
    user_data = list(data)
    if(len(user_data) > 0):
        return User(**user_data[0])

def get_user_id_by_username(username: str, db: MongoClient):
    """Get only user _id from database by username"""
    data = db[database_name][user_collection_name].find({"username": username}, {"_id": 1})
    data = list(data)
    if(len(data) > 0):
        return data[0]["_id"]

def get_child_role(role: str, db: MongoClient):
    """Get all child role of a specific role"""
    pipeline = [
        {
            '$match': {
                'role_name': role
            }
        }, {
            '$unwind': {
                'path': '$subordinate'
            }
        }, {
            '$lookup': {
                'from': 'role', 
                'localField': 'subordinate', 
                'foreignField': '_id', 
                'as': 'child_rolename'
            }
        }, {
            '$project': {
                'role_name': {
                    '$first': '$child_rolename.role_name'
                }, 
                '_id': 0
            }
        }
    ]
    
    data = db[database_name][role_collection_name].aggregate(pipeline)
    roles = [x["role_name"] for x in list(data)]
    return roles

"""
CRUD CREATE
"""

def create_new_user(user: UserInCreate, manager_name: str, db: MongoClient):
    """Create new user and insert into database"""
    manager_id = get_user_id_by_username(manager_name, db) 
    user.password = get_password_hash(user.password) 
    user_json = jsonable_encoder(user)
    user_json["manager_id"] = manager_id
    # insert into database
    db[database_name][user_collection_name].insert_one(user_json)
    