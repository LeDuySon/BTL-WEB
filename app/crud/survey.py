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
                           civil_group_collection_name,
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


def transform_data(data, db):
    hometown = db[database_name][city_collection_name].find_one(
        {'name': data['hometown']})['code']

    p_city = db[database_name][city_collection_name].find_one(
        {'name': data['permanent_address']['city']})['code']
    p_district = db[database_name][district_collection_name].find_one({'name': data['permanent_address']['district']})['code']
    
    p_ward = db[database_name][ward_collection_name].find_one(
        {'name': data['permanent_address']['ward']})['code']
    p_civil_group = db[database_name][civil_group_collection_name].find_one(
        {'name': data['permanent_address']['civil_group']})['code']

    t_city = db[database_name][city_collection_name].find_one(
        {'name': data['temporary_address']['city']})['code']
    t_district = db[database_name][district_collection_name].find_one(
        {'name': data['temporary_address']['district']})['code']
    t_ward = db[database_name][ward_collection_name].find_one(
        {'name': data['temporary_address']['ward']})['code']
    t_civil_group = db[database_name][civil_group_collection_name].find_one(
        {'name': data['temporary_address']['civil_group']})['code']

    trans_data = {
        'identity_number': data['identity_number'],
        'fullname': data['fullname'],
        'birthday': data['dob'],
        'gender': data['gender'],
        'hometown': hometown,
        'permanent_address': {
            'city': p_city,
            'district': p_district,
            'ward': p_ward,
            'civil_group': p_civil_group,
            'home_address': data['permanent_address']['home_address'] + ', ' + data['permanent_address']['ward'] + ', ' + data['permanent_address']['district'] + ', ' + data['permanent_address']['city']
        },
        'temporary_address': {
            'city': t_city,
            'district': t_district,
            'ward': t_ward,
            'civil_group': t_civil_group,
            'home_address': data['temporary_address']['home_address'] + ', ' + data['temporary_address']['ward'] + ', ' + data['temporary_address']['district'] + ', ' + data['temporary_address']['city']
        },
        'religion': data['religion'],
        'job': data['job'],
        'edu_level': data['edu_level'],
        'createAt': data['createAt']
    }

    return trans_data


def insert_data_into_col(data: SurveyForm, db: MongoClient):
    data_json = jsonable_encoder(data)
    id_num = data_json['identity_number']

    if db[database_name][survey_collection_name].find_one({'identity_number': id_num}):
        return False

    trans_data = transform_data(data_json, db)

    try:
        db[database_name][survey_collection_name].insert_one(trans_data)
    except pymongo.errors.DuplicateKeyError:
        return False
    return True
