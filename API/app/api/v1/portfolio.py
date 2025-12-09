from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from pydantic import BaseModel
from app.db.database import get_db
from app.api.v1.auth import get_current_user
from app.models.models import User, Holding, StockMeta, KisKey
from app.services.portfolio_service import sync_user_portfolio

router = APIRouter(prefix="/portfolio", tags=["portfolio"])

# Schemas
class KisKeyCreate(BaseModel):
    app_key: str
    app_secret: str
    account_no: str # 8 digits
    account_prod: str = "01" # 2 digits
    is_virtual: bool = False

class StockMetaSchema(BaseModel):
    note: Optional[str] = None
    target_price: Optional[float] = None
    tags: Optional[str] = None

class HoldingResponse(BaseModel):
    stock_code: str
    stock_name: str
    quantity: int
    avg_price: float
    current_price: Optional[float]
    meta: Optional[StockMetaSchema] = None
    
    class Config:
        from_attributes = True

@router.post("/keys")
async def register_keys(keys: KisKeyCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    # Check if exists
    stmt = select(KisKey).where(KisKey.user_id == current_user.id)
    existing = (await db.execute(stmt)).scalars().first()
    
    if existing:
        existing.app_key = keys.app_key
        existing.app_secret = keys.app_secret
        existing.account_no = keys.account_no
        existing.account_prod = keys.account_prod
        existing.is_virtual = keys.is_virtual
    else:
        new_key = KisKey(
            user_id=current_user.id,
            **keys.dict()
        )
        db.add(new_key)
    
    await db.commit()
    return {"message": "Keys registered successfully"}

@router.post("/sync")
async def sync_portfolio(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await sync_user_portfolio(current_user.id, db)
    return {"message": "Sync started/completed"}

@router.get("/holdings", response_model=List[HoldingResponse])
async def get_holdings(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    # Join Holding and StockMeta
    # Because StockMeta is optional, we do outer join
    # Note: StockMeta is keyed by (user_id, stock_code).
    
    stmt = select(Holding, StockMeta).outerjoin(
        StockMeta, 
        (StockMeta.stock_code == Holding.stock_code) & (StockMeta.user_id == Holding.user_id)
    ).where(Holding.user_id == current_user.id)
    
    results = await db.execute(stmt)
    
    response = []
    for holding, meta in results:
        h_dict = {
            "stock_code": holding.stock_code,
            "stock_name": holding.stock_name,
            "quantity": holding.quantity,
            "avg_price": holding.avg_price,
            "current_price": holding.current_price,
            "meta": None
        }
        if meta:
            h_dict["meta"] = {
                "note": meta.note,
                "target_price": meta.target_price,
                "tags": meta.tags
            }
        response.append(h_dict)
        
    return response

@router.post("/stocks/{code}/meta")
async def update_stock_meta(code: str, meta: StockMetaSchema, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = select(StockMeta).where(StockMeta.user_id == current_user.id, StockMeta.stock_code == code)
    existing = (await db.execute(stmt)).scalars().first()
    
    if existing:
        if meta.note is not None: existing.note = meta.note
        if meta.target_price is not None: existing.target_price = meta.target_price
        if meta.tags is not None: existing.tags = meta.tags
    else:
        new_meta = StockMeta(
            user_id=current_user.id,
            stock_code=code,
            note=meta.note,
            target_price=meta.target_price,
            tags=meta.tags
        )
        db.add(new_meta)
        
    await db.commit()
    return {"message": "Meta updated"}
