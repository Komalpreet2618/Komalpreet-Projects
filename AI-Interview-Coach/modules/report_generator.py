from io import BytesIO
from typing import Dict, List

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


def generate_pdf_report(payload: Dict, suggestions: List[str]) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, title="AI Interview Coach Report")
    styles = getSampleStyleSheet()
    body = []

    body.append(Paragraph("AI Interview Coach Report", styles["Title"]))
    body.append(Spacer(1, 12))

    body.append(Paragraph(f"Role: {payload.get('role', '-')}", styles["Normal"]))
    body.append(Paragraph(f"Language: {payload.get('language', '-')}", styles["Normal"]))
    body.append(Paragraph(f"Timestamp: {payload.get('timestamp', '-')}", styles["Normal"]))
    body.append(Spacer(1, 10))

    body.append(Paragraph(f"Question: {payload.get('question', '-')}", styles["Heading3"]))
    body.append(Paragraph(f"Transcript: {payload.get('transcript', '-')}", styles["Normal"]))
    body.append(Spacer(1, 10))

    scores = payload.get("scores", {})
    body.append(Paragraph("Scores", styles["Heading3"]))
    for key in [
        "relevance_score",
        "voice_score",
        "emotion_score",
        "eye_contact_score",
        "posture_score",
        "speech_clarity_score",
        "final_score",
    ]:
        body.append(Paragraph(f"{key.replace('_', ' ').title()}: {scores.get(key, 0)}", styles["Normal"]))

    body.append(Spacer(1, 10))
    body.append(Paragraph("Suggestions", styles["Heading3"]))
    for tip in suggestions:
        body.append(Paragraph(f"- {tip}", styles["Normal"]))

    if payload.get("followup_question"):
        body.append(Spacer(1, 10))
        body.append(Paragraph("AI Follow-up Question", styles["Heading3"]))
        body.append(Paragraph(payload["followup_question"], styles["Normal"]))

    doc.build(body)
    pdf_data = buffer.getvalue()
    buffer.close()
    return pdf_data
