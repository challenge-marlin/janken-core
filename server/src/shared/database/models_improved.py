"""
改善版SQLAlchemyモデル定義

WebSocketバトル対応のじゃんけんゲーム特化型DB設計
"""

from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, Enum, Text, 
    ForeignKey, Index, DECIMAL, JSON, BIGINT, DATE, func
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, date
import enum

Base = declarative_base()


class UserRank(enum.Enum):
    """ユーザーランク"""
    bronze = "bronze"
    silver = "silver"
    gold = "gold"
    platinum = "platinum"
    diamond = "diamond"


class HandType(enum.Enum):
    """じゃんけんの手"""
    rock = "rock"
    scissors = "scissors"
    paper = "paper"


class MatchResult(enum.Enum):
    """試合結果"""
    win = "win"
    lose = "lose"
    draw = "draw"


class MatchType(enum.Enum):
    """マッチングタイプ"""
    random = "random"
    friend = "friend"
    tournament = "tournament"


class BattleStatus(enum.Enum):
    """バトル状態"""
    waiting = "waiting"
    matched = "matched"
    preparing = "preparing"
    ready = "ready"
    playing = "playing"
    judging = "judging"
    finished = "finished"
    cancelled = "cancelled"


class ConnectionStatus(enum.Enum):
    """WebSocket接続状態"""
    connected = "connected"
    in_queue = "in_queue"
    in_battle = "in_battle"
    disconnected = "disconnected"


class RegisterType(enum.Enum):
    """登録方法"""
    email = "email"
    dev = "dev"
    oauth = "oauth"


# ============================================
# ユーザー関連テーブル
# ============================================

class User(Base):
    """ユーザー情報（簡素化版）"""
    __tablename__ = 'users'
    
    user_id = Column(String(36), primary_key=True)
    email = Column(String(255), unique=True, index=True)
    nickname = Column(String(50), nullable=False)
    profile_image_url = Column(String(255))
    is_banned = Column(Boolean, default=False, index=True)
    register_type = Column(Enum(RegisterType), default=RegisterType.email)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # リレーション
    user_stats = relationship("UserStats", back_populates="user", uselist=False)
    sessions = relationship("Session", back_populates="user")
    websocket_connections = relationship("WebSocketConnection", back_populates="user")
    player1_matches = relationship("MatchHistory", foreign_keys="MatchHistory.player1_id", back_populates="player1")
    player2_matches = relationship("MatchHistory", foreign_keys="MatchHistory.player2_id", back_populates="player2")
    battle_sessions_p1 = relationship("BattleSession", foreign_keys="BattleSession.player1_id", back_populates="player1")
    battle_sessions_p2 = relationship("BattleSession", foreign_keys="BattleSession.player2_id", back_populates="player2")


class UserStats(Base):
    """ユーザー戦績（強化版）"""
    __tablename__ = 'user_stats'
    
    user_id = Column(String(36), ForeignKey('users.user_id', ondelete='CASCADE'), primary_key=True)
    
    # 基本戦績
    total_wins = Column(Integer, default=0)
    total_losses = Column(Integer, default=0)
    total_draws = Column(Integer, default=0)
    total_matches = Column(Integer, default=0)
    win_rate = Column(DECIMAL(5, 2), default=0.00)
    
    # 連勝記録
    current_win_streak = Column(Integer, default=0)
    max_win_streak = Column(Integer, default=0)
    current_lose_streak = Column(Integer, default=0)
    max_lose_streak = Column(Integer, default=0)
    
    # 手の使用統計
    hand_stats_rock = Column(Integer, default=0)
    hand_stats_scissors = Column(Integer, default=0)
    hand_stats_paper = Column(Integer, default=0)
    favorite_hand = Column(Enum(HandType), default=HandType.rock)
    
    # デイリー統計
    daily_wins = Column(Integer, default=0)
    daily_losses = Column(Integer, default=0)
    daily_draws = Column(Integer, default=0)
    daily_matches = Column(Integer, default=0)
    last_daily_reset = Column(DATE, default=func.current_date())
    
    # ランキング関連
    user_rank = Column(Enum(UserRank), default=UserRank.bronze)
    rank_points = Column(Integer, default=1000)
    highest_rank = Column(Enum(UserRank), default=UserRank.bronze)
    highest_rank_points = Column(Integer, default=1000)
    
    # 活動状況
    last_battle_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # リレーション
    user = relationship("User", back_populates="user_stats")
    
    # インデックス
    __table_args__ = (
        Index('idx_user_stats_rank_points', 'rank_points'),
        Index('idx_user_stats_daily_wins', 'daily_wins'),
        Index('idx_user_stats_total_wins', 'total_wins'),
        Index('idx_user_stats_win_rate', 'win_rate'),
        Index('idx_user_stats_composite_ranking', 'is_active', 'rank_points', 'daily_wins'),
    )


# ============================================
# バトル関連テーブル
# ============================================

class BattleSession(Base):
    """バトルセッション管理"""
    __tablename__ = 'battle_sessions'
    
    battle_id = Column(String(36), primary_key=True)
    status = Column(Enum(BattleStatus), default=BattleStatus.waiting, index=True)
    
    # プレイヤー情報
    player1_id = Column(String(36), ForeignKey('users.user_id', ondelete='CASCADE'), index=True)
    player2_id = Column(String(36), ForeignKey('users.user_id', ondelete='CASCADE'), index=True)
    player1_ready = Column(Boolean, default=False)
    player2_ready = Column(Boolean, default=False)
    
    # ゲーム状態
    player1_hand = Column(Enum(HandType))
    player2_hand = Column(Enum(HandType))
    current_round = Column(Integer, default=1)
    draw_count = Column(Integer, default=0)
    
    # タイムスタンプ
    created_at = Column(DateTime, default=func.now())
    started_at = Column(DateTime)
    finished_at = Column(DateTime)
    expires_at = Column(DateTime, nullable=False, index=True)
    
    # リレーション
    player1 = relationship("User", foreign_keys=[player1_id], back_populates="battle_sessions_p1")
    player2 = relationship("User", foreign_keys=[player2_id], back_populates="battle_sessions_p2")
    match_history = relationship("MatchHistory", back_populates="battle_session", uselist=False)


class WebSocketConnection(Base):
    """WebSocket接続管理"""
    __tablename__ = 'websocket_connections'
    
    connection_id = Column(String(128), primary_key=True)
    user_id = Column(String(36), ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    session_id = Column(String(128), ForeignKey('sessions.session_id'))
    battle_id = Column(String(36), ForeignKey('battle_sessions.battle_id', ondelete='SET NULL'), index=True)
    status = Column(Enum(ConnectionStatus), default=ConnectionStatus.connected, index=True)
    
    # 接続情報
    ip_address = Column(String(45))
    user_agent = Column(String(255))
    connected_at = Column(DateTime, default=func.now())
    last_activity = Column(DateTime, default=func.now(), onupdate=func.now(), index=True)
    
    # リレーション
    user = relationship("User", back_populates="websocket_connections")
    session = relationship("Session", back_populates="websocket_connections")
    
    # インデックス
    __table_args__ = (
        Index('idx_ws_connections_active_users', 'status', 'user_id', 'last_activity'),
    )


class MatchHistory(Base):
    """対戦履歴（改良版）"""
    __tablename__ = 'match_history'
    
    match_id = Column(BIGINT, primary_key=True, autoincrement=True)
    battle_id = Column(String(36), ForeignKey('battle_sessions.battle_id'), unique=True)
    
    # プレイヤー情報
    player1_id = Column(String(36), ForeignKey('users.user_id'), nullable=False, index=True)
    player2_id = Column(String(36), ForeignKey('users.user_id'), nullable=False, index=True)
    player1_nickname = Column(String(50))
    player2_nickname = Column(String(50))
    
    # ゲーム結果
    player1_hand = Column(Enum(HandType), nullable=False)
    player2_hand = Column(Enum(HandType), nullable=False)
    player1_result = Column(Enum(MatchResult), nullable=False)
    player2_result = Column(Enum(MatchResult), nullable=False)
    winner = Column(Integer, nullable=False, default=0, index=True)  # 1=p1, 2=p2, 3=draw
    
    # ゲーム詳細
    total_rounds = Column(Integer, default=1)
    draw_count = Column(Integer, default=0)
    match_type = Column(Enum(MatchType), default=MatchType.random, index=True)
    battle_duration_seconds = Column(Integer)
    
    # レーティング変動
    player1_rating_before = Column(Integer)
    player1_rating_after = Column(Integer)
    player1_rating_change = Column(Integer, default=0)
    player2_rating_before = Column(Integer)
    player2_rating_after = Column(Integer)
    player2_rating_change = Column(Integer, default=0)
    
    # タイムスタンプ
    created_at = Column(DateTime(3), default=func.now(), index=True)
    finished_at = Column(DateTime(3))
    
    # リレーション
    player1 = relationship("User", foreign_keys=[player1_id], back_populates="player1_matches")
    player2 = relationship("User", foreign_keys=[player2_id], back_populates="player2_matches")
    battle_session = relationship("BattleSession", back_populates="match_history")
    
    # インデックス
    __table_args__ = (
        Index('idx_match_history_recent', 'created_at', 'match_type'),
    )


class DailyRanking(Base):
    """デイリーランキング（改良版）"""
    __tablename__ = 'daily_ranking'
    
    ranking_date = Column(DATE, primary_key=True)
    ranking_position = Column(Integer, primary_key=True)
    user_id = Column(String(36), ForeignKey('users.user_id'), nullable=False, index=True)
    daily_wins = Column(Integer, default=0)
    daily_matches = Column(Integer, default=0)
    daily_win_rate = Column(DECIMAL(5, 2), default=0.00)
    rating_points = Column(Integer, default=1000)
    rank_change = Column(Integer, default=0)  # 前日からの順位変動
    
    # インデックス
    __table_args__ = (
        Index('idx_daily_ranking_date_wins', 'ranking_date', 'daily_wins'),
    )


# ============================================
# 認証関連テーブル（簡素化）
# ============================================

class Session(Base):
    """セッション管理（WebSocket連携強化）"""
    __tablename__ = 'sessions'
    
    session_id = Column(String(128), primary_key=True)
    user_id = Column(String(36), ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    access_token_hash = Column(String(512), nullable=False)
    refresh_token_hash = Column(String(512))
    device_info = Column(JSON)
    expires_at = Column(DateTime, nullable=False, index=True)
    last_activity = Column(DateTime, default=func.now(), onupdate=func.now())
    ip_address = Column(String(45), nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    websocket_connection_id = Column(String(128))
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # リレーション
    user = relationship("User", back_populates="sessions")
    websocket_connections = relationship("WebSocketConnection", back_populates="session")


class MagicLink(Base):
    """Magic Link認証"""
    __tablename__ = 'magic_links'
    
    token_id = Column(String(128), primary_key=True)
    email = Column(String(255), nullable=False, index=True)
    token_hash = Column(String(512), nullable=False)
    user_id = Column(String(36), ForeignKey('users.user_id', ondelete='SET NULL'))
    expires_at = Column(DateTime, nullable=False, index=True)
    used_at = Column(DateTime)
    ip_address = Column(String(45), nullable=False)
    created_at = Column(DateTime, default=func.now())


class RateLimit(Base):
    """レート制限"""
    __tablename__ = 'rate_limits'
    
    limit_id = Column(BIGINT, primary_key=True, autoincrement=True)
    ip_address = Column(String(45), nullable=False, index=True)
    endpoint = Column(String(100), nullable=False)
    request_count = Column(Integer, default=1)
    window_start = Column(DateTime, nullable=False)
    window_end = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=func.now())
    
    # 複合ユニークキー
    __table_args__ = (
        Index('unique_ip_endpoint_window', 'ip_address', 'endpoint', 'window_start', unique=True),
    )


class SecurityEvent(Base):
    """セキュリティイベント"""
    __tablename__ = 'security_events'
    
    event_id = Column(BIGINT, primary_key=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey('users.user_id', ondelete='SET NULL'), index=True)
    event_type = Column(String(50), nullable=False, index=True)
    status = Column(String(20), nullable=False)
    ip_address = Column(String(45), nullable=False)
    details = Column(JSON)
    created_at = Column(DateTime, default=func.now(), index=True)


# ============================================
# ユーティリティ関数
# ============================================

def get_all_tables():
    """全テーブルクラスのリストを取得"""
    return [
        User, UserStats, BattleSession, WebSocketConnection, 
        MatchHistory, DailyRanking, Session, MagicLink, 
        RateLimit, SecurityEvent
    ]


def create_all_tables(engine):
    """全テーブルを作成"""
    Base.metadata.create_all(bind=engine)


def drop_all_tables(engine):
    """全テーブルを削除"""
    Base.metadata.drop_all(bind=engine)