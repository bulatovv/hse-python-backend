from collections import Counter, OrderedDict
from pydantic import BaseModel, PrivateAttr, computed_field
from types import SimpleNamespace


class SimpleStorage(OrderedDict):
    def get_last_id(self):
        last_id = next(reversed(self), -1)
        return last_id + 1

storage = SimpleNamespace(
    items=SimpleStorage(),
    carts=SimpleStorage(),
)

class Item(BaseModel):
    id: int
    name: str
    price: float
    deleted: bool = False

class CartPosition(BaseModel):
    id: int
    name: str
    quantity: int
    available: bool

class ItemWrap(BaseModel):
    item: Item

    def __hash__(self):
        return self.item.id

class Cart(BaseModel):
    id: int
    _counts: Counter = PrivateAttr(default_factory=Counter)
    
    def add_item(self, item: Item): 
        self._counts[ItemWrap(item=item)] += 1

    @computed_field
    @property
    def items(self) -> list[CartPosition]:
        return [
            CartPosition(
                id=wrap.item.id, name=wrap.item.name, quantity=quantity, available=wrap.item.deleted
            )
            for wrap, quantity in self._counts.items()
        ]

    @computed_field
    @property
    def price(self) -> float:
        return sum(
            wrap.item.price * quantity
            for wrap, quantity in self._counts.items()
        )

