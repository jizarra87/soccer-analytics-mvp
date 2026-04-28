from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def generate_player_report(player_name, position, stats, output_path):
    doc = SimpleDocTemplate(output_path)
    styles = getSampleStyleSheet()

    content = []

    # Title
    content.append(Paragraph(f"<b>Player Report: {player_name}</b>", styles["Title"]))
    content.append(Spacer(1, 12))

    # Basic info
    content.append(Paragraph(f"Position: {position}", styles["Normal"]))
    content.append(Spacer(1, 12))

    # Stats
    content.append(Paragraph("<b>Match Stats</b>", styles["Heading2"]))
    content.append(Spacer(1, 10))

    for key, value in stats.items():
        content.append(Paragraph(f"{key}: {value}", styles["Normal"]))

    content.append(Spacer(1, 12))

    # Simple AI-style summary (placeholder)
    summary = "Strong performance with active involvement in key plays."
    content.append(Paragraph("<b>Summary</b>", styles["Heading2"]))
    content.append(Paragraph(summary, styles["Normal"]))

    doc.build(content)