from dataclasses import dataclass
from pickle import NONE
from datamodels import Person,Roles
import pymongo
import bcrypt
import re


#DATABASE NAME
DATABASE_NAME = 'library'

# TABLES IN DATABASE
USER = 'user'
BOOK = 'book'

CURRENT_USER = None


@dataclass
class User:
  user: Person = None

  def __init__(self, person:Person):
    user = person 
    if person.banned== True :
      # TODO there has to be a function that informs the user he is banned
      user = None

    #check if librarian is doing this coz then no approval needed
    # check limit=6 and time=6 days
    def borrow_book():
        print("hello")
        pass

    def return_book():
        pass

    def find_book():
        pass


@dataclass
class Librarian(User):
  user: Person = None



  def __init__(self, person:Person):
    self.user = person

    if person.banned== True :
      # TODO there has to be a function that informs the user he is banned
      self.user = None


    # don't forget approval
    def change_account():
        pass

    def ban_user():
        pass

    def edit_user():
        pass

    def accept_user_changes():
        pass

    def get_all_users():
        pass

    def find_user():
        pass
    # can only be done if no books borrowed
    def edit_book():
        pass

  def add_book(self, mongo_client: pymongo.MongoClient, title: str, author: str, length: int, year: int, image: str,
             copies_available: int, genre: str, description: str,
             count_borrowed: int) -> bool:
    if not book_exists(mongo_client, title):
        new_book = Person(title=title, author=author, length=length, year=year, image=image,
                          copies_available=copies_available, genre=genre,
                          description=description, count_borrowed=count_borrowed)
        get_book_column(mongo_client).insert_one(new_book.to_dict())
        return True
    else:
        return False

    # can only be done if no books borrowed
    def delete_book():
        pass

    # delete old librarian and promoto new user
    def appoint_new_librarian():
        pass





def get_book_column(mongo_client: pymongo.MongoClient):
    return mongo_client[DATABASE_NAME][BOOK]


def book_exists(mongo_client: pymongo.MongoClient, book_name):
    users = get_user_column(mongo_client)

    query = {"title": book_name}
    cursor = users.find(query)
    found = 0
    for _ in cursor:
        found += 1
    if found >= 1:
        return True
    else:
        return False


def book_exists_return(mongo_client: pymongo.MongoClient, book_name):
    users = get_user_column(mongo_client)
    query = {"title": book_name}
    return users.find_one(query)


def get_user_column(mongo_client:pymongo.MongoClient):
    return mongo_client[DATABASE_NAME][USER]


def user_exists(mongo_client: pymongo.MongoClient, user_name):
    users = get_user_column(mongo_client)

    query = {"login_name": user_name}
    cursor = users.find(query)
    found = 0
    for _ in cursor:
        found += 1
    if found >= 1:
        return True
    else:
        return False


def user_exists_return(mongo_client: pymongo.MongoClient, user_name):
    users = get_user_column(mongo_client)
    query = {"login_name": user_name}
    return users.find_one(query)


def create_account(mongo_client:pymongo.MongoClient,first_name:str,surname:str,pid:int,address:str,login:str,password:str)->bool:

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
    
    if(not user_exists(mongo_client,login)):
        #password needs to be saved in bytes
        #byte_password = bytes(password,'UTF-8')
        if re.fullmatch(r'[A-Za-z0-9@#$%^&+=_]{6,}', password):
            new_user = Person(first_name=first_name,surname=surname,pid=pid,address=address
                            ,login_name=login,password=password,role=Roles.User.name)
            new_user.hash_password()
            get_user_column(mongo_client).insert_one(new_user.to_dict())
            return True
        else:
            return False, "Password must have at least 6 characters"
    else:
        return False
    

def hash_password(password,salt):
    return bcrypt.hashpw(password,salt)

def login(mongo_client:pymongo.MongoClient,login:str,password:str)->Person:
    user_column = get_user_column(mongo_client)
    if(user_exists(mongo_client,login)):
        user_exists_return(mongo_client,login)

    query = {"login_name":login}
    user = user_column.find_one(query)
    if user is not None:
        byte_password = bytes(password,'UTF-8')
        salt = user['salt']
        if re.fullmatch(r'[A-Za-z0-9@#$%^&+=_]{6,}', password):
            if hash_password(password,salt) == user['password']:
                #TODO can be done with =0 borrowed_books but w/e
                try:
                    CURRENT_USER = Person(
                        login_name=user['login_name'],password=user['password'],
                        id=user['_id'],first_name=user['first_name'],
                        surname=user['surname'],pid=user['pid'],address=user['address'],
                        salt=user['salt'],borrowed_books=user['borrowed_books'],
                        count_borrowed_books=user['count_borrowed_books'],
                        banned=user['banned'],approved_by_librarian=user['approved_by_librarian'],
                        role=user['role'],created_at=user['created_at'])
                except KeyError as e:
                    CURRENT_USER = Person(
                        login_name=user['login_name'],password=user['password'],
                        id=user['_id'],first_name=user['first_name'],
                        surname=user['surname'],pid=user['pid'],address=user['address'],
                        salt=user['salt'],count_borrowed_books=user['count_borrowed_books'],
                        banned=user['banned'],approved_by_librarian=user['approved_by_librarian'],
                        role=user['role'],created_at=user['created_at'])

                return True,CURRENT_USER
            else:
                return False,"Incorrect username or password"
        else:
             return False, "Password must have at least 6 characters"
    else:
        return False,"Incorrect username or password"







