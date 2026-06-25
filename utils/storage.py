import json
from pathlib import Path

from .rss import generate_rss


def load_all_entries() -> list[dict]:
    all_entries = []
    for json_file in sorted(Path("data").glob("*.json")):
        all_entries.extend(json.loads(json_file.read_text(encoding="utf-8")))
    all_entries.sort(key=lambda entry: entry["release_date"])
    return all_entries


def save(entries: list[dict], month: str) -> tuple[Path, Path]:
    Path("data").mkdir(exist_ok=True)
    Path("schedule").mkdir(exist_ok=True)

    yyyymm = month.replace("-", "")

    Path("data", f"{yyyymm}.json").write_text(
        json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    month_file = Path("schedule") / f"{yyyymm}.xml"
    month_file.write_text(generate_rss(entries, month), encoding="utf-8")

    root_feed = Path("feed.xml")
    root_feed.write_text(generate_rss(load_all_entries()), encoding="utf-8")

    return month_file, root_feed
