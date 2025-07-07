"""
認証画面専用サービス

認証画面で使用するビジネスロジックを実装
"""

import hashlib
import secrets
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import uuid
import jwt
from fastapi import HTTPException

from ...shared.config.settings import settings
from ...shared.exceptions.handlers import (
    AuthenticationError, ValidationError, BusinessLogicError
)
from ...shared.database.models import (
    User, MagicLink, CaptchaChallenge, generate_magic_link_token,
    create_magic_link_expires_at, generate_captcha_challenge_id,
    create_captcha_expires_at, UserStats
)
from ...shared.services.jwt_service import jwt_service
from ...shared.database.connection import get_db_session as get_db
from ...shared.config.auth_config import AuthConfig
from ...shared.services.email_service import EmailService


class AuthService:
    """認証画面専用サービスクラス"""
    
    def __init__(self):
        self.jwt_service = jwt_service
        self.email_service = EmailService()
        self._magic_link_tokens: Dict[str, MagicLinkToken] = {}
    
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
            
            # CAPTCHA検証
            await self._verify_captcha(captcha)
            # TODO: reCAPTCHA検証実装
            # await self._verify_recaptcha(recaptcha_token)
        
        # Magic Linkトークン生成
        magic_token = generate_magic_link_token()
        token_hash = self._hash_token(magic_token)
        
        # データベースに保存
        db = next(get_db())
        try:
            # 既存のユーザーを確認
            user = db.query(User).filter(User.email == email).first()
            
            # Magic Linkレコード作成
            magic_link = MagicLink(
                token_id=magic_token,
                email=email,
                token_hash=token_hash,
                user_id=user.user_id if user else None,
                expires_at=create_magic_link_expires_at(),
                ip_address="127.0.0.1",  # TODO: 実際のIPアドレスを取得
                user_agent="",  # TODO: 実際のUser-Agentを取得
                captcha_token=captcha.get("token") if captcha else None,
                recaptcha_score=None  # TODO: reCAPTCHAスコアを保存
            )
            
            db.add(magic_link)
            db.commit()
            
            # TODO: メール送信実装
            # await self._send_magic_link_email(email, magic_token)
            
            result = {
                "message": "Magic link sent."
            }
            
            # 開発環境ではトークンを返却
            if settings.environment == "development":
                result["token"] = magic_token
                
            return result
            
        except Exception as e:
            db.rollback()
            raise BusinessLogicError(f"Magic Link作成に失敗しました: {str(e)}")
        finally:
            db.close()
    
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
        
        db = next(get_db())
        try:
            # トークンハッシュ化
            token_hash = self._hash_token(token)
            
            # Magic Linkレコード検索
            magic_link = db.query(MagicLink).filter(
                MagicLink.token_hash == token_hash
            ).first()
            
            if not magic_link:
                raise AuthenticationError("無効なトークンです")
            
            # 有効期限チェック
            if magic_link.is_expired:
                raise AuthenticationError("トークンの有効期限が切れています")
            
            # 使用済みチェック
            if magic_link.is_used:
                raise AuthenticationError("このトークンは既に使用されています")
            
            # ユーザー情報取得または作成
            user = await self._get_or_create_user(magic_link.email, db)
            
            # トークンを使用済みにマーク
            magic_link.mark_as_used()
            db.commit()
            
            # JWT生成
            jwt_token = self.jwt_service.generate_token({
                "email": user.email,
                "user_id": user.user_id,
                "nickname": user.nickname,
                "role": "user"
            })
            
            return {
                "token": jwt_token,
                "user": {
                    "email": user.email,
                    "user_id": user.user_id,
                    "nickname": user.nickname,
                    "role": "user"
                }
            }
            
        except Exception as e:
            db.rollback()
            if isinstance(e, AuthenticationError):
                raise
            raise AuthenticationError(f"トークン検証に失敗しました: {str(e)}")
        finally:
            db.close()
    
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
        jwt_token = self.jwt_service.create_dev_token(email, role)
        
        return {
            "token": jwt_token,
            "user": {
                "email": email,
                "user_id": f"dev_{email.split('@')[0]}",
                "nickname": f"開発者_{email.split('@')[0]}",
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
        
        db = next(get_db())
        try:
            # ユーザー検索
            user = db.query(User).filter(User.user_id == user_id).first()
            
            if not user:
                raise AuthenticationError("ユーザーIDまたはパスワードが正しくありません")
            
            # パスワード検証
            if not self._verify_password(password, user.password):
                raise AuthenticationError("ユーザーIDまたはパスワードが正しくありません")
            
            # BANチェック
            if user.is_banned:
                raise AuthenticationError("このアカウントは利用停止されています")
            
            return {
                "user": {
                    "user_id": user.user_id,
                    "nickname": user.nickname,
                    "title": "",  # TODO: user_statsから取得
                    "alias": "",  # TODO: user_statsから取得
                    "profile_image_url": user.profile_image_url
                }
            }
            
        except Exception as e:
            if isinstance(e, (AuthenticationError, ValidationError)):
                raise
            raise AuthenticationError(f"ログイン処理に失敗しました: {str(e)}")
        finally:
            db.close()
    
    async def _verify_captcha(self, captcha: Optional[Dict]) -> bool:
        """
        じゃんけんCAPTCHA検証
        
        Args:
            captcha: CAPTCHA情報
            
        Returns:
            検証結果
            
        Raises:
            ValidationError: バリデーションエラー
        """
        if not captcha:
            raise ValidationError("CAPTCHAが必要です", field="captcha")
        
        opponent = captcha.get("opponent")
        answer = captcha.get("answer")
        token = captcha.get("token")
        
        if not all([opponent, answer, token]):
            raise ValidationError("CAPTCHA情報が不完全です", field="captcha")
        
        db = next(get_db())
        try:
            # チャレンジを検索
            challenge = db.query(CaptchaChallenge).filter(
                CaptchaChallenge.signature_token == token,
                CaptchaChallenge.challenge_type == "janken"
            ).first()
            
            if not challenge:
                raise ValidationError("無効なCAPTCHAトークンです", field="captcha")
            
            # 有効期限チェック
            if challenge.is_expired:
                raise ValidationError("CAPTCHAの有効期限が切れています", field="captcha")
            
            # 使用済みチェック
            if challenge.is_solved:
                raise ValidationError("このCAPTCHAは既に使用されています", field="captcha")
            
            # 試行回数をインクリメント
            challenge.increment_attempt()
            
            # 試行回数制限チェック
            if challenge.attempt_count > 3:
                raise ValidationError("試行回数が上限を超えました", field="captcha")
            
            # 正解チェック
            question_data = challenge.question_data
            if question_data["opponent_hand"] != opponent:
                raise ValidationError("不正な回答です", field="captcha")
            
            # じゃんけんの勝敗判定
            opponent_hand = question_data["opponent_hand_name"]
            is_correct = False
            
            if opponent_hand == "rock" and answer == "✋":
                is_correct = True
            elif opponent_hand == "scissors" and answer == "✊":
                is_correct = True
            elif opponent_hand == "paper" and answer == "✌️":
                is_correct = True
            
            if not is_correct:
                raise ValidationError("不正解です。もう一度試してください。", field="captcha")
            
            # 正解としてマーク
            challenge.mark_as_solved()
            db.commit()
            
            return True
            
        except Exception as e:
            db.rollback()
            if isinstance(e, ValidationError):
                raise
            raise ValidationError(f"CAPTCHA検証に失敗しました: {str(e)}", field="captcha")
        finally:
            db.close()
    
    async def _get_or_create_user(self, email: str, db: Session) -> User:
        """
        ユーザー情報取得または新規作成（Magic Link認証用）
        
        Args:
            email: メールアドレス
            db: データベースセッション
            
        Returns:
            ユーザー情報
            
        Raises:
            BusinessLogicError: ビジネスロジックエラー
        """
        # 既存ユーザーを検索
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            # 新規ユーザー作成
            user = User(
                user_id=str(uuid.uuid4()),
                email=email,
                nickname=email.split('@')[0],  # メールアドレスのローカル部分をニックネームに
                profile_image_url='https://lesson01.myou-kou.com/avatars/defaultAvatar1.png',
                student_id_image_url='https://lesson01.myou-kou.com/avatars/defaultStudentId.png',
                register_type='magic_link'
            )
            db.add(user)
            db.flush()  # management_codeを取得するためにflush
            
            # 初期統計データ作成
            stats = UserStats(
                management_code=user.management_code,
                user_id=user.user_id,
                last_reset_at=datetime.utcnow()
            )
            db.add(stats)
            
            try:
                db.commit()
            except Exception as e:
                db.rollback()
                raise BusinessLogicError(f"ユーザー作成に失敗しました: {str(e)}")
        
        return user
    
    def _hash_token(self, token: str) -> str:
        """トークンをハッシュ化"""
        return hashlib.sha256(f"{token}:{settings.jwt_secret_key}".encode()).hexdigest()
    
    def _verify_password(self, password: str, hashed_password: str) -> bool:
        """パスワード検証"""
        # TODO: bcryptを使用した実装
        return password == hashed_password  # 暫定実装
    
    # TODO: メール送信機能実装
    # async def _send_magic_link_email(self, email: str, token: str):
    #     """Magic Linkメール送信"""
    #     pass 

    def _create_magic_link_token(self, email: str) -> str:
        """Magic Linkトークンを生成"""
        # タイムスタンプ + メールアドレス + ランダム文字列でトークンを生成
        timestamp = int(datetime.utcnow().timestamp())
        random_string = secrets.token_urlsafe(16)
        token_parts = [str(timestamp), email, random_string]
        token = base64.urlsafe_b64encode("_".join(token_parts).encode()).decode()

        # トークン情報を保存
        self._magic_link_tokens[token] = MagicLinkToken(
            token=token,
            email=email,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + AuthConfig.JWT_MAGIC_LINK_EXPIRE
        )

        return token

    def _verify_magic_link_token(self, token: str) -> Optional[str]:
        """Magic Linkトークンを検証"""
        token_info = self._magic_link_tokens.get(token)
        if not token_info:
            return None

        # 有効期限と使用済みチェック
        if (
            token_info.expires_at < datetime.utcnow() or
            token_info.used
        ):
            return None

        # トークンを使用済みにマーク
        token_info.used = True
        
        # 同じメールアドレスの未使用トークンを無効化
        for t in self._magic_link_tokens.values():
            if t.email == token_info.email and not t.used:
                t.used = True

        return token_info.email

    def _create_jwt_token(self, user: Dict[str, Any]) -> str:
        """JWTトークンを生成"""
        payload = {
            "user_id": user["user_id"],
            "email": user["email"],
            "exp": datetime.utcnow() + AuthConfig.JWT_ACCESS_TOKEN_EXPIRE
        }
        return jwt.encode(
            payload,
            AuthConfig.JWT_SECRET_KEY,
            algorithm=AuthConfig.JWT_ALGORITHM
        )

    async def login_as_test_user(
        self,
        user_number: int,
        db: Session
    ) -> Dict[str, Any]:
        """テストユーザーでログイン"""
        if not AuthConfig.is_test_user_allowed():
            raise HTTPException(403, "この機能は開発環境でのみ利用可能です")

        if not 1 <= user_number <= 5:
            raise HTTPException(400, "無効なユーザー番号です")

        # テストユーザー情報を取得
        user = AuthConfig.TEST_USERS[user_number - 1]

        # JWTを生成
        jwt_token = self._create_jwt_token(user)

        return {
            "success": True,
            "data": {
                "user": user,
                "token": jwt_token
            }
        } 