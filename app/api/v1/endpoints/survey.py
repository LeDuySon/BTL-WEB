from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from pymongo import MongoClient
from ....models.auth import AuthToken

from ....db.mongodb import get_database
from ....core.jwt import validate_token
from app.crud.location import get_location_unit_from_location_code
from app.crud.survey import (get_citizen_by_identidy_number,
                             get_citizens_from_survey_col,
                             retrieve_number_of_people_per_occupation,
                             retrieve_age_dist_per_gender)
from app.models.location import LocationListInSurvey

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
