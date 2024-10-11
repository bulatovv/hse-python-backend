from pydantic import BaseModel

class ItemCreate(BaseModel):
    name: str
    price: float

class ItemReplace(BaseModel):
    name: str
    price: float

class ItemUpdate(BaseModel):
    name: str | None = None
    price: float | None = None
