# Igniter — Spec 001: FastAPI Adapter [NEXT]

## Task: Build Python/FastAPI x402 middleware adapter

### Context
Igniter v0.1.0 ships Express middleware. FastAPI adapter opens the Python agent ecosystem.

### Goal
pip-installable `kindling-igniter` package with FastAPI middleware: x402 payment gating, A2A card generation, MCP tool definition helpers, referral economics disclosure.

### Acceptance Criteria
- [ ] FastAPI middleware returns 402 on unpaid requests
- [ ] A2A Agent Card auto-generated from FastAPI route decorators
- [ ] MCP tool definition helpers
- [ ] Referral split disclosed in 402 response before payment
- [ ] `is_first_party: true` in A2A output where applicable
- [ ] pytest suite, 90%+ coverage
- [ ] Publishable to PyPI as `kindling-igniter`

### Constraints
- Python 3.11+, type hints throughout
- Referral split cannot influence routing order
- Follow CLAUDE.md conventions

### Model Routing
- Implementation: sonnet
- Security review: opus (referral economics are security-sensitive)
