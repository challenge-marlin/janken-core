# バトル画面API

バトル画面（マッチング〜対戦〜結果）で使用する専用APIを定義します。他画面での使用は禁止します。

## 基本方針
- **画面特化**: バトル画面のマッチング・対戦・結果表示に最適化
- **独立性**: 他画面のAPIに依存しない
- **完全性**: バトル画面で必要な全ての機能を提供

## 1. マッチング開始

### エンドポイント
```
POST /battle
```

### 用途
- バトル画面でのマッチング開始
- 対戦相手の自動検索
- マッチング状態の初期化

### リクエスト
```json
{
  "userId": "string"
}
```

### レスポンス（成功時）
```json
{
  "success": true,
  "data": {
    "message": "マッチングを開始しました",
    "matchingId": "string",
    "status": "waiting"
  }
}
```

## 2. マッチング状態確認

### エンドポイント
```
GET /battle
```

### 用途
- バトル画面でのマッチング状態監視
- 対戦相手情報の取得
- 対戦準備状態の確認
- 結果判定状態の確認

### リクエストパラメータ
- userId: ユーザーID（クエリパラメータ）
- matchingId: マッチングID（クエリパラメータ、任意）

### レスポンス（成功時）
```json
{
  "success": true,
  "data": {
    "id": "string",
    "player1_id": "string",
    "player2_id": "string",
    "status": "string",
    "player1_ready": boolean,
    "player2_ready": boolean,
    "player1_hand": "string",
    "player2_hand": "string",
    "draw_count": number,
    "result": {
      "player1_result": "string",
      "player2_result": "string",
      "winner": number,
      "is_draw": boolean,
      "judged": boolean,
      "is_finished": boolean
    }
  }
}
```

### ステータス値
- `waiting`: マッチング待機中
- `matched`: マッチング成立（準備待ち）
- `ready`: 対戦準備完了
- `draw`: 引き分け状態
- `finished`: 対戦終了
- `cancelled`: キャンセル

## 3. 対戦準備完了

### エンドポイント
```
POST /battle/ready
```

### 用途
- バトル画面での準備完了通知
- 両プレイヤー準備状態の管理
- 対戦開始の同期

### リクエスト
```json
{
  "userId": "string",
  "matchingId": "string"
}
```

### レスポンス（成功時）
```json
{
  "success": true,
  "data": {
    "id": "string",
    "status": "string",
    "player1_ready": boolean,
    "player2_ready": boolean,
    "message": "string"
  }
}
```

## 4. 手の送信

### エンドポイント
```
POST /battle/hand
```

### 用途
- バトル画面での手（グー・チョキ・パー）送信
- 対戦手の記録
- 手出し完了状態の管理

### リクエスト
```json
{
  "userId": "string",
  "matchingId": "string",
  "hand": "string"
}
```

### 手の値
- `"rock"`: グー
- `"scissors"`: チョキ
- `"paper"`: パー

### レスポンス（成功時）
```json
{
  "success": true,
  "data": {
    "message": "手を送信しました",
    "status": "string"
  }
}
```

## 5. 結果判定

### エンドポイント
```
POST /battle/judge
```

### 用途
- バトル画面での結果判定実行
- 勝敗・引き分けの決定
- 対戦終了判定

### リクエスト
```json
{
  "matchingId": "string"
}
```

### レスポンス（成功時）
```json
{
  "success": true,
  "data": {
    "result": {
      "player1_hand": "string",
      "player2_hand": "string",
      "player1_result": "string",
      "player2_result": "string",
      "winner": number,
      "is_draw": boolean,
      "draw_count": number,
      "judged": boolean,
      "judged_at": "string",
      "is_finished": boolean
    }
  }
}
```

### 結果値
- `player1_result` / `player2_result`: `"win"` | `"lose"` | `"draw"`
- `winner`: `1` (プレイヤー1勝利) | `2` (プレイヤー2勝利) | `3` (引き分け)

## 6. 手のリセット

### エンドポイント
```
POST /battle/reset_hands
```

### 用途
- バトル画面での引き分け後の手リセット
- 次ラウンド準備
- 連続対戦サポート

### リクエスト
```json
{
  "matchingId": "string"
}
```

### レスポンス（成功時）
```json
{
  "success": true,
  "data": {
    "message": "手をリセットしました",
    "status": "ready"
  }
}
```

## 7. マッチ辞退

### エンドポイント
```
POST /battle/quit
```

### 用途
- バトル画面での対戦辞退
- マッチングキャンセル
- 対戦相手への通知

### リクエスト
```json
{
  "userId": "string",
  "matchingId": "string"
}
```

### レスポンス（成功時）
```json
{
  "success": true,
  "data": {
    "message": "マッチを辞退しました",
    "matchingId": "string",
    "status": "cancelled"
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
- `MATCH_NOT_FOUND`: マッチングが見つからない
- `PLAYER_NOT_FOUND`: プレイヤーが見つからない
- `INVALID_HAND`: 無効な手
- `INVALID_STATE`: 不正な状態での操作
- `ALREADY_MATCHED`: 既にマッチング中
- `INTERNAL_ERROR`: サーバー内部エラー

## バトル画面でのフロー

### 1. マッチング〜対戦開始
```
1. POST /battle (マッチング開始)
2. GET /battle (ポーリングで status: "matched" を待機)
3. POST /battle/ready (準備完了)
4. GET /battle (ポーリングで status: "ready" を待機)
```

### 2. 対戦実行
```
1. POST /battle/hand (手を送信)
2. GET /battle (相手の手を待機)
3. POST /battle/judge (両者の手が揃ったら結果判定)
4. GET /battle (結果を取得)
```

### 3. 結果処理
```
・引き分けの場合: POST /battle/reset_hands → 手順2に戻る
・勝敗決定の場合: ロビー画面に戻る
・辞退の場合: POST /battle/quit → ロビー画面に戻る
```

## 実装ガイドライン

### クライアント側
```dart
class BattleApiService {
  static const String _baseUrl = 'http://160.251.137.105';
  
  // マッチング開始
  Future<Map<String, dynamic>> startMatching(String userId) async {
    final response = await http.post(
      Uri.parse('$_baseUrl/battle'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({'userId': userId}),
    );
    return json.decode(response.body);
  }
  
  // マッチング状態確認
  Future<Map<String, dynamic>> getMatchStatus(String userId, [String? matchingId]) async {
    String url = '$_baseUrl/battle?userId=$userId';
    if (matchingId != null) {
      url += '&matchingId=$matchingId';
    }
    final response = await http.get(Uri.parse(url));
    return json.decode(response.body);
  }
  
  // 準備完了
  Future<Map<String, dynamic>> setReady(String userId, String matchingId) async {
    final response = await http.post(
      Uri.parse('$_baseUrl/battle/ready'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({'userId': userId, 'matchingId': matchingId}),
    );
    return json.decode(response.body);
  }
  
  // 手の送信
  Future<Map<String, dynamic>> submitHand(String userId, String matchingId, String hand) async {
    final response = await http.post(
      Uri.parse('$_baseUrl/battle/hand'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({'userId': userId, 'matchingId': matchingId, 'hand': hand}),
    );
    return json.decode(response.body);
  }
  
  // 結果判定
  Future<Map<String, dynamic>> judgeMatch(String matchingId) async {
    final response = await http.post(
      Uri.parse('$_baseUrl/battle/judge'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({'matchingId': matchingId}),
    );
    return json.decode(response.body);
  }
  
  // 手のリセット
  Future<Map<String, dynamic>> resetHands(String matchingId) async {
    final response = await http.post(
      Uri.parse('$_baseUrl/battle/reset_hands'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({'matchingId': matchingId}),
    );
    return json.decode(response.body);
  }
  
  // マッチ辞退
  Future<Map<String, dynamic>> quitMatch(String userId, String matchingId) async {
    final response = await http.post(
      Uri.parse('$_baseUrl/battle/quit'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({'userId': userId, 'matchingId': matchingId}),
    );
    return json.decode(response.body);
  }
}
```

### サーバー側実装要件
1. **独立性**: ロビー・設定画面のAPIロジックと分離
2. **リアルタイム**: Redis使用による高速な状態管理
3. **同期処理**: 両プレイヤーの状態同期
4. **エラー処理**: 接続断・タイムアウトへの対応

## 注意事項
- **専用性**: このAPIはバトル画面専用です
- **依存禁止**: ロビー・設定画面からの使用は禁止
- **状態管理**: Redis使用による一時的な状態管理
- **パフォーマンス**: リアルタイム性を重視した設計 