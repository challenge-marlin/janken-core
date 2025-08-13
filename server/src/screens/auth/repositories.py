"""
認証画面専用リポジトリ - LaravelのEloquentに相当

データベース操作をカプセル化し、SQLAlchemy ORMの複雑さを隠蔽
Laravel的なクエリビルダーパターンを提供
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from datetime import datetime, timedelta
from fastapi import Depends

from .models import User, MagicLinkToken, UserSession, LoginAttempt
from ...shared.database.connection import get_db_session


class UserRepository:
    """
    ユーザーリポジトリ - LaravelのEloquentの代替
    
    LaravelのUser::find()やUser::where()のような直感的なインターフェースを提供
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    async def find_by_id(self, user_id: str) -> Optional[User]:
        """
        ID検索 - Laravel風: User::find($userId)
        
        Args:
            user_id: ユーザーID
            
        Returns:
            ユーザーモデル or None
        """
        return self.db.query(User).filter(User.user_id == user_id).first()
    
    async def find_by_email(self, email: str) -> Optional[User]:
        """
        メール検索 - Laravel風: User::where('email', $email)->first()
        
        Args:
            email: メールアドレス
            
        Returns:
            ユーザーモデル or None
        """
        return self.db.query(User).filter(User.email == email.lower()).first()
    
    async def create(self, user_data: Dict[str, Any]) -> User:
        """
        ユーザー作成 - Laravel風: User::create($data)
        
        Args:
            user_data: ユーザーデータ辞書
            
        Returns:
            作成されたユーザーモデル
        """
        user = User(**user_data)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    async def update(self, user_id: str, update_data: Dict[str, Any]) -> Optional[User]:
        """
        ユーザー更新 - Laravel風: User::where('id', $id)->update($data)
        
        Args:
            user_id: ユーザーID
            update_data: 更新データ辞書
            
        Returns:
            更新されたユーザーモデル or None
        """
        user = await self.find_by_id(user_id)
        if user:
            for key, value in update_data.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            user.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(user)
        return user
    
    async def get_active_users(self, limit: int = 100) -> List[User]:
        """
        アクティブユーザー取得 - Laravel風: User::where('is_active', true)->limit($limit)->get()
        
        Args:
            limit: 取得件数制限
            
        Returns:
            アクティブユーザーリスト
        """
        return self.db.query(User)\
            .filter(User.is_active == True)\
            .filter(User.is_banned == False)\
            .limit(limit)\
            .all()
    
    async def search_by_nickname(self, nickname: str, limit: int = 20) -> List[User]:
        """
        ニックネーム検索 - Laravel風: User::where('nickname', 'like', "%$nickname%")->get()
        
        Args:
            nickname: 検索するニックネーム
            limit: 取得件数制限
            
        Returns:
            マッチするユーザーリスト
        """
        return self.db.query(User)\
            .filter(User.nickname.contains(nickname))\
            .filter(User.is_active == True)\
            .limit(limit)\
            .all()
    
    async def exists_by_email(self, email: str) -> bool:
        """
        メール存在確認 - Laravel風: User::where('email', $email)->exists()
        
        Args:
            email: メールアドレス
            
        Returns:
            存在するかどうか
        """
        return self.db.query(User).filter(User.email == email.lower()).first() is not None


class MagicLinkRepository:
    """
    Magic Linkトークンリポジトリ
    
    パスワードレス認証のトークン管理を担当
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_token(self, token_data: Dict[str, Any]) -> MagicLinkToken:
        """
        トークン作成 - Laravel風: MagicLinkToken::create($data)
        
        Args:
            token_data: トークンデータ辞書
            
        Returns:
            作成されたトークンモデル
        """
        token = MagicLinkToken(**token_data)
        self.db.add(token)
        self.db.commit()
        self.db.refresh(token)
        return token
    
    async def find_valid_token(self, token_hash: str) -> Optional[MagicLinkToken]:
        """
        有効なトークン検索 - Laravel風のスコープチェーン
        
        Args:
            token_hash: トークンハッシュ値
            
        Returns:
            有効なトークンモデル or None
        """
        now = datetime.utcnow()
        return self.db.query(MagicLinkToken)\
            .filter(MagicLinkToken.token_hash == token_hash)\
            .filter(MagicLinkToken.expires_at > now)\
            .filter(MagicLinkToken.used_at.is_(None))\
            .first()
    
    async def mark_as_used(self, token_hash: str) -> bool:
        """
        トークンを使用済みにマーク
        
        Args:
            token_hash: トークンハッシュ値
            
        Returns:
            更新成功フラグ
        """
        token = await self.find_valid_token(token_hash)
        if token:
            token.used_at = datetime.utcnow()
            self.db.commit()
            return True
        return False
    
    async def cleanup_expired_tokens(self) -> int:
        """
        期限切れトークンのクリーンアップ - Laravel風: MagicLinkToken::where()->delete()
        
        Returns:
            削除件数
        """
        expired_count = self.db.query(MagicLinkToken)\
            .filter(MagicLinkToken.expires_at < datetime.utcnow())\
            .count()
        
        self.db.query(MagicLinkToken)\
            .filter(MagicLinkToken.expires_at < datetime.utcnow())\
            .delete()
        
        self.db.commit()
        return expired_count


class LoginAttemptRepository:
    """
    ログイン試行リポジトリ
    
    セキュリティ監査とブルートフォース攻撃対策用
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    async def log_attempt(self, attempt_data: Dict[str, Any]) -> LoginAttempt:
        """
        ログイン試行記録 - Laravel風: LoginAttempt::create($data)
        
        Args:
            attempt_data: 試行データ辞書
            
        Returns:
            記録された試行モデル
        """
        attempt = LoginAttempt(**attempt_data)
        self.db.add(attempt)
        self.db.commit()
        self.db.refresh(attempt)
        return attempt
    
    async def get_recent_attempts(
        self, 
        ip_address: str, 
        minutes: int = 60
    ) -> List[LoginAttempt]:
        """
        最近の試行履歴取得 - Laravel風のスコープクエリ
        
        Args:
            ip_address: IPアドレス
            minutes: 取得範囲（分）
            
        Returns:
            試行履歴リスト
        """
        since_time = datetime.utcnow() - timedelta(minutes=minutes)
        
        return self.db.query(LoginAttempt)\
            .filter(LoginAttempt.ip_address == ip_address)\
            .filter(LoginAttempt.attempt_time > since_time)\
            .order_by(desc(LoginAttempt.attempt_time))\
            .all()
    
    async def count_failed_attempts(
        self, 
        ip_address: str, 
        minutes: int = 60
    ) -> int:
        """
        失敗試行回数カウント - Laravel風: LoginAttempt::where()->count()
        
        Args:
            ip_address: IPアドレス
            minutes: カウント範囲（分）
            
        Returns:
            失敗回数
        """
        since_time = datetime.utcnow() - timedelta(minutes=minutes)
        
        return self.db.query(LoginAttempt)\
            .filter(LoginAttempt.ip_address == ip_address)\
            .filter(LoginAttempt.attempt_time > since_time)\
            .filter(LoginAttempt.success == False)\
            .count()
    
    async def is_rate_limited(
        self, 
        ip_address: str, 
        max_attempts: int = 5, 
        minutes: int = 60
    ) -> bool:
        """
        レート制限チェック - Laravel風のカスタムスコープ
        
        Args:
            ip_address: IPアドレス
            max_attempts: 最大試行回数
            minutes: 制限時間範囲（分）
            
        Returns:
            制限されているかどうか
        """
        failed_count = await self.count_failed_attempts(ip_address, minutes)
        return failed_count >= max_attempts


# ========================================
# 依存注入用ファクトリー関数（FastAPI Depends対応）
# ========================================

def get_user_repository(db: Session = Depends(get_db_session)) -> UserRepository:
    """ユーザーリポジトリのDI用ファクトリー"""
    return UserRepository(db)

def get_magic_link_repository(db: Session = Depends(get_db_session)) -> MagicLinkRepository:
    """Magic LinkリポジトリのDI用ファクトリー"""
    return MagicLinkRepository(db)

def get_login_attempt_repository(db: Session = Depends(get_db_session)) -> LoginAttemptRepository:
    """ログイン試行リポジトリのDI用ファクトリー"""
    return LoginAttemptRepository(db)
