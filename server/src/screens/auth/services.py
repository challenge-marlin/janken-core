"""
認証画面専用サービス

認証画面で使用するビジネスロジックを実装
"""

import hashlib
import secrets
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import select
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
    create_captcha_expires_at, UserStats, AuthCredentials, UserProfile
)
from ...shared.services.jwt_service import jwt_service
from ...shared.services.redis_service import redis_service
from ...shared.database.connection import get_db_session as get_db
from ...shared.config.auth_config import AuthConfig
from ...shared.services.email_service import EmailService
from fastapi.security import HTTPBearer
from fastapi import Depends
from .models import MagicLinkToken
import base64


class AuthService:
    """認証画面専用サービスクラス"""
    
    def __init__(self):
        self.jwt_service = jwt_service
        self.email_service = EmailService()
        self._magic_link_tokens: Dict[str, MagicLinkToken] = {}
        self.security = HTTPBearer()
    
    async def request_magic_link(
        self,
        email: str,
        captcha: Optional[Dict] = None,
        recaptcha_token: Optional[str] = None,
        db: Optional[Session] = None
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
        
        print(f"🔍 [DEBUG] Magic Link生成: email={email}, token={magic_token[:20]}..., hash={token_hash[:20]}...")
        
        # データベース接続の処理を簡略化（開発用）
        if db is None:
            # 開発モード: Redisでの一時保存（永続的で信頼性が高い）
            # Redisにトークンを保存
            redis_service.set_magic_link_token(token_hash, {
                "email": email,
                "token": magic_token,
                "expires_at": create_magic_link_expires_at(),
                "used": False,
                "created_at": datetime.utcnow()
            })
            
            print(f"🔍 [DEBUG] Redis保存完了: 保存件数={redis_service.get_magic_link_count()}")
            
            result = {
                "message": "Magic link sent.",
                "token": magic_token  # 開発環境ではトークンを直接返却
            }
            return result
        
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
            if db:
                db.rollback()
            raise BusinessLogicError(f"Magic Link作成に失敗しました: {str(e)}")
        finally:
            if db:
                db.close()
    
    async def verify_magic_link(self, token: str, db: Optional[Session] = None) -> Dict[str, Any]:
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
        
        print(f"🔍 [DEBUG] Magic Link検証開始: token={token[:20]}...")
        
        # データベース接続なしの場合（開発モード）
        if db is None:
            # 開発モード: Redisでの検証（永続的で信頼性が高い）
            token_hash = self._hash_token(token)
            print(f"🔍 [DEBUG] トークンハッシュ計算: hash={token_hash[:20]}...")
            print(f"🔍 [DEBUG] Redis内トークン数: {redis_service.get_magic_link_count()}")
            
            # Redisからトークンを検索
            token_data = redis_service.get_magic_link_token(token_hash)
            
            if not token_data:
                print(f"❌ [DEBUG] トークンが見つかりません: hash={token_hash[:20]}...")
                raise AuthenticationError("無効なMagic Linkトークンです")
            
            print(f"🔍 [DEBUG] トークン発見: email={token_data['email']}")
            
            # 有効期限チェック
            if datetime.utcnow() > token_data["expires_at"]:
                print(f"❌ [DEBUG] 有効期限切れ: expires_at={token_data['expires_at']}")
                raise AuthenticationError("Magic Linkの有効期限が切れています")
            
            # 使用済みチェック
            if token_data["used"]:
                print(f"❌ [DEBUG] 既に使用済み")
                raise AuthenticationError("このMagic Linkは既に使用されています")
            
            # トークンを使用済みにマーク（Redisで更新）
            redis_service.update_magic_link_token(token_hash, {"used": True})
            print(f"✅ [DEBUG] トークン検証成功")
            
            # ユーザーデータ生成
            user_data = {
                "email": token_data["email"],
                "user_id": f"magic_user_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                "nickname": "Magic User",
                "role": "user",
                "last_login": datetime.utcnow().isoformat()
            }
            
            # JWT生成
            jwt_token = self.jwt_service.generate_token({
                "email": user_data["email"],
                "user_id": user_data["user_id"],
                "nickname": user_data["nickname"],
                "role": user_data["role"]
            })
            
            return {
                "token": jwt_token,
                "user": user_data
            }
        
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
            if db:
                db.rollback()
            if isinstance(e, AuthenticationError):
                raise
            raise AuthenticationError(f"トークン検証に失敗しました: {str(e)}")
        finally:
            if db:
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
        
        # 開発環境の場合、サンプルユーザーで認証
        if settings.environment == "development":
            return await self._authenticate_sample_user(user_id, password)
        
        # 本番環境の場合、データベースで認証
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

    async def _authenticate_sample_user(self, user_id: str, password: str) -> Dict[str, Any]:
        """
        開発環境用サンプルユーザー認証
        
        Args:
            user_id: ユーザーID
            password: パスワード
            
        Returns:
            ユーザー情報とJWTトークン
            
        Raises:
            AuthenticationError: 認証エラー
        """
        # サンプルユーザーから検索
        sample_user = None
        for user in AuthConfig.SAMPLE_LOGIN_USERS:
            if user["user_id"] == user_id and user["password"] == password:
                sample_user = user
                break
        
        if not sample_user:
            raise AuthenticationError("ユーザーIDまたはパスワードが正しくありません")
        
        # JWTトークン生成
        jwt_token = self._create_jwt_token({
            "user_id": sample_user["user_id"],
            "email": f"{sample_user['user_id']}@example.com",
            "nickname": sample_user["nickname"]
        })
        
        return {
            "user": {
                "user_id": sample_user["user_id"],
                "nickname": sample_user["nickname"],
                "title": sample_user["title"],
                "alias": sample_user["alias"],
                "profile_image_url": sample_user["profile_image_url"]
            },
            "token": jwt_token
        }
    
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
                profile_image_url='defaultAvatar1',
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
            "nickname": user.get("nickname", ""),
            "exp": datetime.utcnow() + AuthConfig.JWT_ACCESS_TOKEN_EXPIRE,
            "iss": "janken-api",  # 発行者を追加
            "aud": "janken-app"   # 対象者を追加
        }
        # JWTサービスと同じシークレットキーを使う
        from ...shared.config.settings import settings
        return jwt.encode(
            payload,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm
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
            "user": user,
            "token": jwt_token
        }
    
    async def get_current_user(self, token: str = Depends(HTTPBearer())):
        """
        現在のユーザーを認証トークンから取得
        
        Args:
            token: HTTPBearerから取得されたトークン
            
        Returns:
            ユーザー情報
            
        Raises:
            HTTPException: 認証エラー
        """
        try:
            # JWTトークン検証
            payload = self.jwt_service.verify_token(token.credentials)
            
            return {
                "email": payload.get("email"),
                "user_id": payload.get("user_id"),
                "nickname": payload.get("nickname"),
                "role": payload.get("role", "user")
            }
        except Exception as e:
            raise HTTPException(
                status_code=401,
                detail=f"認証に失敗しました: {str(e)}"
            )

    async def get_current_user_from_token(self, token: str) -> Dict[str, Any]:
        """
        トークン文字列から直接ユーザー情報を取得
        
        Args:
            token: JWT トークン文字列
            
        Returns:
            ユーザー情報
            
        Raises:
            AuthenticationError: 認証エラー
        """
        try:
            # JWTトークン検証
            payload = self.jwt_service.verify_token(token)
            
            return {
                "email": payload.get("email"),
                "user_id": payload.get("user_id"),
                "nickname": payload.get("nickname"),
                "role": payload.get("role", "user"),
                "exp": payload.get("exp"),
                "iat": payload.get("iat")
            }
        except Exception as e:
            raise AuthenticationError(f"認証に失敗しました: {str(e)}")

    async def login_with_db_credentials(
        self,
        email: str,
        password: str
    ) -> Dict[str, Any]:
        """
        DBに保存された認証情報を使用したログイン
        
        Args:
            email: メールアドレス
            password: パスワード
            
        Returns:
            ログイン結果（ユーザー情報とトークン）
            
        Raises:
            AuthenticationError: 認証エラー
        """
        try:
            # 非同期データベース接続
            from ...shared.database.connection_improved import get_async_session
            
            async with get_async_session() as db:
                # ユーザー情報を取得
                result = await db.execute(
                    select(User).where(User.email == email)
                )
                user = result.scalar_one_or_none()
                
                if not user:
                    raise AuthenticationError("ユーザーが見つかりません")
                
                # 認証資格情報を取得
                result = await db.execute(
                    select(AuthCredentials).where(AuthCredentials.user_id == user.user_id)
                )
                auth_cred = result.scalar_one_or_none()
                
                if not auth_cred:
                    raise AuthenticationError("認証情報が見つかりません")
                
                # パスワード検証
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                if auth_cred.password_hash != password_hash:
                    raise AuthenticationError("パスワードが正しくありません")
                
                # ユーザープロフィール情報を取得
                result = await db.execute(
                    select(UserProfile).where(UserProfile.user_id == user.user_id)
                )
                user_profile = result.scalar_one_or_none()
                
                # ユーザー統計情報を取得
                result = await db.execute(
                    select(UserStats).where(UserStats.user_id == user.user_id)
                )
                user_stats = result.scalar_one_or_none()
                
                # レスポンス用のユーザー情報を構築
                user_data = {
                    "user_id": user.user_id,
                    "email": user.email,
                    "nickname": user.nickname,
                    "role": getattr(user, 'role', 'user'),
                    "title": getattr(user, 'title', ''),
                    "alias": getattr(user, 'alias', ''),
                    "created_at": getattr(user, 'created_at', None),
                    "updated_at": getattr(user, 'updated_at', None),
                    "profile": {
                        "register_type": user_profile.register_type if user_profile else "email"
                    },
                    "stats": {
                        "total_matches": getattr(user_stats, 'total_matches', 0) if user_stats else 0,
                        "total_wins": getattr(user_stats, 'total_wins', 0) if user_stats else 0,
                        "total_losses": getattr(user_stats, 'total_losses', 0) if user_stats else 0,
                        "total_draws": getattr(user_stats, 'total_draws', 0) if user_stats else 0,
                        "win_rate": float(getattr(user_stats, 'win_rate', 0.0)) if user_stats else 0.0,
                        "current_streak": getattr(user_stats, 'current_streak', 0) if user_stats else 0,
                        "best_streak": getattr(user_stats, 'best_streak', 0) if user_stats else 0
                    } if user_stats else {}
                }
                
                # JWTトークンを生成
                jwt_token = self._create_jwt_token(user_data)
                
                return {
                    "user": user_data,
                    "token": jwt_token
                }
            
        except Exception as e:
            if isinstance(e, AuthenticationError):
                raise e
            raise AuthenticationError(f"ログイン処理に失敗しました: {str(e)}") 