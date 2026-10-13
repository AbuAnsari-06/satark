"""Multimodal Gemini LLM integration for Satark scam detection platform.

Provides:
- Gemini API client initialization via google-genai SDK
- Multimodal payload construction supporting text and screenshot image bytes (PNG/JPG)
- Verbatim system prompt and structured JSON schema enforcement
- Code fence cleanup, parsing resilience, single-retry mechanism, and graceful fallback
"""

import json
import logging
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

# Google GenAI SDK
from google import genai
from google.genai import types

load_dotenv()
logger = logging.getLogger("satark.llm")

# Model configuration
DEFAULT_MODEL = "gemini-2.5-flash"
GEMINI_MODEL = os.getenv("GEMINI_MODEL", DEFAULT_MODEL)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Verbatim system prompt from SATARK_PROJECT.md Section 5.3
SYSTEM_PROMPT = """You are a fraud analyst helping everyday Indian smartphone users. You understand English, Hindi (Devanagari), and Hinglish (Hindi in Roman script). Analyze the given message (or screenshot) for scam risk.

Rules:
- Receiving a genuine OTP, bank transaction alert, or delivery update is NORMAL. The red flag is being ASKED to share an OTP/PIN/CVV/password, to click an unfamiliar link, to install an app, or to send money.
- Be calibrated. Do not label ordinary messages as scams. Do not call a clear scam safe.
- `suspicious_phrases` must be EXACT substrings copied character for character from `extracted_text`.
- If the input is an image, read all the text in it into `extracted_text`.
- Write explanations in simple language a first-time smartphone user can understand. Provide both English and natural Hindi.
- Return ONLY valid JSON, no markdown, matching this structure:
{"llm_score": 0-100, "scam_type": string, "how_it_works": string, "extracted_text": string, "suspicious_phrases": [string], "red_flags": [string], "explanation_en": string, "explanation_hi": string, "family_alert": {"en": string, "hi": string}, "report_summary": string}
- `scam_type` examples: "Fake KYC", "Fake Loan", "Lottery / Prize", "OTP Theft", "Fake Customer Care", "Phishing Link", "Job Offer Scam", "Not a scam".
- `family_alert`: a short, friendly, forwardable warning about this kind of scam (2-3 sentences).
- `report_summary`: a factual 3-4 line summary suitable for pasting into a cybercrime complaint (what was received, what it asked for, any links)."""


@dataclass
class LLMAnalysisResult:
    """Structured response from Gemini analysis."""

    llm_score: int
    scam_type: str
    how_it_works: str
    extracted_text: str
    suspicious_phrases: List[str]
    red_flags: List[str]
    explanation_en: str
    explanation_hi: str
    family_alert: Dict[str, str]
    report_summary: str


def get_genai_client() -> Optional[genai.Client]:
    """Initializes and returns a Google GenAI Client if a valid API key is configured."""
    load_dotenv(override=True)
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key or api_key == "your_gemini_api_key_here":
        logger.warning(
            "GEMINI_API_KEY is not set or contains placeholder value. "
            "AI analysis will fall back to rules-only mode."
        )
        return None

    try:
        return genai.Client(api_key=api_key)
    except Exception as exc:
        logger.error(f"Failed to initialize Google GenAI client: {exc}")
        return None


def build_multimodal_contents(
    text: Optional[str] = None,
    image_bytes: Optional[bytes] = None,
    mime_type: Optional[str] = None,
) -> list:
    """Builds content list for generate_content supporting text and/or image inputs."""
    contents = []

    if image_bytes and mime_type:
        image_part = types.Part.from_bytes(
            data=image_bytes,
            mime_type=mime_type,
        )
        contents.append(image_part)

    if text and text.strip():
        contents.append(text.strip())
    elif image_bytes:
        contents.append(
            "Extract all text from this screenshot and analyze it for scam risk according to your instructions."
        )

    return contents


def clean_and_parse_json(raw_text: str) -> Optional[Dict[str, Any]]:
    """Strips code fences, isolates JSON payload, and parses into a dictionary."""
    if not raw_text:
        return None

    cleaned = raw_text.strip()

    # Strip markdown code blocks like ```json ... ``` or ``` ... ```
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)
        cleaned = cleaned.strip()

    # Try standard parse
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Fallback: Extract substring between outermost { and }
    match = re.search(r"\{[\s\S]*\}", cleaned)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    return None


def validate_and_coerce_payload(data: Dict[str, Any]) -> Optional[LLMAnalysisResult]:
    """Validates required keys, clamps score, and converts to LLMAnalysisResult."""
    try:
        # Score clamping
        raw_score = data.get("llm_score", 0)
        try:
            score = int(raw_score)
        except (ValueError, TypeError):
            score = 0
        clamped_score = max(0, min(100, score))

        # Family alert validation
        raw_family = data.get("family_alert") or {}
        if isinstance(raw_family, dict):
            family_alert = {
                "en": str(raw_family.get("en", "")).strip(),
                "hi": str(raw_family.get("hi", "")).strip(),
            }
        else:
            family_alert = {"en": str(raw_family), "hi": str(raw_family)}

        # Suspicious phrases list coercion
        raw_phrases = data.get("suspicious_phrases") or []
        suspicious_phrases = [str(p).strip() for p in raw_phrases if str(p).strip()]

        # Red flags list coercion
        raw_flags = data.get("red_flags") or []
        red_flags = [str(f).strip() for f in raw_flags if str(f).strip()]

        return LLMAnalysisResult(
            llm_score=clamped_score,
            scam_type=str(data.get("scam_type", "Unknown Scam")).strip(),
            how_it_works=str(data.get("how_it_works", "")).strip(),
            extracted_text=str(data.get("extracted_text", "")).strip(),
            suspicious_phrases=suspicious_phrases,
            red_flags=red_flags,
            explanation_en=str(data.get("explanation_en", "")).strip(),
            explanation_hi=str(data.get("explanation_hi", "")).strip(),
            family_alert=family_alert,
            report_summary=str(data.get("report_summary", "")).strip(),
        )
    except Exception as exc:
        logger.error(f"Error coercing Gemini JSON payload: {exc}")
        return None


def analyze_with_gemini(
    text: Optional[str] = None,
    image_bytes: Optional[bytes] = None,
    mime_type: Optional[str] = None,
) -> Optional[LLMAnalysisResult]:
    """Calls Gemini API enforcing structured JSON and handling retries/fallbacks.

    Args:
        text: Optional text message.
        image_bytes: Optional raw bytes of screenshot image.
        mime_type: Optional MIME string (e.g., 'image/png', 'image/jpeg').

    Returns:
        LLMAnalysisResult if successful, or None on failure to trigger rules-only fallback.
    """
    client = get_genai_client()
    if client is None:
        return None

    contents = build_multimodal_contents(
        text=text,
        image_bytes=image_bytes,
        mime_type=mime_type,
    )
    if not contents:
        return None

    model_name = os.getenv("GEMINI_MODEL", DEFAULT_MODEL)
    generation_config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        response_mime_type="application/json",
        temperature=0.1,
    )

    # Attempt 1
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=contents,
            config=generation_config,
        )
        parsed_data = clean_and_parse_json(response.text)
        if parsed_data:
            result = validate_and_coerce_payload(parsed_data)
            if result:
                return result
    except Exception as exc:
        logger.warning(f"First attempt with Gemini failed: {exc}. Retrying once...")

    # Retry attempt 2 (once)
    try:
        retry_prompt = [
            *contents,
            "IMPORTANT: Return ONLY a valid JSON object matching the requested schema. Do not include markdown code fences or conversational text.",
        ]
        response = client.models.generate_content(
            model=model_name,
            contents=retry_prompt,
            config=generation_config,
        )
        parsed_data = clean_and_parse_json(response.text)
        if parsed_data:
            result = validate_and_coerce_payload(parsed_data)
            if result:
                return result
    except Exception as exc:
        logger.error(f"Retry attempt with Gemini failed: {exc}")

    # Fallback return None on any failure
    logger.info("Falling back to rules-only detection.")
    return None
