# 1. Framework Imports
from fastapi import APIRouter, Depends, HTTPException
from fastapi.concurrency import run_in_threadpool
from asyncpg import Connection


# Local Project Imports
from app.schemas import ComplaintCreate
from app.crud import insert_complaint
from app.ml.predictor import predict_complaint
from app.database import get_db
from app.database import get_pool

router = APIRouter()

@router.post("/check")
async def checking(data : str):
    
    data = "saeed" + "taj" + "wajahat"

    return data

@router.get("/debug-db")
async def debug_db():
    pool = await get_pool()

    async with pool.acquire() as conn:
        user = await conn.fetchval("SELECT current_user")
        db = await conn.fetchval("SELECT current_database()")

    return {
        "user": user,
        "db": db
    }

@router.post("/complaints")
async def create_complaint(data: ComplaintCreate, db: Connection = Depends(get_db)):
    try:
        conn = db

        query = """
        SELECT COUNT(*) 
        FROM complaints 
        WHERE location = $1 AND issue_type = $2 AND issue_status != 'resolved'
        """

        existing_reports = await conn.fetchval(query, data.location, data.issue_type)
        current_count = (existing_reports or 0) + 1

        result = await run_in_threadpool(predict_complaint, data, current_count)

        await insert_complaint(conn, result)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"System Error: {str(e)}")
