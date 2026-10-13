# Satark Development Roadmap & Task Breakdown

This document provides a complete, atomic, step-by-step roadmap for building **Satark** from inception to completion, strictly following the specifications in [SATARK_PROJECT.md](file:///d:/Abu%20Horairah%20Ansari/Satark/SATARK_PROJECT.md). Each task represents a self-contained, testable unit of work designed for implementation efficiency, code correctness, and reliability.

---

## Phase 1: Environment & Project Scaffolding

### Section 1.1: Backend Foundation
- [x] **Task 1.1.1: Backend directory structure and dependency management**
  - Create `backend/` directory.
  - Define `backend/requirements.txt` with `fastapi`, `uvicorn[standard]`, `pydantic>=2.0`, `google-genai`, `python-dotenv`, `python-multipart`, and test tools (`pytest`, `httpx`).
  - Create `backend/.env.example` defining `GEMINI_API_KEY`, `GEMINI_MODEL=gemini-2.5-flash`, and backend host configuration.

- [x] **Task 1.1.2: OpenAPI schemas & data contracts (`backend/schemas.py`)**
  - Implement Pydantic v2 schemas: `LinkDetail`, `ScoreBreakdown`, `FamilyAlert`, and `AnalyzeResponse`.
  - Include rich field descriptions, type constraints, and complete schema examples as specified in `SATARK_PROJECT.md` Section 4 for interactive `/docs`.

- [x] **Task 1.1.3: FastAPI application entrypoint & health check (`backend/main.py`)**
  - Initialize the FastAPI app with metadata (title, description, version).
  - Configure CORS middleware allowing frontend origin (`http://localhost:5173` and flexible env origins).
  - Implement `GET /health` returning `{"status": "ok"}`.

---

## Phase 2: Core Detection & Scoring Engine

### Section 2.1: Heuristic Rule Engine (`backend/rules.py`)
- [x] **Task 2.1.1: Pattern catalogs & keyword matching**
  - Implement case-insensitive regex patterns for Urgency (English & Hinglish like *turant*, *band ho jayega*), Credential requests (OTP, PIN, CVV, password, Aadhaar, PAN), Scam themes (KYC, lottery, loans, electricity disconnection, customer care, jobs), and Impersonation (banks: SBI/HDFC/ICICI, wallets: Paytm/PhonePe/GPay, agencies: TRAI/RBI/IT, brands: Amazon/Flipkart).
  - Implement payment pressure and link presence detection.

- [x] **Task 2.1.2: Scoring weights & genuine OTP exception logic**
  - Calculate `rules_score` (0–100) using weighted category additions.
  - Implement the **genuine transactional OTP exception**: if text contains *"do not share"* / *"never share"* and lacks external links or sharing requests, ensure score remains low.
  - Return `(rules_score, matched_flags, asks_credentials)`.

### Section 2.2: Local URL Inspector (`backend/url_inspector.py`)
- [x] **Task 2.2.1: URL extraction and domain parsing**
  - Extract all URLs from message text using robust regex.
  - Parse hostnames and paths locally using `urllib.parse` without making external network calls.

- [x] **Task 2.2.2: Risk heuristic rules for links**
  - Detect known shorteners (`bit.ly`, `tinyurl.com`, `t.co`, `cutt.ly`, etc.).
  - Flag suspicious TLDs (`.xyz`, `.top`, `.click`, `.live`, `.online`, etc.).
  - Implement brand lookalike detection via dictionary mapping genuine brands (SBI, HDFC, ICICI, Axis, Paytm, PhonePe, Amazon) against rogue hostnames.
  - Flag raw IP addresses, excessive subdomains/hyphens, and non-HTTPS protocols (`http://`).
  - Classify each URL into `low`, `medium`, or `high` risk and compile `LinkDetail` objects.

### Section 2.3: Multimodal LLM Intelligence (`backend/llm.py`)
- [x] **Task 2.3.1: Google Gemini API client integration**
  - Initialize Gemini client via `google-genai` SDK using `GEMINI_API_KEY` and `GEMINI_MODEL`.
  - Support both plain text input and multimodal image bytes input (PNG/JPG screenshots).

- [x] **Task 2.3.2: System prompt, structured JSON enforcement & resilience**
  - Embed the exact verbatim system prompt from `SATARK_PROJECT.md` Section 5.3.
  - Enforce JSON response output.
  - Implement code-fence cleanup, schema parsing, and a single-retry mechanism on malformed output.
  - Ensure graceful fallback returning `None` if the LLM call fails or times out.

### Section 2.4: Score Synthesis & Fallback Templating (`backend/scoring.py`)
- [x] **Task 2.4.1: Weighted scoring calculation & hard floors**
  - Calculate `risk_score = round(0.4 * rules_score + 0.6 * llm_score)` when LLM is available, or use `rules_score` alone if unavailable (`ai_available = False`).
  - Enforce **Hard Floor of 40**: elevate score to at least 40 if credential sharing is requested or any high-risk URL is present.
  - Classify verdict into bands: `< 35` (**Safe**), `35 - 65` (**Suspicious**), `> 65` (**Likely Scam**).

- [x] **Task 2.4.2: Red flag consolidation & template fallback generation**
  - Deduplicate and combine red flags from rules, URLs, and LLM (maximum 6 flags).
  - Build contextual `next_steps` (standard advisory for Safe; block sender, cybercrime reporting, helpline 1930 for Suspicious/Likely Scam).
  - Implement fallback bilingual templates (`explanation_en`, `explanation_hi`, `family_alert`, `report_summary`) for cases where the LLM is unreachable.

### Section 2.5: Analysis Endpoint Integration (`backend/main.py`)
- [x] **Task 2.5.1: Multipart request handler for `POST /analyze`**
  - Accept optional `text` (form field) and optional `image` (`UploadFile`, max 5MB, image MIME validation).
  - Validate that at least one of `text` or `image` is provided; return HTTP 422 otherwise.
  - Coordinate the execution flow: OCR/text extraction -> rules -> URL inspection -> LLM evaluation -> scoring synthesis -> return `AnalyzeResponse`.

---

## Phase 3: Frontend Foundation & User Inputs

### Section 3.1: Frontend Scaffolding & Setup (`frontend/`)
- [x] **Task 3.1.1: Vite React project setup with Tailwind CSS**
  - Initialize Vite React project in `frontend/`.
  - Configure Tailwind CSS, mobile-first responsive breakpoints, and custom theme tokens (calm blue/white, emerald/amber/red status colors).
  - Configure `.env.example` and `.env` with `VITE_API_URL=http://localhost:8000`.

- [x] **Task 3.1.2: Design system typography, icons & base CSS (`frontend/src/index.css`)**
  - Import clean modern typography (Inter / Outfit).
  - Set up global reset, smooth scrolling, accessible focus states, and custom transitions.

### Section 3.2: Application Header & Language Control
- [x] **Task 3.2.1: Navigation header & privacy guarantee badge**
  - Build `Header.jsx` displaying Satark logo, tagline, and prominent privacy badge (*"Your message is analyzed and never stored"*).
  - Add bilingual toggle button (**EN / हिं**) controlling active language state across the app.

### Section 3.3: Interactive Input Section
- [x] **Task 3.3.1: Message textarea & screenshot drop-zone (`frontend/src/components/InputCard.jsx`)**
  - Build responsive input textarea with clear placeholder and character counter.
  - Implement drag-and-drop file upload zone for screenshot images (PNG/JPG up to 5MB) with thumbnail preview and removal button.
  - Add client-side validation for file size and MIME type.

- [x] **Task 3.3.2: Sample test chips (`frontend/src/components/SampleChips.jsx`)**
  - Create a dataset of 8 realistic sample messages:
    - 4 Scams: Hinglish fake KYC, Fake loan approval with short link, Lottery prize with release fee, Fake electricity disconnection threat.
    - 4 Genuine: Real bank OTP delivery alert, Courier delivery update, UPI credit notification, Food-delivery app login OTP.
  - Implement interactive chips that auto-populate the textarea on click.

- [x] **Task 3.3.3: Analysis trigger & loading skeleton**
  - Implement primary **Analyze** button with disabled states when inputs are empty.
  - Build a shimmering loading skeleton representing the result card during active network requests.

---

## Phase 4: Frontend Result Presentation & Interactivity

### Section 4.1: Verdict & Risk Meter
- [x] **Task 4.1.1: Verdict banner & animated SVG circular risk gauge (`frontend/src/components/RiskGauge.jsx`)**
  - Create color-coded verdict banner (Emerald for Safe, Amber for Suspicious, Rose/Red for Likely Scam).
  - Build an animated circular progress gauge displaying the numerical risk score (0–100) with dynamic stroke animations.

- [x] **Task 4.1.2: AI availability alert badge**
  - Render an informative warning banner whenever `ai_available === false` (*"AI analysis unavailable, showing rule-based result only"*).

### Section 4.2: Message In-Context Highlighting
- [x] **Task 4.2.1: Safe phrase highlighter (`frontend/src/components/HighlightedMessage.jsx`)**
  - Display the original or extracted message text with `suspicious_phrases` highlighted in amber/red badges.
  - Implement safe, case-insensitive substring search and text splitting to prevent XSS injection.
  - Ensure graceful rendering if no phrases match.

### Section 4.3: Scoring Breakdown & Scam Explanations
- [x] **Task 4.3.1: Dual score contribution bar & red flag chips**
  - Build the *"How we got this score"* component showing comparative contribution bars for Rule-based vs. AI scores.
  - Render red flag badges with distinct warning icons (up to 6 flags).

- [x] **Task 4.3.2: Scam taxonomy & mechanism explainer**
  - Display scam category badge (e.g., Fake KYC, Lottery / Prize, OTP Theft).
  - Implement *"How this scam works"* educational card explaining the fraud mechanism in simple language.

### Section 4.4: Local Link Inspector Table
- [x] **Task 4.4.1: URL risk inspection table (`frontend/src/components/LinkInspector.jsx`)**
  - Conditionally render when links are found.
  - Present tabular breakdown: Target Domain, Shortener status, Suspicious TLD indicator, Brand Lookalike alerts, and Risk badge (Low/Medium/High).

### Section 4.5: Actionable Guidance & Quick Sharing
- [x] **Task 4.5.1: Recommended next steps checklist**
  - Display dynamic action items based on verdict.
  - Highlight official external links: National Cyber Crime Reporting Portal (`cybercrime.gov.in`) and 1930 Helpline.

- [x] **Task 4.5.2: Copyable Family Alert & Cybercrime Report Summary**
  - Build **Copy Family Alert** button for pre-formatted WhatsApp/SMS warnings.
  - Build **Copy Report Summary** button for pre-formatted complaint text.
  - Implement clipboard integration with an animated floating "Copied!" toast message.

### Section 4.6: Footer & Reset Actions
- [x] **Task 4.6.1: Footer and reset controls (`frontend/src/components/Footer.jsx`)**
  - Render statutory decision-support disclaimer (*"Satark is a decision-support tool, not a guarantee. When in doubt, contact your bank using the number on your card."*).
  - Provide a **"Try another message"** reset button that clears state and scrolls to top.
  - Include quick link to backend `/docs`.

---

## Phase 5: Bilingual Localization (EN / Hindi)

### Section 5.1: i18n Translation Dictionary
- [x] **Task 5.1.1: Comprehensive translation map (`frontend/src/i18n.js`)**
  - Define bilingual strings for all UI headers, button labels, placeholders, card headings, sample chip labels, disclaimers, and toast messages.
  - Connect language state to toggle `explanation_en` vs. `explanation_hi` and `family_alert.en` vs. `family_alert.hi`.

---

## Phase 6: Testing & Quality Assurance

### Section 6.1: Backend Automated Validation
- [x] **Task 6.1.1: Automated test suite for detection accuracy (`backend/tests/test_detection.py`)**
  - Write test cases for all 8 standard samples: verify 4 scam samples return Suspicious or Likely Scam; verify 4 genuine samples return Safe.
  - Explicit test: Ensure genuine OTP message with *"do not share"* scores as Safe.
  - Test URL inspector against sample suspicious domains and brand lookalikes.
  - Test fallback scoring when LLM returns `None`.

### Section 6.2: Frontend UX & Responsive Verification
- [x] **Task 6.2.1: Mobile responsiveness & interactive checks**
  - Verify layout integrity and touch targets at 360px viewport width.
  - Test clipboard copy functionality on both desktop and mobile viewports.
  - Verify image upload preview, file removal, and error handling for oversized files (> 5MB).

---

## Phase 7: Documentation & Polish

### Section 7.1: Project Documentation (`README.md`)
- [x] **Task 7.1.1: Production-grade README.md**
  - Write complete README meeting all 10 requirements of Section 10 in `SATARK_PROJECT.md`:
    1. Overview & Problem statement
    2. Key features
    3. Architecture diagram (Mermaid)
    4. Tech stack
    5. Setup & run instructions (backend venv & frontend npm)
    6. API reference with curl requests and response samples
    7. Scoring breakdown explanation (weights, hard floor, bands)
    8. Privacy and security guarantees (zero persistence)
    9. Limitations
    10. Forward-looking Roadmap.

- [x] **Task 7.1.2: Final review & UI polish**
  - Audit styling, micro-animations, contrast, and error states for a polished demo experience.
