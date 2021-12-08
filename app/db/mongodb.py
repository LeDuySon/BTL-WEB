from pymongo import MongoClient

class DataBase:
    client: MongoClient = None

db = DataBase()

def get_database() -> MongoClient:
    return db.client
