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
from ...shared.database.connection import get_db_session

router = APIRouter(prefix="/api/auth", tags=["auth"])
auth_service = AuthService()

@router.post("/request-link", response_model=AuthResponse)
async def request_magic_link(request: MagicLinkRequest):
    """Magic Linkをリクエスト"""
    try:
        result = await auth_service.request_magic_link(
            email=request.email,
            captcha=request.captcha,
            recaptcha_token=request.recaptcha_token,
            db=None  # データベース接続なし（開発用）
        )
        
        return AuthResponse(
            success=True,
            data=result
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
async def verify_magic_link(request: MagicLinkVerifyRequest):
    """Magic Linkを検証"""
    try:
        result = await auth_service.verify_magic_link(
            token=request.token,
            db=None  # データベース接続なし（開発用）
        )
        
        return AuthResponse(
            success=True,
            data=result
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
    db: Session = Depends(get_db_session)
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

@router.post("/dev-login", response_model=AuthResponse)
async def dev_login(
    request: dict,
    db: Session = Depends(get_db_session)
):
    """開発用簡易認証（開発/VPS環境のみ）"""
    try:
        email = request.get("email")
        mode = request.get("mode", "dev")
        
        result = await auth_service.dev_login(
            email=email,
            mode=mode
        )
        
        return AuthResponse(
            success=True,
            data=result
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

@router.post("/UserInfo", response_model=AuthResponse)
async def user_info_login(
    request: dict,
    db: Session = Depends(get_db_session)
):
    """従来形式ログイン（互換性維持）"""
    try:
        user_id = request.get("userId")
        password = request.get("password")
        
        result = await auth_service.user_info_login(
            user_id=user_id,
            password=password,
            db=db
        )
        
        return AuthResponse(
            success=True,
            data=result
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

@router.get("/protected-test")
async def protected_test(
    current_user: dict = Depends(auth_service.get_current_user)
):
    """認証テスト用の保護されたエンドポイント"""
    return {
        "success": True,
        "message": "認証が成功しました",
        "user": current_user
    }

@router.get("/simple-test")
async def simple_test():
    """シンプルな動作確認用エンドポイント"""
    return {
        "success": True,
        "message": "認証APIは正常に動作しています",
        "timestamp": "2024-01-01T00:00:00Z"
    }

@router.post("/simple-dev-login")
async def simple_dev_login(request: dict):
    """シンプルな開発用ログイン（データベース接続なし）"""
    try:
        email = request.get("email", "test@example.com")
        
        # 簡単なJWT生成（データベース接続なし）
        from ...shared.services.jwt_service import jwt_service
        
        user_data = {
            "email": email,
            "user_id": f"dev_{email.split('@')[0]}",
            "nickname": f"開発者_{email.split('@')[0]}",
            "role": "developer"
        }
        
        jwt_token = jwt_service.generate_token(user_data)
        
        return {
            "success": True,
            "data": {
                "token": jwt_token,
                "user": user_data
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": {
                "code": "SIMPLE_LOGIN_ERROR",
                "message": str(e)
            }
        } 