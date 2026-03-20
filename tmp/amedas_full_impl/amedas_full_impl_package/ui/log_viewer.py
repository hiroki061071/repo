from __future__ import annotations
from pathlib import Path
from PySide6.QtWidgets import QDialog, QLineEdit, QPlainTextEdit, QPushButton, QVBoxLayout

class LogViewer(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ログ閲覧")
        self.resize(900, 600)

        layout = QVBoxLayout(self)
        self.search = QLineEdit()
        self.search.setPlaceholderText("検索キーワード")
        self.search.textChanged.connect(self.refresh)
        layout.addWidget(self.search)

        self.text = QPlainTextEdit()
        self.text.setReadOnly(True)
        layout.addWidget(self.text)

        btn = QPushButton("更新")
        btn.clicked.connect(self.refresh)
        layout.addWidget(btn)

        self.refresh()

    def refresh(self):
        path = Path("logs/app.log")
        if not path.exists():
            self.text.setPlainText("ログファイルがありません。")
            return
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        keyword = self.search.text().strip()
        if keyword:
            lines = [line for line in lines if keyword in line]
        self.text.setPlainText("\n".join(lines[-300:]))
