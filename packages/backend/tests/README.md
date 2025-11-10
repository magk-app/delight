# Delight Backend Test Suite

Production-ready pytest framework for the Delight FastAPI backend.

## Setup

### Prerequisites

- Python 3.11+
- Poetry (dependency management)
- Running PostgreSQL (for integration tests with real DB)
- Running Redis (for integration tests with real Redis)

### Installation

```bash
# Install all dependencies including test dependencies
cd packages/backend
poetry install

# Install additional test dependencies if needed
poetry add --group dev faker pytest-cov aiosqlite
```

### Environment Configuration

Tests use isolated test databases by default:

- Unit tests: No database needed
- Integration tests: SQLite in-memory database (default)
- Database-specific tests: Test PostgreSQL database (configured in `conftest.py`)

For PostgreSQL-specific tests (pgvector, etc.):

1. Create test database: `createdb delight_test`
2. Update `test_database_url` fixture in `conftest.py`

## Running Tests

### Local Development

```bash
# Run all tests
poetry run pytest

# Run with verbose output
poetry run pytest -v

# Run specific test file
poetry run pytest tests/integration/test_health_endpoint.py

# Run by marker (test category)
poetry run pytest -m unit          # Unit tests only
poetry run pytest -m integration   # Integration tests only
poetry run pytest -m api           # API endpoint tests
poetry run pytest -m database      # Database tests
poetry run pytest -m slow          # Slow tests

# Run with coverage report
poetry run pytest --cov=app --cov-report=html

# Watch mode (requires pytest-watch)
poetry run ptw
```

### View Test Results

```bash
# Open HTML coverage report
start test-results/coverage/index.html  # Windows
open test-results/coverage/index.html   # Mac
xdg-open test-results/coverage/index.html  # Linux

# JUnit XML (for CI/CD)
# Automatically generated at test-results/junit.xml
```

### CI/CD

Tests run automatically on:

- Pull requests
- Commits to `main` branch

CI configuration:

- All test markers run
- Coverage report generated
- JUnit XML output for test tracking
- Fails if coverage < 70%

## Test Architecture

### Directory Structure

```
tests/
├── conftest.py              # Root fixtures (database, client, auth)
├── fixtures/                # Test data factories
│   ├── __init__.py
│   └── factories.py         # UserFactory, QuestFactory, etc.
├── helpers/                 # Utility functions
│   ├── __init__.py
│   ├── auth.py              # Mock auth helpers
│   └── database.py          # DB setup/teardown helpers
├── unit/                    # Unit tests (fast, isolated)
│   └── test_example.py
├── integration/             # Integration tests (database, APIs)
│   └── test_health_endpoint.py
└── README.md                # This file
```

### Test Categories (Markers)

Tests are organized by markers for selective execution:

- **`@pytest.mark.unit`**: Fast, pure function tests, no external dependencies
- **`@pytest.mark.integration`**: Database, Redis, or external service integration
- **`@pytest.mark.api`**: FastAPI endpoint tests using TestClient
- **`@pytest.mark.database`**: Database-specific tests (transactions, queries)
- **`@pytest.mark.redis`**: Redis-specific tests
- **`@pytest.mark.auth`**: Authentication/authorization tests
- **`@pytest.mark.slow`**: Slow-running tests (run separately in CI)

### Fixture Pattern

Tests use **pytest fixtures** for setup and teardown with automatic cleanup:

```python
import pytest
from tests.fixtures import UserFactory

@pytest.mark.integration
async def test_create_user(db_session):
    """Database session automatically rolls back after test"""
    factory = UserFactory(db_session)
    user = await factory.create_user(email="test@example.com")

    # Test logic here
    assert user["email"] == "test@example.com"

    # No cleanup needed - transaction automatically rolled back
```

**Key Fixtures (from `conftest.py`):**

- `db_session`: Database session with automatic rollback
- `client`: Async HTTP client for API testing
- `app`: FastAPI application instance
- `auth_headers`: Mock authentication headers
- `mock_clerk_user`: Mock Clerk user object

### Data Factories

Use **factories** for generating realistic test data:

```python
from tests.fixtures import UserFactory, QuestFactory

async def test_quest_creation(db_session):
    user_factory = UserFactory(db_session)
    quest_factory = QuestFactory(db_session)

    # Create user
    user = await user_factory.create_user()

    # Create quest for user
    quest = await quest_factory.create_quest(
        user_id=user["id"],
        title="Learn Python"
    )

    assert quest["title"] == "Learn Python"
    # Both automatically cleaned up via transaction rollback
```

**Benefits:**

- Realistic data with Faker
- Consistent patterns across tests
- Easy overrides for specific scenarios
- Automatic cleanup (no manual teardown)

### API Testing Pattern

Test FastAPI endpoints using the `client` fixture:

```python
import pytest
from httpx import AsyncClient

@pytest.mark.api
async def test_health_endpoint(client: AsyncClient):
    """Test health check endpoint"""
    response = await client.get("/api/v1/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
```

### Authentication Testing

Mock Clerk authentication for protected endpoints:

```python
from tests.helpers import mock_auth_dependency

@pytest.mark.auth
async def test_protected_endpoint(client, app):
    """Test endpoint requiring authentication"""
    from app.core.dependencies import get_current_user

    # Mock auth dependency
    app.dependency_overrides[get_current_user] = lambda: mock_auth_dependency()

    response = await client.get("/api/v1/protected")
    assert response.status_code == 200

    # Cleanup
    app.dependency_overrides.clear()
```

## Best Practices

### Test Design

1. **Test Isolation**: Each test should be independent

   - Use `db_session` fixture for automatic rollback
   - Don't depend on test execution order
   - Clear mocks/overrides after each test

2. **Arrange-Act-Assert (AAA) Pattern**:

   ```python
   async def test_example(db_session):
       # Arrange: Set up test data
       factory = UserFactory(db_session)
       user = await factory.create_user()

       # Act: Execute the operation
       result = await some_function(user["id"])

       # Assert: Verify the outcome
       assert result == expected_value
   ```

3. **Test Naming**: Use descriptive names

   - ✅ `test_health_endpoint_returns_200_ok`
   - ❌ `test1`

4. **Test Length**: Keep tests focused
   - One scenario per test
   - Max 20-30 lines per test
   - Break complex flows into multiple tests

### Performance

- **Fast Tests First**: Unit tests should run in milliseconds
- **Async Support**: All I/O operations use async/await
- **Database Isolation**: SQLite in-memory for speed, PostgreSQL for DB-specific tests
- **Parallel Execution**: pytest-xdist for parallel test runs (future)

### Debugging

When tests fail:

1. **Run with verbose output**:

   ```bash
   poetry run pytest -vv --tb=long
   ```

2. **Run single test**:

   ```bash
   poetry run pytest tests/integration/test_health_endpoint.py::TestHealthEndpoint::test_health_endpoint_returns_200 -v
   ```

3. **Use pytest debugging**:

   ```python
   import pytest
   pytest.set_trace()  # Breakpoint in test
   ```

4. **Check coverage for missing tests**:
   ```bash
   poetry run pytest --cov=app --cov-report=term-missing
   ```

### Common Pitfalls

❌ **Don't**: Hardcode test data in tests

```python
# Bad
user_id = "12345"
```

✅ **Do**: Use factories

```python
# Good
user = await UserFactory(db_session).create_user()
user_id = user["id"]
```

---

❌ **Don't**: Use time.sleep or arbitrary waits

```python
# Bad
import time
time.sleep(2)
```

✅ **Do**: Use async/await properly

```python
# Good
result = await async_function()
```

---

❌ **Don't**: Skip cleanup

```python
# Bad
def test_example():
    create_data()
    # No cleanup!
```

✅ **Do**: Use fixtures with automatic cleanup

```python
# Good
async def test_example(db_session):
    factory = UserFactory(db_session)
    user = await factory.create_user()
    # Automatic rollback after test
```

## Test Coverage Goals

- **Target**: 70%+ coverage for core logic
- **Priority**:
  - P0 (Critical): API endpoints, authentication, database operations
  - P1 (High): Business logic, services, agents
  - P2 (Medium): Utility functions, helpers
  - P3 (Low): Configuration, constants

Coverage reports generated in `test-results/coverage/`

## Epic 1 Test Checklist

Based on Epic 1 stories, here's what needs testing:

### Story 1.1: Infrastructure (✅ In Progress)

- ✅ Health check endpoint (tests/integration/test_health_endpoint.py)
- ⏳ Swagger UI accessibility
- ⏳ CORS configuration

### Story 1.2: Database Schema (Not Started)

- ⏳ Database connection tests
- ⏳ Migration up/down tests
- ⏳ Model CRUD operations
- ⏳ pgvector extension enabled

### Story 1.3: Clerk Authentication (Not Started)

- ⏳ Clerk webhook handler tests
- ⏳ User creation/sync tests
- ⏳ JWT validation tests
- ⏳ Protected endpoint auth tests

### Story 1.4: Onboarding Flow (Not Started)

- ⏳ Onboarding API endpoint tests
- ⏳ User preferences CRUD tests
- ⏳ Onboarding completion tracking

### Story 1.5: Deployment Pipeline (Not Started)

- ⏳ CI/CD integration
- ⏳ Test reporting
- ⏳ Coverage gates

## Knowledge Base References

This framework implements patterns from BMAD Test Architect knowledge base:

- **Fixture Architecture**: Pure function → fixture pattern with auto-cleanup
- **Data Factories**: Faker-based generation with overrides
- **Test Quality**: Deterministic, isolated, explicit assertions
- **API Testing**: FastAPI TestClient with async support

## Next Steps

1. ✅ Framework scaffolded
2. ⏳ Add tests for Story 1.2 (database schema)
3. ⏳ Add tests for Story 1.3 (authentication)
4. ⏳ Set up CI/CD pipeline
5. ⏳ Add performance tests (Story 5+)

## Support

- **Pytest Docs**: https://docs.pytest.org
- **FastAPI Testing**: https://fastapi.tiangolo.com/tutorial/testing/
- **BMAD Test Architect**: Run `@bmad/bmm/agents/tea` for expert guidance
- **Project Issues**: See GitHub Issues

---

**Framework Version**: 1.0 (BMAD v6)  
**Last Updated**: 2025-11-10  
**Next Review**: After Story 1.2 completion
