"""
Tests for Mulan Agent integration.
"""
import pytest
from backend.agent.mulan_client import MulanClient


@pytest.mark.asyncio
async def test_mulan_client_init():
    """Test Mulan client initialization."""
    client = MulanClient()
    assert client.base_url is not None
    assert client.api_key is not None


# Add more tests as needed
# Note: These tests should mock the Mulan Agent API

