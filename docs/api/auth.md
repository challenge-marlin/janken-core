# 認証API

ログイン画面で使用する専用APIを定義します。他画面での使用は禁止します。

## 基本方針
- **画面特化**: ログイン画面の認証機能に最適化
- **独立性**: 他画面のAPIに依存しない
- **完全性**: ログイン画面で必要な全ての機能を提供

## ログイン

### エンドポイント
```
POST /UserInfo
```

### 用途
- ログイン画面でのユーザー認証
- 認証情報の検証
- ログイン成功時のユーザー情報取得

### リクエスト
```json
{
  "userId": "string",    // ユーザーID
  "password": "string"   // パスワード
}
```

### レスポンス（成功時）
```json
{
  "success": true,
  "user": {
    "user_id": "string",           // ユーザーID
    "nickname": "string",          // ニックネーム
    "title": "string",             // 称号
    "alias": "string",             // 二つ名
    "profile_image_url": "string"  // プロフィール画像URL
  }
}
```

### レスポンス（失敗時）
```json
{
  "success": false,
  "message": "ユーザーIDまたはパスワードが正しくありません",
  "error": {
    "code": "AUTH_ERROR",
    "details": "認証に失敗しました"
  }
}
```

### エラーケース
1. APIキー未設定
   - ステータスコード: 401
   - メッセージ: "APIキーが設定されていません"

2. 必須パラメータ不足
   - ステータスコード: 400
   - メッセージ: "ユーザーIDとパスワードは必須です"

3. 認証失敗
   - ステータスコード: 401
   - メッセージ: "ユーザーIDまたはパスワードが正しくありません"

4. レート制限超過
   - ステータスコード: 429
   - メッセージ: "リクエスト制限を超過しました"

5. サーバーエラー
   - ステータスコード: 500
   - メッセージ: "ログイン処理中にエラーが発生しました"

### セキュリティ要件
- パスワードはハッシュ化して保存
- HTTPS通信必須
- APIキーによる認証必須
- レート制限の適用

### 実装例

#### クライアント側（Flutter）
```dart
final response = await http.post(
  Uri.parse('$baseUrl/UserInfo'),
  headers: {
    'Content-Type': 'application/json',
    'x-api-key': apiKey,
  },
  body: jsonEncode({
    'userId': userId,
    'password': password,
  }),
);

if (response.statusCode == 200) {
  final data = jsonDecode(response.body);
  if (data['success']) {
    // ログイン成功時の処理
    final user = data['user'];
    // 画面遷移など
  } else {
    // エラーメッセージの表示
    showErrorMessage(data['message']);
  }
} else if (response.statusCode == 429) {
  // レート制限超過時の処理
  showRateLimitError();
}
```

#### サーバー側（Node.js）
```javascript
app.post('/dev/api/login', async (req, res) => {
  try {
    const { userId, password } = req.body;
    
    if (!userId || !password) {
      return res.status(400).json({
        success: false,
        message: 'ユーザーIDとパスワードは必須です'
      });
    }

    // ユーザー認証処理
    const user = await authenticateUser(userId, password);
    
    if (!user) {
      return res.status(401).json({
        success: false,
        message: 'ユーザーIDまたはパスワードが正しくありません'
      });
    }

    // ログイン成功
    res.json({
      success: true,
      user: {
        user_id: user.user_id,
        nickname: user.nickname,
        title: user.title,
        alias: user.alias,
        profile_image_url: user.profile_image_url
      }
    });
  } catch (error) {
    console.error('ログイン処理エラー:', error);
    res.status(500).json({
      success: false,
      message: 'ログイン処理中にエラーが発生しました'
    });
  }
});
``` 