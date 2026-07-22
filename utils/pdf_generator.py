from io import BytesIO
from xml.sax.saxutils import escape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm


def generate_prototype_pdf(spec, output_path=None):
    styles = getSampleStyleSheet()
    target = output_path or BytesIO()
    doc = SimpleDocTemplate(target, title="AI Prototype Specification", author="AI Governance Platform")
    story = [Paragraph("AI Prototype Specification", styles["Title"]), Spacer(1, 20)]
    sections = [
        ("Architecture Design", "architecture_design"), ("Technical Details", "technical_details"),
        ("Implementation Plan", "implementation_plan"), ("Data & Features", "data_features"),
        ("Models Used", "models_used"), ("Model Validation", "model_validation"),
        ("Results Analysis", "results_analysis"), ("Infrastructure", "infrastructure"),
        ("Security", "security"), ("Deployment", "deployment"),
        ("Maintenance", "maintenance"), ("Future Scope", "future_scope"),
    ]
    for title, key in sections:
        story.extend([Paragraph(escape(title), styles["Heading2"]),
                      Paragraph(escape(str(spec.get(key, "-") or "-")), styles["BodyText"]),
                      Spacer(1, 12)])
    doc.build(story)
    return target.getvalue() if output_path is None else output_path


def generate_execution_report(project, gate, output_path=None):
    """Create a concise, client-ready PDF of the delivery gate decision."""
    styles = getSampleStyleSheet()
    target = output_path or BytesIO()
    doc = SimpleDocTemplate(
        target,
        pagesize=A4,
        rightMargin=16 * mm,
        leftMargin=16 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title="AI Delivery Gate Review",
        author="AI Maturity Governance",
    )
    story = [
        Paragraph("AI Delivery Gate Review", styles["Title"]),
        Paragraph(escape(str(project.get("id", ""))), styles["Heading3"]),
        Paragraph(escape(str(project.get("problem_statement", ""))), styles["BodyText"]),
        Spacer(1, 12),
        Paragraph("Execution Readiness Summary", styles["Heading2"]),
    ]
    readiness = gate.get("readiness", [])
    table_data = [["Readiness Area", "Status", "Notes"]]
    for row in readiness:
        table_data.append([
            Paragraph(escape(str(row.get("area", ""))), styles["BodyText"]),
            Paragraph(escape(str(row.get("status", ""))), styles["BodyText"]),
            Paragraph(escape(str(row.get("notes", ""))), styles["BodyText"]),
        ])
    table = Table(table_data, colWidths=[46 * mm, 43 * mm, 88 * mm], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3563")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), .35, colors.HexColor("#D9E2F0")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F8FD")]),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.extend([table, Spacer(1, 14), Paragraph("Open Blockers", styles["Heading2"]),
                  Paragraph(escape(str(gate.get("blockers", "") or "None recorded")), styles["BodyText"]),
                  Spacer(1, 12), Paragraph("Stakeholder Approvals", styles["Heading2"])] )
    approvals = gate.get("stakeholders", [])
    approval_data = [["Stakeholder", "Approved", "Date"]]
    for row in approvals:
        approval_data.append([str(row.get("role", "")), "Yes" if row.get("approved") else "No", str(row.get("date", ""))])
    approval_table = Table(approval_data, colWidths=[75 * mm, 35 * mm, 55 * mm], repeatRows=1)
    approval_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3563")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), .35, colors.HexColor("#D9E2F0")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F8FD")]),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.extend([approval_table, Spacer(1, 14),
                  Paragraph("Recorded By", styles["Heading2"]),
                  Paragraph(escape(str(gate.get("updated_by", ""))), styles["BodyText"])])
    doc.build(story)
    return target.getvalue() if output_path is None else output_path
