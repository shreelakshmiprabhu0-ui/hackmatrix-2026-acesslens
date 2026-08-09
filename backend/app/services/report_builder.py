from html import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle,
)
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib.units import mm


def _safe_text(value, default="N/A"):
    """
    Convert a value into safe text for ReportLab.
    """
    if value is None:
        return default

    text = str(value).strip()

    if not text:
        return default

    return escape(text)


def _format_wcag(criteria):
    """
    Format WCAG criteria list.
    """

    if not criteria:
        return "N/A"

    if isinstance(criteria, list):
        return ", ".join(
            str(item)
            for item in criteria
            if item
        ) or "N/A"

    return str(criteria)


def _get_severity(violation):
    """
    Get severity from the normalized scan response.
    """

    severity = violation.get("severity")

    if severity:
        return str(severity).strip()

    impact = violation.get("impact")

    if impact:
        impact = str(impact).strip().lower()

        if impact == "critical":
            return "Critical"

        if impact == "serious":
            return "Critical"

        if impact == "moderate":
            return "Moderate"

        if impact == "minor":
            return "Minor"

    return "Moderate"


def _get_priority(severity):
    """
    Convert severity to remediation priority.
    """

    normalized = severity.lower()

    if normalized == "critical":
        return "High"

    if normalized == "moderate":
        return "Medium"

    if normalized == "minor":
        return "Low"

    return "Medium"


def _get_enrichment(
    violation,
    enrichment_lookup,
):
    """
    Get optional AI enrichment for a violation.
    """

    violation_id = violation.get("id", "")

    enrichment = enrichment_lookup.get(
        violation_id,
        {},
    )

    if not isinstance(enrichment, dict):
        return {}

    return enrichment


def build_report(
    scan_data,
    enrichment_data,
    output_path,
):
    """
    Generate an AccessLens accessibility report as a PDF.

    Args:
        scan_data:
            Scan results returned by Module 3.

        enrichment_data:
            Optional AI-enriched results from Module 4.

        output_path:
            Path where the PDF should be saved.
    """

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=22,
        leading=26,
        spaceAfter=14,
    )

    heading_style = ParagraphStyle(
        "ReportHeading",
        parent=styles["Heading2"],
        fontSize=15,
        leading=18,
        spaceBefore=12,
        spaceAfter=8,
    )

    issue_heading_style = ParagraphStyle(
        "IssueHeading",
        parent=styles["Heading3"],
        fontSize=12,
        leading=15,
        spaceBefore=10,
        spaceAfter=5,
    )

    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["BodyText"],
        fontSize=9.5,
        leading=13,
        spaceAfter=5,
    )

    small_style = ParagraphStyle(
        "Small",
        parent=styles["BodyText"],
        fontSize=8,
        leading=10,
        spaceAfter=3,
    )

    story = []

    # ========================================================
    # TITLE
    # ========================================================

    story.append(
        Paragraph(
            "AccessLens Accessibility Report",
            title_style,
        )
    )

    story.append(
        Spacer(1, 5)
    )

    url = scan_data.get(
        "url",
        "Unknown URL",
    )

    score = scan_data.get(
        "overallScore",
        "N/A",
    )

    story.append(
        Paragraph(
            f"<b>Website:</b> {_safe_text(url)}",
            body_style,
        )
    )

    story.append(
        Paragraph(
            f"<b>Accessibility Score:</b> "
            f"{_safe_text(score)} / 100",
            body_style,
        )
    )

    story.append(
        Spacer(1, 10)
    )

    # ========================================================
    # SUMMARY
    # ========================================================

    story.append(
        Paragraph(
            "Summary",
            heading_style,
        )
    )

    category_counts = scan_data.get(
        "categoryCounts",
        {},
    )

    if not isinstance(category_counts, dict):
        category_counts = {}

    critical = category_counts.get(
        "critical",
        0,
    )

    moderate = category_counts.get(
        "moderate",
        0,
    )

    minor = category_counts.get(
        "minor",
        0,
    )

    violations = scan_data.get(
        "violations",
        [],
    )

    if not isinstance(violations, list):
        violations = []

    # --------------------------------------------------------
    # Include serious count if the incoming data has it.
    # This is useful when Module 3/4 sends axe-style data.
    # --------------------------------------------------------

    serious = category_counts.get(
        "serious",
        0,
    )

    summary_data = [
        [
            "Category",
            "Count",
        ],
        [
            "Critical",
            str(critical),
        ],
        [
            "Serious",
            str(serious),
        ],
        [
            "Moderate",
            str(moderate),
        ],
        [
            "Minor",
            str(minor),
        ],
        [
            "Total Issues",
            str(len(violations)),
        ],
    ]

    summary_table = Table(
        summary_data,
        colWidths=[
            90 * mm,
            50 * mm,
        ],
    )

    summary_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#333333"),
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white,
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey,
                ),
                (
                    "ALIGN",
                    (1, 1),
                    (1, -1),
                    "CENTER",
                ),
                (
                    "PADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
            ]
        )
    )

    story.append(summary_table)

    story.append(
        Spacer(1, 15)
    )

    # ========================================================
    # ACCESSIBILITY ISSUES
    # ========================================================

    story.append(
        Paragraph(
            "Accessibility Issues",
            heading_style,
        )
    )

    if not violations:

        story.append(
            Paragraph(
                "No accessibility violations were detected.",
                body_style,
            )
        )

    # --------------------------------------------------------
    # ENRICHMENT LOOKUP
    # --------------------------------------------------------

    enrichment_lookup = {}

    if isinstance(
        enrichment_data,
        dict,
    ):

        enriched_violations = enrichment_data.get(
            "enrichedViolations",
            [],
        )

        if isinstance(
            enriched_violations,
            list,
        ):

            enrichment_lookup = {
                item.get("id"): item
                for item in enriched_violations
                if isinstance(item, dict)
                and item.get("id")
            }

    # ========================================================
    # EACH VIOLATION
    # ========================================================

    for index, violation in enumerate(
        violations,
        start=1,
    ):

        if not isinstance(
            violation,
            dict,
        ):
            continue

        violation_id = violation.get(
            "id",
            "",
        )

        enrichment = _get_enrichment(
            violation,
            enrichment_lookup,
        )

        title = (
            violation.get("title")
            or violation_id
            or "Accessibility Issue"
        )

        severity = _get_severity(
            violation
        )

        priority = enrichment.get(
            "priority"
        )

        if not priority:
            priority = _get_priority(
                severity
            )

        wcag = _format_wcag(
            violation.get(
                "wcagCriteria",
                [],
            )
        )

        description = (
            violation.get(
                "description"
            )
            or "Accessibility issue detected."
        )

        plain_english = (
            enrichment.get(
                "plainEnglish"
            )
            or description
        )

        why_it_matters = enrichment.get(
            "whyItMatters",
            "This issue may make the website harder to use for people with disabilities.",
        )

        who_is_affected = enrichment.get(
            "whoIsAffected",
            "Users who rely on assistive technologies or accessibility features may be affected.",
        )

        suggested_fix = enrichment.get(
            "suggestedFix"
        )

        if not suggested_fix:
            suggested_fix = (
                "Review the affected element and "
                "correct it according to the accessibility rule."
            )

        affected_nodes = violation.get(
            "affectedNodes",
            0,
        )

        # ----------------------------------------------------
        # ISSUE TITLE
        # ----------------------------------------------------

        story.append(
            Paragraph(
                f"{index}. {_safe_text(title)}",
                issue_heading_style,
            )
        )

        # ----------------------------------------------------
        # METADATA
        # ----------------------------------------------------

        metadata = (
            f"<b>Rule ID:</b> "
            f"{_safe_text(violation_id)}<br/>"
            f"<b>Severity:</b> "
            f"{_safe_text(severity)}<br/>"
            f"<b>WCAG:</b> "
            f"{_safe_text(wcag)}<br/>"
            f"<b>Priority:</b> "
            f"{_safe_text(priority)}<br/>"
            f"<b>Affected Elements:</b> "
            f"{_safe_text(affected_nodes)}"
        )

        story.append(
            Paragraph(
                metadata,
                body_style,
            )
        )

        # ----------------------------------------------------
        # EXPLANATION
        # ----------------------------------------------------

        story.append(
            Paragraph(
                f"<b>Explanation:</b> "
                f"{_safe_text(plain_english)}",
                body_style,
            )
        )

        # ----------------------------------------------------
        # WHY IT MATTERS
        # ----------------------------------------------------

        story.append(
            Paragraph(
                f"<b>Why it matters:</b> "
                f"{_safe_text(why_it_matters)}",
                body_style,
            )
        )

        # ----------------------------------------------------
        # WHO IS AFFECTED
        # ----------------------------------------------------

        story.append(
            Paragraph(
                f"<b>Who is affected:</b> "
                f"{_safe_text(who_is_affected)}",
                body_style,
            )
        )

        # ----------------------------------------------------
        # SUGGESTED FIX
        # ----------------------------------------------------

        story.append(
            Paragraph(
                f"<b>Suggested fix:</b> "
                f"{_safe_text(suggested_fix)}",
                body_style,
            )
        )

        # ----------------------------------------------------
        # OPTIONAL NODE DETAILS
        # ----------------------------------------------------

        nodes = violation.get(
            "nodes",
            [],
        )

        if isinstance(nodes, list) and nodes:

            story.append(
                Paragraph(
                    "<b>Affected Elements:</b>",
                    body_style,
                )
            )

            for node in nodes:

                if not isinstance(
                    node,
                    dict,
                ):
                    continue

                html = node.get(
                    "html",
                    "",
                )

                target = node.get(
                    "target",
                    "",
                )

                failure_summary = node.get(
                    "failureSummary",
                    "",
                )

                if isinstance(
                    target,
                    list,
                ):
                    target = ", ".join(
                        str(x)
                        for x in target
                    )

                node_text = (
                    f"<b>HTML:</b> "
                    f"{_safe_text(html)}<br/>"
                    f"<b>Selector:</b> "
                    f"{_safe_text(target)}<br/>"
                    f"<b>Detection:</b> "
                    f"{_safe_text(failure_summary)}"
                )

                story.append(
                    Paragraph(
                        node_text,
                        small_style,
                    )
                )

        # ----------------------------------------------------
        # REFERENCE
        # ----------------------------------------------------

        help_url = violation.get(
            "helpUrl"
        )

        if help_url:

            story.append(
                Paragraph(
                    f"<b>Reference:</b> "
                    f"{_safe_text(help_url)}",
                    small_style,
                )
            )

        story.append(
            Spacer(1, 8)
        )

    # ========================================================
    # BUILD PDF
    # ========================================================

    doc.build(story)

    return output_path