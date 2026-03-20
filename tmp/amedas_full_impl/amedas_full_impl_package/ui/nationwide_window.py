from __future__ import annotations
from PySide6.QtWidgets import QDialog, QLabel, QMessageBox, QPushButton, QVBoxLayout
from core.batch import run_nationwide
from core.master import load_master

class NationwideWindow(QDialog):
    def __init__(self, source_df, start_date, end_date, period, stat, parent=None):
        super().__init__(parent)
        self.setWindowTitle("全国一括解析")
        self.source_df = source_df
        self.start_date = start_date
        self.end_date = end_date
        self.period = period
        self.stat = stat

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("現在読み込んでいるデータを対象に、地点マスタの地点を一括解析します。"))
        run_btn = QPushButton("実行")
        run_btn.clicked.connect(self.run)
        layout.addWidget(run_btn)

    def run(self):
        master = load_master()
        summary = run_nationwide(self.source_df, master, self.start_date, self.end_date, self.period, self.stat, "output")
        QMessageBox.information(self, "完了", f"全国一括解析が完了しました。件数: {len(summary)}")
        self.accept()
