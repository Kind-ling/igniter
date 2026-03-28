"""
Kindling Igniter — MCP (Model Context Protocol) helpers.

Provides the `mcp_tool` decorator that annotates FastAPI route handlers
with MCP tool definitions. The A2A card generator reads this metadata
when building the agent card.
"""

from __future__ import annotations

from typing import Any, Callable


def mcp_tool(
    name: str,
    description: str,
    input_schema: dict[str, Any],
) -> Callable:
    """
    Decorator that attaches MCP tool metadata to a FastAPI route handler.

    The metadata is read by `generate_agent_card` and included in the
    A2A agent card under each capability's `mcp` key.

    Args:
        name: MCP tool name (should be a valid identifier)
        description: Human-readable description of what the tool does
        input_schema: JSON Schema dict describing the tool's input parameters

    Returns:
        Decorator that attaches `_mcp_meta` to the wrapped function.

    Example:
        @app.post("/api/forecast")
        @mcp_tool(
            name="get_forecast",
            description="Get weather forecast for a location",
            input_schema={
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "City name"},
                },
                "required": ["location"],
            },
        )
        async def forecast(request: Request):
            ...
    """

    def decorator(func: Callable) -> Callable:
        func._mcp_meta = build_tool_definition(  # type: ignore[attr-defined]
            name=name,
            description=description,
            input_schema=input_schema,
        )
        return func

    return decorator


def build_tool_definition(
    name: str,
    description: str,
    input_schema: dict[str, Any],
) -> dict[str, Any]:
    """
    Build a standalone MCP tool definition dict.

    Args:
        name: Tool name
        description: Tool description
        input_schema: JSON Schema for the tool's inputs

    Returns:
        MCP-compliant tool definition dict
    """
    return {
        "name": name,
        "description": description,
        "inputSchema": input_schema,
    }
