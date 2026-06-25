from collections import defaultdict
from datetime import datetime, timezone, timedelta
from email.utils import format_datetime
from xml.sax.saxutils import escape

from .fetcher import BASE_URL

FEED_TITLE = "Lịch Phát Hành Truyện Bản Quyền"
FEED_DESCRIPTION = "Lịch phát hành manga bản quyền tại Việt Nam"
ICT = timezone(timedelta(hours=7))

_CSS = (
    "<style>"
    "table{width:100%;border-collapse:collapse;margin-bottom:15px}"
    "td{padding:4px 0;vertical-align:top}"
    "td:nth-child(1){text-align:left}"
    "td:nth-child(2){text-align:right;width:1%;white-space:nowrap;padding-left:15px}"
    "b{display:block;margin-top:10px;font-size:1.1em}"
    "</style>"
)


def _rss_date(date_str: str) -> str:
    dt = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=ICT)
    return format_datetime(dt)


def _month_description(month_entries: list[dict]) -> str:
    by_day: dict[str, list[dict]] = defaultdict(list)
    for entry in month_entries:
        by_day[entry["release_date"][8:]].append(entry)

    parts = [_CSS]
    for day in sorted(by_day):
        rows = "".join(
            f'<tr>'
            f'<td>{escape(e["title"])} - {escape((e["volume_number"] or "").removeprefix("Tập "))}</td>'
            f'<td>{escape(e["price"] or "")}</td>'
            f'</tr>'
            for e in by_day[day]
        )
        parts.append(f"<b>{day}</b><table>{rows}</table>")
    return "\n".join(parts)


def generate_rss(entries: list[dict], month: str | None = None) -> str:
    now_rfc = format_datetime(datetime.now(tz=ICT))
    if month:
        year, mon = month.split("-")
        channel_title = f"{FEED_TITLE} — {mon}/{year}"
        channel_link = f"{BASE_URL}?month={month}"
    else:
        channel_title = FEED_TITLE
        channel_link = BASE_URL

    by_month: dict[str, list[dict]] = defaultdict(list)
    for entry in entries:
        by_month[entry["release_date"][:7]].append(entry)

    items = []
    for month_key in sorted(by_month):
        month_title = datetime.strptime(month_key, "%Y-%m").strftime("%B %Y")
        desc = _month_description(by_month[month_key])
        item = (
            "    <item>\n"
            f"      <title>{escape(month_title)}</title>\n"
            f'      <guid isPermaLink="false">{escape(channel_link)}#{escape(month_key)}</guid>\n'
            f"      <pubDate>{_rss_date(f'{month_key}-01')}</pubDate>\n"
            f"      <description><![CDATA[{desc}]]></description>\n"
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
