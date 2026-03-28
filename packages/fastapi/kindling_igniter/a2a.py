"""
Kindling Igniter — A2A (Agent-to-Agent) card generator.

Generates an A2A-compliant agent card from a FastAPI application's
route registry. The `is_first_party` field is MANDATORY in all output.
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI

KINDLING_VERSION = "0.1.0"


def generate_agent_card(
    app: FastAPI,
    *,
    is_first_party: bool = True,
    name: str | None = None,
    description: str | None = None,
    version: str = "1.0.0",
    url: str | None = None,
) -> dict[str, Any]:
    """
    Generate an A2A Agent Card from a FastAPI application.

    Auto-discovers routes and builds capability list.
    `is_first_party` is included in ALL output — no exceptions.

    Args:
        app: FastAPI application instance
        is_first_party: Whether this agent is operating as a first-party
            service (not via a third-party proxy). Mandatory field.
        name: Agent name (defaults to app.title)
        description: Agent description (defaults to app.description)
        version: Agent version string
        url: Base URL for the agent

    Returns:
        A2A-compliant agent card dict with is_first_party always set.
    """
    app_name = name or app.title or "Unnamed Agent"
    app_description = description or app.description or ""

    capabilities = _discover_capabilities(app)

    card: dict[str, Any] = {
        # is_first_party MUST appear first — it is the primary trust signal
        "is_first_party": is_first_party,
        "schema_version": "1.0",
        "name": app_name,
        "description": app_description,
        "version": version,
        "capabilities": capabilities,
        "built_with": f"kindling-igniter@{KINDLING_VERSION}",
    }

    if url:
        card["url"] = url

    return card


def _discover_capabilities(app: FastAPI) -> list[dict[str, Any]]:
    """Extract capabilities from FastAPI route definitions."""
    capabilities: list[dict[str, Any]] = []

    for route in app.routes:
        # Skip internal FastAPI routes (openapi, docs, etc.)
        path: str = getattr(route, "path", "")
        if path in ("/openapi.json", "/docs", "/redoc", "/docs/oauth2-redirect"):
            continue

        methods: set[str] = getattr(route, "methods", None) or {"GET"}
        endpoint = getattr(route, "endpoint", None)
        route_name: str = getattr(route, "name", "") or (
            endpoint.__name__ if endpoint else path
        )
        summary: str = getattr(route, "summary", "") or ""
        route_description: str = getattr(route, "description", "") or ""
        if not route_description and endpoint and endpoint.__doc__:
            route_description = endpoint.__doc__.strip()

        # Check if this route has MCP metadata attached
        mcp_meta: dict[str, Any] | None = getattr(endpoint, "_mcp_meta", None)

        capability: dict[str, Any] = {
            "name": route_name,
            "path": path,
            "methods": sorted(methods),
            "description": summary or route_description or "",
        }

        if mcp_meta:
            capability["mcp"] = mcp_meta

        capabilities.append(capability)

    return capabilities
