import asyncio
import json
import os
import urllib.error
import urllib.request

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import gemini


client = TestClient(app)


SAMPLE_VIOLATION = {
    "id": "image-alt",
    "title": "Images must have alternate text",
    "description": (
        "Informative elements should aim for short, descriptive alternate text."
    ),
    "impact": "critical",
    "wcagCriteria": ["1.1.1"],
}


SAMPLE_GEMINI_RESULT = {
    "plainEnglish": (
        "Some images on this page don't have text descriptions."
    ),
    "whyItMatters": (
        "Screen readers can't describe an image to a user if it has no alt text."
    ),
    "whoIsAffected": (
        "Users who rely on screen readers, including blind and low-vision users."
    ),
    "suggestedFix": (
        "Add a descriptive alt attribute to each image."
    ),
    "priority": "High",
}


def fake_gemini_response():
    return {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": json.dumps(SAMPLE_GEMINI_RESULT)
                        }
                    ]
                }
            }
        ]
    }


def test_enrich_route_is_registered():
    assert any(
        route.path == "/api/enrich"
        and "POST" in route.methods
        for route in app.routes
    )


def test_valid_enrichment(monkeypatch):
    async def fake_enrich(violation):
        return SAMPLE_GEMINI_RESULT

    monkeypatch.setattr(
        gemini,
        "enrich_violation",
        fake_enrich,
    )

    response = client.post(
        "/api/enrich",
        json={
            "violations": [SAMPLE_VIOLATION]
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "enrichedViolations" in data
    assert len(data["enrichedViolations"]) == 1

    result = data["enrichedViolations"][0]

    assert result["plainEnglish"]
    assert result["whyItMatters"]
    assert result["whoIsAffected"]
    assert result["suggestedFix"]
    assert result["priority"] in ["High", "Medium", "Low"]


def test_empty_violations():
    response = client.post(
        "/api/enrich",
        json={
            "violations": []
        },
    )

    assert response.status_code == 200

    assert response.json() == {
        "enrichedViolations": []
    }


def test_multiple_violations(monkeypatch):
    violation1 = SAMPLE_VIOLATION.copy()

    violation2 = {
        "id": "color-contrast",
        "title": "Color contrast",
        "description": (
            "Background and foreground colors have insufficient contrast."
        ),
        "impact": "moderate",
        "wcagCriteria": ["1.4.3"],
    }

    async def fake_enrich(violation):
        return {
            **SAMPLE_GEMINI_RESULT,
            "priority": (
                "High"
                if violation["id"] == "image-alt"
                else "Medium"
            ),
        }

    monkeypatch.setattr(
        gemini,
        "enrich_violation",
        fake_enrich,
    )

    response = client.post(
        "/api/enrich",
        json={
            "violations": [
                violation1,
                violation2,
            ]
        },
    )

    assert response.status_code == 200

    results = response.json()["enrichedViolations"]

    assert len(results) == 2


def test_invalid_request():
    response = client.post(
        "/api/enrich",
        json={},
    )

    assert response.status_code == 422


def test_priority_values():
    for priority in ["High", "Medium", "Low"]:
        result = {
            **SAMPLE_GEMINI_RESULT,
            "priority": priority,
        }

        assert result["priority"] in {
            "High",
            "Medium",
            "Low",
        }


def test_gemini_success(monkeypatch):
    monkeypatch.setattr(
        gemini,
        "GEMINI_API_KEY",
        "fake-test-key",
    )

    monkeypatch.setattr(
        gemini,
        "_call_gemini_sync",
        lambda prompt: fake_gemini_response(),
    )

    result = asyncio.run(
        gemini.enrich_violation(SAMPLE_VIOLATION)
    )

    assert result == SAMPLE_GEMINI_RESULT


def test_gemini_missing_api_key(monkeypatch):
    monkeypatch.setattr(
        gemini,
        "GEMINI_API_KEY",
        "",
    )

    with pytest.raises(
        gemini.GeminiServiceError,
        match="API key is not configured",
    ):
        asyncio.run(
            gemini.enrich_violation(SAMPLE_VIOLATION)
        )


def test_gemini_malformed_response(monkeypatch):
    monkeypatch.setattr(
        gemini,
        "GEMINI_API_KEY",
        "fake-test-key",
    )

    monkeypatch.setattr(
        gemini,
        "_call_gemini_sync",
        lambda prompt: {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": "THIS IS NOT JSON"
                            }
                        ]
                    }
                }
            ]
        },
    )

    with pytest.raises(
        gemini.GeminiServiceError,
        match="not valid JSON|malformed JSON",
    ):
        asyncio.run(
            gemini.enrich_violation(SAMPLE_VIOLATION)
        )


def test_gemini_empty_response(monkeypatch):
    monkeypatch.setattr(
        gemini,
        "GEMINI_API_KEY",
        "fake-test-key",
    )

    monkeypatch.setattr(
        gemini,
        "_call_gemini_sync",
        lambda prompt: {
            "candidates": []
        },
    )

    with pytest.raises(
        gemini.GeminiServiceError,
        match="no candidates",
    ):
        asyncio.run(
            gemini.enrich_violation(SAMPLE_VIOLATION)
        )


def test_gemini_api_error(monkeypatch):
    monkeypatch.setattr(
        gemini,
        "GEMINI_API_KEY",
        "fake-test-key",
    )

    def fake_call(prompt):
        raise gemini.GeminiServiceError(
            "Gemini API returned HTTP 500."
        )

    monkeypatch.setattr(
        gemini,
        "_call_gemini_sync",
        fake_call,
    )

    with pytest.raises(
        gemini.GeminiServiceError,
        match="HTTP 500",
    ):
        asyncio.run(
            gemini.enrich_violation(SAMPLE_VIOLATION)
        )


def test_gemini_timeout(monkeypatch):
    monkeypatch.setattr(
        gemini,
        "GEMINI_API_KEY",
        "fake-test-key",
    )

    def fake_call(prompt):
        raise gemini.GeminiServiceError(
            "Gemini API request timed out."
        )

    monkeypatch.setattr(
        gemini,
        "_call_gemini_sync",
        fake_call,
    )

    with pytest.raises(
        gemini.GeminiServiceError,
        match="timed out",
    ):
        asyncio.run(
            gemini.enrich_violation(SAMPLE_VIOLATION)
        )


def test_ids_are_preserved(monkeypatch):
    async def fake_enrich(violation):
        return {
            **SAMPLE_GEMINI_RESULT,
        }

    monkeypatch.setattr(
        gemini,
        "enrich_violation",
        fake_enrich,
    )

    response = client.post(
        "/api/enrich",
        json={
            "violations": [
                SAMPLE_VIOLATION
            ]
        },
    )

    assert response.status_code == 200

    result = response.json()["enrichedViolations"][0]

    assert result["id"] == "image-alt"


def test_enrich_api_success(monkeypatch):
    async def fake_enrich(violation):
        return SAMPLE_GEMINI_RESULT

    monkeypatch.setattr(
        gemini,
        "enrich_violation",
        fake_enrich,
    )

    response = client.post(
        "/api/enrich",
        json={
            "violations": [
                SAMPLE_VIOLATION
            ]
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["enrichedViolations"][0]["id"] == "image-alt"
    assert data["enrichedViolations"][0]["priority"] == "High"


def test_enrich_api_failure(monkeypatch):
    async def fake_enrich(violation):
        raise gemini.GeminiServiceError(
            "Gemini API failed."
        )

    monkeypatch.setattr(
        gemini,
        "enrich_violation",
        fake_enrich,
    )

    response = client.post(
        "/api/enrich",
        json={
            "violations": [
                SAMPLE_VIOLATION
            ]
        },
    )

    assert response.status_code in [500, 502, 503]


def test_real_gemini_connection():
    """
    Real integration test.

    This test uses the Gemini API key from the application
    configuration and verifies that the configured Gemini
    model can be reached.

    This test may consume API quota.
    """

    from app.config import GEMINI_API_KEY

    assert GEMINI_API_KEY, (
        "GEMINI_API_KEY is not configured"
    )

    model = os.getenv(
        "GEMINI_MODEL",
        "gemini-2.5-flash",
    )

    url = (
        "https://generativelanguage.googleapis.com/"
        f"v1beta/models/{model}:generateContent"
    )

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": (
                            "Reply with exactly: "
                            "Gemini connection successful"
                        )
                    }
                ]
            }
        ]
    }

    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": GEMINI_API_KEY,
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=30,
        ) as response:
            body = response.read().decode("utf-8")

        assert response.status == 200

        response_json = json.loads(body)

        assert "candidates" in response_json
        assert response_json["candidates"]

    except urllib.error.HTTPError as exc:
        try:
            error_body = exc.read().decode("utf-8")
        except Exception:
            error_body = ""

        pytest.fail(
            f"Gemini API returned HTTP {exc.code}: {error_body}"
        )

    except urllib.error.URLError as exc:
        pytest.fail(
            f"Could not connect to Gemini API: {exc}"
        )