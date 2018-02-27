from pymongo import MongoClient
from datetime import datetime



client = MongoClient()
db = client.amlis
collection = db.weeklysum

collection.delete_many({})

new_ws = [{
    "TEAM": "amlis",
    "YEAR": "2017",
    "MONTH": "8",
    "WEEK": "one", #datetime.strptime("2017-08-10", "%Y-%m-%d").isocalendar(),
    "HI_LO": "zero",
    "NOTE": "Zebra Printer Exploded"
},
{
    "TEAM": "amlis",
    "YEAR": "2017",
    "MONTH": "8",
    "WEEK": "one", #datetime.strptime("2017-08-10", "%Y-%m-%d").isocalendar(),
    "HI_LO": "zero",
    "NOTE": "Carlos left crying"
},
{
    "TEAM": "amlis",
    "YEAR": "2017",
    "MONTH": "8",
    "WEEK": "one", #datetime.strptime("2017-08-10", "%Y-%m-%d").isocalendar(),
    "HI_LO": "zero",
    "NOTE": "Jose ran out of diesel"
},
{
    "TEAM": "amlis",
    "YEAR": "2017",
    "MONTH": "8",
    "WEEK": "one", #datetime.strptime("2017-08-10", "%Y-%m-%d").isocalendar(),
    "HI_LO": "one",
    "NOTE": "Free daily gas for everybody!"
},
{
    "TEAM": "amlis",
    "YEAR": "2017",
    "MONTH": "8",
    "WEEK": "one", #datetime.strptime("2017-08-10", "%Y-%m-%d").isocalendar(),
    "HI_LO": "one",
    "NOTE": "Free massage while other makes your laundry"
},
{
    "TEAM": "amlis",
    "YEAR": "2016",
    "MONTH": "7",
    "WEEK": "two",
    "HI_LO": "one",
    "NOTE": "Bonus for next 10 years given in advance"
},
{
    "TEAM": "amlis",
    "YEAR": "2017",
    "MONTH": "8",
    "WEEK": "one",
    "HI_LO": "zero",
    "NOTE": "Supply Chain will go back to DJE execution system"
},
{
    "TEAM": "amlis",
    "YEAR": "2017",
    "MONTH": "8",
    "WEEK": "two",
    "HI_LO": "zero",
    "NOTE": "Unsuccessful Meeting"
},
{
    "TEAM": "amlis",
    "YEAR": "2017",
    "MONTH": "8",
    "WEEK": "three",
    "HI_LO": "zero",
    "NOTE": "Unsuccessful Meeting."
},
{
    "TEAM": "amlis",
    "YEAR": "2017",
    "MONTH": "8",
    "WEEK": "three",
    "HI_LO": "one",
    "NOTE": "Successful Meeting."
},
{
    "TEAM": "amlis",
    "YEAR": "2017",
    "MONTH": "8",
    "WEEK": "four",
    "HI_LO": "one",
    "NOTE": "Successful Meeting."
},
{
    "TEAM": "amlis",
    "YEAR": "2017",
    "MONTH": "8",
    "WEEK": "four",
    "HI_LO": "zero",
    "NOTE": "Unsuccessful Meeting."
},
{
    "TEAM": "amlis",
    "YEAR": "2017",
    "MONTH": "8",
    "WEEK": "five",
    "HI_LO": "zero",
    "NOTE": "Unsuccessful Meeting."
},
{
    "TEAM": "amlis",
    "YEAR": "2017",
    "month": "8",
    "WEEK": "five",
    "HI_LO": "zero",
    "NOTE": "Unsuccessful Meeting."
}]

result = collection.insert_many(new_ws)
result.inserted_ids
