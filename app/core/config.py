from decouple import config

API_V1_STR = "/api/v1"

JWT_TOKEN_PREFIX = "Token"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # one week

PROJECT_NAME = config("PROJECT_NAME")
MONGODB_URI = config("MONGODB_URI")
SECRET_KEY = config("SECRET_KEY")
ALGORITHM = config("ALGORITHM")

database_name = PROJECT_NAME
user_collection_name = "user"
role_collection_name = "role"
city_collection_name = "city"
district_collection_name = "district"
ward_collection_name = "ward"

