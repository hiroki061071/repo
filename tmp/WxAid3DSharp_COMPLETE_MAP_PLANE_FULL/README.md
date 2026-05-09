# WxAid3DSharp

C# / WPF / HelixToolkit.Wpf.SharpDX による、日本地形ベースの3D気象可視化ビューア雛形です。

## 実装済み機能

- 日本3D地形ビューア
- 自動回転、視点切替、ズーム、パン
- AMeDAS風CSV読込
- 気温、降水量、風速の3D柱表示
- 風向風速ベクトル表示
- GRIB2を `wgrib2.exe` 経由で読み込み
- 気温面、降水面、等値線表示
- U/V風から格子風ベクトル、流線表示
- 国土地理院タイルの自動取得処理
- 地理院タイルの出典表示
- PNGスクリーンショット保存

## 開発環境

- Windows
- Visual Studio 2022 推奨
- .NET 8 SDK

## NuGet

プロジェクトに含まれています。

- CsvHelper
- HelixToolkit.Wpf.SharpDX

## GRIB2読込について

`Tools/wgrib2.exe` は同梱していません。NOAA/CPC等からWindows版wgrib2を入手し、以下に配置してください。

```text
WxAid3DSharp/Tools/wgrib2.exe
```

アプリ側では次の要素を抽出します。

- TMP
- UGRD
- VGRD

内部的には以下のようにCSV抽出します。

```text
wgrib2 input.grib2 -match "TMP"  -csv tmp.csv
wgrib2 input.grib2 -match "UGRD" -csv ugrd.csv
wgrib2 input.grib2 -match "VGRD" -csv vgrd.csv
```

## 地理院タイルの利用と出典表示

このアプリは地理院タイルの自動取得機能を含みます。
画面右下に以下の出典表示を常時表示します。

```text
出典：地理院タイル（国土地理院）を加工して作成
```

国土地理院の案内では、国土地理院の地図等を利用する際は、申請不要の場合であっても出典記載が必要で、編集・加工する場合はその旨も記載する必要があります。実運用・公開・配布時は、利用するタイル種別ごとの備考と最新の利用条件を確認してください。

参照先：

- 国土地理院コンテンツ利用規約
- 出典の記載｜国土地理院
- 地理院タイル一覧

## AMeDAS風CSV形式

```csv
Time,Name,Latitude,Longitude,Temperature,Precipitation,WindSpeed,WindDirection
2026-05-06 09:00,東京,35.6895,139.6917,18.6,1.0,4.0,270
2026-05-06 09:00,大阪,34.6937,135.5023,20.0,0.0,3.5,250
```

## 注意

- 動画出力機能は意図的に外しています。
- `Assets/japan_dem.png` と `Assets/japan_map.png` を置くと、起動時にそれらを使って地形を生成します。
- 未配置の場合は仮地形で起動します。
- 地図タイル自動取得後のタイル結合は、今後の拡張余地としてサービスクラスを含めています。
