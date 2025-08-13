"""
認証画面専用SQLAlchemyモデル

Laravel風のEloquentモデルに相当するSQLAlchemyモデルを定義
Pydanticスキーマは schemas.py に分離
"""

from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from typing import Optional

Base = declarative_base()


class User(Base):
    """
    ユーザーモデル - LaravelのEloquentに相当
    
    認証システムの中核となるユーザー情報を管理
    """
    __tablename__ = 'users'
    
    user_id = Column(String(50), primary_key=True, comment="ユーザー識別子")
    email = Column(String(255), unique=True, nullable=False, comment="メールアドレス")
    nickname = Column(String(100), nullable=False, comment="ニックネーム")
    name = Column(String(50), nullable=True, comment="実名")
    role = Column(String(20), nullable=False, default='user', comment="ユーザーロール")
    profile_image_url = Column(String(500), nullable=True, comment="プロフィール画像URL")
    title = Column(String(100), nullable=True, comment="ユーザー称号")
    alias = Column(String(100), nullable=True, comment="別名")
    is_active = Column(Boolean, default=True, comment="アカウント有効性")
    is_banned = Column(Boolean, default=False, comment="BAN状態")
    created_at = Column(DateTime, default=func.now(), comment="作成日時")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新日時")


class MagicLinkToken(Base):
    """
    Magic Linkトークンモデル - Laravel風の認証トークン管理
    
    パスワードレス認証用のワンタイムトークンを管理
    """
    __tablename__ = 'magic_link_tokens'
    
    token_hash = Column(String(128), primary_key=True, comment="トークンハッシュ値")
    email = Column(String(255), nullable=False, comment="送信先メールアドレス")
    user_id = Column(String(50), nullable=True, comment="ユーザーID（既存ユーザーの場合）")
    issued_at = Column(DateTime, nullable=False, comment="発行日時")
    expires_at = Column(DateTime, nullable=False, comment="有効期限")
    used_at = Column(DateTime, nullable=True, comment="使用日時")
    ip_address = Column(String(45), nullable=True, comment="発行元IPアドレス")
    user_agent = Column(String(255), nullable=True, comment="発行元ブラウザ情報")


class UserSession(Base):
    """
    ユーザーセッションモデル - Laravel風のセッション管理
    
    JWT以外の永続化セッション情報を管理
    """
    __tablename__ = 'sessions'
    
    session_id = Column(String(100), primary_key=True, comment="セッション識別子")
    user_id = Column(String(50), nullable=False, comment="ユーザーID")
    device_id = Column(String(128), nullable=False, comment="端末識別子")
    ip_address = Column(String(45), nullable=True, comment="接続元IP")
    user_agent = Column(String(255), nullable=True, comment="ブラウザ情報")
    created_at = Column(DateTime, default=func.now(), comment="作成日時")
    last_seen_at = Column(DateTime, nullable=True, comment="最終アクセス日時")
    is_revoked = Column(Boolean, default=False, comment="無効化フラグ")


class LoginAttempt(Base):
    """
    ログイン試行モデル - Laravel風のセキュリティログ
    
    ブルートフォース攻撃対策用のログイン試行履歴
    """
    __tablename__ = 'login_attempts'
    
    attempt_id = Column(Integer, primary_key=True, autoincrement=True, comment="試行識別子")
    user_id = Column(String(50), nullable=True, comment="試行対象ユーザー")
    email = Column(String(255), nullable=True, comment="試行対象メール")
    ip_address = Column(String(45), nullable=False, comment="試行元IP")
    attempt_time = Column(DateTime, default=func.now(), comment="試行日時")
    success = Column(Boolean, default=False, comment="試行結果")
    failure_reason = Column(String(100), nullable=True, comment="失敗理由")
    user_agent = Column(String(255), nullable=True, comment="ブラウザ情報") 