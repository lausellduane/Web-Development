from pymongo import MongoClient
from datetime import datetime



client = MongoClient()
db = client.amlis
collection = db.period

collection.delete_many({"year": "2018"})
