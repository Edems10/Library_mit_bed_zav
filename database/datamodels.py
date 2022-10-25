from array import array
import uuid
from dataclasses import field
from datetime import datetime
from marshmallow_dataclass import dataclass as mm_dataclass
from typing import Optional, List
from dataclasses_json import dataclass_json, Undefined
from marshmallow import validate
from enum import Enum

class Roles(Enum):
    Librarian = 1
    User = 2

@dataclass_json(undefined=Undefined.EXCLUDE)
class Book:
    title: str = field(metadata={"validate": validate.Length(min=1, max=256)})
    author: str = field(metadata={"validate": validate.Length(min=1, max=256)})
    length: int
    year: int
    image: str
    # idk mby we want to save text as well
    # text : str
    copies_available: int
    genre: Optional[str]
    description: Optional[str]
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])


@dataclass_json(undefined=Undefined.EXCLUDE)
class Person:
    first_name: str = field(metadata={"validate": validate.Length(min=1, max=256)})
    surname: str = field(metadata={"validate": validate.Length(min=1, max=256)})
    pid: int
    address: str = field(metadata={"validate": validate.Length(min=1, max=256)})
    login_name: str = field(metadata={"validate": validate.Length(min=1, max=32)})
    password: str = field(metadata={"validate":validate.Length(min=6,max=64)})
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    borrowed_books = array
    banned = bool
    approved_by_librarian = bool
    role = Roles
    created_at: datetime = field(metadata={
        'dataclasses_json': {
            'encoder': lambda x: datetime.timestamp(x),
        }
    }, default_factory=datetime.utcnow)


    