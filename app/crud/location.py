from pymongo import MongoClient
from typing import List

from ..core.config import (database_name,
                           country_collection_name,
                           city_collection_name,
                           district_collection_name,
                           ward_collection_name)

def get_all_city(db: MongoClient) -> List[dict]: 
    """Get all cities name and code from city collection"""
    data = db[database_name][city_collection_name].find({}, {"name": 1, "code": 1, "_id": 0})
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
            "$match": {
                "code": location_code
            }
        },
        {
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
                'info': 1, 
                '_id': 0
            }
        }
    ]
    
    data = db[database_name][query_collection].aggregate(pipeline)
    flatten_data = [k["info"][0] for k in list(data)]
    return flatten_data
    


"""
Utils for location
"""
def get_collection_name_from_location_code(code: str) -> str:
    code_length = len(code) 
    collection_name = ""
    if(code_length == 1):
        collection_name = country_collection_name
    elif(code_length == 2):
        collection_name = city_collection_name
    elif(code_length == 4):
        collection_name = district_collection_name
    elif(code_length == 6):
        collection_name = ward_collection_name
    return collection_name

def get_collection_field(location_info: dict) -> str: 
    """Get the sub collection in location info (country -> city)""" 
    exclude_fields = ["_id", "name", "code"]
    for key in location_info.keys():
        if(key not in exclude_fields):
            return key 
