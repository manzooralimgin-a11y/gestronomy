"""Tests for MCP server tool registration and handler dispatch."""
import pytest

import mcp.types as types
from app.integrations.mcp_server import (
    mcp_server,
    mcp_app,
    handle_list_tools,
    handle_call_tool,
)


# ---------------------------------------------------------------------------
# Tool listing
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_tools_returns_three_tools() -> None:
    """The MCP server must expose exactly 3 VoiceBooker tools."""
    tools = await handle_list_tools()
    assert len(tools) == 3
    names = {t.name for t in tools}
    assert names == {"check_table_availability", "create_reservation", "cancel_reservation"}


@pytest.mark.asyncio
async def test_list_tools_have_required_schema_fields() -> None:
    """Every tool must declare a description and an inputSchema with 'required'."""
    tools = await handle_list_tools()
    for tool in tools:
        assert tool.description, f"{tool.name} has no description"
        schema = tool.inputSchema
        assert "properties" in schema, f"{tool.name} schema missing 'properties'"
        assert "required" in schema, f"{tool.name} schema missing 'required'"


# ---------------------------------------------------------------------------
# Tool dispatch — unknown tool
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_call_unknown_tool_returns_error() -> None:
    """Calling a non-existent tool should return an error message, not crash."""
    result = await handle_call_tool("nonexistent_tool", {})
    assert len(result) == 1
    assert "Error" in result[0].text or "Unknown" in result[0].text


# ---------------------------------------------------------------------------
# Tool dispatch — bad arguments (validation-only, no DB)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_check_table_availability_bad_date_format() -> None:
    """Invalid date format should return a friendly error string."""
    result = await handle_call_tool(
        "check_table_availability",
        {"date": "15-03-2026", "time": "19:00", "party_size": 4},
    )
    assert len(result) == 1
    assert "Error" in result[0].text or "Invalid" in result[0].text


@pytest.mark.asyncio
async def test_create_reservation_bad_date_format() -> None:
    """Invalid date format should return a friendly error string."""
    result = await handle_call_tool(
        "create_reservation",
        {
            "name": "Test User",
            "phone": "555-0100",
            "date": "not-a-date",
            "time": "19:00",
            "party_size": 2,
        },
    )
    assert len(result) == 1
    assert "Error" in result[0].text or "Invalid" in result[0].text


# ---------------------------------------------------------------------------
# Starlette sub-app structure
# ---------------------------------------------------------------------------


def test_mcp_app_has_sse_and_messages_routes() -> None:
    """The Starlette sub-app must declare /sse and /messages routes."""
    route_paths = {r.path for r in mcp_app.routes}
    assert "/sse" in route_paths
    assert "/messages" in route_paths


def test_mcp_server_name() -> None:
    """Server name should match what we set."""
    assert mcp_server.name == "gestronomy-voicebooker-mcp"
