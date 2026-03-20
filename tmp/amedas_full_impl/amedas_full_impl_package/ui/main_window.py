from __future__ import annotations

from pathlib import Path

import pandas as pd
from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.analysis import (
    analyze_dataframe,
    build_event_dataframe,
    create_output_name,
    export_result_csv,
)
from core.history import append_history
from core.loader import load_jma_csv, normalize_to_standard_csv
from core.master import filter_master
from core.report import export_pdf
from core.validator import validate_date_range, validate_station_selected
from ui.batch_window import BatchWindow
from ui.csv_dialog import CsvDialog
from ui.graph_window import GraphWindow
from ui.history_window import HistoryWindow
from ui.jma_fetch_dialog import JmaFetchDialog
from ui.log_viewer import LogViewer
from ui.nationwide_window import NationwideWindow
from ui.report_preview import ReportPreviewDialog
from ui.settings_dialog import SettingsDialog
from utils.config import load_config
from utils.logger import get_logger


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.logger = get_logger("main")
        self.cfg = load_config()

        self.df = None
        self.result = None
        self.event_df = None
        self.current_csv = ""

        self.setWindowTitle("アメダス連続無日照時間算出ツール")
        self.resize(1120, 740)

        self._ensure_dirs()
        self._build_ui()
        self.reload_station_candidates()

    def _ensure_dirs(self):
        for d in ["input", "output", "logs", "master", "sample"]:
            Path(d).mkdir(exist_ok=True)

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        top = QHBoxLayout()
        self.path_label = QLabel("CSV未選択")

        btn_csv = QPushButton("CSV読込")
        btn_csv.clicked.connect(self.load_csv)

        btn_preview = QPushButton("プレビュー")
        btn_preview.clicked.connect(self.preview_csv)

        btn_normalize = QPushButton("標準CSV保存")
        btn_normalize.clicked.connect(self.normalize_csv)

        btn_jma = QPushButton("JMA取得")
        btn_jma.clicked.connect(self.show_jma_fetch)

        top.addWidget(self.path_label, 1)
        top.addWidget(btn_csv)
        top.addWidget(btn_preview)
        top.addWidget(btn_normalize)
        top.addWidget(btn_jma)
        layout.addLayout(top)

        filter_line = QHBoxLayout()
        self.station_filter = QLineEdit()
        self.station_filter.setPlaceholderText("地点検索")
        self.station_filter.textChanged.connect(self.reload_station_candidates)

        self.pref_combo = QComboBox()
        self.pref_combo.addItem("")
        self.pref_combo.addItems(["北海道", "東京都"])
        self.pref_combo.currentTextChanged.connect(self.reload_station_candidates)

        filter_line.addWidget(QLabel("地点検索"))
        filter_line.addWidget(self.station_filter)
        filter_line.addWidget(QLabel("都道府県"))
        filter_line.addWidget(self.pref_combo)
        layout.addLayout(filter_line)

        grid = QGridLayout()

        self.station = QComboBox()

        self.period = QComboBox()
        self.period.addItems(["月別", "年別", "季節別"])
        self.period.setCurrentText(self.cfg["default_period"])

        self.stat = QComboBox()
        self.stat.addItems(["最大値", "平均値", "標準偏差"])
        self.stat.setCurrentText(self.cfg["default_stat"])

        self.start = QDateEdit()
        self.end = QDateEdit()
        self.start.setCalendarPopup(True)
        self.end.setCalendarPopup(True)

        grid.addWidget(QLabel("地点"), 0, 0)
        grid.addWidget(self.station, 0, 1)
        grid.addWidget(QLabel("集計単位"), 0, 2)
        grid.addWidget(self.period, 0, 3)
        grid.addWidget(QLabel("統計値"), 0, 4)
        grid.addWidget(self.stat, 0, 5)
        grid.addWidget(QLabel("開始日"), 1, 0)
        grid.addWidget(self.start, 1, 1)
        grid.addWidget(QLabel("終了日"), 1, 2)
        grid.addWidget(self.end, 1, 3)

        btn_run = QPushButton("実行")
        btn_run.clicked.connect(self.run_analysis)

        btn_csv_out = QPushButton("CSV出力")
        btn_csv_out.clicked.connect(self.export_csv)

        btn_pdf = QPushButton("PDF出力")
        btn_pdf.clicked.connect(self.export_pdf_report)

        btn_graph = QPushButton("グラフ")
        btn_graph.clicked.connect(self.show_graph)

        btn_batch = QPushButton("一括処理")
        btn_batch.clicked.connect(self.show_batch)

        btn_nation = QPushButton("全国解析")
        btn_nation.clicked.connect(self.show_nationwide)

        btn_hist = QPushButton("履歴")
        btn_hist.clicked.connect(self.show_history)

        btn_log = QPushButton("ログ")
        btn_log.clicked.connect(self.show_logs)

        btn_set = QPushButton("設定")
        btn_set.clicked.connect(self.show_settings)

        grid.addWidget(btn_run, 1, 4)
        grid.addWidget(btn_csv_out, 1, 5)
        grid.addWidget(btn_pdf, 1, 6)
        grid.addWidget(btn_graph, 1, 7)
        grid.addWidget(btn_batch, 2, 4)
        grid.addWidget(btn_nation, 2, 5)
        grid.addWidget(btn_hist, 2, 6)
        grid.addWidget(btn_log, 2, 7)
        grid.addWidget(btn_set, 2, 8)

        layout.addLayout(grid)

        self.summary = QLabel("未実行")
        layout.addWidget(self.summary)

        self.table = QTableWidget()
        layout.addWidget(self.table)

    def reload_station_candidates(self):
        keyword = self.station_filter.text().strip() if hasattr(self, "station_filter") else ""
        pref = self.pref_combo.currentText().strip() if hasattr(self, "pref_combo") else ""

        df = filter_master(keyword, pref)
        stations = sorted(df["station_name"].astype(str).unique())

        current = self.station.currentText() if hasattr(self, "station") else ""
        if hasattr(self, "station"):
            self.station.clear()
            self.station.addItems(stations)
            if current in stations:
                self.station.setCurrentText(current)

    def load_csv(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "CSV選択",
            self.cfg["input_dir"],
            "CSV (*.csv)",
        )
        if not path:
            return

        try:
            self.df = load_jma_csv(path)
            self.current_csv = path
            self.result = None
            self.event_df = None

            self.path_label.setText(path)
            self.logger.info("CSV読込成功 file=%s rows=%s", path, len(self.df))

            if not self.df.empty:
                dmin = self.df["date"].min().date()
                dmax = self.df["date"].max().date()

                self.start.setDate(QDate(dmin.year, dmin.month, dmin.day))
                self.end.setDate(QDate(dmax.year, dmax.month, dmax.day))

                vals = sorted(self.df["station_name"].astype(str).unique())
                self.station.clear()
                self.station.addItems(vals)

                self.summary.setText(
                    f"CSV読込完了 / 行数={len(self.df)} / 地点数={self.df['station_name'].nunique()}"
                )
        except Exception as e:
            self.logger.exception("CSV読込失敗")
            QMessageBox.critical(self, "エラー", str(e))

    def preview_csv(self):
        if self.df is None:
            QMessageBox.warning(self, "警告", "先に CSV を読み込んでください。")
            return
        CsvDialog(self.df, self).exec()

    def normalize_csv(self):
        if not self.current_csv:
            QMessageBox.warning(self, "警告", "先に CSV を読み込んでください。")
            return

        out, _ = QFileDialog.getSaveFileName(
            self,
            "標準CSV保存",
            "input/normalized.csv",
            "CSV (*.csv)",
        )
        if not out:
            return

        try:
            normalize_to_standard_csv(self.current_csv, out)
            QMessageBox.information(self, "完了", f"保存しました。\n{out}")
        except Exception as e:
            QMessageBox.critical(self, "エラー", str(e))

    def show_jma_fetch(self):
        JmaFetchDialog(self).exec()

    def _current_target(self):
        if self.df is None:
            raise ValueError("先に CSV を読み込んでください。")

        station = self.station.currentText()
        validate_station_selected(station)

        start_date = pd.Timestamp(self.start.date().toPython())
        end_date = pd.Timestamp(self.end.date().toPython())

        validate_date_range(start_date, end_date)

        target = self.df[
            (self.df["station_name"] == station)
            & (self.df["date"] >= start_date)
            & (self.df["date"] <= end_date)
        ].copy()

        return target, station, start_date, end_date

    def run_analysis(self):
        try:
            target, station, start_date, end_date = self._current_target()
            period = self.period.currentText()
            stat = self.stat.currentText()

            self.result = analyze_dataframe(target, period, stat)
            self.event_df = build_event_dataframe(target)

            self._show_table(self.result)

            event_count = 0 if self.event_df is None else len(self.event_df)
            self.summary.setText(
                f"地点={station} / 集計={period} / 統計={stat} / "
                f"集計行数={len(self.result)} / イベント件数={event_count}"
            )

            self.logger.info(
                "集計完了 station=%s period=%s stat=%s rows=%s events=%s",
                station,
                period,
                stat,
                len(self.result),
                event_count,
            )

            append_history(
                {
                    "station_name": station,
                    "period": period,
                    "stat": stat,
                    "result_rows": len(self.result),
                    "output_file": "",
                }
            )
        except Exception as e:
            self.logger.exception("集計失敗")
            QMessageBox.critical(self, "エラー", str(e))

    def _show_table(self, df):
        self.table.clear()
        self.table.setRowCount(len(df))
        self.table.setColumnCount(len(df.columns))
        self.table.setHorizontalHeaderLabels([str(c) for c in df.columns])

        for row_idx, (_, row) in enumerate(df.iterrows()):
            for col_idx, value in enumerate(row):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

        self.table.resizeColumnsToContents()

    def export_csv(self):
        if self.result is None or self.result.empty:
            QMessageBox.warning(self, "警告", "先に集計を実行してください。")
            return

        try:
            _, station, start_date, end_date = self._current_target()

            filename = create_output_name(
                station,
                self.period.currentText(),
                self.stat.currentText(),
                start_date,
                end_date,
            )

            path, _ = QFileDialog.getSaveFileName(
                self,
                "CSV出力",
                str(Path(self.cfg["output_dir"]) / filename),
                "CSV (*.csv)",
            )
            if not path:
                return

            saved = export_result_csv(self.result, Path(path).parent, Path(path).name)

            append_history(
                {
                    "station_name": station,
                    "period": self.period.currentText(),
                    "stat": self.stat.currentText(),
                    "result_rows": len(self.result),
                    "output_file": str(saved),
                }
            )

            QMessageBox.information(self, "完了", f"CSV を保存しました。\n{saved}")
        except Exception as e:
            QMessageBox.critical(self, "エラー", str(e))

    def export_pdf_report(self):
        if self.result is None or self.result.empty:
            QMessageBox.warning(self, "警告", "先に集計を実行してください。")
            return

        try:
            _, station, start_date, end_date = self._current_target()

            filename = create_output_name(
                station,
                self.period.currentText(),
                self.stat.currentText(),
                start_date,
                end_date,
                "pdf",
            )

            path, _ = QFileDialog.getSaveFileName(
                self,
                "PDF出力",
                str(Path(self.cfg["report_dir"]) / filename),
                "PDF (*.pdf)",
            )
            if not path:
                return

            export_pdf(
                path,
                station,
                start_date.date(),
                end_date.date(),
                self.period.currentText(),
                self.stat.currentText(),
                self.result,
                self.event_df,
            )
            ReportPreviewDialog(path, self).exec()
        except Exception as e:
            QMessageBox.critical(self, "エラー", str(e))

    def show_graph(self):
        if self.result is None or self.result.empty:
            QMessageBox.warning(self, "警告", "先に集計を実行してください。")
            return

        GraphWindow(self.result, self.event_df, self).exec()

    def show_batch(self):
        if self.df is None:
            QMessageBox.warning(self, "警告", "先に CSV を読み込んでください。")
            return
        BatchWindow(self.df, self).exec()

    def show_nationwide(self):
        if self.df is None:
            QMessageBox.warning(self, "警告", "先に CSV を読み込んでください。")
            return
        NationwideWindow(
            self.df,
            pd.Timestamp(self.start.date().toPython()),
            pd.Timestamp(self.end.date().toPython()),
            self.period.currentText(),
            self.stat.currentText(),
            self,
        ).exec()

    def show_history(self):
        HistoryWindow(self).exec()

    def show_logs(self):
        LogViewer(self).exec()

    def show_settings(self):
        SettingsDialog(self).exec()
        self.cfg = load_config()
