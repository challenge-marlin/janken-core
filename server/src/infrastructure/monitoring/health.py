"""
ヘルスチェック機能

各種サービスの接続状態を監視します。
"""

import asyncio
from typing import Dict, Any
from datetime import datetime

from ...shared.config.settings import settings


class HealthChecker:
    """ヘルスチェック管理クラス"""
    
    def __init__(self):
        self.services = {
            "mysql": self._check_mysql,
            "redis": self._check_redis,
            "minio": self._check_minio
        }
    
    async def check_all_services(self) -> Dict[str, Any]:
        """全サービスのヘルスチェック"""
        results = {}
        
        for service_name, check_func in self.services.items():
            try:
                result = await check_func()
                results[service_name] = {
                    "status": "healthy",
                    "details": result,
                    "checked_at": datetime.utcnow().isoformat()
                }
            except Exception as e:
                results[service_name] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "checked_at": datetime.utcnow().isoformat()
                }
        
        # 全体のステータス判定
        overall_status = "healthy" if all(
            result["status"] == "healthy" for result in results.values()
        ) else "unhealthy"
        
        return {
            "overall_status": overall_status,
            "services": results,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _check_mysql(self) -> Dict[str, Any]:
        """MySQL接続チェック"""
        try:
            # TODO: 実際のMySQL接続チェック実装
            # from ...shared.database.connection import db_connection
            # async with db_connection.get_session() as session:
            #     result = await session.execute("SELECT 1")
            #     return {"connection": "ok", "query_result": result.scalar()}
            
            return {
                "connection": "ok",
                "message": "MySQL接続は正常です（モック）"
            }
        except Exception as e:
            raise Exception(f"MySQL接続エラー: {str(e)}")
    
    async def _check_redis(self) -> Dict[str, Any]:
        """Redis接続チェック"""
        try:
            # TODO: 実際のRedis接続チェック実装
            # import redis.asyncio as redis
            # client = redis.from_url(settings.redis_url)
            # await client.ping()
            # await client.close()
            
            return {
                "connection": "ok",
                "message": "Redis接続は正常です（モック）"
            }
        except Exception as e:
            raise Exception(f"Redis接続エラー: {str(e)}")
    
    async def _check_minio(self) -> Dict[str, Any]:
        """MinIO接続チェック"""
        try:
            from ...shared.storage.minio_client import minio_client
            result = await minio_client.health_check()
            return result
        except Exception as e:
            raise Exception(f"MinIO接続エラー: {str(e)}")


# グローバルインスタンス
health_checker = HealthChecker() 