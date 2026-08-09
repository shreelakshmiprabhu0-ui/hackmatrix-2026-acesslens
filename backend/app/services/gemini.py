"""
Gemini AI service for AccessLens Module 4.

This service takes a batch of accessibility violations from one scan
and asks Gemini, in a single request, to generate for each one:

- plain-English explanation
- why it matters
- who is affected
- suggested fix
- priority

All violations from a scan are sent in one Gemini call rather than
one call per violation. A typical scan has several violations, and
issuing one Gemini request per violation multiplied real API usage
(and rate-limit exposure) by however many violations were found —
observed in practice as intermittent 429 "rate limit exceeded"
errors on scans with several violations. Batching keeps quota usage
at one request per scan regardless of violation count.

The Gemini API key is read from app.config.
The API key must never be hardcoded in this file.
"""

import asyncio
import json
import re
from typing import Any, Dict, List

import httpx

from app.config import GEMINI_API_KEY, GEMINI_MODEL


GEMINI_API_URL = (
    "https://generativelanguage.googleapis.com/"
    f"v1beta/models/{GEMINI_MODEL}:generateContent"
)

GEMINI_TIMEOUT_SECONDS = 30


class GeminiServiceError(Exception):
    """Raised when Gemini cannot generate a valid enrichment result."""


def _build_batch_prompt(violations: List[Dict[str, Any]]) -> str:
    """Build a single prompt covering every violation in the batch."""

    violation_blocks = []

    for violation in violations:
        violation_id = violation.get("id", "")
        title = violation.get("title", "")
        description = violation.get("description", "")
        impact = violation.get("impact", "")
        wcag_criteria = violation.get("wcagCriteria", [])

        violation_blocks.append(
            f"""
Violation ID:
{violation_id}

Title:
{title}

Technical description:
{description}

Impact:
{impact}

WCAG criteria:
{json.dumps(wcag_criteria)}
""".strip()
        )

    joined_violations = "\n\n---\n\n".join(violation_blocks)

    return f"""
You are an expert web accessibility analyst.

Analyze EACH of the following accessibility violations. There are
{len(violations)} violation(s) below, separated by "---".

{joined_violations}

Return ONLY a valid JSON array with exactly one object per violation
above — {len(violations)} object(s) total, no more and no fewer.

Each object in the array must contain exactly these fields:

{{
  "id": "The violation's ID, copied exactly as given above.",
  "plainEnglish": "Explain the problem in simple language.",
  "whyItMatters": "Explain why this matters to users.",
  "whoIsAffected": "Explain which users may be affected.",
  "suggestedFix": "Give a practical developer-friendly fix.",
  "priority": "High"
}}

Priority must be exactly one of:

High
Medium
Low

Priority rules:

- Critical or serious problems: High
- Moderate problems: Medium
- Minor problems: Low

Do not use Markdown.
Do not use code fences.
Do not add text before or after the JSON array.
Do not invent WCAG criteria.
Do not omit any violation.
Do not invent violations that were not listed above.
Every "id" in your response must exactly match one of the violation
IDs given above.
""".strip()


def _strip_code_fences(text: str) -> str:
    """Remove Markdown code fences if Gemini wraps its response in them."""

    cleaned = text.strip()

    cleaned = re.sub(
        r"^```(?:json)?\s*",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )

    cleaned = re.sub(
        r"\s*```$",
        "",
        cleaned,
    )

    return cleaned.strip()


def _find_balanced_span(
    text: str,
    start: int,
    open_char: str,
    close_char: str,
) -> int:
    """
    Return the index of the char that closes the bracket opened at
    `start`, respecting string literals, or -1 if unbalanced.
    """

    depth = 0
    in_string = False
    escape = False

    for index in range(start, len(text)):
        char = text[index]

        if escape:
            escape = False
            continue

        if char == "\\" and in_string:
            escape = True
            continue

        if char == '"':
            in_string = not in_string
            continue

        if in_string:
            continue

        if char == open_char:
            depth += 1

        elif char == close_char:
            depth -= 1

            if depth == 0:
                return index

    return -1


def _extract_json_array(text: str) -> List[Any]:
    """Extract and parse a JSON array from Gemini's response."""

    if not isinstance(text, str) or not text.strip():
        raise GeminiServiceError(
            "Gemini returned an empty response."
        )

    cleaned = _strip_code_fences(text)

    # First: try the complete response.
    try:
        result = json.loads(cleaned)

        if isinstance(result, list):
            return result

    except json.JSONDecodeError:
        pass

    # Second: search for the first balanced JSON array.
    start = cleaned.find("[")

    if start == -1:
        raise GeminiServiceError(
            "Gemini returned a response that is not valid JSON."
        )

    end = _find_balanced_span(cleaned, start, "[", "]")

    if end == -1:
        raise GeminiServiceError(
            "Gemini returned a response that is not valid JSON."
        )

    json_text = cleaned[start:end + 1]

    try:
        result = json.loads(json_text)

    except json.JSONDecodeError as exc:
        raise GeminiServiceError(
            "Gemini returned malformed JSON."
        ) from exc

    if not isinstance(result, list):
        raise GeminiServiceError(
            "Gemini response must be a JSON array."
        )

    return result


def _validate_batch_items(
    items: List[Any],
    expected_ids: List[str],
) -> Dict[str, Dict[str, str]]:
    """
    Validate each object Gemini returned and index the results by
    violation id. Items whose id doesn't match anything we asked
    about are dropped defensively rather than failing the whole
    batch.
    """

    if not isinstance(items, list):
        raise GeminiServiceError(
            "Gemini response must be a JSON array."
        )

    expected = set(expected_ids)

    required_fields = [
        "id",
        "plainEnglish",
        "whyItMatters",
        "whoIsAffected",
        "suggestedFix",
        "priority",
    ]

    results: Dict[str, Dict[str, str]] = {}

    for item in items:

        if not isinstance(item, dict):
            raise GeminiServiceError(
                "Gemini response must be an array of JSON objects."
            )

        for field in required_fields:

            if field not in item:
                raise GeminiServiceError(
                    f"Gemini response is missing required field: {field}"
                )

            if not isinstance(item[field], str):
                raise GeminiServiceError(
                    f"Gemini field '{field}' must be a string."
                )

            if not item[field].strip():
                raise GeminiServiceError(
                    f"Gemini field '{field}' must not be empty."
                )

        violation_id = item["id"].strip()
        priority = item["priority"].strip()

        if priority not in {
            "High",
            "Medium",
            "Low",
        }:
            raise GeminiServiceError(
                "Gemini returned an invalid priority."
            )

        if violation_id not in expected:
            # Gemini returned an id we never asked about — ignore it
            # rather than failing the whole batch over it.
            continue

        results[violation_id] = {
            "plainEnglish": item["plainEnglish"].strip(),
            "whyItMatters": item["whyItMatters"].strip(),
            "whoIsAffected": item["whoIsAffected"].strip(),
            "suggestedFix": item["suggestedFix"].strip(),
            "priority": priority,
        }

    return results


def _call_gemini_sync(
    prompt: str,
) -> Dict[str, Any]:
    """
    Perform the Gemini REST API request.

    Uses httpx (already a project dependency, and already used
    successfully by app/services/pagespeed.py against Google APIs
    from this same environment). Switched from urllib.request,
    which was observed to hang until timeout on some networks that
    perform TLS interception/renegotiation (corporate proxies,
    antivirus HTTPS scanning, etc.) — httpx's TLS stack handles
    that renegotiation correctly where urllib/ssl did not.
    """

    if not GEMINI_API_KEY:
        raise GeminiServiceError(
            "Gemini API key is not configured."
        )

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt,
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.1,
            "responseMimeType": "application/json",
        },
    }

    try:

        response = httpx.post(
            GEMINI_API_URL,
            json=payload,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "x-goog-api-key": GEMINI_API_KEY,
            },
            timeout=GEMINI_TIMEOUT_SECONDS,
        )

    except httpx.TimeoutException as exc:

        raise GeminiServiceError(
            "Gemini API request timed out."
        ) from exc

    except httpx.RequestError as exc:

        raise GeminiServiceError(
            "Unable to reach Gemini API."
        ) from exc

    if response.status_code >= 400:

        if response.status_code == 400:
            raise GeminiServiceError(
                "Gemini rejected the request."
            )

        if response.status_code in (401, 403):
            raise GeminiServiceError(
                "Gemini API authentication failed. "
                "Check the API key."
            )

        if response.status_code == 404:
            raise GeminiServiceError(
                "Gemini model or API endpoint was not found. "
                f"Configured model: {GEMINI_MODEL}"
            )

        if response.status_code == 429:
            raise GeminiServiceError(
                "Gemini API rate limit exceeded."
            )

        raise GeminiServiceError(
            f"Gemini API returned HTTP {response.status_code}."
        )

    try:

        response_json = response.json()

    except json.JSONDecodeError as exc:

        raise GeminiServiceError(
            "Gemini returned invalid JSON."
        ) from exc

    if not isinstance(response_json, dict):

        raise GeminiServiceError(
            "Gemini returned an unexpected response."
        )

    return response_json


def _extract_gemini_text(
    response: Dict[str, Any],
) -> str:
    """Extract generated text from Gemini's response."""

    try:

        candidates = response["candidates"]

        if (
            not isinstance(candidates, list)
            or not candidates
        ):
            raise GeminiServiceError(
                "Gemini returned no candidates."
            )

        content = candidates[0]["content"]

        parts = content["parts"]

        if (
            not isinstance(parts, list)
            or not parts
        ):
            raise GeminiServiceError(
                "Gemini returned no response parts."
            )

        text_parts = []

        for part in parts:

            if (
                isinstance(part, dict)
                and isinstance(
                    part.get("text"),
                    str,
                )
            ):
                text_parts.append(
                    part["text"]
                )

        if not text_parts:

            raise GeminiServiceError(
                "Gemini returned no generated text."
            )

        return "".join(text_parts)

    except GeminiServiceError:
        raise

    except (
        KeyError,
        TypeError,
        IndexError,
    ) as exc:

        raise GeminiServiceError(
            "Unexpected Gemini response format."
        ) from exc


async def enrich_violations(
    violations: List[Dict[str, Any]],
) -> Dict[str, Dict[str, str]]:
    """
    Enrich a batch of accessibility violations using Gemini in a
    single request.

    Returns a dict mapping violation id -> enrichment fields. The
    caller (app/routers/enrich.py) is responsible for looking up
    each requested violation's id in the result and deciding how to
    handle any that are missing.

    The blocking HTTP request is executed in a worker thread so it
    does not block FastAPI's event loop.
    """

    if not violations:
        return {}

    expected_ids = [
        violation.get("id", "")
        for violation in violations
    ]

    prompt = _build_batch_prompt(
        violations
    )

    response = await asyncio.to_thread(
        _call_gemini_sync,
        prompt,
    )

    generated_text = _extract_gemini_text(
        response
    )

    items = _extract_json_array(
        generated_text
    )

    return _validate_batch_items(
        items,
        expected_ids,
    )