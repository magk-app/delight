"""
Integration Tests: Health Check Endpoint
Tests for Story 1.1 health check endpoint

These tests verify the health endpoint returns correct status codes
and response format.
"""

import pytest
from httpx import AsyncClient
from datetime import datetime


@pytest.mark.integration
@pytest.mark.api
class TestHealthEndpoint:
    """Test suite for health check endpoint"""
    
    async def test_health_endpoint_returns_200(self, client: AsyncClient):
        """
        Story 1.1: Health check should return 200 OK
        
        Given the API is running
        When I request GET /api/v1/health
        Then I receive 200 OK
        """
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
    
    async def test_health_endpoint_returns_json(self, client: AsyncClient):
        """
        Story 1.1: Health check should return JSON
        
        Given the API is running
        When I request GET /api/v1/health
        Then I receive JSON response
        """
        response = await client.get("/api/v1/health")
        assert response.headers["content-type"] == "application/json"
    
    async def test_health_endpoint_response_structure(self, client: AsyncClient):
        """
        Story 1.1: Health check should return required fields
        
        Given the API is running
        When I request GET /api/v1/health
        Then response contains: status, database, redis, timestamp
        """
        response = await client.get("/api/v1/health")
        data = response.json()
        
        assert "status" in data
        assert "database" in data
        assert "redis" in data
        assert "timestamp" in data
    
    async def test_health_endpoint_status_values(self, client: AsyncClient):
        """
        Story 1.1: Health check status should be valid enum value
        
        Note: In Story 1.1, returns mock "healthy" status.
        Story 1.2 will add real database checks.
        """
        response = await client.get("/api/v1/health")
        data = response.json()
        
        # Status should be one of: healthy, degraded, unhealthy
        assert data["status"] in ["healthy", "degraded", "unhealthy"]
        
        # Database status should be one of: connected, disconnected
        assert data["database"] in ["connected", "disconnected"]
        
        # Redis status should be one of: connected, disconnected
        assert data["redis"] in ["connected", "disconnected"]
    
    async def test_health_endpoint_timestamp_format(self, client: AsyncClient):
        """
        Story 1.1: Health check timestamp should be ISO 8601 format
        
        Given the API is running
        When I request GET /api/v1/health
        Then timestamp is parseable as ISO 8601 datetime
        """
        response = await client.get("/api/v1/health")
        data = response.json()
        
        # Should parse without error
        timestamp = datetime.fromisoformat(data["timestamp"])
        assert isinstance(timestamp, datetime)
    
    @pytest.mark.parametrize("expected_status", [
        "healthy",  # Story 1.1 always returns "healthy" (mock)
    ])
    async def test_health_endpoint_mock_status(
        self, 
        client: AsyncClient, 
        expected_status: str
    ):
        """
        Story 1.1: Health check returns mock "healthy" status
        
        Note: Story 1.1 implementation returns mock status.
        Real connectivity checks added in Stories 1.2 (DB) and 2.1 (Redis).
        """
        response = await client.get("/api/v1/health")
        data = response.json()
        
        assert data["status"] == expected_status
        assert data["database"] == "connected"  # Mock value
        assert data["redis"] == "connected"  # Mock value


# ============================================================================
# Future Tests (Story 1.2, 2.1)
# ============================================================================

@pytest.mark.skip(reason="Story 1.2 not implemented - real DB checks")
@pytest.mark.integration
@pytest.mark.database
class TestHealthEndpointDatabaseConnectivity:
    """
    Tests for Story 1.2: Real database connectivity checks
    
    These tests will be enabled when Story 1.2 adds actual database checks.
    """
    
    async def test_health_endpoint_detects_database_failure(self, client: AsyncClient):
        """Should return 'degraded' or 'unhealthy' when database is down"""
        # TODO: Implement after Story 1.2
        pass


@pytest.mark.skip(reason="Story 2.1 not implemented - real Redis checks")
@pytest.mark.integration
@pytest.mark.redis
class TestHealthEndpointRedisConnectivity:
    """
    Tests for Story 2.1: Real Redis connectivity checks
    
    These tests will be enabled when Story 2.1 adds actual Redis checks.
    """
    
    async def test_health_endpoint_detects_redis_failure(self, client: AsyncClient):
        """Should return 'degraded' or 'unhealthy' when Redis is down"""
        # TODO: Implement after Story 2.1
        pass


# ============================================================================
# Running Tests
# ============================================================================
# Run all health tests: poetry run pytest tests/integration/test_health_endpoint.py -v
# Run integration tests: poetry run pytest -m integration
# Run API tests: poetry run pytest -m api

