# API仕様書

## 概要
このドキュメントは、じゃんけんゲームアプリケーションのAPI仕様を定義します。
クライアント（Flutter）とサーバー（FastAPI）間の通信インターフェースを明確化し、開発の効率化と品質の向上を図ります。

## API設計方針

### 画面単位でのAPI分離原則
本プロジェクトでは、**画面単位でのAPI分離**を基本方針とします：

1. **画面専用API**: 各画面（ロビー、設定、バトル等）には専用のAPIエンドポイントを用意
2. **機能横断の禁止**: あるAPIの修正が他画面に影響することを防ぐため、APIの機能横断的な使用は禁止
3. **代替案の回避**: クライアントが既存APIの組み合わせで代替実装することは避け、必要な機能は専用APIとして実装
4. **独立性の保証**: 各画面のAPIは独立して動作し、他画面のAPIに依存しない設計

### 実装責任
- **サーバーサイド**: 画面ごとに必要な専用APIを実装する責任
- **クライアントサイド**: 画面に対応する専用APIのみを使用する責任

### API命名規則
```
/api/{画面名}/{機能名}/{パラメータ}
```

例：
- `/api/lobby/user-stats/{userId}` - ロビー画面専用のユーザーステータス取得
- `/api/settings/user-profile/{userId}` - 設定画面専用のユーザープロフィール取得
- `/api/battle/ws/{userId}` - バトル画面専用のWebSocket接続

### WebSocket vs REST API使い分け

本プロジェクトでは、**リアルタイム性が重要な機能はWebSocket**、**一般的なCRUD操作はREST API**を使用します：

#### WebSocket推奨ケース
- **バトル画面**: マッチング・対戦・結果のリアルタイム通信
- **チャット機能**: 即座のメッセージ送受信
- **リアルタイムランキング**: 順位変動の即座の反映
- **通知システム**: プッシュ通知の即座配信

#### REST API推奨ケース
- **ロビー画面**: ユーザー情報取得・更新
- **設定画面**: プロフィール編集・画像アップロード
- **認証処理**: ログイン・ログアウト・トークン管理
- **データ取得**: 履歴・統計情報の取得

#### API移行方針
従来のポーリングベースから効率的なリアルタイム通信への移行：

1. **従来方式（非推奨）**: 
   ```
   GET /battle → ポーリング → レスポンス遅延
   ```

2. **新方式（推奨）**: 
   ```
   WebSocket /api/battle/ws/{userId} → 即座の状態変化通知
   ```

この方針により、各画面の機能が独立し、保守性と安定性を確保します。

## 環境ごとの仕様

### 共通仕様
- Bearer Token認証（JWT）を基本とする
- トークン有効期限: 24時間
- リフレッシュトークン: 30日
- レート制限: 環境ごとに設定可能

### 開発環境（ローカル）
- ベースURL: `http://192.168.0.150:3000/`
- WebSocket URL: `ws://192.168.0.150:3000/api/battle/ws/{userId}`
- 簡易ログインボタンでJWT即時発行可能
- reCAPTCHAはオプション（環境変数で制御）
- デバッグ用ヘッダー許可
- レート制限: なし
- 通信: HTTP/WebSocket
- 実装: FastAPI + WebSocket

### VPS環境
- ベースURL: `http://160.251.137.105/`
- WebSocket URL: `ws://160.251.137.105/api/battle/ws/{userId}`
- 簡易ログインボタンでJWT即時発行可能
- reCAPTCHA必須
- レート制限: 1000req/min
- 通信: HTTP/WebSocket
- 実装: FastAPI + WebSocket

### AWS環境（予定）
- ベースURL: `https://avwnok61nj.execute-api.ap-northeast-3.amazonaws.com/proc`
- WebSocket URL: `wss://avwnok61nj.execute-api.ap-northeast-3.amazonaws.com/proc/api/battle/ws/{userId}`
- 通常の認証フローのみ（簡易ログイン不可）
- reCAPTCHA必須
- APIキー認証追加
- レート制限: 2000req/min
- 通信: HTTPS/WSS
- 実装: API Gateway + Lambda

## 共通仕様

### 基本情報
- リクエスト形式: JSON
- レスポンス形式: JSON
- 文字コード: UTF-8

### リクエストヘッダー
```http
# 必須ヘッダー
Content-Type: application/json; charset=utf-8
Accept: application/json
Accept-Charset: utf-8

# 認証ヘッダー（環境に応じて必須）
Authorization: Bearer {jwt_token}    # VPS・AWS環境で必須
x-api-key: {api_key}                # AWS環境でのみ必須

# トレーシングヘッダー
x-request-id: {UUID}                # リクエスト追跡用
x-environment: {環境名}             # 環境識別用
x-api-version: {API_VERSION}        # APIバージョン
x-client-version: {CLIENT_VERSION}  # クライアントバージョン

# セキュリティヘッダー（本番環境で必須）
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Content-Security-Policy: default-src 'self'

# キャッシュ制御
Cache-Control: no-store, must-revalidate
Pragma: no-cache
```

### レスポンス形式
#### 成功時
```json
{
  "success": true,
  "data": {
    // レスポンスデータ
  }
}
```

#### エラー時
```json
{
  "success": false,
  "error": {
    "code": "string",
    "message": "string",
    "details": "string"
  }
}
```

### ステータスコード
- 200: 成功
- 400: リクエスト不正
- 401: 認証エラー
- 403: アクセス権限エラー
- 404: リソース未検出
- 429: レート制限超過
- 500: サーバーエラー
- 502: バッドゲートウェイ
- 503: サービス利用不可
- 504: ゲートウェイタイムアウト

## 主要APIエンドポイント

### 認証API

#### Magic Link認証
- `POST /api/auth/request-link` - Magic Linkリクエスト
  - リクエスト:
    ```json
    {
      "email": "string",
      "captcha": {
        "opponent": "string",
        "answer": "string",
        "token": "string"
      },
      "recaptchaToken": "string"
    }
    ```
  - レスポンス:
    ```json
    {
      "success": true,
      "data": {
        "message": "Magic link sent."
      }
    }
    ```

- `GET /api/auth/verify` - Magic Linkトークン検証
  - クエリパラメータ:
    - `token`: Magic Linkトークン
  - レスポンス:
    ```json
    {
      "success": true,
      "data": {
        "token": "string",
        "user": {
          "email": "string"
        }
      }
    }
    ```

#### 開発用簡易認証（開発環境・VPS環境のみ）
- `POST /api/auth/dev-login` - 開発用JWT即時発行
  - リクエスト:
    ```json
    {
      "email": "string",
      "mode": "dev" | "admin"
    }
    ```
  - レスポンス:
    ```json
    {
      "success": true,
      "data": {
        "token": "string",
        "user": {
          "email": "string",
          "role": "string"
        }
      }
    }
    ```

## WebSocket API仕様

### 基本情報
- プロトコル: WebSocket (RFC 6455)
- エンドポイント: `/api/battle/ws/{userId}`
- メッセージ形式: JSON
- 文字コード: UTF-8

### WebSocket接続仕様

#### 接続URL形式
```
# 開発環境
ws://192.168.0.150:3000/api/battle/ws/{userId}

# VPS環境
ws://160.251.137.105/api/battle/ws/{userId}

# AWS環境（予定）
wss://avwnok61nj.execute-api.ap-northeast-3.amazonaws.com/proc/api/battle/ws/{userId}
```

#### 接続ヘッダー
```http
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Version: 13
Authorization: Bearer {jwt_token}  # 認証が必要な場合
```

#### メッセージ形式

##### 送信メッセージ（クライアント → サーバー）
```json
{
  "type": "string",      // メッセージタイプ
  "data": {              // メッセージデータ
    // タイプ固有のデータ
  },
  "timestamp": "string", // ISO8601形式
  "messageId": "string"  // UUID（オプション）
}
```

##### 受信メッセージ（サーバー → クライアント）
```json
{
  "type": "string",      // メッセージタイプ
  "data": {              // メッセージデータ
    // タイプ固有のデータ
  },
  "timestamp": "string", // ISO8601形式
  "success": boolean,    // 処理結果
  "error": {             // エラー情報（失敗時のみ）
    "code": "string",
    "message": "string"
  }
}
```

#### 接続ライフサイクル

1. **接続確立**
   ```json
   // サーバーからの接続確認
   {
     "type": "connection_established",
     "data": {
       "userId": "string",
       "nickname": "string",
       "sessionId": "string",
       "status": "connected"
     },
     "timestamp": "2024-01-01T00:00:00Z",
     "success": true
   }
   ```

2. **ハートビート**
   ```json
   // クライアントからのping
   {
     "type": "ping",
     "data": {},
     "timestamp": "2024-01-01T00:00:00Z"
   }
   
   // サーバーからのpong
   {
     "type": "pong",
     "data": {
       "userId": "string",
       "timestamp": "2024-01-01T00:00:00Z"
     },
     "timestamp": "2024-01-01T00:00:00Z",
     "success": true
   }
   ```

3. **接続切断**
   ```json
   // クライアントからの切断通知
   {
     "type": "disconnect",
     "data": {
       "reason": "user_action"
     },
     "timestamp": "2024-01-01T00:00:00Z"
   }
   ```

#### エラーハンドリング
```json
{
  "type": "error",
  "data": {
    "originalType": "string",  // エラーの原因となったメッセージタイプ
    "originalData": {}         // エラーの原因となったメッセージデータ
  },
  "timestamp": "2024-01-01T00:00:00Z",
  "success": false,
  "error": {
    "code": "WEBSOCKET_ERROR",
    "message": "WebSocket通信エラー"
  }
}
```

### バトル画面WebSocket API（画面専用）

バトル画面でのリアルタイム通信に特化したWebSocket API仕様：

#### エンドポイント
```
/api/battle/ws/{userId}
```

#### メッセージタイプ一覧

1. **matching_start** - マッチング開始
2. **matching_status** - マッチング状態更新
3. **match_found** - マッチング成立
4. **battle_ready** - 対戦準備完了
5. **submit_hand** - 手の送信
6. **battle_result** - 対戦結果
7. **reset_hands** - 手のリセット
8. **battle_quit** - 対戦辞退

詳細な仕様は [バトル画面API](battle.md) を参照してください。

### バトル画面API（画面専用）
- `GET /api/battle` - マッチング状態確認（バトル画面専用）
  
  **注意**: このAPIはWebSocket接続が利用できない場合の代替手段として提供されます。
  通常の運用ではWebSocket API (`/api/battle/ws/{userId}`) を使用してください。
  - レスポンス:
    ```json
    {
      "success": true,
      "data": {
        "id": "string",
        "status": "string",
        "player1_id": "string",
        "player2_id": "string",
        "player1_ready": boolean,
        "player2_ready": boolean
      }
    }
    ```

- `POST /api/battle` - マッチング開始（バトル画面専用）
  - リクエスト:
    ```json
    {
      "userId": "string"
    }
    ```
  - レスポンス:
    ```json
    {
      "success": true,
      "data": {
        "matchingId": "string",
        "status": "waiting"
      }
    }
    ```

- `POST /api/battle/hand` - 手の送信（バトル画面専用）
  - リクエスト:
    ```json
    {
      "userId": "string",
      "matchingId": "string",
      "hand": "string"
    }
    ```
  - レスポンス:
    ```json
    {
      "success": true,
      "data": {
        "message": "手を送信しました",
        "status": "string"
      }
    }
    ```

- `POST /api/battle/judge` - 結果判定（バトル画面専用）
  - リクエスト:
    ```json
    {
      "matchingId": "string"
    }
    ```
  - レスポンス:
    ```json
    {
      "success": true,
      "data": {
        "result": {
          "winner": number,
          "is_draw": boolean,
          "is_finished": boolean
        }
      }
    }
    ```

- `POST /api/battle/ready` - 準備完了（バトル画面専用）
- `POST /api/battle/quit` - マッチ辞退（バトル画面専用）
- `POST /api/battle/reset_hands` - 手のリセット（バトル画面専用）

### ロビー画面API
- `GET /api/lobby/user-stats/{userId}` - ロビー用ユーザーステータス取得（ロビー画面専用）
  - レスポンス:
    ```json
    {
      "success": true,
      "data": {
        "stats": {
          "userId": "string",
          "nickname": "string",
          "profileImageUrl": "string",
          "showTitle": boolean,
          "showAlias": boolean,
          "winCount": number,
          "loseCount": number,
          "drawCount": number,
          "totalMatches": number,
          "dailyWins": number,
          "dailyRank": "string",
          "dailyRanking": number,
          "recentHandResultsStr": "string",
          "title": "string",
          "availableTitles": "string",
          "alias": "string"
        }
      }
    }
    ```

- `PUT /api/lobby/user-stats/{userId}/title-alias` - 称号・二つ名更新（ロビー画面専用）
  - リクエスト:
    ```json
    {
      "title": "string",
      "alias": "string"
    }
    ```
  - レスポンス:
    ```json
    {
      "success": true,
      "data": {
        "stats": {
          "userId": "string",
          "title": "string",
          "alias": "string",
          "updatedAt": "string"
        }
      }
    }
    ```

- `PUT /api/lobby/user-stats/{userId}/display` - 表示設定更新（ロビー画面専用）
  - リクエスト:
    ```json
    {
      "showTitle": boolean,
      "showAlias": boolean
    }
    ```
  - レスポンス:
    ```json
    {
      "success": true,
      "data": {
        "stats": {
          "userId": "string",
          "showTitle": boolean,
          "showAlias": boolean,
          "updatedAt": "string"
        }
      }
    }
    ```

### 設定画面API
- `GET /api/settings/user-profile/{userId}` - 設定画面用ユーザープロフィール取得（設定画面専用）
  - レスポンス:
    ```json
    {
      "success": true,
      "data": {
        "profile": {
          "userId": "string",
          "nickname": "string",
          "name": "string",
          "email": "string",
          "profileImageUrl": "string",
          "studentIdImageUrl": "string",
          "title": "string",
          "alias": "string",
          "availableTitles": "string",
          "university": "string",
          "postalCode": "string",
          "address": "string",
          "phoneNumber": "string",
          "isStudentIdEditable": boolean,
          "showTitle": boolean,
          "showAlias": boolean,
          "createdAt": "string",
          "updatedAt": "string"
        }
      }
    }
    ```

- `PUT /api/settings/user-profile/{userId}` - ユーザープロフィール更新（設定画面専用）
  - リクエスト:
    ```json
    {
      "nickname": "string",
      "name": "string",
      "email": "string",
      "university": "string",
      "postalCode": "string",
      "address": "string",
      "phoneNumber": "string",
      "showTitle": boolean,
      "showAlias": boolean
    }
    ```
  - レスポンス:
    ```json
    {
      "success": true,
      "data": {
        "userId": "string",
        "updatedAt": "string"
      }
    }
    ```

- `POST /api/settings/user-profile/{userId}/image` - プロフィール画像アップロード（設定画面専用）
  - リクエスト: multipart/form-data
    - image: 画像ファイル
  - レスポンス:
    ```json
    {
      "success": true,
      "data": {
        "profileImageUrl": "string"
      }
    }
    ```

- `PUT /api/settings/user-profile/{userId}/title-alias` - 称号・二つ名更新（設定画面専用）
  - リクエスト:
    ```json
    {
      "title": "string",
      "alias": "string"
    }
    ```
  - レスポンス:
    ```json
    {
      "success": true,
      "data": {
        "profile": {
          "userId": "string",
          "title": "string",
          "alias": "string",
          "updatedAt": "string"
        }
      }
    }
    ```

### デバッグAPI
- `POST /debug/clear-battles` - バトルデータのクリア
  - レスポンス:
    ```json
    {
      "success": true,
      "data": {
        "message": "string"
      }
    }
    ```

## 注意事項
- VPS環境ではAPIキー認証は不要
- AWS環境への移行時は、APIキー認証が必須となります
- 環境変数や設定ファイルでベースURLを管理することを推奨
- 本番環境へのデプロイ時は、必ずステージング環境でのテストを実施

## ドキュメント構成

### 画面単位API分離原則による構成
各APIドキュメントは対応する画面専用の機能のみを定義し、他画面からの使用は禁止します：

- [認証API](auth.md) - ログイン画面専用の認証関連API
- [登録API](register.md) - 登録画面専用のアカウント作成関連API
- [ロビー画面API](lobby.md) - ロビー画面専用のユーザー情報・設定関連API
- [バトル画面API](battle.md) - バトル画面専用のマッチング・対戦・結果関連API
- [ランキング画面API](ranking.md) - ランキング画面専用のランキング表示関連API
- [設定画面API](settings.md) - 設定画面専用のプロフィール編集・画像管理関連API
- [実装状況](status.md) - APIの実装状況と優先度

### API分離の利点
1. **保守性**: 各画面の修正が他画面に影響しない
2. **安定性**: 画面固有の要件に最適化された専用API
3. **開発効率**: 画面担当者が独立して開発可能
4. **テスト容易性**: 画面単位での独立したテスト実行

## 環境情報

### エンドポイント情報
```
VPS環境（本番）:
- ベースURL: http://160.251.137.105/
- WebSocket: ws://160.251.137.105/api/battle/ws/{userId}

開発環境（ローカル）:
- ベースURL: http://192.168.0.150:3000/
- WebSocket: ws://192.168.0.150:3000/api/battle/ws/{userId}

AWS環境（予定）:
- ベースURL: https://avwnok61nj.execute-api.ap-northeast-3.amazonaws.com/proc
- WebSocket: wss://avwnok61nj.execute-api.ap-northeast-3.amazonaws.com/proc/api/battle/ws/{userId}
```

### リージョン情報
```
リージョン: ap-northeast-3 (大阪)
```

### 注意事項
- AWS環境への移行時は、API Gatewayのステージ名（proc）は環境によって異なる可能性があります
- リージョンは必要に応じて変更される可能性があります
- エンドポイントは環境変数や設定ファイルで管理することを推奨します
- 本番環境へのデプロイ時は、必ずステージング環境でのテストを実施してください

## セキュリティと認証の詳細仕様

### 認証フロー

1. **通常認証フロー（Magic Link）**
   ```mermaid
   sequenceDiagram
       Client->>API: Magic Linkリクエスト
       API-->>Client: メール送信
       Client->>API: トークン検証
       API-->>Client: JWT発行
       Client->>API: APIリクエスト with JWT
       API-->>Client: レスポンス
   ```

2. **開発用簡易認証フロー**
   ```mermaid
   sequenceDiagram
       Client->>API: 開発用ログインリクエスト
       API-->>Client: JWT即時発行
       Client->>API: APIリクエスト with JWT
       API-->>Client: レスポンス
   ```

### 環境別認証要件

1. **開発環境**
   ```http
   # 通常認証
   Authorization: Bearer {jwt_token}
   
   # 開発用認証
   POST /api/auth/dev-login
   ```
   - reCAPTCHAオプション
   - 開発用JWT即時発行可能

2. **VPS環境**
   ```http
   # 通常認証
   Authorization: Bearer {jwt_token}
   
   # 開発用認証
   POST /api/auth/dev-login
   ```
   - reCAPTCHA必須
   - 開発用JWT即時発行可能

3. **AWS環境**
   ```http
   # 通常認証のみ
   x-api-key: {api_key}
   Authorization: Bearer {jwt_token}
   ```
   - reCAPTCHA必須
   - APIキー認証必須
   - 開発用認証不可

### セキュリティヘッダー仕様

1. **必須セキュリティヘッダー**
   ```http
   Strict-Transport-Security: max-age=31536000; includeSubDomains
   X-Content-Type-Options: nosniff
   X-Frame-Options: DENY
   Content-Security-Policy: default-src 'self'
   ```

2. **キャッシュ制御**
   ```http
   Cache-Control: no-store, must-revalidate
   Pragma: no-cache
   ```

3. **CORS設定**
   ```http
   Access-Control-Allow-Origin: {許可されたオリジン}
   Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
   Access-Control-Allow-Headers: Content-Type, Authorization, x-api-key
   Access-Control-Max-Age: 86400
   ```

### エラーレスポンス仕様

1. **認証エラー**
   ```json
   {
     "success": false,
     "error": {
       "code": "AUTH_ERROR",
       "message": "認証に失敗しました",
       "details": {
         "reason": "トークンの有効期限切れ",
         "timestamp": "2024-01-01T00:00:00Z"
       }
     }
   }
   ```

2. **APIキーエラー**
   ```json
   {
     "success": false,
     "error": {
       "code": "API_KEY_ERROR",
       "message": "無効なAPIキー",
       "details": {
         "reason": "APIキーが見つかりません",
         "timestamp": "2024-01-01T00:00:00Z"
       }
     }
   }
   ```

### トレーシングヘッダー

1. **リクエスト追跡**
   ```http
   x-request-id: {UUID}
   x-correlation-id: {UUID}
   x-session-id: {SESSION_ID}
   ```

2. **環境情報**
   ```http
   x-environment: {dev|vps|aws}
   x-api-version: {API_VERSION}
   x-client-version: {CLIENT_VERSION}
   ```

### 文字コード・エンコーディング仕様

1. **文字コード設定**
   ```http
   Content-Type: application/json; charset=utf-8
   Accept-Charset: utf-8
   ```

2. **対応文字種**
   - 漢字（JIS第1水準、第2水準）
   - ひらがな/カタカナ
   - 記号（機種依存文字を含む）
   - 絵文字（Unicode 13.0）

3. **バイナリデータ**
   ```http
   Content-Type: application/octet-stream
   Content-Transfer-Encoding: base64
   ```

### セキュリティ監査・ログ

1. **アクセスログ形式**
   ```json
   {
     "timestamp": "ISO8601形式",
     "request_id": "UUID",
     "client_ip": "IPアドレス",
     "method": "HTTPメソッド",
     "path": "リクエストパス",
     "status": "HTTPステータス",
     "user_agent": "User-Agent文字列",
     "auth_type": "認証タイプ",
     "environment": "実行環境"
   }
   ```

2. **監査ログ保持期間**
   - 開発環境: 7日間
   - VPS環境: 30日間
   - AWS環境: 90日間

### 実装時の注意事項

1. **トークン管理**
   - セキュアクッキーの使用
   - HttpOnly属性の設定
   - Secure属性の設定（HTTPS環境）

2. **エラーハンドリング**
   - 詳細なエラー情報は開発環境のみ
   - 本番環境では一般化されたエラーメッセージ
   - レート制限超過時の適切な応答

3. **セキュリティ対策**
   - 入力値のサニタイズ
   - SQLインジェクション対策
   - XSS対策

## エラーレスポンス仕様

### 1. **認証エラー**
   ```json
   {
     "success": false,
     "error": {
       "code": "AUTH_ERROR",
       "message": "認証に失敗しました",
       "details": {
         "reason": "トークンの有効期限切れ",
         "timestamp": "2024-01-01T00:00:00Z"
       }
     }
   }
   ```

2. **APIキーエラー**
   ```json
   {
     "success": false,
     "error": {
       "code": "API_KEY_ERROR",
       "message": "無効なAPIキー",
       "details": {
         "reason": "APIキーが見つかりません",
         "timestamp": "2024-01-01T00:00:00Z"
       }
     }
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
| `BATTLE_NOT_FOUND` | 404 | バトルが見つからない |
| `INSUFFICIENT_SCORE` | 400 | スコア不足 |
| `GAME_ALREADY_FINISHED` | 400 | ゲーム既に終了 |

### システム関連
| コード | HTTPステータス | 説明 |
|--------|----------------|------|
| `RATE_LIMIT_EXCEEDED` | 429 | レート制限超過 |
| `SERVICE_UNAVAILABLE` | 503 | サービス利用不可 |
| `INTERNAL_SERVER_ERROR` | 500 | サーバー内部エラー |

## レート制限仕様

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
| `/api/battle/*` | 100リクエスト | 1分間 |
| `/api/ranking/*` | 60リクエスト | 1分間 |
| `/api/lobby/*` | 200リクエスト | 1分間 |
| `/api/settings/*` | 50リクエスト | 1分間 |

## セキュリティ仕様

### HTTPS通信
- 全環境でHTTPS通信を必須とする
- 開発環境ではHTTPも許可（localhost）

### CORS設定
```javascript
// 許可するオリジン
const allowedOrigins = [
  'http://localhost:3000',  // 開発環境
  'http://160.251.137.105', // VPS環境
  'https://app.janken-game.com',  // 本番環境
  'https://admin.janken-game.com'  // 管理画面
];
```

### データ暗号化
- 個人情報は暗号化して保存
- パスワードはbcryptでハッシュ化
- Magic Linkトークンは署名付き

## 監視・ログ仕様

### ログレベル
| レベル | 説明 | 保存期間 |
|--------|------|----------|
| ERROR | エラー情報 | 90日 |
| WARN | 警告情報 | 30日 |
| INFO | 一般情報 | 7日 |
| DEBUG | デバッグ情報 | 1日 |

### システムメトリクス
- API応答時間
- エラー率
- リクエスト数
- アクティブユーザー数
- WebSocket接続数
- バトル同時実行数

## 開発者向け情報

### 開発環境セットアップ
```bash
# サーバー起動
cd server
pip install -r requirements.txt
uvicorn src.main:app --reload --host 0.0.0.0 --port 3000

# クライアント起動
cd client/game-app
flutter run
```

### API テスト例
```bash
# ヘルスチェック
curl http://160.251.137.105/api/health

# 開発用認証
curl -X POST http://160.251.137.105/api/auth/dev-login \
  -H "Content-Type: application/json" \
  -d '{"email": "dev@example.com", "mode": "dev"}'

# WebSocket接続テスト
wscat -c ws://160.251.137.105/api/battle/ws/user123
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

## インフラ系API

### システム監視エンドポイント
| エンドポイント | メソッド | 説明 | 認証 |
|----------------|----------|------|------|
| `/api/health` | GET | 基本ヘルスチェック | 不要 |
| `/api/health/detailed` | GET | 詳細ヘルスチェック | 不要 |
| `/api/metrics` | GET | システムメトリクス | 不要 |
| `/api/status` | GET | サービス状態 | 不要 |

### 管理者専用API
| エンドポイント | メソッド | 説明 | 認証 |
|----------------|----------|------|------|
| `/api/admin/users` | GET | ユーザー一覧 | 管理者 |
| `/api/admin/ban-user` | POST | ユーザーBAN | 管理者 |
| `/api/admin/system-stats` | GET | システム統計 | 管理者 |

#### ユーザーBAN例
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

## 今後の実装予定

### 1. 認証機能拡張
- ソーシャルログイン（Google, Apple）
- 多要素認証（SMS, TOTP）
- デバイス管理

### 2. ゲーム機能拡張
- リアルタイム対戦（WebSocket実装完了）
- トーナメント機能
- ギルド機能
- フレンド機能

### 3. 管理機能拡張
- 詳細な統計ダッシュボード
- 自動BAN機能
- 不正検知システム

### 4. パフォーマンス向上
- CDN導入
- キャッシュ最適化
- データベースクエリ最適化
- WebSocket接続プーリング 