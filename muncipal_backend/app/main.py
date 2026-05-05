from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import init_pool, close_pool , pool # Assuming you add a close function
from app.create_db import create_tables
from app.router import complaints
from app.database import get_pool
from fastapi.middleware.cors import CORSMiddleware
import os


FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# Define the Lifespan (Startup & Shutdown)
@asynccontextmanager
async def lifespan(app: FastAPI):
    
    await init_pool()
    print(" Database pool initialized")

    db_pool = await get_pool()
    await create_tables(db_pool)
    print("tables created successfully")
    
    yield  # The app stays "open" here
    
   
    await close_pool()
    print(" Database pool closed")


app = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(complaints.router)