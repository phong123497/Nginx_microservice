from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import SessionLocal, engine, Base
from models import Order
from schemas import OrderCreate, Order as OrderSchema


# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Order Service",
    description="Microservice for managing orders",
    version="1.0.0"
)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"service": "order-service", "status": "running"}

@app.get("/orders", response_model=List[OrderSchema])
def get_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get list of orders"""
    orders = db.query(Order).offset(skip).limit(limit).all()
    return orders
    
@app.get("/orders", response_model=List[OrderSchema])
def get_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get list of orders"""
    orders = db.query(Order).offset(skip).limit(limit).all()
    return orders

@app.post("/orders", response_model=OrderSchema, status_code=201)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    """Create a new order"""
    # Verify user exists (simple check via database)
    from sqlalchemy import text
    result = db.execute(text("SELECT id FROM users WHERE id = :user_id"), {"user_id": order.user_id})
    if not result.fetchone():
        raise HTTPException(status_code=404, detail="User not found")
    
    db_order = Order(user_id=order.user_id, product=order.product, amount=order.amount)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8002
    )