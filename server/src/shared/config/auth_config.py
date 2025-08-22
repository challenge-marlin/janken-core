"""
認証関連の設定

環境別の認証設定や定数を管理します。
"""

from typing import Dict, Any, List
import os
from datetime import timedelta

class AuthConfig:
    """認証設定クラス"""
    
    # 環境設定
    ENVIRONMENTS = {
        "development": {
            "allow_test_users": True,
            "require_recaptcha": False,
            "require_captcha": False,
            "rate_limit": None,
            "magic_link_base_url": "http://localhost:3000/auth/verify"
        },
        "vps": {
            "allow_test_users": True,
            "require_recaptcha": False,
            "require_captcha": True,
            "rate_limit": "5/5minutes",
            "magic_link_base_url": "https://dev.myou-kou.com/auth/verify"
        },
        "aws": {
            "allow_test_users": False,
            "require_recaptcha": True,
            "require_captcha": True,
            "rate_limit": "5/5minutes",
            "magic_link_base_url": "https://myou-kou.com/auth/verify"
        }
    }

    # JWT設定
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key")
    JWT_ALGORITHM = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE = timedelta(hours=24)
    JWT_MAGIC_LINK_EXPIRE = timedelta(minutes=15)

    # メール設定
    MAIL_TEMPLATES = {
        "magic_link": {
            "subject": "[じゃんけんゲーム] ログインリンク",
            "template": """
こんにちは！

以下のリンクからログインしてください：
{magic_link_url}

このリンクは15分間有効です。
期限切れの場合は、再度ログインリンクを要求してください。

※このメールに心当たりがない場合は、無視してください。
            """.strip()
        }
    }

    # テストユーザー設定（Magic Link認証用）
    TEST_USERS: List[Dict[str, Any]] = [
        {
            "user_id": f"test_user_{i}",
            "email": f"test{i}@example.com",
            "nickname": f"テストユーザー{i}",
            "profile_image_url": f"https://lesson01.myou-kou.com/avatars/defaultAvatar{i}.png",
            "title": "テストプレイヤー",
            "alias": f"じゃんけんテスター{i}"
        }
        for i in range(1, 6)
    ]

    # ID/パスワード認証用サンプルユーザー設定
    SAMPLE_LOGIN_USERS: List[Dict[str, Any]] = [
        {
            "user_id": "",
            "password": "password123",
            "nickname": "サンプルユーザー1",
            "profile_image_url": "https://lesson01.myou-kou.com/avatars/defaultAvatar1.png",
            "title": "初心者プレイヤー",
            "alias": "じゃんけん初心者1"
        },
        {
            "user_id": "sample_user_2", 
            "password": "password456",
            "nickname": "サンプルユーザー2",
            "profile_image_url": "https://lesson01.myou-kou.com/avatars/defaultAvatar2.png",
            "title": "中級プレイヤー",
            "alias": "じゃんけん中級2"
        },
        {
            "user_id": "sample_user_3",
            "password": "password789", 
            "nickname": "サンプルユーザー3",
            "profile_image_url": "https://lesson01.myou-kou.com/avatars/defaultAvatar3.png",
            "title": "上級プレイヤー",
            "alias": "じゃんけん上級3"
        },
        {
            "user_id": "admin_user",
            "password": "admin123",
            "nickname": "管理者ユーザー",
            "profile_image_url": "https://lesson01.myou-kou.com/avatars/defaultAvatar4.png", 
            "title": "システム管理者",
            "alias": "じゃんけん管理者"
        },
        {
            "user_id": "demo_user",
            "password": "demo123",
            "nickname": "デモユーザー",
            "profile_image_url": "https://lesson01.myou-kou.com/avatars/defaultAvatar5.png",
            "title": "デモプレイヤー", 
            "alias": "じゃんけんデモ"
        }
    ]

    # CAPTCHA設定
    CAPTCHA_OPTIONS = ["✊", "✌️", "✋"]
    CAPTCHA_RULES = {
        "✊": "✌️",  # グーはチョキに勝つ
        "✌️": "✋",  # チョキはパーに勝つ
        "✋": "✊"   # パーはグーに勝つ
    }

    @classmethod
    def get_environment_config(cls) -> Dict[str, Any]:
        """現在の環境の設定を取得"""
        env = os.getenv("APP_ENV", "development")
        return cls.ENVIRONMENTS.get(env, cls.ENVIRONMENTS["development"])

    @classmethod
    def is_test_user_allowed(cls) -> bool:
        """テストユーザーの利用が許可されているか確認"""
        return cls.get_environment_config()["allow_test_users"]

    @classmethod
    def get_magic_link_base_url(cls) -> str:
        """Magic Link用のベースURLを取得"""
        return cls.get_environment_config()["magic_link_base_url"] 