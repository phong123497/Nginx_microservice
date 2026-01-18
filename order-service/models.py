from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=True)
    product = Column(String(255), nullable=False)
    amount = Column(Integer, nullable=False)

