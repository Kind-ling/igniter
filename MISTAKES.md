# MISTAKES.md — Error Corpus

> Append-only during the day. Review weekly.

## Template

```
### [Short description]
- **Date:** YYYY-MM-DD
- **What happened:**
- **Expected:**
- **Fix:**
- **Root cause:**
- **Rule candidate:** YES/NO
```

## Known patterns (inherited from twig)

- JSON.parse on files from disk must always be in try/catch
- Payment verification stubs must return `false` by default
- Define all type union variants before implementation begins
- Grep for dead variables after implementation

## Log

*No entries yet.*
