import uuid
from dataclasses import dataclass, field
from datetime import datetime
from marshmallow_dataclass import dataclass as mm_dataclass
from typing import Optional, List
from dataclasses_json import dataclass_json, Undefined
from marshmallow import validate
from enum import Enum
import hashlib
import bcrypt


class Roles(Enum):
    Librarian = 1
    User = 2

@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class Book:
    title: str = field(metadata={"validate": validate.Length(min=1, max=256)})
    author: str = field(metadata={"validate": validate.Length(min=1, max=256)})
    length: int
    year: int
    image: str
    # idk mby we want to save text as well
    # text : str
    current_borrowers: dict #{Person_id:current_time}
    copies_available: int
    genre: Optional[str]
    description: Optional[str]
    count_borrowed=int
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class Person:
    first_name: str = field(metadata={"validate": validate.Length(min=1, max=256)})
    surname: str = field(metadata={"validate": validate.Length(min=1, max=256)})
    pid: int
    address: str = field(metadata={"validate": validate.Length(min=1, max=256)})
    login_name: str = field(metadata={"validate": validate.Length(min=1, max=32)})
    #TODO this needs to be hashed
    password: str = field(metadata={"validate":validate.Length(min=6,max=64)})
    salt: str = bcrypt.gensalt()
    #TODO make your own autoincrementing just testing for mongo
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    borrowed_books = Optional[dict]  #{Book_id:time_borrowed_at} 
    count_borrowed_books = Optional[int] 
    banned : bool = False
    approved_by_librarian : bool = False
    role : Roles = Roles.User
    created_at: datetime = field(metadata={
        'dataclasses_json': {
            'encoder': lambda x: datetime.timestamp(x),
        }
    }, default_factory=datetime.utcnow)

    def hash_password(self):
        self.password = bcrypt.hashpw(self.password,self.salt)
        print(self.password)
        


    