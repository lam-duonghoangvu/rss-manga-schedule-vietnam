import requests

BASE_URL = "https://lph.truyenbanquyen.com"


def fetch_schedule(month: str) -> str:
    resp = requests.get(BASE_URL, params={"month": month}, timeout=30)
    resp.raise_for_status()
    return resp.text
