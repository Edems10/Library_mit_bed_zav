import pymongo
import os
from bson.objectid import ObjectId
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
#print(create_account(mongo_client,"librarian","librarian",1213,"home","login_lib","lib_12345"))
#LOGIN LIBRARIAN
#login_result = login(mongo_client,"login_lib","lib_12345")
#LOGIN FOR USER
#create_account(mongo_client,"first_name","surname",123456789,"address","login","password")
create_account(mongo_client,"ssdafirst_name","surname",123456789,"address","sasddalogin","password")
login_result = login(mongo_client,"sdalogin","password")


if login_result[0] == True:
  user = login_result[1]
  if user.role == Roles.Librarian.name:
    current_user = Librarian(user)
    print(current_user.add_book(mongo_client,"How to train a dragon 3", "Cressida Cowell", 231, 2003, "dragon",2, "fantasy",
                          "description",0))
    print(current_user.find_book(mongo_client,"Gladiator"))
    #print(current_user.delete_book(mongo_client,"How to train a dragon 3")[1])
    print(current_user.edit_book(mongo_client,"Gladiator", "Gladiator", "me", 231, 2003, "dragon",2, "fantasy",
                          "description 2",2)[1])
    print(current_user.find_all_books(mongo_client))
    print(current_user.get_all_users(mongo_client))
    user_saved = current_user.find_user(mongo_client, "login111")
    id = user_saved['_id']
    #Still works for librarian
    print(current_user.edit_user(mongo_client, "login111", "Dominik", "IKD", id)[1])

    print(current_user.ban_user(mongo_client,ObjectId('63619fb5b63ff822f52c95b2')))
  else:
    current_user = User(user)
    print(current_user.user._id)
    user_current_id = str(current_user.user._id)
    print(user_current_id)
    print(current_user.user_find_book(mongo_client, "Gladiator"))
    #print(current_user.edit_user(mongo_client, "login111", "Dominik", "IKD", current_user.user._id)[1])
    #FIXME tady je issue ze proste nemame ten _id ulozeny
    print(current_user.edit_user(mongo_client, "login111", "Dominik", "IKD",user_current_id)[1])
    print(current_user.borrow_book(mongo_client,"login111","How to train a dragon")[1])
    print(get_all_borrowed_books_from_user(mongo_client,"login111"))

else:
  print(login_result[1])