from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, select
from ..shared.database.models import UserStats, User
from .schemas import UserStatsResponse
from ..shared.exceptions.handlers import APIException
from datetime import datetime

class LobbyService:
    """ロビー画面専用ビジネスロジックサービス"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_user_stats(self, user_id: str) -> UserStatsResponse:
        """ユーザーステータス取得 - ロビー画面専用"""
        try:
            print(f"🔍 ユーザーID: {user_id} の情報を取得中...")
            
            # ユーザー基本情報を取得（非同期構文）
            stmt = select(User).where(User.user_id == user_id)
            result = await self.db.execute(stmt)
            user = result.scalar_one_or_none()
            
            if not user:
                print(f"❌ ユーザーが見つかりません: {user_id}")
                raise APIException(
                    message="ユーザーが見つかりません",
                    status_code=404
                )
            
            print(f"✅ ユーザー基本情報取得成功:")
            print(f"  - user_id: {user.user_id}")
            print(f"  - nickname: {user.nickname}")
            print(f"  - email: {user.email}")
            print(f"  - profile_image_url: {user.profile_image_url}")
            print(f"  - title: {user.title}")
            print(f"  - alias: {user.alias}")
            print(f"  - is_active: {user.is_active}")
            print(f"  - created_at: {user.created_at}")
            
            # ユーザーステータスを取得（非同期構文）
            stmt = select(UserStats).where(UserStats.user_id == user_id)
            result = await self.db.execute(stmt)
            user_stats = result.scalar_one_or_none()
            
            if not user_stats:
                print(f"📊 ユーザーステータスが存在しないため初期化: {user_id}")
                # ユーザーステータスが存在しない場合は初期化
                user_stats = UserStats(
                    user_id=user_id,
                    total_wins=0,
                    total_losses=0,
                    total_draws=0,
                    total_matches=0,
                    daily_wins=0,
                    user_rank='no_rank',
                    recent_hand_results_str='',
                    title=user.title,  # ユーザーの基本情報から取得
                    alias=user.alias,  # ユーザーの基本情報から取得
                    show_title=True,
                    show_alias=True
                )
                self.db.add(user_stats)
                await self.db.commit()
                await self.db.refresh(user_stats)
                print(f"✅ ユーザーステータス初期化完了: {user_id}")
            else:
                print(f"✅ 既存のユーザーステータス取得成功: {user_id}")
                print(f"  - total_wins: {user_stats.total_wins}")
                print(f"  - total_losses: {user_stats.total_losses}")
                print(f"  - total_draws: {user_stats.total_draws}")
                print(f"  - total_matches: {user_stats.total_matches}")
                print(f"  - daily_wins: {user_stats.daily_wins}")
                print(f"  - user_rank: {user_stats.user_rank}")
                print(f"  - title: {user_stats.title}")
                print(f"  - alias: {user_stats.alias}")
            
            # ユーザー基本情報を統合してレスポンスを作成
            response_data = UserStatsResponse.from_orm(user_stats)
            # プロフィール画像URLとニックネームを追加
            response_data.profile_image_url = user.profile_image_url
            response_data.nickname = user.nickname
            
            print(f"📤 レスポンス作成完了:")
            print(f"  - profile_image_url: {response_data.profile_image_url}")
            print(f"  - nickname: {response_data.nickname}")
            print(f"  - title: {response_data.title}")
            print(f"  - alias: {response_data.alias}")
            
            return response_data
            
        except Exception as e:
            print(f"❌ エラーが発生しました: {type(e).__name__}: {str(e)}")
            import traceback
            print(f"📋 スタックトレース: {traceback.format_exc()}")
            raise APIException(
                message="ユーザーステータスの取得に失敗しました",
                status_code=500,
                details={"error": str(e), "type": type(e).__name__}
            )
    

    
    async def update_user_stats(self, user_id: str, stats_data: dict) -> UserStatsResponse:
        """ユーザーステータス更新 - ロビー画面専用"""
        try:
            user_stats = self.db.query(UserStats).filter(
                UserStats.user_id == user_id
            ).first()
            
            if not user_stats:
                raise APIException(
                    message="ユーザーステータスが見つかりません",
                    status_code=404
                )
            
            # 更新可能なフィールドのみ更新
            updatable_fields = [
                'win_count', 'lose_count', 'draw_count', 'total_matches',
                'daily_wins', 'daily_ranking', 'daily_rank', 'recent_hand_results',
                'title', 'alias', 'show_title', 'show_alias'
            ]
            
            for field in updatable_fields:
                if field in stats_data:
                    setattr(user_stats, field, stats_data[field])
            
            self.db.commit()
            self.db.refresh(user_stats)
            
            return UserStatsResponse.from_orm(user_stats)
            
        except Exception as e:
            if isinstance(e, APIException):
                raise e
            raise APIException(
                message="ユーザーステータスの更新に失敗しました",
                status_code=500,
                details={"error": str(e)}
            )
