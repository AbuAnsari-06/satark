"""Scoring synthesis and fallback templating engine for Satark scam detection platform.

Provides:
- Weighted risk score calculation (0.4 rules + 0.6 LLM) with clamp (0-100)
- Hard floor enforcement (minimum 40 risk score if credentials requested or high-risk link detected)
- Verdict classification bands (<35 Safe, 35-65 Suspicious, >65 Likely Scam)
- Dynamic fallback handling when LLM is unavailable
- Red flag merging and deduplication (capped at 6)
- Contextual next steps generation (including 1930 helpline & cybercrime.gov.in)
- Bilingual fallback templates for explanation, family alert, and report summary
"""

from typing import List, Literal, Optional, Tuple
from schemas import AnalyzeResponse, FamilyAlert, LinkDetail, ScoreBreakdown

# Pre-defined mechanisms for fallback scam explainers
SCAM_MECHANISMS = {
    "Fake KYC": {
        "how_it_works": "Scammers pose as your bank or telecom operator and threaten account closure to force you to click phishing links or share OTPs and Aadhaar/PAN details.",
        "explanation_en": "This message mimics an urgent KYC update request. Legitimate banks and service providers do not threaten immediate account suspension via SMS or require KYC updates via third-party web links.",
        "explanation_hi": "यह संदेश तत्काल KYC अपडेट का दबाव बनाता है। असली बैंक या कंपनियाँ कभी भी SMS में खाता तुरंत बंद करने की धमकी देकर किसी बाहरी लिंक पर KYC नहीं करवातीं।",
        "family_alert": {
            "en": "⚠️ Family Alert: Beware of fake bank KYC messages threatening account blockage. Genuine banks never send links to update KYC. Do not click links or share OTPs!",
            "hi": "⚠️ परिवार के लिए चेतावनी: बैंक खाता बंद होने की धमकी देकर फर्जी KYC संदेश भेजे जा रहे हैं। बैंक कभी भी SMS में लिंक नहीं भेजता। किसी लिंक पर क्लिक न करें!",
        },
    },
    "Electricity Bill Threat": {
        "how_it_works": "Fraudsters claim your power will be cut off tonight due to an unpaid bill, urging you to call a fake customer care number or install remote-access apps.",
        "explanation_en": "This message is a classic electricity disconnection scam. Power distribution companies follow formal billing cycles and do not send sudden cutoff threats with personal mobile contact numbers.",
        "explanation_hi": "यह बिजली बिल काटने वाला फर्जी संदेश है। बिजली विभाग कभी भी अचानक रात में बिजली काटने की धमकी वाले SMS या व्यक्तिगत मोबाइल नंबर से संपर्क करने को नहीं कहता।",
        "family_alert": {
            "en": "⚠️ Family Alert: Fake electricity bill disconnection messages are in circulation. Electricity boards do not cut power via SMS threats. Do not call numbers given in such messages!",
            "hi": "⚠️ परिवार के लिए चेतावनी: बिजली कटने के फर्जी संदेशों से सावधान रहें। बिजली विभाग ऐसे SMS नहीं भेजता। किसी भी दिए गए नंबर पर कॉल न करें!",
        },
    },
    "Lottery / Prize / Reward": {
        "how_it_works": "Scammers claim you won a major lucky draw or prize, then demand a 'processing fee', 'GST', or 'tax' in advance to release the funds.",
        "explanation_en": "This message claims you won an unearned prize or lottery. Legitimate lotteries never ask winners to pay advance fees or processing charges to receive rewards.",
        "explanation_hi": "यह संदेश लॉटरी या इनाम जीतने का झांसा देता है। असली लॉटरी या पुरस्कार में कभी भी पैसे प्राप्त करने के लिए अग्रिम शुल्क या टैक्स जमा करने की मांग नहीं की जाती।",
        "family_alert": {
            "en": "⚠️ Family Alert: Fake lottery and prize messages are circulating. Remember: if you didn't enter a contest, you didn't win. Never pay any fee to claim prizes!",
            "hi": "⚠️ परिवार के लिए चेतावनी: फर्जी लॉटरी संदेशों से सावधान रहें। यदि आपने किसी प्रतियोगिता में भाग नहीं लिया तो आप विजेता नहीं हैं। कोई भी शुल्क न दें!",
        },
    },
    "Fake Loan Approval": {
        "how_it_works": "Fraudsters offer instant, pre-approved loans with no paperwork, directing users to malicious loan apps or asking for upfront processing fees.",
        "explanation_en": "This message promotes an unverified instant loan. Fraudulent loan apps often steal personal data, access contacts, or demand upfront payments without genuine RBI registration.",
        "explanation_hi": "यह संदेश बिना दस्तावेज़ के तुरंत लोन का लालच देता है। फर्जी लोन ऐप्स फोन का व्यक्तिगत डेटा चुराते हैं और पहले पैसे जमा करने का दबाव बनाते हैं।",
        "family_alert": {
            "en": "⚠️ Family Alert: Watch out for instant loan approval messages containing links. Never install unknown loan apps or transfer advance processing fees!",
            "hi": "⚠️ परिवार के लिए चेतावनी: बिना जांचे तुरंत लोन देने वाले SMS से बचें। किसी भी अनजान लोन ऐप को डाउनलोड न करें और पहले पैसे न भेजें!",
        },
    },
    "Generic Scam": {
        "how_it_works": "Attackers use psychological pressure, urgency, or deceptive links to convince you to transfer money or compromise your digital security.",
        "explanation_en": "This message exhibits strong scam patterns including high urgency, suspicious links, or unauthorized requests for action.",
        "explanation_hi": "इस संदेश में धोखाधड़ी के स्पष्ट संकेत हैं जैसे अत्यधिक जल्दबाज़ी, संदेहास्पद लिंक या व्यक्तिगत जानकारी की मांग।",
        "family_alert": {
            "en": "⚠️ Family Alert: A suspicious message was detected. Please be careful and do not click any links or send money without verifying the sender directly.",
            "hi": "⚠️ परिवार के लिए चेतावनी: एक संदेहास्पद संदेश प्राप्त हुआ है। कृपया किसी भी लिंक पर क्लिक न करें और सीधे जांच किए बिना पैसे न भेजें।",
        },
    },
    "Safe": {
        "how_it_works": "Normal communication pattern without typical fraud signals or unauthorized credential harvesting attempts.",
        "explanation_en": "No major scam indicators or deceptive links were detected in this message. It appears to be standard informational or transactional communication.",
        "explanation_hi": "इस संदेश में धोखाधड़ी या संदेहास्पद लिंक के कोई लक्षण नहीं मिले हैं। यह सामान्य सूचनात्मक संदेश प्रतीत होता है।",
        "family_alert": {
            "en": "✅ This message appears safe. Always remember to stay cautious and never share OTPs or passwords with anyone.",
            "hi": "✅ यह संदेश सुरक्षित प्रतीत होता है। हमेशा सतर्क रहें और किसी के साथ भी अपना OTP या पासवर्ड साझा न करें।",
        },
    },
}


def compute_risk_score(
    rules_score: int,
    llm_score: Optional[int],
    asks_credentials: bool,
    links: List[LinkDetail],
) -> Tuple[int, ScoreBreakdown, bool]:
    """Calculates composite risk score applying weights and safety hard floors.

    Formula:
        risk_score = round(0.4 * rules_score + 0.6 * llm_score) if AI is available,
        otherwise uses rules_score directly.

    Hard Floor:
        If credentials requested or any link has risk == 'high', risk_score is at least 40.
    """
    if llm_score is not None:
        raw_score = round(0.4 * rules_score + 0.6 * llm_score)
        ai_available = True
        breakdown = ScoreBreakdown(rules=rules_score, ai=llm_score)
    else:
        raw_score = rules_score
        ai_available = False
        breakdown = ScoreBreakdown(rules=rules_score, ai=None)

    # Hard floor enforcement
    has_high_risk_link = any(link.risk == "high" for link in links)
    if asks_credentials or has_high_risk_link:
        raw_score = max(raw_score, 40)

    # Ensure score stays within [0, 100]
    final_score = max(0, min(100, raw_score))

    return final_score, breakdown, ai_available


def determine_verdict(risk_score: int) -> Literal["Safe", "Suspicious", "Likely Scam"]:
    """Maps numerical risk score to verdict band."""
    if risk_score < 35:
        return "Safe"
    elif risk_score <= 65:
        return "Suspicious"
    else:
        return "Likely Scam"


def merge_red_flags(
    rules_flags: List[str],
    links: List[LinkDetail],
    llm_flags: Optional[List[str]] = None,
) -> List[str]:
    """Combines and deduplicates red flags from rules, URLs, and AI model up to 6 items."""
    flags: List[str] = []

    # 1. Add link-specific red flags first
    for link in links:
        if link.lookalike_of:
            flags.append(f"Deceptive link impersonating {link.lookalike_of}")
        if link.suspicious_tld:
            flags.append(f"Suspicious top-level domain ({link.domain})")
        if link.is_shortener:
            flags.append(f"Hidden destination URL shortener ({link.domain})")

    # 2. Add LLM red flags if available
    if llm_flags:
        for f in llm_flags:
            if f and f not in flags:
                flags.append(f)

    # 3. Add rules red flags
    for f in rules_flags:
        if f and f not in flags and f != "Legitimate transactional or authentication notification":
            flags.append(f)

    # If message is genuinely safe and has no flags
    if not flags:
        flags = ["No red flags detected"]

    # Deduplicate while preserving order, max 6 items
    deduped = list(dict.fromkeys(flags))
    return deduped[:6]


def generate_next_steps(verdict: str) -> List[str]:
    """Builds actionable next steps based on verdict band."""
    if verdict == "Safe":
        return [
            "No major red flags found, but stay careful with unexpected messages",
            "Never share banking OTPs, PINs, or passwords with anyone",
            "If in doubt, contact the official organization through their verified website",
        ]
    else:
        return [
            "Do not click any links or share your OTP / PIN / card details",
            "Block and report the sender immediately in your messaging app",
            "Report the fraud incident at cybercrime.gov.in or call the 1930 national helpline",
        ]


def build_fallback_analysis_content(
    text: str,
    verdict: str,
    detected_themes: List[str],
    links: List[LinkDetail],
    rules_flags: List[str],
) -> dict:
    """Generates structured analysis content using templates when AI is unavailable."""
    # Determine scam theme
    theme_key = "Safe"
    if verdict != "Safe":
        if detected_themes:
            theme_key = detected_themes[0]
            if theme_key not in SCAM_MECHANISMS:
                theme_key = "Generic Scam"
        elif any(l.risk == "high" for l in links):
            theme_key = "Fake KYC" if any("kyc" in l.domain for l in links) else "Generic Scam"
        else:
            theme_key = "Generic Scam"

    template = SCAM_MECHANISMS.get(theme_key, SCAM_MECHANISMS["Generic Scam"])
    scam_type = theme_key if verdict != "Safe" else "Not a scam"

    # Report summary template
    link_info = f" Embedded links: {', '.join(l.url for l in links)}." if links else ""
    if verdict != "Safe":
        report_summary = (
            f"Received suspicious message categorized as '{scam_type}'. "
            f"Message excerpt: '{text[:120]}...'.{link_info} "
            f"Detected red flags: {', '.join(rules_flags[:3])}."
        )
    else:
        report_summary = "Informational message analyzed. No cybercrime complaint required."

    return {
        "scam_type": scam_type,
        "how_it_works": template["how_it_works"],
        "explanation_en": template["explanation_en"],
        "explanation_hi": template["explanation_hi"],
        "family_alert": template["family_alert"],
        "report_summary": report_summary,
    }


def synthesize_full_response(
    extracted_text: str,
    rules_score: int,
    rules_flags: List[str],
    detected_themes: List[str],
    asks_credentials: bool,
    rules_phrases: List[str],
    links: List[LinkDetail],
    llm_result: Optional[Any],
) -> AnalyzeResponse:
    """Combines all analysis sources into the final AnalyzeResponse data contract."""
    llm_score = llm_result.llm_score if llm_result else None
    risk_score, breakdown, ai_available = compute_risk_score(
        rules_score=rules_score,
        llm_score=llm_score,
        asks_credentials=asks_credentials,
        links=links,
    )
    verdict = determine_verdict(risk_score)

    # Red flags merging
    llm_flags = llm_result.red_flags if llm_result else None
    red_flags = merge_red_flags(rules_flags=rules_flags, links=links, llm_flags=llm_flags)

    # Next steps
    next_steps = generate_next_steps(verdict)

    # Suspicious phrases: prefer LLM phrases if present, otherwise rules phrases
    if llm_result and llm_result.suspicious_phrases:
        suspicious_phrases = llm_result.suspicious_phrases
    else:
        suspicious_phrases = rules_phrases if verdict != "Safe" else []

    # Explanations, scam type, family alert, and report summary
    if llm_result:
        scam_type = llm_result.scam_type
        how_it_works = llm_result.how_it_works
        explanation_en = llm_result.explanation_en
        explanation_hi = llm_result.explanation_hi
        family_alert = FamilyAlert(
            en=llm_result.family_alert.get("en", ""),
            hi=llm_result.family_alert.get("hi", ""),
        )
        report_summary = llm_result.report_summary
    else:
        fallback = build_fallback_analysis_content(
            text=extracted_text,
            verdict=verdict,
            detected_themes=detected_themes,
            links=links,
            rules_flags=rules_flags,
        )
        scam_type = fallback["scam_type"]
        how_it_works = fallback["how_it_works"]
        explanation_en = fallback["explanation_en"]
        explanation_hi = fallback["explanation_hi"]
        family_alert = FamilyAlert(
            en=fallback["family_alert"]["en"],
            hi=fallback["family_alert"]["hi"],
        )
        report_summary = fallback["report_summary"]

    return AnalyzeResponse(
        verdict=verdict,
        risk_score=risk_score,
        score_breakdown=breakdown,
        scam_type=scam_type,
        how_it_works=how_it_works,
        extracted_text=extracted_text,
        suspicious_phrases=suspicious_phrases,
        red_flags=red_flags,
        links=links,
        explanation_en=explanation_en,
        explanation_hi=explanation_hi,
        next_steps=next_steps,
        family_alert=family_alert,
        report_summary=report_summary,
        ai_available=ai_available,
    )
