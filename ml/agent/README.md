# Agent API

ルート生成を統括するAPIサービスです。Maps Routes API、Places API、Ranker、Vertex AIを組み合わせて最適な散歩ルートを提案します。

## 環境変数

### 必須環境変数

| 変数名 | 説明 | 例 |
|--------|------|-----|
| `MAPS_API_KEY` | Google Maps Platform API Key（Routes API / Places API共通） | `AIza...` |
| `VERTEX_PROJECT` | Google Cloud Project ID（Vertex AI使用時） | `firstdown-482704` |
| `VERTEX_LOCATION` | Vertex AI リージョン | `asia-northeast1` |

### オプション環境変数

| 変数名 | デフォルト値 | 説明 |
|--------|------------|------|
| `RANKER_URL` | `http://ranker:8080` | Ranker APIの内部URL |
| `REQUEST_TIMEOUT_SEC` | `10.0` | 外部API呼び出しのタイムアウト（秒） |
| `RANKER_TIMEOUT_SEC` | `10.0` | Ranker API呼び出しのタイムアウト（秒） |
| `VERTEX_TEXT_MODEL` | `gemini-2.5-flash` | Vertex AIで使用するモデル名 |
| `VERTEX_TEMPERATURE` | `0.3` | Vertex AIの温度パラメータ |
| `VERTEX_MAX_OUTPUT_TOKENS` | `256` | Vertex AIの最大出力トークン数 |
| `VERTEX_TOP_P` | `0.95` | Vertex AIのtop_pパラメータ |
| `VERTEX_TOP_K` | `40` | Vertex AIのtop_kパラメータ |
| `BQ_DATASET` | `firstdown_mvp` | BigQueryデータセット名 |
| `BQ_TABLE_REQUEST` | `route_request` | BigQueryリクエストテーブル名 |
| `BQ_TABLE_PROPOSAL` | `route_proposal` | BigQuery提案テーブル名 |
| `BQ_TABLE_FEEDBACK` | `route_feedback` | BigQueryフィードバックテーブル名 |
| `FEATURES_VERSION` | `mvp_v1` | 特徴量バージョン |

## API Key 管理

### Google Maps Platform API Key

**用途:**
- Routes API: ルート候補の生成
- Places API: ルート上のスポット検索

**取得方法:**
1. [Google Cloud Console](https://console.cloud.google.com/)にアクセス
2. 「APIとサービス」→「認証情報」→「認証情報を作成」→「APIキー」
3. 必要なAPIを有効化:
   - Routes API (Directions API v2)
   - Places API (New)

**セキュリティ:**
- Cloud Runの環境変数として設定（GitHub Secrets経由）
- APIキー制限を設定（HTTPリファラー、IPアドレスなど）

### Vertex AI 認証

**用途:**
- Vertex AI: ルート紹介文の生成

**認証方法:**
- サービスアカウントを使用（Cloud RunのサービスアカウントにVertex AI権限を付与）
- `VERTEX_PROJECT`と`VERTEX_LOCATION`を環境変数で指定

**必要な権限:**
- `aiplatform.endpoints.predict`
- `aiplatform.models.predict`

## ログ

### Cloud Logging での追跡

すべてのログに`request_id`を含めることで、1つのリクエストを追跡可能です。

**ログ形式:**
```
[Component] request_id={request_id} message...
```

**主要なログタグ:**
- `[Routes API Error]`: Maps Routes APIエラー
- `[Places]`: Places API成功
- `[Places Error]`: Places APIエラー
- `[Ranker Timeout]`: Rankerタイムアウト
- `[Ranker Error]`: Rankerエラー
- `[Vertex LLM Error]`: Vertex AIエラー
- `[Fallback Polyline Error]`: Fallback処理エラー

**Cloud Loggingでの検索例:**
```
resource.type="cloud_run_revision"
jsonPayload.request_id="your-request-id"
```

## API仕様

### エンドポイント

- `POST /route/generate`: ルート生成
- `POST /route/feedback`: フィードバック送信
- `GET /health`: ヘルスチェック

詳細はAPIドキュメントを参照してください。

## デプロイ

Cloud Runにデプロイされます。設定は`.github/workflows/deploy-agent.yml`を参照してください。

**リソース設定:**
- Timeout: 300秒（5分）
- Memory: 2Gi
- CPU: 2
- Concurrency: 10
