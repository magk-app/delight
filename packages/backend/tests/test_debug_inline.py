"""Debug test to check settings.ENVIRONMENT"""
import sys
import os

def test_check_environment_in_tests_dir():
    """Check what ENVIRONMENT value is being used"""
    from app.core.config import settings
    import app.core.clerk_auth
    
    print(f"\n=== ENVIRONMENT DEBUG ===")
    print(f"os.environ['ENVIRONMENT']: {os.environ.get('ENVIRONMENT')}")
    print(f"settings.ENVIRONMENT: {settings.ENVIRONMENT}")
    print(f"clerk_auth.settings.ENVIRONMENT: {app.core.clerk_auth.settings.ENVIRONMENT}")
    print(f"Is test env? {settings.ENVIRONMENT in ['test', 'testing']}")
    
    assert settings.ENVIRONMENT == "test", f"Expected 'test' but got '{settings.ENVIRONMENT}'"
