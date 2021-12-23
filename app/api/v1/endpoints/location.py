from fastapi import APIRouter, Depends, status, HTTPException
from pymongo import MongoClient

from ....models.location import LocationInUpdateCode, LocationInCreate
from ....models.auth import AuthToken
from ....db.mongodb import get_database
from ....core.jwt import validate_token
from ....core.authorization import validate_user_authorization_on_update_location
from ....crud.location import (update_code_of_location, 
                               is_location_exists,
                               create_new_location)
from ....crud.user import get_user_by_username

router = APIRouter()

@router.put("/location/update", tags=["Location"])
def update_location_code(
    location: LocationInUpdateCode,
    db: MongoClient = Depends(get_database),
    auth: AuthToken = Depends(validate_token)
    ):
    return_msg = ""
    user = get_user_by_username(auth.username, db)

    if(validate_user_authorization_on_update_location(user, location, db)):
        is_success = update_code_of_location(user, location, db)
        if(is_success):
            return {
                "messages": return_msg,
                "success": True
            }
        else:
            return_msg = "Location code is already existed"
            raise HTTPException(
                status_code=409,
                detail = return_msg
            )
    else:
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User is not authorized to access this location",
            )
    
@router.post("/location/create", tags=["Location"])
def create_location(
    location: LocationInCreate,
    db: MongoClient = Depends(get_database),
    auth: AuthToken = Depends(validate_token)
    ):
    
    user = get_user_by_username(auth.username, db)
    if(not is_location_exists(user.manage_location, location, db)):
        # location not exists
        create_new_location(user, location, db)
    else:
        raise HTTPException(
            status_code=409,
            detail = "Location already existed"
        )
    return {
        "messages": {},
        "success": True
    }
    
    