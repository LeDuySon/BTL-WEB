from fastapi import APIRouter


router = APIRouter()


@router.get("/", tags=["Home"])
def home():
    return "Hello, world!"
