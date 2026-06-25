from pathlib import Path

from rss import entries_from_rss, generate_rss


def load_all_entries() -> list[dict]:
    all_entries: list[dict] = []
    for xml_file in sorted(Path("schedule").glob("*.xml")):
        all_entries.extend(entries_from_rss(xml_file))
    all_entries.sort(key=lambda e: e["release_date"])
    return all_entries


def save(entries: list[dict], month: str) -> tuple[Path, Path]:
    Path("schedule").mkdir(exist_ok=True)

    yyyymm = month.replace("-", "")
    month_file = Path("schedule") / f"{yyyymm}.xml"
    month_file.write_text(generate_rss(entries, month), encoding="utf-8")

    root_feed = Path("feed.xml")
    root_feed.write_text(generate_rss(load_all_entries()), encoding="utf-8")

    return month_file, root_feed
