from __future__ import annotations

from matplotlib import font_manager, rcParams
from matplotlib.figure import Figure


def _setup_japanese_font():
    candidates = [
        "Yu Gothic",
        "Yu Gothic UI",
        "Meiryo",
        "MS Gothic",
        "Noto Sans CJK JP",
        "IPAexGothic",
        "IPAGothic",
    ]

    available = {f.name for f in font_manager.fontManager.ttflist}
    for name in candidates:
        if name in available:
            rcParams["font.family"] = name
            break

    rcParams["axes.unicode_minus"] = False


def _empty_figure(message: str) -> Figure:
    fig = Figure(figsize=(8, 4.6))
    ax = fig.add_subplot(111)
    ax.text(0.5, 0.5, message, ha="center", va="center", fontsize=12)
    ax.set_axis_off()
    fig.tight_layout()
    return fig


def build_line_figure(df):
    _setup_japanese_font()

    if df is None or df.empty:
        return _empty_figure("表示できる集計結果がありません。")

    fig = Figure(figsize=(8, 4.6))
    ax = fig.add_subplot(111)

    x = df.iloc[:, 0].astype(str).tolist()
    y = [float(v) for v in df.iloc[:, 1].tolist()]

    if len(df) == 1:
        ax.bar(x, y, width=0.45)
        ax.set_title("連続無日照時間（単一点表示）")
        ax.text(
            0,
            y[0] + max(abs(y[0]) * 0.02, 1),
            f"{y[0]:g}",
            ha="center",
            va="bottom",
        )
    else:
        ax.plot(x, y, marker="o", linewidth=2)
        ax.set_title("連続無日照時間 推移")

        for i, value in enumerate(y):
            ax.text(
                i,
                value + max(abs(value) * 0.02, 1),
                f"{value:g}",
                ha="center",
                va="bottom",
            )

    ax.set_xlabel("期間")
    ax.set_ylabel("値(時間)")
    ax.tick_params(axis="x", rotation=45)
    ax.grid(True, linestyle="--", alpha=0.5)

    fig.tight_layout()
    return fig


def build_hist_figure(result_df=None, event_df=None):
    _setup_japanese_font()

    values = []
    title = ""
    xlabel = ""

    if event_df is not None and not event_df.empty:
        if "時間" in event_df.columns:
            values = event_df["時間"].dropna().astype(float).tolist()
        elif "hours" in event_df.columns:
            values = event_df["hours"].dropna().astype(float).tolist()

        if values:
            title = "連続無日照イベント時間 分布"
            xlabel = "イベント時間"

    if not values and result_df is not None and not result_df.empty:
        values = result_df.iloc[:, 1].dropna().astype(float).tolist()
        title = "集計値 分布"
        xlabel = "値(時間)"

    if not values:
        return _empty_figure("表示できるデータがありません。")

    fig = Figure(figsize=(8, 4.6))
    ax = fig.add_subplot(111)

    if len(values) == 1:
        ax.bar(["1件"], [values[0]], width=0.5)
        ax.text(
            0,
            values[0] + max(abs(values[0]) * 0.02, 1),
            f"{values[0]:g}",
            ha="center",
            va="bottom",
        )
        ax.set_title(f"{title}（単一点表示）")
        ax.set_xlabel("件数")
        ax.set_ylabel("時間")
    else:
        unique_count = len(set(values))
        bins = min(10, max(3, unique_count, len(values) // 2))
        ax.hist(values, bins=bins, edgecolor="black")
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel("件数")

    ax.grid(True, linestyle="--", alpha=0.5)

    fig.tight_layout()
    return fig