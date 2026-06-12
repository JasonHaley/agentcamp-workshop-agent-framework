---
name: vendor-rate-lookup
description: Look up the company's negotiated vendor hourly rates and estimate engagement costs with volume discounts applied. Use this skill whenever the user asks about vendor rates, consultant pricing, what a vendor engagement would cost, our negotiated or contracted rates, MSA pricing, or budgeting for external consultants. These rates are internal negotiated terms that exist ONLY in the bundled rate card — never estimate, recall, or guess a rate; always query the script.
---

# Vendor Rate Lookup

Answers questions about negotiated vendor rates using the bundled rate card (`data/rate_card.csv`). These are internal contract terms — they are not public information and cannot be answered from general knowledge. Every rate or cost figure given to the user must come from the script's output.

## How to use

Look up a rate and estimate an engagement cost:

```bash
python scripts/rate_lookup.py --vendor "Contoso" --role "Senior Consultant" --hours 250
```

See everything on the rate card:

```bash
python scripts/rate_lookup.py --list
```

Arguments:

| Argument | Description |
|---|---|
| `--vendor` | Vendor name; case-insensitive partial match (e.g., "contoso") |
| `--role` | Role name; case-insensitive partial match (e.g., "senior") |
| `--hours` | Optional estimated hours; adds a cost estimate with volume discount logic |
| `--list` | List all vendor/role combinations and contract references |

## Output

JSON on stdout. With `--hours`, includes an `estimate` block showing whether the volume discount tier was reached, the effective hourly rate, and total cost. On a failed lookup, returns the list of known vendors so you can correct the query or ask the user to clarify.

## Interpreting results for the user

- Always cite the `contract_ref` (the governing MSA) alongside any rate — users need it for procurement paperwork.
- When giving a cost estimate, state explicitly whether the volume discount applied and at what threshold, since hours estimates often hover near tier boundaries.
- If the requested hours are just below a discount tier, point out how many more hours would trigger the discount — it may change the engagement structure.
- If a vendor or role isn't on the rate card, say so plainly and list the known vendors. Do not substitute a market-rate guess.

## Limitations

- Rates are point-in-time as of the referenced MSA; flag that renewals may have changed them.
- Covers hourly T&M rates only — fixed-bid and license pricing are out of scope.