from dataclasses import dataclass
from pickle import NONE
from datamodels import Person,Roles
import pymongo
import bcrypt


#DATABASE NAME
DATABASE_NAME = 'library'

# TABLES IN DATABASE
USER = 'user'
BOOK = 'book'

CURRENT_USER = None


@dataclass
class Current_user:
  current_user: Person = None

  def __init__(self, person:Person):
    self.current_user = person 
    if person.banned== True :
      # TODO there has to be a function that informs the user he is banned
      self.current_user = None
    if person.role.name == Roles.Librarian.name:
      self.is_librarian= True
    else:
      self.is_librarian= False

@dataclass
class Current_librarian:
  current_user: Person = None

  def __init__(self, person:Person):
    self.current_user = person 
    if person.banned== True :
      # TODO there has to be a function that informs the user he is banned
      self.current_user = None
    if person.role.name == Roles.Librarian.name:
      self.is_librarian= True
    else:
      self.is_librarian= False


def get_user_column(mongo_client:pymongo.MongoClient):
    return  mongo_client[DATABASE_NAME][USER]

def user_exists(mongo_client:pymongo.MongoClient,user_name):
    users = get_user_column(mongo_client)

    query = {"login_name": user_name}
    cursor = users.find(query)
    found = 0
    for _ in cursor:
        found += 1
    if found >= 1 :
        return True
    else:
        return False

def user_exists_return(mongo_client:pymongo.MongoClient,user_name):
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
        new_user = Person(first_name=first_name,surname=surname,pid=pid,address=address
                        ,login_name=login,password=password,role=Roles.User.name)
        new_user.hash_password()
        get_user_column(mongo_client).insert_one(new_user.to_dict())
        return True
    else:
        return False
    



#check if librarian is doing this coz then no approval needed
# check limit=6 and time=6 days
def borrow_book():
    pass

def return_book():
    pass

# don't forget approval
def change_account():
    pass

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
        return False,"Incorrect username or password"

#TODO idk if this needs to be done
def create_user_librarian():
    pass

def ban_user():
    pass

def edit_user():
    pass

def accept_user_changes():
    pass

def get_all_users():
    pass

def find_book():
    pass

def find_user():
    pass

# can only be done if no books borrowed
def edit_book():
    pass

def add_book():
    pass

# can only be done if no books borrowed
def delete_book():
    pass

# delete old librarian and promoto new user
def appoint_new_librarian():
    pass