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

    Each input violation is converted into:
    - plainEnglish
    - whyItMatters
    - whoIsAffected
    - suggestedFix
    - priority
    """

    enriched: List[EnrichedViolation] = []

    for violation in request.violations:
        try:
            ai_result = await gemini.enrich_violation(
                violation.model_dump()
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