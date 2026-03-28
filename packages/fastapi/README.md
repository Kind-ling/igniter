# kindling-igniter

> x402 + MCP + A2A scaffolding for FastAPI — agent payment gating made simple.

Part of the [Kindling](https://github.com/Kind-ling) toolkit for the agent economy.

## Install

```bash
pip install kindling-igniter
```

## Quick Start

```python
from fastapi import FastAPI, Request
from kindling_igniter import X402Gate, generate_agent_card, mcp_tool

app = FastAPI(title="My Agent", description="Does useful things")

@app.get("/api/forecast")
@X402Gate(pay_to="0xYourWallet", amount=50000)  # $0.05 USDC
@mcp_tool(
    name="get_forecast",
    description="Get weather forecast for a location",
    input_schema={
        "type": "object",
        "properties": {"location": {"type": "string"}},
        "required": ["location"],
    },
)
async def forecast(request: Request):
    return {"forecast": "sunny"}

@app.get("/.well-known/agent.json")
async def agent_card():
    return generate_agent_card(app, url="https://api.example.com")
```

## Features

### `X402Gate` — Payment Middleware

Intercepts requests and returns a `402 Payment Required` response with x402-compliant payment details when no `x-payment` header is present.

```python
@X402Gate(
    pay_to="0xYourWallet",          # required
    amount=100000,                  # $0.10 USDC (6 decimals)
    chain_id=8453,                  # Base mainnet (default)
    referral_wallet="0xPartner",    # optional referral
    referral_split_pct=15,          # 15% default; >50% flagged as promotional
)
```

**Referral economics disclosure** is always included in the 402 response, *before* payment details. Splits above 50% are flagged as `"promotional"` in the response body.

### `generate_agent_card` — A2A Card Generator

Auto-discovers routes and generates an [A2A](https://github.com/google/A2A)-compliant agent card.

```python
card = generate_agent_card(
    app,
    is_first_party=True,   # mandatory trust signal, always included
    url="https://api.example.com",
)
```

The `is_first_party` field is **mandatory** and always the first key in the output.

### `mcp_tool` — MCP Tool Decorator

Attaches MCP tool metadata to a FastAPI route. The A2A card generator picks this up automatically.

```python
@mcp_tool(
    name="search_docs",
    description="Search documentation",
    input_schema={
        "type": "object",
        "properties": {"query": {"type": "string"}},
        "required": ["query"],
    },
)
async def search(request: Request):
    ...
```

## Hard Rules

- Referral split percentage **cannot** influence routing order — it's data only.
- `is_first_party` appears in **all** A2A output, no exceptions.
- Referral economics disclosure appears **before** payment details in 402 responses.
- Splits above 50% are flagged as `"promotional"`.

## Dev

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

## License

MIT — Permanent Upper Class / Kind-ling
