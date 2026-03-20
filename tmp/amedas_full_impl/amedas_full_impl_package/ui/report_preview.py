from __future__ import annotations
from pathlib import Path
from PySide6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout

class ReportPreviewDialog(QDialog):
    def __init__(self, pdf_path: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("PDF出力結果")
        self.resize(520, 180)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("PDFを出力しました。"))
        layout.addWidget(QLabel(str(Path(pdf_path).resolve())))

        close_btn = QPushButton("閉じる")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
