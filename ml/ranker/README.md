# Ranker API

ルート候補をスコアリングしてランキングするAPIサービスです。

## API仕様

### エンドポイント

- `POST /rank`: ルート候補をスコアリング

### リクエスト (`RankRequest`)

```json
{
  "request_id": "string (UUID)",
  "routes": [
    {
      "route_id": "string",
      "features": {
        "distance_km": "float",
        "duration_min": "float",
        "distance_error_ratio": "float",
        "round_trip_fit": "int (0 or 1)",
        "park_poi_ratio": "float",
        ...
      }
    }
  ]
}
```

**制約:**
- `routes`: 1件以上5件以下

### レスポンス (`RankResponse`)

```json
{
  "scores": [
    {
      "route_id": "string",
      "score": "float (0.0-1.0)"
    }
  ],
  "failed_route_ids": ["string"]
}
```

**説明:**
- `scores`: スコアリング成功したルートのリスト（スコアは0.0-1.0の範囲）
- `failed_route_ids`: スコアリング失敗したルートIDのリスト

### エラー

- `422 Unprocessable Entity`: すべてのルートのスコアリングに失敗した場合

## スコアリングロジック

現在はルールベースのスタブ実装です（MVP）。

```python
base = 0.5
base -= distance_error_ratio * 0.5      # 距離誤差が小さいほど良い
base += round_trip_fit * 0.2             # 往復ルートに適合しているほど良い
base += park_poi_ratio * 0.2            # 公園/POIの比率が高いほど良い
score = max(0.0, min(1.0, base))        # 0.0〜1.0にクリップ
```

**使用している特徴量:**
- `distance_error_ratio`: 目標距離との誤差比率（小さいほど良い）
- `round_trip_fit`: 往復ルート適合度（1 or 0）
- `park_poi_ratio`: 公園/POIの比率（大きいほど良い）

**注意:** 将来的にVertex AIを使った機械学習モデルに置き換える予定です。

## タイムアウト

Agentからの呼び出しにはタイムアウトが設定されています（デフォルト: 10秒）。

## 実装詳細

- FastAPIベースのREST API
- Pydanticによるスキーマ検証
- 部分的な成功を許容（一部のルートが失敗してもOK）
