from pymongo import MongoClient
import os

def get_mongo_connection():
    mongo_uri = os.environ.get('MONGO_URI', "mongodb+srv://laimizh:1Sr9BD6OuCRpA1ay@cluster0.pgjxqmw.mongodb.net/")
    client = MongoClient(mongo_uri)
    db = client["data_warehouse"]
    return db
