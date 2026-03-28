# Igniter — Spec 001: FastAPI Adapter [NEXT]

## Task: Build Python/FastAPI x402 middleware adapter

### Context
Igniter v0.1.0 ships Express middleware. Many agent services run on FastAPI (Python). The FastAPI adapter is the highest-leverage expansion — it opens the Python agent ecosystem.

### Goal
A pip-installable `kindling-igniter` package with FastAPI middleware that matches the Express adapter's behavior: x402 payment gating, A2A card generation, MCP tool definition helpers, referral economics disclosure.

### Acceptance Criteria
- [ ] FastAPI middleware that returns 402 on unpaid requests
- [ ] A2A Agent Card auto-generated from FastAPI route decorators
- [ ] MCP tool definition helpers
- [ ] Referral split disclosed in 402 response before payment
- [ ] First-party labeled is_first_party: true in A2A output
- [ ] pytest suite with 90%+ coverage
- [ ] Published to PyPI as kindling-igniter

### Constraints
- Python 3.11+, type hints throughout
- No referral split can influence routing order
- Follow CLAUDE.md conventions

### Model Routing
- Implementation: sonnet
- Security review: opus (referral economics are security-sensitive)
