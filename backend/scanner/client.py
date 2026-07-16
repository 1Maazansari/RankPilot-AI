import requests

from config import SCANNER_USER_AGENT


session = requests.Session()
session.headers.update({"User-Agent": SCANNER_USER_AGENT})
