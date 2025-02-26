from typing import List, Optional

import fastapi
import uvicorn
from fastapi.responses import Response
from pydantic import BaseModel

app = fastapi.FastAPI()


class Product(BaseModel):
    id: int
    name: str
    description: str


class ProductIn(BaseModel):
    name: str
    description: str


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


products: List[Product] = []
id_counter = 0


def find_product(product_id: int) -> Optional[int]:
    for i, q in enumerate(products):
        if q.id == product_id:
            return i


@app.post("/product")
def create_product(p: ProductIn) -> Product:
    global id_counter
    products.append(Product(id=id_counter, **p.model_dump()))
    id_counter += 1
    return products[-1]


@app.get("/product/{product_id}")
def get_product(product_id: int) -> Product:
    i = find_product(product_id)
    return products[i] if i is not None else Response(status_code=404)


@app.put("/product/{product_id}")
def edit_product(product_id: int, p: ProductUpdate) -> Product:
    i = find_product(product_id)
    if i is None:
        return Response(status_code=404)
    products[i] = products[i].model_copy(update=dict(filter(lambda x: x[1] is not None, p.model_dump().items())))
    return products[i]


@app.delete("/product/{product_id}")
def delete_product(product_id: int) -> Product:
    global products
    i = find_product(product_id)
    if i is None:
        return Response(status_code=404)
    p = products[i]
    products = products[:i] + products[i + 1:]
    return p


@app.get("/products")
def get_products() -> List[Product]:
    return products


if __name__ == "__main__":
    uvicorn.run(app)
