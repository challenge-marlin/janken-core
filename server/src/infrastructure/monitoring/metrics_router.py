"""
監視用メトリクスAPIルーター

システム監視用のメトリクス取得エンドポイントを提供
"""

import random
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from .health import health_checker


# 監視用ルーター
router = APIRouter(
    prefix="/api",
    tags=["システム監視"],
    responses={
        500: {"description": "サーバーエラー"}
    }
)


@router.get("/metrics")
async def get_metrics():
    """
    システムメトリクス取得
    
    監視用HTMLから呼び出されるメトリクス情報を返します
    """
    try:
        # TODO: 実際のメトリクス取得実装
        # 現在はモックデータを返します
        metrics = {
            "activeUsers": random.randint(0, 50),
            "activeBattles": random.randint(0, 10),
            "apiLatency": random.randint(10, 100),
            "errorRate": round(random.uniform(0, 5), 2)
        }
        
        return {
            "success": True,
            "data": metrics,
            "timestamp": health_checker.check_all_services.__code__.co_consts[0] if hasattr(health_checker.check_all_services, '__code__') else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"メトリクス取得エラー: {str(e)}")


@router.get("/status")
async def get_service_status():
    """
    サービスステータス取得
    
    各サービスの稼働状況を返します
    """
    try:
        health_result = await health_checker.check_all_services()
        
        # フロントエンド用にステータスを変換
        status = {}
        for service_name, service_info in health_result["services"].items():
            if service_info["status"] == "healthy":
                status[service_name] = "healthy"
            else:
                status[service_name] = "error"
        
        # Nginxステータスを追加（常に正常と仮定）
        status["nginx"] = "healthy"
        
        return {
            "success": True,
            "data": status,
            "overall_status": health_result["overall_status"],
            "timestamp": health_result["timestamp"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ステータス取得エラー: {str(e)}")


@router.get("/health/detailed")
async def get_detailed_health():
    """
    詳細ヘルスチェック
    
    全サービスの詳細な健康状態を返します
    """
    try:
        result = await health_checker.check_all_services()
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"詳細ヘルスチェックエラー: {str(e)}") 