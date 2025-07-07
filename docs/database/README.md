# データベース設計書

## 概要

じゃんけんゲームアプリのデータベース設計書です。

## データベース構成

### 主要データベース
- **本番環境**: Amazon DynamoDB
- **開発環境**: DynamoDB Local

## テーブル設計

### Users テーブル
ユーザー情報を管理

```sql
Table: users
Partition Key: user_id (String)

Attributes:
- user_id: String (PK)
- username: String (GSI)
- email: String
- password_hash: String
- created_at: String (ISO 8601)
- last_login: String (ISO 8601)
- is_banned: Boolean
- ban_reason: String
- total_games: Number
- wins: Number
- losses: Number
- draws: Number
- current_score: Number
- highest_score: Number
```

### Games テーブル
ゲーム履歴を管理

```sql
Table: games
Partition Key: user_id (String)
Sort Key: game_id (String)

Attributes:
- user_id: String (PK)
- game_id: String (SK)
- opponent_id: String (可能であれば)
- user_choice: String (rock/paper/scissors)
- opponent_choice: String
- result: String (win/lose/draw)
- score_change: Number
- played_at: String (ISO 8601)
```

### Rankings テーブル
ランキング情報を管理

```sql
Table: rankings
Partition Key: ranking_type (String)
Sort Key: score (Number, descending)

Attributes:
- ranking_type: String (PK) # "global", "daily", "weekly"
- user_id: String
- username: String
- score: Number (SK)
- rank: Number
- updated_at: String (ISO 8601)
```

### AdminLogs テーブル
管理者操作ログを管理

```sql
Table: admin_logs
Partition Key: admin_id (String)
Sort Key: timestamp (String)

Attributes:
- admin_id: String (PK)
- timestamp: String (SK, ISO 8601)
- action: String (ban_user, unban_user, etc.)
- target_user_id: String
- reason: String
- details: Map
```

## Global Secondary Index (GSI)

### Users-Username-Index
ユーザー名でのクエリ用

```
Partition Key: username (String)
Projected Attributes: ALL
```

### Users-Score-Index
スコア順でのクエリ用

```
Partition Key: is_banned (Boolean)
Sort Key: current_score (Number, descending)
Projected Attributes: user_id, username, current_score
```

## データアクセスパターン

### ユーザー関連
1. ユーザーIDでユーザー情報取得
2. ユーザー名でユーザー検索
3. ユーザーのゲーム履歴取得
4. ユーザーのBAN/UNBAN

### ランキング関連
1. 全体ランキング取得（Top 100）
2. ユーザーの順位取得
3. リアルタイムランキング更新

### ゲーム関連
1. ゲーム結果の記録
2. ユーザーの統計情報更新

## パフォーマンス考慮事項

### Read Capacity Units (RCU)
- Users: 50 RCU
- Games: 30 RCU
- Rankings: 100 RCU (リアルタイム読み込み多数)

### Write Capacity Units (WCU)
- Users: 20 WCU
- Games: 80 WCU (ゲーム記録で頻繁な書き込み)
- Rankings: 50 WCU

### キャッシュ戦略
- ランキング情報: Redis/ElastiCache (5分間キャッシュ)
- ユーザー情報: アプリケーションレベルキャッシュ

## データ保持ポリシー

- **ゲーム履歴**: 1年間保持後アーカイブ
- **ユーザー情報**: アカウント削除まで保持
- **管理者ログ**: 3年間保持

## バックアップ戦略

- **Point-in-time Recovery**: 有効
- **日次バックアップ**: 自動実行
- **クロスリージョンレプリケーション**: 本番環境で有効 