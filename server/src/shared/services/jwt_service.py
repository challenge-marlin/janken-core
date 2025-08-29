"""
JWT サービス

JWT トークンの生成・検証・管理を行うサービス
"""

import jwt
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Union
from ..config.settings import settings
from ..exceptions.handlers import AuthenticationError, ValidationError


class JWTService:
    """JWT サービスクラス"""
    
    def __init__(self):
        self.secret_key = settings.jwt_secret_key
        self.algorithm = settings.jwt_algorithm
        self.expire_minutes = settings.jwt_expire_minutes
        
    def generate_token(
        self,
        user_data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        JWT トークンを生成
        
        Args:
            user_data: ユーザーデータ
            expires_delta: 有効期限（指定しない場合は設定値を使用）
            
        Returns:
            JWT トークン文字列
            
        Raises:
            ValidationError: ユーザーデータが不正な場合
        """
        try:
            # 必須フィールドのチェック
            if not user_data.get("email"):
                raise ValidationError("メールアドレスが必要です", field="email")
            
            # 有効期限の設定
            if expires_delta:
                expire = datetime.utcnow() + expires_delta
            else:
                expire = datetime.utcnow() + timedelta(minutes=self.expire_minutes)
            
            # ペイロード作成
            payload = {
                "email": user_data["email"],
                "role": user_data.get("role", "user"),
                "user_id": user_data.get("user_id"),
                "nickname": user_data.get("nickname"),
                "iat": datetime.utcnow(),
                "exp": expire,
                "iss": "janken-api",  # 発行者
                "aud": "janken-app"   # 対象者
            }
            
            # JWT生成
            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            return token
            
        except Exception as e:
            raise ValidationError(f"JWT生成に失敗しました: {str(e)}")
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        JWT トークンを検証
        
        Args:
            token: JWT トークン文字列
            
        Returns:
            デコードされたペイロード
            
        Raises:
            AuthenticationError: トークンが無効な場合
        """
        try:
            # Bearer プレフィックスを除去
            if token.startswith("Bearer "):
                token = token[7:]

            # JWT検証・デコード
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                audience="janken-app",
                issuer="janken-api"
            )

            return payload

        except jwt.ExpiredSignatureError:
            raise AuthenticationError("トークンの有効期限が切れています")
        except jwt.InvalidTokenError as e:
            raise AuthenticationError(f"無効なトークンです: {str(e)}")
        except jwt.InvalidAudienceError:
            raise AuthenticationError("トークンの対象者が無効です")
        except jwt.InvalidIssuerError:
            raise AuthenticationError("トークンの発行者が無効です")
        except jwt.InvalidSignatureError:
            raise AuthenticationError("トークンの署名が無効です（シークレットキーが一致しません）")
        except Exception as e:
            raise AuthenticationError(f"トークン検証に失敗しました: {str(e)}")
    
    def refresh_token(self, token: str) -> str:
        """
        JWT トークンをリフレッシュ
        
        Args:
            token: 既存のJWTトークン
            
        Returns:
            新しいJWTトークン
            
        Raises:
            AuthenticationError: トークンが無効な場合
        """
        try:
            # トークンを検証（期限切れでもOK）
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={"verify_exp": False}  # 期限切れチェックを無効化
            )
            
            # 新しいトークンを生成
            user_data = {
                "email": payload["email"],
                "role": payload.get("role", "user"),
                "user_id": payload.get("user_id"),
                "nickname": payload.get("nickname")
            }
            
            return self.generate_token(user_data)
            
        except Exception as e:
            raise AuthenticationError(f"トークンリフレッシュに失敗しました: {str(e)}")
    
    def get_token_info(self, token: str) -> Dict[str, Any]:
        """
        トークン情報を取得（検証なし）
        
        Args:
            token: JWT トークン文字列
            
        Returns:
            トークン情報
        """
        try:
            # Bearer プレフィックスを除去
            if token.startswith("Bearer "):
                token = token[7:]
            
            # デコード（検証なし）
            payload = jwt.decode(
                token,
                options={"verify_signature": False, "verify_exp": False}
            )
            
            return {
                "email": payload.get("email"),
                "role": payload.get("role"),
                "user_id": payload.get("user_id"),
                "nickname": payload.get("nickname"),
                "issued_at": payload.get("iat"),
                "expires_at": payload.get("exp"),
                "is_expired": datetime.utcnow().timestamp() > payload.get("exp", 0)
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def create_dev_token(self, email: str, role: str = "developer") -> str:
        """
        開発用トークンを生成
        
        Args:
            email: メールアドレス
            role: ロール
            
        Returns:
            開発用JWTトークン
        """
        user_data = {
            "email": email,
            "role": role,
            "user_id": f"dev_{email.split('@')[0]}",
            "nickname": f"開発者_{email.split('@')[0]}"
        }
        
        # 開発用は有効期限を短く設定
        expires_delta = timedelta(hours=8)
        return self.generate_token(user_data, expires_delta)
    
    def create_magic_link_token(self, email: str, magic_token: str) -> str:
        """
        Magic Link検証用の一時トークンを生成
        
        Args:
            email: メールアドレス
            magic_token: Magic Linkトークン
            
        Returns:
            一時JWT トークン
        """
        payload = {
            "email": email,
            "magic_token": magic_token,
            "type": "magic_link_verification",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(minutes=20),  # 20分有効
            "iss": "janken-api",
            "aud": "janken-app"
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_magic_link_token(self, token: str) -> Dict[str, Any]:
        """
        Magic Link検証用トークンを検証
        
        Args:
            token: Magic Link検証用トークン
            
        Returns:
            検証結果
            
        Raises:
            AuthenticationError: トークンが無効な場合
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                audience="janken-app",
                issuer="janken-api"
            )
            
            # Magic Link検証用トークンかチェック
            if payload.get("type") != "magic_link_verification":
                raise AuthenticationError("Magic Link検証用トークンではありません")
            
            return {
                "email": payload["email"],
                "magic_token": payload["magic_token"]
            }
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Magic Linkの有効期限が切れています")
        except jwt.InvalidTokenError:
            raise AuthenticationError("無効なMagic Linkトークンです")
        except Exception as e:
            raise AuthenticationError(f"Magic Linkトークン検証に失敗しました: {str(e)}")


# グローバルインスタンス
jwt_service = JWTService() 