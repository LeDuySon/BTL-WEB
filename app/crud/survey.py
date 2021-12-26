from fastapi.encoders import jsonable_encoder
import pymongo
from pymongo import MongoClient
import datetime
import re

from ..models.location import LocationListInSurvey
from ..models.survey import SurveyForm
from ..core.config import (database_name,
                           user_collection_name,
                           role_collection_name,
                           country_collection_name,
                           city_collection_name,
                           district_collection_name,
                           ward_collection_name,
                           civil_group_collection_name,
                           survey_collection_name)
from .location import get_collection_name_from_location_code


def get_citizens_from_survey_col(code: str, unit: str, db: MongoClient):
    query_field = 'permanent_address.' + unit
    data = db[database_name][survey_collection_name].find(
        {query_field: code}, {'_id': 0})
    return list(data)


def count_number_survey_of_loc(locs: LocationListInSurvey, db: MongoClient):
    if(len(locs.codes) > 0):
        loc_code = locs.codes[0]
        field_name = get_collection_name_from_location_code(loc_code)
        pipeline = [
            {
                '$match': {
                    f'permanent_address.{field_name}': {
                        '$in': locs.codes
                    }
                }
            }, {
                '$group': {
                    '_id': f'$permanent_address.{field_name}',
                    'count': {
                        '$sum': 1
                    }
                }
            }
        ]
        data = db[database_name][survey_collection_name].aggregate(pipeline)
        return list(data)
    return []

def get_citizen_by_username(username: str, unit: str, db: MongoClient):
    query_field = 'permanent_address.' + unit
    data = db[database_name][survey_collection_name].find(
        {query_field: username}, {'_id': 0})
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
                            }, 31536000000  # year
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
            bins_idx = bins["_id"] // 10
            bins_range = f"{age_bins[bins_idx - 1]} - {age_bins[bins_idx]}"
            data_formatted.append({
                bins_range: bins["count"]
            })

        return data_formatted
    return []


def retrieve_doc_in_survey(keyword: str, loc_code: str, db: MongoClient):
    """Get people in survey by name (keyword)"""
    field_name = get_collection_name_from_location_code(loc_code)
    match_phase = None
    keyword_len = len(keyword.split(" "))
    keyword_len = keyword_len if keyword_len <= 3 else 3
    if(field_name == "country"):
        match_phase = {
            '$match': {
                '$text': {
                    '$search': keyword
                }
            }
        }
    else:
        match_phase = {
            '$match': {
                f'permanent_address.{field_name}': loc_code,
                '$text': {
                    '$search': keyword
                }
            }
        }

    pipeline = [
        match_phase, {
            '$project': {
                'identity_number': 1,
                'fullname': 1,
                'score': {
                    '$meta': 'textScore'
                },
                '_id': 0
            }
        }, {
            '$match': {
                'score': {
                    '$gt': (0.3 * keyword_len)
                }
            }
        }, {
            '$sort': {
                'score': {
                    '$meta': 'textScore'
                }
            }
        }
    ]

    data = db[database_name][survey_collection_name].aggregate(pipeline)
    data = [d["identity_number"] for d in list(data)]
    return list(data)


# def transform_data(data, db):
#     hometown = db[database_name][city_collection_name].find_one(
#         {'name': data['hometown']})['code']

#     p_city = db[database_name][city_collection_name].find_one(
#         {'name': data['permanent_address']['city']})['code']
#     p_district = db[database_name][district_collection_name].find_one(
#         {'name': data['permanent_address']['district']})['code']

#     p_ward = db[database_name][ward_collection_name].find_one(
#         {'name': data['permanent_address']['ward']})['code']
#     p_civil_group = db[database_name][civil_group_collection_name].find_one(
#         {'name': data['permanent_address']['civil_group']})['code']

#     t_city = db[database_name][city_collection_name].find_one(
#         {'name': data['temporary_address']['city']})['code']
#     t_district = db[database_name][district_collection_name].find_one(
#         {'name': data['temporary_address']['district']})['code']
#     t_ward = db[database_name][ward_collection_name].find_one(
#         {'name': data['temporary_address']['ward']})['code']
#     t_civil_group = db[database_name][civil_group_collection_name].find_one(
#         {'name': data['temporary_address']['civil_group']})['code']

#     trans_data = {
#         'identity_number': data['identity_number'],
#         'fullname': data['fullname'],
#         'birthday': data['dob'],
#         'gender': data['gender'],
#         'hometown': hometown,
#         'permanent_address': {
#             'city': p_city,
#             'district': p_district,
#             'ward': p_ward,
#             'civil_group': p_civil_group,
#             'home_address': data['permanent_address']['home_address'] + ', ' + data['permanent_address']['ward'] + ', ' + data['permanent_address']['district'] + ', ' + data['permanent_address']['city']
#         },
#         'temporary_address': {
#             'city': t_city,
#             'district': t_district,
#             'ward': t_ward,
#             'civil_group': t_civil_group,
#             'home_address': data['temporary_address']['home_address'] + ', ' + data['temporary_address']['ward'] + ', ' + data['temporary_address']['district'] + ', ' + data['temporary_address']['city']
#         },
#         'religion': data['religion'],
#         'job': data['job'],
#         'edu_level': data['edu_level'],
#         'createAt': data['createAt']
#     }

#     return trans_data


def insert_data_into_col(data: SurveyForm, db: MongoClient):
    data_json = jsonable_encoder(data)
    id_num = db[database_name][survey_collection_name].find_one(
        {'identity_number': data_json['identity_number']})
    if id_num:
        return 'id number has already existed'

    dob = data_json['dob']
    check_dob = re.search("^([1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])(\.|-|/)([1-9]|0[1-9]|1[0-2])(\.|-|/)([0-9][0-9]|19[0-9][0-9]|20[0-9][0-9])$|^([0-9][0-9]|19[0-9][0-9]|20[0-9][0-9])(\.|-|/)([1-9]|0[1-9]|1[0-2])(\.|-|/)([1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])$", dob)
    if check_dob is None:
        return 'invalid date of birth'

    hometown = db[database_name][city_collection_name].find_one(
        {'code': data_json['hometown']})
    if hometown is None:
        return 'hometown not exist'

    try:
        db[database_name][survey_collection_name].insert_one(data_json)
    except pymongo.errors.DuplicateKeyError:
        return False
    return True
