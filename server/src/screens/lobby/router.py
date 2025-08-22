from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from .schemas import (
    LobbyUserStatsRequest, LobbyUserStatsResponse,
    LobbyErrorResponse
)
from .services import LobbyService
from src.shared.database.connection import get_db_session

router = APIRouter(prefix="/api/lobby", tags=["lobby"])

@router.get("/user-stats/{user_id}", response_model=LobbyUserStatsResponse)
async def get_lobby_user_stats(
    user_id: str,
    db: Session = Depends(get_db_session)
):
    """ロビー画面専用のユーザーステータス取得API"""
    try:
        service = LobbyService(db)
        user_stats = await service.get_user_stats(user_id)
        
        return LobbyUserStatsResponse(
            success=True,
            message="ユーザーステータスを取得しました",
            data={
                "stats": {
                    "user_id": user_stats.user_id,
                    "userId": user_stats.user_id,  # クライアント側の期待に合わせて追加
                    "nickname": user_stats.nickname,
                    "profile_image_url": user_stats.profile_image_url,
                    "profileImageUrl": user_stats.profile_image_url,  # クライアント側の期待に合わせて追加
                    "winCount": user_stats.total_wins,
                    "loseCount": user_stats.total_losses,
                    "drawCount": user_stats.total_draws,
                    "totalMatches": user_stats.total_matches,
                    "dailyWins": user_stats.daily_wins,
                    "dailyRanking": user_stats.daily_ranking,
                    "dailyRank": user_stats.user_rank,
                    "recentHandResultsStr": user_stats.recent_hand_results_str,
                    "title": user_stats.title,
                    "alias": user_stats.alias,
                    "showTitle": user_stats.show_title,
                    "showAlias": user_stats.show_alias,
                }
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "message": "ユーザーステータスの取得に失敗しました",
                "error": str(e)
            }
        )



@router.get("/health")
async def lobby_health_check():
    """ロビー画面APIのヘルスチェック"""
    return {
        "success": True,
        "message": "ロビー画面APIは正常に動作しています",
        "status": "healthy"
    }
