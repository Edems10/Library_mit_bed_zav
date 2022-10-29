import pymongo
import os
from actions_user import create_account
from dataclasses import dataclass
from dataclasses_json import dataclass_json

from datamodels import Person

LOGIN =Person

API_KEY = os.path.join(os.path.dirname(__file__),'api_key.txt')

def get_mongo_client():
  with open(API_KEY) as f:
    secret = f.read()
  return pymongo.MongoClient(secret)


#TODO run sanity check that all columns exist

mongo_client = get_mongo_client()
create_account(mongo_client,"Thomas","Random",1213,"home","login","12345")
