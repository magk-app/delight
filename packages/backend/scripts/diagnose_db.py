"""
Diagnose database connection issues.
Shows DATABASE_URL (masked), connection test, and helpful error messages.
"""

import asyncio
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
from app.db.session import engine, AsyncSessionLocal
from sqlalchemy import text


def mask_url(url: str) -> str:
    """Mask password in database URL for display"""
    try:
        parsed = urlparse(url)
        if parsed.password:
            return url.replace(parsed.password, "***")
        return url
    except:
        return url[:50] + "..."


async def test_connection():
    """Test database connection"""
    print("\n" + "=" * 60)
    print("DATABASE CONNECTION DIAGNOSTICS")
    print("=" * 60)
    
    # Show DATABASE_URL (masked)
    try:
        db_url = settings.DATABASE_URL
        async_url = settings.async_database_url
        print(f"\nDATABASE_URL: {mask_url(db_url)}")
        print(f"Async URL: {mask_url(async_url)}")
        
        # Parse hostname
        parsed = urlparse(async_url)
        hostname = parsed.hostname
        port = parsed.port or 5432
        database = parsed.path.lstrip('/') or 'postgres'
        
        print(f"\nConnection Details:")
        print(f"   Hostname: {hostname}")
        print(f"   Port: {port}")
        print(f"   Database: {database}")
        print(f"   Username: {parsed.username}")
        
    except Exception as e:
        print(f"\nERROR: Error reading DATABASE_URL: {e}")
        return False
    
    # Test DNS resolution (supports both IPv4 and IPv6)
    print(f"\nTesting DNS Resolution...")
    try:
        import socket
        # Try IPv4 first
        try:
            ipv4 = socket.gethostbyname(hostname)
            print(f"   [OK] Hostname '{hostname}' resolves to IPv4: {ipv4}")
        except socket.gaierror:
            # Try IPv6
            try:
                addrinfo = socket.getaddrinfo(hostname, port, socket.AF_INET6)
                ipv6 = addrinfo[0][4][0]
                print(f"   [OK] Hostname '{hostname}' resolves to IPv6: {ipv6}")
                print(f"   [WARN] Only IPv6 address found - Python socket may not connect")
                print(f"   [INFO] asyncpg should handle IPv6, but if connection fails,")
                print(f"          try using IPv4 address directly in DATABASE_URL")
            except:
                raise
    except socket.gaierror as e:
        print(f"   [FAIL] DNS Resolution FAILED: {e}")
        print(f"\nPossible issues:")
        print(f"   - Hostname '{hostname}' cannot be resolved")
        print(f"   - Check your internet connection (if cloud database)")
        print(f"   - Verify the hostname in DATABASE_URL is correct")
        print(f"   - If using localhost, make sure PostgreSQL is running")
        return False
    except Exception as e:
        print(f"   [WARN] DNS check error: {e}")
    
    # Test port connectivity
    print(f"\nTesting Port Connectivity...")
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((hostname, port))
        sock.close()
        if result == 0:
            print(f"   [OK] Port {port} is open and accessible")
        else:
            print(f"   [FAIL] Port {port} is NOT accessible (connection refused)")
            print(f"\nPossible issues:")
            print(f"   - Database server is not running")
            print(f"   - Firewall is blocking port {port}")
            print(f"   - Database is not listening on {hostname}:{port}")
            return False
    except Exception as e:
        print(f"   [WARN] Port check error: {e}")
    
    # Test SQLAlchemy connection
    print(f"\nTesting SQLAlchemy Connection...")
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT 1"))
            result.scalar()
        print(f"   [OK] Database connection successful!")
        print(f"\n[SUCCESS] All checks passed! Database is accessible.")
        return True
    except Exception as e:
        print(f"   [FAIL] Connection FAILED: {e}")
        print(f"\nError details:")
        print(f"   {type(e).__name__}: {str(e)}")
        
        # Provide specific guidance based on error
        error_str = str(e).lower()
        if "getaddrinfo" in error_str or "name resolution" in error_str:
            print(f"\nDNS Resolution Issue:")
            print(f"   - The hostname '{hostname}' cannot be resolved")
            print(f"   - If using a cloud database, check your internet connection")
            print(f"   - If using localhost, try '127.0.0.1' instead")
        elif "connection refused" in error_str or "refused" in error_str:
            print(f"\nConnection Refused:")
            print(f"   - Database server is not running on {hostname}:{port}")
            print(f"   - Start PostgreSQL: sudo service postgresql start (Linux)")
            print(f"   - Or check if database service is running")
        elif "password" in error_str or "authentication" in error_str:
            print(f"\nAuthentication Issue:")
            print(f"   - Check username and password in DATABASE_URL")
            print(f"   - Verify database credentials are correct")
        elif "database" in error_str and "does not exist" in error_str:
            print(f"\nDatabase Not Found:")
            print(f"   - Database '{database}' does not exist")
            print(f"   - Create it: CREATE DATABASE {database};")
        
        return False


if __name__ == "__main__":
    try:
        result = asyncio.run(test_connection())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\n[WARN] Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

