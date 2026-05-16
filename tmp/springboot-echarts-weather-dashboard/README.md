# Spring Boot + JSON + ECharts 気象ダッシュボード

Open-Meteo の予報 API を Spring Boot で取得し、ECharts で可視化するサンプルです。

## 構成
- Backend: Spring Boot 4.0.6
- Frontend: HTML + JavaScript + ECharts
- Weather API: Open-Meteo Forecast API

## 機能
- 地点プリセット（東京・大阪・新潟・札幌・那覇）
- 緯度経度の手入力
- 7日間の最高/最低気温 折れ線グラフ
- 降水確率の棒グラフ
- 風速 + 天気コードの複合グラフ
- 日別予報テーブル表示
- バックエンド API: `/api/forecast`

## 前提
- Java 17 以上
- Maven 3.9 以上推奨

## 起動
```bash
mvn spring-boot:run
```

ブラウザ:
```text
http://localhost:8080
```

## API 例
```text
GET /api/forecast?lat=37.9162&lon=139.0364&timezone=Asia/Tokyo
```

## 補足
- Open-Meteo は JSON で日別の最高/最低気温、降水確率、風速、天気コードなどを取得できます。
- Spring Boot の公式では Java 17 以上が必要です。
- ECharts は `dataset` や `encode` を使ったデータマッピングをサポートします。
