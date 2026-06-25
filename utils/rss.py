from collections import defaultdict
from datetime import datetime, timezone, timedelta
from email.utils import format_datetime
from xml.sax.saxutils import escape

from .fetcher import BASE_URL

FEED_TITLE = "Lịch Phát Hành Truyện Bản Quyền"
FEED_DESCRIPTION = "Lịch phát hành Manga & Light Novel bản quyền tại Việt Nam"
ICT = timezone(timedelta(hours=7))


def _rss_date(date_str: str) -> str:
    dt = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=ICT)
    return format_datetime(dt)


def _month_description(month_entries: list[dict], month_key: str) -> str:
    year, mon = month_key.split("-")

    by_day: dict[str, list[dict]] = defaultdict(list)
    for entry in month_entries:
        by_day[entry["release_date"][8:]].append(entry)

    rows = []
    for day in sorted(by_day):
        rows.append(f'          <tr><td colspan="2" align="left"><h1>{day}</h1></td></tr>')
        for e in by_day[day]:
            title = escape(e["title"])
            volume = escape((e["volume_number"] or "").removeprefix("Tập "))
            price = escape((e["price"] or "").removesuffix("\xa0₫").removesuffix(" ₫"))
            rows.append(f'          <tr><td align="left">{title} - {volume}</td><td align="right">{price}</td></tr>')

    rows_xml = "\n".join(rows)
    return (
        f'        <p>Lịch phát hành Manga & Light Novel bản quyền tại Việt Nam trong tháng {mon}/{year}</p>\n'
        f'        <table width="100%">\n'
        f'{rows_xml}\n'
        f'        </table>'
    )


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
        year, mon = month_key.split("-")
        month_title = f"Tháng {mon}, {year}"
        desc = _month_description(by_month[month_key], month_key)
        item = (
            "    <item>\n"
            f"      <title>{escape(month_title)}</title>\n"
            f'      <guid isPermaLink="false">{escape(channel_link)}#{escape(month_key)}</guid>\n'
            f"      <pubDate>{_rss_date(f'{month_key}-01')}</pubDate>\n"
            f"      <description>\n      <![CDATA[\n{desc}\n      ]]>\n      </description>\n"
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
