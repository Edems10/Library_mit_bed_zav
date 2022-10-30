import pymongo
import os

from torch import true_divide
from actions import *
from dataclasses import dataclass
from dataclasses_json import dataclass_json

from datamodels import Person,Roles


API_KEY = os.path.join(os.path.dirname(__file__),'api_key.env')

def get_mongo_client():
  with open(API_KEY) as f:
    secret = f.read()
  return pymongo.MongoClient(secret)


#TODO run sanity check that all columns exist
mongo_client = get_mongo_client()
print(create_account(mongo_client,"librarian","librarian",1213,"home","login_lib","lib_12345"))
login_result = login(mongo_client,"login_lib","lib_12345")


if login_result[0] == True:
  user = login_result[1]
  if user.role == Roles.Librarian.name:
    current_user = Librarian(user)
    print(current_user.add_book(mongo_client,"How to train a dragon 3", "Cressida Cowell", 231, 2003, "dragon",2, "fantasy",
                          "description",0))
    print(current_user.find_book(mongo_client,"How to train a dragon 2"))
    current_user.delete_book(mongo_client,"How to train a dragon 3")

  else:
    current_user = User(user)
else:
  print(login_result[1])