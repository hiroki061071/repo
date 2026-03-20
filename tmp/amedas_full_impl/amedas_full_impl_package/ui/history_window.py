from __future__ import annotations
from PySide6.QtWidgets import QDialog, QTableWidget, QTableWidgetItem, QVBoxLayout
from core.history import load_history

class HistoryWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("実行履歴")
        self.resize(900, 500)

        layout = QVBoxLayout(self)
        self.table = QTableWidget()
        layout.addWidget(self.table)
        self.load_data()

    def load_data(self):
        df = load_history()
        self.table.setRowCount(len(df))
        self.table.setColumnCount(len(df.columns))
        self.table.setHorizontalHeaderLabels([str(c) for c in df.columns])

        for i, row in df.iterrows():
            for j, v in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(v)))
