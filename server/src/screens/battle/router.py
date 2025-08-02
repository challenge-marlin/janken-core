"""
バトル画面専用WebSocketルーター

リアルタイムじゃんけんバトル用WebSocketエンドポイント
"""

import json
from typing import Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import logging

from .services import battle_service
from .models import battle_manager
from .database_service import battle_db_service


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
    
    Args:
        websocket: WebSocket接続
        user_id: ユーザーID
    """
    logger = logging.getLogger(__name__)
    logger.info(f"WebSocket connection attempt for user: {user_id}")
    
    # ユーザー接続
    connected = await battle_service.connect_user(websocket, user_id)
    if not connected:
        logger.error(f"Failed to connect user: {user_id}")
        return
    
    logger.info(f"User {user_id} connected successfully")
    
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
        await battle_service.disconnect_user(user_id)
    except Exception as e:
        logger.error(f"Unexpected error for user {user_id}: {e}")
        await battle_service.disconnect_user(user_id)


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
        "disconnect": lambda uid, data: battle_service.disconnect_user(uid)
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
async def get_battle_info():
    """
    バトル全体情報取得
    
    システム状態の監視用エンドポイント
    """
    return {
        "success": True,
        "data": {
            "activeConnections": battle_manager.get_active_connections_count(),
            "activeBattles": battle_manager.get_active_battles_count(),
            "queueCount": battle_manager.get_queue_count(),
            "message": "バトルWebSocketサービスが稼働中です"
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
        stats = await battle_db_service.get_user_stats(user_id)
        if not stats:
            return {
                "success": False,
                "error": {
                    "code": "USER_NOT_FOUND",
                    "message": "ユーザーが見つからないか、統計データがありません"
                }
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
        ranking = await battle_db_service.get_daily_ranking(limit)
        
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
async def get_battle_info(battle_id: str):
    """
    バトル詳細情報取得
    
    Args:
        battle_id: バトルID
    """
    try:
        battle_info = await battle_db_service.get_battle_session(battle_id)
        if not battle_info:
            return {
                "success": False,
                "error": {
                    "code": "BATTLE_NOT_FOUND",
                    "message": "バトルが見つかりません"
                }
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
        cleaned_count = await battle_db_service.cleanup_expired_battles()
        
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