import argparse
import sys
from datetime import date

from utils.fetcher import fetch_schedule
from utils.parser import parse_schedule
from utils.storage import load_all_entries, save


def month_range(start: str, end: str) -> list[str]:
    year, month = int(start[:4]), int(start[5:])
    end_year, end_month = int(end[:4]), int(end[5:])
    months = []
    while (year, month) <= (end_year, end_month):
        months.append(f"{year:04d}-{month:02d}")
        month += 1
        if month > 12:
            month = 1
            year += 1
    return months


def main():
    today = date.today()
    default_end = f"{today.year:04d}-{today.month:02d}"

    parser = argparse.ArgumentParser(description="Fetch manga release schedules in bulk")
    parser.add_argument("--start", default="2025-01", metavar="YYYY-MM")
    parser.add_argument("--end", default=default_end, metavar="YYYY-MM")
    args = parser.parse_args()

    months = month_range(args.start, args.end)
    print(f"Fetching {len(months)} months: {months[0]} → {months[-1]}")

    for month in months:
        print(f"  {month}…", end=" ", flush=True)
        html = fetch_schedule(month)
        entries = parse_schedule(html)
        save(entries, month)
        print(f"{len(entries)} entries")

    total = len(load_all_entries())
    print(f"Done. {total} total entries across all months.")


if __name__ == "__main__":
    main()
