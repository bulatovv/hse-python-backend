from http import HTTPStatus
from fastapi import FastAPI
from collections import OrderedDict
from types import SimpleNamespace
from typing import Any
from fastapi.responses import JSONResponse
from lecture_2.hw.shop_api.schemas import ItemCreate

app = FastAPI(title="Shop API")

storage = SimpleNamespace(
    items=OrderedDict(),
    carts=OrderedDict(),
)


def get_last_key(od: OrderedDict, default: Any) -> Any:
    return next(reversed(od), default)


@app.post("/cart")
async def create_cart():
    new_cart_id = get_last_key(storage.carts, -1) + 1
    storage.carts[new_cart_id] = {}
    return JSONResponse(
        content={'id': new_cart_id},
        headers={
            'Location': f'/cart/{new_cart_id}'
        },
        status_code=HTTPStatus.CREATED
    )


@app.post("/item")
async def create_item(data: ItemCreate):
    new_item_id = get_last_key(storage.items, -1) + 1
    data_dict = data.model_dump()
    storage.items[new_item_id] = data_dict
    return JSONResponse(
        content={'id': new_item_id, **data_dict},
        headers={
            'Location': f'/item/{new_item_id}'
        },
        status_code=HTTPStatus.CREATED
    )

