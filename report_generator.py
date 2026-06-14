from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def create_report(filename, skills, careers, scores, gaps, roadmaps):

    pdf_path = "career_report.pdf"
    doc = SimpleDocTemplate(pdf_path)

    styles = getSampleStyleSheet()
    title = styles["Title"]
    heading = styles["Heading2"]
    text = styles["BodyText"]

    content = []

    # ---------------- TITLE ----------------
    content.append(Paragraph("CareerCompass AI Report", title))
    content.append(Spacer(1, 12))

    # ---------------- FILE ----------------
    content.append(Paragraph(f"Resume: {filename}", text))
    content.append(Spacer(1, 10))

    # ---------------- SKILLS ----------------
    content.append(Paragraph("Detected Skills", heading))

    for s in skills:
        content.append(Paragraph(f"• {s}", text))

    content.append(Spacer(1, 10))

    # ---------------- CAREERS ----------------
    content.append(Paragraph("Recommended Careers", heading))

    for c in careers:
        content.append(Paragraph(f"• {c}", text))

    content.append(Spacer(1, 10))

    # ---------------- SCORES ----------------
    content.append(Paragraph("Career Readiness Scores", heading))

    for career, score in scores.items():
        content.append(Paragraph(f"{career} → {score}%", text))

    content.append(Spacer(1, 10))

    # ---------------- SKILL GAPS (FIXED PART) ----------------
    content.append(Paragraph("Skill Gap Analysis", heading))

    for career, gap_list in gaps.items():
        content.append(Paragraph(f"<b>{career}</b>", text))

        if gap_list:
            for g in gap_list:
                content.append(Paragraph(f"• Missing: {g}", text))
        else:
            content.append(Paragraph("No missing skills", text))

        content.append(Spacer(1, 8))

    # ---------------- ROADMAP (FIXED PART) ----------------
    content.append(Paragraph("Learning Roadmap", heading))

    for career, steps in roadmaps.items():
        content.append(Paragraph(f"<b>{career}</b>", text))

        for i, step in enumerate(steps, 1):
            content.append(Paragraph(f"{i}. {step}", text))

        content.append(Spacer(1, 8))

    # ---------------- BUILD PDF ----------------
    doc.build(content)

    return pdf_path