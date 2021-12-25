from fastapi.encoders import jsonable_encoder
from pymongo import MongoClient
import pymongo

from app.models.survey import SurveyForm
from ..core.config import (database_name,
                           user_collection_name,
                           role_collection_name,
                           country_collection_name,
                           city_collection_name,
                           district_collection_name,
                           ward_collection_name,
                           survey_collection_name)


def get_citizens_from_survey_col(code: str, unit: str, db: MongoClient):
    query_field = 'permanent_address.' + unit
    data = db[database_name][survey_collection_name].find(
        {query_field: code}, {'_id': 0})
    return list(data)


def get_citizen_by_identidy_number(id_number: str, db: MongoClient):
    data = db[database_name][survey_collection_name].find_one(
        {"identity_number": id_number}, {'_id': 0})
    return data


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
