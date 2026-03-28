"""Tests for MCP tool helpers."""

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from kindling_igniter import build_tool_definition, mcp_tool

SCHEMA = {
    "type": "object",
    "properties": {
        "location": {"type": "string", "description": "City name"},
    },
    "required": ["location"],
}


# ── build_tool_definition ──────────────────────────────────────────────────────

def test_build_tool_definition_structure():
    tool = build_tool_definition("forecast", "Get forecast", SCHEMA)
    assert tool["name"] == "forecast"
    assert tool["description"] == "Get forecast"
    assert tool["inputSchema"] == SCHEMA


def test_build_tool_definition_returns_dict():
    tool = build_tool_definition("x", "y", {})
    assert isinstance(tool, dict)


def test_build_tool_definition_empty_schema():
    tool = build_tool_definition("noop", "Does nothing", {})
    assert tool["inputSchema"] == {}


# ── mcp_tool decorator ─────────────────────────────────────────────────────────

def test_mcp_tool_attaches_meta():
    @mcp_tool(name="forecast", description="Get forecast", input_schema=SCHEMA)
    async def my_handler(request):
        return {}

    assert hasattr(my_handler, "_mcp_meta")


def test_mcp_tool_meta_correct():
    @mcp_tool(name="forecast", description="Get forecast", input_schema=SCHEMA)
    async def my_handler(request):
        return {}

    meta = my_handler._mcp_meta
    assert meta["name"] == "forecast"
    assert meta["description"] == "Get forecast"
    assert meta["inputSchema"] == SCHEMA


def test_mcp_tool_preserves_function_name():
    @mcp_tool(name="t", description="d", input_schema={})
    async def original_name(request):
        return {}

    assert original_name.__name__ == "original_name"


def test_mcp_tool_preserves_docstring():
    @mcp_tool(name="t", description="d", input_schema={})
    async def original_name(request):
        """My docstring."""
        return {}

    assert original_name.__doc__ == "My docstring."


def test_mcp_tool_still_callable_as_route():
    """Decorated handler should still work as a normal FastAPI route."""
    app = FastAPI()

    @app.get("/api/test")
    @mcp_tool(name="test_tool", description="test", input_schema={})
    async def test_endpoint(request: Request):
        return {"ok": True}

    c = TestClient(app)
    resp = c.get("/api/test")
    assert resp.status_code == 200
    assert resp.json() == {"ok": True}


def test_mcp_tool_meta_uses_input_schema_key():
    """MCP spec uses 'inputSchema' (camelCase), not 'input_schema'."""
    @mcp_tool(name="x", description="y", input_schema={"type": "object"})
    async def handler(request):
        return {}

    assert "inputSchema" in handler._mcp_meta
    assert "input_schema" not in handler._mcp_meta
