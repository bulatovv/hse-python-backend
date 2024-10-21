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
    
    def __hash__(self):
        return self.id

class CartPosition(BaseModel):
    id: int
    name: str
    quantity: int
    available: bool
    

class Cart(BaseModel):
    id: int
    _counts: Counter = PrivateAttr(default_factory=Counter)
    
    def add_item(self, item: Item): 
        self._counts[item] += 1

    @computed_field
    @property
    def items(self) -> list[CartPosition]:
        return [
            CartPosition(
                id=item.id, name=item.name, quantity=quantity, available=item.deleted
            )
            for item, quantity in self._counts.items()
        ]

    @computed_field
    @property
    def price(self) -> float:
        return sum(
            item.price * quantity
            for item, quantity in self._counts.items()
        )

    def get_total_quantity(self) -> int:
        print(self._counts.values())
        return sum(q for q in self._counts.values())
