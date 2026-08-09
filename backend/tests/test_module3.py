import pytest
import httpx

from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.main import app
from app.models.schemas import Impact, Severity
from app.routers import scan as scan_router
from app.services import pagespeed


def sample_pagespeed_payload():
    return {
        "lighthouseResult": {
            "categories": {
                "accessibility": {
                    "score": 0.85
                }
            },
            "audits": {
                "image-alt": {
                    "title": "Images have alt",
                    "description": "Images need alt text.",
                    "score": 0,
                    "scoreDisplayMode": "binary",
                    "impact": "serious",
                    "tags": [
                        "cat.accessibility",
                        "wcag111",
                    ],
                    "details": {
                        "items": [
                            {},
                            {},
                        ]
                    },
                },
                "color-contrast": {
                    "title": "Color contrast",
                    "description": "Contrast is insufficient.",
                    "score": 0,
                    "scoreDisplayMode": "binary",
                    "impact": "moderate",
                    "tags": [
                        "cat.accessibility",
                        "wcag143",
                    ],
                    "details": {
                        "items": [
                            {}
                        ]
                    },
                },
                "unused-javascript": {
                    "title": "Unused JavaScript",
                    "description": "Performance issue.",
                    "score": 0,
                    "scoreDisplayMode": "binary",
                    "impact": "serious",
                    "tags": [
                        "cat.performance"
                    ],
                    "details": {
                        "items": [
                            {},
                            {},
                            {},
                        ]
                    },
                },
                "manual-audit": {
                    "title": "Manual check",
                    "description": "Manual review.",
                    "score": 0,
                    "scoreDisplayMode": "manual",
                    "impact": "minor",
                    "tags": [
                        "cat.accessibility",
                        "wcag111",
                    ],
                },
            },
        }
    }


@pytest.fixture(autouse=True)
def clear_cache():
    pagespeed.clear_cache()
    yield
    pagespeed.clear_cache()


def test_health():
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_scan_route_is_registered():
    assert any(
        route.path == "/api/scan"
        and "POST" in route.methods
        for route in app.routes
    )


def test_scan_request_validation():
    client = TestClient(app)

    response = client.post(
        "/api/scan",
        json={},
    )

    assert response.status_code == 422


def test_valid_url():
    result = pagespeed.validate_website_url(
        " https://example.com/ "
    )

    assert result == "https://example.com/"


def test_invalid_url():
    with pytest.raises(HTTPException) as exc:
        pagespeed.validate_website_url(
            "example.com"
        )

    assert exc.value.status_code == 400


def test_empty_url():
    with pytest.raises(HTTPException) as exc:
        pagespeed.validate_website_url("")

    assert exc.value.status_code == 422


def test_score_extraction():
    result = pagespeed.parse_pagespeed_response(
        "https://example.com",
        sample_pagespeed_payload(),
    )

    assert result.overallScore == 85


def test_only_accessibility_violations():
    result = pagespeed.parse_pagespeed_response(
        "https://example.com",
        sample_pagespeed_payload(),
    )

    ids = {
        violation.id
        for violation in result.violations
    }

    assert "image-alt" in ids
    assert "color-contrast" in ids
    assert "unused-javascript" not in ids
    assert "manual-audit" not in ids


def test_violation_normalization():
    result = pagespeed.parse_pagespeed_response(
        "https://example.com",
        sample_pagespeed_payload(),
    )

    violation = next(
        item
        for item in result.violations
        if item.id == "image-alt"
    )

    assert violation.impact == Impact.serious
    assert violation.severity == Severity.critical
    assert violation.affectedNodes == 2
    assert "wcag111" in violation.wcagCriteria


def test_severity_mapping():
    assert (
        pagespeed.map_impact_to_severity("critical")
        == Severity.critical
    )

    assert (
        pagespeed.map_impact_to_severity("serious")
        == Severity.critical
    )

    assert (
        pagespeed.map_impact_to_severity("moderate")
        == Severity.moderate
    )

    assert (
        pagespeed.map_impact_to_severity("minor")
        == Severity.minor
    )


def test_category_counts():
    result = pagespeed.parse_pagespeed_response(
        "https://example.com",
        sample_pagespeed_payload(),
    )

    assert result.categoryCounts.critical == 1
    assert result.categoryCounts.moderate == 1
    assert result.categoryCounts.minor == 0


def test_zero_violations():
    payload = {
        "lighthouseResult": {
            "categories": {
                "accessibility": {
                    "score": 1
                }
            },
            "audits": {},
        }
    }

    result = pagespeed.parse_pagespeed_response(
        "https://example.com",
        payload,
    )

    assert result.overallScore == 100
    assert result.violations == []
    assert result.categoryCounts.critical == 0
    assert result.categoryCounts.moderate == 0
    assert result.categoryCounts.minor == 0


@pytest.mark.asyncio
async def test_pagespeed_success(monkeypatch):
    monkeypatch.setattr(
        pagespeed,
        "PAGESPEED_API_KEY",
        "test-key",
    )

    captured = {}

    class FakeResponse:
        status_code = 200

        def json(self):
            return sample_pagespeed_payload()

    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def get(self, url, params=None):
            captured["url"] = url
            captured["params"] = params
            return FakeResponse()

    monkeypatch.setattr(
        pagespeed.httpx,
        "AsyncClient",
        FakeClient,
    )

    result = await pagespeed.fetch_pagespeed_data(
        "https://example.com"
    )

    assert result == sample_pagespeed_payload()

    assert (
        captured["params"]["category"]
        == "accessibility"
    )

    assert (
        captured["params"]["strategy"]
        == "mobile"
    )

    assert (
        captured["params"]["key"]
        == "test-key"
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status_code, expected",
    [
        (400, 400),
        (403, 403),
        (429, 429),
        (500, 502),
    ],
)
async def test_pagespeed_errors(
    monkeypatch,
    status_code,
    expected,
):
    monkeypatch.setattr(
        pagespeed,
        "PAGESPEED_API_KEY",
        "test-key",
    )

    class FakeResponse:
        def __init__(self):
            self.status_code = status_code

    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def get(self, *args, **kwargs):
            return FakeResponse()

    monkeypatch.setattr(
        pagespeed.httpx,
        "AsyncClient",
        FakeClient,
    )

    with pytest.raises(HTTPException) as exc:
        await pagespeed.fetch_pagespeed_data(
            "https://example.com"
        )

    assert exc.value.status_code == expected


@pytest.mark.asyncio
async def test_pagespeed_timeout(monkeypatch):
    monkeypatch.setattr(
        pagespeed,
        "PAGESPEED_API_KEY",
        "test-key",
    )

    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def get(self, *args, **kwargs):
            raise httpx.ReadTimeout(
                "timed out"
            )

    monkeypatch.setattr(
        pagespeed.httpx,
        "AsyncClient",
        FakeClient,
    )

    with pytest.raises(HTTPException) as exc:
        await pagespeed.fetch_pagespeed_data(
            "https://example.com"
        )

    assert exc.value.status_code == 504


@pytest.mark.asyncio
async def test_cache_behavior(monkeypatch):
    calls = 0

    async def fake_fetch(url):
        nonlocal calls
        calls += 1
        return sample_pagespeed_payload()

    monkeypatch.setattr(
        pagespeed,
        "fetch_pagespeed_data",
        fake_fetch,
    )

    first = await pagespeed.scan_url_with_pagespeed(
        "https://example.com"
    )

    second = await pagespeed.scan_url_with_pagespeed(
        "https://example.com/"
    )

    assert calls == 1
    assert first == second


@pytest.mark.asyncio
async def test_scan_api_success(monkeypatch):
    result = pagespeed.parse_pagespeed_response(
        "https://example.com",
        sample_pagespeed_payload(),
    )

    async def fake_scan(url):
        return result

    # Patch the function where scan.py actually imported it.
    monkeypatch.setattr(
        scan_router,
        "scan_url_with_pagespeed",
        fake_scan,
    )

    client = TestClient(app)

    response = client.post(
        "/api/scan",
        json={
            "url": "https://example.com"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["overallScore"] == 85
    assert len(data["violations"]) == 2