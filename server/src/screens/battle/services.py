"""
バトル画面専用WebSocketサービス

リアルタイムじゃんけんバトル用WebSocket接続管理（Redis対応版）
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Union
from fastapi import WebSocket

from .models import (
    BattleManager, BattleSession, BattlePlayer, BattleStatus,
    HandType, MatchingQueue, battle_manager
)
from .schemas import (
    ConnectionEstablishedResponse, MatchingStartedResponse,
    MatchFoundResponse, BattleReadyStatusResponse,
    BattleStartResponse, HandSubmittedResponse,
    BattleResultResponse, BattleDrawResponse,
    BattleQuitConfirmedResponse, OpponentQuitResponse,
    ErrorResponse, ErrorCode, HandsResetResponse, PlayerInfo, BattleResult
)
from ...shared.services.redis_service import redis_service
from ...shared.database.connection import DatabaseSessionContext
from ...shared.database.models import User

class BattleWebSocketService:
    """WebSocketバトルサービス（Redis対応版）"""
    
    def __init__(self, manager: BattleManager = battle_manager):
        self.manager = manager
        self.logger = logging.getLogger(__name__)
    
    async def connect_user(self, websocket: WebSocket, user_id: str) -> bool:
        """ユーザー接続処理（Redis対応版）"""
        try:
            # WebSocketは既にrouterでacceptされているので、ここではacceptしない
            
            # DBからユーザー情報を取得（常にDB依存）
            user_info = await self._get_user_info_from_db(user_id)
            if not user_info:
                # DBにユーザーが見つからない場合は常にエラー
                self.logger.warning(f"ユーザー {user_id} がDBに見つかりません")
                error_response = {
                    "type": "error",
                    "data": {"code": "USER_NOT_FOUND", "message": "ユーザーが見つかりません"}
                }
                try:
                    await websocket.send_json(error_response)
                except Exception as e:
                    self.logger.error(f"エラーレスポンス送信失敗: {str(e)}")
                finally:
                    await websocket.close(code=4001, reason="User not found")
                return False

            # ユーザーの有効性をチェック
            if not user_info.get("is_active", True):
                self.logger.warning(f"ユーザー {user_id} は無効化されています")
                await websocket.send_json({
                    "type": "error",
                    "data": {"code": "USER_INACTIVE", "message": "アカウントが無効化されています"}
                })
                await websocket.close(code=4001, reason="User inactive")
                return False

            if user_info.get("is_banned", 0) > 0:
                self.logger.warning(f"ユーザー {user_id} はBANされています")
                await websocket.send_json({
                    "type": "error",
                    "data": {"code": "USER_BANNED", "message": "アカウントが制限されています"}
                })
                await websocket.close(code=4001, reason="User banned")
                return False

            # 必須フィールドのデフォルト値を設定
            if not user_info.get("nickname"):
                user_info["nickname"] = user_id  # ユーザーIDをニックネームとして使用

            if not user_info.get("profile_image_url"):
                user_info["profile_image_url"] = "https://lesson01.myou-kou.com/avatars/defaultAvatar1.png"
            
            # 既存の接続がある場合は、古い接続を適切に処理
            existing_connection = self.manager.active_connections.get(user_id)
            if existing_connection:
                self.logger.warning(f"既存の接続を検出: {user_id}。古い接続を適切に処理します。")
                try:
                    await existing_connection.close(code=1000, reason="New connection")
                except Exception as e:
                    self.logger.error(f"古い接続の閉じる際にエラー: {e}")
            
            # 接続管理に追加
            self.manager.add_connection(user_id, websocket)
            
            # Redisに接続状態を保存
            connection_data = {
                "user_id": user_id,
                "nickname": user_info["nickname"],
                "connected_at": datetime.now().isoformat(),
                "status": "connected"
            }
            await self._save_connection_state(user_id, connection_data)
            
            # 接続確立メッセージ送信（WebSocketが既にacceptされているので直接送信）
            response = ConnectionEstablishedResponse(
                data={
                    "userId": user_id,
                    "nickname": user_info["nickname"],
                    "sessionId": f"ws_{user_id}_{int(datetime.now().timestamp())}",
                    "status": "connected"
                }
            )
            await websocket.send_json(response.dict())
            
            self.logger.info(f"✅ ユーザー {user_id} の接続が確立されました")
            return True
            
        except Exception as e:
            self.logger.error(f"Error connecting user {user_id}: {e}")
            return False
    
    async def _save_connection_state(self, user_id: str, data: Dict[str, Any]):
        """Redisに接続状態を保存"""
        try:
            redis_service.set_battle_connection_state(user_id, data, 300)  # 5分TTL
        except Exception as e:
            self.logger.error(f"Redis接続状態保存エラー: {e}")
    
    async def _get_connection_state(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Redisから接続状態を取得"""
        try:
            return redis_service.get_battle_connection_state(user_id)
        except Exception as e:
            self.logger.error(f"Redis接続状態取得エラー: {e}")
            return None
    
    async def _get_user_info_from_db(self, user_id: str) -> Optional[Dict[str, Union[str, bool, int]]]:
        """既存のDBからユーザー情報を取得"""
        try:
            async with DatabaseSessionContext() as session:
                # ユーザーIDでユーザーを検索
                from sqlalchemy import select
                
                # user_idで検索
                stmt = select(User).where(User.user_id == user_id)
                result = await session.execute(stmt)
                user = result.scalar_one_or_none()
                
                if user:
                    return {
                        "user_id": user.user_id,
                        "nickname": user.nickname or user.user_id,
                        "profile_image_url": user.profile_image_url or "https://lesson01.myou-kou.com/avatars/defaultAvatar1.png",
                        "is_active": user.is_active,
                        "is_banned": user.is_banned
                    }

                return None
                
        except Exception as e:
            self.logger.error(f"DBからユーザー情報取得エラー: {e}")
            return None
    
    async def disconnect_user(self, user_id: str):
        """ユーザー切断処理（Redis対応版）"""
        try:
            # バトル中の場合は辞退処理
            battle = self.manager.get_user_battle(user_id)
            if battle:
                await self.handle_battle_quit(user_id, battle.battle_id, "connection_lost")
            
            # 接続管理から削除
            self.manager.remove_connection(user_id)
            
            # Redisから接続状態を削除
            await self._remove_connection_state(user_id)
            
        except Exception as e:
            self.logger.error(f"Error disconnecting user {user_id}: {e}")
    
    async def _remove_connection_state(self, user_id: str):
        """Redisから接続状態を削除"""
        try:
            redis_service.delete_battle_connection_state(user_id)
        except Exception as e:
            self.logger.error(f"Redis接続状態削除エラー: {e}")
    
    async def handle_connection_loss(self, user_id: str):
        """接続不安定時の処理（Redis対応版）"""
        try:
            # バトル中の場合は辞退処理
            battle = self.manager.get_user_battle(user_id)
            if battle:
                player = battle.get_player(user_id)
                if player and player.hand is not None:
                    # 手送信済みの場合は、接続のみを削除して辞退処理は実行しない
                    self.logger.warning(f"手送信済みユーザー {user_id} の接続が不安定。辞退処理を遅延します。")
                    self.manager.remove_connection(user_id)
                    return
                
                # 手送信前の場合は通常の辞退処理
                await self.handle_battle_quit(user_id, battle.battle_id, "connection_lost")
            
            # バトル中でない場合は通常の切断処理
            await self.disconnect_user(user_id)
            
        except Exception as e:
            self.logger.error(f"Error handling connection loss for user {user_id}: {e}")
            self.manager.remove_connection(user_id)
    
    async def send_message(self, user_id: str, message: Dict[str, Any]) -> bool:
        """メッセージ送信（Redis対応版）"""
        try:
            websocket = self.manager.active_connections.get(user_id)
            if websocket:
                await websocket.send_text(json.dumps(message))
                return True
            
            # WebSocket接続がない場合はRedisにメッセージを保存
            await self._save_offline_message(user_id, message)
            return False
        except Exception as e:
            self.logger.error(f"Error sending message to {user_id}: {e}")
            return False
    
    async def _save_offline_message(self, user_id: str, message: Dict[str, Any]):
        """オフラインメッセージをRedisに保存"""
        try:
            redis_service.push_offline_message(user_id, message, 3600)  # 1時間TTL
        except Exception as e:
            self.logger.error(f"Redisオフラインメッセージ保存エラー: {e}")
    
    async def get_offline_messages(self, user_id: str) -> list:
        """オフラインメッセージを取得"""
        try:
            return redis_service.get_offline_messages(user_id)
        except Exception as e:
            self.logger.error(f"Redisオフラインメッセージ取得エラー: {e}")
            return []
    
    async def send_error(self, user_id: str, error_code: ErrorCode, message: str, original_data: Dict = None):
        """エラーメッセージ送信"""
        response = ErrorResponse(
            error={
                "code": error_code,
                "message": message,
                "originalData": original_data
            }
        )
        await self.send_message(user_id, response.dict())
    
    async def handle_matching_start(self, user_id: str, data: Dict[str, Any]) -> bool:
        """マッチング開始処理（Redis対応版）"""
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
            
                        # DBからユーザー情報を取得（常にDB依存）
            user_info = await self._get_user_info_from_db(user_id)
            if not user_info:
                # DBにユーザーが見つからない場合は常にエラー
                self.logger.warning(f"ユーザー {user_id} がDBに見つかりません")
                await self.send_error(
                    user_id,
                    ErrorCode.USER_NOT_FOUND,
                    "ユーザーが見つかりません"
                )
                return False

            # ユーザーの有効性をチェック
            if not user_info.get("is_active", True):
                self.logger.warning(f"ユーザー {user_id} は無効化されています")
                await self.send_error(
                    user_id,
                    ErrorCode.USER_INACTIVE,
                    "アカウントが無効化されています"
                )
                return False

            if user_info.get("is_banned", 0) > 0:
                self.logger.warning(f"ユーザー {user_id} はBANされています")
                await self.send_error(
                    user_id,
                    ErrorCode.USER_BANNED,
                    "アカウントが制限されています"
                )
                return False

            # 必須フィールドのデフォルト値を設定
            if not user_info.get("nickname"):
                user_info["nickname"] = user_id  # ユーザーIDをニックネームとして使用

            if not user_info.get("profile_image_url"):
                user_info["profile_image_url"] = "https://lesson01.myou-kou.com/avatars/defaultAvatar1.png"
            
            # プレイヤー情報を作成
            player = BattlePlayer(
                user_id=user_id,
                nickname=user_info["nickname"],
                profile_image_url=user_info["profile_image_url"],
                connection_id=user_id,
                connected_at=datetime.now()
            )
            
            # マッチングキューに追加
            matching = self.manager.add_to_matching_queue(user_id, player)
            
            # Redisにマッチング状態を保存
            await self._save_matching_state(user_id, matching)
            
            # マッチング開始応答
            response = MatchingStartedResponse(
                data={
                    "matchingId": matching.matching_id,
                    "status": "waiting",
                    "message": "マッチングを開始しました"
                }
            )
            response_dict = response.dict()
            response_dict["timestamp"] = datetime.now().isoformat()
            response_dict["success"] = True
            await self.send_message(user_id, response_dict)
            
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
    
    async def _save_matching_state(self, user_id: str, matching: MatchingQueue):
        """Redisにマッチング状態を保存"""
        try:
            data = {
                "matching_id": matching.matching_id,
                "joined_at": matching.joined_at.isoformat(),
                "status": "waiting"
            }
            redis_service.set_battle_matching_state(user_id, data, 300)  # 5分TTL
        except Exception as e:
            self.logger.error(f"Redisマッチング状態保存エラー: {e}")
    
    async def try_match_user(self, user_id: str):
        """マッチング試行（Redis対応版）"""
        try:
            match_result = self.manager.find_match(user_id)
            if match_result:
                battle, opponent = match_result
                
                # Redisにバトル状態を保存
                await self._save_battle_state(battle)
                
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
                        response_dict = response.dict()
                        response_dict["timestamp"] = datetime.now().isoformat()
                        response_dict["success"] = True
                        await self.send_message(player.user_id, response_dict)
                        
        except Exception as e:
            self.logger.error(f"Error in try_match_user: {e}")
    
    async def _save_battle_state(self, battle: BattleSession):
        """Redisにバトル状態を保存"""
        try:
            data = {
                "battle_id": battle.battle_id,
                "status": battle.status.value,
                "player1": {
                    "user_id": battle.player1.user_id,
                    "nickname": battle.player1.nickname,
                    "is_ready": battle.player1.is_ready,
                    "hand": battle.player1.hand.value if battle.player1.hand else None
                } if battle.player1 else None,
                "player2": {
                    "user_id": battle.player2.user_id,
                    "nickname": battle.player2.nickname,
                    "is_ready": battle.player2.is_ready,
                    "hand": battle.player2.hand.value if battle.player2.hand else None
                } if battle.player2 else None,
                "created_at": battle.created_at.isoformat(),
                "started_at": battle.started_at.isoformat() if battle.started_at else None,
                "draw_count": battle.draw_count
            }
            redis_service.set_battle_session_state(battle.battle_id, data, 1800)  # 30分TTL
        except Exception as e:
            self.logger.error(f"Redisバトル状態保存エラー: {e}")
    
    async def update_matching_status(self, user_id: str):
        """マッチング状態更新（Redis対応版）"""
        try:
            position = self.manager.get_queue_position(user_id)
            if position > 0:
                matching = self.manager.matching_queue.get(user_id)
                if matching:
                                    response = {
                    "type": "matching_status",
                    "data": {
                        "matchingId": matching.matching_id,
                        "status": "waiting",
                        "queuePosition": position,
                        "estimatedWaitTime": position * 15  # 推定待ち時間（秒）
                    },
                    "timestamp": datetime.now().isoformat(),
                    "success": True
                }
                await self.send_message(user_id, response)
                    
        except Exception as e:
            self.logger.error(f"Error updating matching status: {e}")
    
    async def handle_battle_ready(self, user_id: str, data: Dict[str, Any]) -> bool:
        """対戦準備完了処理（Redis対応版）"""
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
            
            # Redisにバトル状態を更新
            await self._save_battle_state(battle)
            
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
                    response_dict = response.dict()
                    response_dict["timestamp"] = datetime.now().isoformat()
                    response_dict["success"] = True
                    await self.send_message(p.user_id, response_dict)
            
            # 両者準備完了の場合はバトル開始
            if battle.both_ready():
                await self.start_battle(battle_id)
            
            return True
            
        except Exception as e:
            await self.send_error(user_id, ErrorCode.INTERNAL_ERROR, f"準備完了エラー: {str(e)}")
            return False
    
    async def start_battle(self, battle_id: str):
        """バトル開始（Redis対応版）"""
        try:
            battle = self.manager.get_battle(battle_id)
            if not battle:
                return
            
            battle.status = BattleStatus.ready
            battle.started_at = datetime.now()
            
            # Redisにバトル状態を更新
            await self._save_battle_state(battle)
            
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
                    response_dict = response.dict()
                    response_dict["timestamp"] = datetime.now().isoformat()
                    response_dict["success"] = True
                    await self.send_message(player.user_id, response_dict)
                    
        except Exception as e:
            self.logger.error(f"Error starting battle: {e}")
    
    async def handle_submit_hand(self, user_id: str, data: Dict[str, Any]) -> bool:
        """手送信処理（Redis対応版）"""
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
            
            # Redisにバトル状態を更新
            await self._save_battle_state(battle)
            
            # 手送信確認
            response = HandSubmittedResponse(
                data={
                    "battleId": battle_id,
                    "status": "hand_submitted",
                    "message": "手を送信しました",
                    "waitingForOpponent": not battle.both_submitted_hands()
                }
            )
            response_dict = response.dict()
            response_dict["timestamp"] = datetime.now().isoformat()
            response_dict["success"] = True
            await self.send_message(user_id, response_dict)
            
            # 両者の手が揃った場合は結果判定
            if battle.both_submitted_hands():
                await self.judge_battle(battle_id)
            
            return True
            
        except Exception as e:
            await self.send_error(user_id, ErrorCode.INTERNAL_ERROR, f"手送信エラー: {str(e)}")
            return False
    
    async def judge_battle(self, battle_id: str):
        """バトル結果判定（Redis対応版）"""
        try:
            battle = self.manager.get_battle(battle_id)
            if not battle:
                return
            
            battle.status = BattleStatus.judging
            
            # 結果判定
            player1_result, player2_result, winner = battle.judge_battle()
            
            # 結果データ作成
            result_data = {
                "player1": {
                    "userId": battle.player1.user_id,
                    "hand": battle.player1.hand.value if battle.player1.hand else None,
                    "result": player1_result.value
                } if battle.player1 else None,
                "player2": {
                    "userId": battle.player2.user_id,
                    "hand": battle.player2.hand.value if battle.player2.hand else None,
                    "result": player2_result.value
                } if battle.player2 else None,
                "winner": winner,
                "isDraw": (winner == 3),
                "drawCount": battle.draw_count,
                "isFinished": (winner != 3)
            }
            
            if winner == 3:  # 引き分け
                battle.status = BattleStatus.draw
                battle.draw_count += 1
                
                # 引き分け通知
                for player in [battle.player1, battle.player2]:
                    if player:
                        response = BattleDrawResponse(
                            data={
                                "battleId": battle_id,
                                "result": result_data,
                                "status": "draw",
                                "message": "引き分けです！もう一度手を選択してください"
                            }
                        )
                        response_dict = response.dict()
                        response_dict["timestamp"] = datetime.now().isoformat()
                        response_dict["success"] = True
                        await self.send_message(player.user_id, response_dict)
                
                # 手をリセット
                battle.reset_hands()
                battle.status = BattleStatus.ready
                
                # Redisにバトル状態を更新
                await self._save_battle_state(battle)
                
            else:  # 勝敗決定
                battle.status = BattleStatus.finished
                result_data["isFinished"] = True
                
                # 勝敗結果通知
                for player in [battle.player1, battle.player2]:
                    if player:
                        response = BattleResultResponse(
                            data={
                                "battleId": battle_id,
                                "result": result_data,
                                "status": "finished",
                                "message": "対戦終了！"
                            }
                        )
                        response_dict = response.dict()
                        response_dict["timestamp"] = datetime.now().isoformat()
                        response_dict["success"] = True
                        await self.send_message(player.user_id, response_dict)
                
                # バトル終了処理
                self.manager.finish_battle(battle_id)
                
                # Redisからバトル状態を削除
                await self._remove_battle_state(battle_id)
                
        except Exception as e:
            self.logger.error(f"Error judging battle: {e}")
    
    async def _remove_battle_state(self, battle_id: str):
        """Redisからバトル状態を削除"""
        try:
            redis_service.delete_battle_session_state(battle_id)
        except Exception as e:
            self.logger.error(f"Redisバトル状態削除エラー: {e}")
    
    async def handle_reset_hands(self, user_id: str, data: Dict[str, Any]) -> bool:
        """手リセット処理（Redis対応版）"""
        try:
            battle_id = data.get("battleId")
            if not battle_id:
                await self.send_error(user_id, ErrorCode.INVALID_MESSAGE, "battleIdが必要です")
                return False
            
            battle = self.manager.get_battle(battle_id)
            if not battle:
                await self.send_error(user_id, ErrorCode.BATTLE_NOT_FOUND, "バトルが見つかりません")
                return False
            
            # 手をリセット
            battle.reset_hands()
            battle.status = BattleStatus.ready
            
            # Redisにバトル状態を更新
            await self._save_battle_state(battle)
            
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
                    response_dict = response.dict()
                    response_dict["timestamp"] = datetime.now().isoformat()
                    response_dict["success"] = True
                    await self.send_message(player.user_id, response_dict)
            
            return True
            
        except Exception as e:
            await self.send_error(user_id, ErrorCode.INTERNAL_ERROR, f"手リセットエラー: {str(e)}")
            return False
    
    async def handle_battle_quit(self, user_id: str, battle_id: str, reason: str = "user_action") -> bool:
        """対戦辞退処理（Redis対応版）"""
        try:
            battle = self.manager.get_battle(battle_id)
            if not battle:
                return False
            
            battle.status = BattleStatus.cancelled
            
            # Redisにバトル状態を更新
            await self._save_battle_state(battle)
            
            # 辞退確認を本人に送信
            quit_response = BattleQuitConfirmedResponse(
                data={
                    "battleId": battle_id,
                    "status": "cancelled",
                    "message": "対戦を辞退しました"
                }
            )
            response_dict = quit_response.dict()
            response_dict["timestamp"] = datetime.now().isoformat()
            response_dict["success"] = True
            await self.send_message(user_id, response_dict)
            
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
                response_dict = opponent_response.dict()
                response_dict["timestamp"] = datetime.now().isoformat()
                response_dict["success"] = True
                await self.send_message(opponent.user_id, response_dict)
            
            # バトル終了
            self.manager.finish_battle(battle_id)
            
            # Redisからバトル状態を削除
            await self._remove_battle_state(battle_id)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error handling battle quit: {e}")
            return False
    
    async def get_battle_stats(self, user_id: str) -> Dict[str, Any]:
        """バトル統計取得（Redis対応版）"""
        try:
            # Redisから統計情報を取得
            stats = redis_service.get_battle_stats(user_id)
            
            if stats:
                return stats
            
            # デフォルト統計
            default_stats = {
                "total_battles": 0,
                "wins": 0,
                "losses": 0,
                "draws": 0,
                "win_rate": 0.0
            }
            
            # Redisに保存
            redis_service.set_battle_stats(user_id, default_stats, 3600)  # 1時間TTL
            
            return default_stats
            
        except Exception as e:
            self.logger.error(f"Error getting battle stats: {e}")
            return {}
    
    async def update_battle_stats(self, user_id: str, result: str):
        """バトル統計更新（Redis対応版）"""
        try:
            stats = await self.get_battle_stats(user_id)
            
            stats["total_battles"] += 1
            if result == "win":
                stats["wins"] += 1
            elif result == "loss":
                stats["losses"] += 1
            elif result == "draw":
                stats["draws"] += 1
            
            # 勝率計算
            if stats["total_battles"] > 0:
                stats["win_rate"] = round(stats["wins"] / stats["total_battles"] * 100, 2)
            
            # Redisに保存
            redis_service.set_battle_stats(user_id, stats, 3600)  # 1時間TTL
            
        except Exception as e:
            self.logger.error(f"Error updating battle stats: {e}")
    
    async def cleanup_expired_data(self):
        """期限切れデータのクリーンアップ（Redis対応版）"""
        try:
            # Redisサービスのクリーンアップ機能を使用
            cleanup_results = redis_service.cleanup_battle_system_data()
            
            if "error" not in cleanup_results:
                self.logger.info(f"Redis期限切れデータのクリーンアップが完了しました: {cleanup_results}")
            else:
                self.logger.error(f"Redisクリーンアップエラー: {cleanup_results['error']}")
            
        except Exception as e:
            self.logger.error(f"Redisクリーンアップエラー: {e}")
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """システム統計取得（Redis対応版）"""
        try:
            return redis_service.get_battle_system_stats()
        except Exception as e:
            self.logger.error(f"システム統計取得エラー: {e}")
            return {"error": str(e)}


# サービスインスタンス
battle_service = BattleWebSocketService()


class BattleUserInfoService:
    """バトル画面専用ユーザー情報サービス"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def get_user_battle_info(self, user_id: str) -> Dict[str, Any]:
        """バトル画面用ユーザー情報取得"""
        try:
            # データベースからユーザー情報を取得
            from ...shared.database.connection import DatabaseSessionContext
            from ...shared.database.models import User, UserStats
            
            # セッションを直接取得
            session = db_connection.async_session_local()
            try:
                # ユーザー基本情報取得
                from sqlalchemy import select
                stmt = select(User).where(User.user_id == user_id)
                result = await session.execute(stmt)
                user = result.scalar_one_or_none()
                
                if not user:
                    raise ValueError(f"ユーザーが見つかりません: {user_id}")
                
                # ユーザー統計情報取得
                stmt = select(UserStats).where(UserStats.user_id == user_id)
                result = await session.execute(stmt)
                user_stats = result.scalar_one_or_none()
                
                # 基本情報
                user_info = {
                    "userId": user.user_id,
                    "nickname": user.nickname,
                    "profileImageUrl": user.profile_image_url,
                    "level": 1,  # デフォルト値
                    "experience": 0,  # デフォルト値
                    "rank": "bronze"  # デフォルト値
                }
                
                # 統計情報
                battle_stats = {
                    "totalBattles": 0,
                    "wins": 0,
                    "losses": 0,
                    "draws": 0,
                    "winRate": 0.0,
                    "currentStreak": 0,
                    "bestStreak": 0,
                    "rank": "bronze",
                    "level": 1,
                    "experience": 0,
                    "nextLevelExp": 200
                }
                
                if user_stats:
                    battle_stats.update({
                        "totalBattles": user_stats.total_matches or 0,
                        "wins": user_stats.total_wins or 0,
                        "losses": user_stats.total_losses or 0,
                        "draws": user_stats.total_draws or 0,
                        "winRate": float(user_stats.win_rate or 0.0),
                        "currentStreak": user_stats.current_streak or 0,
                        "bestStreak": user_stats.best_streak or 0,
                        "rank": user_stats.user_rank or "bronze",
                        "level": 1,  # レベル計算ロジックは後で実装
                        "experience": 0,  # 経験値計算ロジックは後で実装
                        "nextLevelExp": 200
                    })
                
                # ユーザー設定（デフォルト値）
                preferences = {
                    "autoMatching": True,
                    "soundEnabled": True,
                    "vibrationEnabled": False,
                    "theme": "dark"
                }
                
                return {
                    "user": user_info,
                    "battleStats": battle_stats,
                    "preferences": preferences
                }
                
            finally:
                await session.close()
                
        except Exception as e:
            self.logger.error(f"ユーザー情報取得エラー: {e}")
            raise
    
    async def get_user_battle_stats(self, user_id: str) -> Dict[str, Any]:
        """バトル画面用統計情報取得"""
        try:
            # データベースからユーザー統計情報を取得
            from ...shared.database.connection import DatabaseSessionContext
            from ...shared.database.models import User, UserStats
            
            # セッションを直接取得
            session = db_connection.async_session_local()
            try:
                # ユーザー基本情報取得
                from sqlalchemy import select
                stmt = select(User).where(User.user_id == user_id)
                result = await session.execute(stmt)
                user = result.scalar_one_or_none()
                
                if not user:
                    raise ValueError(f"ユーザーが見つかりません: {user_id}")
                
                # ユーザー統計情報取得
                stmt = select(UserStats).where(UserStats.user_id == user_id)
                result = await session.execute(stmt)
                user_stats = result.scalar_one_or_none()
                
                # バトル画面用の統計情報
                stats_info = {
                    "userId": user.user_id,
                    "nickname": user.nickname,
                    "totalBattles": 0,
                    "wins": 0,
                    "losses": 0,
                    "draws": 0,
                    "winRate": 0.0,
                    "currentStreak": 0,
                    "bestStreak": 0,
                    "rank": "bronze",
                    "level": 1,
                    "experience": 0,
                    "nextLevelExp": 200
                }
                
                if user_stats:
                    stats_info.update({
                        "totalBattles": user_stats.total_matches or 0,
                        "wins": user_stats.total_wins or 0,
                        "losses": user_stats.total_losses or 0,
                        "draws": user_stats.total_draws or 0,
                        "winRate": float(user_stats.win_rate or 0.0),
                        "currentStreak": user_stats.current_streak or 0,
                        "bestStreak": user_stats.best_streak or 0
                    })
                    
                    # レベル計算
                    total_exp = stats_info["wins"] * 10 + stats_info["losses"] * 2 + stats_info["draws"] * 5
                    stats_info["experience"] = total_exp
                    stats_info["level"] = (total_exp // 100) + 1
                    stats_info["nextLevelExp"] = (stats_info["level"] * 100)
                    
                    # ランク計算
                    if stats_info["winRate"] >= 80:
                        stats_info["rank"] = "diamond"
                    elif stats_info["winRate"] >= 70:
                        stats_info["rank"] = "platinum"
                    elif stats_info["winRate"] >= 60:
                        stats_info["rank"] = "gold"
                    elif stats_info["winRate"] >= 50:
                        stats_info["rank"] = "silver"
                    else:
                        stats_info["rank"] = "bronze"
                
                return stats_info
                
            finally:
                await session.close()
                
        except Exception as e:
            self.logger.error(f"バトル画面用統計情報取得エラー: {e}")
            raise
    
    async def get_user_battle_history(self, user_id: str, limit: int = 10) -> list:
        """バトル画面用戦歴取得"""
        try:
            # データベースから戦歴を取得
            from ...shared.database.connection import DatabaseSessionContext
            from ...shared.database.models import MatchHistory
            
            # セッションを直接取得
            session = db_connection.async_session_local()
            try:
                # 最近の戦歴を取得（MatchHistoryテーブルを使用）
                from sqlalchemy import select, desc
                stmt = select(MatchHistory).where(
                    MatchHistory.player1_id == user_id
                ).union(
                    select(MatchHistory).where(
                        MatchHistory.player2_id == user_id
                    )
                ).order_by(desc(MatchHistory.created_at)).limit(limit)
                
                result = await session.execute(stmt)
                battles = result.scalars().all()
                
                battle_history = []
                for battle in battles:
                    # プレイヤー1かプレイヤー2かを判定
                    is_player1 = battle.player1_id == user_id
                    opponent_id = battle.player2_id if is_player1 else battle.player1_id
                    
                    # 結果を判定
                    if battle.winner == 3:
                        result_text = "draw"
                    elif battle.winner == 1 and is_player1:
                        result_text = "win"
                    elif battle.winner == 2 and not is_player1:
                        result_text = "win"
                    else:
                        result_text = "lose"
                    
                    battle_history.append({
                        "battleId": str(battle.fight_no),
                        "opponent": opponent_id,
                        "result": result_text,
                        "timestamp": battle.created_at.isoformat()
                    })
                
                return battle_history
                
            finally:
                await session.close()
                
        except Exception as e:
            self.logger.error(f"バトル画面用戦歴取得エラー: {e}")
            return []

    async def get_opponent_info(self, battle_id: str, user_id: str) -> Dict[str, Any]:
        """バトル画面用対戦相手情報取得"""
        try:
            # バトル情報から対戦相手を特定
            battle = self.manager.get_battle(battle_id)
            if not battle:
                raise ValueError(f"バトルが見つかりません: {battle_id}")
            
            # 対戦相手のユーザーIDを取得
            opponent_id = None
            if battle.player1 and battle.player1.user_id == user_id:
                opponent_id = battle.player2.user_id if battle.player2 else None
            elif battle.player2 and battle.player2.user_id == user_id:
                opponent_id = battle.player1.user_id if battle.player1 else None
            
            if not opponent_id:
                raise ValueError("対戦相手が見つかりません")
            
            # 対戦相手の情報を取得
            from ...shared.database.connection import DatabaseSessionContext
            from ...shared.database.models import User, UserStats
            
            # セッションを直接取得
            session = db_connection.async_session_local()
            try:
                # 対戦相手の基本情報取得
                from sqlalchemy import select
                stmt = select(User).where(User.user_id == opponent_id)
                result = await session.execute(stmt)
                opponent = result.scalar_one_or_none()
                
                if not opponent:
                    raise ValueError(f"対戦相手の情報が見つかりません: {opponent_id}")
                
                # 対戦相手の統計情報取得
                stmt = select(UserStats).where(UserStats.user_id == opponent_id)
                result = await session.execute(stmt)
                opponent_stats = result.scalar_one_or_none()
                
                opponent_info = {
                    "userId": opponent.user_id,
                    "nickname": opponent.nickname,
                    "profileImageUrl": opponent.profile_image_url or "defaultAvatar.png",
                    "title": opponent.title or "称号未設定",
                    "alias": opponent.alias or "二つ名未設定",
                    "level": 1,
                    "rank": "bronze",
                    "battleStats": {
                        "totalBattles": 0,
                        "wins": 0,
                        "losses": 0,
                        "draws": 0,
                        "winRate": 0.0
                    }
                }
                
                if opponent_stats:
                    opponent_info["battleStats"].update({
                        "totalBattles": opponent_stats.total_matches or 0,
                        "wins": opponent_stats.total_wins or 0,
                        "losses": opponent_stats.total_losses or 0,
                        "draws": opponent_stats.total_draws or 0,
                        "winRate": float(opponent_stats.win_rate or 0.0)
                    })
                
                return opponent_info
                
            finally:
                await session.close()
                
        except Exception as e:
            self.logger.error(f"バトル画面用対戦相手情報取得エラー: {e}")
            raise


# バトル画面専用ユーザー情報サービスインスタンス
battle_user_info_service = BattleUserInfoService()
