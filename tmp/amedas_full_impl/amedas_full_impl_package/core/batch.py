from __future__ import annotations
from pathlib import Path
import pandas as pd
from core.analysis import analyze_dataframe, create_output_name, export_result_csv

def run_batch(data_df: pd.DataFrame, settings_path: str, output_dir: str) -> pd.DataFrame:
    settings = pd.read_csv(settings_path, encoding="utf-8-sig")
    rows = []

    for row in settings.itertuples():
        station = row.station_name
        period = row.period_type
        stat = row.stat_type
        start_date = pd.Timestamp(row.start_date)
        end_date = pd.Timestamp(row.end_date)

        target = data_df[
            (data_df["station_name"] == station)
            & (data_df["date"] >= start_date)
            & (data_df["date"] <= end_date)
        ].copy()

        result = analyze_dataframe(target, period, stat)
        filename = create_output_name(station, period, stat, start_date, end_date)
        out_path = export_result_csv(result, output_dir, filename)

        rows.append({
            "station_name": station,
            "period": period,
            "stat": stat,
            "output_file": str(out_path),
            "result_rows": len(result),
        })

    summary = pd.DataFrame(rows)
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    summary.to_csv(Path(output_dir) / "batch_summary.csv", index=False, encoding="utf-8-sig")
    return summary

def run_nationwide(data_df: pd.DataFrame, master_df: pd.DataFrame, start_date, end_date, period: str, stat: str, output_dir: str) -> pd.DataFrame:
    rows = []
    for station in master_df["station_name"].astype(str).unique():
        target = data_df[
            (data_df["station_name"] == station)
            & (data_df["date"] >= pd.Timestamp(start_date))
            & (data_df["date"] <= pd.Timestamp(end_date))
        ].copy()

        if target.empty:
            continue

        result = analyze_dataframe(target, period, stat)
        filename = create_output_name(station, period, stat, start_date, end_date)
        out_path = export_result_csv(result, output_dir, filename)
        rows.append({"station_name": station, "output_file": str(out_path), "result_rows": len(result)})

    summary = pd.DataFrame(rows)
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    summary.to_csv(Path(output_dir) / "nationwide_summary.csv", index=False, encoding="utf-8-sig")
    return summary
