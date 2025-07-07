# API仕様書

## 概要

じゃんけんゲームアプリのAPI仕様書です。
Magic Link方式による認証を基本とし、画面単位API分離原則に基づいて設計されています。

## 基本情報

### ベースURL

```
# 開発環境
http://localhost:8000

# VPS環境
https://api-vps.janken-game.com

# AWS環境
https://api.janken-game.com
```

### API設計原則

- **画面単位API分離**: 各画面専用のAPIエンドポイントを提供
- **環境別認証レベル**: 開発/VPS/AWS環境で異なるセキュリティレベル
- **統一レスポンス形式**: 全APIで統一されたレスポンス構造
- **包括的エラーハンドリング**: 詳細なエラー情報とコードを提供

## 認証

### 基本認証方式

| 方式 | 説明 | 対象環境 |
|------|------|----------|
| Magic Link | メール認証によるパスワードレス認証 | 全環境 |
| 開発用認証 | JWT即時発行による簡易認証 | 開発/VPS環境のみ |
| 従来認証 | ID/パスワード方式（互換性維持） | 全環境 |

### 認証ヘッダー

```http
# JWT認証（推奨）
Authorization: Bearer <jwt_token>

# APIキー認証（AWS環境のみ）
x-api-key: <api_key>

# 環境識別
x-environment: <development|vps|aws>
x-api-version: 1.0.0
x-client-version: <client_version>
```

## APIエンドポイント

### 認証系 (`/api/auth`)

詳細は [認証API仕様書](auth.md) を参照

| エンドポイント | メソッド | 説明 |
|----------------|----------|------|
| `/api/auth/request-link` | POST | Magic Link リクエスト |
| `/api/auth/verify` | GET | Magic Link 検証 |
| `/api/auth/dev-login` | POST | 開発用簡易認証 |
| `/api/auth/UserInfo` | POST | 従来形式ログイン |

### ゲーム系 (`/api/game`)

| エンドポイント | メソッド | 説明 | 認証 |
|----------------|----------|------|------|
| `/api/game/play` | POST | じゃんけん実行 | 必須 |
| `/api/game/history` | GET | 対戦履歴取得 | 必須 |
| `/api/game/stats` | GET | 統計情報取得 | 必須 |

#### じゃんけん実行

```http
POST /api/game/play
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "choice": "rock|paper|scissors"
}
```

**レスポンス**
```json
{
  "success": true,
  "result": "win|lose|draw",
  "opponent_choice": "rock|paper|scissors",
  "score_change": 10,
  "new_score": 1010,
  "battle_id": "uuid"
}
```

### ランキング系 (`/api/ranking`)

| エンドポイント | メソッド | 説明 | 認証 |
|----------------|----------|------|------|
| `/api/ranking/daily` | GET | 日次ランキング | 必須 |
| `/api/ranking/weekly` | GET | 週次ランキング | 必須 |
| `/api/ranking/monthly` | GET | 月次ランキング | 必須 |

#### ランキング取得

```http
GET /api/ranking/daily?limit=100&offset=0
Authorization: Bearer <jwt_token>
```

**レスポンス**
```json
{
  "success": true,
  "rankings": [
    {
      "rank": 1,
      "user_id": "user123",
      "nickname": "じゃんけん王",
      "score": 1500,
      "wins": 150,
      "losses": 50,
      "draws": 25
    }
  ],
  "total_count": 1000,
  "current_user_rank": 42
}
```

### ユーザー管理系 (`/api/user`)

| エンドポイント | メソッド | 説明 | 認証 |
|----------------|----------|------|------|
| `/api/user/profile` | GET | プロフィール取得 | 必須 |
| `/api/user/profile` | PUT | プロフィール更新 | 必須 |
| `/api/user/avatar` | POST | アバター画像アップロード | 必須 |

### 管理系 (`/api/admin`)

| エンドポイント | メソッド | 説明 | 認証 |
|----------------|----------|------|------|
| `/api/admin/users` | GET | ユーザー一覧 | 管理者 |
| `/api/admin/ban-user` | POST | ユーザーBAN | 管理者 |
| `/api/admin/system-stats` | GET | システム統計 | 管理者 |

#### ユーザーBAN

```http
POST /api/admin/ban-user
Authorization: Bearer <admin_jwt_token>
Content-Type: application/json

{
  "user_id": "user123",
  "reason": "不正行為",
  "duration_days": 7
}
```

**レスポンス**
```json
{
  "success": true,
  "message": "ユーザーをBANしました",
  "ban_info": {
    "user_id": "user123",
    "banned_until": "2024-07-01T00:00:00Z",
    "reason": "不正行為"
  }
}
```

### インフラ系 (`/api`)

| エンドポイント | メソッド | 説明 | 認証 |
|----------------|----------|------|------|
| `/api/health` | GET | 基本ヘルスチェック | 不要 |
| `/api/health/detailed` | GET | 詳細ヘルスチェック | 不要 |
| `/api/metrics` | GET | システムメトリクス | 不要 |
| `/api/status` | GET | サービス状態 | 不要 |

## 統一レスポンス形式

### 成功レスポンス

```json
{
  "success": true,
  "data": {
    // 実際のデータ
  },
  "message": "処理が完了しました",
  "timestamp": "2024-06-24T12:00:00Z"
}
```

### エラーレスポンス

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "ユーザー向けエラーメッセージ",
    "details": "詳細なエラー情報",
    "field": "エラーが発生したフィールド名"
  },
  "timestamp": "2024-06-24T12:00:00Z"
}
```

## エラーコード一覧

### 認証関連

| コード | HTTPステータス | 説明 |
|--------|----------------|------|
| `AUTH_TOKEN_MISSING` | 401 | 認証トークンが不足 |
| `AUTH_TOKEN_INVALID` | 401 | 認証トークンが無効 |
| `AUTH_TOKEN_EXPIRED` | 401 | 認証トークンが期限切れ |
| `AUTH_PERMISSION_DENIED` | 403 | 権限不足 |

### バリデーション関連

| コード | HTTPステータス | 説明 |
|--------|----------------|------|
| `VALIDATION_ERROR` | 400 | バリデーションエラー |
| `REQUIRED_FIELD_MISSING` | 400 | 必須フィールドが不足 |
| `INVALID_FORMAT` | 400 | 形式が不正 |
| `VALUE_OUT_OF_RANGE` | 400 | 値が範囲外 |

### ビジネスロジック関連

| コード | HTTPステータス | 説明 |
|--------|----------------|------|
| `USER_NOT_FOUND` | 404 | ユーザーが見つからない |
| `GAME_NOT_FOUND` | 404 | ゲームが見つからない |
| `INSUFFICIENT_SCORE` | 400 | スコア不足 |
| `GAME_ALREADY_FINISHED` | 400 | ゲーム既に終了 |

### システム関連

| コード | HTTPステータス | 説明 |
|--------|----------------|------|
| `RATE_LIMIT_EXCEEDED` | 429 | レート制限超過 |
| `SERVICE_UNAVAILABLE` | 503 | サービス利用不可 |
| `INTERNAL_SERVER_ERROR` | 500 | サーバー内部エラー |

## レート制限

### 環境別制限

| 環境 | 制限 | 単位 |
|------|------|------|
| 開発環境 | 制限なし | - |
| VPS環境 | 1000リクエスト | 1分間 |
| AWS環境 | 2000リクエスト | 1分間 |

### エンドポイント別制限

| エンドポイント | 制限 | 単位 |
|----------------|------|------|
| `/api/auth/request-link` | 5リクエスト | 5分間 |
| `/api/game/play` | 100リクエスト | 1分間 |
| `/api/ranking/*` | 60リクエスト | 1分間 |

## WebSocket エンドポイント

### リアルタイム機能

| エンドポイント | 説明 | 認証 |
|----------------|------|------|
| `wss://api.janken-game.com/realtime/ranking` | リアルタイムランキング | 必須 |
| `wss://api.janken-game.com/realtime/battle` | リアルタイム対戦 | 必須 |

#### 接続例

```javascript
const ws = new WebSocket('wss://api.janken-game.com/realtime/ranking');
ws.onopen = () => {
  // 認証情報送信
  ws.send(JSON.stringify({
    type: 'auth',
    token: 'your_jwt_token'
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'ranking_update') {
    // ランキング更新処理
    console.log(data.rankings);
  }
};
```

## セキュリティ

### HTTPS通信

- 全環境でHTTPS通信を必須とする
- 開発環境ではHTTPも許可（localhost）

### CORS設定

```javascript
// 許可するオリジン
const allowedOrigins = [
  'http://localhost:3000',  // 開発環境
  'https://app.janken-game.com',  // 本番環境
  'https://admin.janken-game.com'  // 管理画面
];
```

### データ暗号化

- 個人情報は暗号化して保存
- パスワードはbcryptでハッシュ化
- Magic Linkトークンは署名付き

## 監視・ログ

### ログレベル

| レベル | 説明 | 保存期間 |
|--------|------|----------|
| ERROR | エラー情報 | 90日 |
| WARN | 警告情報 | 30日 |
| INFO | 一般情報 | 7日 |
| DEBUG | デバッグ情報 | 1日 |

### メトリクス

- API応答時間
- エラー率
- リクエスト数
- アクティブユーザー数

## 開発者向け情報

### 開発環境セットアップ

```bash
# サーバー起動
cd server
pip install -r requirements.txt
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# クライアント起動
cd client/game-app
flutter run
```

### API テスト

```bash
# ヘルスチェック
curl http://localhost:8000/api/health

# 開発用認証
curl -X POST http://localhost:8000/api/auth/dev-login \
  -H "Content-Type: application/json" \
  -d '{"email": "dev@example.com", "mode": "dev"}'
```

### 環境変数

```bash
# 必須環境変数
export ENVIRONMENT=development
export JWT_SECRET_KEY=your-secret-key
export DB_HOST=localhost
export DB_NAME=janken_game
export REDIS_HOST=localhost
export MINIO_ENDPOINT=localhost:9000
```

## 今後の実装予定

1. **認証機能拡張**
   - ソーシャルログイン（Google, Apple）
   - 多要素認証（SMS, TOTP）
   - デバイス管理

2. **ゲーム機能拡張**
   - リアルタイム対戦
   - トーナメント機能
   - ギルド機能

3. **管理機能拡張**
   - 詳細な統計ダッシュボード
   - 自動BAN機能
   - 不正検知システム

4. **パフォーマンス向上**
   - CDN導入
   - キャッシュ最適化
   - データベースクエリ最適化

## 更新履歴

| 日付 | バージョン | 変更内容 |
|------|------------|----------|
| 2024-06-24 | 1.0.0 | Magic Link認証方式への移行 |
| 2024-06-24 | 1.0.0 | 画面単位API分離原則の適用 |
| 2024-06-24 | 1.0.0 | 環境別認証レベルの実装 | 