from __future__ import annotations

from pathlib import Path

import pandas as pd

from core.analysis import analyze_dataframe, create_output_name, export_result_csv


_BATCH_COLUMN_ALIASES = {
    "station_name": ["station_name", "station", "地点", "地点名"],
    "period_type": ["period_type", "period", "集計単位"],
    "stat_type": ["stat_type", "stat", "統計値"],
    "start_date": ["start_date", "開始日", "from", "date_from"],
    "end_date": ["end_date", "終了日", "to", "date_to"],
}


def _normalize_text(value: str) -> str:
    return str(value).strip().replace("\ufeff", "").replace(" ", "").replace("　", "")


def _build_column_map(df: pd.DataFrame) -> dict[str, str]:
    """
    設定CSVの実列名を、内部標準列名へマッピングする。
    例:
      地点名 -> station_name
      集計単位 -> period_type
    """
    actual_cols = list(df.columns)
    normalized_actual = {_normalize_text(c): c for c in actual_cols}

    resolved = {}
    missing = []

    for std_name, aliases in _BATCH_COLUMN_ALIASES.items():
        found = None
        for alias in aliases:
            key = _normalize_text(alias)
            if key in normalized_actual:
                found = normalized_actual[key]
                break
        if found is None:
            missing.append(std_name)
        else:
            resolved[std_name] = found

    if missing:
        raise ValueError(
            "設定CSVの列が不足しています。"
            f" 不足: {', '.join(missing)}"
            f" / 実際の列: {', '.join(map(str, actual_cols))}"
        )

    return resolved


def _read_settings_csv(settings_path: str) -> pd.DataFrame:
    settings = pd.read_csv(settings_path, encoding="utf-8-sig")
    if settings.empty:
        raise ValueError("設定CSVにデータ行がありません。")
    return settings


def run_batch(data_df: pd.DataFrame, settings_path: str, output_dir: str) -> pd.DataFrame:
    if data_df is None or data_df.empty:
        raise ValueError("一括処理の元データがありません。先にCSVを読み込んでください。")

    settings = _read_settings_csv(settings_path)
    colmap = _build_column_map(settings)

    rows = []

    for i, row in settings.iterrows():
        station = str(row[colmap["station_name"]]).strip()
        period = str(row[colmap["period_type"]]).strip()
        stat = str(row[colmap["stat_type"]]).strip()
        start_date = pd.Timestamp(row[colmap["start_date"]])
        end_date = pd.Timestamp(row[colmap["end_date"]])

        target = data_df[
            (data_df["station_name"].astype(str) == station)
            & (data_df["date"] >= start_date)
            & (data_df["date"] <= end_date)
        ].copy()

        if target.empty:
            rows.append(
                {
                    "station_name": station,
                    "period": period,
                    "stat": stat,
                    "output_file": "",
                    "result_rows": 0,
                    "status": "no_data",
                    "message": "指定条件に一致する元データがありません。",
                }
            )
            continue

        try:
            result = analyze_dataframe(target, period, stat)
            filename = create_output_name(station, period, stat, start_date, end_date)
            out_path = export_result_csv(result, output_dir, filename)

            rows.append(
                {
                    "station_name": station,
                    "period": period,
                    "stat": stat,
                    "output_file": str(out_path),
                    "result_rows": len(result),
                    "status": "ok",
                    "message": "",
                }
            )
        except Exception as e:
            rows.append(
                {
                    "station_name": station,
                    "period": period,
                    "stat": stat,
                    "output_file": "",
                    "result_rows": 0,
                    "status": "error",
                    "message": str(e),
                }
            )

    summary = pd.DataFrame(rows)
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    summary.to_csv(Path(output_dir) / "batch_summary.csv", index=False, encoding="utf-8-sig")
    return summary


def run_nationwide(
    data_df: pd.DataFrame,
    master_df: pd.DataFrame,
    start_date,
    end_date,
    period: str,
    stat: str,
    output_dir: str,
) -> pd.DataFrame:
    if data_df is None or data_df.empty:
        raise ValueError(
            "設定CSVの列が不足しています。"
            f" 不足: {', '.join(missing)}"
            f" / 実際の列: {', '.join(map(str, actual_cols))}"
            " / 一括処理の設定CSVには、地点名・集計単位・統計値・開始日・終了日 が必要です。"
            " 元データCSV（日付・日照時間のCSV）を選んでいないか確認してください。"
        )
    rows = []
    start_ts = pd.Timestamp(start_date)
    end_ts = pd.Timestamp(end_date)

    for station in master_df["station_name"].astype(str).unique():
        target = data_df[
            (data_df["station_name"].astype(str) == station)
            & (data_df["date"] >= start_ts)
            & (data_df["date"] <= end_ts)
        ].copy()

        if target.empty:
            continue

        try:
            result = analyze_dataframe(target, period, stat)
            filename = create_output_name(station, period, stat, start_ts, end_ts)
            out_path = export_result_csv(result, output_dir, filename)

            rows.append(
                {
                    "station_name": station,
                    "output_file": str(out_path),
                    "result_rows": len(result),
                    "status": "ok",
                    "message": "",
                }
            )
        except Exception as e:
            rows.append(
                {
                    "station_name": station,
                    "output_file": "",
                    "result_rows": 0,
                    "status": "error",
                    "message": str(e),
                }
            )

    summary = pd.DataFrame(rows)
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    summary.to_csv(Path(output_dir) / "nationwide_summary.csv", index=False, encoding="utf-8-sig")
    return summary
        rows.append({"station_name": station, "output_file": str(out_path), "result_rows": len(result)})

    summary = pd.DataFrame(rows)
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    summary.to_csv(Path(output_dir) / "nationwide_summary.csv", index=False, encoding="utf-8-sig")
    return summary
