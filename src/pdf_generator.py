"""
FasalRakshak - PDF Prescription Generator Module
Generates downloadable, print-ready Agricultural Health Reports & Treatment Prescriptions for farmers.
"""

from pathlib import Path
from io import BytesIO
from datetime import datetime
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
import config

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable


def generate_prescription_pdf(prediction_result, advisory_data, weather_risk=None, farmer_name="Farmer"):
    """
    Generates a PDF prescription in memory and returns bytes.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontSize=20,
        textColor=colors.HexColor("#1b5e20"),
        spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#555555"),
        spaceAfter=15
    )
    section_heading = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontSize=13,
        textColor=colors.HexColor("#2e7d32"),
        spaceBefore=10,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        "BodyTextCustom",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#222222")
    )
    bold_body = ParagraphStyle(
        "BoldBody",
        parent=body_style,
        fontName="Helvetica-Bold"
    )

    elements = []

    # 1. Header Banner
    elements.append(Paragraph("🌾 FASALRAKSHAK: CROP HEALTH PRESCRIPTION", title_style))
    elements.append(Paragraph(
        f"AI-Powered Crop Disease Diagnostic & Advisory Report | Generated: {datetime.now().strftime('%d-%b-%Y %I:%M %p')}",
        subtitle_style
    ))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#2e7d32"), spaceAfter=12))

    # 2. Patient / Farmer Metadata Table
    meta_data = [
        [Paragraph("<b>Farmer / Field ID:</b>", body_style), Paragraph(str(farmer_name), body_style),
         Paragraph("<b>Target Crop:</b>", body_style), Paragraph(str(advisory_data.get("crop", "General")), body_style)],
        [Paragraph("<b>Diagnosis Status:</b>", body_style),
         Paragraph(f"<font color='{'#2e7d32' if prediction_result.get('is_healthy') else '#c62828'}'><b>{prediction_result.get('display_title', 'Analyzed')}</b></font>", body_style),
         Paragraph("<b>AI Confidence:</b>", body_style), Paragraph(f"<b>{prediction_result.get('confidence', 0)}%</b>", body_style)]
    ]
    meta_table = Table(meta_data, colWidths=[120, 140, 100, 140])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f1f8e9")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#c5e1a5")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 14))

    # 3. Diagnosis & Severity
    elements.append(Paragraph("🔬 Diagnostic Details", section_heading))
    elements.append(Paragraph(f"<b>Pathogen / Cause:</b> {advisory_data.get('cause', 'N/A')}", body_style))
    elements.append(Paragraph(f"<b>Disease Severity Level:</b> {advisory_data.get('severity', 'Moderate')}", body_style))
    elements.append(Spacer(1, 10))

    # 4. Prescribed Treatment Plans (Table Format)
    elements.append(Paragraph("💊 Prescribed Treatment Roadmap", section_heading))
    treatment_data = [
        [Paragraph("<b>Treatment Type</b>", bold_body), Paragraph("<b>Actionable Prescription & Application Guidelines</b>", bold_body)],
        [Paragraph("🌱 <b>Organic & Eco-Friendly Remedies</b><br/><i>(SDG 15 - Life on Land)</i>", body_style),
         Paragraph(advisory_data.get("organic_treatment", "Apply neem extract."), body_style)],
        [Paragraph("🧪 <b>Precision Chemical Treatment</b><br/><i>(SDG 12 - Responsible Use)</i>", body_style),
         Paragraph(advisory_data.get("chemical_treatment", "Consult local KVK."), body_style)],
        [Paragraph("🛡️ <b>Preventative Field Hygiene</b>", body_style),
         Paragraph(advisory_data.get("prevention", "Maintain crop spacing."), body_style)]
    ]
    treatment_table = Table(treatment_data, colWidths=[160, 340])
    treatment_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e8f5e9")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#a5d6a7")),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(treatment_table)
    elements.append(Spacer(1, 14))

    # 5. Outbreak Weather Risk (if provided)
    if weather_risk:
        elements.append(Paragraph("🌦️ Weather-Driven Disease Outbreak Risk", section_heading))
        elements.append(Paragraph(
            f"<b>Calculated Outbreak Risk Index:</b> {weather_risk.get('risk_score', 0)}% ({weather_risk.get('risk_level', 'Normal')})<br/>"
            f"<b>Advisory Note:</b> {weather_risk.get('recommendation_en', 'Normal monitoring.')}",
            body_style
        ))
        elements.append(Spacer(1, 10))

    # 6. Footer Disclaimer & Sustainability Seal
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cccccc"), spaceBefore=10, spaceAfter=8))
    elements.append(Paragraph(
        "<b>Responsible AI & Sustainability Notice:</b> This report is generated by FasalRakshak AI in accordance with UN Sustainable Development Goals (SDG 2: Zero Hunger, SDG 12, SDG 15). For severe emergencies, verify with your nearest Agricultural Extension Center (Krishi Vigyan Kendra).",
        ParagraphStyle("FooterNotice", parent=styles["Normal"], fontSize=8, textColor=colors.HexColor("#777777"))
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()


if __name__ == "__main__":
    print("[PDF Module] Testing Prescription PDF Generation...")
    sample_pred = {
        "display_title": "Potato - Late Blight",
        "confidence": 98.4,
        "is_healthy": False
    }
    sample_adv = {
        "crop": "Potato",
        "disease": "Late Blight",
        "cause": "Phytophthora infestans (Oomycete)",
        "severity": "Critical",
        "organic_treatment": "Destroy heavily infected foliage. Apply Bordeaux mixture 1%.",
        "chemical_treatment": "Spray Metalaxyl-M + Mancozeb (2.5g/L).",
        "prevention": "Ensure good drainage and hill soil around stems."
    }
    pdf_bytes = generate_prescription_pdf(sample_pred, sample_adv)
    output_path = config.ASSETS_DIR / "sample_prescription.pdf"
    with open(output_path, "wb") as f:
        f.write(pdf_bytes)
    print(f"Sample PDF successfully written to: {output_path}")
