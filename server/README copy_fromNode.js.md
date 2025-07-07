# かみのてじゃんけん - バックエンドAPIサーバー

じゃんけんゲームのバックエンドAPIサーバーです。VPS環境での開発/テストを経て、AWS環境への移行を前提とした設計となっています。

## 技術スタック

### 現行環境（VPS）
- Node.js (v20.x)
- Express.js (APIサーバー)
- MySQL 8.0 (メインDB)
- Redis 6.2 (セッション/キャッシュ)
- MinIO (S3互換ストレージ)
- Docker & Docker Compose
- Nginx (リバースプロキシ)

### 移行先環境（AWS）
- AWS Lambda (サーバーレス実行環境)
- Amazon RDS for MySQL
- Amazon ElastiCache (Redis)
- Amazon S3 (オブジェクトストレージ)
- Amazon API Gateway
- AWS SAM (開発/デプロイ)

## 開発環境のセットアップ

### 1. 環境変数の設定

```bash
# ローカル開発環境用
cp environments/environment.local.template environments/.env.local

# VPS環境用
cp environments/environment.vps.template environments/.env.vps
```

各環境ファイルを編集し、必要な値を設定してください。

### 2. 開発環境の起動

```bash
# 依存関係のインストール
npm install

# ローカル開発環境の起動
docker-compose up -d   # localhost:80 でアクセス可能

# VPS環境の起動
docker-compose -f docker-compose-vps.yml up -d
```

### 3. 動作確認

以下のエンドポイントにアクセスして機能を確認できます：

- ヘルスチェック: `/api/health`
- MySQL状態: `/api/health/mysql`
- Redis状態: `/api/health/redis`
- MinIO状態: `/api/health/minio`

## アーキテクチャ

### コンテナ構成

- nginx: リバースプロキシ（80番ポート公開）
- api: バックエンドAPI（Express, 3000番ポート）
- mysql: データベース
- redis: セッション/キャッシュ
- minio: S3互換ストレージ

### ルーティング設計

すべてのAPIリクエストは、nginxリバースプロキシ経由でアクセスします：

- `/api/*` - バックエンドAPIへのプロキシ
- `/health` - Nginxのヘルスチェック
- `/` - 静的ファイル（テストページなど）

### Lambda/Express ブリッジパターン

AWS Lambda関数をExpressサーバーでラップして実行：

```javascript
const wrapLambda = async (handler, req, res) => {
    const event = {
        httpMethod: req.method,
        path: req.path,
        body: JSON.stringify(req.body),
        headers: req.headers,
        pathParameters: req.params,
        queryStringParameters: req.query
    };
    
    const result = await handler(event, context);
    res.status(result.statusCode).json(JSON.parse(result.body));
};
```

## プロジェクト構造

```
/
├── src/                  # ソースコード
│   ├── core/            # 共通コア機能
│   │   ├── controllers/ # ビジネスロジック
│   │   ├── models/      # データモデル
│   │   └── services/    # 共通サービス
│   │
│   ├── handlers/        # Lambda handlers
│   │   ├── auth/       # 認証系
│   │   ├── game/       # ゲーム系
│   │   ├── user/       # ユーザー系
│   │   └── lobby/      # ロビー系
│   │
│   ├── infrastructure/ # インフラ層
│   │   ├── storage/   # ストレージ抽象化
│   │   ├── cache/     # キャッシュ抽象化
│   │   └── database/  # DB抽象化
│   │
│   └── config/        # 設定
│
├── nginx/              # Nginx設定
├── environments/       # 環境変数
├── docs/              # ドキュメント
├── tests/             # テスト
├── Dockerfile         # アプリケーションのDockerfile
└── docker-compose.yml # Docker Compose設定
```

## Docker環境の管理

```bash
# コンテナの状態確認
docker-compose ps

# ログの確認
docker-compose logs

# 特定のサービスのログ確認
docker-compose logs api

# コンテナの停止
docker-compose down

# コンテナの再起動
docker-compose restart
```

## トラブルシューティング

### よくある問題と解決策

1. コンテナが起動しない
   - ログを確認: `docker-compose logs`
   - ポート競合の確認: `netstat -an | findstr "80 3000"`
   - 環境変数の確認: `.env`ファイルの存在と内容

2. APIにアクセスできない
   - Nginxのログを確認: `docker-compose logs nginx`
   - APIコンテナの状態確認: `docker-compose ps api`
   - ヘルスチェックの実行: `curl http://localhost/api/health`

3. データベース接続エラー
   - MySQLコンテナの状態確認: `docker-compose logs mysql`
   - 接続情報の確認: 環境変数の設定を確認
   - データベース初期化の確認: `docker-compose exec mysql mysql -u root -p`

### デバッグモード

```bash
# 詳細なログ出力の有効化
DEBUG=true docker-compose up -d
```

## ライセンス

MIT

## コントリビューション

Issue、Pull Requestは歓迎します。
