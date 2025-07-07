# API仕様書

## 概要

じゃんけんゲームアプリのAPI仕様書です。

## ベースURL

```
# 開発環境
https://api-dev.janken-game.com

# 本番環境
https://api.janken-game.com
```

## 認証

### JWT トークン認証

```
Authorization: Bearer <token>
```

## API エンドポイント

### 認証系

#### POST /auth/login
ユーザーログイン

**リクエスト**
```json
{
  "username": "string",
  "password": "string"
}
```

**レスポンス**
```json
{
  "token": "string",
  "user": {
    "id": "string",
    "username": "string",
    "rank": "number"
  }
}
```

### ゲーム系

#### POST /game/play
じゃんけん実行

**リクエスト**
```json
{
  "choice": "rock|paper|scissors"
}
```

**レスポンス**
```json
{
  "result": "win|lose|draw",
  "opponent_choice": "rock|paper|scissors",
  "score_change": "number"
}
```

#### GET /game/ranking
ランキング取得

**レスポンス**
```json
{
  "rankings": [
    {
      "rank": "number",
      "username": "string",
      "score": "number"
    }
  ]
}
```

### 管理系

#### POST /admin/ban-user
ユーザーBAN

**リクエスト**
```json
{
  "user_id": "string",
  "reason": "string"
}
```

**レスポンス**
```json
{
  "success": "boolean",
  "message": "string"
}
```

## エラーレスポンス

```json
{
  "error": {
    "code": "string",
    "message": "string"
  }
}
```

## WebSocket エンドポイント

### リアルタイムランキング

```
wss://api.janken-game.com/realtime/ranking
```

**メッセージ形式**
```json
{
  "type": "ranking_update",
  "data": {
    "rankings": [...]
  }
}
``` 