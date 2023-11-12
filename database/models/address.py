from typing import Annotated, Optional
from pydantic import BaseModel, BeforeValidator, Field
from loader import db

PyObjectId = Annotated[str, BeforeValidator(str)]


class Address(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    address: str
    shortAddress: str
    lon: float
    lat: float


addresses_collection = db["addresses"]
