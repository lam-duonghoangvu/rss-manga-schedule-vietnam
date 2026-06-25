import re

from bs4 import BeautifulSoup


def parse_card(anchor) -> dict | None:
    badge = anchor.find("span", class_=re.compile(r"\bbg-amber-"))
    edition = badge.get_text(strip=True) if badge else None

    image = anchor.find("img")
    photo = image["src"] if image else None

    title_div = anchor.find("div", class_=re.compile(r"\bdecoration-primary-400\b"))
    title = title_div.get_text(strip=True) if title_div else None

    volume_container = anchor.find("div", class_=re.compile(r"\bspace-y-1\b"))
    volume = None
    if volume_container:
        children = volume_container.find_all("div", recursive=False)
        if len(children) >= 2:
            volume = children[1].get_text(strip=True)

    price_span = anchor.find("span", class_=re.compile(r"\bblock\b"))
    price = price_span.get_text(strip=True) if price_span else None

    if not title:
        return None

    return {
        "href": anchor.get("href", ""),
        "title": title,
        "volume_number": volume,
        "volume_photo": photo,
        "price": price,
        "edition": edition,
    }


def parse_schedule(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    results = []

    for day_section in soup.find_all("div", class_="release-day"):
        release_date = day_section.get("id")
        if not release_date:
            continue

        groups: dict[tuple, list[dict]] = {}
        for anchor in day_section.find_all("a", href=re.compile(r"tana\.moe/title/")):
            card = parse_card(anchor)
            if not card:
                continue
            key = (card["href"], card["volume_number"])
            groups.setdefault(key, []).append(card)

        for cards in groups.values():
            standard = [card for card in cards if card["edition"] is None]
            editions = [card for card in cards if card["edition"] is not None]

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
                        {"edition": card["edition"], "price": card["price"]}
                        for card in others
                    ],
                }
            )

    return results
