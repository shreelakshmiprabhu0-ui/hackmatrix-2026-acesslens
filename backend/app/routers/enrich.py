"""
Module 4 enrichment API.

POST /api/enrich

Receives accessibility violations from Module 3 and uses Gemini
to generate plain-English explanations and suggested fixes.
"""

from typing import List

from fastapi import APIRouter, HTTPException, status

from app.models.schemas import (
    EnrichedViolation,
    EnrichmentRequest,
    EnrichmentResponse,
)
from app.services import gemini


router = APIRouter(
    tags=["enrich"],
)


@router.post(
    "/enrich",
    response_model=EnrichmentResponse,
)
async def enrich_violations(
    request: EnrichmentRequest,
) -> EnrichmentResponse:
    """
    Enrich accessibility violations using Gemini.

    All violations from the request are sent to Gemini in a single
    batched call (see app/services/gemini.py) rather than one call
    per violation, to avoid multiplying real API/rate-limit usage by
    the violation count.

    Each input violation is converted into:
    - plainEnglish
    - whyItMatters
    - whoIsAffected
    - suggestedFix
    - priority
    """

    if not request.violations:
        return EnrichmentResponse(enrichedViolations=[])

    try:
        results_by_id = await gemini.enrich_violations(
            [violation.model_dump() for violation in request.violations]
        )

    except gemini.GeminiServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to generate accessibility enrichment.",
        ) from exc

    enriched: List[EnrichedViolation] = []

    for violation in request.violations:
        ai_result = results_by_id.get(violation.id)

        if ai_result is None:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=(
                    "Gemini did not return an enrichment result for "
                    f"violation id: {violation.id}"
                ),
            )

        try:
            enriched_violation = EnrichedViolation(
                id=violation.id,
                plainEnglish=ai_result["plainEnglish"],
                whyItMatters=ai_result["whyItMatters"],
                whoIsAffected=ai_result["whoIsAffected"],
                suggestedFix=ai_result["suggestedFix"],
                priority=ai_result["priority"],
            )

        except (KeyError, ValueError, TypeError) as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Gemini returned an invalid enrichment result.",
            ) from exc

        enriched.append(enriched_violation)

    return EnrichmentResponse(
        enrichedViolations=enriched
    )