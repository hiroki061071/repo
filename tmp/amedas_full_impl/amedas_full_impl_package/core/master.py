from __future__ import annotations
from pathlib import Path
import pandas as pd

MASTER_PATH = Path("master/stations.csv")

def ensure_master() -> None:
    MASTER_PATH.parent.mkdir(parents=True, exist_ok=True)
    if MASTER_PATH.exists():
        return
    df = pd.DataFrame([
        {"station_code":"12442","station_name":"旭川","prefecture":"北海道","region":"北海道","sunshine_available":1,"prec_no":"12","block_no":"47407"},
        {"station_code":"14163","station_name":"札幌","prefecture":"北海道","region":"北海道","sunshine_available":1,"prec_no":"14","block_no":"47412"},
        {"station_code":"44132","station_name":"東京","prefecture":"東京都","region":"関東","sunshine_available":1,"prec_no":"44","block_no":"47662"},
    ])
    df.to_csv(MASTER_PATH, index=False, encoding="utf-8-sig")

def load_master() -> pd.DataFrame:
    ensure_master()
    return pd.read_csv(MASTER_PATH, encoding="utf-8-sig")

def filter_master(keyword: str = "", prefecture: str = "") -> pd.DataFrame:
    df = load_master()
    df = df[df["sunshine_available"] == 1].copy()
    if keyword:
        df = df[df["station_name"].astype(str).str.contains(keyword, na=False)]
    if prefecture:
        df = df[df["prefecture"].astype(str) == prefecture]
    return df.reset_index(drop=True)
