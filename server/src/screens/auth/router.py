"""
認証画面専用FastAPIルーター

認証画面で使用する専用APIエンドポイントを定義
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import JSONResponse

from .schemas import (
    MagicLinkRequest, MagicLinkResponse,
    DevLoginRequest, AuthResponse,
    LoginRequest, LoginResponse,
    ErrorResponse
)
from .services import AuthService
from ...shared.exceptions.handlers import (
    AuthenticationError, ValidationError, BaseApplicationError
)

# 認証画面専用ルーター
router = APIRouter(
    prefix="/auth",
    tags=["認証画面専用API"],
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)

# サービス依存性注入
def get_auth_service() -> AuthService:
    return AuthService()


@router.post("/request-link", response_model=MagicLinkResponse)
async def request_magic_link(
    request: MagicLinkRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Magic Linkリクエスト（認証画面専用）
    
    認証画面でのMagic Link認証要求を処理します。
    他画面からの使用は禁止されています。
    """
    try:
        result = await auth_service.request_magic_link(
            email=request.email,
            captcha=request.captcha,
            recaptcha_token=request.recaptcha_token
        )
        return MagicLinkResponse(
            success=True,
            message="Magic link sent."
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.to_dict())
    except BaseApplicationError as e:
        raise HTTPException(status_code=500, detail=e.to_dict())


@router.get("/verify", response_model=AuthResponse)
async def verify_magic_link(
    token: str = Query(..., description="Magic Linkトークン"),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Magic Linkトークン検証（認証画面専用）
    
    認証画面でのMagic Linkトークン検証を処理します。
    他画面からの使用は禁止されています。
    """
    try:
        result = await auth_service.verify_magic_link(token)
        return AuthResponse(
            success=True,
            token=result["token"],
            user=result["user"]
        )
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=e.to_dict())
    except BaseApplicationError as e:
        raise HTTPException(status_code=500, detail=e.to_dict())


@router.post("/dev-login", response_model=AuthResponse)
async def dev_login(
    request: DevLoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    開発用簡易認証（認証画面専用・開発/VPS環境のみ）
    
    認証画面での開発用JWT即時発行を処理します。
    AWS環境では無効化されます。
    他画面からの使用は禁止されています。
    """
    try:
        result = await auth_service.dev_login(
            email=request.email,
            mode=request.mode
        )
        return AuthResponse(
            success=True,
            token=result["token"],
            user=result["user"]
        )
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=e.to_dict())
    except BaseApplicationError as e:
        raise HTTPException(status_code=500, detail=e.to_dict())


@router.post("/UserInfo", response_model=LoginResponse)
async def user_info_login(
    request: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    ログイン（認証画面専用・従来API互換）
    
    認証画面での従来形式ログインを処理します。
    API仕様書のPOST /UserInfoに対応。
    他画面からの使用は禁止されています。
    """
    try:
        result = await auth_service.user_info_login(
            user_id=request.user_id,
            password=request.password
        )
        return LoginResponse(
            success=True,
            user=result["user"]
        )
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=e.to_dict())
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.to_dict())
    except BaseApplicationError as e:
        raise HTTPException(status_code=500, detail=e.to_dict())


@router.get("/health")
async def auth_health_check():
    """
    認証画面API用ヘルスチェック
    
    認証画面専用APIの動作確認用エンドポイント
    """
    return {
        "status": "healthy",
        "service": "auth_screen_api",
        "message": "認証画面専用APIは正常に動作しています"
    } 