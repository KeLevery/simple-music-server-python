import pytest
import sys
from pathlib import Path
from httpx import AsyncClient, ASGITransport

# Ensure app package is in sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app

@pytest.fixture
def anyio_backend():
    return "asyncio"

@pytest.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
