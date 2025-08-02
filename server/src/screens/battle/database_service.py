"""
バトル画面専用データベースサービス

WebSocketバトルとDB連携のためのサービス層
"""

import asyncio
from typing import Optional, Tuple, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_, desc, func
from sqlalchemy.orm import selectinload

from ...shared.database.models_improved import (
    User, UserStats, BattleSession, MatchHistory, 
    WebSocketConnection, DailyRanking, Session,
    HandType, MatchResult, BattleStatus, ConnectionStatus, MatchType
)
from ...shared.database.connection_improved import get_async_session
from .models import BattlePlayer
from .schemas import PlayerResult


class BattleDatabaseService:
    """バトル用データベースサービス"""
    
    def __init__(self):
        self.session_factory = get_async_session
    
    async def get_user_info(self, user_id: str) -> Optional[BattlePlayer]:
        """ユーザー情報を取得してBattlePlayer形式で返す"""
        async with self.session_factory() as session:
            try:
                # ユーザー情報とuser_statsを結合取得
                stmt = select(User).options(
                    selectinload(User.user_stats)
                ).where(
                    and_(User.user_id == user_id, User.is_banned == False)
                )
                result = await session.execute(stmt)
                user = result.scalar_one_or_none()
                
                if not user:
                    return None
                
                return BattlePlayer(
                    user_id=user.user_id,
                    nickname=user.nickname,
                    profile_image_url=user.profile_image_url,
                    connection_id=None,  # WebSocket接続時に設定
                    connected_at=None
                )
                
            except Exception as e:
                print(f"Error getting user info: {e}")
                return None
    
    async def create_battle_session(self, player1: BattlePlayer, player2: BattlePlayer, 
                                   battle_id: str) -> bool:
        """バトルセッションをDBに作成"""
        async with self.session_factory() as session:
            try:
                battle_session = BattleSession(
                    battle_id=battle_id,
                    status=BattleStatus.matched,
                    player1_id=player1.user_id,
                    player2_id=player2.user_id,
                    player1_ready=False,
                    player2_ready=False,
                    expires_at=datetime.now() + timedelta(minutes=30)  # 30分で期限切れ
                )
                
                session.add(battle_session)
                await session.commit()
                return True
                
            except Exception as e:
                await session.rollback()
                print(f"Error creating battle session: {e}")
                return False
    
    async def update_battle_status(self, battle_id: str, status: BattleStatus,
                                  player1_ready: Optional[bool] = None,
                                  player2_ready: Optional[bool] = None) -> bool:
        """バトル状態を更新"""
        async with self.session_factory() as session:
            try:
                update_dict = {"status": status}
                
                if player1_ready is not None:
                    update_dict["player1_ready"] = player1_ready
                if player2_ready is not None:
                    update_dict["player2_ready"] = player2_ready
                
                if status == BattleStatus.ready:
                    update_dict["started_at"] = datetime.now()
                elif status in [BattleStatus.finished, BattleStatus.cancelled]:
                    update_dict["finished_at"] = datetime.now()
                
                stmt = update(BattleSession).where(
                    BattleSession.battle_id == battle_id
                ).values(**update_dict)
                
                await session.execute(stmt)
                await session.commit()
                return True
                
            except Exception as e:
                await session.rollback()
                print(f"Error updating battle status: {e}")
                return False
    
    async def submit_hand(self, battle_id: str, user_id: str, hand: HandType) -> bool:
        """プレイヤーの手をDBに記録"""
        async with self.session_factory() as session:
            try:
                # どちらのプレイヤーかを確認
                stmt = select(BattleSession).where(BattleSession.battle_id == battle_id)
                result = await session.execute(stmt)
                battle = result.scalar_one_or_none()
                
                if not battle:
                    return False
                
                update_dict = {}
                if battle.player1_id == user_id:
                    update_dict["player1_hand"] = hand
                elif battle.player2_id == user_id:
                    update_dict["player2_hand"] = hand
                else:
                    return False
                
                stmt = update(BattleSession).where(
                    BattleSession.battle_id == battle_id
                ).values(**update_dict)
                
                await session.execute(stmt)
                await session.commit()
                return True
                
            except Exception as e:
                await session.rollback()
                print(f"Error submitting hand: {e}")
                return False
    
    async def reset_hands(self, battle_id: str) -> bool:
        """手をリセット（引き分け時）"""
        async with self.session_factory() as session:
            try:
                stmt = update(BattleSession).where(
                    BattleSession.battle_id == battle_id
                ).values(
                    player1_hand=None,
                    player2_hand=None,
                    draw_count=BattleSession.draw_count + 1
                )
                
                await session.execute(stmt)
                await session.commit()
                return True
                
            except Exception as e:
                await session.rollback()
                print(f"Error resetting hands: {e}")
                return False
    
    async def save_match_result(self, battle_id: str, player1_result: PlayerResult,
                               player2_result: PlayerResult, winner: int,
                               duration_seconds: int) -> bool:
        """対戦結果をmatch_historyに保存"""
        async with self.session_factory() as session:
            try:
                # バトルセッション情報を取得
                stmt = select(BattleSession).options(
                    selectinload(BattleSession.player1),
                    selectinload(BattleSession.player2)
                ).where(BattleSession.battle_id == battle_id)
                result = await session.execute(stmt)
                battle = result.scalar_one_or_none()
                
                if not battle or not battle.player1_hand or not battle.player2_hand:
                    return False
                
                # プレイヤーの現在のレーティングを取得
                stmt_stats = select(UserStats).where(
                    UserStats.user_id.in_([battle.player1_id, battle.player2_id])
                )
                result_stats = await session.execute(stmt_stats)
                stats_dict = {stats.user_id: stats for stats in result_stats.scalars().all()}
                
                p1_stats = stats_dict.get(battle.player1_id)
                p2_stats = stats_dict.get(battle.player2_id)
                
                # レーティング変動計算（簡単なElo風）
                p1_rating_before = p1_stats.rank_points if p1_stats else 1000
                p2_rating_before = p2_stats.rank_points if p2_stats else 1000
                
                if winner == 1:  # Player1勝利
                    p1_rating_change = 20
                    p2_rating_change = -20
                elif winner == 2:  # Player2勝利
                    p1_rating_change = -20
                    p2_rating_change = 20
                else:  # 引き分け
                    p1_rating_change = 10
                    p2_rating_change = 10
                
                p1_rating_after = p1_rating_before + p1_rating_change
                p2_rating_after = p2_rating_before + p2_rating_change
                
                # MatchHistory作成
                match_history = MatchHistory(
                    battle_id=battle_id,
                    player1_id=battle.player1_id,
                    player2_id=battle.player2_id,
                    player1_nickname=battle.player1.nickname,
                    player2_nickname=battle.player2.nickname,
                    player1_hand=battle.player1_hand,
                    player2_hand=battle.player2_hand,
                    player1_result=MatchResult(player1_result.value),
                    player2_result=MatchResult(player2_result.value),
                    winner=winner,
                    total_rounds=1,
                    draw_count=battle.draw_count,
                    match_type=MatchType.random,
                    battle_duration_seconds=duration_seconds,
                    player1_rating_before=p1_rating_before,
                    player1_rating_after=p1_rating_after,
                    player1_rating_change=p1_rating_change,
                    player2_rating_before=p2_rating_before,
                    player2_rating_after=p2_rating_after,
                    player2_rating_change=p2_rating_change,
                    finished_at=datetime.now()
                )
                
                session.add(match_history)
                await session.commit()
                
                # 統計更新はトリガーで自動実行されるが、レーティングは手動更新
                await self._update_user_ratings(session, battle.player1_id, p1_rating_after)
                await self._update_user_ratings(session, battle.player2_id, p2_rating_after)
                
                return True
                
            except Exception as e:
                await session.rollback()
                print(f"Error saving match result: {e}")
                return False
    
    async def _update_user_ratings(self, session: AsyncSession, user_id: str, new_rating: int):
        """ユーザーのレーティングを更新"""
        try:
            # ランク判定
            if new_rating >= 2000:
                new_rank = "diamond"
            elif new_rating >= 1600:
                new_rank = "platinum"
            elif new_rating >= 1300:
                new_rank = "gold"
            elif new_rating >= 1100:
                new_rank = "silver"
            else:
                new_rank = "bronze"
            
            stmt = update(UserStats).where(
                UserStats.user_id == user_id
            ).values(
                rank_points=new_rating,
                user_rank=new_rank
            )
            
            await session.execute(stmt)
            await session.commit()
            
        except Exception as e:
            print(f"Error updating user rating: {e}")
    
    async def get_battle_session(self, battle_id: str) -> Optional[Dict[str, Any]]:
        """バトルセッション情報を取得"""
        async with self.session_factory() as session:
            try:
                stmt = select(BattleSession).options(
                    selectinload(BattleSession.player1),
                    selectinload(BattleSession.player2)
                ).where(BattleSession.battle_id == battle_id)
                
                result = await session.execute(stmt)
                battle = result.scalar_one_or_none()
                
                if not battle:
                    return None
                
                return {
                    "battle_id": battle.battle_id,
                    "status": battle.status.value,
                    "player1": {
                        "user_id": battle.player1_id,
                        "nickname": battle.player1.nickname if battle.player1 else "",
                        "ready": battle.player1_ready,
                        "hand": battle.player1_hand.value if battle.player1_hand else None
                    },
                    "player2": {
                        "user_id": battle.player2_id,
                        "nickname": battle.player2.nickname if battle.player2 else "",
                        "ready": battle.player2_ready,
                        "hand": battle.player2_hand.value if battle.player2_hand else None
                    },
                    "draw_count": battle.draw_count,
                    "created_at": battle.created_at.isoformat() if battle.created_at else None,
                    "started_at": battle.started_at.isoformat() if battle.started_at else None
                }
                
            except Exception as e:
                print(f"Error getting battle session: {e}")
                return None
    
    async def cleanup_expired_battles(self) -> int:
        """期限切れバトルセッションをクリーンアップ"""
        async with self.session_factory() as session:
            try:
                # 期限切れのバトルを検索
                stmt = select(BattleSession).where(
                    and_(
                        BattleSession.expires_at < datetime.now(),
                        BattleSession.status.not_in([BattleStatus.finished, BattleStatus.cancelled])
                    )
                )
                result = await session.execute(stmt)
                expired_battles = result.scalars().all()
                
                # キャンセル状態に更新
                for battle in expired_battles:
                    battle.status = BattleStatus.cancelled
                    battle.finished_at = datetime.now()
                
                await session.commit()
                return len(expired_battles)
                
            except Exception as e:
                await session.rollback()
                print(f"Error cleaning up expired battles: {e}")
                return 0
    
    async def register_websocket_connection(self, connection_id: str, user_id: str,
                                          session_id: Optional[str] = None,
                                          ip_address: Optional[str] = None) -> bool:
        """WebSocket接続を登録"""
        async with self.session_factory() as session:
            try:
                # 既存接続があれば削除
                await session.execute(
                    delete(WebSocketConnection).where(WebSocketConnection.user_id == user_id)
                )
                
                # 新しい接続を登録
                connection = WebSocketConnection(
                    connection_id=connection_id,
                    user_id=user_id,
                    session_id=session_id,
                    status=ConnectionStatus.connected,
                    ip_address=ip_address,
                    connected_at=datetime.now(),
                    last_activity=datetime.now()
                )
                
                session.add(connection)
                await session.commit()
                return True
                
            except Exception as e:
                await session.rollback()
                print(f"Error registering websocket connection: {e}")
                return False
    
    async def unregister_websocket_connection(self, user_id: str) -> bool:
        """WebSocket接続を削除"""
        async with self.session_factory() as session:
            try:
                stmt = delete(WebSocketConnection).where(WebSocketConnection.user_id == user_id)
                await session.execute(stmt)
                await session.commit()
                return True
                
            except Exception as e:
                await session.rollback()
                print(f"Error unregistering websocket connection: {e}")
                return False
    
    async def update_connection_status(self, user_id: str, status: ConnectionStatus,
                                     battle_id: Optional[str] = None) -> bool:
        """WebSocket接続状態を更新"""
        async with self.session_factory() as session:
            try:
                update_dict = {
                    "status": status,
                    "last_activity": datetime.now()
                }
                
                if battle_id is not None:
                    update_dict["battle_id"] = battle_id
                
                stmt = update(WebSocketConnection).where(
                    WebSocketConnection.user_id == user_id
                ).values(**update_dict)
                
                await session.execute(stmt)
                await session.commit()
                return True
                
            except Exception as e:
                await session.rollback()
                print(f"Error updating connection status: {e}")
                return False
    
    async def get_user_stats(self, user_id: str) -> Optional[Dict[str, Any]]:
        """ユーザー統計情報を取得"""
        async with self.session_factory() as session:
            try:
                stmt = select(UserStats).where(UserStats.user_id == user_id)
                result = await session.execute(stmt)
                stats = result.scalar_one_or_none()
                
                if not stats:
                    return None
                
                return {
                    "total_wins": stats.total_wins,
                    "total_losses": stats.total_losses,
                    "total_draws": stats.total_draws,
                    "total_matches": stats.total_matches,
                    "win_rate": float(stats.win_rate),
                    "current_win_streak": stats.current_win_streak,
                    "max_win_streak": stats.max_win_streak,
                    "user_rank": stats.user_rank.value,
                    "rank_points": stats.rank_points,
                    "daily_wins": stats.daily_wins,
                    "daily_losses": stats.daily_losses,
                    "daily_draws": stats.daily_draws,
                    "favorite_hand": stats.favorite_hand.value
                }
                
            except Exception as e:
                print(f"Error getting user stats: {e}")
                return None
    
    async def get_daily_ranking(self, limit: int = 50) -> List[Dict[str, Any]]:
        """本日のランキングを取得"""
        async with self.session_factory() as session:
            try:
                stmt = select(DailyRanking).where(
                    DailyRanking.ranking_date == datetime.now().date()
                ).order_by(
                    DailyRanking.ranking_position
                ).limit(limit)
                
                result = await session.execute(stmt)
                rankings = result.scalars().all()
                
                return [
                    {
                        "position": ranking.ranking_position,
                        "user_id": ranking.user_id,
                        "daily_wins": ranking.daily_wins,
                        "daily_matches": ranking.daily_matches,
                        "daily_win_rate": float(ranking.daily_win_rate),
                        "rating_points": ranking.rating_points,
                        "rank_change": ranking.rank_change
                    }
                    for ranking in rankings
                ]
                
            except Exception as e:
                print(f"Error getting daily ranking: {e}")
                return []


# サービスインスタンス
battle_db_service = BattleDatabaseService()