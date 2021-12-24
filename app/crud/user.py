from pymongo import MongoClient
from odmantic import ObjectId
from datetime import datetime, timedelta
from fastapi.encoders import jsonable_encoder

from .location import (get_collection_name_from_location_code,
                       retrieve_location_info_by_code,
                       get_collection_field,
                       get_all_childs_of_location)
from ..models.user import UserInDelete, UserInLogin, User, UserInCreate, UserState, UserInAuthorize
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
    # print(user_datas)
    if(len(user_datas) > 0):
        user_data = user_datas[0]
        user_data["id"] = user_data.pop("_id")
        return User(**user_data)


def get_user_id_by_username(username: str, db: MongoClient):
    """Get only user _id from database by username"""
    data = db[database_name][user_collection_name].find(
        {"username": username}, {"_id": 1})
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
    data = db[database_name][user_collection_name].find(
        {"manager_id": id}, {"_id": 0, "manager_id": 0, "password": 0})
    return list(data)


def get_child_user_survey_time_from_user_id(id: ObjectId, db: MongoClient):
    data = db[database_name][user_collection_name].find(
        {"manager_id": id, "is_finish": False, "survey_time": {"$exists" : True}}, {"username": 1, "survey_time": 1, "is_finish": 1, "_id": 0})
    return list(data)


def get_management_info_by_username(username: str, db: MongoClient):
    """Get locations and users which is managed by the given username"""

    # get data for query
    user = get_user_by_username(username, db)
    query_collection = get_collection_name_from_location_code(
        user.manage_location)
    location_info = retrieve_location_info_by_code(
        user.manage_location, query_collection, db)
    sub_collection = get_collection_field(location_info)
    # query info
    child_locations = get_all_childs_of_location(
        user.manage_location, query_collection, sub_collection, db)
    child_users = get_child_user_from_user_id(user.id, db)
    location_has_manager = [k["manage_location"] for k in child_users]
    for obj in child_locations:
        if(obj["code"] in location_has_manager):
            obj["username"] = obj["code"]
        else:
            obj["username"] = None

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


"""
CRUD UPDATE
"""


def update_user_state(user_state: UserState, db: MongoClient):
    user = get_user_by_username(user_state.username, db)
    child_users = get_child_user_from_user_id(user.id, db)
    names = [u["username"] for u in list(child_users)] + [user.username]
    # update active fields in database
    query = {"username": {"$in": names}}
    newvalues = {"$set": {"active": user_state.is_active}}
    update_results = db[database_name][user_collection_name].update_many(
        query, newvalues)
    if(update_results.modified_count > 0):
        return True
    return False


def update_valid_declare_time(user: UserInAuthorize, db: MongoClient):
    """Update the start and end time of the right of declaration"""

    # check valid UTC time stamp
    current_time = datetime.now()
    # check time start of the day
    check_time = datetime.now() - timedelta(hours=int(current_time.hour))
    print(check_time)
    start_diff = (datetime.fromtimestamp(
        int(user.start_time)) - check_time).total_seconds()
    start_end_diff = (datetime.fromtimestamp(int(user.end_time))
                      - datetime.fromtimestamp(int(user.start_time))).total_seconds()
    if(start_diff <= 0 or start_end_diff < 0):
        return False

    query = {"username": user.username}
    data = {
        "$set": {
            "survey_time": {
                "start_time": user.start_time,
                "end_time": user.end_time
            }
        }
    }
    update_results = db[database_name][user_collection_name].update_many(
        query, data, upsert=True)
    if(update_results.modified_count > 0):
        return True
    return False


"""
CRUD DELETE
"""


def delete_user_by_username(user: UserInDelete, db: MongoClient):
    delete_user = db[database_name][user_collection_name].delete_one(
        {'username': user.username})
    if(not delete_user):
        return False
    else:
        return True
