"""Vendor rate lookup skill.

Looks up negotiated hourly rates from the bundled rate card and
computes engagement cost estimates with volume discounts applied.
This data is internal and not public -- it can ONLY be answered
by consulting the bundled rate_card.csv.

Usage:
    # List all vendors/roles on the rate card
    python rate_lookup.py --list

    # Look up a rate and estimate cost
    python rate_lookup.py --vendor "Contoso Consulting" \
        --role "Senior Consultant" --hours 250

Output: JSON to stdout.
"""

import argparse
import csv
import json
import sys
from pathlib import Path

RATE_CARD = Path(__file__).parent.parent / "data" / "rate_card.csv"


def load_rates() -> list[dict]:
    with open(RATE_CARD, newline="") as f:
        return list(csv.DictReader(f))


def main() -> None:
    parser = argparse.ArgumentParser(description="Look up negotiated vendor rates.")
    parser.add_argument("--vendor", help="Vendor name (case-insensitive, partial match ok)")
    parser.add_argument("--role", help="Role name (case-insensitive, partial match ok)")
    parser.add_argument("--hours", type=float, default=None, help="Estimated hours, to compute total cost")
    parser.add_argument("--list", action="store_true", help="List all vendors and roles on the rate card")
    args = parser.parse_args()

    rates = load_rates()

    if args.list:
        print(json.dumps([
            {"vendor": r["vendor"], "role": r["role"], "contract_ref": r["contract_ref"]}
            for r in rates
        ], indent=2))
        return

    if not args.vendor or not args.role:
        print(json.dumps({"error": "Provide --vendor and --role, or use --list"}))
        sys.exit(1)

    matches = [
        r for r in rates
        if args.vendor.lower() in r["vendor"].lower()
        and args.role.lower() in r["role"].lower()
    ]

    if not matches:
        vendors = sorted({r["vendor"] for r in rates})
        print(json.dumps({
            "error": f"No rate found for vendor '{args.vendor}' / role '{args.role}'",
            "known_vendors": vendors,
            "hint": "Run with --list to see all vendor/role combinations",
        }, indent=2))
        sys.exit(1)

    results = []
    for r in matches:
        rate = float(r["hourly_rate_usd"])
        tier = float(r["volume_tier_hours"])
        discount = float(r["volume_discount_pct"])
        entry = {
            "vendor": r["vendor"],
            "role": r["role"],
            "hourly_rate_usd": rate,
            "volume_discount": f"{discount:.0f}% on engagements of {tier:.0f}+ hours",
            "contract_ref": r["contract_ref"],
        }
        if args.hours is not None:
            discount_applies = args.hours >= tier
            effective_rate = rate * (1 - discount / 100) if discount_applies else rate
            entry["estimate"] = {
                "hours": args.hours,
                "volume_discount_applied": discount_applies,
                "effective_hourly_rate_usd": round(effective_rate, 2),
                "total_cost_usd": round(effective_rate * args.hours, 2),
            }
        results.append(entry)

    print(json.dumps(results if len(results) > 1 else results[0], indent=2))


if __name__ == "__main__":
    main()