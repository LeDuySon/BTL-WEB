from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.v1.api import router as api_router
from .core.config import PROJECT_NAME, API_V1_STR
from .db.mongodb_utils import close_mongo_connection, connect_to_mongo

app = FastAPI(
    title=PROJECT_NAME,
    redoc_url="/redocs"
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.add_event_handler("startup", connect_to_mongo)
app.add_event_handler("shutdown", close_mongo_connection)

app.include_router(api_router, prefix=API_V1_STR)