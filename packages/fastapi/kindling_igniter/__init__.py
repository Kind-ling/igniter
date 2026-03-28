"""
Kindling Igniter — FastAPI x402 + MCP + A2A scaffolding.

Usage:
    from kindling_igniter import X402Gate, generate_agent_card, mcp_tool

    @app.get("/api/forecast")
    @X402Gate(pay_to="0xYourWallet", amount=50000)  # $0.05 USDC
    async def forecast(request: Request):
        return {"forecast": "..."}
"""

from .a2a import generate_agent_card
from .mcp import build_tool_definition, mcp_tool
from .middleware import KindlingPayment, X402Gate

__version__ = "0.1.0"
__all__ = [
    "KindlingPayment",
    "X402Gate",
    "generate_agent_card",
    "mcp_tool",
    "build_tool_definition",
]
