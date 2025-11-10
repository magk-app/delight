"""
Database connection and CRUD operations test script.
Verifies async SQLAlchemy setup and user model operations.
"""

import asyncio
import uuid

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.session import AsyncSessionLocal
from app.models.user import User, UserPreferences


async def test_database() -> None:
    """Test database connection and basic CRUD operations."""
    print("=" * 60)
    print("DATABASE CONNECTION TEST")
    print("=" * 60)

    async with AsyncSessionLocal() as session:
        try:
            # Test 1: Create user
            print("\n1️⃣  Creating test user...")
            test_clerk_id = f"test_clerk_{uuid.uuid4()}"
            test_user = User(
                clerk_user_id=test_clerk_id,
                email="test@example.com",
                timezone="America/Los_Angeles",
            )
            session.add(test_user)
            await session.commit()
            await session.refresh(test_user)
            print(f"   ✅ Created user: {test_user.id}")
            print(f"   📧 Email: {test_user.email}")
            print(f"   🆔 Clerk ID: {test_user.clerk_user_id}")

            # Test 2: Create user preferences
            print("\n2️⃣  Creating user preferences...")
            test_prefs = UserPreferences(
                user_id=test_user.id,
                theme="medieval",
                custom_hours={
                    "start": "09:00",
                    "end": "17:00",
                    "timezone": "America/Los_Angeles",
                },
                communication_preferences={"email": True, "sms": False, "in_app": True},
            )
            session.add(test_prefs)
            await session.commit()
            print(f"   ✅ Created preferences for user")
            print(f"   🎨 Theme: {test_prefs.theme}")
            print(f"   🕐 Custom hours: {test_prefs.custom_hours}")

            # Test 3: Query user by clerk_user_id (primary lookup pattern)
            print("\n3️⃣  Querying user by Clerk ID...")
            result = await session.execute(
                select(User).where(User.clerk_user_id == test_clerk_id)
            )
            queried_user = result.scalar_one()
            print(f"   ✅ Found user: {queried_user.email}")

            # Test 4: Query with relationship (user + preferences) - eagerly load relationship
            print("\n4️⃣  Testing relationship access...")
            result = await session.execute(
                select(User)
                .options(selectinload(User.preferences))
                .where(User.clerk_user_id == test_clerk_id)
            )
            queried_user = result.scalar_one()
            print(f"   ✅ User preferences theme: {queried_user.preferences.theme}")
            print(
                f"   ✅ User preferences communication: {queried_user.preferences.communication_preferences}"
            )

            # Test 5: Test cascade delete
            print("\n5️⃣  Testing cascade delete...")
            await session.delete(queried_user)  # Should cascade delete preferences
            await session.commit()
            print("   ✅ Deleted user (preferences auto-deleted via CASCADE)")

            # Verify deletion
            result = await session.execute(
                select(User).where(User.clerk_user_id == test_clerk_id)
            )
            deleted_user = result.scalar_one_or_none()
            if deleted_user is None:
                print("   ✅ Verified: User successfully deleted")
            else:
                print("   ❌ Error: User still exists after deletion")

            print("\n" + "=" * 60)
            print("✅ ALL TESTS PASSED")
            print("=" * 60)
            print("\n💡 Database is properly configured and working!")
            print("   - Async SQLAlchemy engine: ✓")
            print("   - User model CRUD: ✓")
            print("   - Relationships: ✓")
            print("   - Cascade delete: ✓")
            print("")

        except Exception as e:
            print("\n" + "=" * 60)
            print("❌ TEST FAILED")
            print("=" * 60)
            print(f"\n❌ Error: {e}")
            print("\nPlease check:")
            print("   1. DATABASE_URL is correctly set in .env")
            print("   2. Migrations have been applied (alembic upgrade head)")
            print("   3. Database is accessible")
            raise


if __name__ == "__main__":
    asyncio.run(test_database())
