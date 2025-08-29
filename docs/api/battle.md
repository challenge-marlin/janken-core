# バトル画面WebSocket API

バトル画面（マッチング〜対戦〜結果）で使用する専用WebSocket APIを定義します。他画面での使用は禁止します。

## 基本方針
- **リアルタイム通信**: WebSocketによる即座の状態変化通知
- **画面特化**: バトル画面のマッチング・対戦・結果表示に最適化
- **独立性**: 他画面のAPIに依存しない
- **完全性**: バトル画面で必要な全ての機能を提供
- **セキュリティ**: JWTトークンによる認証必須
- **DB依存**: 常にデータベースからユーザー情報を取得

## WebSocket接続

### エンドポイント
```
# 開発環境
ws://192.168.0.150:3000/api/battle/ws/{userId}

# VPS環境
ws://160.251.137.105/api/battle/ws/{userId}

# AWS環境（予定）
wss://avwnok61nj.execute-api.ap-northeast-3.amazonaws.com/proc/api/battle/ws/{userId}
```

### 接続パラメータ
- `userId`: ユーザーID（URLパス）
  - 通常ユーザー: `user123`
  - テストユーザー: `test_user_1`, `test_user_2`, etc.

### 接続確立フロー

#### 1. WebSocket接続確立
```javascript
// クライアント側接続例
const ws = new WebSocket('ws://192.168.0.150:3000/api/battle/ws/test_user_1');
```

#### 2. 認証メッセージ送信（接続直後）
```json
// クライアント → サーバー（必須）
{
  "type": "auth",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  },
  "timestamp": "2024-01-01T07:29:44.685Z",
  "messageId": "34e263d4-a262-4ab6-b88a-ff1c452ccb7b"
}
```

#### 3. 認証成功レスポンス
```json
// サーバー → クライアント
{
  "type": "auth_success",
  "data": {
    "userId": "test_user_1",
    "message": "認証成功"
  },
  "timestamp": "2024-01-01T07:29:44.716Z",
  "success": true
}
```

#### 4. 接続確立完了
```json
// サーバー → クライアント
{
  "type": "connection_established",
  "data": {
    "userId": "test_user_1",
    "nickname": "テストユーザー1",
    "sessionId": "ws_test_user_1_1756452584",
    "status": "connected"
  },
  "timestamp": "2024-01-01T07:29:44.716Z",
  "success": true
}
```

## メッセージ仕様

### 共通メッセージ形式

すべてのメッセージは以下の形式に従います：

```json
{
  "type": "message_type",
  "data": {
    // メッセージ固有のデータ
  },
  "timestamp": "2024-01-01T07:29:44.685Z",
  "messageId": "uuid",  // クライアント→サーバーのみ
  "success": true       // サーバー→クライアントのみ
}
```

### 1. マッチング開始

#### クライアント → サーバー
```json
{
  "type": "matching_start",
  "data": {
    "userId": "test_user_1"
  },
  "timestamp": "2024-01-01T07:29:49.854Z",
  "messageId": "dd592cac-5c0e-4c25-8b30-d026fb0981bc"
}
```

#### サーバー → クライアント（成功時）
```json
{
  "type": "matching_started",
  "data": {
    "matchingId": "matching_test_user_1_1756452589",
    "status": "waiting",
    "message": "マッチングを開始しました"
  },
  "timestamp": "2024-01-01T07:29:49.858Z",
  "success": true
}
```

#### サーバー → クライアント（エラー時）
```json
{
  "type": "error",
  "data": {
    "originalType": "matching_start",
    "originalData": {
      "userId": "test_user_1"
    }
  },
  "timestamp": "2024-01-01T07:29:49.858Z",
  "success": false,
  "error": {
    "code": "ALREADY_IN_MATCHING",
    "message": "既にマッチング中またはバトル中です"
  }
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

### 9. ハートビート

#### クライアント → サーバー
```json
{
  "type": "ping",
  "data": {},
  "timestamp": "2024-01-01T00:00:00Z"
}
```

#### サーバー → クライアント
```json
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
- `INVALID_TOKEN`: 無効なトークン（JWT検証失敗）
- `USER_ID_MISMATCH`: ユーザーID不一致
- `USER_NOT_FOUND`: ユーザーがDBに見つからない
- `USER_INACTIVE`: アカウントが無効化されている
- `USER_BANNED`: アカウントが制限されている（BAN）
- `INVALID_STATE`: 不正な状態での操作（既にマッチング中など）
- `ALREADY_IN_MATCHING`: 既にマッチング中またはバトル中
- `BATTLE_NOT_FOUND`: バトルが見つからない
- `PLAYER_NOT_IN_BATTLE`: プレイヤーがバトルに参加していない
- `INVALID_HAND`: 無効な手
- `ALREADY_SUBMITTED`: 既に手を送信済み
- `CONNECTION_ERROR`: 接続エラー
- `TIMEOUT`: タイムアウト
- `INTERNAL_ERROR`: サーバー内部エラー

## WebSocketフロー

### 1. マッチング〜対戦開始
```
1. WebSocket接続: /api/battle/ws/{userId}
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

#### WebSocket接続（JavaScript実装例）
```javascript
class BattleWebSocketService {
  constructor() {
    this.ws = null;
    this.userId = null;
    this.jwtToken = null;
    this.isConnected = false;
  }
  
  // WebSocket接続
  connect(userId, jwtToken) {
    this.userId = userId;
    this.jwtToken = jwtToken;

    const wsUrl = `ws://192.168.0.150:3000/api/battle/ws/${userId}`;
    this.ws = new WebSocket(wsUrl);

    return new Promise((resolve, reject) => {
      this.ws.onopen = () => {
        console.log('[INFO] WebSocket接続確立');
        this.isConnected = true;

        // 接続直後に認証メッセージを送信
        this._sendAuthMessage().then(resolve).catch(reject);
      };

      this.ws.onmessage = (event) => {
        this._handleMessage(JSON.parse(event.data));
      };

      this.ws.onerror = (error) => {
        console.error('[ERROR] WebSocketエラー:', error);
        reject(error);
      };

      this.ws.onclose = (event) => {
        console.log(`[INFO] WebSocket切断: ${event.code} - ${event.reason}`);
        this.isConnected = false;
        this._handleDisconnected();
      };
    });
  }

  // 認証メッセージ送信（接続直後必須）
  async _sendAuthMessage() {
    const message = {
      type: 'auth',
      data: {
        token: this.jwtToken
      },
      timestamp: new Date().toISOString(),
      messageId: this._generateMessageId()
    };

    this.ws.send(JSON.stringify(message));
    console.log('[INFO] 認証メッセージ送信:', message);
  }
  
  // メッセージ送信
  _sendMessage(type, data) {
    const message = {
      type: type,
      data: data,
      timestamp: new Date().toISOString(),
      messageId: this._generateMessageId()
    };

    this.ws.send(JSON.stringify(message));
    console.log(`[INFO] 送信: ${type}`, message);
  }
  
  // マッチング開始
  startMatching() {
    this._sendMessage('matching_start', {
      userId: this.userId
    });
  }
  
  // 準備完了
  setReady(battleId) {
    this._sendMessage('battle_ready', {
      battleId: battleId,
      userId: this.userId
    });
  }
  
  // 手の送信
  submitHand(battleId, hand) {
    this._sendMessage('submit_hand', {
      battleId: battleId,
      userId: this.userId,
      hand: hand
    });
  }
  
  // 手のリセット
  resetHands(battleId) {
    this._sendMessage('reset_hands', {
      battleId: battleId
    });
  }
  
  // 対戦辞退
  quitBattle(battleId) {
    this._sendMessage('battle_quit', {
      battleId: battleId,
      userId: this.userId,
      reason: 'user_action'
    });
  }
  
  // メッセージハンドラー
  _handleMessage(message) {
    const { type, data, success } = message;

    console.log(`[INFO] 受信: ${type}`, message);
    
    switch (type) {
      case 'auth_success':
        console.log('[SUCCESS] 認証成功:', data.userId);
        break;

      case 'connection_established':
        console.log('[SUCCESS] 接続確立:', data.sessionId);
        break;

      case 'matching_started':
        console.log('[SUCCESS] マッチング開始:', data.matchingId);
        break;

      case 'matching_status':
        console.log('[INFO] マッチング状況:', data);
        break;

      case 'match_found':
        console.log('[SUCCESS] マッチング成立:', data.battleId);
        break;

      case 'battle_ready_status':
        console.log('[INFO] 準備状況:', data);
        break;

      case 'battle_start':
        console.log('[SUCCESS] 対戦開始');
        break;

      case 'hand_submitted':
        console.log('[INFO] 手送信完了');
        break;

      case 'battle_result':
        console.log('[SUCCESS] 対戦結果:', data.result);
        break;

      case 'battle_draw':
        console.log('[INFO] 引き分け');
        break;

      case 'hands_reset':
        console.log('[INFO] 手リセット完了');
        break;

      case 'error':
        console.error('[ERROR] エラー:', message.error);
        break;
    }
  }

  // ユーティリティメソッド
  _generateMessageId() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      const r = Math.random() * 16 | 0;
      const v = c == 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  }

  _handleDisconnected() {
    console.log('[INFO] WebSocket接続が切断されました');
    this.isConnected = false;
    // 再接続ロジックをここに実装
    }
  }
  
  // 接続切断
  disconnect() {
    if (this.ws && this.isConnected) {
      this._sendMessage('disconnect', {
        reason: 'user_action'
      });
      this.ws.close(1000, 'Normal closure');
    }
    this.ws = null;
    this.isConnected = false;
  }
}
```

### サーバー側実装要件

#### FastAPI + WebSocket（実際の実装例）
```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from typing import Dict, Any
import json
import asyncio
from datetime import datetime
from ...shared.services.jwt_service import JWTService
from ...shared.database.connection import get_db_session

class BattleWebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_battles: Dict[str, str] = {}
        self.matching_queue: List[str] = []
        self.battles: Dict[str, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        # WebSocket接続を確立
        await websocket.accept()
        self.active_connections[user_id] = websocket
        print(f"[INFO] User {user_id} connected to battle service")

    async def handle_auth(self, user_id: str, token: str) -> bool:
        """JWTトークン認証処理"""
        try:
            # JWTトークン検証
            payload = JWTService.verify_token(token)

            # ユーザーID一致確認
            if payload.get("user_id") != user_id:
                await self.send_error(user_id, "USER_ID_MISMATCH", "ユーザーIDが一致しません")
                return False

            # 認証成功メッセージ送信
            await self.send_message(user_id, {
                "type": "auth_success",
                "data": {"userId": user_id, "message": "認証成功"},
                "timestamp": datetime.now().isoformat(),
                "success": True
            })

            return True

        except Exception as e:
            print(f"[ERROR] JWT validation failed for user {user_id}: {str(e)}")
            await self.send_error(user_id, "INVALID_TOKEN", "無効なトークンです")
            return False

    async def handle_connection_established(self, user_id: str):
        """接続確立処理"""
        # DBからユーザー情報を取得（常にDB依存）
        user_info = await get_user_battle_info(user_id)
        if not user_info:
            # DBにユーザーが見つからない場合はエラー
            raise HTTPException(status_code=404, detail="ユーザーが見つかりません")

        # ユーザーの有効性をチェック
        if not user_info.get("is_active", True):
            raise HTTPException(status_code=403, detail="アカウントが無効化されています")

        if user_info.get("is_banned", 0) > 0:
            raise HTTPException(status_code=403, detail="アカウントが制限されています")

        # 必須フィールドのデフォルト値を設定
        nickname = user_info.get("nickname") or user_id
        profile_image_url = user_info.get("profile_image_url") or "https://lesson01.myou-kou.com/avatars/defaultAvatar1.png"

        session_id = f"ws_{user_id}_{int(datetime.now().timestamp())}"

        await self.send_message(user_id, {
            "type": "connection_established",
            "data": {
                "userId": user_id,
                "nickname": nickname,
                "profileImageUrl": profile_image_url,
                "sessionId": session_id,
                "status": "connected"
            },
            "timestamp": datetime.now().isoformat(),
            "success": True
        })
    
    async def handle_matching_start(self, user_id: str, data: Dict[str, Any]):
        """マッチング開始処理"""
        try:
            # 既にマッチング中またはバトル中の場合はエラー
            if user_id in self.matching_queue or user_id in self.user_battles:
                await self.send_error(user_id, "ALREADY_IN_MATCHING", "既にマッチング中またはバトル中です")
                return

            # マッチングキューに追加
            self.matching_queue.append(user_id)
            matching_id = f"matching_{user_id}_{int(datetime.now().timestamp())}"

            # マッチング開始成功メッセージ
            await self.send_message(user_id, {
                "type": "matching_started",
                "data": {
                    "matchingId": matching_id,
                    "status": "waiting",
                    "message": "マッチングを開始しました"
                },
                "timestamp": datetime.now().isoformat(),
                "success": True
            })

            print(f"[INFO] User {user_id} started matching: {matching_id}")

        except Exception as e:
            print(f"[ERROR] Error starting matching for {user_id}: {str(e)}")
            await self.send_error(user_id, "INTERNAL_ERROR", "マッチング開始に失敗しました")
    
    async def send_message(self, user_id: str, message: dict):
        """メッセージ送信"""
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_json(message)

    async def send_error(self, user_id: str, error_code: str, message: str):
        """エラーメッセージ送信"""
        await self.send_message(user_id, {
            "type": "error",
            "data": {
                "code": error_code,
                "message": message
            },
            "timestamp": datetime.now().isoformat(),
            "success": False
        })

    async def disconnect(self, user_id: str):
        """切断処理"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]

        # マッチングキューから削除
        if user_id in self.matching_queue:
            self.matching_queue.remove(user_id)

        # バトル中の場合はクリーンアップ
        if user_id in self.user_battles:
            battle_id = self.user_battles[user_id]
            # 相手に通知などの処理（未実装）
            del self.user_battles[user_id]

        print(f"[INFO] User {user_id} disconnected from battle service")

app = FastAPI()
battle_manager = BattleWebSocketManager()

@app.websocket("/api/battle/ws/{user_id}")
async def websocket_battle_endpoint(websocket: WebSocket, user_id: str):
    await battle_manager.connect(websocket, user_id)

    try:
        while True:
            # 最初のメッセージは認証メッセージであることを期待
            data = await websocket.receive_text()
            message = json.loads(data)
            message_type = message.get("type")

            if message_type == "auth":
                # 認証処理
                token = message.get("data", {}).get("token")
                if not token or not await battle_manager.handle_auth(user_id, token):
                    # 認証失敗時は接続を閉じる
                    await websocket.close(code=4001, reason="Authentication failed")
                    break

                # 認証成功時は接続確立メッセージを送信
                await battle_manager.handle_connection_established(user_id)

            else:
                # 認証前のメッセージは無効
                await battle_manager.send_error(user_id, "INVALID_MESSAGE", "認証が必要です")
                await websocket.close(code=4002, reason="Authentication required")
                break

            # 認証後のメッセージループ
            while True:
                data = await websocket.receive_text()
                message = json.loads(data)
            message_type = message.get("type")
            message_data = message.get("data", {})

                print(f"[DEBUG] Received message from {user_id}: {message}")
            
            if message_type == "matching_start":
                await battle_manager.handle_matching_start(user_id, message_data)
            elif message_type == "battle_ready":
                await battle_manager.handle_battle_ready(user_id, message_data)
            elif message_type == "submit_hand":
                await battle_manager.handle_submit_hand(user_id, message_data)
            # 他のメッセージタイプも処理
            
    except WebSocketDisconnect:
        await battle_manager.disconnect(user_id)
    except Exception as e:
        print(f"[ERROR] WebSocket error for {user_id}: {str(e)}")
        await battle_manager.disconnect(user_id)
```

## 接続管理とエラー処理

### 自動再接続（JavaScript実装例）
```javascript
class BattleWebSocketService {
  constructor() {
    // ... 既存のプロパティ ...
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 3;
    this.reconnectDelay = 2000; // 2秒
    this.reconnectTimer = null;
  }

  async _handleDisconnected() {
    console.log('[INFO] WebSocket接続が切断されました');

    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`[INFO] ${this.reconnectDelay}ms後に再接続を試行します (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

      this.reconnectTimer = setTimeout(async () => {
        try {
          await this.connect(this.userId, this.jwtToken);
          console.log('[SUCCESS] 再接続に成功しました');
          this.reconnectAttempts = 0; // 成功したらリセット
        } catch (error) {
          console.error('[ERROR] 再接続に失敗しました:', error);
          this._handleDisconnected(); // 再帰的に再試行
        }
      }, this.reconnectDelay);
    } else {
      console.error('[ERROR] 再接続試行回数を超えました');
      this._onConnectionFailed();
    }
  }

  _onConnectionFailed() {
    console.error('[ERROR] WebSocket接続に失敗しました');
    // UIに接続失敗を通知
    if (this.onConnectionFailed) {
      this.onConnectionFailed();
    }
  }

  disconnect() {
    // タイマーをクリア
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }

    // ... 既存の切断処理 ...
  }
}
```

### ハートビート（JavaScript実装例）
```javascript
class BattleWebSocketService {
  constructor() {
    // ... 既存のプロパティ ...
    this.heartbeatInterval = 30000; // 30秒
    this.heartbeatTimer = null;
    this.lastPongTime = null;
  }

  _startHeartbeat() {
    console.log('[INFO] ハートビートを開始します');

    this.heartbeatTimer = setInterval(() => {
      if (this.isConnected) {
        this.lastPongTime = Date.now();
        this._sendMessage('ping', {});
      }
    }, this.heartbeatInterval);
  }

  _stopHeartbeat() {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }

  // メッセージハンドラーにpong処理を追加
  _handleMessage(message) {
    const { type, data } = message;

    switch (type) {
      case 'pong':
        const latency = Date.now() - this.lastPongTime;
        console.log(`[INFO] ハートビート応答: ${latency}ms`);
        break;
      // ... 他のメッセージ処理 ...
    }
  }
}
```

## バトル画面専用ユーザー情報API

画面単位API分離原則に従い、バトル画面で必要なユーザー情報を取得する専用APIを定義します。

### エンドポイント
```
# 開発環境
GET http://192.168.0.150:3000/api/battle/user-info/{userId}

# VPS環境
GET http://160.251.137.105/api/battle/user-info/{userId}

# AWS環境（予定）
GET https://avwnok61nj.execute-api.ap-northeast-3.amazonaws.com/proc/api/battle/user-info/{userId}
```

### リクエスト
```http
GET /api/battle/user-info/{userId}
Authorization: Bearer {jwt_token}
Content-Type: application/json
```

### レスポンス
```json
{
  "success": true,
  "data": {
    "user": {
      "userId": "string",
      "nickname": "string",
      "profileImageUrl": "string",
      "level": 1,
      "experience": 150,
      "rank": "bronze"
    },
    "battleStats": {
      "totalBattles": 42,
      "wins": 28,
      "losses": 12,
      "draws": 2,
      "winRate": 66.7,
      "currentStreak": 3,
      "bestStreak": 8
    },
    "preferences": {
      "autoMatching": true,
      "soundEnabled": true,
      "vibrationEnabled": false,
      "theme": "dark"
    }
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### エラーレスポンス
```json
{
  "success": false,
  "error": {
    "code": "USER_NOT_FOUND",
    "message": "ユーザーが見つかりません"
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### エラーコード一覧
- `USER_NOT_FOUND`: ユーザーが存在しない
- `UNAUTHORIZED`: 認証が必要
- `FORBIDDEN`: アクセス権限がない
- `INTERNAL_ERROR`: サーバー内部エラー

## バトル画面専用統計情報API

バトル画面で表示する統計情報を取得する専用APIも定義します。

### エンドポイント
```
GET /api/battle/user-stats/{userId}
```

### レスポンス
```json
{
  "success": true,
  "data": {
    "stats": {
      "userId": "string",
      "nickname": "string",
      "totalBattles": 42,
      "wins": 28,
      "losses": 12,
      "draws": 2,
      "winRate": 66.7,
      "currentStreak": 3,
      "bestStreak": 8,
      "rank": "bronze",
      "level": 1,
      "experience": 150,
      "nextLevelExp": 200
    },
    "recentBattles": [
      {
        "battleId": "string",
        "opponent": "string",
        "result": "win",
        "timestamp": "2024-01-01T00:00:00Z"
      }
    ],
    "achievements": [
      {
        "id": "string",
        "name": "初勝利",
        "description": "初めての勝利を達成",
        "unlockedAt": "2024-01-01T00:00:00Z"
      }
    ]
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## 実装ガイドライン

### クライアント側（Flutter）

#### バトル画面専用APIサービス
```dart
class BattleApiService {
  static const String baseUrl = 'http://192.168.0.150:3000';
  
  /// バトル画面用ユーザー情報取得
  static Future<Map<String, dynamic>> getUserInfo(String userId) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/battle/user-info/$userId'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ${await _getAuthToken()}',
        },
      );
      
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw HttpException('ユーザー情報取得失敗: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('ユーザー情報取得エラー: $e');
    }
  }
  
  /// バトル画面用統計情報取得
  static Future<Map<String, dynamic>> getUserStats(String userId) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/battle/user-stats/$userId'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ${await _getAuthToken()}',
        },
      );
      
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw HttpException('統計情報取得失敗: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('統計情報取得エラー: $e');
    }
  }
}
```

#### マッチング画面での使用例
```dart
class MatchingPage extends StatefulWidget {
  // ... 既存コード ...
  
  @override
  void initState() {
    super.initState();
    
    // バトル画面専用APIを使用
    _userDataFuture = Future.wait([
      BattleApiService.getUserInfo(widget.userId),
      BattleApiService.getUserStats(widget.userId),
    ]).then((results) => {
      'user': results[0]['data']['user'],
      'userStats': results[1]['data']['stats'],
    });
    
    // ... 既存コード ...
  }
}
```

### サーバー側実装要件

#### FastAPI実装例
```python
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from datetime import datetime

router = APIRouter(prefix="/api/battle")

@router.get("/user-info/{user_id}")
async def get_battle_user_info(
    user_id: str,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """バトル画面用ユーザー情報取得"""
    try:
        user_info = await get_user_battle_info(user_id)
        return {
            "success": True,
            "data": user_info,
            "timestamp": datetime.now().isoformat()
        }
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりません")

@router.get("/user-stats/{user_id}")
async def get_battle_user_stats(
    user_id: str,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """バトル画面用統計情報取得"""
    try:
        user_stats = await get_user_battle_stats(user_id)
        return {
            "success": True,
            "data": user_stats,
            "timestamp": datetime.now().isoformat()
        }
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりません")
```

## REST API代替手段

WebSocket接続が利用できない場合の代替として、従来のREST APIも併用可能です：

- `GET /api/battle` - マッチング状態確認
- `POST /api/battle` - マッチング開始
- `POST /api/battle/ready` - 準備完了
- `POST /api/battle/hand` - 手の送信
- `POST /api/battle/judge` - 結果判定
- `POST /api/battle/quit` - 対戦辞退

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

### 現在の実装状況

#### ✅ 実装済み機能
- **WebSocket通信基盤**
  - ✅ WebSocketエンドポイント: `/api/battle/ws/{userId}`
  - ✅ JWT認証システム（トークン検証・ユーザー認証）
  - ✅ DB依存ユーザー管理（常にDBから取得・有効性チェック）
  - ✅ 接続管理（accept/reject・切断処理・再接続対応）

- **リアルタイム対戦機能**
  - ✅ マッチング開始処理（キュー管理・状態管理）
  - ✅ マッチング成立処理（対戦相手マッチング）
  - ✅ バトル実行処理（手送信・結果判定）
  - ✅ マッチング状況自動通知
  - ✅ バトル準備・開始フロー
  - ✅ 対戦結果判定・通知

- **Redis統合（複数プロセス対応）**
  - ✅ 接続状態管理（`battle:connection:{user_id}`）
  - ✅ マッチング状態管理（`battle:matching:{user_id}`）
  - ✅ セッション状態管理（`battle:session:{battle_id}`）
  - ✅ 統計データ管理（`battle:stats:{user_id}`）
  - ✅ オフラインメッセージ（`battle:offline_messages:{user_id}`）
  - ✅ システム統計監視（メモリ使用量・キー数・接続数）
  - ✅ 自動クリーンアップ（期限切れデータ削除）

- **セキュリティ・エラーハンドリング**
  - ✅ エラーハンドリング（詳細なエラーコード・メッセージ）
  - ✅ 認証フロー（WebSocket接続後authメッセージ送信）
  - ✅ ユーザー状態検証（is_active, is_bannedチェック）
  - ✅ Magic Linkトークン管理（Redis TTL管理）

#### 🔄 未実装機能（今後の拡張）
- **DB永続化レイヤー**
  - 🔄 バトル結果DB保存（battle_resultsテーブル）
  - 🔄 バトル詳細DB保存（battle_roundsテーブル）
  - 🔄 ユーザー統計DB更新（user_statsテーブル）
  - 🔄 ランキング計算・更新

- **高度な機能**
  - 🔄 引き分け時の手リセット機能
  - 🔄 詳細な対戦辞退処理
  - 🔄 リアルタイム統計情報
  - 🔄 チャット・通知機能

- **運用・監視**
  - 🔄 パフォーマンス監視（Redisメトリクス統合）
  - 🔄 ログ集約・分析
  - 🔄 スケーラビリティ対応（Redisクラスタ）

この仕様により、ポーリングベースの従来方式から大幅にパフォーマンスが向上し、よりスムーズなリアルタイム対戦体験を提供できます。 

## テスト手順

### 1. 環境準備
```bash
# Dockerコンテナ起動
cd server
docker-compose up -d

# ブラウザでテストページを開く
# http://192.168.0.150:3000/main-html/battle/index.html
```

### 2. WebSocket接続テスト
```javascript
// コンソールログで以下の順序で確認
[INFO] WebSocket接続試行: ws://192.168.0.150:3000/api/battle/ws/test_user_1
[INFO] WebSocket接続確立
[INFO] 認証メッセージ送信 {type: 'auth', data: {…}}
[INFO] 受信: auth_success {type: 'auth_success', data: {…}}
[SUCCESS] 認証成功: test_user_1
[INFO] 受信: connection_established {type: 'connection_established', data: {…}}
[SUCCESS] 接続確立: ws_test_user_1_1756452584
```

### 3. マッチング開始テスト
```javascript
// マッチング開始ボタンをクリック
[INFO] 送信: matching_start {type: 'matching_start', data: {…}}
[INFO] 受信: matching_started {type: 'matching_started', data: {…}}
[SUCCESS] マッチング開始: matching_test_user_1_1756452589
```

### 4. エラーテスト
```javascript
// 同じユーザーで再度マッチング開始
[INFO] 送信: matching_start {type: 'matching_start', data: {…}}
[ERROR] エラー: ALREADY_IN_MATCHING - 既にマッチング中またはバトル中です
```

### 5. サーバーログ確認
```bash
# Dockerコンテナのログを確認
docker-compose logs -f api

# 期待されるログ出力
INFO: User test_user_1 connected to battle service
DEBUG: Received message from test_user_1: {"type":"matching_start",...}
INFO: User test_user_1 started matching: matching_test_user_1_1756452589
```

### 6. 複数ユーザー同時テスト
1. 新しいブラウザタブ/ウィンドウを開く
2. テストユーザー2としてログイン・接続
3. 両方のユーザーがマッチングを開始すると対戦が成立

### 注意点
- **ブラウザキャッシュ**: テスト前にキャッシュをクリアすること
- **開発環境**: 192.168.0.150 のIPアドレスは環境に合わせて変更
- **DBセットアップ**: **必須** - テスト前にユーザー情報をDBに登録しておくこと
- **ユーザー登録**: テストユーザーはDBのusersテーブルに登録する必要あり
- **JWTトークン**: ログインAPIから取得した有効なトークンを使用
- **エラーハンドリング**: ユーザーがDBにいない場合は即座にエラーになる

### テスト用ユーザー登録SQL
```sql
-- テストユーザーの登録例
INSERT INTO users (
    user_id, email, nickname, profile_image_url, is_active, is_banned
) VALUES (
    'test_user_1',
    'test1@example.com',
    'テストユーザー1',
    'https://lesson01.myou-kou.com/avatars/defaultAvatar1.png',
    TRUE,
    0
);

INSERT INTO users (
    user_id, email, nickname, profile_image_url, is_active, is_banned
) VALUES (
    'test_user_2',
    'test2@example.com',
    'テストユーザー2',
    'https://lesson01.myou-kou.com/avatars/defaultAvatar2.png',
    TRUE,
    0
);
```