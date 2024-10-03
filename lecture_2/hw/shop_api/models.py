from dataclasses import dataclass, field

@dataclass
class Item:
    id: int
    name: str
    price: float
    deleted: bool = False

@dataclass
class Cart:
    id: int
    items: list[Item] = field(default_factory=list)
