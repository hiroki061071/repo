from __future__ import annotations

from pathlib import Path

import pandas as pd

from core.constants import SEASONS
from core.engine import extract_events
from core.errors import NoDataError


def _season_name(month: int) -> str:
    for name, months in SEASONS.items():
        if month in months:
            return name
    return ""


def _season_year_and_name(ts: pd.Timestamp) -> tuple[int, str]:
    """
    季節別キーの年付け。
    冬(12,1,2)は 12月の年を冬年とする。
    例:
      2015-12 -> 2015 冬
      2016-01 -> 2015 冬
      2016-02 -> 2015 冬
    """
    month = ts.month
    season_name = _season_name(month)

    if season_name == "冬":
        season_year = ts.year if month == 12 else ts.year - 1
    else:
        season_year = ts.year

    return season_year, season_name


def build_event_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    columns = ["開始日", "終了日", "連続日数", "時間", "hours"]

    if df is None or df.empty:
        return pd.DataFrame(columns=columns)

    rows = []
    for event in extract_events(df):
        rows.append(
            {
                "開始日": pd.Timestamp(event.start),
                "終了日": pd.Timestamp(event.end),
                "連続日数": int(event.days),
                "時間": float(event.hours),
                "hours": float(event.hours),
            }
        )

    event_df = pd.DataFrame(rows, columns=columns)
    if event_df.empty:
        return pd.DataFrame(columns=columns)

    event_df = event_df.sort_values(["開始日", "終了日"]).reset_index(drop=True)
    return event_df


def analyze_dataframe(df: pd.DataFrame, period: str, stat: str) -> pd.DataFrame:
    if df is None or df.empty:
        raise NoDataError("指定地点または期間のデータがありません。")

    rows = []
    for event in extract_events(df):
        end_ts = pd.Timestamp(event.end)
        season_year, season_name = _season_year_and_name(end_ts)

        rows.append(
            {
                "period_month": end_ts.strftime("%Y/%m"),
                "period_year": str(end_ts.year),
                "period_season": f"{season_year} {season_name}",
                "hours": float(event.hours),
            }
        )

    ev = pd.DataFrame(rows)
    if ev.empty:
        return pd.DataFrame(columns=["期間", "値(時間)"])

    if period == "月別":
        key = "period_month"
    elif period == "年別":
        key = "period_year"
    elif period == "季節別":
        key = "period_season"
    else:
        raise ValueError("集計単位は 月別 / 年別 / 季節別 を指定してください。")

    if stat == "最大値":
        res = ev.groupby(key, sort=True)["hours"].max()
    elif stat == "平均値":
        res = ev.groupby(key, sort=True)["hours"].mean().round(1)
    elif stat == "標準偏差":
        res = ev.groupby(key, sort=True)["hours"].std(ddof=0).fillna(0).round(1)
    else:
        raise ValueError("統計値は 最大値 / 平均値 / 標準偏差 を指定してください。")

    return (
        res.reset_index()
        .rename(columns={key: "期間", "hours": "値(時間)"})
        .reset_index(drop=True)
    )


def create_output_name(station_name, period, stat, start_date, end_date, suffix="csv"):
    s = pd.Timestamp(start_date).strftime("%Y%m%d")
    e = pd.Timestamp(end_date).strftime("%Y%m%d")
    return f"{station_name}_{period}_{stat}_{s}_{e}.{suffix}"


def export_result_csv(df: pd.DataFrame, output_dir, filename):
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    path = out_dir / filename
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return path