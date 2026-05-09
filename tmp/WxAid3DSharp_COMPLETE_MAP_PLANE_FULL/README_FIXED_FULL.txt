WxAid3DSharp 修正版フルZIP

このZIPは差分パッチではなく、プロジェクト一式です。

主な修正:
- CreatePseudoTerrain() に TextureCoordinates を追加
- Assets/japan_map.png が存在する場合、仮地形にも地図テクスチャを貼付
- PhongMaterial の DiffuseColor / AmbientColor を白に固定し、テクスチャの暗潰れを回避
- 地図タイル取得後、実行フォルダ側 Assets/japan_map.png に保存し、即 CreatePseudoTerrain() で反映
- TileMerger.MergeTilesByRange() を追加
- SaveBitmapSourceAsPng() を追加

注意:
- この環境では dotnet build が実行できないため、Visual Studio 側でビルド確認してください。
- wgrib2.exe は同梱していません。GRIB2読込を使う場合は Tools/wgrib2.exe に配置してください。
