"""
認証画面専用ルーター - LaravelのControllerに相当

Laravel風のコントローラーパターンに従い、明確な責任分離と
統一されたエラーハンドリングを実装
"""

from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import datetime

from .schemas import (
    MagicLinkRequest,
    MagicLinkVerifyRequest, 
    TestLoginRequest,
    DevLoginRequest,
    UserInfoLoginRequest,
    AuthResponse,
    LoginSuccessResponse,
    MagicLinkResponse
)
from .services import AuthService
from .repositories import UserRepository, get_user_repository
from ...shared.database.connection import get_db_session
from ...shared.exceptions.handlers import (
    APIException, 
    ValidationError, 
    AuthenticationError,
    handle_validation_error
)

# Laravel風のルーター設定
router = APIRouter(
    prefix="/api/auth",
    tags=["認証画面"],
    responses={
        400: {"description": "バリデーションエラー"},
        401: {"description": "認証エラー"},
        403: {"description": "権限エラー"},
        500: {"description": "サーバーエラー"}
    }
)

# AuthServiceインスタンス作成（Dependency Injection用）
def get_auth_service() -> AuthService:
    """AuthServiceのDependency Injection"""
    return AuthService()

# ========================================
# Laravel風のコントローラーメソッド
# ========================================

@router.post("/request-magic-link", response_model=AuthResponse)
async def request_magic_link(
    request: MagicLinkRequest,
    http_request: Request,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Magic Linkリクエスト - Laravel風: AuthController@requestMagicLink
    
    Args:
        request: Magic Linkリクエストデータ
        http_request: HTTPリクエスト情報（IP取得用）
        auth_service: 認証サービス（DI）
    
    Returns:
        認証レスポンス
    
    Raises:
        APIException: 業務エラー（自動的にエラーハンドラーで処理）
    """
    # Laravel風: $request->validate() に相当（Pydanticで自動実行）
    
    try:
        # IPアドレス取得（Laravel風: $request->ip()）
        client_ip = http_request.client.host if http_request.client else "unknown"
        
        # サービス層に処理を委譲（Laravel風の責任分離）
        result = await auth_service.request_magic_link(
            email=request.email,
            captcha=request.captcha,
            recaptcha_token=request.recaptcha_token,
            db=None  # 開発環境のため、DBなしで動作
        )
        
        return AuthResponse(
            success=True,
            message="Magic link sent successfully",
            data=result
        )
    except ValidationError as e:
        return AuthResponse(
            success=False,
            message=str(e),
            error={
                "code": "VALIDATION_ERROR",
                "details": str(e)
            }
        )
    except Exception as e:
        return AuthResponse(
            success=False,
            message="Magic Linkリクエストに失敗しました",
            error={
                "code": "MAGIC_LINK_ERROR",
                "details": str(e)
            }
        )

@router.post("/verify-magic-link", response_model=AuthResponse)
async def verify_magic_link(
    request: MagicLinkVerifyRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
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



@router.post("/dev-login", response_model=AuthResponse)
async def dev_login(
    request: dict,
    auth_service: AuthService = Depends(get_auth_service)
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
    except Exception as e:
        return AuthResponse(
            success=False,
            message="サーバーエラーが発生しました",
            error={
                "code": "INTERNAL_SERVER_ERROR",
                "details": str(e)
            }
        )

@router.post("/user-info", response_model=AuthResponse)
async def user_info_login(
    request: UserInfoLoginRequest,
    http_request: Request,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    従来形式ログイン - Laravel風: AuthController@userInfoLogin
    
    互換性維持のため既存のUserInfo APIを snake_case に変更
    
    Args:
        request: ユーザー情報ログインリクエスト
        http_request: HTTPリクエスト情報
        auth_service: 認証サービス（DI）
    
    Returns:
        認証レスポンス
    """
    try:
        # IPアドレス取得
        client_ip = http_request.client.host if http_request.client else "unknown"
        
        # サービス層に処理を委譲
        result = await auth_service.user_info_login(
            user_id=request.userId,  # 既存API互換のためaliasを使用
            password=request.password
        )
        
        return AuthResponse(
            success=True,
            message="ログインに成功しました",
            data=result
        )
    except ValidationError as e:
        return AuthResponse(
            success=False,
            message=str(e),
            error={
                "code": "VALIDATION_ERROR",
                "details": str(e)
            }
        )
    except AuthenticationError as e:
        return AuthResponse(
            success=False,
            message=str(e),
            error={
                "code": "AUTHENTICATION_ERROR",
                "details": str(e)
            }
        )
    except Exception as e:
        return AuthResponse(
            success=False,
            message="ログインに失敗しました",
            error={
                "code": "LOGIN_ERROR",
                "details": str(e)
            }
        )

# 既存API互換性のための移行用エンドポイント（非推奨）
@router.post("/UserInfo", response_model=AuthResponse, deprecated=True)
async def user_info_login_legacy(
    request: dict,
    http_request: Request,
    auth_service: AuthService = Depends(get_auth_service),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """
    【非推奨】従来形式ログイン（互換性維持）
    
    新しいクライアントは /user-info を使用してください
    """
    # 型安全でないdict形式を変換
    user_info_request = UserInfoLoginRequest(
        userId=request.get("userId", ""),
        password=request.get("password", "")
    )
    
    # 新しいエンドポイントに転送
    result = await user_info_login(user_info_request, http_request, auth_service)
    
    # 既存形式のレスポンスとして返す
    return result

@router.get("/verify-token", response_model=AuthResponse)
async def verify_token(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    トークン検証 - Laravel風: AuthController@verifyToken
    
    認証が必要な保護されたエンドポイントのテスト用
    
    Args:
        request: HTTPリクエスト（Authorizationヘッダーから）
        auth_service: 認証サービス（DI）
    
    Returns:
        認証レスポンス
    """
    try:
        # Authorizationヘッダーからトークンを取得
        authorization = request.headers.get("authorization")
        if not authorization:
            return AuthResponse(
                success=False,
                message="認証トークンが必要です",
                error={
                    "code": "TOKEN_MISSING",
                    "details": "Authorizationヘッダーが見つかりません"
                }
            )
        
        # Bearer トークンの形式チェック
        if not authorization.startswith("Bearer "):
            return AuthResponse(
                success=False,
                message="不正なトークン形式です",
                error={
                    "code": "INVALID_TOKEN_FORMAT",
                    "details": "Bearer形式で送信してください"
                }
            )
        
        # トークンを抽出
        token = authorization.replace("Bearer ", "")
        
        # JWTトークンを検証
        current_user = await auth_service.get_current_user_from_token(token)
        
        return AuthResponse(
            success=True,
            message="Token is valid",
            data={
                "user": current_user,
                "authenticated": True,
                "token_info": {
                    "valid": True,
                    "type": "Bearer"
                }
            }
        )
    except Exception as e:
        return AuthResponse(
            success=False,
            message="トークン検証に失敗しました",
            error={
                "code": "TOKEN_VERIFICATION_FAILED",
                "details": str(e)
            }
        )

@router.get("/health", response_model=AuthResponse)
async def health_check():
    """
    認証サービスヘルスチェック - Laravel風: AuthController@health
    
    サービスの動作確認用エンドポイント
    
    Returns:
        ヘルスチェックレスポンス
    """
    return AuthResponse(
        success=True,
        message="認証サービスは正常に動作しています",
        data={
            "service": "auth",
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat()
        }
    )



@router.post("/test-login", response_model=AuthResponse)
async def test_login(
    request: TestLoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    テストユーザーログイン - Laravel風: AuthController@testLogin
    
    開発環境専用のテストユーザー認証機能
    
    Args:
        request: テストログインリクエスト
        auth_service: 認証サービス（DI）
    
    Returns:
        認証レスポンス
    """
    try:
        # サービス層に処理を委譲（既存のlogin_as_test_userメソッドを使用）
        result = await auth_service.login_as_test_user(
            user_number=request.user_number,
            db=None  # 開発環境のため、DBなしで動作
        )
        
        return AuthResponse(
            success=True,
            data=result  # login_as_test_userは{"user": {...}, "token": "..."}を返す
        )
    except Exception as e:
        return AuthResponse(
            success=False,
            message="テストユーザーログインに失敗しました",
            error={
                "code": "TEST_LOGIN_ERROR", 
                "details": str(e)
            }
        ) 