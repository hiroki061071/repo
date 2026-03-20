from __future__ import annotations
import pandas as pd
from PySide6.QtWidgets import QDialog, QFileDialog, QHBoxLayout, QLabel, QMessageBox, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout
from core.batch import run_batch

class BatchWindow(QDialog):
    def __init__(self, source_df, parent=None):
        super().__init__(parent)
        self.setWindowTitle("一括処理")
        self.resize(850, 500)
        self.source_df = source_df
        self.settings_path = None

        layout = QVBoxLayout(self)
        top = QHBoxLayout()
        self.path_label = QLabel("設定CSV未選択")
        select_btn = QPushButton("設定CSV選択")
        run_btn = QPushButton("実行")
        select_btn.clicked.connect(self.select_file)
        run_btn.clicked.connect(self.run_batch_job)
        top.addWidget(self.path_label)
        top.addWidget(select_btn)
        top.addWidget(run_btn)
        layout.addLayout(top)

        self.table = QTableWidget()
        layout.addWidget(self.table)

    def select_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "設定CSV選択", "sample", "CSV (*.csv)")
        if not path:
            return
        self.settings_path = path
        self.path_label.setText(path)

        df = pd.read_csv(path, encoding="utf-8-sig")
        self.table.setRowCount(len(df))
        self.table.setColumnCount(len(df.columns))
        self.table.setHorizontalHeaderLabels([str(c) for c in df.columns])
        for i, row in df.iterrows():
            for j, v in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(v)))

    def run_batch_job(self):
        if self.source_df is None or self.settings_path is None:
            QMessageBox.warning(self, "警告", "元データまたは設定CSVがありません。")
            return
        summary = run_batch(self.source_df, self.settings_path, "output")
        QMessageBox.information(self, "完了", f"一括処理が完了しました。件数: {len(summary)}")
