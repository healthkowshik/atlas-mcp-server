"""Shared pytest fixtures for the ATLAS MCP server test suite."""

from __future__ import annotations

from collections.abc import AsyncGenerator

import pytest
from fastmcp.client import Client
from fastmcp.utilities.tests import run_server_async

from atlas.server import create_server


@pytest.fixture
async def atlas_client() -> AsyncGenerator[Client, None]:
    """Start the ATLAS MCP server and yield a connected Client.

    Scope is 'function' (default) so each test gets a fresh session.
    The server is torn down automatically after the test returns.
    """
    server = create_server()
    async with run_server_async(server) as url:
        async with Client(url) as client:
            yield client
