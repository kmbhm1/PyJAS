from urllib.parse import urlparse


def is_valid_uri(url: str) -> bool:
    """Validate that the URL is properly formed."""
    parsed = urlparse(url)
    return (
        all([parsed.scheme, parsed.netloc])
        or all([parsed.scheme, parsed.path])
        or bool(parsed.path)  # Allow relative URIs
    )
