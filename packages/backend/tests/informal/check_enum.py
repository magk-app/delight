import asyncio
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import text
from app.core.config import settings
from sqlalchemy.ext.asyncio import create_async_engine

load_dotenv(Path(__file__).parent / ".env")

async def check_enum():
    engine = create_async_engine(settings.async_database_url)
    async with engine.connect() as conn:
        result = await conn.execute(text("""
            SELECT e.enumlabel as value
            FROM pg_type t 
            JOIN pg_enum e ON t.oid = e.enumtypid  
            WHERE t.typname = 'memory_type'
            ORDER BY e.enumsortorder;
        """))
        values = [row[0] for row in result]
        print(f"Database enum values: {values}")
    await engine.dispose()

asyncio.run(check_enum())
