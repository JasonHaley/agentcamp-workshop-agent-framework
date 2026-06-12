---
name: contract-deadline-calculator
description: Compute contract renewal dates, non-renewal notice deadlines, and days remaining with deterministic date arithmetic. Use this skill whenever the user asks about contract deadlines, renewal dates, notice periods, auto-renewal windows, "when do I need to act on this contract", or any question requiring date math on contract terms (effective dates, term lengths, notice periods). Always use this script instead of computing dates mentally — month-end clamping, leap years, and business-day counts are error-prone without it.
---

# Contract Deadline Calculator

Computes the key dates for a contract's renewal cycle from three inputs: the effective date, the initial term length, and the non-renewal notice period. Date arithmetic must be done with the bundled script, never estimated — calendar math (month-end clamping like Jan 31 + 1 month, leap years, business-day counting) is exactly where mental calculation fails.

## When to use

- The user asks when a contract renews, when notice is due, or whether a deadline has been missed.
- A contract analysis surfaces an effective date, term, and notice period, and the user needs actionable dates.
- Any question of the form "how long until we have to decide on this contract?"

## How to use

Run the bundled script with the contract's terms:

```bash
python scripts/contract_deadlines.py \
  --effective-date 2024-03-15 \
  --term-months 24 \
  --notice-days 90
```

Arguments:

| Argument | Required | Description |
|---|---|---|
| `--effective-date` | yes | Contract effective date, `YYYY-MM-DD` |
| `--term-months` | yes | Initial term length in whole months |
| `--notice-days` | yes | Non-renewal notice period in calendar days |
| `--as-of` | no | Override "today" (`YYYY-MM-DD`); defaults to the current date |

## Output

JSON on stdout:

```json
{
  "effective_date": "2024-03-15",
  "initial_term_end": "2026-03-15",
  "notice_deadline": "2025-12-15",
  "notice_deadline_weekday": "Monday",
  "as_of": "2025-06-12",
  "calendar_days_until_deadline": 186,
  "business_days_until_deadline": 132,
  "status": "OK - no immediate action needed"
}
```

Status values: `OK` (more than 90 days out), `UPCOMING` (within 90 days), `URGENT` (within 30 days), `MISSED` (deadline passed; contract will auto-renew).

## Interpreting results for the user

- Lead with the `notice_deadline` and its weekday — that is the actionable date.
- If status is `MISSED`, state clearly that the contract will auto-renew and the next opportunity to exit is the following renewal cycle.
- If the notice deadline falls on a weekend, recommend acting by the preceding Friday.
- Quote business days remaining when the user is planning work (e.g., legal review lead time); quote calendar days for general urgency.

## Limitations

- Assumes the notice period is measured in calendar days before the end of the initial term. If a contract measures notice differently (e.g., business days, or before a renewal term), say so and adjust the inputs rather than guessing.
- Does not account for public holidays in business-day counts (weekends only).
- Handles the initial term only; for contracts already in a renewal term, pass the current term's start date as `--effective-date`.
