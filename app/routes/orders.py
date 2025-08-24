from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from .. import models, database, auth
from datetime import datetime

router = APIRouter()

# Pydantic model for receiving a new order request


class OrderCreate(BaseModel):
    user_id: int
    total_amount: float

# Dependency to get a database session


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoint to place a new order (PROTECTED)


@router.post("/orders/", status_code=status.HTTP_201_CREATED)
def place_order(
    order: OrderCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(auth.get_current_user)  # AUTH DEPENDENCY
):
    # Check if the user exists
    user_exists = db.query(models.DBUser).filter(
        models.DBUser.id == order.user_id).first()
    if not user_exists:
        raise HTTPException(status_code=404, detail="User not found")

    # Create and save the order
    db_order = models.DBOrder(
        user_id=order.user_id,
        total_amount=order.total_amount,
        order_date=datetime.utcnow()
    )

    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    return {"message": "Order placed successfully", "order_id": db_order.id}
