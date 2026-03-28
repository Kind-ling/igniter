"""Tests for A2A agent card generator."""

import pytest
from fastapi import FastAPI, Request

from kindling_igniter import X402Gate, generate_agent_card
from kindling_igniter.mcp import mcp_tool

WALLET = "0xB1e55EdD3176Ce9C9aF28F15b79e0c0eb8Fe51AA"


def make_basic_app() -> FastAPI:
    app = FastAPI(title="Test Agent", description="A test agent service")

    @app.get("/api/forecast", summary="Get weather forecast")
    async def forecast(request: Request):
        """Returns a weather forecast."""
        return {}

    @app.post("/api/data")
    async def data(request: Request):
        return {}

    return app


# ── is_first_party — mandatory field ──────────────────────────────────────────

def test_is_first_party_present_by_default():
    card = generate_agent_card(make_basic_app())
    assert "is_first_party" in card


def test_is_first_party_true_by_default():
    card = generate_agent_card(make_basic_app())
    assert card["is_first_party"] is True


def test_is_first_party_can_be_false():
    card = generate_agent_card(make_basic_app(), is_first_party=False)
    assert card["is_first_party"] is False


def test_is_first_party_first_key():
    """is_first_party is the primary trust signal — must be the first key."""
    card = generate_agent_card(make_basic_app())
    assert list(card.keys())[0] == "is_first_party"


# ── Card structure ─────────────────────────────────────────────────────────────

def test_card_has_required_fields():
    card = generate_agent_card(make_basic_app())
    for field in ("schema_version", "name", "description", "version", "capabilities", "built_with"):
        assert field in card, f"Missing field: {field}"


def test_card_name_from_app_title():
    card = generate_agent_card(make_basic_app())
    assert card["name"] == "Test Agent"


def test_card_description_from_app():
    card = generate_agent_card(make_basic_app())
    assert card["description"] == "A test agent service"


def test_card_name_override():
    card = generate_agent_card(make_basic_app(), name="My Custom Agent")
    assert card["name"] == "My Custom Agent"


def test_card_url_included_when_provided():
    card = generate_agent_card(make_basic_app(), url="https://api.example.com")
    assert card["url"] == "https://api.example.com"


def test_card_url_absent_when_not_provided():
    card = generate_agent_card(make_basic_app())
    assert "url" not in card


def test_card_built_with_includes_kindling():
    card = generate_agent_card(make_basic_app())
    assert "kindling-igniter" in card["built_with"]


# ── Route discovery ────────────────────────────────────────────────────────────

def test_capabilities_list_present():
    card = generate_agent_card(make_basic_app())
    assert isinstance(card["capabilities"], list)


def test_capabilities_include_api_routes():
    card = generate_agent_card(make_basic_app())
    paths = [c["path"] for c in card["capabilities"]]
    assert "/api/forecast" in paths
    assert "/api/data" in paths


def test_capability_has_required_fields():
    card = generate_agent_card(make_basic_app())
    forecast_cap = next(c for c in card["capabilities"] if c["path"] == "/api/forecast")
    for field in ("name", "path", "methods", "description"):
        assert field in forecast_cap


def test_capabilities_skip_internal_routes():
    card = generate_agent_card(make_basic_app())
    paths = [c["path"] for c in card["capabilities"]]
    for internal in ("/openapi.json", "/docs", "/redoc"):
        assert internal not in paths


# ── MCP metadata in A2A card ───────────────────────────────────────────────────

def test_mcp_metadata_surfaced_in_card():
    app = FastAPI(title="MCP Agent")

    @app.post("/api/search")
    @mcp_tool(
        name="search",
        description="Search for documents",
        input_schema={"type": "object", "properties": {"query": {"type": "string"}}},
    )
    async def search(request: Request):
        return {}

    card = generate_agent_card(app)
    search_cap = next(c for c in card["capabilities"] if c["path"] == "/api/search")
    assert "mcp" in search_cap
    assert search_cap["mcp"]["name"] == "search"
