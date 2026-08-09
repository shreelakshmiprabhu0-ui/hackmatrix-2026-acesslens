"""
Gemini AI service for AccessLens Module 4.

This service takes a single accessibility violation and asks Gemini
to generate:

- plain-English explanation
- why it matters
- who is affected
- suggested fix
- priority

The Gemini API key is read from app.config.
The API key must never be hardcoded in this file.
"""

import asyncio
import json
import re
import urllib.error
import urllib.request
from typing import Any, Dict

from app.config import GEMINI_API_KEY, GEMINI_MODEL


GEMINI_API_URL = (
    "https://generativelanguage.googleapis.com/"
    f"v1beta/models/{GEMINI_MODEL}:generateContent"
)

GEMINI_TIMEOUT_SECONDS = 30


class GeminiServiceError(Exception):
    """Raised when Gemini cannot generate a valid enrichment result."""


def _build_prompt(violation: Dict[str, Any]) -> str:
    """Build the prompt sent to Gemini."""

    violation_id = violation.get("id", "")
    title = violation.get("title", "")
    description = violation.get("description", "")
    impact = violation.get("impact", "")
    wcag_criteria = violation.get("wcagCriteria", [])

    return f"""
You are an expert web accessibility analyst.

Analyze this accessibility violation.

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

Return ONLY a valid JSON object.

The JSON object must contain exactly these fields:

{{
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
Do not add text before or after the JSON.
Do not invent WCAG criteria.
""".strip()


def _extract_json(text: str) -> Dict[str, Any]:
    """Extract and parse JSON from Gemini's response."""

    if not isinstance(text, str) or not text.strip():
        raise GeminiServiceError(
            "Gemini returned an empty response."
        )

    cleaned = text.strip()

    # Remove Markdown code fences if Gemini returns them.
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

    cleaned = cleaned.strip()

    # First: try the complete response.
    try:
        result = json.loads(cleaned)

        if isinstance(result, dict):
            return result

    except json.JSONDecodeError:
        pass

    # Second: search for the first JSON object.
    start = cleaned.find("{")

    if start == -1:
        raise GeminiServiceError(
            "Gemini returned a response that is not valid JSON."
        )

    # Find a balanced JSON object rather than using rfind("}").
    depth = 0
    in_string = False
    escape = False
    end = -1

    for index in range(start, len(cleaned)):
        char = cleaned[index]

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

        if char == "{":
            depth += 1

        elif char == "}":
            depth -= 1

            if depth == 0:
                end = index
                break

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

    if not isinstance(result, dict):
        raise GeminiServiceError(
            "Gemini response must be a JSON object."
        )

    return result


def _validate_result(
    result: Dict[str, Any],
) -> Dict[str, str]:
    """Validate Gemini's enrichment response."""

    required_fields = [
        "plainEnglish",
        "whyItMatters",
        "whoIsAffected",
        "suggestedFix",
        "priority",
    ]

    for field in required_fields:

        if field not in result:
            raise GeminiServiceError(
                f"Gemini response is missing required field: {field}"
            )

        if not isinstance(result[field], str):
            raise GeminiServiceError(
                f"Gemini field '{field}' must be a string."
            )

        if not result[field].strip():
            raise GeminiServiceError(
                f"Gemini field '{field}' must not be empty."
            )

    priority = result["priority"].strip()

    if priority not in {
        "High",
        "Medium",
        "Low",
    }:
        raise GeminiServiceError(
            "Gemini returned an invalid priority."
        )

    return {
        "plainEnglish": result["plainEnglish"].strip(),
        "whyItMatters": result["whyItMatters"].strip(),
        "whoIsAffected": result["whoIsAffected"].strip(),
        "suggestedFix": result["suggestedFix"].strip(),
        "priority": priority,
    }


def _call_gemini_sync(
    prompt: str,
) -> Dict[str, Any]:
    """
    Perform the Gemini REST API request.

    Uses Python's standard library, so no additional dependency
    is required.
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

    request = urllib.request.Request(
        GEMINI_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "x-goog-api-key": GEMINI_API_KEY,
        },
        method="POST",
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=GEMINI_TIMEOUT_SECONDS,
        ) as response:

            response_body = response.read().decode(
                "utf-8"
            )

    except urllib.error.HTTPError as exc:

        try:
            error_body = exc.read().decode(
                "utf-8"
            )
        except Exception:
            error_body = ""

        if exc.code == 400:
            raise GeminiServiceError(
                "Gemini rejected the request."
            ) from exc

        if exc.code in (401, 403):
            raise GeminiServiceError(
                "Gemini API authentication failed. "
                "Check the API key."
            ) from exc

        if exc.code == 404:
            raise GeminiServiceError(
                "Gemini model or API endpoint was not found. "
                f"Configured model: {GEMINI_MODEL}"
            ) from exc

        if exc.code == 429:
            raise GeminiServiceError(
                "Gemini API rate limit exceeded."
            ) from exc

        raise GeminiServiceError(
            f"Gemini API returned HTTP {exc.code}."
        ) from exc

    except urllib.error.URLError as exc:

        raise GeminiServiceError(
            "Unable to reach Gemini API."
        ) from exc

    except TimeoutError as exc:

        raise GeminiServiceError(
            "Gemini API request timed out."
        ) from exc

    except OSError as exc:

        raise GeminiServiceError(
            "Unable to connect to Gemini API."
        ) from exc

    try:

        response_json = json.loads(
            response_body
        )

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


async def enrich_violation(
    violation: Dict[str, Any],
) -> Dict[str, str]:
    """
    Enrich one accessibility violation using Gemini.

    The blocking HTTP request is executed in a worker thread
    so it does not block FastAPI's event loop.
    """

    prompt = _build_prompt(
        violation
    )

    response = await asyncio.to_thread(
        _call_gemini_sync,
        prompt,
    )

    generated_text = _extract_gemini_text(
        response
    )

    result = _extract_json(
        generated_text
    )

    return _validate_result(
        result
    )