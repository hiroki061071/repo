from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import pandas as pd
import requests

@dataclass
class FetchParams:
    prec_no: str
    block_no: str
    year: int
    month: int
    station_name: str = ""
    station_code: str = ""

def build_daily_url(params: FetchParams) -> str:
    return (
        "https://www.data.jma.go.jp/stats/etrn/view/daily_s1.php"
        f"?prec_no={params.prec_no}&block_no={params.block_no}"
        f"&year={params.year}&month={params.month}&day=&view="
    )

def fetch_daily_month(params: FetchParams) -> pd.DataFrame:
    url = build_daily_url(params)
    html = requests.get(url, timeout=30).text
    dfs = pd.read_html(html)
    target = None
    for df in dfs:
        cols = [str(c) for c in df.columns]
        if any("日照" in c for c in cols):
            target = df
            break

    if target is None:
        return pd.DataFrame(columns=["station_code", "station_name", "date", "sunshine_hours"])

    day_col = None
    sun_col = None
    for c in target.columns:
        sc = str(c)
        if sc.strip() == "日":
            day_col = c
        if "日照" in sc:
            sun_col = c

    if day_col is None or sun_col is None:
        return pd.DataFrame(columns=["station_code", "station_name", "date", "sunshine_hours"])

    out = pd.DataFrame()
    out["day"] = pd.to_numeric(target[day_col], errors="coerce")
    out["sunshine_hours"] = pd.to_numeric(target[sun_col], errors="coerce")
    out = out.dropna(subset=["day"])
    out["date"] = pd.to_datetime({
        "year": [params.year] * len(out),
        "month": [params.month] * len(out),
        "day": out["day"].astype(int),
    })
    out["station_name"] = params.station_name
    out["station_code"] = params.station_code
    return out[["station_code", "station_name", "date", "sunshine_hours"]].reset_index(drop=True)

def save_month_csv(df: pd.DataFrame, output_path: str):
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
