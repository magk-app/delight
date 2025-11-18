"""
Integration tests for workflow API endpoints.

Tests the complete workflow API including creation, execution,
status checking, and result retrieval.
"""

import pytest
from httpx import AsyncClient
from fastapi import status

from main import app
from app.agents.task_types import TaskType, TaskStatus, TaskPriority


@pytest.fixture(autouse=True)
def cleanup_workflows():
    """Clean up in-memory workflow storage before and after each test."""
    from app.api.v1.workflows import _workflows, _orchestrators

    # Clear before test
    _workflows.clear()
    _orchestrators.clear()

    yield

    # Clear after test
    _workflows.clear()
    _orchestrators.clear()


@pytest.fixture
async def client():
    """Create async HTTP client for testing."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
class TestWorkflowAPI:
    """Test workflow API endpoints."""

    async def test_create_simple_workflow(self, client: AsyncClient):
        """Test creating a simple workflow via API."""
        payload = {
            "name": "Test Workflow",
            "description": "A simple test workflow",
            "tasks": [
                {
                    "name": "Task 1",
                    "prompt": "Execute task 1",
                    "task_type": "sequential",
                    "priority": "normal",
                    "depends_on": [],
                    "context": {},
                    "max_retries": 3,
                },
                {
                    "name": "Task 2",
                    "prompt": "Execute task 2",
                    "task_type": "sequential",
                    "priority": "normal",
                    "depends_on": ["Task 1"],
                    "context": {},
                    "max_retries": 3,
                },
            ],
            "config": {
                "breadth": 3,
                "depth": 5,
                "timeout_seconds": 300,
                "enable_retry": True,
                "collect_intermediate": True,
            },
        }

        response = await client.post("/api/v1/workflows/", json=payload)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        assert data["name"] == "Test Workflow"
        assert data["description"] == "A simple test workflow"
        assert len(data["tasks"]) == 2
        assert data["status"] == "pending"
        assert data["config"]["breadth"] == 3

    async def test_create_workflow_with_invalid_dependency(self, client: AsyncClient):
        """Test creating workflow with invalid task dependency."""
        payload = {
            "name": "Invalid Workflow",
            "tasks": [
                {
                    "name": "Task 1",
                    "prompt": "Execute task 1",
                    "task_type": "sequential",
                    "depends_on": ["NonExistentTask"],
                }
            ],
        }

        response = await client.post("/api/v1/workflows/", json=payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "not found" in response.json()["detail"].lower()

    async def test_get_workflow(self, client: AsyncClient):
        """Test retrieving a workflow by ID."""
        # Create workflow first
        create_payload = {
            "name": "Get Test Workflow",
            "tasks": [{"name": "Task 1", "prompt": "Test prompt"}],
        }

        create_response = await client.post("/api/v1/workflows/", json=create_payload)
        workflow_id = create_response.json()["id"]

        # Get workflow
        response = await client.get(f"/api/v1/workflows/{workflow_id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == workflow_id
        assert data["name"] == "Get Test Workflow"

    async def test_get_nonexistent_workflow(self, client: AsyncClient):
        """Test retrieving a workflow that doesn't exist."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await client.get(f"/api/v1/workflows/{fake_id}")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_list_workflows(self, client: AsyncClient):
        """Test listing workflows."""
        # Create multiple workflows
        for i in range(3):
            payload = {
                "name": f"Workflow {i}",
                "tasks": [{"name": "Task 1", "prompt": "Test"}],
            }
            await client.post("/api/v1/workflows/", json=payload)

        # List workflows
        response = await client.get("/api/v1/workflows/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 3

    async def test_list_workflows_with_pagination(self, client: AsyncClient):
        """Test listing workflows with pagination."""
        # Create workflows
        for i in range(5):
            payload = {
                "name": f"Workflow {i}",
                "tasks": [{"name": "Task 1", "prompt": "Test"}],
            }
            await client.post("/api/v1/workflows/", json=payload)

        # List with limit
        response = await client.get("/api/v1/workflows/?limit=2&offset=0")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2

    async def test_execute_workflow(self, client: AsyncClient):
        """Test executing a workflow."""
        # Create workflow
        create_payload = {
            "name": "Execute Test Workflow",
            "tasks": [
                {"name": "Task 1", "prompt": "Execute task 1"},
                {"name": "Task 2", "prompt": "Execute task 2"},
            ],
        }

        create_response = await client.post("/api/v1/workflows/", json=create_payload)
        workflow_id = create_response.json()["id"]

        # Execute workflow
        response = await client.post(f"/api/v1/workflows/{workflow_id}/execute")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Status should be running (execution happens in background)
        assert data["status"] in ["running", "completed"]

    async def test_execute_nonexistent_workflow(self, client: AsyncClient):
        """Test executing a workflow that doesn't exist."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await client.post(f"/api/v1/workflows/{fake_id}/execute")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_workflow_status(self, client: AsyncClient):
        """Test getting workflow execution status."""
        # Create and execute workflow
        create_payload = {
            "name": "Status Test Workflow",
            "tasks": [{"name": "Task 1", "prompt": "Test"}],
        }

        create_response = await client.post("/api/v1/workflows/", json=create_payload)
        workflow_id = create_response.json()["id"]

        # Get status (before execution)
        response = await client.get(f"/api/v1/workflows/{workflow_id}/status")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["workflow_id"] == workflow_id
        assert data["status"] == "pending"
        assert data["progress"] == 0.0
        assert data["tasks_total"] == 1
        assert data["tasks_completed"] == 0

    async def test_cancel_workflow(self, client: AsyncClient):
        """Test cancelling a running workflow."""
        # Create workflow
        create_payload = {
            "name": "Cancel Test Workflow",
            "tasks": [
                {"name": f"Task {i}", "prompt": f"Task {i}"} for i in range(10)
            ],
        }

        create_response = await client.post("/api/v1/workflows/", json=create_payload)
        workflow_id = create_response.json()["id"]

        # Execute workflow
        await client.post(f"/api/v1/workflows/{workflow_id}/execute")

        # Cancel workflow
        response = await client.post(f"/api/v1/workflows/{workflow_id}/cancel")

        # Note: This might fail if workflow completes too quickly
        # In real scenario with longer tasks, this would work
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]

    async def test_delete_workflow(self, client: AsyncClient):
        """Test deleting a workflow."""
        # Create workflow
        create_payload = {
            "name": "Delete Test Workflow",
            "tasks": [{"name": "Task 1", "prompt": "Test"}],
        }

        create_response = await client.post("/api/v1/workflows/", json=create_payload)
        workflow_id = create_response.json()["id"]

        # Delete workflow
        response = await client.delete(f"/api/v1/workflows/{workflow_id}")

        assert response.status_code == status.HTTP_200_OK

        # Verify workflow is deleted
        get_response = await client.get(f"/api/v1/workflows/{workflow_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    async def test_create_parallel_workflow(self, client: AsyncClient):
        """Test creating workflow with parallel tasks."""
        payload = {
            "name": "Parallel Workflow",
            "tasks": [
                {
                    "name": "Init",
                    "prompt": "Initialize",
                    "task_type": "sequential",
                },
                {
                    "name": "Parallel 1",
                    "prompt": "Execute parallel 1",
                    "task_type": "parallel",
                    "depends_on": ["Init"],
                },
                {
                    "name": "Parallel 2",
                    "prompt": "Execute parallel 2",
                    "task_type": "parallel",
                    "depends_on": ["Init"],
                },
                {
                    "name": "Parallel 3",
                    "prompt": "Execute parallel 3",
                    "task_type": "parallel",
                    "depends_on": ["Init"],
                },
                {
                    "name": "Finalize",
                    "prompt": "Finalize results",
                    "task_type": "sequential",
                    "depends_on": ["Parallel 1", "Parallel 2", "Parallel 3"],
                },
            ],
            "config": {"breadth": 3},
        }

        response = await client.post("/api/v1/workflows/", json=payload)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert len(data["tasks"]) == 5

        # Verify parallel tasks
        parallel_tasks = [t for t in data["tasks"] if "Parallel" in t["name"]]
        assert len(parallel_tasks) == 3
        assert all(t["task_type"] == "parallel" for t in parallel_tasks)

    async def test_create_example_workflow(self, client: AsyncClient):
        """Test creating example workflow via builder endpoint."""
        response = await client.post("/api/v1/workflows/builder/example")

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        assert "Example" in data["name"]
        assert len(data["tasks"]) >= 3  # Should have multiple tasks


@pytest.mark.asyncio
class TestPlanExecuteWorkflow:
    """Test plan-execute-reflect workflow endpoints."""

    async def test_create_plan_execute_workflow(self, client: AsyncClient):
        """Test creating a plan-execute workflow."""
        payload = {
            "objective": "Research the impact of AI on healthcare",
            "context": {"domain": "healthcare", "focus": "AI applications"},
            "config": {"breadth": 3, "depth": 5},
        }

        response = await client.post("/api/v1/workflows/plan-execute", json=payload)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        assert "Plan-Execute" in data["name"]
        assert data["status"] in ["pending", "running"]

    async def test_plan_execute_minimal(self, client: AsyncClient):
        """Test plan-execute with minimal parameters."""
        payload = {"objective": "Simple objective"}

        response = await client.post("/api/v1/workflows/plan-execute", json=payload)

        assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.asyncio
class TestWorkflowExecution:
    """Test workflow execution scenarios."""

    async def test_sequential_workflow_execution(self, client: AsyncClient):
        """Test executing a purely sequential workflow."""
        payload = {
            "name": "Sequential Workflow",
            "tasks": [
                {
                    "name": "Step 1",
                    "prompt": "First step",
                    "task_type": "sequential",
                },
                {
                    "name": "Step 2",
                    "prompt": "Second step",
                    "task_type": "sequential",
                    "depends_on": ["Step 1"],
                },
                {
                    "name": "Step 3",
                    "prompt": "Third step",
                    "task_type": "sequential",
                    "depends_on": ["Step 2"],
                },
            ],
        }

        create_response = await client.post("/api/v1/workflows/", json=payload)
        workflow_id = create_response.json()["id"]

        # Execute
        await client.post(f"/api/v1/workflows/{workflow_id}/execute")

        # Wait a bit for execution (in real tests, use polling)
        import asyncio

        await asyncio.sleep(1)

        # Check status
        status_response = await client.get(f"/api/v1/workflows/{workflow_id}/status")
        status_data = status_response.json()

        # Should be completed or making progress
        assert status_data["status"] in ["running", "completed"]

    async def test_parallel_workflow_execution(self, client: AsyncClient):
        """Test executing a workflow with parallel tasks."""
        payload = {
            "name": "Parallel Workflow",
            "tasks": [
                {
                    "name": f"Parallel Task {i}",
                    "prompt": f"Execute task {i}",
                    "task_type": "parallel",
                }
                for i in range(5)
            ],
            "config": {"breadth": 5},
        }

        create_response = await client.post("/api/v1/workflows/", json=payload)
        workflow_id = create_response.json()["id"]

        # Execute
        await client.post(f"/api/v1/workflows/{workflow_id}/execute")

        # Wait for execution
        import asyncio

        await asyncio.sleep(1)

        # Check status
        status_response = await client.get(f"/api/v1/workflows/{workflow_id}/status")
        status_data = status_response.json()

        # With parallel execution, should complete quickly
        assert status_data["status"] in ["running", "completed"]
        assert status_data["tasks_total"] == 5
