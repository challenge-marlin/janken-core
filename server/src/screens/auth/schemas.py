"""
認証画面専用Pydanticスキーマ

Laravel風のRequest/Resourceクラスに相当するPydanticスキーマを定義
入出力データの構造とバリデーションを担当
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field, validator


# ========================================
# Requestスキーマ（LaravelのFormRequestに相当）
# ========================================

class MagicLinkRequest(BaseModel):
    """Magic Linkリクエスト - LaravelのFormRequestに相当"""
    email: EmailStr = Field(..., description="メールアドレス")
    captcha: Optional[Dict[str, Any]] = Field(None, description="CAPTCHA情報")
    recaptcha_token: Optional[str] = Field(None, description="reCAPTCHAトークン")
    
    @validator('email')
    def validate_email(cls, v):
        """メールアドレス形式検証"""
        if not v or len(v) < 5:
            raise ValueError('有効なメールアドレスを入力してください')
        return v.lower()


class MagicLinkVerifyRequest(BaseModel):
    """Magic Link検証リクエスト"""
    token: str = Field(..., min_length=1, description="Magic Linkトークン")
    
    @validator('token')
    def validate_token(cls, v):
        """トークン形式検証"""
        if not v or len(v) < 10:
            raise ValueError('有効なトークンが必要です')
        return v


class TestLoginRequest(BaseModel):
    """テストユーザーログインリクエスト"""
    user_number: int = Field(..., ge=1, le=5, description="テストユーザー番号（1-5）")


class DevLoginRequest(BaseModel):
    """開発用ログインリクエスト"""
    email: EmailStr = Field(..., description="メールアドレス")
    mode: str = Field(default="dev", pattern="^(dev|admin)$", description="ログインモード")


class UserInfoLoginRequest(BaseModel):
    """従来形式ログインリクエスト（互換性維持）"""
    userId: str = Field(..., alias="userId", description="ユーザーID")  # 既存API互換
    password: str = Field(..., description="パスワード")
    
    class Config:
        populate_by_name = True


class DBLoginRequest(BaseModel):
    """DBありきログインリクエスト"""
    email: EmailStr = Field(..., description="メールアドレス")
    password: str = Field(..., min_length=1, description="パスワード")
    
    @validator('email')
    def validate_email(cls, v):
        """メールアドレス形式検証"""
        if not v or len(v) < 5:
            raise ValueError('有効なメールアドレスを入力してください')
        return v.lower()


# ========================================
# Responseスキーマ（LaravelのResourceに相当）
# ========================================

class UserResource(BaseModel):
    """ユーザー情報リソース - LaravelのResourceに相当"""
    user_id: str = Field(..., description="ユーザーID")
    email: str = Field(..., description="メールアドレス")
    nickname: str = Field(..., description="ニックネーム")
    name: Optional[str] = Field(None, description="実名")
    role: str = Field(..., description="ユーザーロール")
    profile_image_url: Optional[str] = Field(None, description="プロフィール画像URL")
    title: Optional[str] = Field(None, description="ユーザー称号")
    alias: Optional[str] = Field(None, description="別名")
    is_active: bool = Field(..., description="アカウント有効性")
    created_at: datetime = Field(..., description="作成日時")
    
    class Config:
        from_attributes = True  # SQLAlchemyモデルからの変換を許可


class AuthTokenResource(BaseModel):
    """認証トークンリソース"""
    access_token: str = Field(..., description="アクセストークン")
    token_type: str = Field(default="bearer", description="トークンタイプ")
    expires_in: int = Field(..., description="有効期限（秒）")
    refresh_token: Optional[str] = Field(None, description="リフレッシュトークン")


class AuthResponse(BaseModel):
    """認証レスポンス - Laravel風の統一レスポンス形式"""
    success: bool = Field(..., description="処理成功フラグ")
    message: Optional[str] = Field(None, description="メッセージ")
    data: Optional[Dict[str, Any]] = Field(None, description="データ")
    error: Optional[Dict[str, Any]] = Field(None, description="エラー情報")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="レスポンス時刻")


class MagicLinkResponse(BaseModel):
    """Magic Linkレスポンス"""
    success: bool = Field(..., description="処理成功フラグ")
    message: str = Field(..., description="メッセージ")
    token: Optional[str] = Field(None, description="開発用トークン")  # 開発環境のみ


class LoginSuccessResponse(BaseModel):
    """ログイン成功レスポンス"""
    success: bool = Field(default=True, description="処理成功フラグ")
    user: UserResource = Field(..., description="ユーザー情報")
    auth: AuthTokenResource = Field(..., description="認証トークン情報")
    session_id: Optional[str] = Field(None, description="セッションID")


class ValidationErrorResponse(BaseModel):
    """バリデーションエラーレスポンス - LaravelのValidationException相当"""
    success: bool = Field(default=False, description="処理成功フラグ")
    message: str = Field(default="Validation failed", description="エラーメッセージ")
    errors: Dict[str, list] = Field(..., description="フィールド別エラー")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="エラー発生時刻")


# ========================================
# 内部データ転送用スキーマ
# ========================================

class TokenClaims(BaseModel):
    """JWTクレーム - トークン内部データ"""
    sub: str = Field(..., description="ユーザーID")
    email: str = Field(..., description="メールアドレス")
    nickname: str = Field(..., description="ニックネーム")
    role: str = Field(..., description="ユーザーロール")
    iat: int = Field(..., description="発行時刻")
    exp: int = Field(..., description="有効期限")
    jti: str = Field(..., description="JTI（JWT ID）")


class CaptchaChallenge(BaseModel):
    """CAPTCHAチャレンジデータ"""
    challenge_id: str = Field(..., description="チャレンジID")
    question: str = Field(..., description="問題文")
    expected_answer: str = Field(..., description="正解")
    expires_at: datetime = Field(..., description="有効期限") 