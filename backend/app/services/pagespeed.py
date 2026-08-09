import time
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import httpx
from fastapi import HTTPException, status

from app.config import PAGESPEED_API_KEY
from app.models.schemas import (
    CategoryCounts,
    Impact,
    ScanResponse,
    Severity,
    Violation,
)


PAGESPEED_API_URL = (
    "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
)

PAGESPEED_TIMEOUT_SECONDS = 30
CACHE_TTL_SECONDS = 3600

_CACHE: Dict[str, Dict[str, Any]] = {}


# ---------------------------------------------------------------------------
# URL VALIDATION
# ---------------------------------------------------------------------------

def validate_website_url(url: str) -> str:
    if not isinstance(url, str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="URL must be a string.",
        )

    cleaned = url.strip()

    if not cleaned:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="URL must not be empty.",
        )

    parsed = urlparse(cleaned)

    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Invalid URL. Please provide a valid "
                "http or https URL."
            ),
        )

    return cleaned


# ---------------------------------------------------------------------------
# CACHE
# ---------------------------------------------------------------------------

def _get_cache_key(url: str) -> str:
    return url.strip().lower().rstrip("/")


def _get_cached_result(
    url: str,
) -> Optional[ScanResponse]:

    key = _get_cache_key(url)

    cached = _CACHE.get(key)

    if cached is None:
        return None

    if time.time() > cached["expires_at"]:
        _CACHE.pop(key, None)
        return None

    return cached["value"]


def _set_cached_result(
    url: str,
    value: ScanResponse,
) -> None:

    key = _get_cache_key(url)

    _CACHE[key] = {
        "value": value,
        "expires_at": (
            time.time() + CACHE_TTL_SECONDS
        ),
    }


def clear_cache() -> None:
    _CACHE.clear()


# ---------------------------------------------------------------------------
# IMPACT / SEVERITY
# ---------------------------------------------------------------------------

def normalize_impact(
    impact: Optional[str],
) -> Impact:

    normalized = (impact or "").strip().lower()

    if normalized == "critical":
        return Impact.critical

    if normalized == "serious":
        return Impact.serious

    if normalized == "moderate":
        return Impact.moderate

    if normalized == "minor":
        return Impact.minor

    # Shared schema does not allow "unknown".
    return Impact.moderate


def map_impact_to_severity(
    impact: Optional[str],
) -> Severity:

    normalized = (impact or "").strip().lower()

    if normalized in {"critical", "serious"}:
        return Severity.critical

    if normalized == "moderate":
        return Severity.moderate

    if normalized == "minor":
        return Severity.minor

    return Severity.moderate


# ---------------------------------------------------------------------------
# ACCESSIBILITY AUDIT DETECTION
# ---------------------------------------------------------------------------

def _get_accessibility_audit_ids(
    lighthouse_result: Dict[str, Any],
) -> Optional[set]:
    """
    Return the authoritative set of audit IDs that belong to the
    "accessibility" category, straight from Lighthouse's own category
    metadata.

    This is the correct source of truth: `audit.tags` is essentially
    never populated on individual audit objects in the PageSpeed
    Insights API response, and any hardcoded ID whitelist will always
    drift out of date as Lighthouse adds/renames/removes audits. The
    `categories.accessibility.auditRefs` list is what Lighthouse itself
    uses to decide which audits count toward the accessibility score,
    so it's the one place we can trust.

    Returns None if this metadata isn't present, so callers can fall
    back to the legacy heuristics.
    """

    categories = lighthouse_result.get("categories")

    if not isinstance(categories, dict):
        return None

    accessibility = categories.get("accessibility")

    if not isinstance(accessibility, dict):
        return None

    audit_refs = accessibility.get("auditRefs")

    if not isinstance(audit_refs, list):
        return None

    ids = set()

    for ref in audit_refs:

        if not isinstance(ref, dict):
            continue

        ref_id = ref.get("id")

        if isinstance(ref_id, str) and ref_id.strip():
            ids.add(ref_id.strip().lower())

    return ids if ids else None


def _is_accessibility_audit(
    audit_id: str,
    audit: Dict[str, Any],
) -> bool:

    if not isinstance(audit, dict):
        return False

    tags = audit.get("tags")

    if isinstance(tags, list):

        normalized_tags = {
            str(tag).strip().lower()
            for tag in tags
            if isinstance(tag, str)
        }

        if any(
            tag == "accessibility"
            or tag.startswith("cat.accessibility")
            or tag.startswith("wcag")
            for tag in normalized_tags
        ):
            return True

    details = audit.get("details")

    if isinstance(details, dict):

        debug_data = details.get("debugData")

        if isinstance(debug_data, dict):

            debug_tags = debug_data.get("tags")

            if isinstance(debug_tags, list):

                normalized_tags = {
                    str(tag).strip().lower()
                    for tag in debug_tags
                    if isinstance(tag, str)
                }

                if any(
                    tag == "accessibility"
                    or tag.startswith("cat.accessibility")
                    or tag.startswith("wcag")
                    for tag in normalized_tags
                ):
                    return True

    # Fallback only: used when the caller couldn't determine the
    # authoritative auditRefs set (see _get_accessibility_audit_ids).
    # This list is NOT exhaustive and will miss newer/renamed audits
    # (e.g. "landmark-one-main", "heading-order", "bypass",
    # "empty-heading", "target-size", various "aria-required-*"
    # checks) — it exists only as a last-resort safety net.
    known_accessibility_ids = {
        "accesskeys",
        "aria-allowed-attr",
        "aria-allowed-role",
        "aria-command-name",
        "aria-conditional-attr",
        "aria-deprecated-role",
        "aria-dialog-name",
        "aria-hidden-body",
        "aria-hidden-focus",
        "aria-input-field-name",
        "aria-meter-name",
        "aria-progressbar-name",
        "aria-prohibited-attr",
        "aria-required-attr",
        "aria-required-children",
        "aria-required-parent",
        "aria-roles",
        "aria-text",
        "aria-toggle-field-name",
        "aria-tooltip-name",
        "aria-treeitem-name",
        "aria-valid-attr-value",
        "aria-valid-attr",
        "bypass",
        "button-name",
        "color-contrast",
        "definition-list",
        "dlitem",
        "document-title",
        "duplicate-id-aria",
        "empty-heading",
        "form-field-multiple-labels",
        "frame-title",
        "heading-order",
        "html-has-lang",
        "html-lang-valid",
        "html-xml-lang-mismatch",
        "identical-links-same-purpose",
        "image-alt",
        "image-redundant-alt",
        "input-button-name",
        "input-image-alt",
        "label-content-name-mismatch",
        "label",
        "landmark-one-main",
        "link-name",
        "link-in-text-block",
        "list",
        "listitem",
        "meta-refresh",
        "meta-viewport",
        "object-alt",
        "select-name",
        "skip-link",
        "tabindex",
        "target-size",
        "table-duplicate-name",
        "table-fake-caption",
        "td-has-header",
        "td-headers-attr",
        "th-has-data-cells",
        "valid-lang",
        "video-caption",
    }

    return audit_id.lower() in known_accessibility_ids


def _is_failed_audit(
    audit: Dict[str, Any],
) -> bool:

    if not isinstance(audit, dict):
        return False

    if audit.get("scoreDisplayMode") in {
        "notApplicable",
        "manual",
        "informative",
        "error",
    }:
        return False

    score = audit.get("score")

    if score is None:
        return False

    try:
        numeric_score = float(score)
    except (TypeError, ValueError):
        return False

    return numeric_score < 1.0


def _is_failed_accessibility_audit(
    audit_id: str,
    audit: Dict[str, Any],
    accessibility_audit_ids: Optional[set] = None,
) -> bool:

    if accessibility_audit_ids is not None:
        is_accessibility = audit_id.lower() in accessibility_audit_ids
    else:
        is_accessibility = _is_accessibility_audit(
            audit_id,
            audit,
        )

    return (
        is_accessibility
        and _is_failed_audit(audit)
    )


# ---------------------------------------------------------------------------
# WCAG
# ---------------------------------------------------------------------------

def _extract_wcag_criteria(
    audit: Dict[str, Any],
) -> List[str]:

    collected: List[str] = []

    def collect_tags(tags: Any) -> None:

        if not isinstance(tags, list):
            return

        for tag in tags:

            if not isinstance(tag, str):
                continue

            cleaned = tag.strip()

            if cleaned.lower().startswith("wcag"):
                collected.append(cleaned)

    collect_tags(audit.get("tags"))

    details = audit.get("details")

    if isinstance(details, dict):

        debug_data = details.get("debugData")

        if isinstance(debug_data, dict):
            collect_tags(
                debug_data.get("tags")
            )

    unique: List[str] = []
    seen = set()

    for criterion in collected:

        key = criterion.lower()

        if key not in seen:
            seen.add(key)
            unique.append(criterion)

    return unique


# ---------------------------------------------------------------------------
# AFFECTED NODES
# ---------------------------------------------------------------------------

def _extract_affected_nodes(
    audit: Dict[str, Any],
) -> int:

    details = audit.get("details")

    if not isinstance(details, dict):
        return 0

    items = details.get("items")

    if isinstance(items, list):
        return len(items)

    nodes = details.get("nodes")

    if isinstance(nodes, list):
        return len(nodes)

    return 0


# ---------------------------------------------------------------------------
# VIOLATION NORMALIZATION
# ---------------------------------------------------------------------------

def _extract_impact(
    audit: Dict[str, Any],
) -> Optional[str]:
    """
    Pull the axe-core impact rating (minor/moderate/serious/critical)
    for this audit.

    In the real PageSpeed Insights response this lives nested at
    details.debugData.impact — audits don't carry a top-level "impact"
    key. We check both: debugData first (the actual location), then a
    top-level key as a defensive fallback in case that ever changes.
    """

    details = audit.get("details")

    if isinstance(details, dict):

        debug_data = details.get("debugData")

        if isinstance(debug_data, dict):

            nested_impact = debug_data.get("impact")

            if isinstance(nested_impact, str) and nested_impact.strip():
                return nested_impact

    top_level_impact = audit.get("impact")

    if isinstance(top_level_impact, str) and top_level_impact.strip():
        return top_level_impact

    return None


def _normalize_violation(
    audit_id: str,
    audit: Dict[str, Any],
) -> Violation:

    raw_impact = _extract_impact(audit)

    return Violation(
        id=audit_id,
        title=str(
            audit.get("title")
            or audit_id
        ),
        description=str(
            audit.get("description")
            or "Accessibility issue detected."
        ),
        impact=normalize_impact(
            raw_impact
        ),
        wcagCriteria=_extract_wcag_criteria(
            audit
        ),
        affectedNodes=_extract_affected_nodes(
            audit
        ),
        severity=map_impact_to_severity(
            raw_impact
        ),
    )


# ---------------------------------------------------------------------------
# CATEGORY COUNTS
# ---------------------------------------------------------------------------

def _calculate_category_counts(
    violations: List[Violation],
) -> CategoryCounts:

    return CategoryCounts(
        critical=sum(
            violation.severity
            == Severity.critical
            for violation in violations
        ),
        moderate=sum(
            violation.severity
            == Severity.moderate
            for violation in violations
        ),
        minor=sum(
            violation.severity
            == Severity.minor
            for violation in violations
        ),
    )


# ---------------------------------------------------------------------------
# SCORE
# ---------------------------------------------------------------------------

def _extract_overall_score(
    lighthouse_result: Dict[str, Any],
) -> int:

    categories = lighthouse_result.get(
        "categories"
    )

    if not isinstance(categories, dict):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "Malformed PageSpeed response: "
                "missing categories."
            ),
        )

    accessibility = categories.get(
        "accessibility"
    )

    if not isinstance(accessibility, dict):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "Malformed PageSpeed response: "
                "missing accessibility category."
            ),
        )

    raw_score = accessibility.get("score")

    if raw_score is None:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "Malformed PageSpeed response: "
                "missing accessibility score."
            ),
        )

    try:
        score = round(
            float(raw_score) * 100
        )

    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "Malformed PageSpeed response: "
                "invalid accessibility score."
            ),
        ) from None

    return max(
        0,
        min(100, score),
    )


# ---------------------------------------------------------------------------
# RESPONSE PARSING
# ---------------------------------------------------------------------------

def parse_pagespeed_response(
    target_url: str,
    payload: Dict[str, Any],
) -> ScanResponse:

    if not isinstance(payload, dict):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Malformed PageSpeed response.",
        )

    lighthouse_result = payload.get(
        "lighthouseResult"
    )

    if not isinstance(
        lighthouse_result,
        dict,
    ):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "Malformed PageSpeed response: "
                "missing lighthouseResult."
            ),
        )

    overall_score = _extract_overall_score(
        lighthouse_result
    )

    audits = lighthouse_result.get(
        "audits"
    )

    if not isinstance(audits, dict):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "Malformed PageSpeed response: "
                "missing audits."
            ),
        )

    violations: List[Violation] = []

    accessibility_audit_ids = _get_accessibility_audit_ids(
        lighthouse_result
    )

    for audit_id, audit in audits.items():

        if not isinstance(audit_id, str):
            continue

        if not isinstance(audit, dict):
            continue

        if not _is_failed_accessibility_audit(
            audit_id,
            audit,
            accessibility_audit_ids,
        ):
            continue

        violations.append(
            _normalize_violation(
                audit_id,
                audit,
            )
        )

    return ScanResponse(
        url=target_url,
        overallScore=overall_score,
        categoryCounts=_calculate_category_counts(
            violations
        ),
        violations=violations,
    )


# ---------------------------------------------------------------------------
# PAGESPEED API
# ---------------------------------------------------------------------------

async def fetch_pagespeed_data(
    url: str,
) -> Dict[str, Any]:

    if not PAGESPEED_API_KEY:
        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                "PageSpeed API key is not configured."
            ),
        )

    params = {
        "url": url,
        "category": "accessibility",
        "strategy": "mobile",
        "key": PAGESPEED_API_KEY,
    }

    timeout = httpx.Timeout(
        PAGESPEED_TIMEOUT_SECONDS
    )

    try:

        async with httpx.AsyncClient(
            timeout=timeout
        ) as client:

            response = await client.get(
                PAGESPEED_API_URL,
                params=params,
            )

    except httpx.TimeoutException as exc:

        raise HTTPException(
            status_code=(
                status.HTTP_504_GATEWAY_TIMEOUT
            ),
            detail="PageSpeed request timed out.",
        ) from exc

    except httpx.RequestError as exc:

        raise HTTPException(
            status_code=(
                status.HTTP_502_BAD_GATEWAY
            ),
            detail=(
                "Failed to reach PageSpeed "
                "Insights API."
            ),
        ) from exc

    if response.status_code == 400:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "PageSpeed rejected the request. "
                "Check the target URL."
            ),
        )

    if response.status_code == 403:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "PageSpeed API access was denied. "
                "Check the API key and quota settings."
            ),
        )

    if response.status_code == 429:

        raise HTTPException(
            status_code=(
                status.HTTP_429_TOO_MANY_REQUESTS
            ),
            detail=(
                "PageSpeed rate limit exceeded. "
                "Please try again later."
            ),
        )

    if response.status_code >= 500:

        raise HTTPException(
            status_code=(
                status.HTTP_502_BAD_GATEWAY
            ),
            detail=(
                "PageSpeed Insights API "
                "is currently unavailable."
            ),
        )

    if response.status_code >= 400:

        raise HTTPException(
            status_code=(
                status.HTTP_502_BAD_GATEWAY
            ),
            detail=(
                "Unexpected error from "
                "PageSpeed Insights API."
            ),
        )

    try:

        payload = response.json()

    except ValueError as exc:

        raise HTTPException(
            status_code=(
                status.HTTP_502_BAD_GATEWAY
            ),
            detail=(
                "PageSpeed returned invalid JSON."
            ),
        ) from exc

    if not isinstance(payload, dict):

        raise HTTPException(
            status_code=(
                status.HTTP_502_BAD_GATEWAY
            ),
            detail=(
                "PageSpeed returned an invalid response."
            ),
        )

    return payload


# ---------------------------------------------------------------------------
# MAIN SCAN
# ---------------------------------------------------------------------------

async def scan_url_with_pagespeed(
    url: str,
) -> ScanResponse:

    validated_url = validate_website_url(
        url
    )

    cached = _get_cached_result(
        validated_url
    )

    if cached is not None:
        return cached

    payload = await fetch_pagespeed_data(
        validated_url
    )

    parsed = parse_pagespeed_response(
        validated_url,
        payload,
    )

    _set_cached_result(
        validated_url,
        parsed,
    )

    return parsed