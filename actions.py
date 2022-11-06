from dataclasses import dataclass
from typing import Tuple, Union
from datetime import datetime
from bson.objectid import ObjectId
from datamodels import Autocomplete_options_book, Autocomplete_options_user, Book, Person, Roles 
import pymongo
import bcrypt
import re
import time

# DATABASE NAME
DATABASE_NAME = 'library'

# TABLES IN DATABASE
USER = 'user'
BOOK = 'book'

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
        #TODO podobně jako u banned, (toto se musi jeste vyresit)
        #if person.verified == False:
        #    self.user = None


    # check if librarian is doing this coz then no approval needed
    # check limit=6 and time=6 days
    def borrow_book(self, mongo_client: pymongo.MongoClient, _id, title) -> Tuple[bool, str]:
        if user_exists_id(mongo_client, _id):
            if book_exists(mongo_client, title):
                books = get_book_column(mongo_client)
                query = {"$and": [{"title": title}, {"copies_available": {"$ne": 0}}]}
                result = books.find_one(query)
                actual_borrowed_books = get_all_borrowed_books_from_user(mongo_client, _id)
                users = get_user_column(mongo_client)
                query_user = {"_id": ObjectId(_id)}
                users_result = users.find_one(query_user)
                if result is not None:
                    if title not in actual_borrowed_books:
                        if users_result["count_borrowed_books"] < 6:
                            get_user_column(mongo_client).update_one({"_id": ObjectId(_id)},
                                                                     {"$push":  {"borrowed_books": {
                                                                      "_id": ObjectId(_id),
                                                                      "title": title,
                                                                      "author": result["author"],
                                                                      "length": result["length"],
                                                                      "year": result["year"], "image": result["image"],
                                                                      "genre": result["genre"],
                                                                      "description": result["description"],
                                                                      "borrowed_at": time.time()}}})
                            get_user_column(mongo_client).update_one({"_id": ObjectId(_id)},
                                                                     {"$push": {"history_of_books": {
                                                                         "_id": ObjectId(_id),
                                                                         "title": title,
                                                                         "author": result["author"],
                                                                         "length": result["length"],
                                                                         "year": result["year"],
                                                                         "image": result["image"],
                                                                         "genre": result["genre"],
                                                                         "description": result["description"],
                                                                         "borrowed_at": time.time()}}})
                            get_user_column(mongo_client).update_one({"_id": ObjectId(_id)},
                                                                     {'$inc': {"count_borrowed_books": 1}})
                            get_book_column(mongo_client).update_one({"title": title},
                                                                     {'$inc': {"count_borrowed": 1}})
                            return True, "User: " + str(_id) + " has borrowed book named: " + str(title)
                        else:
                            return False, "User: " + str(_id) + "has borrowed the maximum number of books"
                    else:
                        return False, "User: " + str(_id) + " has already borrowed book named: " + str(title)
                else:
                    return False, "Book: " + str(title) + " is currently borrowed"
            else:
                return False, "There is no book with title: " + str(title)
        else:
            return False, "There is no user with this name: " + str(_id)

    def return_book(self, mongo_client: pymongo.MongoClient, _id, title) -> Tuple[bool, str]:
        if user_exists_id(mongo_client, _id):
            if book_exists(mongo_client, title):
                actual_borrowed_books = get_all_borrowed_books_from_user(mongo_client, _id)
                users = get_user_column(mongo_client)
                query_user = {"_id": ObjectId(_id)}
                users_result = users.find_one(query_user)
                if title in actual_borrowed_books:
                    get_user_column(mongo_client).update_one({"_id":  ObjectId(_id)},
                                                             {"$pull": {"borrowed_books": {"title": title}}})
                    print(users_result["borrowed_books"][0]["title"])
                    #get_user_column(mongo_client).update_one({"_id": ObjectId(_id)},
                    #                                         {"$push": {"history_of_books.$[]": {"returned_at": time.time()}}})
                    get_user_column(mongo_client).update_one({"_id":  ObjectId(_id)},
                                                             {'$inc': {"count_borrowed_books": -1}})
                    get_book_column(mongo_client).update_one({"title": title},
                                                             {'$inc': {"count_borrowed": -1}})
                    return True, "User: " + str(_id) + " has returned a book named: " + str(title)
                else:
                    return False, "User: " + str(_id) + " has not borrowed a book named: " + str(title)
            else:
                return False, "There is no book with title: " + str(title)
        else:
            return False, "There is no user with this name: " + str(_id)

    def user_find_book(self, mongo_client: pymongo.MongoClient, title):
        books = get_book_column(mongo_client)
        query = {"title": title}
        return books.find_one(query, {"_id": 0, "count_borrowed": 0})

    def edit_user(self, mongo_client: pymongo.MongoClient, _id, first_name: str, surname: str, address: str) -> \
            Tuple[bool, str]:
        if user_exists_id(mongo_client, _id):
            query = {"_id": ObjectId(_id)}
            new_values = {"$set": {"first_name": first_name, "surname": surname, "address": address}}
            if self.user.role == Roles.Librarian.name:
                get_user_column(mongo_client).update_one(query, new_values)
                return True, "User: " + str(_id) + " has been updated!"
            else:
                # TODO iam pretty sure this can be done in one query but can't be asked rn
                new_values = {
                    "$set": {'stashed_changes': {"first_name": first_name, "surname": surname, "address": address}}}
                get_user_column(mongo_client).update_one(query, new_values)
                new_values = {"$set": {'approved_by_librarian': False}}
                get_user_column(mongo_client).update_one(query, new_values)
                return True, f"User: {_id} has been updated waiting for approve from librarian"
        else:
            return False, "There is no user with _id: " + str(_id)


@dataclass
class Librarian(User):

    def __init__(self, person: Person):
        self.user = person

    user: Person = None

    def ban_user(self, mongo_client: pymongo.MongoClient, _id) -> Tuple[bool, str]:
        if user_exists_id(mongo_client, _id):
            query = {"_id":  ObjectId(_id)}
            new_values = {"$set": {"banned": True}}
            get_user_column(mongo_client).update_one(query, new_values)
            return True, "User: " + str(_id) + " has been banned!"
        else:
            return False, "There is no user with _id: " + str(_id)

    def verified_user(self, mongo_client: pymongo.MongoClient, _id) -> Tuple[bool, str]:
        if user_exists_id(mongo_client, _id):
            query = {"_id": ObjectId(_id)}
            new_values = {"$set": {"verified": True}}
            get_user_column(mongo_client).update_one(query, new_values)
            return True, "User: " + str(_id) + " has been verified!"
        else:
            return False, "There is no user with _id: " + str(_id)


    def accept_user_changes(self, mongo_client: pymongo.MongoClient, _id) -> Tuple[bool, str]:
        if user_exists_id(mongo_client, _id):
            user = get_user_column(mongo_client)
            user_changes = []
            try:
                user_changes.append(user.find_one({"_id": ObjectId(_id)}, {"_id": 0, "stashed_changes": 1}))
                if user_changes is not None:
                    get_user_column(mongo_client).update_one({"_id": ObjectId(_id)}, {
                        "$set": {"first_name": user_changes[0]["stashed_changes"]["first_name"],
                                 "surname": user_changes[0]["stashed_changes"]["surname"],
                                 "address": user_changes[0]["stashed_changes"]["address"]}})
                    get_user_column(mongo_client).update_one({"_id": ObjectId(_id)},
                                                             {"$set": {'approved_by_librarian': True}})
                    get_user_column(mongo_client).update_one({"_id": ObjectId(_id)},
                                                             {"$unset": {"stashed_changes": {}}})
                    return True, "Admin has accepted changes to the profile data of user: " + str(_id)
            except KeyError:
                return False, "User: " + str(_id) + " has no changes to approve"
        else:
            return False, "There is no user with _id: " + str(_id)

    def get_all_users(self, mongo_client: pymongo.MongoClient):
        users = get_user_column(mongo_client)
        return list(users.find({}, {"_id": 1, "login_name": 1, "first_name": 1, "surname": 1, "borrowed_books": 1,
                                    "count_borrowed_books": 1, "created_at": 1}))

    def find_user(self, mongo_client: pymongo.MongoClient, _id):
        users = get_user_column(mongo_client)
        query = {"_id":  ObjectId(_id)}
        return users.find_one(query, {"_id": 1, "login_name": 1, "first_name": 1, "surname": 1, "borrowed_books": 1})

    def get_all_users_with_stashed_changes(self, mongo_client: pymongo.MongoClient):
        users = get_user_column(mongo_client)
        return list(users.find({"approved_by_librarian": False}, {"_id": 1}))

    def add_book(self, mongo_client: pymongo.MongoClient, title: str, author: str, length: int, year: int, image: str,
                 copies_available: int, genre: str, description: str, count_borrowed: int) -> Tuple[bool, str]:
        if not book_exists(mongo_client, title):
            new_book = Book(title=title, author=author, length=length, year=year, image=image,
                            copies_available=copies_available, genre=genre,
                            description=description, count_borrowed=count_borrowed)
            get_book_column(mongo_client).insert_one(new_book.to_dict())
            return True, "Book: " + title + " has been added to library"
        else:
            return False, "Book: " + title + " already exists in library"

    # can only be done if no books borrowed
    def edit_book(self, mongo_client: pymongo.MongoClient, _id, title: str, author: str, length: int, year: int,
                  image: str,
                  copies_available: int, genre: str, description: str, count_borrowed: int) -> Tuple[bool, str]:
        books = get_book_column(mongo_client)
        if book_exists_id(mongo_client, _id):
            if not book_exists(mongo_client, title):
                query = {"$and": [{"_id": ObjectId(_id)}, {"count_borrowed": 0}]}
                result = books.find_one(query)
                if result is not None:
                    new_values = {"$set": {"title": title, "author": author, "length": length, "year": year, "image": image,
                                           "copies_available": copies_available, "genre": genre, "description": description,
                                           "count_borrowed": count_borrowed}}
                    get_book_column(mongo_client).update_one(query, new_values)
                    return True, "Book with ID: " + str(_id) + " has been modified!"
                else:
                    return False, "Book with ID: " + str(_id) + " is currently borrowed!"
            else:
                return False, "There is already a book with the title: " + str(title)
        else:
            return False, "There is no book with the ID: " + str(_id)

    # can only be done if no books borrowed
    def delete_book(self, mongo_client: pymongo.MongoClient, _id) -> Tuple[bool, str]:
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

    def find_book(self, mongo_client: pymongo.MongoClient, title):
        books = get_book_column(mongo_client)
        query = {"title": title}
        return books.find_one(query)

    def find_all_books(self, mongo_client: pymongo.MongoClient):
        books = get_book_column(mongo_client)
        return list(books.find({}, {"_id": 0, "title": 1, "author": 1}))


def get_all_borrowed_books_from_user(mongo_client: pymongo.MongoClient, _id):
    users = get_user_column(mongo_client)
    borrowed_books = []
    all_books = users.find_one({"_id": ObjectId(_id)}, {"borrowed_books": 1})
    try:
        for x in range(len(all_books['borrowed_books'])):
            borrowed_books.append((all_books['borrowed_books'][x]["title"]))
        return borrowed_books
    except KeyError:
        return []


def get_book_column(mongo_client: pymongo.MongoClient):
    return mongo_client[DATABASE_NAME][BOOK]


def book_exists(mongo_client: pymongo.MongoClient, book_name):
    books = get_book_column(mongo_client)

    query = {"title": book_name}
    cursor = books.find(query)
    found = 0
    for _ in cursor:
        found += 1
    if found >= 1:
        return True
    else:
        return False


def book_exists_id(mongo_client: pymongo.MongoClient, id):
    books = get_book_column(mongo_client)
    cursor = books.find({"_id": ObjectId(id)})
    for _ in cursor:
        return True
    return False

def book_exists_return(mongo_client: pymongo.MongoClient, book_name):
    books = get_book_column(mongo_client)
    query = {"title": book_name}
    return books.find_one(query)


def get_user_column(mongo_client: pymongo.MongoClient):
    return mongo_client[DATABASE_NAME][USER]


def user_exists_id(mongo_client: pymongo.MongoClient, id):
    users = get_user_column(mongo_client)
    cursor = users.find({"_id": ObjectId(id)})
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

    if (not user_exists(mongo_client, login)):
        # password needs to be saved in bytes
        # byte_password = bytes(password,'UTF-8')
        if re.fullmatch(r'[A-Za-z0-9@#$%^&+=_]{6,}', password):
            new_user = Person(first_name=first_name, surname=surname, pid=pid, address=address,
                              login_name=login, password=password, role=Roles.User.name)
            new_user.hash_password()
            get_user_column(mongo_client).insert_one(new_user.to_dict())
            return True, "Account has been created successfully"
        else:
            return False, "Password must have at least 6 characters!"
    else:
        return False, "This account already exists"


def hash_password(password, salt):
    return bcrypt.hashpw(password, salt)


def login(mongo_client: pymongo.MongoClient, login: str, password: str) -> Union[
         Tuple[bool, Person], Tuple[bool, str], bool]:
    user_column = get_user_column(mongo_client)
    if (user_exists(mongo_client, login)):
        user_exists_return(mongo_client, login)

    query = {"login_name": login}
    user = user_column.find_one(query)

    if user is not None:
        byte_password = bytes(password, 'UTF-8')
        salt = user['salt']
        id = user['_id']
        if re.fullmatch(r'[A-Za-z0-9@#$%^&+=_]{6,}', password):
            if hash_password(password, salt) == user['password']:
                # TODO can be done with =0 borrowed_books but w/e
                try:
                    CURRENT_USER = Person(
                        login_name=user['login_name'], password=user['password'],
                        _id=user['_id'], first_name=user['first_name'],
                        surname=user['surname'], pid=user['pid'], address=user['address'],
                        salt=user['salt'], borrowed_books=user['borrowed_books'],
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
                return False, "Incorrect username or password"
        else:
            return False, "Password must have at least 6 characters"
    else:
        return False, "Incorrect username or password"

def autocomplete_book(mongo_client: pymongo.MongoClient,query:str,
                      path:Autocomplete_options_book,limit=10)->Tuple[bool,list[Book]]:
    """ retuns list of autocompleted query based on what we have in DB
    Args:
        mongo_client (pymongo.MongoClient): mongo client
        query (str): what are you looking for in text
        path (Autocomplete_options_book): |title|author|year|
        limit (int, optional): how many results are you looking for. Defaults to 10.

    Returns:
        dict[specific_result]: list of results can be None
    """
    if len(query)<3 or len(query)>15:
        return False,"No result - Query too short"
    results = get_book_column(mongo_client).aggregate([ { 
    "$search": {
        "index": "autocomplete_book_leftEdge", 
        "autocomplete": { 
            "query": query,
            "path": path.name
            ,"fuzzy": { 
                "maxEdits": 2, 
                "prefixLength": 3 
            } 
         } 
    } 
    },{
    "$limit": limit
    }])
    
    book_list = []
    for book in results:
        cur_book = Book(title=book['title'], author=book['author'], length=book['length'],
                    year=book['year'], image=book['image'],
                    copies_available=book['copies_available'], genre=book['genre'],
                    description=book['description'], count_borrowed=book['count_borrowed'])
        book_list.append(cur_book)
    if not book_list:
        return False, "No result - try different query"
    else:
        return True,book_list

def autocomplete_user(mongo_client: pymongo.MongoClient,query:str,
                      path:Autocomplete_options_user,limit=10)->Tuple[bool,list[User]]:
    """ retuns list of autocompleted query based on what we have in DB
    Args:
        mongo_client (pymongo.MongoClient): mongo client
        query (str): what are you looking for in user
        path (Autocomplete_options_user): |first_name|surname|address|pid|
        limit (int, optional): how many results are you looking for. Defaults to 10.

    Returns:
        dict[specific_result]: list of results can be None
    """
    
    if len(query)<3 or len(query)>15:
        return False,"No result - Query too short"
    results = get_user_column(mongo_client).aggregate([ { 
    "$search": {
        "index": "user_prefix", 
        "autocomplete": { 
            "query": query,
            "path": path.name
            ,"fuzzy": { 
                "maxEdits": 2, 
                "prefixLength": 3 
            } 
         } 
    } 
    },{
    "$limit": limit
    }])
    user_list = []
    for user in results:
        cur_user = Person(_id=user['_id'],first_name=user['first_name'], surname=user['surname'],
                          pid=user['pid'], address=user['address'],
                              login_name=user['login_name'], password=user['password'],
                              role=user['role'])
        user_list.append(cur_user)
    if not user_list:
        return False, "No result - try different query"
    else:
        return True,user_list

