"""Local URL inspection engine for Satark scam detection platform.

Performs static heuristic analysis on URLs extracted from messages:
- Extracts URLs without external network calls
- Parses hostnames, paths, and schemes with urllib.parse
- Detects URL shorteners
- Identifies suspicious/abused TLDs
- Identifies brand lookalikes / typo-squatting
- Flags raw IP hosts, excessive hyphens, and insecure HTTP
- Assigns heuristic risk tiers ('low', 'medium', 'high')
"""

import re
from typing import List, Optional, Set, Tuple
from urllib.parse import urlparse

# Pydantic schema for output contract
from schemas import LinkDetail

# ==============================================================================
# CONFIGURATION & STATIC LOOKUP TABLES
# ==============================================================================

# Common URL shortener domains
KNOWN_SHORTENERS: Set[str] = {
    "bit.ly",
    "tinyurl.com",
    "t.co",
    "goo.gl",
    "cutt.ly",
    "rb.gy",
    "is.gd",
    "shorturl.at",
    "ow.ly",
    "buff.ly",
    "tiny.cc",
    "rebrand.ly",
    "t.ly",
    "v.gd",
    "clck.ru",
}

# Frequently abused / high-risk top level domains in fraud campaigns
SUSPICIOUS_TLDS: Set[str] = {
    "xyz",
    "top",
    "click",
    "live",
    "site",
    "online",
    "icu",
    "buzz",
    "cfd",
    "cc",
    "tk",
    "ml",
    "ga",
    "gq",
    "work",
    "link",
    "loan",
    "win",
    "vip",
    "rest",
    "shop",
    "club",
    "info",
    "cam",
    "sbs",
}

# Target brands mapped to their legitimate domains
# If brand keyword appears in domain, but domain is NOT in authorized set -> flag lookalike
BRAND_DOMAINS = {
    "sbi": {"sbi.co.in", "onlinesbi.sbi", "onlinesbi.com", "sbi.bank.in"},
    "hdfc": {"hdfcbank.com", "hdfc.com"},
    "icici": {"icicibank.com", "icici.com"},
    "axis": {"axisbank.com"},
    "pnb": {"pnbindia.in"},
    "kotak": {"kotak.com"},
    "paytm": {"paytm.com", "paytmbank.com"},
    "phonepe": {"phonepe.com"},
    "gpay": {"google.com", "pay.google.com"},
    "google": {"google.com", "google.co.in"},
    "amazon": {"amazon.in", "amazon.com"},
    "flipkart": {"flipkart.com"},
    "swiggy": {"swiggy.com"},
    "zomato": {"zomato.com"},
    "jio": {"jio.com"},
    "airtel": {"airtel.in", "airtel.com"},
    "incometax": {"incometax.gov.in"},
    "epfo": {"epfindia.gov.in"},
    "uidai": {"uidai.gov.in"},
}

# Regex for finding URLs with or without scheme (catches http://, https://, www., shorteners, and TLD-based paths)
URL_EXTRACT_REGEX = re.compile(
    r"\b(?:https?://|www\.)[^\s<>'\"`]+|"
    r"\b(?:bit\.ly|tinyurl\.com|t\.co|cutt\.ly|rb\.gy|is\.gd|shorturl\.at)/[^\s<>'\"`]+|"
    r"\b[a-zA-Z0-9-]+\.(?:xyz|top|click|live|site|online|icu|buzz|cfd|cc|tk|ml|ga|link|app|info)(?:/[^\s<>'\"`]+)?",
    re.IGNORECASE,
)

# Regex to check if host is an IPv4 address
IPV4_REGEX = re.compile(r"^(?:\d{1,3}\.){3}\d{1,3}$")


def extract_urls(text: str) -> List[str]:
    """Extracts raw candidate URLs from text string, stripping trailing punctuation.

    Args:
        text: Input message text.

    Returns:
        List of deduplicated URL strings in order of occurrence.
    """
    urls: List[str] = []

    for match in URL_EXTRACT_REGEX.finditer(text):
        candidate = match.group(0).strip()

        # Clean trailing punctuation
        candidate = re.sub(r"[.,;:!?'\"\)>\]]+$", "", candidate)

        # Basic sanity check
        if "." in candidate and len(candidate) >= 4:
            # If candidate already starts with http/https/www, it's valid
            if re.match(r"^(?:https?://|www\.)", candidate, re.IGNORECASE):
                if candidate not in urls:
                    urls.append(candidate)
            else:
                # For bare domains like bit.ly/123, check the host part before the first slash
                host_part = candidate.split("/")[0]
                host_segments = host_part.split(".")
                if len(host_segments) >= 2 and any(seg.isalpha() for seg in host_segments[1:]):
                    if candidate not in urls:
                        urls.append(candidate)

    return urls


def parse_domain_info(raw_url: str) -> Tuple[str, str, str, bool]:
    """Parses a raw URL into normalized scheme, domain, path, and security status.

    Args:
        raw_url: Candidate URL string.

    Returns:
        Tuple of (normalized_url, hostname, path, is_https).
    """
    url_to_parse = raw_url
    # If no protocol scheme is given, default to http for parsing purposes
    if not re.match(r"^https?://", url_to_parse, re.IGNORECASE):
        url_to_parse = "http://" + url_to_parse

    parsed = urlparse(url_to_parse)
    hostname = (parsed.hostname or "").lower().strip()
    path = parsed.path or ""
    is_https = parsed.scheme.lower() == "https"

    return raw_url, hostname, path, is_https


def detect_brand_lookalike(hostname: str) -> Optional[str]:
    """Detects if hostname mimics a legitimate bank or brand without being official.

    Args:
        hostname: Normalized domain name.

    Returns:
        Brand name string if impersonated (e.g., 'SBI'), else None.
    """
    # Clean port or subdomains for inspection
    for brand, legit_domains in BRAND_DOMAINS.items():
        # Check if the domain itself is already verified as legitimate
        if any(hostname == d or hostname.endswith("." + d) for d in legit_domains):
            continue

        # Look for the brand keyword surrounded by hyphens, dots, or word boundaries
        brand_pattern = rf"(?:^|[-.]){re.escape(brand)}(?:[-.]|$)"
        if re.search(brand_pattern, hostname) or brand in hostname:
            return brand.upper()

    return None


def inspect_single_url(raw_url: str) -> LinkDetail:
    """Performs deep heuristic security analysis on a single extracted URL.

    Args:
        raw_url: URL to analyze.

    Returns:
        LinkDetail object matching API schema contract.
    """
    _, hostname, path, is_https = parse_domain_info(raw_url)

    # 1. URL Shortener check
    is_shortener = hostname in KNOWN_SHORTENERS or any(
        hostname.endswith("." + s) for s in KNOWN_SHORTENERS
    )

    # 2. Suspicious TLD check
    tld = hostname.split(".")[-1] if "." in hostname else ""
    suspicious_tld = tld in SUSPICIOUS_TLDS

    # 3. Brand lookalike check
    lookalike_of = detect_brand_lookalike(hostname)

    # 4. Raw IP address host
    is_ip = bool(IPV4_REGEX.match(hostname))

    # 5. Domain complexity heuristics (excessive hyphens / subdomains)
    excessive_hyphens = hostname.count("-") >= 2
    excessive_subdomains = hostname.count(".") >= 3

    # Calculate heuristic risk score
    risk_points = 0
    if lookalike_of:
        risk_points += 50
    if is_ip:
        risk_points += 45
    if suspicious_tld:
        risk_points += 30
    if is_shortener:
        risk_points += 25
    if not is_https:
        risk_points += 15
    if excessive_hyphens:
        risk_points += 15
    if excessive_subdomains:
        risk_points += 10

    # Risk tier determination
    if risk_points >= 40:
        risk = "high"
    elif risk_points >= 20:
        risk = "medium"
    else:
        risk = "low"

    return LinkDetail(
        url=raw_url,
        domain=hostname,
        is_shortener=is_shortener,
        suspicious_tld=suspicious_tld,
        lookalike_of=lookalike_of,
        risk=risk,
    )


def inspect_urls(text: str) -> List[LinkDetail]:
    """Finds all URLs in text and executes heuristic inspection on each.

    Args:
        text: Input message to inspect.

    Returns:
        List of LinkDetail objects.
    """
    extracted = extract_urls(text)
    return [inspect_single_url(u) for u in extracted]
