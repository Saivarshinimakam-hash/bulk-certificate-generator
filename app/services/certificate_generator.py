from pathlib import Path
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors


GENERATED_DIR = Path("generated")
GENERATED_DIR.mkdir(exist_ok=True)


def generate_certificate(
    recipient_name: str,
    event_name: str,
    certificate_title: str,
    issuer: str,
    certificate_id: int,
) -> str:
    """
    Generate a single certificate PDF and return its file path.
    """

    file_path = GENERATED_DIR / f"certificate_{certificate_id}.pdf"

    width, height = landscape(A4)

    pdf = canvas.Canvas(str(file_path), pagesize=(width, height))

    # Outer border
    pdf.setStrokeColor(colors.HexColor("#1F4E79"))
    pdf.setLineWidth(4)
    pdf.rect(25, 25, width - 50, height - 50)

    # Inner border
    pdf.setStrokeColor(colors.HexColor("#D9A441"))
    pdf.setLineWidth(1.5)
    pdf.rect(40, 40, width - 80, height - 80)

    # Certificate title
    pdf.setFillColor(colors.HexColor("#1F4E79"))
    pdf.setFont("Helvetica-Bold", 28)

    title_width = pdf.stringWidth(
        certificate_title,
        "Helvetica-Bold",
        28,
    )

    pdf.drawString(
        (width - title_width) / 2,
        height - 130,
        certificate_title,
    )

    # Presented to
    pdf.setFillColor(colors.black)
    pdf.setFont("Helvetica", 15)

    text = "This certificate is proudly presented to"

    text_width = pdf.stringWidth(text, "Helvetica", 15)

    pdf.drawString(
        (width - text_width) / 2,
        height - 190,
        text,
    )

    # Recipient name
    pdf.setFillColor(colors.HexColor("#1F4E79"))
    pdf.setFont("Helvetica-Bold", 30)

    name_width = pdf.stringWidth(
        recipient_name,
        "Helvetica-Bold",
        30,
    )

    pdf.drawString(
        (width - name_width) / 2,
        height - 245,
        recipient_name,
    )

    # Event description
    pdf.setFillColor(colors.black)
    pdf.setFont("Helvetica", 15)

    description = (
        f"for successfully completing {event_name}"
    )

    description_width = pdf.stringWidth(
        description,
        "Helvetica",
        15,
    )

    pdf.drawString(
        (width - description_width) / 2,
        height - 300,
        description,
    )

    # Issuer
    pdf.setFont("Helvetica-Bold", 14)

    issuer_width = pdf.stringWidth(
        issuer,
        "Helvetica-Bold",
        14,
    )

    pdf.drawString(
        (width - issuer_width) / 2,
        100,
        issuer,
    )

    pdf.setFont("Helvetica", 10)

    certificate_label = f"Certificate ID: {certificate_id}"

    pdf.drawString(
        60,
        60,
        certificate_label,
    )

    pdf.save()

    return str(file_path)