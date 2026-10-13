"""Automated test suite for Satark detection accuracy, heuristics, URL inspection, and scoring engine.

Validates:
1. 8 standard samples (4 scams return Suspicious or Likely Scam; 4 genuine return Safe)
2. Genuine OTP alert calibration (no false positives for 'do not share this OTP')
3. URL inspector heuristics (suspicious TLDs, shorteners, brand lookalikes, IP addresses, legitimate domains)
4. Fallback scoring engine behavior when LLM is unavailable (None return, hard floors, bilingual templates)
5. FastAPI /analyze endpoint integration (HTTP validation, error codes, and response schemas)
"""

import os
import sys
from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient

# Ensure backend root is on Python path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(CURRENT_DIR)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from main import app
from rules import extract_matched_patterns
from llm import LLMAnalysisResult
from schemas import AnalyzeResponse
from scoring import compute_risk_score, determine_verdict, synthesize_full_response
from url_inspector import inspect_urls

client = TestClient(app)

# ==============================================================================
# STANDARD TEST DATA (4 SCAMS, 4 GENUINE)
# ==============================================================================

STANDARD_SAMPLES = [
    {
        "id": "sample-kyc",
        "type": "scam",
        "text": "Dear customer, your SBI account band ho jayega today. Update KYC turant: http://sbi-kyc-update.xyz",
        "expected_verdicts": ["Suspicious", "Likely Scam"],
    },
    {
        "id": "sample-loan",
        "type": "scam",
        "text": "Congratulations! Your instant pre-approved personal loan of Rs 5,00,000 is ready for disbursal. Click to claim immediately: http://bit.ly/loan392",
        "expected_verdicts": ["Suspicious", "Likely Scam"],
    },
    {
        "id": "sample-lottery",
        "type": "scam",
        "text": "Dear winner, you won KBC lucky draw of Rs 25,00,000! Deposit small processing fee of Rs 1,500 to release your prize cheque. Call 9876543210",
        "expected_verdicts": ["Suspicious", "Likely Scam"],
    },
    {
        "id": "sample-electricity",
        "type": "scam",
        "text": "Dear consumer, your electricity power will be disconnected tonight at 9:30 PM by electricity office due to unpaid bill. Call electricity officer immediately: 9876543210",
        "expected_verdicts": ["Suspicious", "Likely Scam"],
    },
    {
        "id": "sample-bank-otp",
        "type": "genuine",
        "text": "482910 is your secret OTP for transaction of Rs 2,499.00 at Amazon Pay. Valid for 10 mins. Do not share this OTP with anyone. - State Bank of India",
        "expected_verdicts": ["Safe"],
    },
    {
        "id": "sample-courier",
        "type": "genuine",
        "text": "Your Amazon order #402-8392102 has been dispatched via BlueDart and is out for delivery today. Track your courier: https://amazon.in/orders",
        "expected_verdicts": ["Safe"],
    },
    {
        "id": "sample-upi",
        "type": "genuine",
        "text": "Rs 1,500.00 credited to your HDFC Bank A/C ending in 4521 via UPI from Rahul Sharma. UPI Ref: 409218291045.",
        "expected_verdicts": ["Safe"],
    },
    {
        "id": "sample-food-otp",
        "type": "genuine",
        "text": "584920 is your OTP to log in to Swiggy. Valid for 5 minutes. Never share your OTP with anyone.",
        "expected_verdicts": ["Safe"],
    },
]


# ==============================================================================
# 1. 8 STANDARD SAMPLES ACCURACY SUITE
# ==============================================================================

class TestStandardSamples:
    """Validates the 8 standard reference samples across heuristic engine and synthesis."""

    @pytest.mark.parametrize("sample", STANDARD_SAMPLES, ids=lambda s: s["id"])
    def test_samples_fallback_engine(self, sample):
        """Tests that heuristic rules + URL inspector alone correctly classify the sample."""
        text = sample["text"]
        rules = extract_matched_patterns(text)
        links = inspect_urls(text)
        response = synthesize_full_response(
            extracted_text=text,
            rules_score=rules.rules_score,
            rules_flags=rules.matched_flags,
            detected_themes=rules.detected_themes,
            asks_credentials=rules.asks_for_credentials,
            rules_phrases=rules.suspicious_phrases,
            links=links,
            llm_result=None,
        )

        assert response.verdict in sample["expected_verdicts"], (
            f"Failed for {sample['id']}: expected {sample['expected_verdicts']} but got {response.verdict} "
            f"(Score: {response.risk_score})"
        )

        if sample["type"] == "scam":
            assert response.risk_score >= 35, f"Scam {sample['id']} scored below 35: {response.risk_score}"
        else:
            assert response.risk_score < 35, f"Genuine {sample['id']} scored 35 or above: {response.risk_score}"

    @pytest.mark.parametrize("sample", STANDARD_SAMPLES, ids=lambda s: s["id"])
    def test_samples_via_analyze_endpoint(self, sample):
        """Tests standard samples through the FastAPI /analyze endpoint with mocked LLM for determinism."""
        # Mock LLM to return high score for scam and low score for genuine
        is_scam = sample["type"] == "scam"
        mock_llm_score = 85 if is_scam else 10
        mock_scam_type = "Generic Scam" if is_scam else "Safe"

        mock_llm = LLMAnalysisResult(
            llm_score=mock_llm_score,
            scam_type=mock_scam_type,
            how_it_works="Attacker mechanism." if is_scam else "Normal traffic.",
            extracted_text=sample["text"],
            suspicious_phrases=["band ho jayega", "turant"] if is_scam else [],
            red_flags=["Urgent threat detected", "Fake sender identity"] if is_scam else [],
            explanation_en="Simulated analysis for test.",
            explanation_hi="परीक्षण हेतु कृत्रिम विश्लेषण।",
            family_alert={
                "en": "Alert for testing." if is_scam else "Message safe.",
                "hi": "परीक्षण हेतु चेतावनी।" if is_scam else "संदेश सुरक्षित है।",
            },
            report_summary="Simulated summary for test.",
        )

        with patch("main.analyze_with_gemini", return_value=mock_llm):
            resp = client.post("/analyze", data={"text": sample["text"]})
            assert resp.status_code == 200
            data = resp.json()
            assert data["verdict"] in sample["expected_verdicts"]
            if is_scam:
                assert data["risk_score"] >= 35
            else:
                assert data["risk_score"] < 35


# ==============================================================================
# 2. GENUINE OTP CALIBRATION TESTS
# ==============================================================================

class TestGenuineOTPCalibration:
    """Verifies that legitimate OTP notifications with 'do not share' are strictly protected from false positives."""

    def test_bank_otp_with_do_not_share_is_safe(self):
        text = "739201 is your OTP for transaction of Rs 1,499.00 at Flipkart. Do not share this OTP with anyone. - HDFC Bank"
        rules = extract_matched_patterns(text)
        assert rules.is_genuine_otp_alert is True
        assert rules.asks_for_credentials is False
        assert rules.rules_score <= 10

        response = synthesize_full_response(
            extracted_text=text,
            rules_score=rules.rules_score,
            rules_flags=rules.matched_flags,
            detected_themes=rules.detected_themes,
            asks_credentials=rules.asks_for_credentials,
            rules_phrases=rules.suspicious_phrases,
            links=[],
            llm_result=None,
        )
        assert response.verdict == "Safe"
        assert response.risk_score < 35

    def test_app_login_otp_with_never_share_is_safe(self):
        text = "492018 is your Zomato login verification code. Never share your OTP with anyone, including Zomato delivery partners."
        rules = extract_matched_patterns(text)
        assert rules.is_genuine_otp_alert is True
        assert rules.asks_for_credentials is False
        assert rules.rules_score <= 10

        response = synthesize_full_response(
            extracted_text=text,
            rules_score=rules.rules_score,
            rules_flags=rules.matched_flags,
            detected_themes=rules.detected_themes,
            asks_credentials=rules.asks_for_credentials,
            rules_phrases=rules.suspicious_phrases,
            links=[],
            llm_result=None,
        )
        assert response.verdict == "Safe"

    def test_hinglish_otp_with_kisi_ko_na_dein_is_safe(self):
        text = "Aapka SBI netbanking OTP 920145 hai. Yeh OTP kisi ko na batayein aur kisi ko na dein."
        rules = extract_matched_patterns(text)
        assert rules.is_genuine_otp_alert is True
        assert rules.asks_for_credentials is False
        assert rules.rules_score <= 10

    def test_malicious_otp_request_is_flagged(self):
        """Contrast: A message demanding the user to send/share their OTP MUST be flagged as credential harvesting."""
        malicious_text = "Urgent: Your account is locked. Share your OTP immediately to customer care officer 9876543210 to unlock."
        rules = extract_matched_patterns(malicious_text)
        assert rules.is_genuine_otp_alert is False
        assert rules.asks_for_credentials is True
        assert rules.rules_score >= 40

        response = synthesize_full_response(
            extracted_text=malicious_text,
            rules_score=rules.rules_score,
            rules_flags=rules.matched_flags,
            detected_themes=rules.detected_themes,
            asks_credentials=rules.asks_for_credentials,
            rules_phrases=rules.suspicious_phrases,
            links=[],
            llm_result=None,
        )
        assert response.verdict in ["Suspicious", "Likely Scam"]
        assert response.risk_score >= 40


# ==============================================================================
# 3. URL INSPECTOR HEURISTIC SUITE
# ==============================================================================

class TestURLInspector:
    """Tests static URL parsing, TLD detection, brand lookalikes, and risk tier assignments."""

    def test_suspicious_tld_detection(self):
        links = inspect_urls("Click here to verify: http://account-update.xyz")
        assert len(links) == 1
        link = links[0]
        assert link.suspicious_tld is True
        assert link.risk == "high"

    def test_url_shortener_detection(self):
        links = inspect_urls("Claim your loan here: http://bit.ly/fastloan99")
        assert len(links) == 1
        link = links[0]
        assert link.is_shortener is True
        assert link.risk in ["medium", "high"]

    def test_brand_lookalike_spoofing_sbi(self):
        links = inspect_urls("SBI update notice: http://sbi-kyc-verify.xyz/login")
        assert len(links) == 1
        link = links[0]
        assert link.lookalike_of == "SBI"
        assert link.risk == "high"

    def test_brand_lookalike_spoofing_hdfc(self):
        links = inspect_urls("Login to netbanking: http://secure-hdfcbank-portal.top")
        assert len(links) == 1
        link = links[0]
        assert link.lookalike_of == "HDFC"
        assert link.risk == "high"

    def test_legitimate_brand_domains_are_safe(self):
        # Genuine Amazon tracking link
        links = inspect_urls("Track your order at https://amazon.in/orders")
        assert len(links) == 1
        assert links[0].lookalike_of is None
        assert links[0].suspicious_tld is False
        assert links[0].risk == "low"

        # Genuine SBI portal
        links_sbi = inspect_urls("Visit official portal at https://onlinesbi.sbi")
        assert len(links_sbi) == 1
        assert links_sbi[0].lookalike_of is None
        assert links_sbi[0].risk == "low"

    def test_ip_address_host_flagged_as_high_risk(self):
        links = inspect_urls("Login to router admin at http://192.168.1.1/admin")
        assert len(links) == 1
        assert links[0].domain == "192.168.1.1"
        assert links[0].risk == "high"

    def test_bare_shortener_without_scheme_extracted(self):
        links = inspect_urls("Urgent notice see bit.ly/alert-now for details")
        assert len(links) == 1
        assert links[0].is_shortener is True
        assert "bit.ly" in links[0].domain


# ==============================================================================
# 4. FALLBACK SCORING & COMPOSITE FORMULA TESTS
# ==============================================================================

class TestFallbackScoring:
    """Verifies composite calculations, hard floors, and fallback template behavior when LLM is unavailable."""

    def test_fallback_when_llm_is_none(self):
        text = "Dear consumer, your electricity power will be disconnected tonight at 9:30 PM by electricity office due to unpaid bill. Call electricity officer immediately: 9876543210"
        rules = extract_matched_patterns(text)
        links = inspect_urls(text)

        response = synthesize_full_response(
            extracted_text=text,
            rules_score=rules.rules_score,
            rules_flags=rules.matched_flags,
            detected_themes=rules.detected_themes,
            asks_credentials=rules.asks_for_credentials,
            rules_phrases=rules.suspicious_phrases,
            links=links,
            llm_result=None,
        )

        # AI should be flagged as unavailable
        assert response.ai_available is False
        assert response.score_breakdown.ai is None
        assert response.score_breakdown.rules == rules.rules_score
        assert response.risk_score == rules.rules_score

        # Fallback templates should provide bilingual explanations and family alert
        assert response.scam_type == "Electricity Bill Threat"
        assert "electricity" in response.explanation_en.lower()
        assert "बिजली" in response.explanation_hi
        assert response.family_alert.en.startswith("⚠️ Family Alert")
        assert "बिजली" in response.family_alert.hi
        assert response.how_it_works != ""

    def test_hard_floor_enforcement_on_credentials(self):
        """Even if rule score is below 40, asking for credentials forces risk_score >= 40."""
        score, breakdown, ai_avail = compute_risk_score(
            rules_score=20,
            llm_score=None,
            asks_credentials=True,
            links=[],
        )
        assert score >= 40
        assert determine_verdict(score) in ["Suspicious", "Likely Scam"]

    def test_composite_formula_with_llm(self):
        """Validates round(0.4 * rules + 0.6 * llm)."""
        rules_score = 50
        llm_score = 90
        # 0.4 * 50 = 20; 0.6 * 90 = 54; 20 + 54 = 74
        score, breakdown, ai_avail = compute_risk_score(
            rules_score=rules_score,
            llm_score=llm_score,
            asks_credentials=False,
            links=[],
        )
        assert score == 74
        assert breakdown.rules == 50
        assert breakdown.ai == 90
        assert ai_avail is True
        assert determine_verdict(score) == "Likely Scam"


# ==============================================================================
# 5. FASTAPI /analyze ENDPOINT INTEGRATION TESTS
# ==============================================================================

class TestAPIEndpoint:
    """Verifies HTTP status codes, validations, and schema conformity."""

    def test_health_check(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}

    def test_analyze_empty_payload_rejected(self):
        resp = client.post("/analyze", data={})
        assert resp.status_code == 422
        assert "At least one of 'text' or 'image' must be provided" in resp.json()["detail"]

    def test_analyze_invalid_image_mime(self):
        files = {"image": ("test.pdf", b"%PDF-1.4...", "application/pdf")}
        resp = client.post("/analyze", files=files)
        assert resp.status_code == 400
        assert "Only PNG, JPG, JPEG, and WebP images are allowed" in resp.json()["detail"]

    def test_analyze_valid_text_structure(self):
        with patch("main.analyze_with_gemini", return_value=None):
            resp = client.post(
                "/analyze",
                data={"text": "Congratulations you won lottery. Pay fee to claim."}
            )
            assert resp.status_code == 200
            data = resp.json()
            # Verify conformity to AnalyzeResponse schema keys
            required_keys = [
                "risk_score",
                "verdict",
                "ai_available",
                "score_breakdown",
                "scam_type",
                "red_flags",
                "explanation_en",
                "explanation_hi",
                "next_steps",
                "family_alert",
                "links",
                "suspicious_phrases",
                "extracted_text",
            ]
            for key in required_keys:
                assert key in data, f"Missing key '{key}' in response"
