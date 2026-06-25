from collections import defaultdict
from datetime import datetime, timezone, timedelta
from email.utils import format_datetime
from xml.sax.saxutils import escape

from .fetcher import BASE_URL

FEED_TITLE = "Lịch Phát Hành Truyện Bản Quyền"
FEED_DESCRIPTION = "Lịch phát hành manga bản quyền tại Việt Nam"
ICT = timezone(timedelta(hours=7))


def _rss_date(date_str: str) -> str:
    dt = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=ICT)
    return format_datetime(dt)


def generate_rss(entries: list[dict], month: str | None = None) -> str:
    now_rfc = format_datetime(datetime.now(tz=ICT))
    if month:
        year, mon = month.split("-")
        channel_title = f"{FEED_TITLE} — {mon}/{year}"
        channel_link = f"{BASE_URL}?month={month}"
    else:
        channel_title = FEED_TITLE
        channel_link = BASE_URL

    by_date: dict[str, list[dict]] = defaultdict(list)
    for entry in entries:
        by_date[entry["release_date"]].append(entry)

    items = []
    for release_date in sorted(by_date):
        lines = "\n".join(
            f"{e['title']} - {e['volume_number'] or ''}\t{e['price'] or ''}"
            for e in by_date[release_date]
        )
        item = (
            "    <item>\n"
            f"      <title>{escape(release_date)}</title>\n"
            f"      <guid isPermaLink=\"false\">{escape(channel_link)}#{escape(release_date)}</guid>\n"
            f"      <pubDate>{_rss_date(release_date)}</pubDate>\n"
            f"      <description><![CDATA[{lines}]]></description>\n"
            "    </item>"
        )
        items.append(item)

    items_xml = "\n".join(items)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0">\n'
        "  <channel>\n"
        f"    <title>{escape(channel_title)}</title>\n"
        f"    <link>{escape(channel_link)}</link>\n"
        f"    <description>{escape(FEED_DESCRIPTION)}</description>\n"
        "    <language>vi</language>\n"
        f"    <lastBuildDate>{now_rfc}</lastBuildDate>\n"
        f"{items_xml}\n"
        "  </channel>\n"
        "</rss>\n"
    )
