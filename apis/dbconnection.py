from pymongo import MongoClient
import os

def connect_to_mongo():
    client = MongoClient(os.getenv("MONGO_URI"))
    collection = client["portfolio"]["test"]
    return client, collection

