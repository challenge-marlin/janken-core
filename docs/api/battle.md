# バトル画面WebSocket API

バトル画面（マッチング〜対戦〜結果）で使用する専用WebSocket APIを定義します。他画面での使用は禁止します。

## 基本方針
- **リアルタイム通信**: WebSocketによる即座の状態変化通知
- **画面特化**: バトル画面のマッチング・対戦・結果表示に最適化
- **独立性**: 他画面のAPIに依存しない
- **完全性**: バトル画面で必要な全ての機能を提供

## WebSocket接続

### エンドポイント
```
ws://160.251.137.105/ws/battle/{userId}
```

### 接続パラメータ
- `userId`: ユーザーID（URLパス）
- `Authorization`: Bearer {jwt_token}（ヘッダー、認証が必要な場合）

### 接続確立
```json
// サーバーからの接続確認メッセージ
{
  "type": "connection_established",
  "data": {
    "userId": "string",
    "sessionId": "string",
    "status": "connected"
  },
  "timestamp": "2024-01-01T00:00:00Z",
  "success": true
}
```

## メッセージ仕様

### 1. マッチング開始

#### クライアント → サーバー
```json
{
  "type": "matching_start",
  "data": {
    "userId": "string"
  },
  "timestamp": "2024-01-01T00:00:00Z",
  "messageId": "uuid"
}
```

#### サーバー → クライアント（成功時）
```json
{
  "type": "matching_started",
  "data": {
    "matchingId": "string",
    "status": "waiting",
    "message": "マッチングを開始しました"
  },
  "timestamp": "2024-01-01T00:00:00Z",
  "success": true
}
```

### 2. マッチング状態更新（自動通知）

#### サーバー → クライアント
```json
{
  "type": "matching_status",
  "data": {
    "matchingId": "string",
    "status": "waiting",
    "queuePosition": 3,
    "estimatedWaitTime": 30
  },
  "timestamp": "2024-01-01T00:00:00Z",
  "success": true
}
```

### 3. マッチング成立

#### サーバー → クライアント
```json
{
  "type": "match_found",
  "data": {
    "matchingId": "string",
    "battleId": "string",
    "opponent": {
      "userId": "string",
      "nickname": "string",
      "profileImageUrl": "string"
    },
    "playerNumber": 1,
    "status": "matched",
    "message": "対戦相手が見つかりました"
  },
  "timestamp": "2024-01-01T00:00:00Z",
  "success": true
}
```

### 4. 対戦準備完了

#### クライアント → サーバー
```json
{
  "type": "battle_ready",
  "data": {
    "battleId": "string",
    "userId": "string"
  },
  "timestamp": "2024-01-01T00:00:00Z",
  "messageId": "uuid"
}
```

#### サーバー → クライアント（準備状態更新）
```json
{
  "type": "battle_ready_status",
  "data": {
    "battleId": "string",
    "player1Ready": true,
    "player2Ready": false,
    "status": "preparing",
    "message": "対戦準備中..."
  },
  "timestamp": "2024-01-01T00:00:00Z",
  "success": true
}
```

#### サーバー → クライアント（両者準備完了時）
```json
{
  "type": "battle_start",
  "data": {
    "battleId": "string",
    "status": "ready",
    "countdown": 3,
    "message": "対戦開始！手を選択してください"
  },
  "timestamp": "2024-01-01T00:00:00Z",
  "success": true
}
```

### 5. 手の送信

#### クライアント → サーバー
```json
{
  "type": "submit_hand",
  "data": {
    "battleId": "string",
    "userId": "string",
    "hand": "rock"
  },
  "timestamp": "2024-01-01T00:00:00Z",
  "messageId": "uuid"
}
```

#### 手の値
- `"rock"`: グー
- `"scissors"`: チョキ
- `"paper"`: パー

#### サーバー → クライアント（手送信確認）
```json
{
  "type": "hand_submitted",
  "data": {
    "battleId": "string",
    "status": "hand_submitted",
    "message": "手を送信しました",
    "waitingForOpponent": true
  },
  "timestamp": "2024-01-01T00:00:00Z",
  "success": true
}
```

### 6. 対戦結果（自動判定）

#### サーバー → クライアント（両者の手が揃った時）
```json
{
  "type": "battle_result",
  "data": {
    "battleId": "string",
    "result": {
      "player1": {
        "userId": "string",
        "hand": "rock",
        "result": "win"
      },
      "player2": {
        "userId": "string",
        "hand": "scissors",
        "result": "lose"
      },
      "winner": 1,
      "isDraw": false,
      "drawCount": 0,
      "isFinished": true
    },
    "status": "finished",
    "message": "対戦終了！"
  },
  "timestamp": "2024-01-01T00:00:00Z",
  "success": true
}
```

### 7. 引き分け時の手リセット

#### サーバー → クライアント（引き分け時）
```json
{
  "type": "battle_draw",
  "data": {
    "battleId": "string",
    "result": {
      "player1": {
        "userId": "string",
        "hand": "rock",
        "result": "draw"
      },
      "player2": {
        "userId": "string",
        "hand": "rock",
        "result": "draw"
      },
      "winner": 3,
      "isDraw": true,
      "drawCount": 1,
      "isFinished": false
    },
    "status": "draw",
    "message": "引き分けです！もう一度手を選択してください"
  },
  "timestamp": "2024-01-01T00:00:00Z",
  "success": true
}
```

#### クライアント → サーバー（手リセット要求）
```json
{
  "type": "reset_hands",
  "data": {
    "battleId": "string"
  },
  "timestamp": "2024-01-01T00:00:00Z",
  "messageId": "uuid"
}
```

#### サーバー → クライアント（手リセット完了）
```json
{
  "type": "hands_reset",
  "data": {
    "battleId": "string",
    "status": "ready",
    "message": "手をリセットしました。再度選択してください"
  },
  "timestamp": "2024-01-01T00:00:00Z",
  "success": true
}
```

### 8. 対戦辞退

#### クライアント → サーバー
```json
{
  "type": "battle_quit",
  "data": {
    "battleId": "string",
    "userId": "string",
    "reason": "user_action"
  },
  "timestamp": "2024-01-01T00:00:00Z",
  "messageId": "uuid"
}
```

#### サーバー → クライアント（辞退確認）
```json
{
  "type": "battle_quit_confirmed",
  "data": {
    "battleId": "string",
    "status": "cancelled",
    "message": "対戦を辞退しました"
  },
  "timestamp": "2024-01-01T00:00:00Z",
  "success": true
}
```

#### サーバー → 相手クライアント（相手辞退通知）
```json
{
  "type": "opponent_quit",
  "data": {
    "battleId": "string",
    "status": "cancelled",
    "message": "相手が対戦を辞退しました"
  },
  "timestamp": "2024-01-01T00:00:00Z",
  "success": true
}
```

## ステータス値一覧

- `waiting`: マッチング待機中
- `matched`: マッチング成立（準備待ち）
- `preparing`: 対戦準備中
- `ready`: 対戦準備完了（手選択待ち）
- `hand_submitted`: 手送信済み（相手待ち）
- `judging`: 結果判定中
- `draw`: 引き分け状態
- `finished`: 対戦終了
- `cancelled`: キャンセル・辞退

## エラーレスポンス

### WebSocketエラー形式
```json
{
  "type": "error",
  "data": {
    "originalType": "submit_hand",
    "originalData": {
      "battleId": "string",
      "userId": "string",
      "hand": "invalid_hand"
    }
  },
  "timestamp": "2024-01-01T00:00:00Z",
  "success": false,
  "error": {
    "code": "INVALID_HAND",
    "message": "無効な手が指定されました"
  }
}
```

### エラーコード一覧
- `INVALID_MESSAGE`: 無効なメッセージ形式
- `BATTLE_NOT_FOUND`: バトルが見つからない
- `PLAYER_NOT_IN_BATTLE`: プレイヤーがバトルに参加していない
- `INVALID_HAND`: 無効な手
- `INVALID_STATE`: 不正な状態での操作
- `ALREADY_SUBMITTED`: 既に手を送信済み
- `CONNECTION_ERROR`: 接続エラー
- `TIMEOUT`: タイムアウト
- `INTERNAL_ERROR`: サーバー内部エラー

## WebSocketフロー

### 1. マッチング〜対戦開始
```
1. WebSocket接続: ws://host/ws/battle/{userId}
2. 接続確立メッセージ受信: connection_established
3. マッチング開始: matching_start → matching_started
4. マッチング状況監視: matching_status（自動通知）
5. マッチング成立: match_found
6. 準備完了: battle_ready → battle_ready_status
7. 対戦開始: battle_start（両者準備完了時）
```

### 2. 対戦実行
```
1. 手送信: submit_hand → hand_submitted
2. 相手待ち: （相手の手送信を自動待機）
3. 結果判定: battle_result（自動実行）
```

### 3. 結果処理
```
・勝敗決定: battle_result → 接続切断
・引き分け: battle_draw → reset_hands → hands_reset → 手順2に戻る
・辞退: battle_quit → battle_quit_confirmed → 接続切断
```

## 実装ガイドライン

### クライアント側（Flutter）

#### WebSocket接続
```dart
import 'package:web_socket_channel/web_socket_channel.dart';

class BattleWebSocketService {
  static const String _baseWsUrl = 'ws://160.251.137.105/ws';
  WebSocketChannel? _channel;
  String? _userId;
  
  // WebSocket接続
  Future<void> connect(String userId) async {
    _userId = userId;
    _channel = WebSocketChannel.connect(
      Uri.parse('$_baseWsUrl/battle/$userId'),
    );
    
    // メッセージリスナー設定
    _channel!.stream.listen(
      (message) => _handleMessage(json.decode(message)),
      onError: (error) => _handleError(error),
      onDone: () => _handleDisconnected(),
    );
  }
  
  // メッセージ送信
  void _sendMessage(Map<String, dynamic> message) {
    message['timestamp'] = DateTime.now().toIso8601String();
    message['messageId'] = Uuid().v4();
    _channel?.sink.add(json.encode(message));
  }
  
  // マッチング開始
  void startMatching() {
    _sendMessage({
      'type': 'matching_start',
      'data': {
        'userId': _userId,
      },
    });
  }
  
  // 準備完了
  void setReady(String battleId) {
    _sendMessage({
      'type': 'battle_ready',
      'data': {
        'battleId': battleId,
        'userId': _userId,
      },
    });
  }
  
  // 手の送信
  void submitHand(String battleId, String hand) {
    _sendMessage({
      'type': 'submit_hand',
      'data': {
        'battleId': battleId,
        'userId': _userId,
        'hand': hand,
      },
    });
  }
  
  // 手のリセット
  void resetHands(String battleId) {
    _sendMessage({
      'type': 'reset_hands',
      'data': {
        'battleId': battleId,
      },
    });
  }
  
  // 対戦辞退
  void quitBattle(String battleId) {
    _sendMessage({
      'type': 'battle_quit',
      'data': {
        'battleId': battleId,
        'userId': _userId,
        'reason': 'user_action',
      },
    });
  }
  
  // メッセージハンドラー
  void _handleMessage(Map<String, dynamic> message) {
    final type = message['type'];
    final data = message['data'];
    
    switch (type) {
      case 'connection_established':
        _onConnectionEstablished(data);
        break;
      case 'matching_started':
        _onMatchingStarted(data);
        break;
      case 'matching_status':
        _onMatchingStatus(data);
        break;
      case 'match_found':
        _onMatchFound(data);
        break;
      case 'battle_ready_status':
        _onBattleReadyStatus(data);
        break;
      case 'battle_start':
        _onBattleStart(data);
        break;
      case 'hand_submitted':
        _onHandSubmitted(data);
        break;
      case 'battle_result':
        _onBattleResult(data);
        break;
      case 'battle_draw':
        _onBattleDraw(data);
        break;
      case 'hands_reset':
        _onHandsReset(data);
        break;
      case 'battle_quit_confirmed':
        _onBattleQuitConfirmed(data);
        break;
      case 'opponent_quit':
        _onOpponentQuit(data);
        break;
      case 'error':
        _onError(message);
        break;
    }
  }
  
  // 接続切断
  void disconnect() {
    _sendMessage({
      'type': 'disconnect',
      'data': {
        'reason': 'user_action',
      },
    });
    _channel?.sink.close();
    _channel = null;
  }
}
```

### サーバー側実装要件

#### FastAPI + WebSocket
```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import Dict, List
import json
import asyncio
from datetime import datetime

class BattleWebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_battles: Dict[str, str] = {}
        self.battles: Dict[str, Dict] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        
        # 接続確立メッセージ送信
        await self.send_message(user_id, {
            "type": "connection_established",
            "data": {
                "userId": user_id,
                "sessionId": f"session_{user_id}_{int(datetime.now().timestamp())}",
                "status": "connected"
            },
            "timestamp": datetime.now().isoformat(),
            "success": True
        })
    
    async def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        
        # バトル中の場合は相手に通知
        if user_id in self.user_battles:
            battle_id = self.user_battles[user_id]
            await self.handle_battle_quit(user_id, battle_id, "connection_lost")
    
    async def send_message(self, user_id: str, message: dict):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(json.dumps(message))
    
    async def handle_matching_start(self, user_id: str, data: dict):
        # マッチング処理実装
        pass
    
    async def handle_battle_ready(self, user_id: str, data: dict):
        # 準備完了処理実装
        pass
    
    async def handle_submit_hand(self, user_id: str, data: dict):
        # 手送信処理実装
        pass

app = FastAPI()
battle_manager = BattleWebSocketManager()

@app.websocket("/ws/battle/{user_id}")
async def websocket_battle_endpoint(websocket: WebSocket, user_id: str):
    await battle_manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            message_type = message.get("type")
            message_data = message.get("data", {})
            
            if message_type == "matching_start":
                await battle_manager.handle_matching_start(user_id, message_data)
            elif message_type == "battle_ready":
                await battle_manager.handle_battle_ready(user_id, message_data)
            elif message_type == "submit_hand":
                await battle_manager.handle_submit_hand(user_id, message_data)
            # 他のメッセージタイプも処理
            
    except WebSocketDisconnect:
        await battle_manager.disconnect(user_id)
```

## 接続管理とエラー処理

### 自動再接続
```dart
class BattleWebSocketService {
  int _reconnectAttempts = 0;
  static const int _maxReconnectAttempts = 3;
  static const Duration _reconnectDelay = Duration(seconds: 2);
  
  Future<void> _handleDisconnected() async {
    if (_reconnectAttempts < _maxReconnectAttempts) {
      _reconnectAttempts++;
      await Future.delayed(_reconnectDelay);
      await connect(_userId!);
    } else {
      _onConnectionFailed();
    }
  }
}
```

### ハートビート
```dart
Timer? _heartbeatTimer;

void _startHeartbeat() {
  _heartbeatTimer = Timer.periodic(Duration(seconds: 30), (timer) {
    _sendMessage({
      'type': 'ping',
      'data': {},
    });
  });
}
```

## REST API代替手段

WebSocket接続が利用できない場合の代替として、従来のREST APIも併用可能です：

- `GET /battle` - マッチング状態確認
- `POST /battle` - マッチング開始
- `POST /battle/ready` - 準備完了
- `POST /battle/hand` - 手の送信
- `POST /battle/judge` - 結果判定
- `POST /battle/quit` - 対戦辞退

ただし、リアルタイム性とパフォーマンスの観点から、WebSocketの使用を強く推奨します。

## 注意事項

### WebSocket使用時の重要な点
1. **接続管理**: 適切な接続・切断処理
2. **エラー処理**: 接続断・タイムアウトへの対応
3. **メッセージ順序**: 非同期メッセージの順序管理
4. **リソース管理**: メモリリーク防止
5. **セキュリティ**: 認証・認可の適切な実装

### 実装優先度
1. **必須**: 基本的なマッチング・対戦機能
2. **重要**: エラーハンドリング・再接続機能
3. **推奨**: ハートビート・接続状態監視
4. **オプション**: 高度な状態管理・ログ機能

この仕様により、ポーリングベースの従来方式から大幅にパフォーマンスが向上し、よりスムーズなリアルタイム対戦体験を提供できます。 