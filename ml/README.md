# ML Services

このディレクトリには、firstdownのML関連サービスが含まれています。

## サービス一覧

- **agent**: ルート生成を統括するAPIサービス
- **ranker**: ルート候補をスコアリングするAPIサービス

## 環境変数

各サービスの環境変数については、各サービスのREADMEを参照してください。

- [Agent README](./agent/README.md)
- [Ranker README](./ranker/README.md)

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

**Cloud Loggingでの検索例:**
```
resource.type="cloud_run_revision"
jsonPayload.request_id="your-request-id"
```

## デプロイ

各サービスはCloud Runにデプロイされます。設定は`.github/workflows/`を参照してください。