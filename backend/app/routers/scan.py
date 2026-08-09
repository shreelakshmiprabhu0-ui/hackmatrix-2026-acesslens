from fastapi import APIRouter

from app.models.schemas import ScanRequest, ScanResponse
from app.services.pagespeed import scan_url_with_pagespeed


router = APIRouter(tags=["scan"])


@router.post("/scan", response_model=ScanResponse)
async def scan_website(request: ScanRequest) -> ScanResponse:
    """
    Scan a website for accessibility issues using
    Google PageSpeed Insights.
    """
    return await scan_url_with_pagespeed(request.url)