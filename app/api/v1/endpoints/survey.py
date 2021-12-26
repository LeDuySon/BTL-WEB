from fastapi import APIRouter, Depends, File
from fastapi import responses
from fastapi.datastructures import UploadFile
from fastapi.responses import FileResponse
from fastapi.exceptions import HTTPException
from pymongo import MongoClient
from app.crud.user import get_user_by_username
import xlrd
import shutil

from app.models.survey import SurveyForm
from ....models.auth import AuthToken

from ....db.mongodb import get_database
from ....core.jwt import validate_token
from ....crud.location import get_location_unit_from_location_code
from ....crud.survey import (check_user_has_permission_to_delete, get_citizen_by_identidy_number, get_citizen_by_username,
                             get_citizens_from_survey_col,
                             retrieve_number_of_people_per_occupation,
                             retrieve_age_dist_per_gender,
                             insert_data_into_col,
                             retrieve_doc_in_survey)
from ....models.location import LocationListInSurvey

router = APIRouter()


@router.get('/survey/location/citizens', tags=["Survey"])
def get_citizens_from_location_code(
    code: str,
    db: MongoClient = Depends(get_database),
    auth: AuthToken = Depends(validate_token)
):
    """List all citizens of a given location code"""
    location_unit = get_location_unit_from_location_code(code)
    data = get_citizens_from_survey_col(code, location_unit, db)

    if len(data) != 0:
        return {
            "success": True,
            "messages": {
                "data": data
            }
        }
    else:
        raise HTTPException(
            status_code=401,
            detail="not found"
        )


@router.get('/survey/citizens', tags=['Survey'])
def get_citizen_managed_by_username(
    db: MongoClient = Depends(get_database),
    auth: AuthToken = Depends(validate_token)
):

    username = auth.username
    location_unit = get_location_unit_from_location_code(username)
    if location_unit == 'ward' or location_unit == 'civil_group':
        data = get_citizen_by_username(username, location_unit, db)

        if len(data) != 0:
            return {
                "success": True,
                "messages": {
                    "data": data
                }
            }
        else:
            raise HTTPException(
                status_code=401,
                detail="not found"
            )
    else:
        return []


@router.get('/survey/citizen/{id_number}', tags=["Survey"])
def get_citizen_by_id_number(
    id_number: str,
    db: MongoClient = Depends(get_database),
    auth: AuthToken = Depends(validate_token)
):
    """Get one citizen by a given identity number"""
    data = get_citizen_by_identidy_number(id_number, db)

    if data != None:
        return {
            "success": True,
            "messages": {
                "data": data
            }
        }
    else:
        raise HTTPException(
            status_code=401,
            detail="not found"
        )


@router.post('/survey/location/occupation', tags=["Survey"])
def get_number_of_peole_per_occupation(
    location: LocationListInSurvey,
    db: MongoClient = Depends(get_database),
    auth: AuthToken = Depends(validate_token)
):
    """Get number of people in each occupation"""
    data = retrieve_number_of_people_per_occupation(location, db)

    return {
        "success": True,
        "messages": {
            "data": data
        }
    }


@router.post('/survey/location/age-dist', tags=["Survey"])
def get_age_gender_dist_in_loc(
    location: LocationListInSurvey,
    gender: str,
    db: MongoClient = Depends(get_database),
    auth: AuthToken = Depends(validate_token)
):
    """Get number of oeople in each age range (per gender)"""
    if(gender in ["Nam", "Nữ"]):
        data = retrieve_age_dist_per_gender(location, gender, db)

        return {
            "success": True,
            "messages": {
                "data": data
            }
        }
    else:
        raise HTTPException(
            status_code=400,
            detail="Gender not existed"
        )


@router.post('/survey/insert', tags=['Survey'])
def insert_data(
    data: SurveyForm,
    db: MongoClient = Depends(get_database),
    auth: AuthToken = Depends(validate_token)
):
    user = get_user_by_username(auth.username, db)
    if not user.active:
        return {
            "success": False,
            "messages": 'user is not active'
        }

    res = insert_data_into_col(data, db)
    if res == False:
        raise HTTPException(
            status_code=409,
            detail="somthing went wrong",
        )
    elif isinstance(res, str):
        raise HTTPException(
            status_code=409,
            detail=res,
        )
    else:
        return {
            "success": True,
            "messages": {}
        }


@router.post('/survey/citizen/delete', tags=['Survey'])
def delete_one_citizen(
    id_num: str,
    db: MongoClient = Depends(get_database),
    auth: AuthToken = Depends(validate_token)
):
    user = get_user_by_username(auth.username, db)
    if not user.active:
        return {
            "success": False,
            "messages": 'user is not active'
        }

    location_unit = get_location_unit_from_location_code(user.username)
    if location_unit:
        res = check_user_has_permission_to_delete(
            user.username, location_unit, id_num, db)
        if isinstance(res, str):
            raise HTTPException(
                status_code=409,
                detail=res,
            )
        else:
            return {
                "success": True,
                "messages": {}
            }
    else:
        raise HTTPException(
            status_code=409,
            detail='user not have permission',
        )


@router.get('/survey/search/{keyword}', tags=['Survey'])
def search_in_survey_by_keyword(
    keyword: str,
    db: MongoClient = Depends(get_database),
    auth: AuthToken = Depends(validate_token)
):
    user = get_user_by_username(auth.username, db)
    data = retrieve_doc_in_survey(keyword, user.manage_location, db)
    return {
        "success": True,
        "messages": {
            "data": data
        }
    }


@router.post('/survey/upload_file', tags=['Survey'])
async def upload_file_survey(
    file: UploadFile = File(...),
    db: MongoClient = Depends(get_database),
    auth: AuthToken = Depends(validate_token)
):
    user = get_user_by_username(auth.username, db)
    if not user.active:
        return {
            "success": False,
            "messages": 'user is not active'
        }

    with open(f'survey_upload/{file.filename}', 'wb') as buffer:
        shutil.copyfileobj(file.file, buffer)

    # content = await file.read()
    # print(content)
    return file.filename


@router.get('/survey/template/download', response_class=FileResponse, tags=['Survey'])
def get_template(
    db: MongoClient = Depends(get_database),
    auth: AuthToken = Depends(validate_token)
):
    file_path = 'download_template/template.docx'
    return FileResponse(path=file_path, filename='template.docx', media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    # return file_path
