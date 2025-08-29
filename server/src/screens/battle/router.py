"""
バトル画面専用WebSocketルーター

リアルタイムじゃんけんバトル用WebSocketエンドポイント
"""

import json
from typing import Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import logging
from datetime import datetime
from urllib.parse import urlparse, parse_qs

from .services import battle_service, battle_user_info_service
from .models import battle_manager
from ...shared.services.redis_service import redis_service


# バトル専用ルーター
router = APIRouter(
    prefix="/api/battle",
    tags=["バトル画面WebSocket"],
    responses={
        404: {"description": "バトルが見つかりません"},
        400: {"description": "リクエストエラー"}
    }
)


@router.websocket("/ws/{user_id}")
async def websocket_battle_endpoint(websocket: WebSocket, user_id: str):
    """
    バトル画面WebSocketエンドポイント

    リアルタイムじゃんけんバトル用のWebSocket接続を処理
    """
    logger = logging.getLogger(__name__)
    logger.info(f"WebSocket connection attempt for user: {user_id}")

    # WebSocket接続を受け入れる
    await websocket.accept()
    logger.info("WebSocket connection accepted")

    # 最初のメッセージで認証情報を待つ
    try:
        # 最初のメッセージ（認証）を待つ
        auth_message = await websocket.receive_json()
        logger.info(f"Received auth message: {auth_message}")

        # 認証メッセージの検証
        if auth_message.get("type") != "auth":
            logger.error("First message must be auth type")
            await websocket.send_json({
                "type": "error",
                "data": {"code": "INVALID_AUTH_FORMAT", "message": "最初のメッセージは認証である必要があります"}
            })
            await websocket.close(code=4001, reason="Invalid auth format")
            return

        auth_data = auth_message.get("data", {})
        token = auth_data.get("token")

        if not token:
            logger.error("Missing token in auth message")
            await websocket.send_json({
                "type": "error",
                "data": {"code": "MISSING_AUTH_DATA", "message": "トークンがありません"}
            })
            await websocket.close(code=4001, reason="Missing auth data")
            return

        # JWTトークンの検証
        try:
            logger.info(f"Verifying JWT token for user: {user_id}")
            logger.info(f"Token length: {len(token)} characters")
            logger.info(f"Token preview: {token[:50]}...")

            from ...shared.services.jwt_service import jwt_service
            token_payload = jwt_service.verify_token(token)

            logger.info("Token verification successful")
            logger.info(f"Token payload keys: {list(token_payload.keys())}")

            # トークン内のユーザーIDとURLパラメータのユーザーIDを比較
            token_user_id = token_payload.get("user_id")
            logger.info(f"Token user_id: {token_user_id}")
            logger.info(f"URL user_id: {user_id}")

            if token_user_id != user_id:
                logger.error(f"Token user_id mismatch: '{token_user_id}' != '{user_id}'")
                await websocket.send_json({
                    "type": "error",
                    "data": {"code": "USER_ID_MISMATCH", "message": "ユーザーIDが一致しません"}
                })
                await websocket.close(code=4003, reason="User ID mismatch")
                return

            logger.info(f"JWT token verified for user: {user_id}")

            # 認証成功のレスポンス
            await websocket.send_json({
                "type": "auth_success",
                "data": {
                    "user_id": user_id,
                    "nickname": token_payload.get("nickname"),
                    "message": "認証成功"
                }
            })

        except Exception as jwt_error:
            logger.error(f"JWT validation failed for user {user_id}: {jwt_error}")
            logger.error(f"Token content: {token[:50]}...")
            await websocket.send_json({
                "type": "error",
                "data": {"code": "INVALID_TOKEN", "message": f"無効なトークンです: {str(jwt_error)}"}
            })
            await websocket.close(code=4002, reason="Invalid token")
            return

    except Exception as e:
        logger.error(f"Auth message processing error: {e}")
        await websocket.close(code=4001, reason="Auth processing failed")
        return

    # 認証成功後にバトルサービスに接続
    connected = await battle_service.connect_user(websocket, user_id)
    if not connected:
        logger.error(f"Failed to connect user: {user_id}")
        # connect_user内で既にエラーメッセージが送信されているので、ここでは何もしない
        return

    logger.info(f"User {user_id} connected successfully to battle service")

    try:
        while True:
            # メッセージ受信
            data = await websocket.receive_text()
            logger.debug(f"Received message from {user_id}: {data}")

            try:
                message = json.loads(data)
                await handle_websocket_message(user_id, message)

            except json.JSONDecodeError:
                logger.error(f"Invalid JSON from user {user_id}: {data}")
                await battle_service.send_error(
                    user_id,
                    "INVALID_MESSAGE",
                    "無効なJSONメッセージです"
                )
            except Exception as e:
                logger.error(f"Error handling message from {user_id}: {e}")
                await battle_service.send_error(
                    user_id,
                    "INTERNAL_ERROR",
                    f"メッセージ処理エラー: {str(e)}"
                )

    except WebSocketDisconnect:
        logger.info(f"User {user_id} disconnected")
        # 接続不安定時の処理を改善
        await battle_service.handle_connection_loss(user_id)
    except Exception as e:
        logger.error(f"Unexpected error for user {user_id}: {e}")
        # 予期しないエラー時の処理を改善
        await battle_service.handle_connection_loss(user_id)


async def handle_websocket_message(user_id: str, message: Dict[str, Any]):
    """
    WebSocketメッセージハンドラー
    
    Args:
        user_id: ユーザーID
        message: 受信メッセージ
    """
    message_type = message.get("type")
    message_data = message.get("data", {})
    
    handlers = {
        "matching_start": battle_service.handle_matching_start,
        "battle_ready": battle_service.handle_battle_ready,
        "submit_hand": battle_service.handle_submit_hand,
        "reset_hands": battle_service.handle_reset_hands,
        "battle_quit": lambda uid, data: battle_service.handle_battle_quit(
            uid, data.get("battleId", ""), data.get("reason", "user_action")
        ),
        "ping": handle_ping,
        "disconnect": lambda uid, data: battle_service.handle_connection_loss(uid)
    }
    
    handler = handlers.get(message_type)
    if handler:
        await handler(user_id, message_data)
    else:
        await battle_service.send_error(
            user_id,
            "INVALID_MESSAGE",
            f"未知のメッセージタイプ: {message_type}"
        )


async def handle_ping(user_id: str, data: Dict[str, Any]):
    """ハートビート処理"""
    pong_message = {
        "type": "pong",
        "data": {
            "userId": user_id,
            "timestamp": data.get("timestamp", "")
        },
        "success": True
    }
    await battle_service.send_message(user_id, pong_message)


# REST API エンドポイント（WebSocket補完用）
@router.get("/")
async def get_battle_system_info():
    """
    バトル全体情報取得
    
    システム状態の監視用エンドポイント
    """
    try:
        # Redisの状態も確認
        redis_status = "healthy" if redis_service.ping() else "unhealthy"
        
        return {
            "success": True,
            "data": {
                "activeConnections": battle_manager.get_active_connections_count(),
                "activeBattles": battle_manager.get_active_battles_count(),
                "queueCount": battle_manager.get_queue_count(),
                "redisStatus": redis_status,
                "message": "バトルWebSocketサービスが稼働中です（Redis対応版）"
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": {
                "message": f"システム状態取得エラー: {str(e)}",
                "code": "SYSTEM_ERROR"
            }
        }


@router.get("/status/{user_id}")
async def get_user_battle_status(user_id: str):
    """
    ユーザーのバトル状態取得
    
    Args:
        user_id: ユーザーID
    """
    battle = battle_manager.get_user_battle(user_id)
    is_in_queue = user_id in battle_manager.matching_queue
    is_connected = user_id in battle_manager.active_connections
    
    if battle:
        status_data = {
            "status": "in_battle",
            "battleId": battle.battle_id,
            "battleStatus": battle.status.value,
            "playerNumber": battle.get_player_number(user_id),
            "opponent": None
        }
        
        opponent = battle.get_opponent(user_id)
        if opponent:
            status_data["opponent"] = {
                "userId": opponent.user_id,
                "nickname": opponent.nickname,
                "profileImageUrl": opponent.profile_image_url
            }
            
    elif is_in_queue:
        matching = battle_manager.matching_queue[user_id]
        status_data = {
            "status": "matching",
            "matchingId": matching.matching_id,
            "queuePosition": battle_manager.get_queue_position(user_id),
            "joinedAt": matching.joined_at.isoformat()
        }
    else:
        status_data = {
            "status": "idle",
            "message": "バトル・マッチング待機中ではありません"
        }
    
    return {
        "success": True,
        "data": {
            "userId": user_id,
            "connected": is_connected,
            **status_data
        }
    }


@router.post("/debug/reset-user/{user_id}")
async def debug_reset_user(user_id: str):
    """
    デバッグ用：ユーザー状態リセット
    
    開発時のデバッグ用エンドポイント
    """
    # マッチングキューから削除
    battle_manager.matching_queue.pop(user_id, None)
    
    # バトルから削除
    battle_id = battle_manager.user_battles.pop(user_id, None)
    if battle_id and battle_id in battle_manager.active_battles:
        battle = battle_manager.active_battles[battle_id]
        battle.status = "cancelled"
        battle_manager.finish_battle(battle_id)
    
    # 接続も削除
    battle_manager.active_connections.pop(user_id, None)
    
    return {
        "success": True,
        "data": {
            "userId": user_id,
            "message": "ユーザー状態をリセットしました"
        }
    }


@router.get("/debug/stats")
async def debug_get_stats():
    """
    デバッグ用：システム統計取得
    """
    return {
        "success": True,
        "data": {
            "activeConnections": list(battle_manager.active_connections.keys()),
            "activeBattles": {
                bid: {
                    "battleId": battle.battle_id,
                    "status": battle.status.value,
                    "player1": battle.player1.user_id if battle.player1 else None,
                    "player2": battle.player2.user_id if battle.player2 else None,
                    "drawCount": battle.draw_count
                }
                for bid, battle in battle_manager.active_battles.items()
            },
            "matchingQueue": {
                uid: {
                    "userId": matching.user_id,
                    "matchingId": matching.matching_id,
                    "joinedAt": matching.joined_at.isoformat()
                }
                for uid, matching in battle_manager.matching_queue.items()
            },
            "counts": {
                "connections": battle_manager.get_active_connections_count(),
                "battles": battle_manager.get_active_battles_count(),
                "queue": battle_manager.get_queue_count()
            }
        }
    }


@router.get("/user/{user_id}/stats")
async def get_user_stats(user_id: str):
    """
    ユーザー統計情報取得
    
    Args:
        user_id: ユーザーID
    """
    try:
        # DB接続を削除
        # stats = await battle_db_service.get_user_stats(user_id)
        # if not stats:
        #     return {
        #         "success": False,
        #         "error": {
        #             "code": "USER_NOT_FOUND",
        #             "message": "ユーザーが見つからないか、統計データがありません"
        #         }
        #     }
        
        # メモリ上のデータを返す（DB接続がないため）
        stats = {
            "userId": user_id,
            "totalMatches": 0,
            "totalWins": 0,
            "totalLosses": 0,
            "totalDraws": 0,
            "winRate": 0.0,
            "lastMatchAt": None
        }
        
        return {
            "success": True,
            "data": stats
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": f"統計取得エラー: {str(e)}"
            }
        }


@router.get("/ranking/daily")
async def get_daily_ranking(limit: int = 20):
    """
    デイリーランキング取得
    
    Args:
        limit: 取得件数（最大50）
    """
    try:
        limit = min(limit, 50)  # 最大50件に制限
        # DB接続を削除
        # ranking = await battle_db_service.get_daily_ranking(limit)
        
        # メモリ上のデータを返す（DB接続がないため）
        ranking = [
            {
                "ranking_date": "2023-10-27",
                "user_id": "user1",
                "nickname": "Player 1",
                "profile_image_url": "https://via.placeholder.com/50",
                "total_matches": 10,
                "total_wins": 7,
                "total_losses": 3,
                "total_draws": 0,
                "win_rate": 0.700
            },
            {
                "ranking_date": "2023-10-27",
                "user_id": "user2",
                "nickname": "Player 2",
                "profile_image_url": "https://via.placeholder.com/50",
                "total_matches": 10,
                "total_wins": 6,
                "total_losses": 4,
                "total_draws": 0,
                "win_rate": 0.600
            }
        ]
        
        return {
            "success": True,
            "data": {
                "ranking": ranking,
                "total": len(ranking),
                "date": ranking[0]["ranking_date"] if ranking else None
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR", 
                "message": f"ランキング取得エラー: {str(e)}"
            }
        }


@router.get("/battle/{battle_id}")
async def get_battle_detail(battle_id: str):
    """
    バトル詳細情報取得
    
    Args:
        battle_id: バトルID
    """
    try:
        # DB接続を削除
        # battle_info = await battle_db_service.get_battle_session(battle_id)
        # if not battle_info:
        #     return {
        #         "success": False,
        #         "error": {
        #             "code": "BATTLE_NOT_FOUND",
        #             "message": "バトルが見つかりません"
        #         }
        #     }
        
        # メモリ上のデータを返す（DB接続がないため）
        battle_info = {
            "battleId": battle_id,
            "status": "completed",
            "player1": {
                "userId": "player1",
                "nickname": "Player 1",
                "profileImageUrl": "https://via.placeholder.com/50"
            },
            "player2": {
                "userId": "player2",
                "nickname": "Player 2",
                "profileImageUrl": "https://via.placeholder.com/50"
            },
            "drawCount": 0,
            "winner": "player1",
            "battleTime": "2023-10-27T10:00:00Z",
            "createdAt": "2023-10-27T09:50:00Z"
        }
        
        return {
            "success": True,
            "data": battle_info
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": f"バトル情報取得エラー: {str(e)}"
            }
        }


@router.post("/debug/cleanup")
async def debug_cleanup():
    """
    デバッグ用：期限切れバトルクリーンアップ
    """
    try:
        # DB接続を削除
        # cleaned_count = await battle_db_service.cleanup_expired_battles()
        
        # メモリ上のデータを返す（DB接続がないため）
        cleaned_count = 0
        
        return {
            "success": True,
            "data": {
                "cleanedBattles": cleaned_count,
                "message": f"{cleaned_count}件の期限切れバトルをクリーンアップしました"
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": f"クリーンアップエラー: {str(e)}"
            }
        }


# バトル画面専用ユーザー情報API
@router.get("/user-info/{user_id}")
async def get_battle_user_info(user_id: str):
    """
    バトル画面専用ユーザー情報取得
    
    バトル画面で必要なユーザー情報のみを取得する専用API
    
    Args:
        user_id: ユーザーID
    """
    try:
        # ユーザー基本情報を取得
        user_info = await battle_user_info_service.get_user_battle_info(user_id)
        
        return {
            "success": True,
            "data": user_info,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "error": {
                "code": "USER_NOT_FOUND",
                "message": f"ユーザー情報取得エラー: {str(e)}"
            },
            "timestamp": datetime.now().isoformat()
        }


@router.get("/user-stats/{user_id}")
async def get_battle_user_stats(user_id: str):
    """
    バトル画面専用統計情報取得
    
    バトル画面で表示する統計情報のみを取得する専用API
    
    Args:
        user_id: ユーザーID
    """
    try:
        # ユーザー統計情報を取得
        user_stats = await battle_user_info_service.get_user_battle_stats(user_id)
        
        return {
            "success": True,
            "data": user_stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "error": {
                "code": "USER_NOT_FOUND",
                "message": f"統計情報取得エラー: {str(e)}"
            },
            "timestamp": datetime.now().isoformat()
        }


@router.get("/battle-history/{user_id}")
async def get_battle_history(user_id: str, limit: int = 10):
    """
    バトル画面専用戦歴取得
    
    バトル画面で表示する最近の戦歴を取得する専用API
    
    Args:
        user_id: ユーザーID
        limit: 取得件数（デフォルト: 10件）
    """
    try:
        # ユーザーの戦歴を取得
        battle_history = await battle_user_info_service.get_user_battle_history(user_id, limit)
        
        return {
            "success": True,
            "data": {
                "userId": user_id,
                "battles": battle_history,
                "totalCount": len(battle_history)
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "error": {
                "code": "BATTLE_HISTORY_ERROR",
                "message": f"戦歴取得エラー: {str(e)}"
            },
            "timestamp": datetime.now().isoformat()
        }


@router.get("/opponent-info/{battle_id}")
async def get_opponent_info(battle_id: str, user_id: str):
    """
    バトル画面専用対戦相手情報取得
    
    バトル画面で表示する対戦相手の情報を取得する専用API
    
    Args:
        battle_id: バトルID
        user_id: ユーザーID（認証用）
    """
    try:
        # 対戦相手の情報を取得
        opponent_info = await battle_user_info_service.get_opponent_info(battle_id, user_id)
        
        return {
            "success": True,
            "data": opponent_info,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "error": {
                "code": "OPPONENT_INFO_ERROR",
                "message": f"対戦相手情報取得エラー: {str(e)}"
            },
            "timestamp": datetime.now().isoformat()
        }


# 開発用テストトークン生成エンドポイント
@router.post("/dev-token")
async def generate_dev_token(email: str = "test@example.com"):
    """
    開発用テストトークン生成
    
    開発・テスト用のJWTトークンを生成します。
    本番環境では使用しないでください。
    """
    try:
        from ...shared.services.jwt_service import jwt_service
        
        # 開発用トークンを生成
        token = jwt_service.create_dev_token(email, "developer")
        
        return {
            "success": True,
            "data": {
                "token": token,
                "email": email,
                "role": "developer",
                "user_id": f"dev_{email.split('@')[0]}",
                "nickname": f"開発者_{email.split('@')[0]}",
                "expires_in": "8 hours"
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "error": {
                "code": "TOKEN_GENERATION_ERROR",
                "message": f"トークン生成エラー: {str(e)}"
            },
            "timestamp": datetime.now().isoformat()
        }