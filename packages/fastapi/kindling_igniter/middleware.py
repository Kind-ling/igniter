"""
Kindling Igniter FastAPI middleware.

Provides x402 payment gating as a decorator for FastAPI route handlers.
"""

from __future__ import annotations

import functools
from typing import Callable, Optional, Union

from fastapi import Request
from fastapi.responses import JSONResponse

KINDLING_VERSION = "0.1.0"
USDC_BASE = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
DEFAULT_FACILITATOR = "https://x402.org/facilitator"


class KindlingPayment:
    """
    FastAPI decorator for x402 payment gating.

    Returns 402 with x402-compliant payment request when no x-payment
    header is present. Passes through when payment header is present.

    Args:
        pay_to: Service provider wallet address (required)
        amount: Amount in smallest units. USDC has 6 decimals: $0.10 = 100000
        chain_id: Chain ID (default: 8453 for Base mainnet)
        asset: Payment asset symbol (default: "USDC")
        asset_address: Payment asset contract address (default: USDC on Base)
        facilitator: x402 facilitator URL
        referral_wallet: Referring wallet address
        referral_split_pct: Referral split percentage 0-100 (default: 15)
        max_age_seconds: Maximum payment receipt age in seconds (default: 60)

    Example:
        @app.get("/api/forecast")
        @KindlingPayment(pay_to="0xYourWallet", amount=50000)
        async def forecast(request: Request):
            return {"forecast": "..."}
    """

    def __init__(
        self,
        pay_to: str,
        amount: Union[str, int],
        chain_id: int = 8453,
        chain: str = "base",
        asset: str = "USDC",
        asset_address: str = USDC_BASE,
        facilitator: str = DEFAULT_FACILITATOR,
        referral_wallet: Optional[str] = None,
        referral_split_pct: int = 15,
        max_age_seconds: int = 60,
    ) -> None:
        self.pay_to = pay_to
        self.amount = str(amount)
        self.chain_id = chain_id
        self.chain = chain
        self.asset = asset
        self.asset_address = asset_address
        self.facilitator = facilitator
        self.referral_wallet = referral_wallet
        self.referral_split_pct = referral_split_pct
        self.max_age_seconds = max_age_seconds

    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(request: Request, *args, **kwargs):  # type: ignore[no-untyped-def]
            payment = request.headers.get("x-payment")

            if payment:
                return await func(request, *args, **kwargs)

            return JSONResponse(
                status_code=402,
                content={
                    "version": "1.0",
                    "maxAmountRequired": self.amount,
                    "asset": self.asset,
                    "assetAddress": self.asset_address,
                    "payTo": self.pay_to,
                    "chainId": self.chain_id,
                    "chain": self.chain,
                    "facilitator": self.facilitator,
                    "maxAgeSeconds": self.max_age_seconds,
                    "referral_split_pct": self.referral_split_pct,
                    "referral_wallet": self.referral_wallet,
                    "referral_disclosure": (
                        f"{self.referral_split_pct}% of payment settles to the referring wallet. "
                        "Built with Kindling Igniter. Economics are on-chain and auditable. "
                        "See: github.com/kind-ling/igniter"
                    ),
                    "built_with": f"kindling-igniter@{KINDLING_VERSION}",
                },
            )

        return wrapper
