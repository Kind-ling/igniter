"""Tests for X402Gate FastAPI middleware."""

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from kindling_igniter import KindlingPayment, X402Gate

WALLET = "0xB1e55EdD3176Ce9C9aF28F15b79e0c0eb8Fe51AA"


def make_app(referral_split_pct: int = 15, referral_wallet: str | None = None) -> FastAPI:
    app = FastAPI()

    @app.get("/api/test")
    @X402Gate(
        pay_to=WALLET,
        amount=100000,
        referral_split_pct=referral_split_pct,
        referral_wallet=referral_wallet,
    )
    async def test_endpoint(request: Request):
        return {"ok": True}

    return app


@pytest.fixture
def client():
    return TestClient(make_app(), raise_server_exceptions=True)


# ── Basic 402 behaviour ────────────────────────────────────────────────────────

def test_returns_402_without_payment(client):
    resp = client.get("/api/test")
    assert resp.status_code == 402


def test_402_includes_required_payment_fields(client):
    body = client.get("/api/test").json()
    assert body["version"] == "1.0"
    assert body["maxAmountRequired"] == "100000"
    assert body["asset"] == "USDC"
    assert body["payTo"] == WALLET
    assert body["chainId"] == 8453
    assert body["chain"] == "base"
    assert "facilitator" in body
    assert body["maxAgeSeconds"] == 60


def test_402_includes_built_with(client):
    body = client.get("/api/test").json()
    assert "kindling-igniter" in body["built_with"]


def test_passes_through_with_payment_header(client):
    resp = client.get("/api/test", headers={"x-payment": "test-receipt"})
    assert resp.status_code == 200
    assert resp.json() == {"ok": True}


def test_integer_amount_converted_to_string():
    app = FastAPI()

    @app.get("/api/int-amount")
    @X402Gate(pay_to=WALLET, amount=50000)
    async def endpoint(request: Request):
        return {"ok": True}

    c = TestClient(app)
    body = c.get("/api/int-amount").json()
    assert body["maxAmountRequired"] == "50000"
    assert isinstance(body["maxAmountRequired"], str)


# ── Referral economics disclosure ─────────────────────────────────────────────

def test_referral_disclosure_present_before_payment_fields(client):
    """Disclosure MUST appear before payment details in key order."""
    body = client.get("/api/test").json()
    keys = list(body.keys())
    disclosure_idx = keys.index("referral_disclosure")
    version_idx = keys.index("version")
    assert disclosure_idx < version_idx, (
        "referral_disclosure must appear before payment fields"
    )


def test_referral_split_default_15(client):
    body = client.get("/api/test").json()
    assert body["referral_split_pct"] == 15
    assert "15%" in body["referral_disclosure"]


def test_referral_disclosure_contains_kindling_link(client):
    body = client.get("/api/test").json()
    assert "github.com/kind-ling/igniter" in body["referral_disclosure"]


def test_custom_referral_split():
    app = FastAPI()

    @app.get("/api/custom")
    @X402Gate(pay_to=WALLET, amount=50000, referral_split_pct=25)
    async def custom_endpoint(request: Request):
        return {"ok": True}

    body = TestClient(app).get("/api/custom").json()
    assert body["referral_split_pct"] == 25
    assert "25%" in body["referral_disclosure"]


def test_high_referral_split_flagged_promotional():
    app = FastAPI()

    @app.get("/api/promo")
    @X402Gate(pay_to=WALLET, amount=50000, referral_split_pct=60)
    async def promo_endpoint(request: Request):
        return {"ok": True}

    body = TestClient(app).get("/api/promo").json()
    assert body.get("referral_promotional") is True
    assert "PROMOTIONAL" in body["referral_disclosure"]


def test_50_pct_split_not_flagged_promotional():
    app = FastAPI()

    @app.get("/api/half")
    @X402Gate(pay_to=WALLET, amount=50000, referral_split_pct=50)
    async def half_endpoint(request: Request):
        return {"ok": True}

    body = TestClient(app).get("/api/half").json()
    assert body.get("referral_promotional") is None


def test_invalid_split_pct_raises():
    with pytest.raises(ValueError):
        X402Gate(pay_to=WALLET, amount=100, referral_split_pct=101)

    with pytest.raises(ValueError):
        X402Gate(pay_to=WALLET, amount=100, referral_split_pct=-1)


def test_referral_wallet_in_response():
    ref = "0xReferralWallet"
    body = TestClient(make_app(referral_wallet=ref)).get("/api/test").json()
    assert body["referral_wallet"] == ref


def test_referral_wallet_null_when_absent(client):
    body = client.get("/api/test").json()
    assert body["referral_wallet"] is None


# ── Alias ──────────────────────────────────────────────────────────────────────

def test_kindling_payment_alias_works():
    app = FastAPI()

    @app.get("/api/alias")
    @KindlingPayment(pay_to=WALLET, amount=100)
    async def alias_endpoint(request: Request):
        return {"ok": True}

    resp = TestClient(app).get("/api/alias")
    assert resp.status_code == 402
