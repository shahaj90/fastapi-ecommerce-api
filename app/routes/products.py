from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from .. import models, database, auth

router = APIRouter()

# Pydantic model for a Product


class Product(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    in_stock: bool

# Dependency to get a database session


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoint to get all products (UNPROTECTED)


@router.get("/products/")
def get_products(db: Session = Depends(get_db)):
    products = db.query(models.DBProduct).all()
    return products

# Endpoint to create a new product (PROTECTED)


@router.post("/products/", status_code=status.HTTP_201_CREATED)
def create_product(
    product: Product,
    db: Session = Depends(get_db),
    current_user: str = Depends(auth.get_current_user)  # AUTH DEPENDENCY
):
    db_product = models.DBProduct(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

# Endpoint to update an existing product (PROTECTED)


@router.put("/products/{product_id}")
def update_product(
    product_id: int,
    product: Product,
    db: Session = Depends(get_db),
    current_user: str = Depends(auth.get_current_user)  # AUTH DEPENDENCY
):
    db_product = db.query(models.DBProduct).filter(
        models.DBProduct.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    for key, value in product.dict().items():
        setattr(db_product, key, value)

    db.commit()
    return db_product

# Endpoint to delete a product (PROTECTED)


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(auth.get_current_user)  # AUTH DEPENDENCY
):
    db_product = db.query(models.DBProduct).filter(
        models.DBProduct.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(db_product)
    db.commit()
    return {"message": f"Product with ID {product_id} deleted"}
