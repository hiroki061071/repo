from __future__ import annotations
from PySide6.QtWidgets import QDialog, QFormLayout, QLineEdit, QMessageBox, QPushButton, QVBoxLayout
from utils.config import load_config, save_config

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("設定")
        self.resize(520, 260)

        cfg = load_config()

        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.input_dir = QLineEdit(cfg["input_dir"])
        self.output_dir = QLineEdit(cfg["output_dir"])
        self.log_dir = QLineEdit(cfg["log_dir"])
        self.report_dir = QLineEdit(cfg["report_dir"])
        form.addRow("入力フォルダ", self.input_dir)
        form.addRow("出力フォルダ", self.output_dir)
        form.addRow("ログフォルダ", self.log_dir)
        form.addRow("レポートフォルダ", self.report_dir)
        layout.addLayout(form)

        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.save)
        layout.addWidget(save_btn)

    def save(self):
        save_config({
            "input_dir": self.input_dir.text(),
            "output_dir": self.output_dir.text(),
            "log_dir": self.log_dir.text(),
            "report_dir": self.report_dir.text(),
        })
        QMessageBox.information(self, "完了", "設定を保存しました。")
        self.accept()
