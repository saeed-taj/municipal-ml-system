# 1. Framework Imports
from fastapi import APIRouter, Depends, HTTPException
from asyncpg import Connection



# Local Project Imports
from app.schemas import ComplaintCreate
from app.crud import insert_complaint
from app.ml.predictor import predict_complaint
from app.database import get_db
import os
from dotenv import load_dotenv

import requests
 
router = APIRouter()
load_dotenv()


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

        result = await predict_complaint(data, current_count)

        await insert_complaint(conn, result)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"System Error: {str(e)}")
    

# async def geocode_address(location : str):
#     url=os.getenv("OPEN_STREET_URL")

#     params = {
#         "q" : location,
#         "format" : "json"
#     }

#     headers = {
#         "User-agent" : "municipal-ml-system"
#     }

#     response = requests.get(url , params=params , headers=headers)
#     res = response.json()


#     if not res:
#         return None, None
    
#     lat = float(res[0]["lat"])
#     lon = float(res[0]["lon"])

#     return lat , lon
