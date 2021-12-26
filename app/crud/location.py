from pymongo import MongoClient
from typing import List
from odmantic import ObjectId

from ..core.config import (database_name,
                           country_collection_name,
                           city_collection_name,
                           district_collection_name,
                           ward_collection_name)
from ..models.location import LocationInUpdateCode, LocationInCreate
from ..models.user import User


def get_all_city(db: MongoClient) -> List[dict]:
    """Get all cities name and code from city collection"""
    data = db[database_name][city_collection_name].find(
        {}, {"name": 1, "code": 1, "_id": 0})
    return list(data)


def retrieve_location_info_by_code(code: str, collection_name: str, db: MongoClient) -> dict:
    """Get location info by CODE from collection name"""
    data = db[database_name][collection_name].find({"code": code})
    data = list(data)
    if(len(data) > 0):
        return data[0]


def get_all_childs_of_location(
        location_code: str,
        query_collection: str,
        sub_collection: str,
        db: MongoClient):
    """Get all locations which is a child of the given location code"""
    pipeline = [
        {
            '$match': {
                'code': location_code
            }
        }, {
            '$unwind': {
                'path': f'${sub_collection}'
            }
        }, {
            '$lookup': {
                'from': sub_collection,
                'localField': sub_collection,
                'foreignField': '_id',
                'as': 'info'
            }
        }, {
            '$project': {
                'info': {
                    '$first': '$info'
                },
                '_id': 0
            }
        }, {
            '$project': {
                'code': '$info.code',
                'name': '$info.name'
            }
        }
    ]

    data = db[database_name][query_collection].aggregate(pipeline)
    data = list(data)
    print(len(data))
    if(len(data[0].keys()) > 0):
        return data
    return []

def get_all_childs_from_code(
        loc_code: str,
        db: MongoClient):
    """Get all locations which is a child of the given location code"""
    sub_collection = get_loc_name_from_parent_code(loc_code, db)
    query_collection = get_collection_name_from_location_code(loc_code)
    pipeline = [
        {
            '$match': {
                'code': loc_code
            }
        }, {
            '$unwind': {
                'path': f'${sub_collection}'
            }
        }, {
            '$lookup': {
                'from': sub_collection,
                'localField': sub_collection,
                'foreignField': '_id',
                'as': 'info'
            }
        }, {
            '$project': {
                'info': {
                    '$first': '$info'
                },
                '_id': 0
            }
        }, {
            '$project': {
                'code': '$info.code',
                'name': '$info.name'
            }
        }
    ]

    data = db[database_name][query_collection].aggregate(pipeline)
    data = list(data)
    if(len(data) > 0):
        if(len(data[0].keys()) > 0):
            return data
    return []

def is_location_exists(parents_code: str, location: LocationInCreate, db: MongoClient):
    """True if exists else False"""
    query = None 
    if(location.code is not None):
        query = {"code": location.code}
    else:
        query = {"name": location.name}
        
    query_collection = get_loc_name_from_parent_code(parents_code, db)
    results = db[database_name][query_collection].find(query)
    
    if(results.count() == 0):
        return False 
    return True
    
def create_new_location(user: User, location: LocationInCreate, db: MongoClient):
    query_collection = get_loc_name_from_parent_code(user.manage_location, db)
    insert_dict = {
        "name": location.name,
        "code": location.code, 
        "parents_code": user.manage_location,
    }
    
    results = db[database_name][query_collection].insert_one(insert_dict)
    # append new location to parent location list childs
    append_child_location(user.manage_location, results.inserted_id, db)
    
def update_code_of_location(user: User, location: LocationInUpdateCode, db: MongoClient):
    query_collection = get_collection_name_from_location_code(location.code)
    data = db[database_name][query_collection].find({"code": location.code})
    data = list(data)
    if(len(data) == 0):
        db[database_name][query_collection].update_one({
            "name": location.name, "parents_code": user.manage_location
        },
            {
            "$set": {"code": location.code}
        })
        return True
    return False

def append_child_location(loc_code: str, object_id: str, db: MongoClient):
    query_collection = get_collection_name_from_code_length(len(loc_code))
    target_field = get_loc_name_from_parent_code(loc_code, db)
    
    target_doc = {"code": loc_code}
    update_field = {'$push': {target_field: object_id}}
    db[database_name][query_collection].find_one_and_update(target_doc, update_field, upsert=True)

"""
Utils for location
"""

def get_collection_name_from_code_length(code_length):
    if(code_length == 1):
        collection_name = country_collection_name
    elif(code_length == 2):
        collection_name = city_collection_name
    elif(code_length == 4):
        collection_name = district_collection_name
    elif(code_length == 6):
        collection_name = ward_collection_name
    return collection_name

def get_loc_name_from_parent_code(parent_code: str, db: MongoClient):
    """Get collection name of location managed by this user"""
    plus_length = 1 if len(parent_code) == 1 else 2 
    code_length = len(parent_code) + plus_length
    
    return get_collection_name_from_code_length(code_length)
    
def get_collection_name_from_location_code(code: str) -> str:
    code_length = len(code)
    
    return get_collection_name_from_code_length(code_length)

def get_location_unit_from_location_code(code: str):
    location_unit = None
    code_length = len(code)
    if(code_length == 1):
        location_unit = 'country'
    elif(code_length == 2):
        location_unit = 'city'
    elif(code_length == 4):
        location_unit = 'district'
    elif(code_length == 6):
        location_unit = 'ward'
    return location_unit

def get_collection_field(location_info: dict) -> str:
    """Get the sub collection in location info (country -> city)"""
    exclude_fields = ["_id", "name", "code", "parents_code"]
    for key in location_info.keys():
        if(key not in exclude_fields):
            return key
