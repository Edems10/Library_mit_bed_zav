import codecs
from dataclasses import dataclass
from typing import Tuple, Union
from datetime import datetime
import pandas as pd
from bson.objectid import ObjectId
from datamodels import Autocomplete_options_book, Autocomplete_options_user, Book, Person, Author, Person_changes, \
    Book_status, Roles
import pymongo
import bcrypt
import re
import time
import os
from tkinter.filedialog import askopenfilename
import gridfs
import bson

# DATABASE NAME
DATABASE_NAME = 'library'

# TABLES IN DATABASE
USER = 'user'
BOOK = 'book'
BOOK_STATUS = 'book_status'
USER_CHANGES = 'user_changes'
AUTHOR = 'author'
CURRENT_USER = None


@dataclass
class User:
    user: Person

    def __init__(self, person: Person):
        self.user = person
        # if person.banned == True:
        # TODO there has to be a function that informs the user he is banned
        # self.user = None
        # FIXME for now i commented the part where we set the user as  none if he is banned
        # TODO podobně jako u banned, (toto se musi jeste vyresit)
        # if person.verified == False:
        #    self.user = None

    # check limit=6 and time=6 days
    def borrow_book(self, mongo_client: pymongo.MongoClient, _id, user_id=None) -> Tuple[bool, str]:
        if ObjectId.is_valid(_id):
            if user_exists_id(mongo_client, self.user.id):
                if self.user.role == Roles.Librarian.name:
                    if book_exists_id(mongo_client, _id):
                        if ObjectId.is_valid(user_id):
                            if user_exists_id(mongo_client, user_id):
                                books = get_book_column(mongo_client)
                                query = {"$and": [{"_id": ObjectId(_id)}, {"copies_available": {"$ne": 0}}]}
                                result = books.find_one(query)
                                actual_borrowed_books = get_all_borrowed_books_from_user(mongo_client, user_id)
                                if result is not None:
                                    if _id not in actual_borrowed_books:
                                        if len(actual_borrowed_books) < 6:
                                            new_book = Book_status(book_id=ObjectId(result["_id"]),
                                                                   user_id=ObjectId(user_id),
                                                                   date_borrowed=time.time(),
                                                                   date_returned=None,
                                                                   returned=False)
                                            get_book_status_column(mongo_client).insert_one(new_book.to_dict())
                                            get_user_column(mongo_client).update_one({"_id": ObjectId(user_id)},
                                                                                     {'$inc': {"count_borrowed_books": 1}})
                                            get_book_column(mongo_client).update_one({"_id": ObjectId(_id)},
                                                                                     {'$inc': {"count_borrowed": 1}})
                                            get_book_column(mongo_client).update_one({"_id": ObjectId(_id)},
                                                                                     {'$inc': {"copies_available": -1}})
                                            return True, "Admin just borrowed book to user: " + str(user_id) \
                                                         + " book named: " + str(result["title"]) \
                                                         + ", Book ID: " + str(result["_id"])
                                        else:
                                            return False, "User: " + str(user_id) \
                                                   + " has borrowed the maximum number of books"
                                    else:
                                        return False, "User: " + str(user_id) + " has already borrowed book named: " \
                                               + str(result["title"]) + ", Book ID: " + str(_id)
                                else:
                                    return False, ", Book ID: " + str(_id) \
                                           + " is currently borrowed and has none copies available"
                            else:
                                return False, "There is no user with this ID: " + str(user_id)
                        else:
                            return False, "ID: " + str(user_id) + " is not valid. ID Must be a single string" \
                                                              " of 12 bytes or a string of 24 hex characters"
                    else:
                        return False, "There is no book with ID: " + str(_id)
                else:
                    if user_is_verified(mongo_client, self.user.id):
                        if user_is_approved_by_librarian(mongo_client, self.user.id):
                            if book_exists_id(mongo_client, _id):
                                books = get_book_column(mongo_client)
                                query = {"$and": [{"_id": ObjectId(_id)}, {"copies_available": {"$ne": 0}}]}
                                result = books.find_one(query)
                                actual_borrowed_books = get_all_borrowed_books_from_user(mongo_client, self.user.id)
                                if result is not None:
                                    if _id not in actual_borrowed_books:
                                        if len(actual_borrowed_books) < 6:
                                            new_book = Book_status(book_id=ObjectId(result["_id"]),
                                                                   user_id=ObjectId(self.user.id),
                                                                   date_borrowed=time.time(),
                                                                   date_returned=None,
                                                                   returned=False)
                                            get_book_status_column(mongo_client).insert_one(new_book.to_dict())
                                            get_user_column(mongo_client).update_one({"_id": ObjectId(self.user.id)},
                                                                                     {'$inc':
                                                                                     {"count_borrowed_books": 1}})
                                            get_book_column(mongo_client).update_one({"_id": ObjectId(_id)},
                                                                                     {'$inc': {"count_borrowed": 1}})
                                            get_book_column(mongo_client).update_one({"_id": ObjectId(_id)},
                                                                                     {'$inc': {"copies_available": -1}})
                                            return True, "User: " + str(self.user.id) \
                                                   + " has borrowed book named: " + str(result["title"]) \
                                                   + ", Book ID: " + str(result["_id"])
                                        else:
                                            return False, "User: " + str(self.user.id) \
                                                   + " has borrowed the maximum number of books"
                                    else:
                                        return False, "User: " + str(self.user.id)\
                                               + " has already borrowed book named: " \
                                               + str(result["title"]) + ", Book ID: " + str(_id)
                                else:
                                    return False, ", Book ID: " + str(_id)\
                                           + " is currently borrowed and has none copies available"
                            else:
                                return False, "There is no book with ID: " + str(_id)
                        else:
                            return False, "User: " + str(self.user.id) \
                                   + " is waiting for the approval of personal data changes by the admin!"
                    else:
                        return False, "User: " + str(self.user.id) + " is not verified to borrow a book!"
            else:
                return False, "There is no user with this ID: " + str(self.user.id)
        else:
            return False, "ID: " + str(_id) + " is not valid. ID Must be a single string" \
                                         " of 12 bytes or a string of 24 hex characters"

    def return_book(self, mongo_client: pymongo.MongoClient, _id, user_id=None) -> Tuple[bool, str]:
        if ObjectId.is_valid(_id):
            if user_exists_id(mongo_client, self.user.id):
                if self.user.role == Roles.Librarian.name:
                    if book_exists_id(mongo_client, _id):
                        if ObjectId.is_valid(user_id):
                            if user_exists_id(mongo_client, user_id):
                                actual_borrowed_books = get_all_borrowed_books_from_user(mongo_client, user_id)
                                if _id in actual_borrowed_books:
                                    get_book_status_column(mongo_client).update_one({"$and":
                                                                                    [{"user_id": ObjectId(user_id)},
                                                                 {"book_id": ObjectId(_id)}], "returned": False},
                                                                 {"$set": {"returned": True, "date_returned": time.time()}})
                                    get_user_column(mongo_client).update_one({"_id": ObjectId(user_id)},
                                                                             {'$inc': {"count_borrowed_books": -1}})
                                    get_book_column(mongo_client).update_one({"_id": ObjectId(_id)},
                                                                             {'$inc': {"count_borrowed": -1}})
                                    get_book_column(mongo_client).update_one({"_id": ObjectId(_id)},
                                                                             {'$inc': {"copies_available": 1}})
                                    return True, "Admin just returned book to User: " + str(self.user.id) +\
                                                 ", book ID: " + str(_id)
                                else:
                                    return False, "User: " + str(self.user.id) + " has not borrowed a book with ID: "\
                                           + str(_id)
                            else:
                                return False, "There is no user with this ID: " + str(user_id)
                        else:
                            return False, "ID: " + str(user_id) + " is not valid. ID Must be a single string" \
                                                              " of 12 bytes or a string of 24 hex characters"
                    else:
                        return False, "There is no book with ID: " + str(_id)
                else:
                    if user_is_verified(mongo_client, self.user.id):
                        if user_is_approved_by_librarian(mongo_client, self.user.id):
                            if book_exists_id(mongo_client, _id):
                                actual_borrowed_books = get_all_borrowed_books_from_user(mongo_client, self.user.id)
                                if _id in actual_borrowed_books:
                                    get_book_status_column(mongo_client).update_one({"$and":
                                                                                         [{"user_id": ObjectId(
                                                                                             self.user.id)},
                                                                                          {"book_id": ObjectId(_id)}],
                                                                                     "returned": False},
                                                                                    {"$set": {"returned": True,
                                                                                              "date_returned":
                                                                                                  time.time()}})
                                    get_user_column(mongo_client).update_one({"_id": ObjectId(self.user.id)},
                                                                             {'$inc': {"count_borrowed_books": -1}})
                                    get_book_column(mongo_client).update_one({"_id": ObjectId(_id)},
                                                                             {'$inc': {"count_borrowed": -1}})
                                    get_book_column(mongo_client).update_one({"_id": ObjectId(_id)},
                                                                             {'$inc': {"copies_available": 1}})
                                    return True, "User: " + str(self.user.id) + " has returned a book with ID: "\
                                                 + str(_id)
                                else:
                                    return False, "User: " + str(self.user.id) + " has not borrowed a book with ID: "\
                                                 + str(_id)
                            else:
                                return False, "There is no book with ID: " + str(_id)
                        else:
                            return False, "User: " + str(self.user.id) \
                                   + " is waiting for the approval of personal data changes by the admin!"
                    else:
                        return False, "User: " + str(self.user.id) + " is not verified to return a book!"
            else:
                return False, "There is no user with this ID: " + str(self.user.id)
        else:
            return False, "ID: " + str(_id) + " is not valid. ID Must be a single string" \
                                         " of 12 bytes or a string of 24 hex characters"

    def user_find_book(self, mongo_client: pymongo.MongoClient, _id):
        if ObjectId.is_valid(_id):
            if user_is_verified(mongo_client, self.user.id):
                if user_is_approved_by_librarian(mongo_client, self.user.id):
                    if book_exists_id(mongo_client, _id):
                        books = get_book_column(mongo_client)
                        query = {"_id": ObjectId(_id)}
                        return books.find_one(query, {"_id": 0, "count_borrowed": 0})
                    else:
                        return False, "There is no book with ID: " + str(_id)
                else:
                    return False, "User: " + str(self.user.id) \
                           + " is waiting for the approval of personal data changes by the admin!"
            else:
                return None, "User: " + str(self.user.id) + " is not verified to find a book!"
        else:
            return False, "ID: " + str(_id) + " is not valid. ID Must be a single string" \
                                         " of 12 bytes or a string of 24 hex characters"

    def user_find_author(self, mongo_client: pymongo.MongoClient, name):
        if user_is_verified(mongo_client, self.user.id):
            if user_is_approved_by_librarian(mongo_client, self.user.id):
                authors = get_author_column(mongo_client)
                query = {"first_name": name}
                result = authors.find_one(query, {"_id": 0})
                if result is not None:
                    return result
                else:
                    return False, "There is no author with name: " + str(name)
            else:
                return False, "User: " + str(self.user.id) \
                       + " is waiting for the approval of personal data changes by the admin!"
        else:
            return None, "User: " + str(self.user.id) + " is not verified to find a book!"

    def edit_user(self, mongo_client: pymongo.MongoClient, first_name: str, surname: str, pid: int, address: str,
                  login_name=None, password=None, _id=None) -> Tuple[bool, str]:
        if user_exists_id(mongo_client, self.user.id):
            if self.user.role == Roles.Librarian.name:
                if ObjectId.is_valid(_id):
                    if user_exists_id(mongo_client, _id):
                        query = {"_id": ObjectId(_id)}
                        new_values = {"$set": {"first_name": first_name, "surname": surname, "pid": pid,
                                               "address": address}}
                        get_user_column(mongo_client).update_one(query, new_values)
                        return True, "User: " + str(_id) + " has been updated!"
                    else:
                        return False, "There is no user with _id: " + str(_id)
                else:
                    return False, "ID: " + str(_id) + " is not valid. ID Must be a single string" \
                                                      " of 12 bytes or a string of 24 hex characters"
            else:
                if user_is_verified(mongo_client, self.user.id):
                    if user_is_approved_by_librarian(mongo_client, self.user.id):
                        new_personal_data_changes = Person_changes(person_id=ObjectId(self.user.id),
                                                                   first_name=first_name,
                                                                   surname=surname, pid=pid,
                                                                   address=address, login_name=login_name,
                                                                   password=hash_password(password, self.user.salt),
                                                                   approved_by_librarian=False,
                                                                   created_at=time.time(),
                                                                   approved_or_rejected_at=None)
                        get_user_changes_column(mongo_client).insert_one(new_personal_data_changes.to_dict())
                        new_approved = {"$set": {'approved_by_librarian': False}}
                        get_user_column(mongo_client).update_one({"_id": ObjectId(self.user.id)}, new_approved)
                        return True, "User: " + str(self.user.id) + " has updated his personal data" \
                                     " and waiting for approve from librarian"
                    else:
                        return False, "User: " + str(self.user.id) \
                               + " is waiting for the approval of personal data changes by the admin!"
                else:
                    return False, "User: " + str(self.user.id) + " is not verified to edit a personal data!"
        else:
            return False, "There is no user with _id: " + str(self.user.id)


@dataclass
class Librarian(User):

    def __init__(self, person: Person):
        self.user = person

    user: Person = None

    def ban_user(self, mongo_client: pymongo.MongoClient, _id) -> Tuple[bool, str]:
        if ObjectId.is_valid(_id):
            if user_exists_id(mongo_client, _id):
                user = get_user_column(mongo_client)
                not_banned_user = user.find_one({"$and": [{"_id": ObjectId(_id)}, {"banned": False}]})
                if not_banned_user is not None:
                    query = {"_id": ObjectId(_id)}
                    new_values = {"$set": {"banned": True}}
                    get_user_column(mongo_client).update_one(query, new_values)
                    return True, "User: " + str(_id) + " has been banned!"
                else:
                    return False, "User: " + str(_id) + " is already banned!"
            else:
                return False, "There is no user with _id: " + str(_id)
        else:
            return False, "ID: " + str(_id) + " is not valid. ID Must be a single string" \
                                         " of 12 bytes or a string of 24 hex characters"

    def unban_user(self, mongo_client: pymongo.MongoClient, _id) -> Tuple[bool, str]:
        if ObjectId.is_valid(_id):
            if user_exists_id(mongo_client, _id):
                user = get_user_column(mongo_client)
                banned_user = user.find_one({"$and": [{"_id": ObjectId(_id)}, {"banned": True}]})
                if banned_user is not None:
                    query = {"_id": ObjectId(_id)}
                    new_values = {"$set": {"banned": False}}
                    get_user_column(mongo_client).update_one(query, new_values)
                    return True, "User: " + str(_id) + " is no longer banned!"
                else:
                    return False, "User: " + str(_id) + " is already unbanned!"
            else:
                return False, "There is no user with _id: " + str(_id)
        else:
            return False, "ID: " + str(_id) + " is not valid. ID Must be a single string" \
                                         " of 12 bytes or a string of 24 hex characters"

    def verified_user(self, mongo_client: pymongo.MongoClient, _id) -> Tuple[bool, str]:
        if ObjectId.is_valid(_id):
            if user_exists_id(mongo_client, _id):
                user = get_user_column(mongo_client)
                not_verified_user = user.find_one({"$and": [{"_id": ObjectId(_id)}, {"verified": False}]})
                if not_verified_user is not None:
                    query = {"_id": ObjectId(_id)}
                    new_values = {"$set": {"verified": True}}
                    get_user_column(mongo_client).update_one(query, new_values)
                    return True, "User: " + str(_id) + " has been verified!"
                else:
                    return False, "User: " + str(_id) + " is already verified!"
            else:
                return False, "There is no user with _id: " + str(_id)
        else:
            return False, "ID: " + str(_id) + " is not valid. ID Must be a single string" \
                                         " of 12 bytes or a string of 24 hex characters"

    def unverified_user(self, mongo_client: pymongo.MongoClient, _id) -> Tuple[bool, str]:
        if ObjectId.is_valid(_id):
            if user_exists_id(mongo_client, _id):
                user = get_user_column(mongo_client)
                verified_user = user.find_one({"$and": [{"_id": ObjectId(_id)}, {"verified": True}]})
                if verified_user is not None:
                    query = {"_id": ObjectId(_id)}
                    new_values = {"$set": {"verified": False}}
                    get_user_column(mongo_client).update_one(query, new_values)
                    return True, "User: " + str(_id) + " is no longer verified!"
                else:
                    return False, "User: " + str(_id) + " is already unverified!"
            else:
                return False, "There is no user with _id: " + str(_id)
        else:
            return False, "ID: " + str(_id) + " is not valid. ID Must be a single string" \
                                         " of 12 bytes or a string of 24 hex characters"

    def accept_user_changes(self, mongo_client: pymongo.MongoClient, _id) -> Tuple[bool, str]:
        if ObjectId.is_valid(_id):
            if user_exists_id(mongo_client, _id):
                user_changes = get_user_changes_column(mongo_client)
                user_with_changed_data = user_changes.find_one({"$and": [{"person_id": ObjectId(_id)},
                                                                         {"approved_by_librarian": False},
                                                                         {"approved_or_rejected_at": None}]})
                if user_with_changed_data is not None:
                    get_user_column(mongo_client).update_one({"_id": ObjectId(_id)}, {
                        "$set": {"first_name": user_with_changed_data["first_name"],
                                 "surname": user_with_changed_data["surname"],
                                 "pid": user_with_changed_data["pid"],
                                 "address": user_with_changed_data["address"],
                                 "login_name": user_with_changed_data["login_name"],
                                 "password": user_with_changed_data["password"]}})
                    get_user_column(mongo_client).update_one({"_id": ObjectId(_id)},
                                                             {"$set": {'approved_by_librarian': True}})
                    get_user_changes_column(mongo_client).update_one({"$and": [{"person_id": ObjectId(_id)},
                                                                               {"approved_by_librarian": False},
                                                                               {"approved_or_rejected_at": None}]},
                                                                     {"$set": {'approved_by_librarian': True,
                                                                               'approved_or_rejected_at': time.time()}})

                    return True, "Admin has accepted the personal data changes to the profile of user: " + str(_id)
                else:
                    return False, "User: " + str(_id) + " has no personal data changes to approve by librarian"
            else:
                return False, "There is no user with _id: " + str(_id)
        else:
            return False, "ID: " + str(_id) + " is not valid. ID Must be a single string" \
                                         " of 12 bytes or a string of 24 hex characters"

    def decline_user_changes(self, mongo_client: pymongo.MongoClient, _id) -> Tuple[bool, str]:
        if ObjectId.is_valid(_id):
            if user_exists_id(mongo_client, _id):
                user_changes = get_user_changes_column(mongo_client)
                user_with_changed_data = user_changes.find_one({"$and": [{"person_id": ObjectId(_id)},
                                                                         {"approved_by_librarian": False},
                                                                         {"approved_or_rejected_at": None}]})
                if user_with_changed_data is not None:
                    get_user_column(mongo_client).update_one({"_id": ObjectId(_id)},
                                                             {"$set": {'approved_by_librarian': True}})
                    get_user_changes_column(mongo_client).update_one({"$and": [{"person_id": ObjectId(_id)},
                                                                               {"approved_by_librarian": False},
                                                                               {"approved_or_rejected_at": None}]},
                                                                     {"$set": {'approved_by_librarian': False,
                                                                               'approved_or_rejected_at': time.time()}})
                    return True, "Admin has declines the personal data changes to the profile of user: " + str(_id)
                else:
                    return False, "User: " + str(_id) + " has no personal data changes to approve by librarian"
            else:
                return False, "There is no user with _id: " + str(_id)
        else:
            return False, "ID: " + str(_id) + " is not valid. ID Must be a single string" \
                                         " of 12 bytes or a string of 24 hex characters"

    def get_all_users(self, mongo_client: pymongo.MongoClient):
        users = get_user_column(mongo_client)
        return list(users.find({}, {"_id": 1, "login_name": 1, "first_name": 1, "surname": 1, "borrowed_books": 1,
                                    "count_borrowed_books": 1, "created_at": 1}))

    def find_user(self, mongo_client: pymongo.MongoClient, _id):
        if ObjectId.is_valid(_id):
            if user_exists_id(mongo_client, _id):
                books = []
                db = mongo_client.library
                docs = db.user.aggregate([
                    {"$match": {"_id": ObjectId(_id)}},
                    {
                        "$lookup":
                            {
                                "from": "book_status",
                                "localField": "_id",
                                "foreignField": "user_id",
                                "as": "borrowed_books"
                            }},
                    {
                        "$project": {
                            "borrowed_books._id": 0,
                            "borrowed_books.user_id": 0,
                        }
                    },
                    {
                        "$unset": ["password", "salt"]
                    }
                ])
                for doc in docs:
                    books.append(doc)
                return True, books
            else:
                return False, "There is no user with the ID: " + str(_id)
        else:
            return False, "ID: " + _id + " is not valid. ID Must be a single string" \
                                         " of 12 bytes or a string of 24 hex characters"

    def find_whole_user(self, mongo_client: pymongo.MongoClient, _id):
        if ObjectId.is_valid(_id):
            if user_exists_id(mongo_client, _id):
                books = []
                db = mongo_client.library
                docs = db.book_status.aggregate([
                    {"$match": {"user_id": ObjectId(_id)}},
                    {
                        "$lookup":
                            {
                                "from": "user",
                                "localField": "user_id",
                                "foreignField": "_id",
                                "as": "user"
                            }},
                    {
                        "$project": {
                            "user.password": 0,
                            "user.salt": 0,
                        }
                    },
                    {
                        "$unset": ["_id"]
                    },
                    {
                        "$lookup":
                            {
                                "from": "book",
                                "localField": "book_id",
                                "foreignField": "_id",
                                "as": "book"
                            }
                    },
                ])
                for doc in docs:
                    books.append(doc)
                return True, books
            else:
                return False, "There is no user with the ID: " + str(_id)
        else:
            return False, "ID: " + _id + " is not valid. ID Must be a single string" \
                                         " of 12 bytes or a string of 24 hex characters"

    def get_all_users_with_stashed_changes(self, mongo_client: pymongo.MongoClient):
        users = get_user_column(mongo_client)
        return list(users.find({"approved_by_librarian": False}, {"_id": 1}))

    def add_book(self, mongo_client: pymongo.MongoClient, title: str, author_id, length: int, year: int ,
                 copies_available: int, genre: str, description: str, count_borrowed: int, image = None) -> Tuple[bool, str]:
        generated_id = ObjectId(str(codecs.encode(os.urandom(12), 'hex').decode()))
        if ObjectId.is_valid(author_id):
            if not book_exists_id(mongo_client, generated_id):
                if author_exists_id(mongo_client, author_id):
                    if image is None:
                        filename = askopenfilename(filetypes=[('JPG files', '*.jpg'),
                                                          ('PNG files', '*.png'),
                                                          ('all files', '.*')])
                        if filename != '':
                            with open(filename, 'rb') as f:
                                contents = f.read()
                        else:
                            contents = None
                    new_book = Book(_id=generated_id, title=title, author=ObjectId(author_id), length=length, year=year,
                                    image=contents,copies_available=copies_available, genre=genre,
                                    description=description, count_borrowed=count_borrowed)
                    get_book_column(mongo_client).insert_one(new_book.to_dict())
                    return True, "Book: " + str(title) + " has been added to library"
                else:
                    return False, "There is no author the ID: " + str(author_id)
            else:
                return False, "Book with ID: " + str(generated_id) + " already exists in library"
        else:
            return False, "ID: " + author_id + " is not valid. ID Must be a single string" \
                                         " of 12 bytes or a string of 24 hex characters"

    # can only be done if no books borrowed
    def edit_book(self, mongo_client: pymongo.MongoClient, _id, title: str, author_id, length: int, year: int,
                  copies_available: int, genre: str, description: str,image=None) -> Tuple[bool, str]:
        if ObjectId.is_valid(_id):
            if ObjectId.is_valid(author_id):
                books = get_book_column(mongo_client)
                if book_exists_id(mongo_client, _id):
                    if author_exists_id(mongo_client, author_id):
                        query = {"$and": [{"_id": ObjectId(_id)}, {"count_borrowed": 0}]}
                        result = books.find_one(query)
                        if result is not None:
                            new_values = {
                                "$set": {"title": title, "author": ObjectId(author_id), "length": length, "year": year,
                                         "image": image,
                                         "copies_available": copies_available, "genre": genre,
                                         "description": description}}
                            get_book_column(mongo_client).update_one(query, new_values)
                            return True, "Book with ID: " + str(_id) + " has been modified!"
                        else:
                            return False, "Book with ID: " + str(_id) + " is currently borrowed!"
                    else:
                        return False, "There is no author the ID: " + str(author_id)
                else:
                    return False, "There is no book with the ID: " + str(_id)
            else:
                return False, "ID: " + str(author_id) + " is not valid. ID Must be a single string" \
                                                   " of 12 bytes or a string of 24 hex characters"
        else:
            return False, "ID: " + str(_id) + " is not valid. ID Must be a single string" \
                                         " of 12 bytes or a string of 24 hex characters"

    # can only be done if no books borrowed
    def delete_book(self, mongo_client: pymongo.MongoClient, _id) -> Tuple[bool, str]:
        if ObjectId.is_valid(_id):
            books = get_book_column(mongo_client)
            if book_exists_id(mongo_client, _id):
                query = {"$and": [{"_id": ObjectId(_id)}, {"count_borrowed": 0}]}
                result = books.find_one(query)
                if result is not None:
                    books.delete_one(query)
                    return True, "Book with ID: " + str(_id) + " has been deleted successfully!"
                else:
                    return False, "Book with ID: " + str(_id) + "  is currently borrowed!"
            else:
                return False, "There is no book with the ID: " + str(_id)
        else:
            return False, "ID: " + str(_id) + " is not valid. ID Must be a single string" \
                                         " of 12 bytes or a string of 24 hex characters"

    def admin_create_account(self, mongo_client: pymongo.MongoClient, first_name: str, surname: str, pid: int,
                             address: str, login: str, password: str) -> Tuple[bool, str]:
        if not user_exists(mongo_client, login):
            if re.fullmatch(r'[A-Za-z0-9@#$%^&+=_]{6,}', password):
                generated_id = ObjectId(str(codecs.encode(os.urandom(12), 'hex').decode()))
                new_user = Person(_id=generated_id, first_name=first_name,
                                  surname=surname, pid=pid, address=address,
                                  login_name=login, password=password, role=Roles.User.name,
                                  verified=True, approved_by_librarian=True)
                new_user.hash_password()
                get_user_column(mongo_client).insert_one(new_user.to_dict())
                return True, "Admin has created account with ID: " + str(generated_id)
            else:
                return False, "Password must have at least 6 characters!"
        else:
            return False, "Account: " + str(login) + " already exists"

    # same as in books, if user has no books borrowed
    def delete_user(self, mongo_client: pymongo.MongoClient, _id) -> Tuple[bool, str]:
        if ObjectId.is_valid(_id):
            users = get_user_column(mongo_client)
            if user_exists_id(mongo_client, _id):
                query = {"$and": [{"_id": ObjectId(_id)}, {"count_borrowed_books": 0}]}
                result = users.find_one(query)
                if result is not None:
                    users.delete_one(query)
                    return True, "User with ID: " + str(_id) + " has been deleted successfully!"
                else:
                    return False, "User with ID: " + str(_id) + " has currently borrowed some books!"
            else:
                return False, "There is no user with the ID: " + str(_id)
        else:
            return False, "ID: " + str(_id) + " is not valid. ID Must be a single string" \
                                         " of 12 bytes or a string of 24 hex characters"

    def add_author(self, mongo_client: pymongo.MongoClient, first_name: str, surname: str) -> Tuple[bool, str]:
        generated_id = ObjectId(str(codecs.encode(os.urandom(12), 'hex').decode()))
        if not author_exists_id(mongo_client, generated_id):
            if len(first_name) != 0 and len(surname) != 0:
                new_author = Author(_id=generated_id, first_name=first_name, surname=surname)
                get_author_column(mongo_client).insert_one(new_author.to_dict())
                return True, "Author: " + first_name + " " + surname + " has been added to library"
            else:
                return False, "First name or surname is null"
        else:
            return False, "Author with ID: " + str(generated_id) + " already exists in library"

    def edit_author(self, mongo_client: pymongo.MongoClient, _id, first_name: str, surname: str) -> Tuple[bool, str]:
        if ObjectId.is_valid(_id):
            if author_exists_id(mongo_client, _id):
                query = {"_id": ObjectId(_id)}
                new_values = {"$set": {"first_name": first_name, "surname": surname}}
                get_author_column(mongo_client).update_one(query, new_values)
                return True, "Author with ID: " + str(_id) + " has been modified!"
            else:
                return False, "There is no author the ID: " + str(_id)
        else:
            return False, "ID: " + str(_id) + " is not valid. ID Must be a single string" \
                                         " of 12 bytes or a string of 24 hex characters"

    def find_author(self, mongo_client: pymongo.MongoClient, _id):
        if ObjectId.is_valid(_id):
            authors = get_author_column(mongo_client)
            query = {"_id": ObjectId(_id)}
            result = authors.find_one(query)
            if result is not None:
                return True, result
            else:
                return False, "There is no author with ID: " + str(_id)
        else:
            return False, "ID: " + str(_id) + " is not valid. ID Must be a single string" \
                                         " of 12 bytes or a string of 24 hex characters"

    def delete_author(self, mongo_client: pymongo.MongoClient, _id) -> Tuple[bool, str]:
        if ObjectId.is_valid(_id):
            authors = get_author_column(mongo_client)
            if author_exists_id(mongo_client, _id):
                query = {"_id": ObjectId(_id)}
                authors.delete_one(query)
                return True, "Author with ID: " + str(_id) + " has been deleted successfully!"
            else:
                return False, "There is no author with the ID: " + str(_id)
        else:
            return False, "ID: " + str(_id) + " is not valid. ID Must be a single string" \
                                         " of 12 bytes or a string of 24 hex characters"

    def find_book(self, mongo_client: pymongo.MongoClient, _id) -> Union[Tuple[bool, list], Tuple[bool, str]]:
        if ObjectId.is_valid(_id):
            if book_exists_id(mongo_client, _id):
                books = []
                db = mongo_client.library
                docs = db.book.aggregate([
                    {"$match": {"_id": ObjectId(_id)}},
                    {
                        "$lookup":
                            {
                                "from": "author",
                                "localField": "author",
                                "foreignField": "_id",
                                "as": "author"
                            }},
                    {
                        "$project": {
                            "author._i": 0
                        }
                    }
                ])
                for doc in docs:
                    books.append(doc)
                return True, books
            else:
                return False, "There is no book with the ID: " + str(_id)
        else:
            return False, "ID: " + str(_id) + " is not valid. ID Must be a single string" \
                                         " of 12 bytes or a string of 24 hex characters"

    def find_all_books(self, mongo_client: pymongo.MongoClient):
        books = get_book_column(mongo_client)
        return list(books.find({}, {"_id": 1, "title": 1, "author": 1,"image":1}))


def get_all_borrowed_books_from_user(mongo_client: pymongo.MongoClient, _id):
    if ObjectId.is_valid(_id):
        borrowed_books = []
        db = mongo_client.library
        try:
            cursor = db.book_status.find({"$and": [{"user_id": ObjectId(_id)}, {"returned": False}]})
            for document in cursor:
                borrowed_books.append(str(document['book_id']))
            return borrowed_books
        except KeyError:
            return []
    else:
        return False, "ID: " + str(_id) + " is not valid. ID Must be a single string" \
                                     " of 12 bytes or a string of 24 hex characters"


def get_book_column(mongo_client: pymongo.MongoClient):
    return mongo_client[DATABASE_NAME][BOOK]


def book_exists(mongo_client: pymongo.MongoClient, book_name):
    books = get_book_column(mongo_client)
    query = {"title": book_name}
    cursor = books.find(query)
    for _ in cursor:
        return True
    return False


def book_exists_id(mongo_client: pymongo.MongoClient, _id):
    books = get_book_column(mongo_client)
    cursor = books.find({"_id": ObjectId(_id)})
    for _ in cursor:
        return True
    return False


def book_exists_return(mongo_client: pymongo.MongoClient, book_name):
    books = get_book_column(mongo_client)
    query = {"title": book_name}
    return books.find_one(query)


def get_user_column(mongo_client: pymongo.MongoClient):
    return mongo_client[DATABASE_NAME][USER]


def user_exists_id(mongo_client: pymongo.MongoClient, _id):
    users = get_user_column(mongo_client)
    cursor = users.find({"_id": ObjectId(_id)})
    for _ in cursor:
        return True
    return False


def user_is_not_banned(mongo_client: pymongo.MongoClient, _id):
    users = get_user_column(mongo_client)
    cursor = users.find({"$and": [{"_id": ObjectId(_id)}, {"banned": False}]})
    for _ in cursor:
        return True
    return False


def user_is_verified(mongo_client: pymongo.MongoClient, _id):
    users = get_user_column(mongo_client)
    cursor = users.find({"$and": [{"_id": ObjectId(_id)}, {"verified": True}]})
    for _ in cursor:
        return True
    return False


def user_is_approved_by_librarian(mongo_client: pymongo.MongoClient, _id):
    users = get_user_column(mongo_client)
    cursor = users.find({"$and": [{"_id": ObjectId(_id)}, {"approved_by_librarian": True}]})
    for _ in cursor:
        return True
    return False


def user_exists(mongo_client: pymongo.MongoClient, user_name):
    users = get_user_column(mongo_client)
    cursor = users.find({"login_name": user_name})
    for _ in cursor:
        return True
    return False


def user_exists_return(mongo_client: pymongo.MongoClient, user_name):
    users = get_user_column(mongo_client)
    query = {"login_name": user_name}
    return users.find_one(query)


def get_author_column(mongo_client: pymongo.MongoClient):
    return mongo_client[DATABASE_NAME][AUTHOR]


def author_exists_id(mongo_client: pymongo.MongoClient, _id):
    authors = get_author_column(mongo_client)
    cursor = authors.find({"_id": ObjectId(_id)})
    for _ in cursor:
        return True
    return False


def get_book_status_column(mongo_client: pymongo.MongoClient):
    return mongo_client[DATABASE_NAME][BOOK_STATUS]


def get_user_changes_column(mongo_client: pymongo.MongoClient):
    return mongo_client[DATABASE_NAME][USER_CHANGES]


def export_to_csv(mongo_client: pymongo.MongoClient):
    db = mongo_client.library
    books = pd.DataFrame(list(db.book.find()))
    books = books.drop(['count_borrowed'], axis=1)
    books.to_csv("books.csv", sep=";")
    users = pd.DataFrame(list(db.user.find()))
    users.to_csv("users.csv", sep=";")
    authors = pd.DataFrame(list(db.author.find()))
    authors.to_csv("authors.csv", sep=";")
    borrowed_books = pd.DataFrame(list(db.book_status.find()))
    borrowed_books.to_csv("borrowed_books.csv", sep=";")
    user_changes = pd.DataFrame(list(db.user_changes.find()))
    user_changes.to_csv("user_changes.csv", sep=";")


def import_from_csv(mongo_client: pymongo.MongoClient, file_name):
    db = mongo_client.library
    collection = db.book
    try:
        data = pd.DataFrame(pd.read_csv(file_name + '.csv', sep=";", header=0))
        data = data.to_dict(orient="records")
        for x in range(len(data)):
            if ObjectId.is_valid(data[x]["_id"]):
                new_book = Book(_id=ObjectId(data[x]["_id"]), title=data[x]["title"], author=data[x]["author"],
                                length=data[x]["length"], year=data[x]["year"], image=data[x]["image"],
                                copies_available=data[x]["copies_available"], genre=data[x]["genre"],
                                description=data[x]["description"], count_borrowed=0)
                if not book_exists_id(mongo_client, data[x]["_id"]):
                    collection.insert_one(new_book.to_dict())
                    print("Book: " + data[x]["title"] + ", ID: " + data[x]["_id"]
                          + "  has been added to library from csv file")
                else:
                    query = {"_id": ObjectId(data[x]["_id"])}
                    new_values = {"$set": {"_id": ObjectId(data[x]["_id"]), "title": data[x]["title"],
                                           "author": data[x]["author"], "length": data[x]["length"],
                                           "year": data[x]["year"], "image": data[x]["image"],
                                           "copies_available": data[x]["copies_available"],
                                           "genre": data[x]["genre"], "description": data[x]["description"]}}
                    get_book_column(mongo_client).update_one(query, new_values)
                    print("Book: " + data[x]["title"] + ", ID: " + data[x]["_id"]
                          + " has been updated from csv file")
            else:
                print("ID: " + data[x]["_id"] + " is not valid."
                      " ID Must be a single string of 12 bytes or a string of 24 hex characters")
    except FileNotFoundError:
        print("File: " + file_name + ".csv was not found")


def create_account(mongo_client: pymongo.MongoClient, first_name: str, surname: str, pid: int, address: str, login: str,
                   password: str) -> Tuple[bool, str]:
    """This function Creates account and saves it to mongo db
        the password is already hashed inside this function
    
    Parameters
    ----------
    mongo_client - connection to mongoClient

    user_info - Data that are needed with registartion eg. first_name,....
 
    Returns
    -------
    bool
        True - Registation went without issue
        
        False - The username already exist
    """
    if not user_exists(mongo_client, login):
        # password needs to be saved in bytes
        # byte_password = bytes(password,'UTF-8')
        if re.fullmatch(r'[A-Za-z0-9@#$%^&+=_]{6,}', password):
            generated_id = ObjectId(str(codecs.encode(os.urandom(12), 'hex').decode()))
            new_user = Person(_id=generated_id, first_name=first_name,
                              surname=surname, pid=pid, address=address,
                              login_name=login, password=password, role=Roles.User.name)
            new_user.hash_password()
            get_user_column(mongo_client).insert_one(new_user.to_dict())
            return True, "Account with ID: " + str(generated_id) + " has been created successfully"
        else:
            return False, "Password must have at least 6 characters!"
    else:
        return False, "Account: " + str(login) + " already exists"


def hash_password(password, salt):
    return bcrypt.hashpw(password, salt)


def login(mongo_client: pymongo.MongoClient, login: str, password: str) -> Union[
          Tuple[bool, Person], Tuple[bool, str], bool]:
    user_column = get_user_column(mongo_client)
    if user_exists(mongo_client, login):
        user_exists_return(mongo_client, login)

    query = {"login_name": login}
    user = user_column.find_one(query)

    if user is not None:
        #byte_password = bytes(password, 'UTF-8')
        salt = user['salt']
        if re.fullmatch(r'[A-Za-z0-9@#$%^&+=_]{6,}', password):
            if hash_password(password, salt) == user['password']:
                if user_is_not_banned(mongo_client, user["_id"]):
                    # TODO can be done with =0 borrowed_books but w/e
                    try:
                        CURRENT_USER = Person(
                            login_name=user['login_name'], password=user['password'],
                            _id=user['_id'], first_name=user['first_name'],
                            surname=user['surname'], pid=user['pid'], address=user['address'],
                            salt=user['salt'],
                            count_borrowed_books=user['count_borrowed_books'],
                            banned=user['banned'], approved_by_librarian=user['approved_by_librarian'],
                            role=user['role'], created_at=user['created_at'])
                    except KeyError:
                        CURRENT_USER = Person(
                            login_name=user['login_name'], password=user['password'],
                            _id=ObjectId(user['_id']), first_name=user['first_name'],
                            surname=user['surname'], pid=user['pid'], address=user['address'],
                            salt=user['salt'], count_borrowed_books=user['count_borrowed_books'],
                            banned=user['banned'], approved_by_librarian=user['approved_by_librarian'],
                            role=user['role'], created_at=user['created_at'])
                    return True, CURRENT_USER
                else:
                    return False, "User: " + str(login) + " is banned!"
            else:
                return False, "Incorrect username or password"
        else:
            return False, "Password must have at least 6 characters"
    else:
        return False, "Incorrect username or password"


def autocomplete_book(mongo_client: pymongo.MongoClient, query: str,
                      path: Autocomplete_options_book, limit=10) -> Tuple[bool, list[Book]]:
    """ retuns list of autocompleted query based on what we have in DB
    Args:
        mongo_client (pymongo.MongoClient): mongo client
        query (str): what are you looking for in text
        path (Autocomplete_options_book): |title|author|year|
        limit (int, optional): how many results are you looking for. Defaults to 10.

    Returns:
        dict[specific_result]: list of results can be None
    """
    if len(query) < 3 or len(query) > 15:
        return False, "No result - Query too short"
    results = get_book_column(mongo_client).aggregate([{
        "$search": {
            "index": "autocomplete_book_leftEdge",
            "autocomplete": {
                "query": query,
                "path": path.name
                , "fuzzy": {
                    "maxEdits": 2,
                    "prefixLength": 3
                }
            }
        }
    }, {
        "$limit": limit
    }])

    book_list = []
    for book in results:
        cur_book = Book(_id=book['_id'], title=book['title'], author=book['author'], length=book['length'],
                        year=book['year'], image=book['image'],
                        copies_available=book['copies_available'], genre=book['genre'],
                        description=book['description'], count_borrowed=book['count_borrowed'])
        book_list.append(cur_book)
    if not book_list:
        return False, "No result - try different query"
    else:
        return True, book_list


def autocomplete_user(mongo_client: pymongo.MongoClient, query: str,
                      path: Autocomplete_options_user, limit=10) -> Tuple[bool, list[User]]:
    """ retuns list of autocompleted query based on what we have in DB
    Args:
        mongo_client (pymongo.MongoClient): mongo client
        query (str): what are you looking for in user
        path (Autocomplete_options_user): |first_name|surname|address|pid|
        limit (int, optional): how many results are you looking for. Defaults to 10.

    Returns:
        dict[specific_result]: list of results can be None
    """

    if len(query) < 3 or len(query) > 15:
        return False, "No result - Query too short"
    results = get_user_column(mongo_client).aggregate([{
        "$search": {
            "index": "user_prefix",
            "autocomplete": {
                "query": query,
                "path": path.name
                , "fuzzy": {
                    "maxEdits": 2,
                    "prefixLength": 3
                }
            }
        }
    }, {
        "$limit": limit
    }])
    user_list = []
    for user in results:
        cur_user = Person(_id=user['_id'], first_name=user['first_name'], surname=user['surname'],
                          pid=user['pid'], address=user['address'],
                          login_name=user['login_name'], password=user['password'],
                          role=user['role'])
        user_list.append(cur_user)
    if not user_list:
        return False, "No result - try different query"
    else:
        return True, user_list
