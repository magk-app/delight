"""Test direct asyncpg connection to diagnose SSL/connection issues"""

import asyncio
import os
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
import asyncpg


async def test_direct_connection():
    """Test direct asyncpg connection"""
    print("\n" + "=" * 60)
    print("DIRECT ASYNCPG CONNECTION TEST")
    print("=" * 60)
    
    # Parse connection string
    from urllib.parse import urlparse
    url = settings.async_database_url
    parsed = urlparse(url)
    
    print(f"\nConnecting to: {parsed.hostname}:{parsed.port}")
    print(f"Database: {parsed.path.lstrip('/')}")
    print(f"Username: {parsed.username}")
    
    # Test without SSL first
    print("\n[TEST 1] Trying connection WITHOUT SSL...")
    try:
        conn = await asyncpg.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            user=parsed.username,
            password=parsed.password,
            database=parsed.path.lstrip('/') or 'postgres',
            ssl=False
        )
        result = await conn.fetchval("SELECT 1")
        print(f"   [SUCCESS] Connected! Result: {result}")
        await conn.close()
        return True
    except Exception as e:
        print(f"   [FAILED] {type(e).__name__}: {e}")
    
    # Test with SSL=True
    print("\n[TEST 2] Trying connection WITH SSL=True...")
    try:
        conn = await asyncpg.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            user=parsed.username,
            password=parsed.password,
            database=parsed.path.lstrip('/') or 'postgres',
            ssl=True
        )
        result = await conn.fetchval("SELECT 1")
        print(f"   [SUCCESS] Connected! Result: {result}")
        await conn.close()
        return True
    except Exception as e:
        print(f"   [FAILED] {type(e).__name__}: {e}")
    
    # Test with SSL context
    print("\n[TEST 3] Trying connection WITH SSL context...")
    try:
        import ssl
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        conn = await asyncpg.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            user=parsed.username,
            password=parsed.password,
            database=parsed.path.lstrip('/') or 'postgres',
            ssl=ssl_context
        )
        result = await conn.fetchval("SELECT 1")
        print(f"   [SUCCESS] Connected! Result: {result}")
        await conn.close()
        return True
    except Exception as e:
        print(f"   [FAILED] {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    
    return False


if __name__ == "__main__":
    try:
        result = asyncio.run(test_direct_connection())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\n[WARN] Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

