from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import httpx
import os

from database import SessionLocal, engine, Base
from models import Order
from schemas import OrderCreate, Order as OrderSchema

# User Service URL - configurable via environment variable
# Can be direct (http://localhost:8001) or via Nginx (http://localhost:8080/api/users)
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:8001")

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Order Service",
    description="Microservice for managing orders",
    version="2.0.0"
)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def verify_user_exists(user_id: int) -> bool:
    """Verify user exists by calling user-service API"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Determine endpoint based on URL
            if "/api/users" in USER_SERVICE_URL:
                endpoint = f"{USER_SERVICE_URL}"
            else:
                endpoint = f"{USER_SERVICE_URL}/users"
            
            response = await client.get(endpoint)
            if response.status_code == 200:
                users = response.json()
                return any(user["id"] == user_id for user in users)
            return False
    except httpx.RequestError as e:
        # If user-service is down, we can't verify
        # In production, you might want to handle this differently
        raise HTTPException(status_code=503, detail=f"User service unavailable: {str(e)}")

@app.get("/")
def read_root():
    return {"service": "order-service", "status": "running", "phase": "2"}

@app.get("/orders", response_model=List[OrderSchema])
def get_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get list of orders"""
    orders = db.query(Order).offset(skip).limit(limit).all()
    return orders

@app.post("/orders", response_model=OrderSchema, status_code=201)
async def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    """Create a new order"""
    # Verify user exists by calling user-service (not database)
    user_exists = await verify_user_exists(order.user_id)
    if not user_exists:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_order = Order(user_id=order.user_id, product=order.product, amount=order.amount)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)
