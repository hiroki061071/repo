from __future__ import annotations
import io
from pathlib import Path
import pandas as pd
from core.errors import CsvStructureError

DATE_CANDIDATES = ["date", "年月日", "年月日時", "日付"]
SUN_CANDIDATES = ["sunshine_hours", "日照時間", "日照時間(時間)", "日照時間(h)", "日照時間（時間）"]
STATION_CANDIDATES = ["station_name", "地点", "地点名", "地点名 "]
CODE_CANDIDATES = ["station_code", "地点番号", "観測所番号", "block_no"]

def _find_column(columns, candidates):
    for cand in candidates:
        if cand in columns:
            return cand
    for col in columns:
        s = str(col)
        for cand in candidates:
            if cand in s:
                return col
    return None

def _read_csv_any(path_or_bytes):
    if hasattr(path_or_bytes, "read"):
        raw = path_or_bytes.read()
        if isinstance(raw, str):
            raw = raw.encode("utf-8")
    else:
        raw = Path(path_or_bytes).read_bytes()

    last_exc = None
    for enc in ["utf-8-sig", "cp932", "utf-8"]:
        try:
            return pd.read_csv(io.StringIO(raw.decode(enc, errors="ignore")))
        except Exception as e:
            last_exc = e
    raise CsvStructureError(f"CSV 読込に失敗しました: {last_exc}")

def load_jma_csv(path_or_bytes) -> pd.DataFrame:
    df = _read_csv_any(path_or_bytes)

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [
            " ".join([str(x) for x in tup if str(x) != "nan"]).strip()
            for tup in df.columns
        ]

    date_col = _find_column(df.columns, DATE_CANDIDATES)
    sun_col = _find_column(df.columns, SUN_CANDIDATES)
    station_col = _find_column(df.columns, STATION_CANDIDATES)
    code_col = _find_column(df.columns, CODE_CANDIDATES)

    if not date_col:
        raise CsvStructureError("日付列が見つかりません。")
    if not sun_col:
        raise CsvStructureError("日照時間列が見つかりません。")

    out = pd.DataFrame()
    out["date"] = pd.to_datetime(df[date_col], errors="coerce")
    out["sunshine_hours"] = pd.to_numeric(
        df[sun_col].astype(str).str.replace(r"[^0-9\.\-]", "", regex=True),
        errors="coerce"
    )
    out["station_name"] = df[station_col].astype(str) if station_col else "地点未設定"
    out["station_code"] = df[code_col].astype(str) if code_col else ""

    out = out.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)
    return out

def normalize_to_standard_csv(input_path, output_path):
    df = load_jma_csv(input_path)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    return df
