from fastapi.encoders import jsonable_encoder
import pymongo
from pymongo import MongoClient
import datetime

from ..models.location import LocationListInSurvey
from ..models.survey import SurveyForm
from ..core.config import (database_name,
                           user_collection_name,
                           role_collection_name,
                           country_collection_name,
                           city_collection_name,
                           district_collection_name,
                           ward_collection_name,
                           survey_collection_name)
from .location import get_collection_name_from_location_code


def get_citizens_from_survey_col(code: str, unit: str, db: MongoClient):
    query_field = 'permanent_address.' + unit
    data = db[database_name][survey_collection_name].find(
        {query_field: code}, {'_id': 0})
    return list(data)


def get_citizen_by_identidy_number(id_number: str, db: MongoClient):
    data = db[database_name][survey_collection_name].find_one(
        {"identity_number": id_number}, {'_id': 0})
    return data


def retrieve_number_of_people_per_occupation(location: LocationListInSurvey, db: MongoClient):
    if(len(location.codes) > 0):
        loc_code = location.codes[0]
        field_name = get_collection_name_from_location_code(loc_code)

        pipeline = [
            {
                '$match': {
                    f'permanent_address.{field_name}': {
                        '$in': location.codes
                    }
                }
            }, {
                '$group': {
                    '_id': {
                        'code': f'$permanent_address.{field_name}',
                        'job': '$job'
                    },
                    'count': {
                        '$sum': 1
                    }
                }
            }, {
                '$group': {
                    '_id': '$_id.code',
                    'jobs': {
                        '$push': {
                            'job': '$_id.job',
                            'count': '$count'
                        }
                    }
                }
            }, {
                '$project': {
                    'code': '$_id',
                    '_id': 0,
                    'jobs': 1
                }
            }
        ]
        data = db[database_name][survey_collection_name].aggregate(pipeline)
        
        return list(data)
    return [] 
        
        
def retrieve_age_dist_per_gender(location: LocationListInSurvey, gender: str, db: MongoClient):
    age_bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    
    if(len(location.codes) > 0):
        loc_code = location.codes[0]
        field_name = get_collection_name_from_location_code(loc_code)
        pipeline = [
            {
                '$match': {
                    f'permanent_address.{field_name}': {
                            '$in': location.codes
                        },
                    'gender': gender
                }
            }, {
                '$project': {
                    'birthday': {
                        '$dateFromString': {
                            'dateString': '$birthday', 
                            'format': '%d/%m/%Y'
                        }
                    }
                }
            }, {
                '$project': {
                    'age': {
                        '$divide': [
                            {
                                '$subtract': [
                                    datetime.datetime.now(), '$birthday'
                                ]
                            }, 31536000000 # year
                        ]
                    }, 
                    'gender': 1
                }
            }, {
                '$bucket': {
                    'groupBy': '$age', 
                    'boundaries': age_bins, 
                    'default': 'other', 
                    'output': {
                        'count': {
                            '$sum': 1
                        }
                    }
                }
            }
        ]
        
        data = db[database_name][survey_collection_name].aggregate(pipeline)
        data = list(data)
        
        # post process
        data_formatted = []
        for bins in data:
            bins_idx = bins["_id"] // 10;
            bins_range = f"{age_bins[bins_idx - 1]} - {age_bins[bins_idx]}"
            data_formatted.append({
                bins_range: bins["count"]
            })
            
        return data_formatted
    return []
        
def insert_data_into_col(data: SurveyForm, db: MongoClient):
    data_json = jsonable_encoder(data)
    id_num = data_json['identity_number']
    if db[database_name][survey_collection_name].find_one({'identity_number': id_num}):
        return False
    # return True

    try:
        db[database_name][survey_collection_name].insert_one(data_json)
    except pymongo.errors.DuplicateKeyError:
        return False
    return True