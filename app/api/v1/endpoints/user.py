from fastapi import APIRouter, Body, Depends, Request, HTTPException
from pydantic.networks import EmailStr
from pymongo import MongoClient, message
from uuid import uuid4

from ....core.jwt import validate_token
from ....core.authorization import (validate_role_authorization_on_create,
                                    validate_user_authorization_on_crud_others)
from ....db.mongodb import get_database
from ....models.user import UserInCreate, UserInAuthorize, UserInDelete, UserState
from ....models.auth import AuthToken
from ....crud.user import (create_new_user, delete_user_by_username, get_child_role, get_child_user_survey_time_from_user_id,
                           get_management_info_by_username,
                           get_user_by_username,
                           get_child_user_from_user_id, update_is_finish,
                           update_user_state,
                           update_valid_declare_time)

router = APIRouter()


@router.post("/user/create", tags=["User"])
def create_user(
    user: UserInCreate,
    db: MongoClient = Depends(get_database),
    auth: AuthToken = Depends(validate_token)
):
    if(validate_role_authorization_on_create(auth.role, user.role, db)):
        valid = create_new_user(user, auth.username, db)
        if(not valid):
            raise HTTPException(
                status_code=409,
                detail=f"User {user.username} already existed",
            )
    else:
        raise HTTPException(
            status_code=401,
            detail=f"User is not authorized to create a new user with role {user.role}",
        )
    return {
        "success": True,
        "messages": {}
    }


@router.post("/user/delete", tags=["User"])
def delete_user(
    user: UserInDelete,
    db: MongoClient = Depends(get_database),
    auth: AuthToken = Depends(validate_token)

):
    if(validate_user_authorization_on_crud_others(auth.username, user.username, db)):
        is_success = delete_user_by_username(user, db)
        message = 'Delete user ' + user.username + ' successfully'
    else:
        raise HTTPException(
            status_code=401,
            detail='You don\'t have permission on this user or user not found'
        )
    return {
        "success": is_success,
        "message": message
    }


@router.get("/user/childs/all", tags=["User"])
def get_all_management_childs_all(
    db: MongoClient = Depends(get_database),
    auth: AuthToken = Depends(validate_token)
):
    """List all childs (locations and users) of a given user"""
    data = get_management_info_by_username(auth.username, db)

    return {
        "success": True,
        "messages": {
            "data": data
        }
    }


@router.get("/user/childs/user", tags=["User"])
def get_all_management_childs_user(
    db: MongoClient = Depends(get_database),
    auth: AuthToken = Depends(validate_token)
):
    """List all childs (users) of a given user"""
    user = get_user_by_username(auth.username, db)
    data = get_child_user_from_user_id(user.id, db)

    return {
        "success": True,
        "messages": {
            "data": data
        }
    }


@router.get('/user/childs/role', tags=['User'])
def get_child_role_name(
    db: MongoClient = Depends(get_database),
    auth: AuthToken = Depends(validate_token)
):
    role = auth.role
    child_role_name = get_child_role(role, db)

    if child_role_name:
        return {
            "success": True,
            "messages": {
                "data": child_role_name
            }
        }
    else:
        raise HTTPException(
            status_code=401,
            detail='Cannot find child roles'
        )


@router.get('/user/childs/survey_time', tags=['User'])
def get_child_survey_time(
    db: MongoClient = Depends(get_database),
    auth: AuthToken = Depends(validate_token)
):
    user = get_user_by_username(auth.username, db)
    child_users = get_child_user_survey_time_from_user_id(user.id, db)

    if child_users:
        data = {
            'user': {
                "username": user.username,
                "survey_time": user.survey_time,
                "is_finish": user.is_finish
            },
            'child_users': child_users
        }

        return {
            "success": True,
            "messages": {
                "data": data
            }
        }
    else:
        return {
            "success": True,
            "messages": {
                "data": []
            }
        }


@router.post('/user/finish_task', tags=['User'])
def remark_finishing_task(
    db: MongoClient = Depends(get_database),
    auth: AuthToken = Depends(validate_token)
):
    user = get_user_by_username(auth.username, db)
    res = update_is_finish(user, db)

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


@router.post("/user/childs/authorize/time", tags=["User"])
def authorize_child_user_declare_time(
    user: UserInAuthorize,
    db: MongoClient = Depends(get_database),
    auth: AuthToken = Depends(validate_token)
):
    """Set the start and end time of the right of declaration"""
    if(validate_user_authorization_on_crud_others(auth.username, user.username, db)):
        is_success = update_valid_declare_time(user, db)
        if(is_success):
            return {
                "success": is_success,
                "messages": {},
            }
        else:
            raise HTTPException(
                status_code=409,
                detail='Time range is not valid or you already set this before'
            )
    else:
        raise HTTPException(
            status_code=401,
            detail='You don\'t have permission on this user or user not found'
        )


@router.post("/user/childs/authorize/state", tags=["User"])
def set_child_user_state(
    user: UserState,
    db: MongoClient = Depends(get_database),
    auth: AuthToken = Depends(validate_token)
):
    """
    Activate/deactivate the authorization of child user to create, update, delete survey data.
    If a child user is active/inactive, all their children will be active/inactive too.
    """
    if(validate_user_authorization_on_crud_others(auth.username, user.username, db)):
        is_success = update_user_state(user, db)
        if(is_success):
            return {
                "success": is_success,
                "messages": {},
            }
        else:
            raise HTTPException(
                status_code=409,
                detail='Conflict with user state in database'
            )
    else:
        raise HTTPException(
            status_code=401,
            detail='You don\'t have permission on this user or user not found'
        )
