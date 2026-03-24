"""Tests for KindlingPayment FastAPI middleware."""

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from kindling_igniter import KindlingPayment

WALLET = "0xB1e55EdD3176Ce9C9aF28F15b79e0c0eb8Fe51AA"


def make_app() -> FastAPI:
    app = FastAPI()

    @app.get("/api/test")
    @KindlingPayment(pay_to=WALLET, amount=100000)
    async def test_endpoint(request: Request):
        return {"ok": True}

    return app


@pytest.fixture
def client():
    return TestClient(make_app(), raise_server_exceptions=True)


def test_returns_402_without_payment(client):
    resp = client.get("/api/test")
    assert resp.status_code == 402


def test_402_includes_required_fields(client):
    resp = client.get("/api/test")
    body = resp.json()
    assert body["version"] == "1.0"
    assert body["maxAmountRequired"] == "100000"
    assert body["asset"] == "USDC"
    assert body["payTo"] == WALLET
    assert body["chainId"] == 8453


def test_402_includes_referral_disclosure(client):
    resp = client.get("/api/test")
    body = resp.json()
    assert body["referral_split_pct"] == 15
    assert "github.com/kind-ling/igniter" in body["referral_disclosure"]


def test_402_includes_built_with(client):
    resp = client.get("/api/test")
    body = resp.json()
    assert "kindling-igniter" in body["built_with"]


def test_passes_through_with_payment_header(client):
    resp = client.get("/api/test", headers={"x-payment": "test-receipt"})
    assert resp.status_code == 200
    assert resp.json() == {"ok": True}


def test_custom_referral_split():
    app = FastAPI()

    @app.get("/api/custom")
    @KindlingPayment(pay_to=WALLET, amount=50000, referral_split_pct=25)
    async def custom_endpoint(request: Request):
        return {"ok": True}

    c = TestClient(app)
    resp = c.get("/api/custom")
    body = resp.json()
    assert body["referral_split_pct"] == 25
    assert "25%" in body["referral_disclosure"]
