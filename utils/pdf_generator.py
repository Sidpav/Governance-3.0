from io import BytesIO
from xml.sax.saxutils import escape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet


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
