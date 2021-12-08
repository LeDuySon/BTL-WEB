import logging

from pymongo import MongoClient
from ..core.config import MONGODB_URI
from .mongodb import db

def connect_to_mongo():
    logging.info("Connecting to database.....")
    db.client = MongoClient(str(MONGODB_URI))
    logging.info("Connected to database!")

def close_mongo_connection():
    logging.info("Closing database.....")
    db.client.close()
    logging.info("Closed database!")