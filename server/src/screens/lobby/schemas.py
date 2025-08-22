from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# リクエストスキーマ
class LobbyUserStatsRequest(BaseModel):
    """ロビー画面ユーザーステータス取得リクエスト"""
    user_id: str = Field(..., description="ユーザーID")

# レスポンススキーマ
class UserStatsResponse(BaseModel):
    """ユーザーステータスレスポンス（統合版）"""
    user_id: str
    nickname: Optional[str] = None
    profile_image_url: Optional[str] = None
    total_wins: int = 0
    total_losses: int = 0
    total_draws: int = 0
    total_matches: int = 0
    daily_wins: int = 0
    daily_ranking: Optional[int] = None
    user_rank: str = "no_rank"
    recent_hand_results_str: str = ""
    title: Optional[str] = None
    alias: Optional[str] = None
    show_title: bool = True
    show_alias: bool = True
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class LobbyUserStatsResponse(BaseModel):
    """ロビー画面ユーザーステータス取得レスポンス"""
    success: bool = True
    message: str = "ユーザーステータスを取得しました"
    data: dict  # クライアント側の期待に合わせてdictに変更

# エラーレスポンス
class LobbyErrorResponse(BaseModel):
    """ロビー画面エラーレスポンス"""
    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[dict] = None
