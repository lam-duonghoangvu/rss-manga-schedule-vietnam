import re

from bs4 import BeautifulSoup


def parse_card(a_tag) -> dict | None:
    badge = a_tag.find("span", class_=re.compile(r"\bbg-amber-"))
    edition = badge.get_text(strip=True) if badge else None

    img = a_tag.find("img")
    photo = img["src"] if img else None

    title_div = a_tag.find("div", class_=re.compile(r"\bdecoration-primary-400\b"))
    title = title_div.get_text(strip=True) if title_div else None

    space_y1 = a_tag.find("div", class_=re.compile(r"\bspace-y-1\b"))
    volume = None
    if space_y1:
        children = space_y1.find_all("div", recursive=False)
        if len(children) >= 2:
            volume = children[1].get_text(strip=True)

    price_span = a_tag.find("span", class_=re.compile(r"\bblock\b"))
    price = price_span.get_text(strip=True) if price_span else None

    if not title:
        return None

    return {
        "href": a_tag.get("href", ""),
        "title": title,
        "volume_number": volume,
        "volume_photo": photo,
        "price": price,
        "edition": edition,
    }


def parse_schedule(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    results = []

    for day_div in soup.find_all("div", class_="release-day"):
        release_date = day_div.get("id")
        if not release_date:
            continue

        groups: dict[tuple, list[dict]] = {}
        for a_tag in day_div.find_all("a", href=re.compile(r"tana\.moe/title/")):
            card = parse_card(a_tag)
            if not card:
                continue
            key = (card["href"], card["volume_number"])
            groups.setdefault(key, []).append(card)

        for cards in groups.values():
            standard = [c for c in cards if c["edition"] is None]
            editions = [c for c in cards if c["edition"] is not None]

            main = standard[0] if standard else editions[0]
            others = editions + standard[1:] if standard else editions[1:]

            results.append(
                {
                    "title": main["title"],
                    "volume_number": main["volume_number"],
                    "volume_photo": main["volume_photo"],
                    "url": main["href"],
                    "release_date": release_date,
                    "price": main["price"],
                    "other_editions": [
                        {"edition": c["edition"], "price": c["price"]} for c in others
                    ],
                }
            )

    return results
