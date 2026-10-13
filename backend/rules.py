"""Heuristic rule-based scam detection engine for Indian digital messages.

Analyzes text for:
- Urgency triggers (English, Hindi, Hinglish)
- Credential sharing requests vs genuine transactional OTP delivery
- Common scam themes (KYC, loans, lottery, electricity disconnection, etc.)
- Entity impersonation (banks, payment apps, government bodies, brands)
- Payment pressure (advance fees, release fees)
- Link presence combined with risk signals
"""

import re
from dataclasses import dataclass, field
from typing import List, Tuple


# ==============================================================================
# PATTERN CATALOGS
# ==============================================================================

# Urgency patterns (English, Hindi, Hinglish)
URGENCY_PATTERNS = [
    r"\bwithin\s+\d+\s*(?:hours?|hrs?|mins?|minutes?|days?)\b",
    r"\bimmediately\b",
    r"\burgent(?:ly)?\b",
    r"\b(?:account|service|connection|sim|card)\s*(?:will\s+be|is)?\s*(?:blocked|suspended|deactivated|frozen|terminated|closed)\b",
    r"\blast\s+warning\b",
    r"\bfinal\s+notice\b",
    r"\bexpires?\s+today\b",
    r"\baction\s+required\b",
    r"\bact\s+now\b",
    # Hinglish & Hindi urgency
    r"\bturant\b",
    r"\babhi\b",
    r"\bjaldi\b",
    r"\bband\s+ho\s+jayeg[aaoei]\b",
    r"\brok\s+diya\s+jayeg[aaoei]\b",
    r"\baaj\s+hi\b",
    r"\bkhatam\s+ho\s+jayeg[aaoei]\b",
]

# Credential request patterns (attempts to harvest credentials)
CREDENTIAL_REQUEST_PATTERNS = [
    # Explicit requests to share / send / enter / verify credentials
    r"(?:share|send|provide|enter|submit|update|tell|forward|verify|fill)\s+(?:your\s+)?(?:otp|one-time\s+password|pin|mpin|cvv|password|passcode|aadhaar|pan\s*card|bank\s+details|card\s+number)",
    r"(?:link|update)\s+your\s+(?:pan|aadhaar|bank\s+account|card)",
    # Hinglish credential sharing requests
    r"(?:otp|pin|mpin|cvv|password|pan|aadhaar)\s*(?:bhejo|bhejiye|batayein|batao|share\s*karein|share\s*karo|daalo|dalein|enter\s*karein|submit\s*karein)",
]

# Genuine OTP delivery alerts (safety markers)
GENUINE_OTP_SAFETY_PATTERNS = [
    r"\bdo\s+not\s+share\s+(?:this\s+)?(?:otp|code|pin|password|details)?\s*(?:with\s+anyone)?\b",
    r"\bnever\s+share\s+(?:your\s+)?(?:otp|pin|password)\b",
    r"\bkisi\s+(?:ko|se)\s+(?:bhi\s+)?(?:share\s+na\s+karein|na\s+batayein|otp\s+na\s+dein)\b",
    r"\bis\s+your\s+(?:secret\s+)?(?:one\s+time\s+password|otp)\b",
    r"\bvalid\s+for\s+\d+\s+mins?\b",
    r"\buse\s+(?:this\s+)?(?:otp|code)\s+to\s+(?:log\s*in|verify|complete\s+your\s+order)\b",
]

# Specific scam themes
SCAM_THEMES = {
    "Fake KYC": [
        r"\b(?:update|pending|suspend(?:ed)?|block(?:ed)?|complete|link)\s*kyc\b",
        r"\bkyc\s*(?:update|pending|suspended|blocked|verification|incomplete|expired)\b",
        r"\bre-kyc\b",
        r"\bkyc\s+(?:karwayein|karein|karayein)\b",
    ],
    "Electricity Bill Threat": [
        r"(?:electricity|power|bijli)\s*(?:bill|power)?\s*(?:will\s+be\s+disconnected|disconnect(?:ed)?|kat\s+jayegi|band\s+hogi)\b",
        r"(?:tonight\s+at\s+\d+|at\s+9:30\s*pm|at\s+8:30\s*pm).*(?:disconnect|electricity)",
        r"(?:electricity\s+office|bijli\s+vibhag)",
    ],
    "Lottery / Prize / Reward": [
        r"\b(?:lottery|lucky\s+draw|congratulations.*won|you\s+won|selected\s+for\s+prize|cash\s+prize)\b",
        r"\b(?:crore|lakh)\s*(?:winner|prize|reward)\b",
        r"\bkbc\s*(?:lottery|head\s+office|lucky\s+draw)\b",
    ],
    "Fake Loan Approval": [
        r"\b(?:pre-approved|instant|congratulations.*approved)\s+loan\b",
        r"\bloan\s+approved.*(?:without\s+documents|zero\s+interest|zero\s+cibil)\b",
        r"\bdisbursal\s+ready\b",
    ],
    "Refund / Cashback": [
        r"\b(?:refund|cashback|reward\s+points|pending\s+refund)\s*(?:approved|credited|claim|pending)\b",
        r"\bclaim\s+your\s+(?:cashback|refund|reward)\b",
    ],
    "Fake Customer Care": [
        r"(?:customer\s+care|support\s+executive|helpline\s+number|electricity\s+officer)\s*(?:call|contact|toll\s*free)?\s*[\d\s+-]{10,}",
        r"\bcontact\s+(?:manager|officer|executive)\s*(?:on|at)\b",
    ],
    "Job Offer / Task Scam": [
        r"\b(?:work\s+from\s+home|part\s+time\s+job|daily\s+earning\s+up\s+to|like\s+and\s+subscribe\s+to\s+earn)\b",
        r"\bearn\s+rs\.?\s*\d+\s*(?:per\s+day|daily)\b",
    ],
}

# Impersonated brands and entities
IMPERSONATION_TARGETS = {
    "Banks": [
        r"\b(?:sbi|state\s+bank\s+of\s+india|onlinesbi)\b",
        r"\b(?:hdfc|hdfc\s+bank)\b",
        r"\b(?:icici|icici\s+bank)\b",
        r"\b(?:axis|axis\s+bank)\b",
        r"\b(?:pnb|punjab\s+national\s+bank)\b",
        r"\b(?:kotak|kotak\s+bank)\b",
        r"\b(?:bob|bank\s+of\s+baroda)\b",
    ],
    "UPI & Payment Apps": [
        r"\b(?:paytm|paytm\s+kyc|paytm\s+wallet)\b",
        r"\b(?:phonepe|phone\s+pe)\b",
        r"\b(?:google\s+pay|gpay)\b",
        r"\b(?:bhim|bhim\s+upi)\b",
    ],
    "Government & Regulatory": [
        r"\b(?:trai|telecom\s+regulatory)\b",
        r"\b(?:rbi|reserve\s+bank\s+of\s+india)\b",
        r"\b(?:income\s+tax\s+department|it\s+dept|incometax)\b",
        r"\b(?:cyber\s*crime\s*cell|police\s+department)\b",
    ],
    "E-Commerce & Courier": [
        r"\b(?:amazon|flipkart)\b",
        r"\b(?:bluedart|delhivery|india\s+post|dtdc)\b",
    ],
}

# Payment pressure & advance fee patterns
PAYMENT_PRESSURE_PATTERNS = [
    r"(?:pay|deposit|transfer|send)\s+(?:(?:rs\.?|inr|₹)?\s*[\d,]+\s*(?:to\s+claim|registration\s+fee|processing\s+fee|refundable\s+fee|tax|to\s+activate|to\s+release|small\s+fee)|(?:small\s+|token\s+|advance\s+)?(?:registration|processing|refundable|advance)?\s*(?:fee|charges|tax|amount)\s*(?:of\s+)?(?:rs\.?|inr|₹)?\s*[\d,]*)",
    r"\bupi\s+collect\s+request\b",
    r"\bpay\s+small\s+fee\b",
]

# Link detection pattern (matches URL presence within text)
LINK_REGEX = re.compile(
    r"(?:https?://|www\.)[^\s/$.?#].[^\s]*|"
    r"\b[a-zA-Z0-9-]+\.(?:xyz|top|click|live|site|online|icu|buzz|cfd|cc|tk|ml|ga|link|app|info)\b[^\s]*|"
    r"\bbit\.ly/[^\s]+|\btinyurl\.com/[^\s]+",
    re.IGNORECASE,
)


@dataclass
class RuleDetectionResult:
    """Output data of rule-based pattern matching."""

    rules_score: int
    matched_flags: List[str]
    detected_themes: List[str]
    impersonated_entities: List[str]
    asks_for_credentials: bool
    has_urgency: bool
    has_links: bool
    is_genuine_otp_alert: bool
    suspicious_phrases: List[str] = field(default_factory=list)


def extract_matched_patterns(text: str) -> RuleDetectionResult:
    """Matches text against catalogs and extracts indicators."""
    matched_flags: List[str] = []
    detected_themes: List[str] = []
    impersonated_entities: List[str] = []
    suspicious_phrases: List[str] = []

    # 1. Check for genuine OTP markers
    has_genuine_otp_markers = any(
        re.search(pat, text, re.IGNORECASE) for pat in GENUINE_OTP_SAFETY_PATTERNS
    )

    # 2. Check for links
    link_match = LINK_REGEX.search(text)
    has_links = bool(link_match)
    if has_links and link_match:
        # Check if URL itself looks suspicious or shortener
        pass

    # 3. Check for urgency triggers
    has_urgency = False
    for pat in URGENCY_PATTERNS:
        for match in re.finditer(pat, text, re.IGNORECASE):
            has_urgency = True
            suspicious_phrases.append(match.group(0))

    if has_urgency:
        matched_flags.append("Creates urgency or threatens immediate disconnection/suspension")

    # 4. Check for credential harvesting
    asks_for_credentials = False
    for pat in CREDENTIAL_REQUEST_PATTERNS:
        for match in re.finditer(pat, text, re.IGNORECASE):
            # Check if this match is part of a safety advisory like "never share..." or "do not share..."
            start_idx = match.start()
            prefix_window = text[max(0, start_idx - 25):start_idx].lower()
            if any(neg in prefix_window for neg in ["do not", "don't", "never", "na karein", "na de", "na dein", "kisi ko", "kisi se", "should not"]):
                continue
            asks_for_credentials = True
            suspicious_phrases.append(match.group(0))

    if asks_for_credentials:
        matched_flags.append("Requests sensitive credentials (OTP/PIN/Password/Aadhaar/PAN)")

    # 5. Check scam themes
    for theme_name, patterns in SCAM_THEMES.items():
        theme_matched = False
        for pat in patterns:
            for match in re.finditer(pat, text, re.IGNORECASE):
                theme_matched = True
                detected_themes.append(theme_name)
                suspicious_phrases.append(match.group(0))
        if theme_matched:
            matched_flags.append(f"Contains {theme_name} indicators")

    # 6. Check impersonation targets
    for entity_type, patterns in IMPERSONATION_TARGETS.items():
        entity_matched = False
        for pat in patterns:
            for match in re.finditer(pat, text, re.IGNORECASE):
                entity_matched = True
                impersonated_entities.append(match.group(0).upper())
                suspicious_phrases.append(match.group(0))
        if entity_matched:
            matched_flags.append(f"Mentions or impersonates {entity_type}")

    # 7. Check payment pressure
    has_payment_pressure = False
    for pat in PAYMENT_PRESSURE_PATTERNS:
        for match in re.finditer(pat, text, re.IGNORECASE):
            has_payment_pressure = True
            suspicious_phrases.append(match.group(0))

    if has_payment_pressure:
        matched_flags.append("Demands advance payment or registration fee")

    if has_links:
        matched_flags.append("Contains embedded link or external URL")
        for match in LINK_REGEX.finditer(text):
            suspicious_phrases.append(match.group(0))

    # Genuine OTP Safety Exception:
    # A message delivering an OTP with safety language ("do not share", "never share"),
    # with NO requests to share credentials, NO external links, and NO fraud themes.
    is_genuine_otp_alert = (
        has_genuine_otp_markers
        and not asks_for_credentials
        and not has_links
        and not detected_themes
        and not has_payment_pressure
    )

    # Compute base heuristic score (0-100)
    score = 0
    if is_genuine_otp_alert:
        # Legitimate OTP delivery or transaction notice
        score = 5
        # Don't mark legitimate OTP notification phrases as suspicious
        suspicious_phrases = []
        matched_flags = ["Legitimate transactional or authentication notification"]
    else:
        # Only add impersonation/link points if there are actual threat/fraud indicators
        has_fraud_context = bool(asks_for_credentials or has_urgency or detected_themes or has_payment_pressure)

        if asks_for_credentials:
            score += 40
        if has_urgency:
            score += 20
        if detected_themes:
            score += 25
        if has_payment_pressure:
            score += 30

        if has_fraud_context:
            if impersonated_entities:
                score += 15
            if has_links:
                score += 20
        else:
            # Informational message mentioning a brand or clean link without threats
            if impersonated_entities:
                score += 5
            if has_links:
                score += 10

    # Clean up and deduplicate suspicious phrases preserving case from original text
    deduped_phrases: List[str] = []
    for phrase in suspicious_phrases:
        cleaned = phrase.strip()
        if cleaned and cleaned not in deduped_phrases:
            deduped_phrases.append(cleaned)

    # Cap score at 100
    rules_score = min(score, 100)

    return RuleDetectionResult(
        rules_score=rules_score,
        matched_flags=list(dict.fromkeys(matched_flags)),
        detected_themes=list(dict.fromkeys(detected_themes)),
        impersonated_entities=list(dict.fromkeys(impersonated_entities)),
        asks_for_credentials=asks_for_credentials,
        has_urgency=has_urgency,
        has_links=has_links,
        is_genuine_otp_alert=is_genuine_otp_alert,
        suspicious_phrases=deduped_phrases,
    )


def evaluate_rules(text: str) -> Tuple[int, List[str], bool, List[str]]:
    """Convenience evaluator returning (rules_score, matched_flags, asks_credentials, suspicious_phrases).

    Args:
        text: Input message to inspect.

    Returns:
        Tuple of:
        - rules_score (int): 0-100 heuristic risk score
        - matched_flags (List[str]): human-readable detection tags
        - asks_credentials (bool): whether credentials were requested
        - suspicious_phrases (List[str]): exact substrings matched in the input
    """
    res = extract_matched_patterns(text)
    return res.rules_score, res.matched_flags, res.asks_for_credentials, res.suspicious_phrases
