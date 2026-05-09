WxAid3DSharp 完全版（地図専用平面レイヤ方式）

内容:
- WPF + HelixToolkit.Wpf.SharpDX
- 地図専用平面レイヤ MapImagePlaneModel
- Assets/japan_map.png 同梱
- CSV読込、気温/降水量/風速/風ベクトル、時系列再生
- 地図タイル取得後に japan_map.png を生成し、CreateMapImagePlane() で即反映

起動:
1. WxAid3DSharp.sln を Visual Studio で開く
2. ビルドして実行
3. CSV読込 → Data/sample_amedas_large.csv または Assets/sample_amedas_large.csv を選択

注意:
- wgrib2.exe は同梱していません。GRIB2読込を使う場合のみ Tools/wgrib2.exe として配置してください。
- 地図が出ない場合は bin/Debug/net8.0-windows/Assets/japan_map.png が存在するか確認してください。
- 出典: 地理院タイル（国土地理院）を加工して作成
