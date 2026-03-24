# kindling-igniter

FastAPI x402 payment middleware for Kindling.

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

See [github.com/Kind-ling/igniter](https://github.com/Kind-ling/igniter) for full docs.
