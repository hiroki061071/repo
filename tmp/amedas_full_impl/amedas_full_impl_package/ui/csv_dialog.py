from __future__ import annotations
from PySide6.QtWidgets import QDialog, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout

class CsvDialog(QDialog):
    def __init__(self, df, parent=None):
        super().__init__(parent)
        self.setWindowTitle("CSVプレビュー")
        self.resize(800, 500)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"読込件数: {len(df)}"))

        table = QTableWidget()
        preview = df.head(30)
        table.setRowCount(len(preview))
        table.setColumnCount(len(preview.columns))
        table.setHorizontalHeaderLabels([str(c) for c in preview.columns])

        for i, row in preview.iterrows():
            for j, value in enumerate(row):
                table.setItem(i, j, QTableWidgetItem(str(value)))

        layout.addWidget(table)
        close_btn = QPushButton("閉じる")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
