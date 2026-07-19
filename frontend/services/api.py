import requests

BASE_URL = "http://127.0.0.1:8000"


def scan_website(url: str):
    response = requests.post(
        f"{BASE_URL}/scan",
        json={"url": url},
        timeout=60,
    )

    response.raise_for_status()

    return response.json()