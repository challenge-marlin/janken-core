# ランキング画面API

ランキング画面で使用する専用APIを定義します。他画面での使用は禁止します。

## 基本方針
- **画面特化**: ランキング画面の表示に最適化
- **独立性**: 他画面のAPIに依存しない
- **完全性**: ランキング画面で必要な全ての機能を提供

## ランキングデータ取得

### エンドポイント
```
GET /ranking
```

### 用途
- ランキング画面でのランキング表示
- ユーザーの順位確認
- ランク・勝利数の表示

### リクエストパラメータ
なし

### レスポンス（成功時）
```json
{
  "success": true,
  "rankings": [
    {
      "user_id": "string",           // ユーザーID
      "nickname": "string",          // ニックネーム
      "ranking_position": number,    // 順位
      "wins": number,               // 勝利数
      "rank": "string"              // ランク（bronze, silver, gold, platinum, diamond, master, grandmaster）
    }
  ]
}
```

### レスポンス（失敗時）
```json
{
  "success": false,
  "message": "ランキングデータの取得に失敗しました",
  "error": {
    "code": "RANKING_ERROR",
    "details": "エラー詳細（開発環境のみ）"
  }
}
```

### エラーケース
1. サーバーエラー
   - ステータスコード: 500
   - メッセージ: "ランキングデータの取得中にエラーが発生しました"

### 実装例

#### クライアント側（Flutter）
```dart
final response = await http.get(
  Uri.parse('$baseUrl/ranking'),
  headers: {
    'Content-Type': 'application/json',
  },
);

if (response.statusCode == 200) {
  final data = jsonDecode(response.body);
  if (data['success']) {
    // ランキングデータ取得成功時の処理
    final rankings = data['rankings'];
    // 画面表示など
  } else {
    // エラーメッセージの表示
    showErrorMessage(data['message']);
  }
}
```

#### サーバー側（Node.js）
```javascript
app.get('/dev/api/ranking', async (req, res) => {
  try {
    // ランキングデータの生成
    const rankings = await generateRankingWithUsername();
    
    // ランキングデータ取得成功
    res.json({
      success: true,
      rankings: rankings
    });
  } catch (error) {
    console.error('ランキングデータ取得エラー:', error);
    res.status(500).json({
      success: false,
      message: 'ランキングデータの取得中にエラーが発生しました'
    });
  }
});
```

## 注意事項

### 専用性
- **このAPIはランキング画面専用です**
- **他画面からの使用は禁止**

### データ更新頻度
- ランキングデータは定期的に更新されます
- リアルタイムの更新は行いません

### 表示制限
- クライアント側で表示するランキングは、ユーザーの位置を中心に前後50件を表示します
- ユーザーが見つからない場合は、トップ200を表示します

### パフォーマンス
- ランキングデータはキャッシュされ、高速なレスポンスを実現します
- 大量のリクエストに対しては、レート制限が適用される場合があります

### セキュリティ
- 認証は不要です
- ユーザーIDとニックネームのみを返し、機密情報は含まれません 