from asyncpg import Connection

async def get_all_complaints(conn: Connection):
    """
    Fetches all complaints. Returning them as dicts is 
    great for FastAPI JSON serialization.
    """
    rows = await conn.fetch(
        "SELECT * FROM complaints ORDER BY report_datetime DESC"
    )
    return [dict(row) for row in rows]


async def insert_complaint(db, result_dict):
    query = """
        INSERT INTO complaints 
        (report_id, issue_description, issue_type, priority_level, 
        priority_score, severity_score, area_importance, 
        citizen_reports_count, location, issue_status)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
    """
    await db.execute(
        query,
        result_dict['report_id'],
        result_dict['issue_description'],
        result_dict['issue_type'],
        result_dict['priority_level'],
        result_dict['priority_score'],
        result_dict['severity_score'],
        result_dict['area_importance'],
        result_dict['citizen_reports_count'],
        result_dict['location'],
        'submitted'
    )
