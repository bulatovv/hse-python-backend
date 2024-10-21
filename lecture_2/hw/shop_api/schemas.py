from pydantic import BaseModel, ConfigDict

class ItemCreate(BaseModel):
    name: str
    price: float

class ItemReplace(BaseModel):
    model_config = ConfigDict(extra='forbid')
    
    name: str
    price: float

class ItemUpdate(BaseModel):
    model_config = ConfigDict(extra='forbid')
    
    name: str | None = None
    price: float | None = None
