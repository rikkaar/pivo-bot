from typing import Annotated, Optional
from pydantic import BaseModel, BeforeValidator, Field
from loader import db

PyObjectId = Annotated[str, BeforeValidator(str)]


class Request(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    address: PyObjectId
    shortAddress: str
    sender: int
    senderUsername: str
    name: str
    link: str
    contact: bool
    fulfilled: bool = False


requests_collection = db["requests"]
