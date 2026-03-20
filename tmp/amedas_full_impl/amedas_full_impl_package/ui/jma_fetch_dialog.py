from __future__ import annotations
from PySide6.QtWidgets import QDialog, QFormLayout, QLineEdit, QMessageBox, QPushButton, QVBoxLayout
from core.jma_fetch import FetchParams, fetch_daily_month, save_month_csv

class JmaFetchDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("JMA 日別取得")
        self.resize(420, 280)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.prec_no = QLineEdit()
        self.block_no = QLineEdit()
        self.year = QLineEdit()
        self.month = QLineEdit()
        self.station_name = QLineEdit()
        self.station_code = QLineEdit()

        form.addRow("prec_no", self.prec_no)
        form.addRow("block_no", self.block_no)
        form.addRow("年", self.year)
        form.addRow("月", self.month)
        form.addRow("地点名", self.station_name)
        form.addRow("地点コード", self.station_code)
        layout.addLayout(form)

        btn = QPushButton("取得して保存")
        btn.clicked.connect(self.run)
        layout.addWidget(btn)

    def run(self):
        params = FetchParams(
            prec_no=self.prec_no.text(),
            block_no=self.block_no.text(),
            year=int(self.year.text()),
            month=int(self.month.text()),
            station_name=self.station_name.text(),
            station_code=self.station_code.text(),
        )
        df = fetch_daily_month(params)
        out = f"input/{params.station_name}_{params.year}{params.month:02d}.csv"
        save_month_csv(df, out)
        QMessageBox.information(self, "完了", f"保存しました。\n{out}\n件数: {len(df)}")
        self.accept()
