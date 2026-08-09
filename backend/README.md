# AccessLens Backend

AccessLens is an accessibility analysis backend that scans websites for accessibility issues, enriches detected violations using Google Gemini AI, and generates accessibility reports.

This repository contains the **FastAPI backend** for AccessLens.

## Features

- Website accessibility scanning using Google PageSpeed Insights API
- Accessibility violation detection and normalization
- Severity classification
- Accessibility score extraction
- Accessibility category counts
- Gemini AI-powered violation enrichment
- Plain-English explanations of accessibility issues
- Explanation of why each issue matters
- Identification of affected users
- Developer-friendly suggested fixes
- Automatic priority classification
- PDF accessibility report generation
- Request validation and error handling
- API response validation
- Automated unit and integration tests
- Real Gemini API connection testing

---

## Technology Stack

- **Python 3.13**
- **FastAPI**
- **Uvicorn**
- **Pydantic**
- **Google PageSpeed Insights API**
- **Google Gemini API**
- **python-dotenv**
- **Pytest**
- **pytest-asyncio**

The backend uses Python's standard library for the Gemini REST API request, so an additional Gemini SDK is not required.

---

## Project Structure

```text
backend/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   │
│   ├── routes/
│   │   ├── ...
│   │
│   ├── services/
│   │   ├── ...
│   │
│   └── ...
│
├── tests/
│   ├── test_module3.py
│   ├── test_module4.py
│   └── ...
│
├── requirements.txt
├── .gitignore
└── README.md
```

> The exact internal file structure may contain additional files depending on the current implementation.

---

# 1. Requirements

Make sure the following are installed:

- Python 3.13 or compatible Python version
- Git
- Internet connection
- Google PageSpeed Insights API key
- Google Gemini API key

---

# 2. Create and Activate Virtual Environment

From the `backend` directory:

### Windows PowerShell

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

If activation is successful, the terminal should show:

```text
(.venv)
```

---

# 3. Install Dependencies

Install the required Python packages:

```powershell
pip install -r requirements.txt
```

---

# 4. Environment Variables

Create a `.env` file inside the `backend` directory.

```text
backend/
├── .env
├── app/
├── tests/
└── requirements.txt
```

Add the following:

```env
PAGESPEED_API_KEY=your_pagespeed_api_key
GEMINI_API_KEY=your_gemini_api_key
ALLOWED_ORIGINS=*
```

### Environment variables

| Variable | Purpose |
|---|---|
| `PAGESPEED_API_KEY` | Used to access Google PageSpeed Insights |
| `GEMINI_API_KEY` | Used for AI-powered accessibility enrichment |
| `ALLOWED_ORIGINS` | Controls allowed frontend origins for CORS |

For local development:

```env
ALLOWED_ORIGINS=*
```

For production, replace `*` with the actual frontend URL.

### Important Security Rule

**Never commit `.env` to GitHub.**

The `.gitignore` file should contain:

```gitignore
.env
.env.local
*.env
```

API keys must never be hardcoded into Python source files.

---

# 5. Run the Backend

From the `backend` directory:

```powershell
uvicorn app.main:app --reload
```

The backend should start at:

```text
http://127.0.0.1:8000
```

---

# 6. API Documentation

FastAPI automatically provides interactive Swagger documentation.

Open:

```text
http://127.0.0.1:8000/docs
```

OpenAPI specification:

```text
http://127.0.0.1:8000/openapi.json
```

---

# 7. API Endpoints

## Health Check

### Request

```http
GET /health
```

Example:

```powershell
curl.exe http://127.0.0.1:8000/health
```

This endpoint verifies that the backend is running.

---

# 8. Website Accessibility Scan

## Endpoint

```http
POST /api/scan
```

This endpoint accepts a website URL and uses Google PageSpeed Insights to analyze its accessibility.

### Example

```powershell
curl.exe -X POST "http://127.0.0.1:8000/api/scan" -H "Content-Type: application/json" -d '{"url":"https://example.com"}'
```

The scan processes accessibility-related information and returns normalized accessibility results.

The scan functionality includes:

- Accessibility score
- Accessibility violations
- Violation IDs
- Violation titles
- Technical descriptions
- Impact/severity
- WCAG criteria
- Category counts

---

# 9. Gemini Accessibility Enrichment

## Endpoint

```http
POST /api/enrich
```

This endpoint sends accessibility violations to Google Gemini and converts technical accessibility information into easier-to-understand explanations.

Each violation is enriched with:

- `plainEnglish`
- `whyItMatters`
- `whoIsAffected`
- `suggestedFix`
- `priority`

### Example Request

```json
{
  "violations": [
    {
      "id": "image-alt",
      "title": "Images must have alternate text",
      "description": "Informative elements should aim for short, descriptive alternate text.",
      "impact": "critical",
      "wcagCriteria": [
        "1.1.1"
      ]
    }
  ]
}
```

### Example Response

```json
{
  "enrichedViolations": [
    {
      "id": "image-alt",
      "plainEnglish": "Images on the webpage are missing alternative text descriptions.",
      "whyItMatters": "Screen readers rely on alternative text to describe images to users who cannot see them.",
      "whoIsAffected": "People who are blind or visually impaired who use screen readers.",
      "suggestedFix": "Add meaningful alt text to informative images. Use an empty alt attribute for decorative images.",
      "priority": "High"
    }
  ]
}
```

### Priority Values

Only the following values are accepted:

```text
High
Medium
Low
```

---

# 10. Report Export

## Endpoint

```http
POST /api/report/export
```

This endpoint generates an accessibility report in PDF format using scan results and Gemini enrichment results.

### Request

```json
{
  "scan_data": {},
  "enrichment_data": {}
}
```

The response is an:

```text
application/pdf
```

The generated report can contain accessibility scan information and AI-enriched explanations.

---

# 11. API Workflow

The intended AccessLens workflow is:

```text
                    ┌─────────────────┐
                    │     Frontend    │
                    └────────┬────────┘
                             │
                             ▼
                    POST /api/scan
                             │
                             ▼
                  PageSpeed Accessibility
                         Analysis
                             │
                             ▼
                    Scan Results
                             │
                             ▼
                   POST /api/enrich
                             │
                             ▼
                       Gemini AI
                             │
                             ▼
                   Enriched Violations
                             │
                             ▼
                POST /api/report/export
                             │
                             ▼
                       PDF Report
```

---

# 12. Running Tests

The backend contains automated tests for Module 3 and Module 4.

Run the complete test suite:

```powershell
python -m pytest -v
```

The current verified test result is:

```text
36 passed
```

The tests cover:

### Module 3

- Health endpoint
- Scan route registration
- Request validation
- Valid URLs
- Invalid URLs
- Empty URLs
- Score extraction
- Accessibility violation filtering
- Violation normalization
- Severity mapping
- Category counts
- Zero-violation handling
- PageSpeed success
- PageSpeed API errors
- PageSpeed timeout
- Cache behavior
- Scan API success

### Module 4

- Enrich route registration
- Valid enrichment
- Empty violation handling
- Multiple violations
- Invalid requests
- Priority validation
- Gemini success
- Missing API key handling
- Malformed Gemini response handling
- Empty Gemini response handling
- Gemini API error handling
- Gemini timeout handling
- Violation ID preservation
- Enrichment API success
- Enrichment API failure
- Real Gemini API connection

---

# 13. Verified Backend Status

The current backend has been manually and automatically verified.

```text
Module 3 tests              PASS
Module 4 tests              PASS
Gemini connection           PASS
/api/scan                   PASS
/api/enrich                 PASS
/api/report/export          PASS
Health endpoint             PASS
Automated tests             36/36 PASS
```

Latest complete test result:

```text
================ 36 passed in 3.15s ================
```

The `/api/report/export` endpoint has also been manually tested through Swagger and returned:

```text
200 OK
```

---

# 14. Testing with Swagger

Start the backend:

```powershell
uvicorn app.main:app --reload
```

Then open:

```text
http://127.0.0.1:8000/docs
```

From Swagger you can test:

```text
GET  /health
POST /api/scan
POST /api/enrich
POST /api/report/export
```

Swagger is recommended for manual API testing because it automatically displays the request and response schemas.

---

# 15. Important Files

### `app/config.py`

Responsible for loading environment variables such as:

```text
PAGESPEED_API_KEY
GEMINI_API_KEY
ALLOWED_ORIGINS
```

### Gemini service

Responsible for:

- Building the accessibility enrichment prompt
- Calling the Gemini REST API
- Extracting Gemini's response
- Validating the generated JSON
- Validating priority values
- Handling Gemini API errors

### Tests

The `tests/` directory contains the automated tests for the implemented modules.

---

# 16. Security

The following information must never be committed to GitHub:

```text
.env
API keys
Secret keys
Access tokens
Credentials
```

The `.gitignore` file should prevent sensitive environment files from being tracked.

If an API key is accidentally exposed publicly, revoke or rotate the key immediately.

---

# 17. GitHub Setup

Before pushing the backend to GitHub, make sure:

```text
.env              ❌
.venv/            ❌
__pycache__/      ❌
.pytest_cache/    ❌
*.pdf             ❌
```

are not committed.

The following should normally be committed:

```text
app/              ✅
tests/            ✅
requirements.txt  ✅
.gitignore        ✅
README.md         ✅
```

---

# 18. Development Notes

The backend is currently configured for local development.

Local backend URL:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

OpenAPI:

```text
http://127.0.0.1:8000/openapi.json
```

For frontend integration, configure the frontend API base URL to point to the running backend.

For production deployment, update:

- CORS configuration
- Environment variables
- API key configuration
- Backend hosting URL
- Frontend API base URL

---

# 19. License

This project is developed as part of the AccessLens project.

Add the appropriate license here if a project-specific license is selected.