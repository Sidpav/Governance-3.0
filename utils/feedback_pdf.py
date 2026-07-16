from io import BytesIO
from xml.sax.saxutils import escape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

styles = getSampleStyleSheet()


def _text(value):
    if isinstance(value, list):
        return "<br/>".join("• " + escape(str(item)) for item in value)
    return escape(str(value or ""))


def generate_stakeholder_summary_pdf(stakeholder, summary, output_path=None):
    target = output_path or BytesIO()
    doc = SimpleDocTemplate(target, title=f"{stakeholder} Summary", author="AI Governance Platform")
    story = [Paragraph(f"<b>{escape(str(stakeholder))} Summary</b>", styles["Heading1"]), Spacer(1, 12)]
    fields = [("Product View","product_view"),("Data View","data_view"),
              ("Compliance View","compliance_view"),("Business View","business_view"),
              ("Infrastructure View","infrastructure_view"),("Overall Decision","overall_decision"),
              ("MVP Recommendation","mvp_recommendation"),("Blockers","blockers"),
              ("Confidence","confidence")]
    for title, key in fields:
        story.extend([Paragraph(f"<b>{title}</b>", styles["Heading2"]),
                      Paragraph(_text(summary.get(key, "")), styles["BodyText"]), Spacer(1, 8)])
    doc.build(story)
    return target.getvalue() if output_path is None else output_path


def generate_committee_summary_pdf(summary, output_path=None):
    target = output_path or BytesIO()
    doc = SimpleDocTemplate(target, title="Governance Committee Summary", author="AI Governance Platform")
    story = [Paragraph("<b>Governance Committee Summary</b>", styles["Heading1"]), Spacer(1, 12),
             Paragraph(_text(summary.get("feedback_summary", "")), styles["BodyText"]), Spacer(1, 12)]
    for title, key in [("Agreement Areas","agreement_areas"),("Disagreement Areas","disagreement_areas"),
                       ("Feature Changes Required","feature_changes_required"),("Risks Raised","risks_raised")]:
        story.append(Paragraph(f"<b>{title}</b>", styles["Heading2"]))
        story.append(Paragraph(_text(summary.get(key, [])), styles["BodyText"]))
        story.append(Spacer(1, 8))
    story.extend([Paragraph("<b>Recommended MVP Scope</b>", styles["Heading2"]),
                  Paragraph(_text(summary.get("recommended_mvp_scope", "")), styles["BodyText"])])
    doc.build(story)
    return target.getvalue() if output_path is None else output_path
