"""Main FastAPI application for Satark scam detection platform.

Provides:
- GET /health: Health check endpoint
- POST /analyze: Main scam detection endpoint (wired to rules, URL inspector, LLM, and scoring engine)
"""

import os
from contextlib import asynccontextmanager
from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware

# Detection pipeline modules
from llm import analyze_with_gemini
from rules import extract_matched_patterns
from schemas import AnalyzeResponse
from scoring import synthesize_full_response
from url_inspector import inspect_urls

# Load environment configuration from .env
load_dotenv()

APP_TITLE = "Satark API"
APP_DESCRIPTION = (
    "Explainable Multilingual Scam Detection Assistant for Indian digital users. "
    "Analyzes suspicious SMS, WhatsApp, and UPI messages or screenshots using a blend of "
    "heuristic rules, local URL inspection, and multimodal AI with zero data persistence."
)
APP_VERSION = "1.0.0"

MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB
ALLOWED_MIME_TYPES = {"image/png", "image/jpeg", "image/jpg", "image/webp"}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for startup and shutdown procedures."""
    yield


app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS setup for frontend development and production
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in ALLOWED_ORIGINS if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(
    "/health",
    summary="Health Check",
    tags=["System"],
    response_model=dict,
)
async def health_check():
    """Returns the operational status of the Satark backend service."""
    return {"status": "ok"}


@app.post(
    "/analyze",
    summary="Analyze Message or Screenshot",
    tags=["Scam Detection"],
    response_model=AnalyzeResponse,
    status_code=status.HTTP_200_OK,
)
async def analyze_message(
    text: Optional[str] = Form(None, description="The suspicious message text"),
    image: Optional[UploadFile] = File(None, description="PNG/JPG screenshot (limit 5 MB)"),
) -> AnalyzeResponse:
    """Analyzes a suspicious text message or screenshot for fraud indicators.

    Combines:
    - Multimodal text extraction & contextual reasoning via Google Gemini
    - Heuristic rule detection for urgency, credentials, themes, and impersonation
    - Local static URL analysis for shorteners, abusive TLDs, and brand lookalikes
    - Composite risk score synthesis with safety floors
    """
    has_text = bool(text and text.strip())
    has_image = bool(image and image.filename)

    # Validation: at least one input is required
    if not has_text and not has_image:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="At least one of 'text' or 'image' must be provided.",
        )

    image_bytes: Optional[bytes] = None
    image_mime: Optional[str] = None

    # Handle image upload validations
    if has_image and image:
        content_type = image.content_type or ""
        if content_type.lower() not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type '{content_type}'. Only PNG, JPG, JPEG, and WebP images are allowed.",
            )

        image_bytes = await image.read()
        if len(image_bytes) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Image size exceeds the 5 MB limit.",
            )
        image_mime = content_type

    input_text = text.strip() if text else ""

    # Call Gemini AI
    llm_result = analyze_with_gemini(
        text=input_text if input_text else None,
        image_bytes=image_bytes,
        mime_type=image_mime,
    )

    # Determine extracted_text
    if llm_result and llm_result.extracted_text:
        # If both text and image were provided, combine them if distinct
        if input_text and input_text not in llm_result.extracted_text:
            extracted_text = f"{input_text}\n\n[Screenshot Extracted]: {llm_result.extracted_text}".strip()
        else:
            extracted_text = llm_result.extracted_text
    elif input_text:
        extracted_text = input_text
    else:
        extracted_text = "[Screenshot uploaded - AI OCR unavailable]"

    # Heuristic rules evaluation
    rule_result = extract_matched_patterns(extracted_text)

    # Local URL heuristic inspection
    links = inspect_urls(extracted_text)

    # Final response synthesis
    response = synthesize_full_response(
        extracted_text=extracted_text,
        rules_score=rule_result.rules_score,
        rules_flags=rule_result.matched_flags,
        detected_themes=rule_result.detected_themes,
        asks_credentials=rule_result.asks_for_credentials,
        rules_phrases=rule_result.suspicious_phrases,
        links=links,
        llm_result=llm_result,
    )

    return response
