# 設定画面API

設定画面で使用する専用APIを定義します。他画面での使用は禁止します。

## 基本方針
- **画面特化**: 設定画面の表示・編集に最適化
- **独立性**: 他画面のAPIに依存しない
- **完全性**: 設定画面で必要な全ての機能を提供

## 1. 設定画面用ユーザー情報取得

### エンドポイント
```
GET /api/settings/user-profile/{userId}
```

### 用途
- 設定画面でのユーザー情報表示
- プロフィール編集フォームの初期値設定
- 称号・二つ名編集の現在値表示
- 各種設定項目の現在値表示

### リクエスト
- userId: パスパラメータ（ユーザーID）

### レスポンス（成功時）
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

### フィールド説明
- `userId`: ユーザーID
- `nickname`: ニックネーム
- `name`: 本名
- `email`: メールアドレス
- `profileImageUrl`: プロフィール画像URL
- `studentIdImageUrl`: 学生証画像URL
- `title`: 現在の称号
- `alias`: 現在の二つ名
- `availableTitles`: 利用可能な称号のカンマ区切り文字列（例: "title_001,title_003,title_005"）
- `university`: 大学名
- `postalCode`: 郵便番号
- `address`: 住所
- `phoneNumber`: 電話番号
- `isStudentIdEditable`: 学生証画像編集可能フラグ
- `showTitle`: 称号表示フラグ
- `showAlias`: 二つ名表示フラグ
- `createdAt`: 作成日時
- `updatedAt`: 更新日時

## 2. 設定画面用ユーザー情報更新

### エンドポイント
```
PUT /api/settings/user-profile/{userId}
```

### 用途
- 設定画面でのユーザー基本情報更新
- ニックネーム変更
- 連絡先情報更新
- 表示設定更新

### リクエスト
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

### レスポンス（成功時）
```json
{
  "success": true,
  "data": {
    "userId": "string",
    "updatedAt": "string"
  }
}
```

## 3. 設定画面用プロフィール画像アップロード

### エンドポイント
```
POST /api/settings/user-profile/{userId}/image
```

### 用途
- 設定画面でのプロフィール画像変更
- 画像の最適化処理
- URLの即座返却

### リクエスト
- Content-Type: multipart/form-data
- image: 画像ファイル（最大サイズ: 5MB）

### レスポンス（成功時）
```json
{
  "success": true,
  "data": {
    "profileImageUrl": "string"
  }
}
```

### 画像仕様
- **対応形式**: JPEG, PNG, GIF
- **最大サイズ**: 5MB
- **推奨サイズ**: 200x200px（正方形）
- **品質**: 80%（JPEG）

## 4. 設定画面用学生証画像アップロード

### エンドポイント
```
POST /api/settings/user-profile/{userId}/student-id-image
```

### 用途
- 設定画面での学生証画像アップロード
- 本人確認用画像の管理
- セキュリティ処理

### リクエスト
- Content-Type: multipart/form-data
- image: 画像ファイル（最大サイズ: 5MB）

### レスポンス（成功時）
```json
{
  "success": true,
  "data": {
    "studentIdImageUrl": "string"
  }
}
```

### 画像仕様
- **対応形式**: JPEG, PNG
- **最大サイズ**: 5MB
- **推奨サイズ**: 800px以上（幅）
- **品質**: 90%（JPEG）
- **アスペクト比**: 16:9 または 4:3

## 5. 設定画面用称号・二つ名更新

### エンドポイント
```
PUT /api/settings/user-profile/{userId}/title-alias
```

### 用途
- 設定画面での称号変更
- 設定画面での二つ名変更
- 利用可能称号の検証

### リクエスト
```json
{
  "title": "string",
  "alias": "string"
}
```

### レスポンス（成功時）
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

## 6. 設定画面用画像削除

### エンドポイント
```
DELETE /api/settings/user-profile/{userId}/image/{type}
```

### パラメータ
- userId: ユーザーID
- type: 画像タイプ（profile | student-id）

### 用途
- プロフィール画像の削除
- 学生証画像の削除
- デフォルト画像への復元

### レスポンス（成功時）
```json
{
  "success": true,
  "data": {
    "message": "画像を削除しました",
    "imageType": "string"
  }
}
```

## エラーレスポンス

### 共通エラー形式
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

### エラーコード一覧
- `INVALID_REQUEST`: リクエストが不正
- `USER_NOT_FOUND`: ユーザーが見つからない
- `IMAGE_TOO_LARGE`: 画像サイズが上限を超過
- `IMAGE_FORMAT_INVALID`: 画像形式が無効
- `TITLE_NOT_AVAILABLE`: 指定された称号が利用不可
- `STUDENT_ID_NOT_EDITABLE`: 学生証画像が編集不可
- `INTERNAL_ERROR`: サーバー内部エラー

## 実装ガイドライン

### クライアント側
```dart
class SettingsApiService {
  static const String _baseUrl = 'http://160.251.137.105';
  
  // 設定画面用ユーザー情報取得
  Future<Map<String, dynamic>> getUserProfile(String userId) async {
    final response = await http.get(
      Uri.parse('$_baseUrl/api/settings/user-profile/$userId'),
      headers: {'Content-Type': 'application/json'},
    );
    return json.decode(response.body);
  }
  
  // ユーザー情報更新
  Future<Map<String, dynamic>> updateUserProfile(
    String userId, 
    Map<String, dynamic> profileData
  ) async {
    final response = await http.put(
      Uri.parse('$_baseUrl/api/settings/user-profile/$userId'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode(profileData),
    );
    return json.decode(response.body);
  }
  
  // プロフィール画像アップロード
  Future<Map<String, dynamic>> uploadProfileImage(
    String userId, 
    Uint8List imageBytes
  ) async {
    final request = http.MultipartRequest(
      'POST',
      Uri.parse('$_baseUrl/api/settings/user-profile/$userId/image'),
    );
    request.files.add(
      http.MultipartFile.fromBytes('image', imageBytes, filename: 'profile.jpg'),
    );
    final response = await request.send();
    final responseString = await response.stream.bytesToString();
    return json.decode(responseString);
  }
  
  // 称号・二つ名更新
  Future<Map<String, dynamic>> updateTitleAndAlias(
    String userId, 
    String title, 
    String alias
  ) async {
    final response = await http.put(
      Uri.parse('$_baseUrl/api/settings/user-profile/$userId/title-alias'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({'title': title, 'alias': alias}),
    );
    return json.decode(response.body);
  }
}
```

### サーバー側実装要件
1. **独立性**: ロビー画面やその他画面のAPIロジックと分離
2. **最適化**: 設定画面に必要なデータのみを効率的に取得
3. **バリデーション**: 厳密な入力値検証
4. **セキュリティ**: 画像アップロード時のセキュリティチェック
5. **トランザクション**: 更新処理の整合性保証

## 注意事項
- **専用性**: このAPIは設定画面専用です
- **依存禁止**: ロビー画面やその他の画面からの使用は禁止
- **画像処理**: アップロード時の自動最適化処理
- **学生証画像**: セキュリティ要件に応じた特別な処理が必要
- **プライバシー**: 個人情報の適切な保護 