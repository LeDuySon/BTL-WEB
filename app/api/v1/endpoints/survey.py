from fastapi import APIRouter, Depends, File
from fastapi.datastructures import UploadFile
from fastapi.exceptions import HTTPException
from pymongo import MongoClient

from app.models.survey import SurveyForm
from ....models.auth import AuthToken

from ....db.mongodb import get_database
from ....core.jwt import validate_token
from app.crud.location import get_location_unit_from_location_code
from app.crud.survey import get_citizen_by_identidy_number, get_citizens_from_survey_col, insert_data_into_col

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


@router.get('/survey/citizen-by-id-number', tags=["Survey"])
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


@router.post('/survey/insert_data_citizen', tags=['Survey'])
def insert_data(
    data: SurveyForm,
    db: MongoClient = Depends(get_database),
    auth: AuthToken = Depends(validate_token)
):
    if not insert_data_into_col(data, db):
        raise HTTPException(
            status_code=409,
            detail="identity number has already existed",
        )

    else:
        return {
            "success": True,
            "messages": {}
        }


# @router.post('/survey/upload_file', tags=['Survey'])
# def upload_file_survey(
#     data_file: UploadFile = File(...),
#     db: MongoClient = Depends(get_database),
#     auth: AuthToken = Depends(validate_token)
# ):
#     return data_file.filename
