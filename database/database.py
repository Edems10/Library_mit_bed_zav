import pymongo
import datetime
import os


API_KEY = os.path.join(os.path.dirname(__file__),'api_key.txt')
with open(API_KEY) as f:
    secret = f.read()
client = pymongo.MongoClient(secret)
#db = client.test

print(client.list_database_names())

#db = client.test

#print(db.list_collection_names())

#todo = {}