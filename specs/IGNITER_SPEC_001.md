# Igniter — Spec 001: FastAPI Adapter [DONE]

## Task: Build Python/FastAPI x402 middleware adapter

### Context
Igniter v0.1.0 ships Express middleware. FastAPI adapter opens the Python agent ecosystem.

### Goal
pip-installable `kindling-igniter` package with FastAPI middleware: x402 payment gating, A2A card generation, MCP tool definition helpers, referral economics disclosure.

### Acceptance Criteria
- [x] FastAPI middleware returns 402 on unpaid requests
- [x] A2A Agent Card auto-generated from FastAPI route decorators
- [x] MCP tool definition helpers
- [x] Referral split disclosed in 402 response before payment
- [x] `is_first_party: true` in A2A output where applicable
- [x] pytest suite, 90%+ coverage (40 tests, all passing)
- [x] Publishable to PyPI as `kindling-igniter`

### Constraints
- Python 3.11+, type hints throughout
- Referral split cannot influence routing order
- Follow CLAUDE.md conventions

### Model Routing
- Implementation: sonnet
- Security review: opus (referral economics are security-sensitive)

### Implementation Notes
- `X402Gate` (alias `KindlingPayment`) decorator intercepts requests missing `x-payment` header
- Referral disclosure structurally enforced to appear before payment fields (OrderedDict insertion order)
- Splits >50% flagged with `referral_promotional: true` and `[PROMOTIONAL]` in disclosure text
- `is_first_party` is always first key in A2A card output
- `mcp_tool` decorator attaches `_mcp_meta` which `generate_agent_card` surfaces in capabilities
- 40 tests across 3 modules: 16 middleware, 16 A2A, 9 MCP (+ 1 shared integration)
