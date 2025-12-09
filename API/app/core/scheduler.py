from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select
from app.db.database import SessionLocal
from app.models.models import User
from app.services.portfolio_service import sync_user_portfolio
import logging

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

async def sync_all_users_portfolios():
    logger.info("Starting scheduled sync for all users")
    async with SessionLocal() as db:
        result = await db.execute(select(User))
        users = result.scalars().all()
        
        for user in users:
            logger.info(f"Syncing user {user.username} (ID: {user.id})")
            await sync_user_portfolio(user.id, db)
    logger.info("Scheduled sync completed")

def start_scheduler():
    # Run every hour
    scheduler.add_job(sync_all_users_portfolios, 'interval', hours=1)
    scheduler.start()
    logger.info("Scheduler started")

def shutdown_scheduler():
    scheduler.shutdown()
    logger.info("Scheduler shutdown")
