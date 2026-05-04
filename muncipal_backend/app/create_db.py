import asyncpg

async def create_tables(db_pool):

    
    query = """
    CREATE TABLE IF NOT EXISTS complaints (
        id SERIAL PRIMARY KEY,
        report_id VARCHAR(50) UNIQUE,
        issue_description TEXT NOT NULL,
        issue_type VARCHAR(100),
        priority_level VARCHAR(20),
        priority_score FLOAT,
        severity_score FLOAT,
        area_importance FLOAT,
        citizen_reports_count INT,
        location VARCHAR(255),
        issue_status VARCHAR(50) DEFAULT 'submitted',
        report_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    if db_pool is None:
        print(" Pool not initialized yet!")
        return

    # Use 'db_pool' (matching the name above)
    async with db_pool.acquire() as conn:
        await conn.execute(query)
        print(" Database tables checked/created.")
