from typing import Annotated, Optional
from pydantic import BaseModel, BeforeValidator, Field
from loader import db

PyObjectId = Annotated[str, BeforeValidator(str)]


class Report(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    address: PyObjectId
    shortAddress: str
    sender: int
    senderUsername: str
    message: str
    contact: bool
    fulfilled: bool = False


reports_collection = db["reports"]
