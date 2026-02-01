# Web App

Nuxt 4 を使ったフロントエンドアプリです。`web/` 配下から起動します。

## 📋 目次
- [概要](#概要)
- [技術スタック](#技術スタック)
- [ディレクトリ構造](#ディレクトリ構造)
- [セットアップ](#セットアップ)
- [環境変数](#環境変数)
- [使用方法](#使用方法)
- [API仕様](#api仕様)
- [開発ガイド](#開発ガイド)
- [テスト](#テスト)
- [デプロイ](#デプロイ)
- [トラブルシューティング](#トラブルシューティング)
- [リンク](#リンク)

## 概要
ユーザーの気分に合わせて散歩ルートを検索・表示するWebアプリです。

### 主な機能
- **テーマ別ルート検索**: exercise / think / refresh / nature
- **現在地ベース検索**: 位置情報から開始地点を設定
- **ルート表示**: 地図上にポリラインとスポットを表示
- **フィードバック送信**: ルート評価を送信

## 技術スタック
- **フロントエンド**: Nuxt 4, Vue 3, Nuxt UI
- **地図**: Google Maps JavaScript API（`gmp-` カスタム要素）

## ディレクトリ構造
```
web/
├── app/            # 画面・レイアウト・ページ・コンポーザブル
├── server/api/     # Nuxt サーバー API
├── assets/         # スタイルなど
├── public/         # 画像/静的ファイル
├── Dockerfile
├── docker-compose.yml
├── package.json
└── README.md
```

## セットアップ
### 前提条件
- Node.js 18+
- npm

### 依存関係のインストール
```bash
cd web
npm install
```

## 環境変数
Google Maps を使う場合は以下を設定します。

- `NUXT_PUBLIC_GOOGLE_MAPS_API_KEY`

例（PowerShell）:
```powershell
$env:NUXT_PUBLIC_GOOGLE_MAPS_API_KEY="YOUR_API_KEY"
```

## 使用方法
### 開発サーバー
```bash
npm run dev
```

### ビルド / プレビュー
```bash
npm run build
npm run preview
```

### 静的生成
```bash
npm run generate
```

### スクリプト一覧
- `npm run dev`: 開発サーバー
- `npm run build`: 本番ビルド
- `npm run preview`: ビルドのプレビュー
- `npm run generate`: 静的生成

### 主要ページ
- `/`: ランディング。気分を色で選んで検索へ遷移
- `/app/search`: ルート検索フォーム（地図 + 条件入力）
- `/app/route`: ルート表示（地図 + サマリ + 再検索/評価）
- `/contact`: お問い合わせ
- `/operator`: 運営者情報
- `/policy`: プライバシーポリシー
- `/terms`: 利用規約

### 主要機能の流れ
1. `/` で気分（テーマ/モチベーション）を選択
2. `/app/search` で現在地を取得し、ルート検索を実行
3. `/app/route` でルート/スポットを表示し、評価を送信

### クイック検索（URL パラメータ）
ランディングの色選択は以下のクエリで `/app/search` に遷移します。

- `theme`: `exercise | think | refresh | nature`
- `motivation`: `light | medium | heavy`
- `quicksearch`: `true` の場合は自動検索

例: `/app/search?theme=exercise&motivation=light&quicksearch=true`

## API仕様
フロントからは Nuxt のサーバー API を経由して Cloud Run に接続します。

- `POST /api/fetch-ai`: ルート生成（`request_id`, `theme`, `distance_km`, `start_location`, `end_location` など）
- `POST /api/route-feedback`: ルート評価（`request_id`, `route_id`, `rating`）

### リクエスト/レスポンス例
`POST /api/fetch-ai`
```json
{
  "request_id": "uuid",
  "theme": "exercise",
  "distance_km": 2,
  "start_location": { "lat": 35.685175, "lng": 139.752799 },
  "end_location": { "lat": 35.685175, "lng": 139.752799 },
  "round_trip": true,
  "debug": false
}
```

```json
{
  "statusCode": 200,
  "body": {
    "request_id": "uuid",
    "route": {
      "route_id": "route-id",
      "polyline": [{ "lat": 35.68, "lng": 139.75 }],
      "distance_km": 2,
      "duration_min": 30,
      "title": "title",
      "summary": "summary",
      "nav_waypoints": [{ "lat": 35.68, "lng": 139.75 }],
      "spots": [{ "name": "spot", "type": "park", "lat": 35.68, "lng": 139.75 }]
    },
    "meta": {}
  }
}
```

`POST /api/route-feedback`
```json
{
  "request_id": "uuid",
  "route_id": "route-id",
  "rating": 5
}
```

```json
{
  "statusCode": 200,
  "body": {
    "request_id": "uuid",
    "status": "accepted"
  }
}
```

## 開発ガイド
### 状態管理とコンポーザブル
- `useSearchParams`: 検索条件を `useState` で保持
- `useCurrentRoute`: 取得したルートを `useState` で保持
- `useRouteApi`: `fetch-ai` / `route-feedback` を呼び出す API クライアント
- `useGenerateRequestid`: `request_id` 生成（`crypto.randomUUID()`）

### 画面仕様メモ
- `/app/search`: 現在地の取得、地図クリック/マーカー操作で開始地点を調整
- `/app/route`: ルートポリライン表示、スポットのピン表示、Google Maps に遷移
- `/contact`: 連絡先表示
- `/operator`: 運営者情報
- `/policy` / `/terms`: 規約表示

### 開発メモ
- Google Maps の表示には `gmp-map` を使用しています
- マップ ID は `app/pages/app/search.vue` と `app/pages/app/route.vue` で設定しています
- API 接続先は `server/api/fetch-ai.post.ts` と `server/api/route-feedback.post.ts` の URL を変更してください
- Maps の読み込みは `NUXT_PUBLIC_GOOGLE_MAPS_API_KEY` を参照します
- ルートの座標は polyline をデコードして描画しています

### セキュリティ / 秘匿情報
- API キーは環境変数で管理し、リポジトリにコミットしないでください
- クライアントに公開される値は `NUXT_PUBLIC_` 付きで定義します

## テスト
現状、専用のテスト・Lint コマンドは用意されていません。

## デプロイ
Docker での起動手順は `README-DOCKER.md` を参照してください。

## トラブルシューティング
- 地図が表示されない: `NUXT_PUBLIC_GOOGLE_MAPS_API_KEY` が未設定/無効の可能性があります
- 位置情報が取れない: ブラウザの位置情報許可を確認してください
- ルート生成が失敗する: Cloud Run 側の API が停止している可能性があります

### FAQ
- Q. ルートが毎回同じになる  
  A. `distance_km` を変更するか、再検索を試してください
- Q. 地図が空白になる  
  A. API キー設定とブラウザの位置情報許可を確認してください

## リンク
- [プロジェクト全体のREADME](../README.md)
- [ML Services README](../ml/README.md)
- [Docker手順](./README-DOCKER.md)