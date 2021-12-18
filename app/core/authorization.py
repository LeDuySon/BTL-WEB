from pymongo import MongoClient

from ..crud.user import get_child_role, get_user_by_username, get_user_id_by_username
from ..crud.location import get_collection_name_from_location_code
from ..core.config import (database_name,
                           user_collection_name,
                           role_collection_name,
                           country_collection_name,
                           city_collection_name,
                           district_collection_name,
                           ward_collection_name)
from ..models.location import LocationInCreate
from ..models.user import User


def validate_role_authorization_on_create(user_role: str, created_role: str,  db: MongoClient):
    """Check if current user is authorized to create new user with specified role"""
    valid_roles = get_child_role(user_role, db)
    return (created_role in valid_roles)


def validate_user_authorization_on_create_location(user: User, location: LocationInCreate, db: MongoClient):
    query_collection = get_collection_name_from_location_code(location.code)
    if(query_collection):
        # check user authorized to create location
        locations = db[database_name][query_collection].find(
            {"name": location.name, "parents_code": user.manage_location})
        if(len(list(locations)) > 0):
            return True
    return False


def validate_user_authorization_on_crud_others(username: str, child_username: str, db: MongoClient):
    """Check user have CRUD authorization on other users"""
    child_user = get_user_by_username(child_username, db)
    if not child_user:
        return False
    user_id = get_user_id_by_username(username, db)

    return (child_user.manager_id == user_id)
