import logging
from ipaddress import ip_address
from urllib.parse import urlparse


logger = logging.getLogger(__name__)

MAX_URL_LENGTH = 2048
LOCAL_HOSTNAMES = {"localhost"}


def validate_url(url: str) -> str:
    logger.debug("Validating scanner URL")
    if not isinstance(url, str) or not url.strip():
        logger.warning("URL validation failed: empty URL")
        raise ValueError("URL is required.")

    normalized_url = url.strip()
    if len(normalized_url) > MAX_URL_LENGTH:
        logger.warning("URL validation failed: URL exceeds maximum length")
        raise ValueError("URL exceeds the maximum length of 2048 characters.")

    parsed = urlparse(normalized_url)
    if parsed.scheme not in {"http", "https"}:
        logger.warning("URL validation failed: unsupported scheme=%s", parsed.scheme)
        raise ValueError("URL must begin with http:// or https://.")

    if not parsed.netloc or not parsed.hostname:
        logger.warning("URL validation failed: missing host")
        raise ValueError("URL must include a valid host.")

    hostname = parsed.hostname.lower()
    if hostname in LOCAL_HOSTNAMES or hostname.endswith(".localhost"):
        logger.warning("URL validation failed: localhost host=%s", hostname)
        raise ValueError("Localhost URLs are not allowed.")

    try:
        address = ip_address(hostname)
    except ValueError:
        logger.info("URL validation succeeded for host=%s", hostname)
        return normalized_url

    if (
        address.is_private
        or address.is_loopback
        or address.is_link_local
        or address.is_multicast
        or address.is_reserved
        or address.is_unspecified
    ):
        logger.warning("URL validation failed: non-public IP host=%s", hostname)
        raise ValueError("Local and private network URLs are not allowed.")

    logger.info("URL validation succeeded for host=%s", hostname)
    return normalized_url
