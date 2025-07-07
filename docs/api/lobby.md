# ロビー画面API

ロビー画面で使用する専用APIを定義します。他画面での使用は禁止します。

## 基本方針
- **画面特化**: ロビー画面の表示・操作に最適化
- **独立性**: 他画面のAPIに依存しない
- **完全性**: ロビー画面で必要な全ての機能を提供

## 1. ロビー用ユーザー情報取得

### エンドポイント
```
GET /api/lobby/user-stats/{userId}
```

### 用途
- ロビー画面でのユーザー情報表示
- プロフィール表示
- 称号・二つ名の表示制御
- 戦績情報の表示

### リクエスト
- userId: パスパラメータ（ユーザーID）

### レスポンス（成功時）
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

### フィールド説明
- `userId`: ユーザーID
- `nickname`: ニックネーム（ロビー表示用）
- `profileImageUrl`: プロフィール画像URL（ロビー表示用）
- `showTitle`: 称号表示フラグ
- `showAlias`: 二つ名表示フラグ
- `winCount`: 勝利数
- `loseCount`: 敗北数
- `drawCount`: 引き分け数
- `totalMatches`: 総試合数
- `dailyWins`: 本日の勝利数
- `dailyRank`: 本日のランク
- `dailyRanking`: 本日の順位
- `recentHandResultsStr`: 最近の手履歴（カンマ区切り）
- `title`: 現在の称号
- `availableTitles`: 利用可能な称号リスト（カンマ区切り）
- `alias`: 現在の二つ名

## 2. 称号・二つ名更新

### エンドポイント
```
PUT /api/lobby/user-stats/{userId}/title-alias
```

### 用途
- ロビー画面での称号変更
- ロビー画面での二つ名変更
- 表示設定の即座反映

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
    "stats": {
      "userId": "string",
      "title": "string",
      "alias": "string",
      "updatedAt": "string"
    }
  }
}
```

## 3. ロビー表示設定更新

### エンドポイント
```
PUT /api/lobby/user-stats/{userId}/display
```

### 用途
- 称号表示ON/OFF設定
- 二つ名表示ON/OFF設定
- ロビー画面での即座反映

### リクエスト
```json
{
  "showTitle": boolean,
  "showAlias": boolean
}
```

### レスポンス（成功時）
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
- `TITLE_NOT_AVAILABLE`: 指定された称号が利用不可
- `INTERNAL_ERROR`: サーバー内部エラー

## 実装ガイドライン

### クライアント側
```dart
class LobbyApiService {
  static const String _baseUrl = 'http://160.251.137.105';
  
  // ロビー用ユーザー情報取得
  Future<Map<String, dynamic>> getUserStats(String userId) async {
    final response = await http.get(
      Uri.parse('$_baseUrl/api/lobby/user-stats/$userId'),
      headers: {'Content-Type': 'application/json'},
    );
    return json.decode(response.body);
  }
  
  // 称号・二つ名更新
  Future<Map<String, dynamic>> updateTitleAlias(
    String userId, 
    String title, 
    String alias
  ) async {
    final response = await http.put(
      Uri.parse('$_baseUrl/api/lobby/user-stats/$userId/title-alias'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({'title': title, 'alias': alias}),
    );
    return json.decode(response.body);
  }
  
  // 表示設定更新
  Future<Map<String, dynamic>> updateDisplaySettings(
    String userId, 
    bool showTitle, 
    bool showAlias
  ) async {
    final response = await http.put(
      Uri.parse('$_baseUrl/api/lobby/user-stats/$userId/display'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({'showTitle': showTitle, 'showAlias': showAlias}),
    );
    return json.decode(response.body);
  }
}
```

### サーバー側実装要件
1. **独立性**: 他画面のAPIロジックと分離
2. **最適化**: ロビー画面に必要なデータのみを効率的に取得
3. **リアルタイム**: 変更の即座反映
4. **キャッシュ**: 頻繁にアクセスされるデータのキャッシュ対応

## 注意事項
- **専用性**: このAPIはロビー画面専用です
- **依存禁止**: 設定画面やその他の画面からの使用は禁止
- **データ整合性**: ロビー専用でありながら、データの整合性は保証
- **性能**: ロビー画面の表示速度を最優先に最適化 