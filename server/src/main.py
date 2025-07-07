"""
FastAPIメインアプリケーション

画面単位API分離原則に基づくじゃんけんゲームAPIサーバー
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import traceback
import logging

# ログレベルを設定
logging.basicConfig(level=logging.DEBUG)

from .config.settings import settings
from .screens.auth.router import router as auth_router
from .shared.exceptions.handlers import BaseApplicationError
from .infrastructure.monitoring.health import health_checker
from .infrastructure.monitoring.metrics_router import router as metrics_router

# ストレージルーターのインポートをtry-catchで囲む
try:
    from .infrastructure.storage.storage_router import router as storage_router
    print("DEBUG: ストレージルーターのインポートに成功しました")
except Exception as e:
    print(f"ERROR: ストレージルーターのインポートに失敗: {str(e)}")
    import traceback
    print(f"Traceback: {traceback.format_exc()}")
    storage_router = None


# FastAPIアプリケーション初期化
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    debug=settings.debug,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)


# 画面単位ルーター登録
app.include_router(auth_router, prefix="/api")

# インフラストラクチャルーター登録
app.include_router(metrics_router)  # /api/metrics, /api/status

# ストレージルーターの登録をtry-catchで囲む
if storage_router is not None:
    try:
        app.include_router(storage_router)  # /storage/*
        print("DEBUG: ストレージルーターの登録に成功しました")
    except Exception as e:
        print(f"ERROR: ストレージルーターの登録に失敗: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
else:
    print("ERROR: ストレージルーターがNoneのため登録をスキップしました")

# デバッグ: 登録されたルートを確認
print("=== 登録されたルート一覧 ===")
for route in app.routes:
    if hasattr(route, 'path') and hasattr(route, 'methods'):
        print(f"Path: {route.path}, Methods: {route.methods}")
print("=== ルート一覧終了 ===")


# グローバル例外ハンドラー
@app.exception_handler(BaseApplicationError)
async def base_application_exception_handler(request, exc: BaseApplicationError):
    """アプリケーション例外ハンドラー"""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            **exc.to_dict()
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """HTTP例外ハンドラー"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": "HTTP_ERROR",
                "message": exc.detail,
                "details": {}
            }
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """一般的な例外ハンドラー"""
    # デバッグモードの場合、詳細なエラー情報を返す
    if settings.debug:
        logging.error(f"Unhandled exception: {exc}")
        logging.error(f"Traceback: {traceback.format_exc()}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": str(exc),
                    "details": {
                        "type": type(exc).__name__,
                        "traceback": traceback.format_exc()
                    }
                }
            }
        )
    else:
        logging.error(f"Unhandled exception: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "サーバーエラーが発生しました",
                    "details": {}
                }
            }
        )


# ヘルスチェックエンドポイント
@app.get("/api/health")
async def health_check():
    """アプリケーションヘルスチェック"""
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "app_version": settings.app_version,
        "environment": settings.environment,
        "message": "かみのてじゃんけんAPIサーバーは正常に動作しています"
    }


# 詳細ヘルスチェック
@app.get("/api/health/detailed")
async def detailed_health_check():
    """詳細なヘルスチェック（全サービス）"""
    result = await health_checker.check_all_services()
    status_code = 200 if result["overall_status"] == "healthy" else 503
    return JSONResponse(status_code=status_code, content=result)


# MySQL状態チェック
@app.get("/api/health/mysql")
async def mysql_health_check():
    """MySQL接続状態チェック"""
    try:
        result = await health_checker._check_mysql()
        return {
            "status": "healthy",
            "service": "mysql",
            "details": result
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "service": "mysql",
                "message": str(e)
            }
        )


# Redis状態チェック
@app.get("/api/health/redis")
async def redis_health_check():
    """Redis接続状態チェック"""
    try:
        result = await health_checker._check_redis()
        return {
            "status": "healthy",
            "service": "redis",
            "details": result
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "service": "redis",
                "message": str(e)
            }
        )


# MinIO状態チェック
@app.get("/api/health/minio")
async def minio_health_check():
    """MinIO接続状態チェック"""
    try:
        result = await health_checker._check_minio()
        return {
            "status": "healthy",
            "service": "minio",
            "details": result
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "service": "minio",
                "message": str(e)
            }
        )


# OCR処理エンドポイント
@app.post("/api/ocr/process")
async def ocr_process():
    """OCR処理（画像OCR機能）"""
    try:
        # TODO: 実際のOCR処理実装
        return {
            "status": "success",
            "text": "OCR処理結果（モック）",
            "message": "OCR処理が完了しました"
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"OCR処理エラー: {str(e)}"
            }
        )


# 開発用エンドポイント
if settings.debug:
    @app.get("/api/debug/info")
    async def debug_info():
        """開発用デバッグ情報"""
        return {
            "settings": {
                "app_name": settings.app_name,
                "environment": settings.environment,
                "debug": settings.debug,
                "db_host": settings.db_host,
                "redis_host": settings.redis_host,
                "minio_endpoint": settings.minio_endpoint
            },
            "message": "デバッグ情報（開発環境のみ）"
        }


# アプリケーション起動
if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=3000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    ) 