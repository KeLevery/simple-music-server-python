import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_health_endpoint(async_client: AsyncClient):
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "code" in data
    assert "message" in data
    assert "data" in data
    assert data["code"] == 0
    assert "status" in data["data"]
