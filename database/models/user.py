from typing import Annotated, Optional, List
from pydantic import BaseModel, BeforeValidator
from loader import db

PyObjectId = Annotated[str, BeforeValidator(str)]


class User(BaseModel):
    id: int
    name: str
    username: str
    status: str = 'user'
    qr: str = None
    subscribtions: List[PyObjectId] = []

users_collection = db["users"]
