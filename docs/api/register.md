# 登録画面API

登録画面で使用する専用APIを定義します。他画面での使用は禁止します。

## 基本方針
- **画面特化**: 登録画面のアカウント作成機能に最適化
- **独立性**: 他画面のAPIに依存しない
- **完全性**: 登録画面で必要な全ての機能を提供

## 概要
このドキュメントは、アカウント作成画面（register_page.dart）専用のAPI仕様を定義します。

---

## 1. ユーザーID重複チェックAPI

### エンドポイント
```
GET /check-userid?userId={userId}
```

### 用途
- 登録画面でのユーザーID重複チェック
- リアルタイム入力検証
- 登録前の事前確認

### 概要
指定したユーザーIDが利用可能かどうかを判定します。

### リクエスト
| パラメータ | 型     | 必須 | 説明           |
|------------|--------|------|----------------|
| userId     | string | ○    | チェック対象ID |

#### 例
```
GET /check-userid?userId=testuser
```

### レスポンス
| フィールド   | 型      | 説明                       |
|-------------|---------|----------------------------|
| available   | boolean | true:利用可, false:重複有  |
| success     | boolean | API処理成功                 |
| message     | string  | 補足メッセージ              |

#### 正常例
```json
{
  "success": true,
  "available": true,
  "message": "利用可能です"
}
```

#### 異常例
```json
{
  "success": true,
  "available": false,
  "message": "既に使用されています"
}
```

---

## 2. ユーザー登録API

### エンドポイント
```
POST /register
```

### 用途
- 登録画面での新規アカウント作成
- ユーザー情報の登録
- プロフィール・学生証画像のアップロード

### 概要
新規ユーザーアカウントを作成します。画像ファイルはmultipart/form-dataで送信します。

### リクエスト（multipart/form-data）
| フィールド         | 型      | 必須 | 説明                       |
|--------------------|---------|------|----------------------------|
| userId             | string  | ○    | ユーザーID（重複不可）     |
| email              | string  | ○    | メールアドレス             |
| password           | string  | ○    | パスワード                 |
| name               | string  | ○    | 氏名                       |
| nickname           | string  | ○    | ニックネーム               |
| postalCode         | string  | -    | 郵便番号                   |
| address            | string  | -    | 住所                       |
| phoneNumber        | string  | -    | 電話番号                   |
| university         | string  | -    | 学校名                     |
| birthdate          | string  | -    | 生年月日（YYYY-MM-DD）     |
| profileImage       | file    | -    | プロフィール画像（任意）   |
| studentIdImage     | file    | ○    | 学生証画像（必須）         |

#### 例
```
POST /register
Content-Type: multipart/form-data

userId=testuser
email=test@example.com
password=pass1234
name=山田太郎
nickname=たろう
profileImage=...（ファイル）
studentIdImage=...（ファイル）
```

### レスポンス
| フィールド   | 型      | 説明                       |
|-------------|---------|----------------------------|
| success     | boolean | 登録成功:true, 失敗:false  |
| message     | string  | 結果メッセージ              |
| user        | object  | 登録ユーザー情報（成功時）  |

#### 正常例
```json
{
  "success": true,
  "message": "登録が完了しました",
  "user": {
    "userId": "testuser",
    "nickname": "たろう",
    ...
  }
}
```

#### 異常例
```json
{
  "success": false,
  "message": "ユーザーIDが既に存在します"
}
```

---

## 3. バリデーション・注意事項
- ユーザーIDは事前に重複チェックを推奨
- パスワードは6文字以上
- メールアドレス形式チェックあり
- 学生証画像は必須
- プロフィール画像は任意
- レスポンスは共通仕様（success, message, error等）に準拠

---

## 4. 関連ファイル
- register_page.dart（Flutterクライアント）
- api_service.dart（API通信処理） 