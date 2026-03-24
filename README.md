# Kindling Igniter

> x402 + MCP + A2A scaffolding for any agent service. Ship in 5 minutes.

[![CI](https://github.com/Kind-ling/igniter/actions/workflows/ci.yml/badge.svg)](https://github.com/Kind-ling/igniter/actions/workflows/ci.yml)
[![npm](https://img.shields.io/npm/v/@kindling/igniter)](https://www.npmjs.com/package/@kindling/igniter)
[![PyPI](https://img.shields.io/pypi/v/kindling-igniter)](https://pypi.org/project/kindling-igniter/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Part of [Kindling](https://github.com/Kind-ling/docs) — open infrastructure for the agent economy.

---

## What it does

Kindling Igniter adds three things to any service:

1. **x402 payment middleware** — agents pay before accessing your API. 402 response includes full economics disclosure before payment.
2. **A2A Agent Card** — machine-readable capability declaration served at `/.well-known/agent.json`
3. **MCP tool definitions** — semantic-search-optimized tool descriptions

**Every 402 response discloses referral economics.** There are no hidden splits. Agents see the economics before they pay.

---

## Quick Start

### Express

```bash
npm install @kindling/igniter
```

```typescript
import express from 'express';
import { kindlingPayment } from '@kindling/igniter';

const app = express();

app.get('/api/forecast/:asset',
  kindlingPayment({
    payTo: '0xYourWallet',
    amount: '50000', // $0.05 USDC (6 decimals)
  }),
  (req, res) => {
    res.json({ forecast: '...' });
  }
);
```

### FastAPI

```bash
pip install kindling-igniter
```

```python
from fastapi import FastAPI, Request
from kindling_igniter import KindlingPayment

app = FastAPI()

@app.get("/api/forecast/{asset}")
@KindlingPayment(pay_to="0xYourWallet", amount=50000)  # $0.05 USDC
async def forecast(asset: str, request: Request):
    return {"forecast": "..."}
```

---

## 402 Response

When an agent calls without payment, they receive:

```json
{
  "version": "1.0",
  "maxAmountRequired": "50000",
  "asset": "USDC",
  "assetAddress": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
  "payTo": "0xYourWallet",
  "chainId": 8453,
  "facilitator": "https://x402.org/facilitator",
  "referral_split_pct": 15,
  "referral_wallet": null,
  "referral_disclosure": "15% of payment settles to the referring wallet. Built with Kindling Igniter. Economics are on-chain and auditable. See: github.com/kind-ling/igniter",
  "built_with": "@kindling/igniter@0.1.0"
}
```

The agent pays via x402, then retries with the `x-payment` header. Your handler is called.

---

## A2A Agent Card

```typescript
import { generateAgentCard } from '@kindling/igniter';

const card = generateAgentCard({
  name: 'My Forecast Service',
  description: 'Probabilistic market forecasts with confidence intervals',
  url: 'https://api.yourservice.com',
  organization: 'Your Org',
  skills: [{
    id: 'generate_forecast',
    name: 'Generate Forecast',
    description: 'Returns probabilistic forecast with confidence interval',
    tags: ['forecast', 'prediction', 'market'],
    examples: ['Generate a 4-hour BTC forecast'],
  }],
});

// Serve at /.well-known/agent.json
app.get('/.well-known/agent.json', (_req, res) => res.json(card));
```

---

## Configuration

All defaults are documented in [kindling.config.yml](./kindling.config.yml).

| Parameter | Default | Description |
|-----------|---------|-------------|
| `chainId` | `8453` | Base mainnet. Use `84532` for Sepolia testnet. |
| `asset` | `USDC` | Payment asset |
| `assetAddress` | USDC on Base | `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` |
| `facilitator` | `https://x402.org/facilitator` | x402 payment verifier |
| `referralSplitPct` | `15` | Referral split (0–100%). Configurable per service. |
| `maxAgeSeconds` | `60` | Max payment receipt age |

---

## Referral Economics

Kindling Igniter defaults to a 15% referral split — configurable from 0 to 100%. The split is:

- Disclosed in every 402 response **before payment**
- Settled on-chain (auditable by anyone)
- Configurable: `referralSplitPct: 0` to disable

Kindling Verifier only counts referral splits ≤50% toward demand score normalization. Splits above 50% are flagged as promotional. [Full economics docs →](https://github.com/Kind-ling/docs/blob/main/economics.md)

---

## First-Party Disclosure

PUC-operated services set `isFirstParty: true` in their Agent Card config. This propagates `is_first_party: true` through all Kindling modules — Verifier, Scout routing, Documenter benchmarks. First-party services receive no scoring advantage and lose tie-breaks.

---

## Packages

| Package | Registry | Language |
|---------|---------|---------|
| `@kindling/igniter` | npm | TypeScript/Express |
| `kindling-igniter` | PyPI | Python/FastAPI |

More adapters welcome — see [contributing →](https://github.com/Kind-ling/docs/blob/main/contributing.md)

---

*Kindling Igniter v0.1.0 · [Permanent Upper Class](https://permanentupperclass.com) · MIT License*
