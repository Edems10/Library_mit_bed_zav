import pymongo
import os
from bson.objectid import ObjectId
from torch import true_divide
from actions import *
from dataclasses import dataclass
from dataclasses_json import dataclass_json

from datamodels import Autocomplete_options_book, Autocomplete_options_user, Person, Roles

API_KEY = os.path.join(os.path.dirname(__file__), 'api_key.env')
IMAGES_DIR = os.path.join(os.path.dirname(__file__),'Book_img')

def get_mongo_client():
    with open(API_KEY) as f:
        secret = f.read()
    return pymongo.MongoClient(secret)


# TODO run sanity check that all columns exist
mongo_client = get_mongo_client()
# print(create_account(mongo_client,"librarian","librarian",1213,"home","login_lib","lib_12345"))
# LOGIN LIBRARIAN
login_result = login(mongo_client,"login_lib","lib_12345")
# LOGIN FOR USER
# create_account(mongo_client,"first_name","surname",123456789,"address","login","password")
# create_account(mongo_client,"ssdafirst_name","surname",123456789,"address","sasddalogin","password")
#create_account(mongo_client, "ssdafirst_name", "surname", 123456789, "address", "sasddalogin", "password")
#create_account(mongo_client, "aaaa", "surnamea", 123456723132, "addresss", "Domi", "password")
#create_account(mongo_client, "aa", "surname", 123456723132, "addresss", "Dom", "password")
#create_account(mongo_client, "aa", "surname", 123456723132, "addresss", "Dom2", "password")

#login_result = login(mongo_client, "sasddalogin", "password")
#login_result = login(mongo_client,"Dom","password")
#login_result = login(mongo_client,"Dom2","password")

if login_result[0]:
    user = login_result[1]
    if user.role == Roles.Librarian.name:
        current_user = Librarian(user)
        #print(current_user.add_book(mongo_client, "No image book", "3bef9919eca266bb9af0248f", 231, 2003, 2,"fantasy", "description", 0))
        # #print(current_user.add_author(mongo_client, "Dominik", "Borec"))
        # print(current_user.admin_create_account(mongo_client, "aa", "surname", 123456723132, "addresss", "Dom3", "password"))
        # print(current_user.find_user(mongo_client, "f2106a1013a07981ba48bfea"))
        # print(current_user.find_whole_user(mongo_client, "f2106a1013a07981ba48bfea"))
        # print(current_user.find_book(mongo_client, "f0eac029e9022e938b0561dd"))
        # print(current_user.edit_author(mongo_client, "4e63ea8abd3b1d2b0c84622d", "Domca", "The King"))
        # print(current_user.find_author(mongo_client, "4e63ea8abd3b1d2b0c84622"))
        # #print(current_user.delete_author(mongo_client, "4e63ea8abd3b1d2b0c84622d"))
        # EXAMPLE GETTING ALL BOOKS AND SAVING ALL IMAGES AS BOOK ID IF THEY DON'T EXIST
        all_books =current_user.find_all_books(mongo_client)
        for book in all_books:
            image_data = book['image']
            if image_data is not None:
                name =book['_id']
                # pridal jsem tam zatim jen jpg museli bychom tam nekde ukladat i ten filetype nebo ho nejak zjistit
                # a taky kdyz jsou files vetsi nez 16MB tak se museji ukladat do chunku a to nechceme
                if not os.path.isfile(os.path.join(IMAGES_DIR,f"{name}.jpg")):
                    with open(os.path.join(IMAGES_DIR,f"{name}.jpg"), "wb") as binary_file:
                        binary_file.write(image_data)
        
        # #print(current_user.delete_book(mongo_client,"63663a15f36f16fe5f225ddd")[1])
        # #print(current_user.edit_book(mongo_client, "f0eac029e9022e938b0561dd", "New book 2", "3bef9919eca266bb9af0248f", 231, 2003, "dragon", 2, "fantasy",
        # #                             "description 2")[1])
        # print(current_user.find_all_books(mongo_client))
        # print(current_user.get_all_users(mongo_client))

        # #user_saved = current_user.find_user(mongo_client, "6361ac3ed731370b853b875a")
        # #id = user_saved['_id']

        #print(current_user.ban_user(mongo_client, "abab3d0d7172399f94acbd11")[1])
        print(current_user.unban_user(mongo_client, "862b3856cd1c7bd15797b58a")[1])
        print(current_user.accept_user_changes(mongo_client, "06a6e72a01f0ffef240466ca")[1])
        #print(current_user.decline_user_changes(mongo_client, "06a6e72a01f0ffef240466ca")[1])
        print(current_user.get_all_users_with_stashed_changes(mongo_client))
        print(current_user.verified_user(mongo_client, "f2106a1013a07981ba48bfea")[1])
        #print(current_user.unverified_user(mongo_client, "862b3856cd1c7bd15797b58a")[1])
        print(user_is_not_banned(mongo_client, "862b3856cd1c7bd15797b58a"))
        print(user_is_verified(mongo_client, "06a6e72a01f0ffef240466ca"))
        print(user_is_approved_by_librarian(mongo_client, "06a6e72a01f0ffef240466ca"))
        #print(current_user.edit_user(mongo_client, "test_of_changes40", "data2", 6543216, "CZ", _id= "06a6e72a01f0ffef240466ca")[1])
        #print(current_user.borrow_book(mongo_client, '6362f102af7f10a4c3ab85f4', "f2106a1013a07981ba48bfea")[1])
        print(get_all_borrowed_books_from_user(mongo_client, "f2106a1013a07981ba48bfea"))
        #print(current_user.return_book(mongo_client, "6362f102af7f10a4c3ab85f4", "f2106a1013a07981ba48bfea")[1])
        #export_to_csv(mongo_client)
        #import_from_csv(mongo_client, "books")

    else:
        current_user = User(user)
        user_current_id = current_user.user.id
        print(current_user.user_find_book(mongo_client, "f0eac029e9022e938b0561dd"))
        print(current_user.edit_user(mongo_client, "test_of_changes1", "data", 24432, "CZ", "Dom2", "password")[1])
        print(current_user.borrow_book(mongo_client, '6362f102af7f10a4c3ab85f4')[1])
        print(get_all_borrowed_books_from_user(mongo_client, user_current_id))
        #print(current_user.return_book(mongo_client, "6362f102af7f10a4c3ab85f4")[1])
        print(autocomplete_book(mongo_client,"train",Autocomplete_options_book.title))
        print(autocomplete_user(mongo_client,"firs",Autocomplete_options_user.first_name, 3))

else:
    print(login_result[1])
