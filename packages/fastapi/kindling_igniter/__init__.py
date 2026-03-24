"""
Kindling Igniter — FastAPI x402 payment middleware.

Usage:
    from kindling_igniter import KindlingPayment

    @app.get("/api/forecast")
    @KindlingPayment(pay_to="0xYourWallet", amount=50000)  # $0.05 USDC
    async def forecast(request: Request):
        return {"forecast": "..."}
"""

from .middleware import KindlingPayment

__version__ = "0.1.0"
__all__ = ["KindlingPayment"]
