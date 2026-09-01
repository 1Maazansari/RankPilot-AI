"""
URL validation and SSRF protection for RankPilot AI.
"""

import logging
import socket
from ipaddress import ip_address
from urllib.parse import urlparse


logger = logging.getLogger(__name__)


MAX_URL_LENGTH = 2048

LOCAL_HOSTNAMES = {
    "localhost",
    "localhost.localdomain",
}

BLOCKED_HOST_SUFFIXES = (
    ".localhost",
    ".local",
    ".internal",
    ".home.arpa",
)


def _is_public_ip(address: str) -> bool:
    """
    Return True only if the IP address is publicly routable.
    """

    try:
        ip = ip_address(address)
    except ValueError:
        return False

    return not (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    )


def _resolve_hostname(hostname: str) -> set[str]:
    """
    Resolve a hostname and return all resolved IP addresses.
    """

    addresses: set[str] = set()

    try:
        results = socket.getaddrinfo(
            hostname,
            None,
            type=socket.SOCK_STREAM,
        )
    except socket.gaierror:
        logger.warning(
            "URL validation failed: hostname could not be resolved: %s",
            hostname,
        )
        raise ValueError(
            "The hostname could not be resolved."
        )

    for result in results:
        sockaddr = result[4]

        if not sockaddr:
            continue

        resolved_ip = sockaddr[0]

        # Remove IPv6 zone identifier if present.
        resolved_ip = resolved_ip.split("%", 1)[0]

        try:
            ip_address(resolved_ip)
            addresses.add(resolved_ip)
        except ValueError:
            continue

    if not addresses:
        raise ValueError(
            "The hostname did not resolve to a valid IP address."
        )

    return addresses


def validate_url(url: str) -> str:
    """
    Validate a URL before making an outbound request.

    Protection includes:
    - URL length limit
    - HTTP/HTTPS-only schemes
    - hostname validation
    - localhost blocking
    - local/internal hostname blocking
    - direct private IP blocking
    - DNS resolution checks
    - blocking hostnames resolving to private/internal IPs
    """

    logger.debug("Validating scanner URL")

    # ---------------------------------------------------------
    # 1. Basic validation
    # ---------------------------------------------------------

    if not isinstance(url, str) or not url.strip():
        logger.warning("URL validation failed: empty URL")
        raise ValueError("URL is required.")

    normalized_url = url.strip()

    if len(normalized_url) > MAX_URL_LENGTH:
        logger.warning(
            "URL validation failed: URL exceeds maximum length"
        )
        raise ValueError(
            "URL exceeds the maximum length of 2048 characters."
        )

    # ---------------------------------------------------------
    # 2. Parse URL
    # ---------------------------------------------------------

    parsed = urlparse(normalized_url)

    # ---------------------------------------------------------
    # 3. Allow only HTTP and HTTPS
    # ---------------------------------------------------------

    if parsed.scheme.lower() not in {"http", "https"}:
        logger.warning(
            "URL validation failed: unsupported scheme=%s",
            parsed.scheme,
        )
        raise ValueError(
            "URL must begin with http:// or https://."
        )

    # ---------------------------------------------------------
    # 4. Require hostname
    # ---------------------------------------------------------

    if not parsed.netloc or not parsed.hostname:
        logger.warning(
            "URL validation failed: missing host"
        )
        raise ValueError(
            "URL must include a valid host."
        )

    hostname = parsed.hostname.lower().rstrip(".")

    # ---------------------------------------------------------
    # 5. Block username/password credentials
    # ---------------------------------------------------------

    if parsed.username is not None or parsed.password is not None:
        logger.warning(
            "URL validation failed: credentials in URL"
        )
        raise ValueError(
            "URLs containing username or password credentials "
            "are not allowed."
        )

    # ---------------------------------------------------------
    # 6. Block localhost
    # ---------------------------------------------------------

    if hostname in LOCAL_HOSTNAMES:
        logger.warning(
            "URL validation failed: localhost host=%s",
            hostname,
        )
        raise ValueError(
            "Localhost URLs are not allowed."
        )

    # ---------------------------------------------------------
    # 7. Block local/internal hostnames
    # ---------------------------------------------------------

    if hostname.endswith(BLOCKED_HOST_SUFFIXES):
        logger.warning(
            "URL validation failed: local/internal hostname=%s",
            hostname,
        )
        raise ValueError(
            "Local and internal hostnames are not allowed."
        )

    # ---------------------------------------------------------
    # 8. Direct IP address check
    # ---------------------------------------------------------

    try:
        address = ip_address(hostname)
    except ValueError:
        address = None

    if address is not None:

        if not _is_public_ip(str(address)):
            logger.warning(
                "URL validation failed: non-public IP host=%s",
                hostname,
            )
            raise ValueError(
                "Local and private network URLs are not allowed."
            )

        logger.info(
            "URL validation succeeded for public IP host=%s",
            hostname,
        )

        return normalized_url

    # ---------------------------------------------------------
    # 9. Resolve hostname
    # ---------------------------------------------------------

    resolved_addresses = _resolve_hostname(hostname)

    # ---------------------------------------------------------
    # 10. Check every resolved IP
    # ---------------------------------------------------------

    for resolved_ip in resolved_addresses:

        if not _is_public_ip(resolved_ip):
            logger.warning(
                "URL validation failed: hostname=%s "
                "resolves to non-public IP=%s",
                hostname,
                resolved_ip,
            )
            raise ValueError(
                "The URL resolves to a local or private "
                "network address."
            )

    # ---------------------------------------------------------
    # 11. Success
    # ---------------------------------------------------------

    logger.info(
        "URL validation succeeded: hostname=%s resolved_ips=%s",
        hostname,
        sorted(resolved_addresses),
    )

    return normalized_url