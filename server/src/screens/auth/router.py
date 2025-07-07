"""
認証関連のルーター
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .models import (
    MagicLinkRequest,
    MagicLinkVerifyRequest,
    TestLoginRequest,
    AuthResponse
)
from .services import AuthService
from ...shared.database.connection import get_db

router = APIRouter(prefix="/api/auth", tags=["auth"])
auth_service = AuthService()

@router.post("/request-link", response_model=AuthResponse)
async def request_magic_link(
    request: MagicLinkRequest,
    db: Session = Depends(get_db)
):
    """Magic Linkをリクエスト"""
    try:
        return await auth_service.request_magic_link(
            email=request.email,
            captcha=request.captcha,
            recaptcha_token=request.recaptcha_token,
            db=db
        )
    except HTTPException as e:
        return AuthResponse(
            success=False,
            message=str(e.detail),
            error={
                "code": "VALIDATION_ERROR",
                "details": str(e.detail)
            }
        )
    except Exception as e:
        return AuthResponse(
            success=False,
            message="サーバーエラーが発生しました",
            error={
                "code": "INTERNAL_SERVER_ERROR",
                "details": str(e)
            }
        )

@router.post("/verify-magic-link", response_model=AuthResponse)
async def verify_magic_link(
    request: MagicLinkVerifyRequest,
    db: Session = Depends(get_db)
):
    """Magic Linkを検証"""
    try:
        return await auth_service.verify_magic_link(
            token=request.token,
            db=db
        )
    except HTTPException as e:
        return AuthResponse(
            success=False,
            message=str(e.detail),
            error={
                "code": "INVALID_TOKEN",
                "details": str(e.detail)
            }
        )
    except Exception as e:
        return AuthResponse(
            success=False,
            message="サーバーエラーが発生しました",
            error={
                "code": "INTERNAL_SERVER_ERROR",
                "details": str(e)
            }
        )

@router.post("/test-login", response_model=AuthResponse)
async def test_login(
    request: TestLoginRequest,
    db: Session = Depends(get_db)
):
    """テストユーザーでログイン（開発環境専用）"""
    try:
        return await auth_service.login_as_test_user(
            user_number=request.user_number,
            db=db
        )
    except HTTPException as e:
        return AuthResponse(
            success=False,
            message=str(e.detail),
            error={
                "code": "INVALID_REQUEST",
                "details": str(e.detail)
            }
        )
    except Exception as e:
        return AuthResponse(
            success=False,
            message="サーバーエラーが発生しました",
            error={
                "code": "INTERNAL_SERVER_ERROR",
                "details": str(e)
            }
        ) 