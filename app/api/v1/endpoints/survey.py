from fastapi import APIRouter, Depends
from pymongo import MongoClient
from ....models.auth import AuthToken

from ....db.mongodb import get_database
from ....core.jwt import validate_token
from app.crud.location import get_location_unit_from_location_code
from app.crud.survey import get_citizen_by_identidy_number, get_citizens_from_survey_col

router = APIRouter()

@router.get('/user/survey/location/citizens', tags=["Survey"])
def get_citizens_from_location_code(
    code: str,
    db: MongoClient = Depends(get_database),
    auth: AuthToken = Depends(validate_token)
):
    """List all citizens of a given location code"""
    location_unit = get_location_unit_from_location_code(code)
    data = get_citizens_from_survey_col(code, location_unit, db)

    return {
        "success": True,
        "messages": {
            "data": data
        }
    }


@router.get('/user/survey/citizen-by-id-number', tags=["Survey"])
def get_citizen_by_id_number(
    id_number: str,
    db: MongoClient = Depends(get_database),
    auth: AuthToken = Depends(validate_token)
):
    """Get one citizen by a given identity number"""
    data = get_citizen_by_identidy_number(id_number, db)

    return {
        "success": True,
        "messages": {
            "data": data
        }
    }
