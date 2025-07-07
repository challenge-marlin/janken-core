"""
MinIOクライアント機能

MinIOサーバーとの接続・操作を提供します。
"""

import io
import os
from typing import List, Dict, Any, Optional, BinaryIO
from datetime import datetime, timedelta
from minio import Minio
from minio.error import S3Error

from ...config.settings import settings
from ...shared.exceptions.handlers import ExternalServiceError


class MinIOClient:
    """MinIOクライアント管理クラス"""
    
    def __init__(self):
        self.client = None
        self.bucket_name = settings.minio_bucket
        self._initialize_client()
    
    def _initialize_client(self):
        """MinIOクライアントの初期化"""
        try:
            self.client = Minio(
                endpoint=settings.minio_endpoint,
                access_key=settings.minio_access_key,
                secret_key=settings.minio_secret_key,
                secure=settings.minio_secure
            )
            
            # バケットの存在確認・作成
            self._ensure_bucket_exists()
            
        except Exception as e:
            raise ExternalServiceError(f"MinIO接続の初期化に失敗しました: {str(e)}", "minio")
    
    def _ensure_bucket_exists(self):
        """バケットの存在確認・作成"""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
        except S3Error as e:
            raise ExternalServiceError(f"バケット操作に失敗しました: {str(e)}", "minio")
    
    def upload_file(
        self,
        file_data: BinaryIO,
        object_name: str,
        content_type: str = "application/octet-stream",
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        ファイルアップロード
        
        Args:
            file_data: ファイルデータ
            object_name: オブジェクト名
            content_type: コンテンツタイプ
            metadata: メタデータ
            
        Returns:
            アップロード結果
        """
        try:
            # ファイルサイズを取得
            file_data.seek(0, 2)  # ファイル末尾に移動
            file_size = file_data.tell()
            file_data.seek(0)  # ファイル先頭に戻す
            
            # アップロード実行
            result = self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                data=file_data,
                length=file_size,
                content_type=content_type,
                metadata=metadata
            )
            
            return {
                "bucket": self.bucket_name,
                "object_name": object_name,
                "etag": result.etag,
                "size": file_size,
                "url": self.get_presigned_url(object_name),
                "uploaded_at": datetime.utcnow().isoformat()
            }
            
        except S3Error as e:
            raise ExternalServiceError(f"ファイルアップロードに失敗しました: {str(e)}", "minio")
    
    def list_objects(self, prefix: str = "") -> List[Dict[str, Any]]:
        """
        オブジェクト一覧取得
        
        Args:
            prefix: プレフィックス
            
        Returns:
            オブジェクト一覧
        """
        try:
            objects = []
            for obj in self.client.list_objects(self.bucket_name, prefix=prefix):
                objects.append({
                    "name": obj.object_name,
                    "size": obj.size,
                    "etag": obj.etag,
                    "last_modified": obj.last_modified.isoformat(),
                    "content_type": obj.content_type
                })
            return objects
            
        except S3Error as e:
            raise ExternalServiceError(f"オブジェクト一覧取得に失敗しました: {str(e)}", "minio")
    
    def delete_object(self, object_name: str) -> Dict[str, Any]:
        """
        オブジェクト削除
        
        Args:
            object_name: オブジェクト名
            
        Returns:
            削除結果
        """
        try:
            self.client.remove_object(self.bucket_name, object_name)
            return {
                "bucket": self.bucket_name,
                "object_name": object_name,
                "deleted_at": datetime.utcnow().isoformat()
            }
            
        except S3Error as e:
            raise ExternalServiceError(f"オブジェクト削除に失敗しました: {str(e)}", "minio")
    
    def get_presigned_url(self, object_name: str, expires: int = 3600) -> str:
        """
        署名付きURL取得
        
        Args:
            object_name: オブジェクト名
            expires: 有効期限（秒）
            
        Returns:
            署名付きURL
        """
        try:
            return self.client.presigned_get_object(
                self.bucket_name,
                object_name,
                expires=timedelta(seconds=expires)
            )
        except S3Error as e:
            raise ExternalServiceError(f"署名付きURL取得に失敗しました: {str(e)}", "minio")
    
    def get_bucket_stats(self) -> Dict[str, Any]:
        """
        バケット統計情報取得
        
        Returns:
            統計情報
        """
        try:
            objects = self.list_objects()
            
            # プレフィックス別の統計
            stats = {
                "profile-images": {"count": 0, "totalSize": 0},
                "student-ids": {"count": 0, "totalSize": 0},
                "temp-uploads": {"count": 0, "totalSize": 0}
            }
            
            for obj in objects:
                if obj["name"].startswith("profile-images/"):
                    stats["profile-images"]["count"] += 1
                    stats["profile-images"]["totalSize"] += obj["size"]
                elif obj["name"].startswith("student-ids/"):
                    stats["student-ids"]["count"] += 1
                    stats["student-ids"]["totalSize"] += obj["size"]
                elif obj["name"].startswith("temp-uploads/"):
                    stats["temp-uploads"]["count"] += 1
                    stats["temp-uploads"]["totalSize"] += obj["size"]
            
            return stats
            
        except S3Error as e:
            raise ExternalServiceError(f"バケット統計取得に失敗しました: {str(e)}", "minio")
    
    def health_check(self) -> Dict[str, Any]:
        """
        MinIOヘルスチェック
        
        Returns:
            ヘルスチェック結果
        """
        try:
            # バケット一覧取得でヘルスチェック
            buckets = self.client.list_buckets()
            return {
                "connection": "ok",
                "buckets": len(buckets),
                "target_bucket": self.bucket_name,
                "bucket_exists": self.client.bucket_exists(self.bucket_name)
            }
            
        except S3Error as e:
            raise ExternalServiceError(f"MinIOヘルスチェックに失敗しました: {str(e)}", "minio")


# グローバルインスタンス
minio_client = MinIOClient() 