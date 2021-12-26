import datetime
from bson import objectid
from pydantic import EmailStr, BaseModel
from typing import Optional
from odmantic import ObjectId
from bson.timestamp import Timestamp
from pydantic.types import condecimal

class SurveyDeleteCitizen(BaseModel):
    identity_number: str

class SurveyForm(BaseModel):

    class PermanentAddress(BaseModel):
        city: str
        district: str
        ward: str
        civil_group: str
        home_address: str

    class TemporaryAddress(BaseModel):
        city: str
        district: str
        ward: str
        civil_group: str
        home_address: str

    identity_number: str
    fullname: str
    dob: str
    gender: str
    hometown: str
    permanent_address: PermanentAddress
    temporary_address: TemporaryAddress
    religion: str
    job: str
    edu_level: str
    createAt: Optional[datetime.datetime] = datetime.datetime.now()
