from pymongo import MongoClient
from datetime import datetime



client = MongoClient()
db = client.amlis
collection = db.period

collection.delete_many({})

new_period = [{
    "team": "amlis",
    "year": "2017",
    "month": "8"
},
{
    "team": "amlis",
    "year": "2016",
    "month": "7"
},
{
    "team": "amlis",
    "year": "2017",
    "month": "6"
},
{
    "team": "amlis",
    "year": "2017",
    "month": "5"
}]

result = collection.insert_many(new_period)
result.inserted_ids
