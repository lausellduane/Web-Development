from pymongo import MongoClient
from datetime import datetime



client = MongoClient()
db = client.amlis
collection = db.days

collection.delete_many({})

days = [
#Safety
{ "team": "amlis", "year": int(2017), "month": int(8), "staff": "Carlos A.", "W1A": "green", "W1B": "red",   "W2A": "green",   "W2B": "white",  "W3A": "white", "W3B": "white", "W4A": "white",  "W4B": "white", "W5A": "white", "W4B": "white"},
{ "team": "amlis", "year": int(2017), "month": int(8), "staff": "Alexis",    "W1A": "blue",  "W1B": "green", "W2A": "green",   "W2B": "white",  "W3A": "white", "W3B": "white", "W4A": "white",  "W4B": "white", "W5A": "white", "W4B": "white"},
{ "team": "amlis", "year": int(2017), "month": int(8), "staff": "Otto",      "W1A": "green", "W1B": "green", "W2A": "green",   "W2B": "white",  "W3A": "white", "W3B": "white", "W4A": "white",  "W4B": "white", "W5A": "white", "W4B": "white"},
{ "team": "amlis", "year": int(2017), "month": int(8), "staff": "Burgos",    "W1A": "red",   "W1B": "red",   "W2A": "blue",    "W2B": "white",  "W3A": "white", "W3B": "white", "W4A": "white",  "W4B": "white", "W5A": "white", "W4B": "white"},
{ "team": "amlis", "year": int(2017), "month": int(8), "staff": "Victor",    "W1A": "green", "W1B": "green", "W2A": "green",   "W2B": "white",  "W3A": "white", "W3B": "white", "W4A": "white",  "W4B": "white", "W5A": "white", "W4B": "white"},

]

result = collection.insert_many(days)
result.inserted_ids
