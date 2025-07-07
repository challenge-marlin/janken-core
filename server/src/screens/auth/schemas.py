"""
認証画面専用Pydanticスキーマ

認証画面で使用するリクエスト・レスポンススキーマを定義
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class MagicLinkRequest(BaseModel):
    """Magic Linkリクエストスキーマ"""
    email: EmailStr = Field(..., description="メールアドレス")
    captcha: Optional[dict] = Field(None, description="CAPTCHA情報")
    recaptcha_token: Optional[str] = Field(None, description="reCAPTCHAトークン")


class MagicLinkResponse(BaseModel):
    """Magic Linkレスポンススキーマ"""
    success: bool = Field(..., description="処理成功フラグ")
    message: str = Field(..., description="メッセージ")


class TokenVerifyRequest(BaseModel):
    """トークン検証リクエストスキーマ"""
    token: str = Field(..., description="Magic Linkトークン")


class DevLoginRequest(BaseModel):
    """開発用ログインリクエストスキーマ"""
    email: EmailStr = Field(..., description="メールアドレス")
    mode: str = Field(default="dev", description="ログインモード", pattern="^(dev|admin)$")


class UserInfo(BaseModel):
    """ユーザー情報スキーマ"""
    email: str = Field(..., description="メールアドレス")
    role: Optional[str] = Field(None, description="ユーザーロール")


class AuthResponse(BaseModel):
    """認証レスポンススキーマ"""
    success: bool = Field(..., description="処理成功フラグ")
    token: str = Field(..., description="JWTトークン")
    user: UserInfo = Field(..., description="ユーザー情報")


class LoginRequest(BaseModel):
    """ログインリクエストスキーマ（従来のUserInfo API用）"""
    user_id: str = Field(..., description="ユーザーID")
    password: str = Field(..., description="パスワード")


class LoginUserInfo(BaseModel):
    """ログインユーザー情報スキーマ"""
    user_id: str = Field(..., description="ユーザーID")
    nickname: str = Field(..., description="ニックネーム")
    title: Optional[str] = Field(None, description="称号")
    alias: Optional[str] = Field(None, description="二つ名")
    profile_image_url: Optional[str] = Field(None, description="プロフィール画像URL")


class LoginResponse(BaseModel):
    """ログインレスポンススキーマ"""
    success: bool = Field(..., description="処理成功フラグ")
    user: LoginUserInfo = Field(..., description="ユーザー情報")


class ErrorResponse(BaseModel):
    """エラーレスポンススキーマ"""
    success: bool = Field(default=False, description="処理成功フラグ")
    message: str = Field(..., description="エラーメッセージ")
    error: Optional[dict] = Field(None, description="エラー詳細") 