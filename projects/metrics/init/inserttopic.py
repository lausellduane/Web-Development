from pymongo import MongoClient
from datetime import datetime



client = MongoClient()
db = client.amlis
collection = db.topic

collection.delete_many({})

new_topic = [{
    "TOPIC": "s"
},
{
    "TOPIC": "q"
},
{
    "TOPIC": "d"
},
{
    "TOPIC": "i"
},
{
    "TOPIC": "p"
}]

result = collection.insert_many(new_topic)
result.inserted_ids
