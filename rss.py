from datetime import datetime, timezone, timedelta
from email.utils import format_datetime
from xml.sax.saxutils import escape

from fetcher import BASE_URL

FEED_TITLE = "Lịch Phát Hành Truyện Bản Quyền"
FEED_DESCRIPTION = "Lịch phát hành manga bản quyền tại Việt Nam"
ICT = timezone(timedelta(hours=7))


def _rss_date(date_str: str) -> str:
    dt = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=ICT)
    return format_datetime(dt)


def _item_description(entry: dict) -> str:
    parts = []
    if entry["volume_photo"]:
        parts.append(f'<img src="{escape(entry["volume_photo"])}" alt="{escape(entry["title"])}" style="max-width:200px"/>')
    parts.append(f'<p><strong>Ngày phát hành:</strong> {escape(entry["release_date"])}</p>')
    if entry["price"]:
        parts.append(f'<p><strong>Giá:</strong> {escape(entry["price"])}</p>')
    if entry["other_editions"]:
        lines = "".join(
            f'<li>{escape(e["edition"] or "")}: {escape(e["price"] or "")}</li>'
            for e in entry["other_editions"]
        )
        parts.append(f"<p><strong>Phiên bản khác:</strong></p><ul>{lines}</ul>")
    return "".join(parts)


def generate_rss(entries: list[dict], month: str | None = None) -> str:
    import json

    now_rfc = format_datetime(datetime.now(tz=ICT))
    if month:
        year, mon = month.split("-")
        channel_title = f"{FEED_TITLE} — {mon}/{year}"
        channel_link = f"{BASE_URL}?month={month}"
    else:
        channel_title = FEED_TITLE
        channel_link = BASE_URL

    items = []
    for e in entries:
        guid = f"{e['url']}#{e['volume_number']}-{e['release_date']}"
        desc_cdata = f"<![CDATA[{_item_description(e)}]]>"
        vol = e["volume_number"] or ""
        price = f" — {e['price']}" if e["price"] else ""
        item = (
            "    <item>\n"
            f"      <title>{escape(e['title'])} - {escape(vol)}{escape(price)}</title>\n"
            f"      <link>{escape(e['url'])}</link>\n"
            f"      <guid isPermaLink=\"false\">{escape(guid)}</guid>\n"
            f"      <pubDate>{_rss_date(e['release_date'])}</pubDate>\n"
            f"      <description>{desc_cdata}</description>\n"
            "    </item>"
        )
        items.append(item)

    # Embed structured data as CDATA so load_all_entries() can reconstruct entries
    # without re-parsing HTML. RSS readers ignore unknown elements.
    data_cdata = f"<![CDATA[{json.dumps(entries, ensure_ascii=False)}]]>"
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
        f"    <items_data>{data_cdata}</items_data>\n"
        f"{items_xml}\n"
        "  </channel>\n"
        "</rss>\n"
    )


def entries_from_rss(path) -> list[dict]:
    import json
    import xml.etree.ElementTree as ET

    root = ET.parse(path).getroot()
    node = root.find("channel/items_data")
    if node is None or not node.text:
        return []
    return json.loads(node.text)
