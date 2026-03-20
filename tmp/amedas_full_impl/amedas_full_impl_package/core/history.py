from __future__ import annotations
from pathlib import Path
from datetime import datetime
import pandas as pd

HISTORY_PATH = Path("logs/history.csv")

def append_history(record: dict) -> None:
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    row = {"executed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), **record}
    df = pd.DataFrame([row])
    if HISTORY_PATH.exists():
        old = pd.read_csv(HISTORY_PATH, encoding="utf-8-sig")
        df = pd.concat([old, df], ignore_index=True)
    df.to_csv(HISTORY_PATH, index=False, encoding="utf-8-sig")

def load_history() -> pd.DataFrame:
    if not HISTORY_PATH.exists():
        return pd.DataFrame(columns=["executed_at", "station_name", "period", "stat", "result_rows", "output_file"])
    return pd.read_csv(HISTORY_PATH, encoding="utf-8-sig")
