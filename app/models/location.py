from pydantic import EmailStr, BaseModel
from typing import Optional, List
from odmantic import ObjectId

class LocationInUpdateCode(BaseModel):
    name: str 
    code: str 
    
class LocationInCreate(BaseModel):
    name: str 
    code: Optional[str] = None
    parents_code: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Hải Phòng",
                "code": "69",
            }
        }
        
class LocationListInSurvey(BaseModel):
    codes: List[str]
    
    class Config:
        schema_extra = {
            "example": {
                "codes": ["01", "02", "03"],
            }
        }
    
