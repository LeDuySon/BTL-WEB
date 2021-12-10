from pymongo import MongoClient
from odmantic import ObjectId

from fastapi.encoders import jsonable_encoder

from .location import (get_collection_name_from_location_code,
                       retrieve_location_info_by_code,
                       get_collection_field,
                       get_all_childs_of_location)
from ..models.user import UserInLogin, User, UserInCreate
from ..core.config import (database_name,
                           user_collection_name,
                           role_collection_name,
                           country_collection_name,
                           city_collection_name,
                           district_collection_name,
                           ward_collection_name)
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
    user_datas = list(data)
    if(len(user_datas) > 0):
        user_data = user_datas[0]
        user_data["id"] = user_data.pop("_id")
        return User(**user_data)

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

def get_child_user_from_user_id(id: ObjectId, db: MongoClient):
    data = db[database_name][user_collection_name].find({"manager_id": id}, {"manage_location": 1})
    return list(data)

def get_management_info_by_username(username: str, db: MongoClient):
    """Get locations and users which is managed by the given username"""
    
    # get data for query
    user = get_user_by_username(username, db)
    query_collection = get_collection_name_from_location_code(user.manage_location)
    location_info = retrieve_location_info_by_code(user.manage_location, query_collection, db)
    sub_collection = get_collection_field(location_info)
    # query info
    child_locations = get_all_childs_of_location(user.manage_location, query_collection, sub_collection, db)
    child_users = get_child_user_from_user_id(user.id, db)
    
    location_has_manager = [k["manage_location"] for k in child_users]
    for obj in child_locations:
        if(obj["code"] in location_has_manager):
            obj["user_name"] = obj["code"] 
        else:
            obj["user_name"] = None
            
        del obj["district"]
        del obj["_id"]
            
    return child_locations
  
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
    