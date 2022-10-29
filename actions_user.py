from datamodels import Person,Roles
import pymongo


#DATABASE NAME
DATABASE_NAME = 'library'

# TABLES IN DATABASE
USER = 'user'
BOOK = 'book'

class Current_user():
    current_user : Person
    
    def login():
        pass
    current_user

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
        byte_password = bytes(password,'UTF-8')
        new_user = Person(first_name=first_name,surname=surname,pid=pid,address=address
                        ,login_name=login,password=byte_password,role=Roles.User.name)
        new_user.hash_password()
        get_user_column(mongo_client).insert_one(new_user.to_dict())
        return True
    else:
        return False
    
    

#check if librarian is doing this coz then no approval needed
def edit_first_name(mongo_client:pymongo.MongoClient,new_first_name:str)->bool:

    pass

# check limit=6 and time=6 days
def borrow_book():
    pass

def return_book():
    pass

# don't forget approval
def change_account():
    pass

def login(mongo_client:pymongo.MongoClient,login:str,password:str)->Person:
    user_column = get_user_column(mongo_client)
    if(user_exists(mongo_client,login)):
        user_exists_return(mongo_client,login)
    query = {"login_name"
            "password"}