from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    kis_keys = relationship("KisKey", back_populates="user", cascade="all, delete-orphan")
    holdings = relationship("Holding", back_populates="user", cascade="all, delete-orphan")
    stock_metas = relationship("StockMeta", back_populates="user", cascade="all, delete-orphan")


class KisKey(Base):
    __tablename__ = "kis_keys"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    app_key = Column(String, nullable=False)
    app_secret = Column(String, nullable=False)
    account_no = Column(String, nullable=False)  # First 8 digits
    account_prod = Column(String, default="01") # Last 2 digits
    is_virtual = Column(Boolean, default=False) # True for VPS (Virtual), False for Real
    htsid = Column(String, nullable=True) # For WebSocket
    
    user = relationship("User", back_populates="kis_keys")


class Holding(Base):
    __tablename__ = "holdings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stock_code = Column(String, index=True, nullable=False)
    stock_name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    avg_price = Column(Float, nullable=False) # Purchase average
    current_price = Column(Float, nullable=True) # Last updated price
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="holdings")


class StockPriceHistory(Base):
    __tablename__ = "stock_price_history"

    id = Column(Integer, primary_key=True, index=True)
    stock_code = Column(String, index=True, nullable=False)
    price = Column(Float, nullable=False)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())


class StockMeta(Base):
    __tablename__ = "stock_metas"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stock_code = Column(String, index=True, nullable=False)
    note = Column(Text, nullable=True)
    target_price = Column(Float, nullable=True)
    tags = Column(String, nullable=True) # Comma separated or JSON string
    
    user = relationship("User", back_populates="stock_metas")
