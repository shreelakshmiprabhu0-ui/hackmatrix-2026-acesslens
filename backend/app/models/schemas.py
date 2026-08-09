"""
Shared API contract for AccessLens.

These models are the single source of truth for the shape of data crossing
the frontend <-> backend boundary. They must match docs/API_CONTRACT.md
exactly. This file is frozen after Hour 1 of the hackathon — changes need
a heads-up to the team, not a silent edit.
"""

from enum import Enum
from typing import List

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Shared enums
# ---------------------------------------------------------------------------

class Impact(str, Enum):
    """Raw Lighthouse impact rating for a violation."""

    minor = "minor"
    moderate = "moderate"
    serious = "serious"
    critical = "critical"


class Severity(str, Enum):
    """Display severity bucket, mapped from Lighthouse's impact field."""

    critical = "Critical"
    moderate = "Moderate"
    minor = "Minor"


class Priority(str, Enum):
    """AI-assigned priority for fixing a violation."""

    high = "High"
    medium = "Medium"
    low = "Low"


# ---------------------------------------------------------------------------
# POST /api/scan
# ---------------------------------------------------------------------------

class ScanRequest(BaseModel):
    url: str = Field(..., description="The URL to scan for accessibility issues.")


class CategoryCounts(BaseModel):
    critical: int = 0
    moderate: int = 0
    minor: int = 0


class Violation(BaseModel):
    id: str = Field(..., description="Lighthouse/axe rule id, e.g. 'image-alt'.")
    title: str
    description: str
    impact: Impact
    wcagCriteria: List[str] = Field(default_factory=list)
    affectedNodes: int = Field(..., ge=0)
    severity: Severity


class ScanResponse(BaseModel):
    url: str
    overallScore: int = Field(..., ge=0, le=100)
    categoryCounts: CategoryCounts
    violations: List[Violation] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# POST /api/enrich
# ---------------------------------------------------------------------------

class ViolationForEnrichment(BaseModel):
    """Subset of Violation fields sent to /api/enrich — no severity/affectedNodes needed."""

    id: str
    title: str
    description: str
    impact: Impact
    wcagCriteria: List[str] = Field(default_factory=list)


class EnrichmentRequest(BaseModel):
    violations: List[ViolationForEnrichment]


class EnrichedViolation(BaseModel):
    id: str = Field(..., description="Matches the corresponding Violation.id from /api/scan.")
    plainEnglish: str
    whyItMatters: str
    whoIsAffected: str
    suggestedFix: str
    priority: Priority


class EnrichmentResponse(BaseModel):
    enrichedViolations: List[EnrichedViolation]


# ---------------------------------------------------------------------------
# GET /health
# ---------------------------------------------------------------------------

class HealthResponse(BaseModel):
    status: str = "ok"
