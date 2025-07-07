"""
SQLAlchemy モデル定義

Magic Link認証機能用のデータベースモデル
"""

from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Text, JSON, DECIMAL, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid

Base = declarative_base()


class User(Base):
    """ユーザー情報テーブル"""
    __tablename__ = "users"
    
    management_code = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), nullable=False, unique=True, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)  # Magic Link認証で必須
    password = Column(String(255), nullable=True)  # Magic Link認証では未使用
    name = Column(String(50), nullable=True)
    nickname = Column(String(50), nullable=False)
    postal_code = Column(String(10), nullable=True)
    address = Column(String(255), nullable=True)
    phone_number = Column(String(15), nullable=True)
    university = Column(String(100), nullable=True)
    birthdate = Column(DateTime, nullable=True)
    profile_image_url = Column(String(255), nullable=False, default='https://lesson01.myou-kou.com/avatars/defaultAvatar1.png')
    student_id_image_url = Column(String(255), nullable=False, default='https://lesson01.myou-kou.com/avatars/defaultStudentId.png')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    register_type = Column(String(20), default="magic_link")  # magic_link / google / line / apple
    is_student_id_editable = Column(Boolean, default=False)
    is_banned = Column(Integer, default=0)  # 0:未設定、1:設定、2:復帰
    
    # リレーションシップ
    magic_links = relationship("MagicLink", back_populates="user")
    sessions = relationship("Session", back_populates="user")
    security_events = relationship("SecurityEvent", back_populates="user")
    login_attempts = relationship("LoginAttempt", back_populates="user")
    stats = relationship("UserStats", back_populates="user", uselist=False)


class MagicLink(Base):
    """Magic Link認証用トークンテーブル"""
    __tablename__ = "magic_links"
    
    token_id = Column(String(128), primary_key=True)
    email = Column(String(255), nullable=False, index=True)
    token_hash = Column(String(512), nullable=False)
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    used_at = Column(DateTime, nullable=True, index=True)
    ip_address = Column(String(45), nullable=False)
    user_agent = Column(String(255), nullable=True)
    captcha_token = Column(String(128), nullable=True)
    recaptcha_score = Column(DECIMAL(3, 2), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # リレーションシップ
    user = relationship("User", back_populates="magic_links")
    
    @property
    def is_expired(self) -> bool:
        """有効期限が切れているかチェック"""
        return datetime.utcnow() > self.expires_at
    
    @property
    def is_used(self) -> bool:
        """使用済みかチェック"""
        return self.used_at is not None
    
    def mark_as_used(self):
        """使用済みマークを付ける"""
        self.used_at = datetime.utcnow()


class CaptchaChallenge(Base):
    """CAPTCHA チャレンジテーブル"""
    __tablename__ = "captcha_challenges"
    
    challenge_id = Column(String(128), primary_key=True)
    challenge_type = Column(String(20), nullable=False)  # 'janken' or 'recaptcha'
    question_data = Column(JSON, nullable=False)
    correct_answer = Column(String(50), nullable=False)
    signature_token = Column(String(256), nullable=False)
    ip_address = Column(String(45), nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    solved_at = Column(DateTime, nullable=True, index=True)
    is_solved = Column(Boolean, default=False)
    attempt_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    @property
    def is_expired(self) -> bool:
        """有効期限が切れているかチェック"""
        return datetime.utcnow() > self.expires_at
    
    def increment_attempt(self):
        """試行回数を増やす"""
        self.attempt_count += 1
    
    def mark_as_solved(self):
        """解決済みマークを付ける"""
        self.is_solved = True
        self.solved_at = datetime.utcnow()


class RateLimit(Base):
    """レート制限テーブル"""
    __tablename__ = "rate_limits"
    
    limit_id = Column(Integer, primary_key=True, autoincrement=True)
    ip_address = Column(String(45), nullable=False, index=True)
    endpoint = Column(String(100), nullable=False)
    request_count = Column(Integer, default=1)
    window_start = Column(DateTime, nullable=False)
    window_end = Column(DateTime, nullable=False, index=True)
    blocked_until = Column(DateTime, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 複合ユニークインデックス
    __table_args__ = (
        Index('unique_ip_endpoint_window', 'ip_address', 'endpoint', 'window_start', unique=True),
    )
    
    @property
    def is_blocked(self) -> bool:
        """ブロック中かチェック"""
        if self.blocked_until is None:
            return False
        return datetime.utcnow() < self.blocked_until
    
    def increment_request(self):
        """リクエスト数を増やす"""
        self.request_count += 1
        self.updated_at = datetime.utcnow()


class Session(Base):
    """セッション管理テーブル"""
    __tablename__ = "sessions"
    
    session_id = Column(String(128), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False)
    access_token = Column(String(512), nullable=False)
    refresh_token = Column(String(512), nullable=False)
    device_id = Column(String(128), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    last_activity = Column(DateTime, nullable=False)
    ip_address = Column(String(45), nullable=False)
    user_agent = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # リレーションシップ
    user = relationship("User", back_populates="sessions")
    
    @property
    def is_expired(self) -> bool:
        """有効期限が切れているかチェック"""
        return datetime.utcnow() > self.expires_at
    
    def update_activity(self):
        """最終活動時刻を更新"""
        self.last_activity = datetime.utcnow()
        self.updated_at = datetime.utcnow()


class SecurityEvent(Base):
    """セキュリティイベントテーブル"""
    __tablename__ = "security_events"
    
    event_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False)
    event_type = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False)
    ip_address = Column(String(45), nullable=False)
    device_info = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # リレーションシップ
    user = relationship("User", back_populates="security_events")


class LoginAttempt(Base):
    """ログイン試行テーブル"""
    __tablename__ = "login_attempts"
    
    attempt_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False)
    ip_address = Column(String(45), nullable=False, index=True)
    attempt_time = Column(DateTime, default=datetime.utcnow, index=True)
    success = Column(Boolean, default=False)
    failure_reason = Column(String(100), nullable=True)
    
    # リレーションシップ
    user = relationship("User", back_populates="login_attempts")


class UserStats(Base):
    """ユーザー統計テーブル"""
    __tablename__ = "user_stats"
    
    management_code = Column(Integer, ForeignKey("users.management_code"), primary_key=True)
    user_id = Column(String(36), nullable=False)
    total_wins = Column(Integer, default=0)
    current_win_streak = Column(Integer, default=0)
    max_win_streak = Column(Integer, default=0)
    hand_stats_rock = Column(Integer, default=0)
    hand_stats_scissors = Column(Integer, default=0)
    hand_stats_paper = Column(Integer, default=0)
    favorite_hand = Column(String(10), nullable=True)
    recent_hand_results_str = Column(String(255), default='')
    daily_wins = Column(Integer, default=0)
    daily_losses = Column(Integer, default=0)
    daily_draws = Column(Integer, default=0)
    title = Column(String(50), default='')
    available_titles = Column(String(255), default='')
    alias = Column(String(50), default='')
    show_title = Column(Boolean, default=True)
    show_alias = Column(Boolean, default=True)
    user_rank = Column(String(20), default='no_rank')
    last_reset_at = Column(DateTime, nullable=True)
    
    # リレーションシップ
    user = relationship("User", back_populates="stats")
    
    def reset_daily_stats(self):
        """日次統計をリセット"""
        self.daily_wins = 0
        self.daily_losses = 0
        self.daily_draws = 0
        self.last_reset_at = datetime.utcnow()
    
    def add_hand_result(self, hand: str, result: str):
        """手と結果を追加"""
        # 手の統計を更新
        if hand == 'rock':
            self.hand_stats_rock += 1
        elif hand == 'scissors':
            self.hand_stats_scissors += 1
        elif hand == 'paper':
            self.hand_stats_paper += 1
        
        # お気に入りの手を更新
        total_hands = {
            'rock': self.hand_stats_rock,
            'scissors': self.hand_stats_scissors,
            'paper': self.hand_stats_paper
        }
        self.favorite_hand = max(total_hands.items(), key=lambda x: x[1])[0]
        
        # 直近の手と結果を更新
        hand_map = {'rock': 'G', 'scissors': 'S', 'paper': 'P'}
        result_map = {'win': 'W', 'lose': 'L', 'draw': 'D'}
        
        new_result = f"{hand_map[hand]}:{result_map[result]}"
        results = self.recent_hand_results_str.split(',') if self.recent_hand_results_str else []
        results.append(new_result)
        if len(results) > 5:
            results = results[-5:]
        self.recent_hand_results_str = ','.join(results)
        
        # 勝敗統計を更新
        if result == 'win':
            self.daily_wins += 1
            self.total_wins += 1
            self.current_win_streak += 1
            if self.current_win_streak > self.max_win_streak:
                self.max_win_streak = self.current_win_streak
        elif result == 'lose':
            self.daily_losses += 1
            self.current_win_streak = 0
        else:  # draw
            self.daily_draws += 1
            # 引き分けは連勝を継続


# ユーティリティ関数
def generate_magic_link_token() -> str:
    """Magic Linkトークンを生成"""
    return str(uuid.uuid4()).replace('-', '')


def generate_captcha_challenge_id() -> str:
    """CAPTCHAチャレンジIDを生成"""
    return str(uuid.uuid4()).replace('-', '')


def generate_session_id() -> str:
    """セッションIDを生成"""
    return str(uuid.uuid4()).replace('-', '')


def create_magic_link_expires_at(minutes: int = 15) -> datetime:
    """Magic Linkの有効期限を生成"""
    return datetime.utcnow() + timedelta(minutes=minutes)


def create_captcha_expires_at(minutes: int = 10) -> datetime:
    """CAPTCHAの有効期限を生成"""
    return datetime.utcnow() + timedelta(minutes=minutes) 