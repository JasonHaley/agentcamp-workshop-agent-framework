"""Contract deadline calculator skill.

Given a contract's effective date, term length, and notice period,
computes key dates deterministically -- something LLMs frequently
get wrong when doing date math "in their head".

Usage:
    python contract_deadlines.py --effective-date 2024-03-15 \
        --term-months 24 --notice-days 90

Output: JSON to stdout (easy for an agent to parse).
"""

import argparse
import json
import sys
from datetime import date, datetime, timedelta


def add_months(d: date, months: int) -> date:
    """Add calendar months, clamping to the last valid day of the month."""
    month_index = d.month - 1 + months
    year = d.year + month_index // 12
    month = month_index % 12 + 1
    # Clamp day (e.g., Jan 31 + 1 month -> Feb 28/29)
    day = min(d.day, [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28,
                      31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
    return date(year, month, day)


def business_days_between(start: date, end: date) -> int:
    """Count business days (Mon-Fri) strictly between start and end."""
    if end <= start:
        return 0
    days = 0
    current = start + timedelta(days=1)
    while current <= end:
        if current.weekday() < 5:
            days += 1
        current += timedelta(days=1)
    return days


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute contract renewal deadlines.")
    parser.add_argument("--effective-date", required=True, help="Contract effective date (YYYY-MM-DD)")
    parser.add_argument("--term-months", type=int, required=True, help="Initial term length in months")
    parser.add_argument("--notice-days", type=int, required=True, help="Non-renewal notice period in calendar days")
    parser.add_argument("--as-of", default=None, help="Reference date for 'today' (YYYY-MM-DD), defaults to current date")
    args = parser.parse_args()

    try:
        effective = datetime.strptime(args.effective_date, "%Y-%m-%d").date()
        today = (datetime.strptime(args.as_of, "%Y-%m-%d").date()
                 if args.as_of else date.today())
    except ValueError as e:
        print(json.dumps({"error": f"Invalid date format: {e}"}))
        sys.exit(1)

    term_end = add_months(effective, args.term_months)
    notice_deadline = term_end - timedelta(days=args.notice_days)
    calendar_days_left = (notice_deadline - today).days
    biz_days_left = business_days_between(today, notice_deadline)

    if calendar_days_left < 0:
        status = "MISSED - notice deadline has passed; contract will auto-renew"
    elif calendar_days_left <= 30:
        status = "URGENT - act within the next 30 days"
    elif calendar_days_left <= 90:
        status = "UPCOMING - plan your renewal decision soon"
    else:
        status = "OK - no immediate action needed"

    result = {
        "effective_date": effective.isoformat(),
        "initial_term_end": term_end.isoformat(),
        "notice_deadline": notice_deadline.isoformat(),
        "notice_deadline_weekday": notice_deadline.strftime("%A"),
        "as_of": today.isoformat(),
        "calendar_days_until_deadline": calendar_days_left,
        "business_days_until_deadline": biz_days_left,
        "status": status,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()