# Shop

A minimal shop domain model: `Order` (with line items) and `LoyaltyAccount`
(a customer's tier + points). Discounting and bonus-point calculation are
deliberately left as TODOs — see `manual.pdf` for the business rules to
implement.

## Development

```bash
pip install -e ".[dev]"
pytest -q
```
