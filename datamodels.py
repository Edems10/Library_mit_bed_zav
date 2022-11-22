from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
import bcrypt
from bson.objectid import ObjectId
from dataclasses_json import Undefined, dataclass_json
from marshmallow import validate
import bson


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
class Person:
    _id: ObjectId
    first_name: str = field(metadata={"validate": validate.Length(min=1, max=256)})
    surname: str = field(metadata={"validate": validate.Length(min=1, max=256)})
    pid: int
    address: str = field(metadata={"validate": validate.Length(min=1, max=256)})
    login_name: str = field(metadata={"validate": validate.Length(min=1, max=32)})
    password: str = field(metadata={"validate": validate.Length(min=6, max=64)})
    salt: str = bcrypt.gensalt()
    count_borrowed_books: int = 0
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


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass    
class Book_status:
    book_id: ObjectId
    user_id: ObjectId
    date_borrowed: datetime
    date_returned: datetime
    returned: bool


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass    
class Person_changes:
    person_id: ObjectId
    first_name: str = field(metadata={"validate": validate.Length(min=1, max=256)})
    surname: str = field(metadata={"validate": validate.Length(min=1, max=256)})
    pid: int
    address: str = field(metadata={"validate": validate.Length(min=1, max=256)})
    login_name: str = field(metadata={"validate": validate.Length(min=1, max=32)})
    password: str = field(metadata={"validate": validate.Length(min=6, max=64)})
    approved_by_librarian: bool
    created_at: datetime
    approved_or_rejected_at: datetime


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass    
class Author:
    _id: ObjectId
    first_name: str = field(metadata={"validate": validate.Length(min=1, max=256)})
    surname: str = field(metadata={"validate": validate.Length(min=1, max=256)})


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class Book:
    _id: ObjectId
    title: str = field(metadata={"validate": validate.Length(min=1, max=256)})
    author: Author
    length: int
    year: int
    image: bson.Binary
    copies_available: int
    genre: Optional[str]
    description: Optional[str]
    count_borrowed: int
