"""
認証画面専用サービス

認証画面で使用するビジネスロジックを実装
"""

import hashlib
import secrets
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from ...config.settings import settings
from ...shared.exceptions.handlers import (
    AuthenticationError, ValidationError, BusinessLogicError
)


class AuthService:
    """認証画面専用サービスクラス"""
    
    def __init__(self):
        self.jwt_secret = settings.jwt_secret_key
        self.jwt_algorithm = settings.jwt_algorithm
        self.jwt_expire_minutes = settings.jwt_expire_minutes
    
    async def request_magic_link(
        self,
        email: str,
        captcha: Optional[Dict] = None,
        recaptcha_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Magic Linkリクエスト処理（認証画面専用）
        
        Args:
            email: メールアドレス
            captcha: CAPTCHA情報
            recaptcha_token: reCAPTCHAトークン
            
        Returns:
            処理結果辞書
            
        Raises:
            ValidationError: バリデーションエラー
            BusinessLogicError: ビジネスロジックエラー
        """
        # メールアドレスバリデーション
        if not email or "@" not in email:
            raise ValidationError("有効なメールアドレスを入力してください", field="email")
        
        # 環境別CAPTCHA検証
        if settings.environment in ["vps", "aws"]:
            if not recaptcha_token:
                raise ValidationError("reCAPTCHAトークンが必要です", field="recaptcha_token")
            # TODO: reCAPTCHA検証実装
        
        # Magic Linkトークン生成
        magic_token = self._generate_magic_token(email)
        
        # TODO: メール送信実装
        # await self._send_magic_link_email(email, magic_token)
        
        return {
            "message": "Magic link sent.",
            "token": magic_token  # 開発環境でのみ返却
        }
    
    async def verify_magic_link(self, token: str) -> Dict[str, Any]:
        """
        Magic Linkトークン検証（認証画面専用）
        
        Args:
            token: Magic Linkトークン
            
        Returns:
            JWT情報とユーザー情報
            
        Raises:
            AuthenticationError: 認証エラー
        """
        if not token:
            raise AuthenticationError("トークンが指定されていません")
        
        # トークン検証
        email = self._verify_magic_token(token)
        if not email:
            raise AuthenticationError("無効なトークンです")
        
        # JWT生成
        jwt_token = self._generate_jwt_token(email)
        
        return {
            "token": jwt_token,
            "user": {
                "email": email,
                "role": "user"
            }
        }
    
    async def dev_login(self, email: str, mode: str = "dev") -> Dict[str, Any]:
        """
        開発用簡易認証（認証画面専用・開発/VPS環境のみ）
        
        Args:
            email: メールアドレス
            mode: ログインモード（dev/admin）
            
        Returns:
            JWT情報とユーザー情報
            
        Raises:
            AuthenticationError: 認証エラー
        """
        # AWS環境では無効
        if settings.environment == "aws":
            raise AuthenticationError("開発用認証はAWS環境では利用できません")
        
        # メールアドレスバリデーション
        if not email or "@" not in email:
            raise ValidationError("有効なメールアドレスを入力してください", field="email")
        
        # ロール決定
        role = "admin" if mode == "admin" else "developer"
        
        # JWT生成
        jwt_token = self._generate_jwt_token(email, role)
        
        return {
            "token": jwt_token,
            "user": {
                "email": email,
                "role": role
            }
        }
    
    async def user_info_login(self, user_id: str, password: str) -> Dict[str, Any]:
        """
        従来形式ログイン（認証画面専用・API仕様書互換）
        
        Args:
            user_id: ユーザーID
            password: パスワード
            
        Returns:
            ユーザー情報
            
        Raises:
            AuthenticationError: 認証エラー
            ValidationError: バリデーションエラー
        """
        # 必須パラメータチェック
        if not user_id or not password:
            raise ValidationError("ユーザーIDとパスワードは必須です")
        
        # TODO: データベースでユーザー認証
        # 現在はモックデータで対応
        if user_id == "testuser" and password == "testpass":
            return {
                "user": {
                    "user_id": user_id,
                    "nickname": "テストユーザー",
                    "title": "初心者",
                    "alias": "じゃんけん戦士",
                    "profile_image_url": None
                }
            }
        else:
            raise AuthenticationError("ユーザーIDまたはパスワードが正しくありません")
    
    def _generate_magic_token(self, email: str) -> str:
        """Magic Linkトークン生成"""
        timestamp = str(int(datetime.now().timestamp()))
        data = f"{email}:{timestamp}:{secrets.token_hex(16)}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def _verify_magic_token(self, token: str) -> Optional[str]:
        """Magic Linkトークン検証"""
        # TODO: 実際のトークン検証ロジック実装
        # 現在はモック実装
        if len(token) == 64:  # SHA256ハッシュ長
            return "test@example.com"
        return None
    
    def _generate_jwt_token(self, email: str, role: str = "user") -> str:
        """JWTトークン生成"""
        # TODO: 実際のJWT生成実装
        # 現在はモック実装
        payload = {
            "email": email,
            "role": role,
            "exp": datetime.utcnow() + timedelta(minutes=self.jwt_expire_minutes)
        }
        return f"mock_jwt_token_{email}_{role}" 