"""
バトル画面専用ビジネスロジック

WebSocketバトルの中核処理を実装
"""

import json
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime
from fastapi import WebSocket

from .models import (
    BattleManager, BattleSession, BattlePlayer, 
    battle_manager
)
from .schemas import (
    HandType, BattleStatus, ErrorCode,
    WebSocketMessage, WebSocketResponse,
    ConnectionEstablishedResponse, MatchingStartedResponse,
    MatchingStatusResponse, MatchFoundResponse,
    BattleReadyStatusResponse, BattleStartResponse,
    HandSubmittedResponse, BattleResultResponse,
    BattleDrawResponse, HandsResetResponse,
    BattleQuitConfirmedResponse, OpponentQuitResponse,
    ErrorResponse, OpponentInfo, PlayerInfo, BattleResult
)
from .database_service import battle_db_service
from ...shared.database.models_improved import ConnectionStatus


class BattleWebSocketService:
    """WebSocketバトルサービス"""
    
    def __init__(self, manager: BattleManager = battle_manager):
        self.manager = manager
    
    async def connect_user(self, websocket: WebSocket, user_id: str) -> bool:
        """ユーザー接続処理（DB連携版）"""
        try:
            await websocket.accept()
            
            # DB連携: ユーザー情報の検証
            user_info = await battle_db_service.get_user_info(user_id)
            if not user_info:
                await websocket.close(code=4001, reason="User not found or banned")
                return False
            
            # メモリ管理に追加
            self.manager.add_connection(user_id, websocket)
            
            # DB連携: WebSocket接続を登録
            connection_id = f"ws_{user_id}_{int(datetime.now().timestamp())}"
            await battle_db_service.register_websocket_connection(
                connection_id=connection_id,
                user_id=user_id,
                ip_address="127.0.0.1"  # TODO: 実際のIPアドレス取得
            )
            
            # 接続確立メッセージ送信
            response = ConnectionEstablishedResponse(
                data={
                    "userId": user_id,
                    "nickname": user_info.nickname,
                    "sessionId": connection_id,
                    "status": "connected"
                }
            )
            await self.send_message(user_id, response.dict())
            return True
            
        except Exception as e:
            print(f"Error connecting user {user_id}: {e}")
            return False
    
    async def disconnect_user(self, user_id: str):
        """ユーザー切断処理（DB連携版）"""
        try:
            # バトル中の場合は辞退処理
            battle = self.manager.get_user_battle(user_id)
            if battle:
                await self.handle_battle_quit(user_id, battle.battle_id, "connection_lost")
            
            # DB連携: WebSocket接続を削除
            await battle_db_service.unregister_websocket_connection(user_id)
            
            # メモリ管理から削除
            self.manager.remove_connection(user_id)
            
        except Exception as e:
            print(f"Error disconnecting user {user_id}: {e}")
    
    async def send_message(self, user_id: str, message: Dict[str, Any]) -> bool:
        """メッセージ送信"""
        try:
            websocket = self.manager.active_connections.get(user_id)
            if websocket:
                await websocket.send_text(json.dumps(message))
                return True
            return False
        except Exception as e:
            print(f"Error sending message to {user_id}: {e}")
            return False
    
    async def send_error(self, user_id: str, error_code: ErrorCode, message: str, original_data: Dict = None):
        """エラーメッセージ送信"""
        error_response = ErrorResponse(
            data={
                "originalType": original_data.get("type") if original_data else None,
                "originalData": original_data or {}
            },
            error={
                "code": error_code.value,
                "message": message
            }
        )
        await self.send_message(user_id, error_response.dict())
    
    async def handle_matching_start(self, user_id: str, data: Dict[str, Any]) -> bool:
        """マッチング開始処理"""
        try:
            # 既にバトル中またはマッチング中の場合はエラー
            if user_id in self.manager.user_battles or user_id in self.manager.matching_queue:
                await self.send_error(
                    user_id, 
                    ErrorCode.INVALID_STATE, 
                    "既にマッチング中またはバトル中です",
                    {"type": "matching_start", "data": data}
                )
                return False
            
            # DB連携: 実際のユーザー情報を取得
            user_info = await battle_db_service.get_user_info(user_id)
            if not user_info:
                await self.send_error(
                    user_id, 
                    ErrorCode.INTERNAL_ERROR, 
                    "ユーザー情報の取得に失敗しました"
                )
                return False
            
            # プレイヤー情報を作成
            player = BattlePlayer(
                user_id=user_id,
                nickname=user_info.nickname,
                profile_image_url=user_info.profile_image_url,
                connection_id=user_id,
                connected_at=datetime.now()
            )
            
            # DB連携: 接続状態を更新
            await battle_db_service.update_connection_status(
                user_id, ConnectionStatus.in_queue
            )
            
            # マッチングキューに追加
            matching = self.manager.add_to_matching_queue(user_id, player)
            
            # マッチング開始応答
            response = MatchingStartedResponse(
                data={
                    "matchingId": matching.matching_id,
                    "status": "waiting",
                    "message": "マッチングを開始しました"
                }
            )
            await self.send_message(user_id, response.dict())
            
            # マッチング状態更新
            await self.update_matching_status(user_id)
            
            # マッチング相手を探す
            await self.try_match_user(user_id)
            
            return True
            
        except Exception as e:
            await self.send_error(
                user_id, 
                ErrorCode.INTERNAL_ERROR, 
                f"マッチング開始エラー: {str(e)}"
            )
            return False
    
    async def try_match_user(self, user_id: str):
        """マッチング試行"""
        try:
            match_result = self.manager.find_match(user_id)
            if match_result:
                battle, opponent = match_result
                
                # DB連携: バトルセッションを作成
                await battle_db_service.create_battle_session(
                    battle.player1, battle.player2, battle.battle_id
                )
                
                # DB連携: 両プレイヤーの接続状態を更新
                await battle_db_service.update_connection_status(
                    battle.player1.user_id, ConnectionStatus.in_battle, battle.battle_id
                )
                await battle_db_service.update_connection_status(
                    battle.player2.user_id, ConnectionStatus.in_battle, battle.battle_id
                )
                
                # 両プレイヤーにマッチング成立通知
                for player in [battle.player1, battle.player2]:
                    if player:
                        opponent_info = battle.get_opponent(player.user_id)
                        response = MatchFoundResponse(
                            data={
                                "matchingId": f"match_{battle.battle_id}",
                                "battleId": battle.battle_id,
                                "opponent": {
                                    "userId": opponent_info.user_id,
                                    "nickname": opponent_info.nickname,
                                    "profileImageUrl": opponent_info.profile_image_url
                                },
                                "playerNumber": battle.get_player_number(player.user_id),
                                "status": "matched",
                                "message": "対戦相手が見つかりました"
                            }
                        )
                        await self.send_message(player.user_id, response.dict())
                        
        except Exception as e:
            print(f"Error in try_match_user: {e}")
    
    async def update_matching_status(self, user_id: str):
        """マッチング状態更新"""
        try:
            position = self.manager.get_queue_position(user_id)
            if position > 0:
                matching = self.manager.matching_queue.get(user_id)
                if matching:
                    response = MatchingStatusResponse(
                        data={
                            "matchingId": matching.matching_id,
                            "status": "waiting",
                            "queuePosition": position,
                            "estimatedWaitTime": position * 15  # 推定待ち時間（秒）
                        }
                    )
                    await self.send_message(user_id, response.dict())
                    
        except Exception as e:
            print(f"Error updating matching status: {e}")
    
    async def handle_battle_ready(self, user_id: str, data: Dict[str, Any]) -> bool:
        """対戦準備完了処理"""
        try:
            battle_id = data.get("battleId")
            if not battle_id:
                await self.send_error(user_id, ErrorCode.INVALID_MESSAGE, "battleIdが必要です")
                return False
            
            battle = self.manager.get_battle(battle_id)
            if not battle:
                await self.send_error(user_id, ErrorCode.BATTLE_NOT_FOUND, "バトルが見つかりません")
                return False
            
            player = battle.get_player(user_id)
            if not player:
                await self.send_error(user_id, ErrorCode.PLAYER_NOT_IN_BATTLE, "このバトルに参加していません")
                return False
            
            # プレイヤーを準備完了に設定
            player.is_ready = True
            battle.status = BattleStatus.preparing
            
            # DB連携: 準備状態を更新
            player1_ready = battle.player1.is_ready if battle.player1 else False
            player2_ready = battle.player2.is_ready if battle.player2 else False
            
            await battle_db_service.update_battle_status(
                battle_id, BattleStatus.preparing, player1_ready, player2_ready
            )
            
            # 準備状態を両プレイヤーに通知
            for p in [battle.player1, battle.player2]:
                if p:
                    response = BattleReadyStatusResponse(
                        data={
                            "battleId": battle_id,
                            "player1Ready": battle.player1.is_ready if battle.player1 else False,
                            "player2Ready": battle.player2.is_ready if battle.player2 else False,
                            "status": "preparing",
                            "message": "対戦準備中..."
                        }
                    )
                    await self.send_message(p.user_id, response.dict())
            
            # 両者準備完了の場合はバトル開始
            if battle.both_ready():
                await self.start_battle(battle_id)
            
            return True
            
        except Exception as e:
            await self.send_error(user_id, ErrorCode.INTERNAL_ERROR, f"準備完了エラー: {str(e)}")
            return False
    
    async def start_battle(self, battle_id: str):
        """バトル開始"""
        try:
            battle = self.manager.get_battle(battle_id)
            if not battle:
                return
            
            battle.status = BattleStatus.ready
            battle.started_at = datetime.now()
            
            # DB連携: バトル開始状態を更新
            await battle_db_service.update_battle_status(battle_id, BattleStatus.ready)
            
            # 両プレイヤーにバトル開始通知
            for player in [battle.player1, battle.player2]:
                if player:
                    response = BattleStartResponse(
                        data={
                            "battleId": battle_id,
                            "status": "ready",
                            "countdown": 3,
                            "message": "対戦開始！手を選択してください"
                        }
                    )
                    await self.send_message(player.user_id, response.dict())
                    
        except Exception as e:
            print(f"Error starting battle: {e}")
    
    async def handle_submit_hand(self, user_id: str, data: Dict[str, Any]) -> bool:
        """手送信処理"""
        try:
            battle_id = data.get("battleId")
            hand_str = data.get("hand")
            
            if not battle_id or not hand_str:
                await self.send_error(user_id, ErrorCode.INVALID_MESSAGE, "battleIdとhandが必要です")
                return False
            
            try:
                hand = HandType(hand_str)
            except ValueError:
                await self.send_error(user_id, ErrorCode.INVALID_HAND, "無効な手が指定されました")
                return False
            
            battle = self.manager.get_battle(battle_id)
            if not battle:
                await self.send_error(user_id, ErrorCode.BATTLE_NOT_FOUND, "バトルが見つかりません")
                return False
            
            player = battle.get_player(user_id)
            if not player:
                await self.send_error(user_id, ErrorCode.PLAYER_NOT_IN_BATTLE, "このバトルに参加していません")
                return False
            
            if player.hand is not None:
                await self.send_error(user_id, ErrorCode.ALREADY_SUBMITTED, "既に手を送信済みです")
                return False
            
            # 手を設定
            player.hand = hand
            battle.status = BattleStatus.hand_submitted
            
            # DB連携: 手をDBに記録
            await battle_db_service.submit_hand(battle_id, user_id, hand)
            
            # 手送信確認
            response = HandSubmittedResponse(
                data={
                    "battleId": battle_id,
                    "status": "hand_submitted",
                    "message": "手を送信しました",
                    "waitingForOpponent": not battle.both_submitted_hands()
                }
            )
            await self.send_message(user_id, response.dict())
            
            # 両者の手が揃った場合は結果判定
            if battle.both_submitted_hands():
                await self.judge_battle(battle_id)
            
            return True
            
        except Exception as e:
            await self.send_error(user_id, ErrorCode.INTERNAL_ERROR, f"手送信エラー: {str(e)}")
            return False
    
    async def judge_battle(self, battle_id: str):
        """バトル結果判定"""
        try:
            battle = self.manager.get_battle(battle_id)
            if not battle:
                return
            
            battle.status = BattleStatus.judging
            
            # 結果判定
            player1_result, player2_result, winner = battle.judge_battle()
            
            # 結果データ作成
            result_data = BattleResult(
                player1=PlayerInfo(
                    userId=battle.player1.user_id,
                    hand=battle.player1.hand,
                    result=player1_result
                ),
                player2=PlayerInfo(
                    userId=battle.player2.user_id,
                    hand=battle.player2.hand,
                    result=player2_result
                ),
                winner=winner,
                isDraw=(winner == 3),
                drawCount=battle.draw_count,
                isFinished=(winner != 3)
            )
            
            if winner == 3:  # 引き分け
                battle.status = BattleStatus.draw
                battle.draw_count += 1
                
                # 引き分け通知
                for player in [battle.player1, battle.player2]:
                    if player:
                        response = BattleDrawResponse(
                            data={
                                "battleId": battle_id,
                                "result": result_data.dict(),
                                "status": "draw",
                                "message": "引き分けです！もう一度手を選択してください"
                            }
                        )
                        await self.send_message(player.user_id, response.dict())
                
                # DB連携: 手をリセット
                await battle_db_service.reset_hands(battle_id)
                
                # 手をリセット
                battle.reset_hands()
                battle.status = BattleStatus.ready
                
            else:  # 勝敗決定
                battle.status = BattleStatus.finished
                result_data.isFinished = True
                
                # DB連携: 対戦結果を保存
                duration_seconds = int((datetime.now() - battle.started_at).total_seconds()) if battle.started_at else 60
                await battle_db_service.save_match_result(
                    battle_id, player1_result, player2_result, winner, duration_seconds
                )
                
                # DB連携: バトル完了状態を更新
                await battle_db_service.update_battle_status(battle_id, BattleStatus.finished)
                
                # 勝敗結果通知
                for player in [battle.player1, battle.player2]:
                    if player:
                        response = BattleResultResponse(
                            data={
                                "battleId": battle_id,
                                "result": result_data.dict(),
                                "status": "finished",
                                "message": "対戦終了！"
                            }
                        )
                        await self.send_message(player.user_id, response.dict())
                
                # バトル終了処理
                self.manager.finish_battle(battle_id)
                
        except Exception as e:
            print(f"Error judging battle: {e}")
    
    async def handle_reset_hands(self, user_id: str, data: Dict[str, Any]) -> bool:
        """手リセット処理"""
        try:
            battle_id = data.get("battleId")
            if not battle_id:
                await self.send_error(user_id, ErrorCode.INVALID_MESSAGE, "battleIdが必要です")
                return False
            
            battle = self.manager.get_battle(battle_id)
            if not battle:
                await self.send_error(user_id, ErrorCode.BATTLE_NOT_FOUND, "バトルが見つかりません")
                return False
            
            # DB連携: 手をリセット
            await battle_db_service.reset_hands(battle_id)
            
            # 手をリセット
            battle.reset_hands()
            battle.status = BattleStatus.ready
            
            # リセット完了通知
            for player in [battle.player1, battle.player2]:
                if player:
                    response = HandsResetResponse(
                        data={
                            "battleId": battle_id,
                            "status": "ready",
                            "message": "手をリセットしました。再度選択してください"
                        }
                    )
                    await self.send_message(player.user_id, response.dict())
            
            return True
            
        except Exception as e:
            await self.send_error(user_id, ErrorCode.INTERNAL_ERROR, f"手リセットエラー: {str(e)}")
            return False
    
    async def handle_battle_quit(self, user_id: str, battle_id: str, reason: str = "user_action") -> bool:
        """対戦辞退処理"""
        try:
            battle = self.manager.get_battle(battle_id)
            if not battle:
                return False
            
            battle.status = BattleStatus.cancelled
            
            # DB連携: バトルキャンセル状態を更新
            await battle_db_service.update_battle_status(battle_id, BattleStatus.cancelled)
            
            # 辞退確認を本人に送信
            quit_response = BattleQuitConfirmedResponse(
                data={
                    "battleId": battle_id,
                    "status": "cancelled",
                    "message": "対戦を辞退しました"
                }
            )
            await self.send_message(user_id, quit_response.dict())
            
            # 相手に辞退通知
            opponent = battle.get_opponent(user_id)
            if opponent:
                opponent_response = OpponentQuitResponse(
                    data={
                        "battleId": battle_id,
                        "status": "cancelled",
                        "message": "相手が対戦を辞退しました"
                    }
                )
                await self.send_message(opponent.user_id, opponent_response.dict())
            
            # バトル終了
            self.manager.finish_battle(battle_id)
            
            return True
            
        except Exception as e:
            print(f"Error handling battle quit: {e}")
            return False


# サービスインスタンス
battle_service = BattleWebSocketService()