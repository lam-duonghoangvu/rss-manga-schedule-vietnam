import argparse
import re
import sys

from utils.fetcher import fetch_schedule
from utils.parser import parse_schedule
from utils.storage import load_all_entries, save


def main():
    parser = argparse.ArgumentParser(
        description="Crawl lph.truyenbanquyen.com schedule"
    )
    parser.add_argument(
        "--month", required=True, metavar="YYYY-MM", help="Release month to fetch"
    )
    args = parser.parse_args()

    if not re.fullmatch(r"\d{4}-\d{2}", args.month):
        print(f"Error: month must be YYYY-MM, got '{args.month}'", file=sys.stderr)
        sys.exit(1)

    print(f"Fetching {args.month}…")
    html = fetch_schedule(args.month)

    print("Parsing…")
    entries = parse_schedule(html)

    month_file, root_feed = save(entries, args.month)
    total = len(load_all_entries())
    print(f"Saved {len(entries)} entries for {args.month} ({total} total across all months)")
    print(f"  RSS  : {month_file}")
    print(f"  RSS  : {root_feed}  ← served by GitHub Pages")


if __name__ == "__main__":
    main()
