import requests

from backend.config import SCANNER_USER_AGENT

session = requests.Session()

session.headers.update({
    "User-Agent": SCANNER_USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate",   # Keep this
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
})