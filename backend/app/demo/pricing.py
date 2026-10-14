"""Versioned application rates; historical Phase 0.5 pricing stays frozen."""

from decimal import ROUND_CEILING, Decimal

VERSION = "openai-standard-short-2026-10-13"
SOURCE = "https://developers.openai.com/api/docs/pricing"
RATES = {
    "gpt-6.1-sol": {"input": "2.00", "cached": "0.10", "write": "2.50", "output": "10.00"},
    "gpt-6-luna": {"input": "0.10", "cached": "0.01", "write": "0.125", "output": "0.50"},
    "gpt-6-astra": {"input": "10.00", "cached": "1.00", "write": "12.50", "output": "50.00"},
}


def reserve_amount(model, input_tokens, max_output):
    rate = RATES[model]
    amount = Decimal("1.05") * (
        input_tokens * (Decimal(rate["input"]) + Decimal(rate["write"]))
        + max_output * Decimal(rate["output"])
    )
    return int(amount.to_integral_value(rounding=ROUND_CEILING))


def dollars(micros):
    return micros / 1_000_000


def microdollars(value):
    return int((Decimal(str(value)) * 1_000_000).to_integral_value(rounding=ROUND_CEILING))
