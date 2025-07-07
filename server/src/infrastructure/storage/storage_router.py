"""
ストレージ管理用FastAPIルーター

ファイルアップロード、管理、統計取得などのエンドポイントを提供
"""

import io
import uuid
from typing import List, Dict, Any
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse

from ...shared.storage.minio_client import minio_client
from ...shared.exceptions.handlers import ExternalServiceError, ValidationError


# ストレージ管理用ルーター
router = APIRouter(
    prefix="/storage",
    tags=["ストレージ管理"],
    responses={
        400: {"description": "バリデーションエラー"},
        500: {"description": "サーバーエラー"}
    }
)


@router.post("/upload/{bucket_type}")
async def upload_file(
    bucket_type: str,
    file: UploadFile = File(...)
):
    """
    ファイルアップロード
    
    Args:
        bucket_type: バケットタイプ（profile-images, student-ids, temp-uploads）
        file: アップロードファイル
    """
    # バケットタイプの検証
    allowed_buckets = ["profile-images", "student-ids", "temp-uploads"]
    if bucket_type not in allowed_buckets:
        raise HTTPException(
            status_code=400,
            detail=f"無効なバケットタイプです。利用可能: {', '.join(allowed_buckets)}"
        )
    
    # ファイルサイズ制限（10MB）
    max_size = 10 * 1024 * 1024  # 10MB
    if file.size and file.size > max_size:
        raise HTTPException(
            status_code=400,
            detail="ファイルサイズが10MBを超えています"
        )
    
    try:
        # ファイル名生成（UUID + 元のファイル名）
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else ''
        object_name = f"{bucket_type}/{uuid.uuid4()}.{file_extension}"
        
        # ファイルデータを読み込み
        file_data = io.BytesIO(await file.read())
        
        # メタデータを安全に処理（日本語文字をBase64エンコード）
        import base64
        safe_filename = base64.b64encode(file.filename.encode('utf-8')).decode('ascii')
        
        # MinIOにアップロード
        result = minio_client.upload_file(
            file_data=file_data,
            object_name=object_name,
            content_type=file.content_type or "application/octet-stream",
            metadata={
                "original_filename_b64": safe_filename,
                "bucket_type": bucket_type
            }
        )
        
        return {
            "success": True,
            "message": "ファイルアップロードが完了しました",
            "data": {
                **result,
                "original_filename": file.filename
            }
        }
        
    except ExternalServiceError as e:
        import traceback
        print(f"ExternalServiceError: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        import traceback
        print(f"Exception: {str(e)}")
        print(f"Exception type: {type(e).__name__}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"アップロードエラー: {str(e)}")


@router.get("/files/{bucket_type}")
async def list_files(bucket_type: str):
    """
    ファイル一覧取得
    
    Args:
        bucket_type: バケットタイプ
    """
    allowed_buckets = ["profile-images", "student-ids", "temp-uploads"]
    if bucket_type not in allowed_buckets:
        raise HTTPException(
            status_code=400,
            detail=f"無効なバケットタイプです。利用可能: {', '.join(allowed_buckets)}"
        )
    
    try:
        objects = minio_client.list_objects(prefix=f"{bucket_type}/")
        print(f"DEBUG: list_files for {bucket_type}, found {len(objects)} objects")
        for obj in objects:
            print(f"DEBUG: Object: {obj['name']}")
        return {
            "success": True,
            "data": objects
        }
        
    except ExternalServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/view/{bucket_type}/{object_name:path}")
async def view_file(bucket_type: str, object_name: str):
    """
    ファイル表示用URL取得
    
    Args:
        bucket_type: バケットタイプ
        object_name: オブジェクト名
    """
    try:
        # デバッグ情報を出力
        print(f"DEBUG: view_file called with bucket_type={bucket_type}, object_name={object_name}")
        
        # オブジェクト名がすでにプレフィックスを含んでいる場合は、そのまま使用
        if object_name.startswith(f"{bucket_type}/"):
            full_object_name = object_name
        else:
            # プレフィックスを含むオブジェクト名を作成
            full_object_name = f"{bucket_type}/{object_name}"
        
        print(f"DEBUG: full_object_name={full_object_name}")
        
        # 署名付きURL取得（外部アクセス可能なエンドポイントを使用）
        url = minio_client.get_presigned_url(full_object_name, expires=3600)
        
        # MinIOの内部エンドポイントを外部アクセス可能なエンドポイントに変換
        if "192.168.100.10:9000" in url:
            # 開発環境では直接MinIOエンドポイントを使用
            external_url = url
        else:
            # 本番環境では適切な外部エンドポイントに変換
            external_url = url
            
        print(f"DEBUG: Generated URL={external_url}")
        
        return {
            "success": True,
            "url": external_url,
            "expires_in": 3600
        }
        
    except ExternalServiceError as e:
        print(f"DEBUG: ExternalServiceError in view_file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        print(f"DEBUG: Exception in view_file: {str(e)}")
        import traceback
        print(f"DEBUG: Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"ファイル表示エラー: {str(e)}")


@router.delete("/delete/{bucket_type}/{object_name:path}")
async def delete_file(bucket_type: str, object_name: str):
    """
    ファイル削除
    
    Args:
        bucket_type: バケットタイプ
        object_name: オブジェクト名
    """
    try:
        # オブジェクト名がすでにプレフィックスを含んでいる場合は、そのまま使用
        if object_name.startswith(f"{bucket_type}/"):
            full_object_name = object_name
        else:
            # プレフィックスを含むオブジェクト名を作成
            full_object_name = f"{bucket_type}/{object_name}"
        
        print(f"DEBUG: delete_file - full_object_name={full_object_name}")
        
        # ファイル削除
        result = minio_client.delete_object(full_object_name)
        
        return {
            "success": True,
            "message": "ファイルが削除されました",
            "data": result
        }
        
    except ExternalServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_storage_stats():
    """
    ストレージ統計情報取得
    """
    try:
        stats = minio_client.get_bucket_stats()
        return {
            "success": True,
            "data": {
                "profileImages": stats["profile-images"],
                "studentIds": stats["student-ids"],
                "tempUploads": stats["temp-uploads"]
            }
        }
        
    except ExternalServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def storage_health_check():
    """
    ストレージヘルスチェック
    """
    try:
        result = minio_client.health_check()
        return {
            "status": "healthy",
            "service": "storage",
            "details": result
        }
        
    except ExternalServiceError as e:
        print(f"DEBUG: ExternalServiceError in storage_health_check: {str(e)}")
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/test-view/{bucket_type}/{object_name:path}")
async def test_view_file(bucket_type: str, object_name: str):
    """
    ファイル表示テスト用エンドポイント
    """
    print(f"TEST: test_view_file called with bucket_type={bucket_type}, object_name={object_name}")
    return {
        "test": "success",
        "bucket_type": bucket_type,
        "object_name": object_name,
        "message": "テストエンドポイントが正常に動作しています"
    }


@router.get("/proxy/{bucket_type}/{object_name:path}")
async def proxy_file(bucket_type: str, object_name: str):
    """
    ファイル直接プロキシ配信
    
    Args:
        bucket_type: バケットタイプ
        object_name: オブジェクト名
    """
    from fastapi.responses import StreamingResponse
    import httpx
    
    try:
        # デバッグ情報を出力
        print(f"DEBUG: proxy_file called with bucket_type={bucket_type}, object_name={object_name}")
        
        # オブジェクト名がすでにプレフィックスを含んでいる場合は、そのまま使用
        if object_name.startswith(f"{bucket_type}/"):
            full_object_name = object_name
        else:
            # プレフィックスを含むオブジェクト名を作成
            full_object_name = f"{bucket_type}/{object_name}"
        
        print(f"DEBUG: full_object_name={full_object_name}")
        
        # 署名付きURL取得
        url = minio_client.get_presigned_url(full_object_name, expires=3600)
        print(f"DEBUG: Generated URL for proxy={url}")
        
        # MinIOから直接ファイルを取得してプロキシ配信
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            if response.status_code != 200:
                raise HTTPException(status_code=404, detail="ファイルが見つかりません")
            
            # コンテンツタイプを決定
            content_type = response.headers.get("content-type", "application/octet-stream")
            
            # ファイルをストリーミング配信
            def generate():
                for chunk in response.iter_bytes():
                    yield chunk
            
            return StreamingResponse(
                generate(),
                media_type=content_type,
                headers={
                    "Content-Disposition": f"inline; filename={object_name.split('/')[-1]}",
                    "Cache-Control": "public, max-age=3600"
                }
            )
        
    except ExternalServiceError as e:
        print(f"DEBUG: ExternalServiceError in proxy_file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        print(f"DEBUG: Exception in proxy_file: {str(e)}")
        import traceback
        print(f"DEBUG: Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"ファイルプロキシエラー: {str(e)}") 