from __future__ import annotations

import tempfile
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from plots.charts import build_hist_figure, build_line_figure


def _register_japanese_font() -> str:
    candidates = [
        r"C:\Windows\Fonts\msgothic.ttc",
        r"C:\Windows\Fonts\YuGothM.ttc",
        r"C:\Windows\Fonts\meiryo.ttc",
        r"C:\Windows\Fonts\YuGothR.ttc",
    ]

    for font_path in candidates:
        if Path(font_path).exists():
            pdfmetrics.registerFont(TTFont("JPFont", font_path))
            return "JPFont"

    return "Helvetica"


def _safe_text(value) -> str:
    if value is None:
        return ""
    return str(value)


def _save_figure_to_temp(fig, prefix: str) -> Path | None:
    if fig is None:
        return None

    tmp = tempfile.NamedTemporaryFile(
        prefix=prefix,
        suffix=".png",
        delete=False,
    )
    tmp_path = Path(tmp.name)
    tmp.close()

    try:
        fig.savefig(tmp_path, dpi=160, bbox_inches="tight")
        return tmp_path
    except Exception:
        try:
            if tmp_path.exists():
                tmp_path.unlink()
        except Exception:
            pass
        return None


def _build_table(df, font_name: str) -> Table:
    table_data = [list(df.columns)] + df.astype(str).values.tolist()

    col_count = len(df.columns)
    default_width = 500 / max(col_count, 1)
    col_widths = [default_width] * col_count

    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), font_name),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("LEADING", (0, 0), (-1, -1), 11),
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.whitesmoke]),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("TOPPADDING", (0, 0), (-1, 0), 8),
            ]
        )
    )
    return table


def export_pdf(
    path,
    station,
    start,
    end,
    period,
    stat,
    df,
    event_df=None,
    include_charts: bool = True,
) -> None:
    """
    PDF出力。
    既存呼び出し:
        export_pdf(path, station, start, end, period, stat, df)

    追加対応:
        - event_df を渡せば、ヒストグラムはイベント一覧ベースで描画
        - include_charts=False でグラフ埋込を無効化可能
    """
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
        spaceAfter=8,
    )
    section_style = ParagraphStyle(
        "JPSection",
        parent=styles["Heading2"],
        fontName=font_name,
        fontSize=13,
        leading=16,
        spaceBefore=8,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "JPBody",
        parent=styles["Normal"],
        fontName=font_name,
        fontSize=10,
        leading=14,
    )

    doc = SimpleDocTemplate(
        str(out_path),
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    story = []
    temp_files: list[Path] = []

    try:
        story.append(Paragraph("アメダス連続無日照時間レポート", title_style))
        story.append(Spacer(1, 8))

        story.append(Paragraph(f"地点: {_safe_text(station)}", body_style))
        story.append(Paragraph(f"期間: {_safe_text(start)} ～ {_safe_text(end)}", body_style))
        story.append(Paragraph(f"集計単位: {_safe_text(period)}", body_style))
        story.append(Paragraph(f"統計値: {_safe_text(stat)}", body_style))

        result_rows = 0 if df is None else len(df)
        event_rows = 0 if event_df is None else len(event_df)

        story.append(Paragraph(f"集計結果件数: {result_rows}", body_style))
        if event_df is not None:
            story.append(Paragraph(f"イベント件数: {event_rows}", body_style))

        story.append(Spacer(1, 12))

        if include_charts:
            story.append(Paragraph("グラフ", section_style))

            line_fig = build_line_figure(df)
            line_png = _save_figure_to_temp(line_fig, "amedas_line_")
            if line_png is not None:
                temp_files.append(line_png)
                story.append(Image(str(line_png), width=520, height=300))
                story.append(Spacer(1, 8))

            hist_fig = build_hist_figure(df, event_df)
            hist_png = _save_figure_to_temp(hist_fig, "amedas_hist_")
            if hist_png is not None:
                temp_files.append(hist_png)
                story.append(Image(str(hist_png), width=520, height=300))
                story.append(Spacer(1, 12))

        story.append(Paragraph("集計結果一覧", section_style))

        if df is not None and not df.empty:
            story.append(_build_table(df, font_name))
        else:
            story.append(Paragraph("集計結果がありません。", body_style))

        if event_df is not None:
            story.append(Spacer(1, 12))
            story.append(Paragraph("イベント一覧", section_style))
            if not event_df.empty:
                display_event_df = event_df.copy()
                for col in ["開始日", "終了日"]:
                    if col in display_event_df.columns:
                        display_event_df[col] = display_event_df[col].astype(str).str[:10]
                story.append(_build_table(display_event_df, font_name))
            else:
                story.append(Paragraph("イベント一覧がありません。", body_style))

        doc.build(story)

    finally:
        for tmp in temp_files:
            try:
                if tmp.exists():
                    tmp.unlink()
            except Exception:
                pass
