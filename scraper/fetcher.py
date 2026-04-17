import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; CMS-Migration-Scraper/1.0)"
}


def fetch_html(url: str) -> str:
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.text
