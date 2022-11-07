from lib2to3.pgen2.token import OP
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from marshmallow_dataclass import dataclass as mm_dataclass
from typing import Optional, List, Union
from dataclasses_json import dataclass_json, Undefined
from marshmallow import validate
from enum import Enum
import bcrypt
from bson.objectid import ObjectId


class Roles(Enum):
    Librarian = 1
    User = 2

class Autocomplete_options_book(Enum):
    title = "title"
    author = "author"
    year = "year"

class Autocomplete_options_user(Enum):
    first_name = "first_name"
    surname = "surname"
    address = "address"
    pid = "pid"


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class Book:
    # id is optional because it is added by mongodb at the time of creation
    # _id: Optional[str]
    title: str = field(metadata={"validate": validate.Length(min=1, max=256)})
    author: str = field(metadata={"validate": validate.Length(min=1, max=256)})
    length: int
    year: int
    image: str
    # idk mby we want to save text as well
    # text : str
    #  current_borrowers: Optional[dict] #{Person_id:current_time}
    copies_available: int
    genre: Optional[str]
    description: Optional[str]
    count_borrowed: int
    # mongo gives id to each object by default so this might not be needed
    # id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class Person:
    _id: Optional[str]
    first_name: str = field(metadata={"validate": validate.Length(min=1, max=256)})
    surname: str = field(metadata={"validate": validate.Length(min=1, max=256)})
    pid: int
    address: str = field(metadata={"validate": validate.Length(min=1, max=256)})
    login_name: str = field(metadata={"validate": validate.Length(min=1, max=32)})
    password: str = field(metadata={"validate": validate.Length(min=6, max=64)})
    salt: str = bcrypt.gensalt()
    borrowed_books = Optional[dict]  # {Book}
    history_of_books = Optional[dict]  # {Book_id: object(sdafasdfasf),time_returned_at : 139025925.23}
    count_borrowed_books: int = 0
    stashed_changes = Optional[dict]
    banned: bool = False
    verified: bool = False
    approved_by_librarian: bool = True

    role: Roles = Roles.User
    created_at: datetime = field(metadata={
        'dataclasses_json': {
            'encoder': lambda x: datetime.timestamp(x),
        }
    }, default_factory=datetime.utcnow)

    def hash_password(self):
        self.password = bcrypt.hashpw(self.password, self.salt)

    @property
    def id(self):
        return self._id
