from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api.v1.router import api_router
from app.core.config import settings

from app.core.scheduler import start_scheduler, shutdown_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load scheduler or db connection here
    print("Application startup")
    
    # Initialize DB Tables
    from app.db.database import engine, Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    start_scheduler()
    yield
    shutdown_scheduler()
    print("Application shutdown")

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

# CORS configuration
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8080",  # Common Flutter web port
    "http://127.0.0.1:8080",
    "*" # For development convenience, allow all. Should be restricted in production.
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to KIS Stock Portfolio API"}
