from typing import Annotated, Optional
from pydantic import BaseModel, BeforeValidator, Field
from loader import db

PyObjectId = Annotated[str, BeforeValidator(str)]


class Config(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    map: str = None


config_collection = db["config"]
