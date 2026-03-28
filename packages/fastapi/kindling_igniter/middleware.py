"""
Kindling Igniter FastAPI middleware.

Provides x402 payment gating as a decorator (`X402Gate` / `KindlingPayment`)
for FastAPI route handlers.

Hard rules enforced here:
- Referral economics disclosure appears BEFORE payment details in 402 response.
- `referral_split_pct` > 50 is flagged as "promotional" in response.
- Referral split percentage CANNOT influence routing order — split is data only.
"""

from __future__ import annotations

import functools
from collections import OrderedDict
from typing import Any, Callable, Optional, Union

from fastapi import Request
from fastapi.responses import JSONResponse

KINDLING_VERSION = "0.1.0"
USDC_BASE = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
DEFAULT_FACILITATOR = "https://x402.org/facilitator"


def _build_402_body(
    *,
    pay_to: str,
    amount: str,
    chain_id: int,
    chain: str,
    asset: str,
    asset_address: str,
    facilitator: str,
    max_age_seconds: int,
    referral_split_pct: int,
    referral_wallet: Optional[str],
) -> dict[str, Any]:
    """
    Build the 402 response body.

    IMPORTANT: Referral economics disclosure appears FIRST, before payment
    details. This is a hard requirement — do not reorder.

    Splits above 50% are flagged as "promotional".
    """
    is_promotional = referral_split_pct > 50

    disclosure_note = (
        f"{referral_split_pct}% of payment settles to the referring wallet. "
        "Built with Kindling Igniter. Economics are on-chain and auditable. "
        "See: github.com/kind-ling/igniter"
    )
    if is_promotional:
        disclosure_note += " [PROMOTIONAL: split exceeds 50%]"

    # Referral economics disclosure MUST come before payment fields.
    # OrderedDict preserves insertion order (Python 3.7+ dicts also do,
    # but we make this structurally explicit).
    body: dict[str, Any] = OrderedDict()

    # ── 1. Referral economics disclosure (FIRST) ──────────────────────────
    body["referral_disclosure"] = disclosure_note
    body["referral_split_pct"] = referral_split_pct
    body["referral_wallet"] = referral_wallet
    if is_promotional:
        body["referral_promotional"] = True

    # ── 2. Payment details (AFTER disclosure) ─────────────────────────────
    body["version"] = "1.0"
    body["maxAmountRequired"] = amount
    body["asset"] = asset
    body["assetAddress"] = asset_address
    body["payTo"] = pay_to
    body["chainId"] = chain_id
    body["chain"] = chain
    body["facilitator"] = facilitator
    body["maxAgeSeconds"] = max_age_seconds
    body["built_with"] = f"kindling-igniter@{KINDLING_VERSION}"

    return dict(body)


class X402Gate:
    """
    FastAPI decorator for x402 payment gating.

    Returns 402 with x402-compliant payment request when no x-payment
    header is present. Passes through when payment header is present.

    Referral split percentage is purely informational — it does NOT
    influence routing order, priority, or response selection.

    Args:
        pay_to: Service provider wallet address (required)
        amount: Amount in smallest units. USDC has 6 decimals: $0.10 = 100000
        chain_id: Chain ID (default: 8453 for Base mainnet)
        chain: Chain name (default: "base")
        asset: Payment asset symbol (default: "USDC")
        asset_address: Payment asset contract address (default: USDC on Base)
        facilitator: x402 facilitator URL
        referral_wallet: Referring wallet address
        referral_split_pct: Referral split percentage 0-100 (default: 15).
            Splits above 50% are flagged as "promotional" in the response.
            This value CANNOT alter routing behaviour.
        max_age_seconds: Maximum payment receipt age in seconds (default: 60)

    Example:
        @app.get("/api/forecast")
        @X402Gate(pay_to="0xYourWallet", amount=50000)
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
        if not (0 <= referral_split_pct <= 100):
            raise ValueError(
                f"referral_split_pct must be 0-100, got {referral_split_pct}"
            )
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
        async def wrapper(request: Request, *args: Any, **kwargs: Any) -> Any:
            payment = request.headers.get("x-payment")

            if payment:
                return await func(request, *args, **kwargs)

            body = _build_402_body(
                pay_to=self.pay_to,
                amount=self.amount,
                chain_id=self.chain_id,
                chain=self.chain,
                asset=self.asset,
                asset_address=self.asset_address,
                facilitator=self.facilitator,
                max_age_seconds=self.max_age_seconds,
                referral_split_pct=self.referral_split_pct,
                referral_wallet=self.referral_wallet,
            )
            return JSONResponse(status_code=402, content=body)

        return wrapper


# Alias for backwards compatibility with the existing skeleton
KindlingPayment = X402Gate
