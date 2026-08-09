from fastapi import APIRouter
from fastapi.responses import FileResponse

from app.services.report_builder import build_report


router = APIRouter()


@router.post(
    "/report/export",
    response_class=FileResponse,
    responses={
        200: {
            "content": {
                "application/pdf": {}
            },
            "description": "Accessibility report PDF",
        }
    },
)
def export_report(
    scan_data: dict,
    enrichment_data: dict,
):

    output_file = "accesslens_report.pdf"

    build_report(
        scan_data,
        enrichment_data,
        output_file,
    )

    return FileResponse(
        output_file,
        media_type="application/pdf",
        filename="accesslens_report.pdf",
    )