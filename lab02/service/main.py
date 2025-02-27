from pathlib import Path
from typing import Annotated, List, Optional

import fastapi
import uvicorn
from fastapi import File
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

app = fastapi.FastAPI()


class Product(BaseModel):
    id: int
    name: str
    description: str
    icon: Optional[str] = None


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


def get_new_image_path() -> str:
    image_dir = Path("images")
    image_num = 0
    while True:
        image_fp = image_dir / f"{image_num}.png"
        if not image_fp.exists():
            break
        image_num += 1
    image_fp.parent.mkdir(parents=True, exist_ok=True)
    return str(image_fp)


@app.post("/product/{product_id}/image")
def set_image(product_id: int, icon: Annotated[bytes, File()]) -> JSONResponse:
    i = find_product(product_id)
    if i is None:
        return Response(status_code=404)
    image_fp = get_new_image_path()
    with open(image_fp, "wb+") as f:
        f.write(icon)
    products[i].icon = image_fp
    return {"file_size": len(icon)}


@app.get("/product/{product_id}/image")
def get_image(product_id: int) -> Response:
    i = find_product(product_id)
    if i is None:
        return Response("No such product", status_code=404)
    if products[i].icon is None:
        return Response("Product has no icon", status_code=404)
    with open(products[i].icon, "rb") as f:
        return Response(content=f.read(), media_type="image/png")


if __name__ == "__main__":
    uvicorn.run(app)
