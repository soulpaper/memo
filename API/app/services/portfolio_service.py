from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.models import User, KisKey, Holding, StockPriceHistory
from app.utils.kis_api import KisApi
import logging

logger = logging.getLogger(__name__)

async def sync_user_portfolio(user_id: int, db: AsyncSession):
    # 1. Get User's KIS Keys
    result = await db.execute(select(KisKey).where(KisKey.user_id == user_id))
    kis_key = result.scalars().first()
    
    if not kis_key:
        logger.warning(f"No KIS Key found for user {user_id}")
        return
    
    # 2. Initialize API
    # Note: kis_key.account_no should be 8 digits. 
    # If we stored full account number, we might need to slice it.
    # Assuming the model stores 8 digits in account_no.
    
    api = KisApi(
        app_key=kis_key.app_key,
        app_secret=kis_key.app_secret,
        account_no=kis_key.account_no,
        account_prod=kis_key.account_prod,
        is_virtual=kis_key.is_virtual
    )
    
    # 3. Fetch Balance
    try:
        balance_data = await api.get_account_balance()
    except Exception as e:
        logger.error(f"Failed to fetch balance for user {user_id}: {e}")
        return

    # Check for API error
    if balance_data.get("rt_cd") != "0":
        logger.error(f"API Error: {balance_data.get('msg1')}")
        return

    # 4. Process Holdings
    # output1 is the list of holdings
    holdings_list = balance_data.get("output1", [])
    
    for item in holdings_list:
        code = item.get("pdno") # Product Number (Stock Code)
        name = item.get("prdt_name")
        qty = int(item.get("hldg_qty", 0))
        if qty == 0:
            continue
            
        avg_price = float(item.get("pchs_avg_pric", 0))
        current_price = float(item.get("prpr", 0)) # Current Price from balance query
        
        # Upsert Holding
        # Check if holding exists
        stmt = select(Holding).where(Holding.user_id == user_id, Holding.stock_code == code)
        existing = (await db.execute(stmt)).scalars().first()
        
        if existing:
            existing.quantity = qty
            existing.avg_price = avg_price
            existing.current_price = current_price
            # updated_at is auto-handled by onupdate=func.now() usually, but explicit touch might be safer if values didn't change? 
            # SQLAlchemy detects changes.
        else:
            new_holding = Holding(
                user_id=user_id,
                stock_code=code,
                stock_name=name,
                quantity=qty,
                avg_price=avg_price,
                current_price=current_price
            )
            db.add(new_holding)
        
        # 5. Record Price History
        # We record the price at this sync time
        price_history = StockPriceHistory(
            stock_code=code,
            price=current_price
        )
        db.add(price_history)
        
    await db.commit()
    logger.info(f"Synced portfolio for user {user_id}")
