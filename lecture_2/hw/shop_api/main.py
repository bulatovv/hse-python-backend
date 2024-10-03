from http import HTTPStatus
from fastapi import FastAPI, HTTPException, Response
from collections import OrderedDict
from dataclasses import asdict
from itertools import groupby
from types import SimpleNamespace
from fastapi.responses import JSONResponse
from lecture_2.hw.shop_api.utils import get_last_key
from lecture_2.hw.shop_api.models import Cart, Item
from lecture_2.hw.shop_api.schemas import ItemCreate

app = FastAPI(title="Shop API")

storage = SimpleNamespace(
    items=OrderedDict(),
    carts=OrderedDict(),
)



@app.post("/cart")
async def create_cart():
    id = get_last_key(storage.carts, -1) + 1
    storage.carts[id] = Cart(id = id)
    

    return JSONResponse(
        content={'id': id},
        headers={
            'Location': f'/cart/{id}'
        },
        status_code=HTTPStatus.CREATED
    )

@app.get("/cart/{id}")
async def get_cart(id: int):
    cart = storage.carts[id]
    key = lambda x: x.id

    grouped_items = groupby(
        sorted(cart.items, key=key),
        key=key
    )

    grouped_items = (
        list(group) for _, group in grouped_items
    ) 

    return asdict(cart) | {
        'items': [
            {
                'id': group[0].id,
                'name': group[0].name,
                'quantity': len(group),
                'available': group[0].deleted
            }
            for group in grouped_items
        ],
        'price': cart.calculate_price()
    }

@app.post("/cart/{cart_id}/add/{item_id}")
async def add_item_to_cart(cart_id: int, item_id: int):
    cart = storage.carts.get(cart_id)
    if cart is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Cart not found")

    item = storage.items.get(item_id)
    if item is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Item not found")
  
    cart.items.append(item)

    return Response(status_code=204)


@app.post("/item")
async def create_item(data: ItemCreate):
    id = get_last_key(storage.items, -1) + 1
    storage.items[id] = Item(
        id=id,
        name=data.name,
        price=data.price
    )
    return JSONResponse(
        content=asdict(storage.items[id]),
        headers={
            'Location': f'/item/{id}'
        },
        status_code=HTTPStatus.CREATED
    )

@app.get("/item/{id}")
async def get_item(id: int):
    item = storage.items.get(id)
    
    if not item:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Item not found")

    return item
