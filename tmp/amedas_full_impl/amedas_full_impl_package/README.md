# アメダス連続無日照時間算出ツール

PySide6 ベースの Windows デスクトップアプリです。  
気象庁 CSV を読み込み、地点別の連続無日照時間を算出します。

## 判定ルール

- 1日の日照時間合計が **3.0 時間未満** の日を **無日照日** とする
- 連続無日照時間 = 連続無日照日数 × 24

## 機能

- 気象庁 CSV 読込
- 地点選択
- 月別 / 年別 / 季節別 集計
- 最大値 / 平均値 / 標準偏差
- CSV 出力
- PDF レポート出力
- グラフ表示
- 一括処理
- 実行履歴
- ログ閲覧
- 設定画面
- JMA 日別ページ取得補助
- 全国一括解析

## 起動

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## EXE 化

```bash
scripts\build_exe.bat
```
