from __future__ import annotations
from pathlib import Path

from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib import colors


def _register_japanese_font():
    candidates = [
        r"C:\Windows\Fonts\msgothic.ttc",
        r"C:\Windows\Fonts\YuGothM.ttc",
        r"C:\Windows\Fonts\meiryo.ttc",
    ]

    for font_path in candidates:
        if Path(font_path).exists():
            pdfmetrics.registerFont(TTFont("JPFont", font_path))
            return "JPFont"

    return "Helvetica"


def export_pdf(path, station, start, end, period, stat, df) -> None:
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    font_name = _register_japanese_font()

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "JPTitle",
        parent=styles["Title"],
        fontName=font_name,
        fontSize=18,
        leading=22,
    )
    body_style = ParagraphStyle(
        "JPBody",
        parent=styles["Normal"],
        fontName=font_name,
        fontSize=10,
        leading=14,
    )

    doc = SimpleDocTemplate(str(out_path))
    story = []

    story.append(Paragraph("アメダス連続無日照時間レポート", title_style))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"地点: {station}", body_style))
    story.append(Paragraph(f"期間: {start} ～ {end}", body_style))
    story.append(Paragraph(f"集計単位: {period}", body_style))
    story.append(Paragraph(f"統計値: {stat}", body_style))
    story.append(Spacer(1, 12))

    if df is not None and not df.empty:
        table_data = [list(df.columns)] + df.astype(str).values.tolist()
        table = Table(table_data)
        table.setStyle(
            TableStyle([
                ("FONTNAME", (0, 0), (-1, -1), font_name),
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ])
        )
        story.append(table)

    doc.build(story)