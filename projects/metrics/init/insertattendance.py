from pymongo import MongoClient
from datetime import datetime



client = MongoClient()
db = client.amlis
collection = db.attendance

collection.delete_many({})

new_attendance = [
#Safety
{ "TEAM": "amlis", "YEAR": "2017", "MONTH": "8", "STAFF": "Carlos A.", "W1A": "green", "W1B": "red",
    "W2A": "green",   "W2B": "white",  "W3A": "white", "W3B": "white", "W4A": "white",  "W4B": "white",
    "W5A": "white", "W5B": "white"},
{ "TEAM": "amlis", "YEAR": "2017", "MONTH": "8", "STAFF": "Alexis",    "W1A": "blue",  "W1B": "green",
    "W2A": "green",   "W2B": "white",  "W3A": "white", "W3B": "white", "W4A": "white",  "W4B": "white",
    "W5A": "white", "W5B": "white"},
{ "TEAM": "amlis", "YEAR": "2017", "MONTH": "8", "STAFF": "Otto",      "W1A": "green", "W1B": "green",
    "W2A": "green",   "W2B": "white",  "W3A": "white", "W3B": "white", "W4A": "white",  "W4B": "white",
    "W5A": "white", "W5B": "white"},
{ "TEAM": "amlis", "YEAR": "2017", "MONTH": "8", "STAFF": "Burgos",    "W1A": "red",   "W1B": "red",
    "W2A": "blue",    "W2B": "white",  "W3A": "white", "W3B": "white", "W4A": "white",  "W4B": "white",
    "W5A": "white", "W5B": "white"},
{ "TEAM": "amlis", "YEAR": "2017", "MONTH": "8", "STAFF": "Victor",    "W1A": "green", "W1B": "green",
    "W2A": "green",   "W2B": "white",  "W3A": "white", "W3B": "white", "W4A": "white",  "W4B": "white",
    "W5A": "white", "W5B": "white"},

]

result = collection.insert_many(new_attendance)
result.inserted_ids
