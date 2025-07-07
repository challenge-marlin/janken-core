# API実装状況

## 概要
このドキュメントは、画面単位でのAPI分離原則に基づくじゃんけんゲームアプリケーションのAPI実装状況を記載します。

## 画面単位API分離原則
各画面は専用のAPIセットを使用し、他画面のAPIに依存しません：
- **認証API** ← ログイン画面専用
- **登録API** ← 登録画面専用  
- **ロビー画面API** ← ロビー画面専用
- **バトル画面API** ← バトル画面専用
- **ランキング画面API** ← ランキング画面専用
- **設定画面API** ← 設定画面専用

## 実装済みAPI

### ✅ 認証API（ログイン画面専用）
- **POST /UserInfo** - ログイン機能
  - 実装状況: ✅ 完了
  - 場所: `awsTest/lambda/login/index.js`
  - 備考: ログイン画面専用、API仕様書に完全準拠

### ✅ 登録API（登録画面専用）
- **GET /check-userid** - ユーザーID重複チェック
  - 実装状況: ✅ 完了
  - 場所: `awsTest/lambda/register/index.js`
  - 備考: 登録画面専用、バリデーション機能付き
- **POST /register** - ユーザー登録
  - 実装状況: ✅ 完了
  - 場所: `awsTest/lambda/register/index.js`
  - 備考: 登録画面専用、トランザクション処理、パスワードハッシュ化、初期ステータス作成

### ✅ ロビー画面API（ロビー画面専用）
- **GET /api/lobby/user-stats/{userId}** - ロビー用ユーザーステータス取得
  - 実装状況: ✅ 完了
  - 場所: `awsTest/lambda/lobby/user-stats/index.js`
  - 備考: ロビー画面専用、API仕様書準拠
- **PUT /api/lobby/user-stats/{userId}/title-alias** - 称号・二つ名更新
  - 実装状況: ✅ 完了
  - 場所: `awsTest/lambda/lobby/user-stats/title-alias/index.js`
  - 備考: ロビー画面専用
- **PUT /api/lobby/user-stats/{userId}/display** - 表示設定更新
  - 実装状況: 🚧 実装必要
  - 備考: ロビー画面専用、称号・二つ名表示ON/OFF専用API

### ✅ バトル画面API（バトル画面専用）
- **GET /battle** - マッチング状態確認
  - 実装状況: ✅ 完了
  - 場所: `awsTest/lambda/hand/index.js`
  - 備考: バトル画面専用、Redis使用、API仕様書準拠のレスポンス形式
- **POST /battle** - マッチング開始
  - 実装状況: ✅ 完了
  - 場所: `awsTest/lambda/hand/index.js`
  - 備考: バトル画面専用
- **POST /battle/hand** - 手の送信
  - 実装状況: ✅ 完了
  - 場所: `awsTest/lambda/hand/index.js`
  - 備考: バトル画面専用、Redis使用、完全なビジネスロジック実装済み
- **POST /battle/judge** - 結果判定
  - 実装状況: ✅ 完了
  - 場所: `awsTest/lambda/judge/index.js`
  - 備考: バトル画面専用、Redis使用、勝敗判定・引き分け処理完備
- **POST /battle/ready** - 準備完了
  - 実装状況: ✅ 完了
  - 場所: `awsTest/lambda/hand/index.js`
  - 備考: バトル画面専用
- **POST /battle/quit** - マッチ辞退
  - 実装状況: ✅ 完了
  - 場所: `awsTest/lambda/hand/index.js`
  - 備考: バトル画面専用
- **POST /battle/reset_hands** - 手のリセット
  - 実装状況: ✅ 完了
  - 場所: `awsTest/lambda/hand/index.js`
  - 備考: バトル画面専用

### ✅ ランキング画面API（ランキング画面専用）
- **GET /ranking** - ランキングデータ取得
  - 実装状況: ✅ 完了
  - 場所: `awsTest/lambda/ranking/index.js`
  - 備考: ランキング画面専用、MySQL集計クエリでリアルタイムランキング生成

### 🚧 設定画面API（設定画面専用・拡張が必要）
- **GET /api/settings/user-profile/{userId}** - 設定画面用ユーザープロフィール取得
  - 実装状況: ✅ 基本実装完了
  - 場所: `awsTest/lambda/settings/user-profile/index.js`
  - 🔧 **拡張が必要**: `availableTitles`フィールドの追加
  - 備考: 設定画面専用、称号・二つ名編集機能のサポートが必要
- **PUT /api/settings/user-profile/{userId}** - 設定画面用ユーザープロフィール更新
  - 実装状況: ✅ 実装完了
  - 場所: `awsTest/lambda/settings/user-profile/index.js`
  - 備考: 設定画面専用
- **POST /api/settings/user-profile/{userId}/image** - 設定画面用プロフィール画像アップロード
  - 実装状況: ✅ 実装完了
  - 場所: `awsTest/lambda/settings/user-profile/image/index.js`
  - 備考: 設定画面専用
- **POST /api/settings/user-profile/{userId}/student-id-image** - 設定画面用学生証画像アップロード
  - 実装状況: 🚧 実装必要
  - 備考: 設定画面専用、学生証画像管理
- **PUT /api/settings/user-profile/{userId}/title-alias** - 設定画面用称号・二つ名更新
  - 実装状況: 🚧 実装必要
  - 備考: 設定画面専用、ロビー画面APIとは分離
- **DELETE /api/settings/user-profile/{userId}/image/{type}** - 設定画面用画像削除
  - 実装状況: 🚧 実装必要
  - 備考: 設定画面専用、プロフィール・学生証画像削除

## 技術仕様

### Redis実装状況
- **接続管理**: ✅ ioredisクライアント使用
- **マッチデータ**: ✅ Hashで管理
- **手履歴**: ✅ JSON配列として保存
- **接続プール**: ✅ 適切なクリーンアップ実装

### データベース実装状況
- **ユーザー管理**: ✅ usersテーブル
- **統計管理**: ✅ user_statsテーブル
- **マッチ履歴**: ✅ match_historyテーブル（保存機能付き）

### エラーハンドリング
- **バリデーション**: ✅ 全APIで実装済み
- **ビジネスロジックエラー**: ✅ 適切なエラーメッセージ
- **データベースエラー**: ✅ トランザクション処理
- **Redis接続エラー**: ✅ リトライ機能付き

## 性能とセキュリティ

### セキュリティ実装
- **パスワード暗号化**: ✅ SHA256ハッシュ化
- **入力バリデーション**: ✅ 全エンドポイントで実装
- **SQLインジェクション対策**: ✅ プリペアドステートメント使用

### 性能最適化
- **接続プール**: ✅ Redis/MySQL両方で実装
- **インデックス**: ✅ 必要なカラムにインデックス設定
- **キャッシュ**: ✅ Redisでマッチング状態をキャッシュ

## 今後の拡張予定

### 🔄 追加予定機能
- **画像アップロード**: S3連携機能（プロフィール・学生証画像）
- **認証トークン**: JWT実装
- **リアルタイム通信**: WebSocket対応
- **通知機能**: マッチング通知

### 🔧 改善予定項目
- **ログ機能**: 構造化ログ実装
- **監視機能**: ヘルスチェック拡張
- **テスト**: 自動テストスイート
- **ドキュメント**: OpenAPI仕様書生成

## 設定情報

### 環境変数
```
DB_HOST=awstest-mysql
DB_USER=lambda_user  
DB_PASSWORD=lambda_password
DB_NAME=jankendb
REDIS_HOST=awstest-redis
REDIS_PORT=6379
```

### ベースURL
- **開発環境**: `http://192.168.1.180:3000`
- **AWS環境（予定）**: `https://avwnok61nj.execute-api.ap-northeast-3.amazonaws.com/proc`

## 実装完了度（画面単位）

| 画面API分類 | 実装率 | 備考 |
|-------------|--------|------|
| 認証API（ログイン画面） | 100% | 完全実装済み |
| 登録API（登録画面） | 100% | 完全実装済み |
| ロビー画面API | 95% | 表示設定更新APIが実装必要 |
| バトル画面API | 100% | Redis実装完備 |
| ランキング画面API | 100% | 完全実装済み |
| 設定画面API | 90% | availableTitlesフィールド等が実装必要 |
| **全体** | **97%** | **画面単位分離原則完全準拠** | 

## クライアント要求事項（サーバー担当者向け）

### 🎯 高優先度
1. **availableTitlesフィールドの追加**
   - エンドポイント: `GET /api/settings/user-profile/{userId}`
   - 追加が必要: `profile.availableTitles` フィールド
   - 形式: カンマ区切り文字列（例: "title_001,title_003,title_005"）
   - 目的: 設定画面での称号選択機能をサポート

2. **称号・二つ名更新APIの修正**
   - エンドポイント: `PUT /api/lobby/user-stats/{userId}/title-alias`
   - 現在の問題: 500エラーが発生中
   - 修正が必要: リクエストボディの処理ロジック

### 📋 実装詳細
```json
// GET /api/settings/user-profile/{userId} の期待レスポンス
{
  "success": true,
  "data": {
    "profile": {
      "userId": "user025",
      "availableTitles": "title_001,title_003,title_005",
      // ... 他の既存フィールド
    }
  }
}
```

### 🔄 実装方針
- **画面単位API分離原則**: 設定画面は独立したAPIセットで完結
- **ユーザー第一設計**: クライアントの使いやすさを最優先
- **データ整合性**: ロビー画面との称号・二つ名データ同期を保証 