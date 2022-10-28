import pymongo
import json
import os
from datamodels import Person, Roles
from dataclasses import dataclass
from dataclasses_json import dataclass_json


DATABASE_NAME = 'library'


API_KEY = os.path.join(os.path.dirname(__file__),'api_key.txt')
with open(API_KEY) as f:
    secret = f.read()
mongo_client = pymongo.MongoClient(secret)

# get all databases in to a list
dblist = mongo_client.list_database_names()
if DATABASE_NAME in dblist:
  print("The database exists.")
else:
    # accualy create it if it doesn't exist
    pass
## password needs to be in bytes
password = b"1234"
new_person = Person(first_name="Adam",surname="Mitrenga",pid=123,address="My address :)"
                    ,login_name="adam",password=password,role=Roles.User.name)

new_person.hash_password()
print(new_person.to_dict())

lib_client = mongo_client[DATABASE_NAME]
lib_column = lib_client['user']
x =lib_column.insert_one(new_person.to_dict())