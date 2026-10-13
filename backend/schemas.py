"""Pydantic data models for Satark API.

Defines the request and response schemas with rich field descriptions
and examples for interactive OpenAPI documentation (/docs).
"""

from typing import List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field


class LinkDetail(BaseModel):
    """Detailed heuristic analysis for a detected URL."""

    url: str = Field(
        ...,
        description="The full detected URL",
        examples=["http://sbi-kyc-update.xyz"]
    )
    domain: str = Field(
        ...,
        description="The extracted hostname/domain",
        examples=["sbi-kyc-update.xyz"]
    )
    is_shortener: bool = Field(
        ...,
        description="Whether the domain belongs to a known URL shortener service (e.g., bit.ly, tinyurl)",
        examples=[False]
    )
    suspicious_tld: bool = Field(
        ...,
        description="Whether the top-level domain is commonly abused for scams (e.g., .xyz, .top, .click)",
        examples=[True]
    )
    lookalike_of: Optional[str] = Field(
        None,
        description="Legitimate brand that this domain appears to impersonate, or null if no brand impersonation detected",
        examples=["SBI"]
    )
    risk: Literal["low", "medium", "high"] = Field(
        ...,
        description="Computed heuristic risk tier for this specific link",
        examples=["high"]
    )


class ScoreBreakdown(BaseModel):
    """Breakdown of rule-based vs AI intelligence contributions to risk score."""

    rules: int = Field(
        ...,
        ge=0,
        le=100,
        description="Rule-based heuristic score (0-100)",
        examples=[80]
    )
    ai: Optional[int] = Field(
        None,
        ge=0,
        le=100,
        description="AI model risk score (0-100), or null if AI was unavailable",
        examples=[92]
    )


class FamilyAlert(BaseModel):
    """Ready-to-forward bilingual safety warnings for family groups."""

    en: str = Field(
        ...,
        description="Forwardable safety warning in English suitable for WhatsApp/SMS",
        examples=[
            "⚠️ Family Alert: Fake SBI messages are circulating asking to update KYC via suspicious links. SBI never sends links to update KYC. Please do not click any links or share OTPs!"
        ]
    )
    hi: str = Field(
        ...,
        description="Forwardable safety warning in Hindi suitable for WhatsApp/SMS",
        examples=[
            "⚠️ सावधान: SBI के नाम से फर्जी संदेश भेजे जा रहे हैं जिनमें KYC अपडेट के लिए लिंक दिया गया है। बैंक कभी भी SMS में लिंक नहीं भेजता। कृपया किसी लिंक पर क्लिक न करें और OTP साझा न करें!"
        ]
    )


class AnalyzeResponse(BaseModel):
    """Full analysis response for scam evaluation."""

    verdict: Literal["Safe", "Suspicious", "Likely Scam"] = Field(
        ...,
        description="Overall safety assessment: Safe (<35), Suspicious (35-65), or Likely Scam (>65)",
        examples=["Likely Scam"]
    )
    risk_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Composite risk score from 0 (completely safe) to 100 (extreme danger)",
        examples=[87]
    )
    score_breakdown: ScoreBreakdown = Field(
        ...,
        description="Comparative breakdown of rules and AI contributions to the final risk score"
    )
    scam_type: str = Field(
        ...,
        description="Identified scam taxonomy or category (e.g., Fake KYC, Lottery / Prize, OTP Theft, Not a scam)",
        examples=["Fake KYC"]
    )
    how_it_works: str = Field(
        ...,
        description="Brief explanation of the mechanics behind this scam technique",
        examples=[
            "Scammers pose as your bank and threaten account closure to make you share your OTP or click a fake link."
        ]
    )
    extracted_text: str = Field(
        ...,
        description="Message content analyzed (from input text or extracted via multimodal OCR)",
        examples=[
            "Dear customer, your SBI account will be blocked today. Update KYC: http://sbi-kyc-update.xyz"
        ]
    )
    suspicious_phrases: List[str] = Field(
        default_factory=list,
        description="Exact substrings identified as red-flag triggers inside the message",
        examples=[["account will be blocked", "Update KYC"]]
    )
    red_flags: List[str] = Field(
        default_factory=list,
        description="Key indicators that raised suspicion (max 6 items)",
        examples=[["Creates urgency", "Asks for personal details", "Suspicious link"]]
    )
    links: List[LinkDetail] = Field(
        default_factory=list,
        description="Heuristic analysis for each URL found in the message"
    )
    explanation_en: str = Field(
        ...,
        description="Clear, non-technical explanation in English tailored for first-time smartphone users",
        examples=[
            "This message pretends to be from SBI and pressures you to act urgently. Genuine banks never threaten immediate account suspension via SMS or send links to update KYC."
        ]
    )
    explanation_hi: str = Field(
        ...,
        description="Clear, non-technical explanation in Hindi tailored for first-time smartphone users",
        examples=[
            "यह संदेश SBI होने का दिखावा करता है और आप पर जल्दबाज़ी का दबाव डालता है। असली बैंक कभी भी SMS पर खाता तुरंत बंद करने की धमकी नहीं देते।"
        ]
    )
    next_steps: List[str] = Field(
        ...,
        description="Actionable guidance on how to respond safely",
        examples=[[
            "Do not click the link or share any personal details",
            "Block the sender immediately",
            "Report at cybercrime.gov.in or call 1930"
        ]]
    )
    family_alert: FamilyAlert = Field(
        ...,
        description="Ready-to-forward bilingual warning for family members and seniors"
    )
    report_summary: str = Field(
        ...,
        description="Concise, factual summary formatted for submission to cybercrime reporting portals (cybercrime.gov.in)",
        examples=[
            "Received SMS claiming SBI account suspension with request to update KYC via phishing URL: http://sbi-kyc-update.xyz."
        ]
    )
    ai_available: bool = Field(
        ...,
        description="True if Google Gemini AI contributed to the analysis; False if fell back to rules-only engine",
        examples=[True]
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "verdict": "Likely Scam",
                "risk_score": 87,
                "score_breakdown": {"rules": 80, "ai": 92},
                "scam_type": "Fake KYC",
                "how_it_works": "Scammers pose as your bank and threaten account closure to make you share your OTP or click a fake link.",
                "extracted_text": "Dear customer, your SBI account will be blocked today. Update KYC: http://sbi-kyc-update.xyz",
                "suspicious_phrases": ["account will be blocked", "Update KYC"],
                "red_flags": ["Creates urgency", "Asks for personal details", "Suspicious link"],
                "links": [
                    {
                        "url": "http://sbi-kyc-update.xyz",
                        "domain": "sbi-kyc-update.xyz",
                        "is_shortener": False,
                        "suspicious_tld": True,
                        "lookalike_of": "SBI",
                        "risk": "high"
                    }
                ],
                "explanation_en": "This message pretends to be from SBI and pressures you to act urgently...",
                "explanation_hi": "यह संदेश SBI होने का दिखावा करता है और आप पर जल्दबाज़ी का दबाव डालता है...",
                "next_steps": [
                    "Do not click the link",
                    "Block the sender",
                    "Report at cybercrime.gov.in or call 1930"
                ],
                "family_alert": {
                    "en": "⚠️ Family Alert: Fake SBI messages are circulating asking to update KYC...",
                    "hi": "⚠️ सावधान: SBI के नाम से फर्जी संदेश भेजे जा रहे हैं..."
                },
                "report_summary": "Received SMS claiming SBI account suspension with request to update KYC via phishing URL: http://sbi-kyc-update.xyz.",
                "ai_available": True
            }
        }
    )
