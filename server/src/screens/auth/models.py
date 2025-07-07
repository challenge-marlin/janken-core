"""
認証関連のモデル定義
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class MagicLinkRequest(BaseModel):
    """Magic Linkリクエストモデル"""
    email: EmailStr
    captcha: Optional[dict] = None
    recaptcha_token: Optional[str] = None

class MagicLinkVerifyRequest(BaseModel):
    """Magic Link検証リクエストモデル"""
    token: str

class TestLoginRequest(BaseModel):
    """テストユーザーログインリクエストモデル"""
    user_number: int = Field(..., ge=1, le=5)

class CaptchaChallenge(BaseModel):
    """CAPTCHAチャレンジモデル"""
    opponent: str
    answer: str
    token: str

class UserResponse(BaseModel):
    """ユーザー情報レスポンスモデル"""
    user_id: str
    email: str
    nickname: str
    profile_image_url: Optional[str] = None
    title: Optional[str] = None
    alias: Optional[str] = None

class AuthResponse(BaseModel):
    """認証レスポンスモデル"""
    success: bool
    message: Optional[str] = None
    data: Optional[dict] = None
    error: Optional[dict] = None

class MagicLinkToken(BaseModel):
    """Magic Linkトークンモデル"""
    token: str
    email: str
    created_at: datetime
    expires_at: datetime
    used: bool = False 