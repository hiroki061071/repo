from __future__ import annotations

from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from plots.charts import build_hist_figure, build_line_figure


class GraphWindow(QDialog):
    def __init__(self, result_df, event_df=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("グラフ")
        self.resize(900, 640)

        self.result_df = result_df
        self.event_df = event_df

        self.layout = QVBoxLayout(self)

        self.info_label = QLabel("")
        self.layout.addWidget(self.info_label)

        self.canvas = FigureCanvas(build_line_figure(self.result_df))
        self.layout.addWidget(self.canvas, 1)

        btns = QHBoxLayout()

        line_btn = QPushButton("折れ線")
        hist_btn = QPushButton("ヒストグラム")
        close_btn = QPushButton("閉じる")

        line_btn.clicked.connect(self.show_line)
        hist_btn.clicked.connect(self.show_hist)
        close_btn.clicked.connect(self.accept)

        btns.addWidget(line_btn)
        btns.addWidget(hist_btn)
        btns.addWidget(close_btn)

        self.layout.addLayout(btns)

        self._update_message(mode="line")

    def _replace_canvas(self, fig):
        self.layout.removeWidget(self.canvas)
        self.canvas.setParent(None)
        self.canvas.deleteLater()

        self.canvas = FigureCanvas(fig)
        self.layout.insertWidget(1, self.canvas, 1)

    def _update_message(self, mode: str):
        result_count = 0 if self.result_df is None else len(self.result_df)
        event_count = 0 if self.event_df is None else len(self.event_df)

        if mode == "line":
            if result_count == 0:
                msg = "集計結果がありません。"
            elif result_count == 1:
                msg = "集計結果が1件のみのため、折れ線ではなく棒グラフ表示に切り替えています。"
            else:
                msg = f"集計結果 {result_count} 件を表示しています。"
        else:
            if event_count == 0:
                msg = "イベント一覧がないため、集計結果ベースでヒストグラムを表示します。"
            elif event_count == 1:
                msg = "イベントが1件のみのため、単一点表示にしています。"
            else:
                msg = f"イベント {event_count} 件の分布を表示しています。"

        self.info_label.setText(msg)

    def show_line(self):
        self._replace_canvas(build_line_figure(self.result_df))
        self._update_message(mode="line")

    def show_hist(self):
        self._replace_canvas(build_hist_figure(self.result_df, self.event_df))
        self._update_message(mode="hist")