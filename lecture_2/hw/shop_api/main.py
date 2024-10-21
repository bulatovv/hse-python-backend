from itertools import islice
from http import HTTPStatus
from typing import Annotated
from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.responses import JSONResponse
from lecture_2.hw.shop_api.models import Cart, Item, storage
from lecture_2.hw.shop_api.schemas import ItemCreate, ItemReplace, ItemUpdate

app = FastAPI(title="Shop API")

@app.post("/cart")
async def create_cart():
    id = storage.carts.get_last_id()
    storage.carts[id] = Cart(id = id)
    return JSONResponse(
        content={'id': id},
        headers={
            'Location': f'/cart/{id}'
        },
        status_code=HTTPStatus.CREATED
    )

@app.get("/cart/{id}")
async def get_cart(id: int) -> Cart:
    cart = storage.carts[id]
    if not cart:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Cart not found")
    return cart

@app.get("/cart")
async def get_carts(
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(gt=0)] = 10,
    min_price: Annotated[float | None, Query(ge=0)] = None,
    max_price: Annotated[float | None, Query(ge=0)] = None,
    max_quantity: Annotated[int | None, Query(ge=0)] = None,
    min_quantity: Annotated[int | None, Query(ge=0)] = None,
) -> list[Cart]:
    min_price = float('-inf') if min_price is None else min_price
    max_price = float('+inf') if max_price is None else max_price
    
    min_quantity = float('-inf') if min_quantity is None else min_quantity # type: ignore
    max_quantity = float('+inf') if max_quantity is None else max_quantity # type: ignore

    carts = (
        cart for cart in storage.carts.values()
        if (min_price < cart.price < max_price) and
           (min_quantity < cart.get_total_quantity() < max_quantity)
    )

    data = list(islice(carts, offset, offset + limit))
    print(data)
    return data



@app.post("/cart/{cart_id}/add/{item_id}")
async def add_item_to_cart(cart_id: int, item_id: int):
    cart = storage.carts.get(cart_id)
    if cart is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Cart not found")

    item = storage.items.get(item_id)
    if item is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Item not found")
  
    cart.add_item(item)

    return Response(status_code=204)


@app.post("/item", status_code=HTTPStatus.CREATED)
async def create_item(data: ItemCreate, response: Response) -> Item:
    id = storage.items.get_last_id()
    storage.items[id] = Item(
        id=id,
        name=data.name,
        price=data.price
    )
    response.headers['Location'] = f'/item/{id}'
    return storage.items[id]


@app.get("/item/{id}")
async def get_item(id: int) -> Item:
    item = storage.items.get(id)
    
    if not item or item.deleted:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Item not found")

    return item

@app.get("/item")
async def get_items(
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(gt=0)] = 10,
    min_price: Annotated[float | None, Query(ge=0)] = None,
    max_price: Annotated[float | None, Query(ge=0)] = None,
    show_deleted: bool = False
) -> list[Item]:
    min_price = float('-inf') if min_price is None else min_price
    max_price = float('+inf') if max_price is None else max_price
    items = (
        item for item in storage.items.values()
        if (min_price < item.price < max_price) and
           (not item.deleted or show_deleted)
    )

    return list(islice(items, offset, offset + limit))

@app.put("/item/{id}")
async def replace_item(id: int, data: ItemReplace) -> Item:
    item = storage.items.get(id)
    if not item:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Item not found")
    
    item.name = data.name
    item.price = data.price

    return item 


@app.patch("/item/{id}")
async def update_item(id: int, data: ItemUpdate):
    item = storage.items.get(id)
    if not item:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Item not found")
   
    if item.deleted:
        return Response(status_code=HTTPStatus.NOT_MODIFIED)
    
    if item.name is not None:
        item.name = data.name

    if item.price is not None:
        item.price = data.price
    
    return item

@app.delete("/item/{id}")
async def delete_item(id: int):
    item = storage.items.get(id)
    if not item:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Item not found")

    item.deleted = True
