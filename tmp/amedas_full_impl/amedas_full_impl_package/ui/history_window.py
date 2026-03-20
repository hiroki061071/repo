from __future__ import annotations

import pandas as pd
from PySide6.QtWidgets import QDialog, QTableWidget, QTableWidgetItem, QVBoxLayout

from core.history import load_history


class HistoryWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("実行履歴")
        self.resize(900, 420)

        layout = QVBoxLayout(self)

        self.table = QTableWidget()
        layout.addWidget(self.table)

        self.load_data()

    def load_data(self):
        df = load_history()

        if df is None or df.empty:
            self.table.clear()
            self.table.setRowCount(0)
            self.table.setColumnCount(0)
            return

        # NaN を空欄表示にする
        df = df.fillna("")

        # output_file 列だけ明示的に空欄化したい場合は以下でも可
        # if "output_file" in df.columns:
        #     df["output_file"] = df["output_file"].fillna("")

        self.table.clear()
        self.table.setRowCount(len(df))
        self.table.setColumnCount(len(df.columns))
        self.table.setHorizontalHeaderLabels([str(c) for c in df.columns])

        for i, row in df.iterrows():
            for j, v in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(v)))

        self.table.resizeColumnsToContents()
