"""
Redisサービス

Redisを使用したデータ管理サービス
"""

import json
import redis
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from ..config.settings import settings


class RedisService:
    """Redisサービスクラス"""
    
    def __init__(self):
        """Redis接続を初期化"""
        self.redis_client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            password=settings.redis_password,
            db=settings.redis_db,
            decode_responses=True  # 文字列として自動デコード
        )
    
    def ping(self) -> bool:
        """Redis接続テスト"""
        try:
            return self.redis_client.ping()
        except Exception:
            return False
    
    def set_magic_link_token(
        self, 
        token_hash: str, 
        token_data: Dict[str, Any], 
        expire_minutes: int = 1440
    ) -> bool:
        """
        Magic LinkトークンをRedisに保存
        
        Args:
            token_hash: トークンハッシュ
            token_data: トークンデータ
            expire_minutes: 有効期限（分）
            
        Returns:
            保存成功フラグ
        """
        try:
            # キー名
            key = f"magic_link:{token_hash}"
            
            # データをJSON文字列に変換
            data_json = json.dumps(token_data, default=str)
            
            # Redisに保存（TTL付き）
            self.redis_client.setex(
                key, 
                expire_minutes * 60,  # 秒単位
                data_json
            )
            
            return True
        except Exception as e:
            print(f"❌ Redis保存エラー: {e}")
            return False
    
    def get_magic_link_token(self, token_hash: str) -> Optional[Dict[str, Any]]:
        """
        Magic LinkトークンをRedisから取得
        
        Args:
            token_hash: トークンハッシュ
            
        Returns:
            トークンデータ（見つからない場合はNone）
        """
        try:
            # キー名
            key = f"magic_link:{token_hash}"
            
            # Redisから取得
            data_json = self.redis_client.get(key)
            
            if data_json is None:
                return None
            
            # JSON文字列を辞書に変換
            token_data = json.loads(data_json)
            
            # 日時文字列をdatetimeオブジェクトに変換
            if "expires_at" in token_data:
                token_data["expires_at"] = datetime.fromisoformat(token_data["expires_at"])
            if "created_at" in token_data:
                token_data["created_at"] = datetime.fromisoformat(token_data["created_at"])
            
            return token_data
        except Exception as e:
            print(f"❌ Redis取得エラー: {e}")
            return None
    
    def update_magic_link_token(self, token_hash: str, updates: Dict[str, Any]) -> bool:
        """
        Magic Linkトークンを更新
        
        Args:
            token_hash: トークンハッシュ
            updates: 更新するデータ
            
        Returns:
            更新成功フラグ
        """
        try:
            # 既存データを取得
            token_data = self.get_magic_link_token(token_hash)
            if token_data is None:
                return False
            
            # データを更新
            token_data.update(updates)
            
            # 残りのTTLを取得
            key = f"magic_link:{token_hash}"
            ttl = self.redis_client.ttl(key)
            
            if ttl > 0:
                # 残りTTLで再保存
                return self.set_magic_link_token(token_hash, token_data, ttl // 60)
            else:
                # TTLが切れている場合は削除
                self.delete_magic_link_token(token_hash)
                return False
                
        except Exception as e:
            print(f"❌ Redis更新エラー: {e}")
            return False
    
    def delete_magic_link_token(self, token_hash: str) -> bool:
        """
        Magic Linkトークンを削除
        
        Args:
            token_hash: トークンハッシュ
            
        Returns:
            削除成功フラグ
        """
        try:
            key = f"magic_link:{token_hash}"
            return bool(self.redis_client.delete(key))
        except Exception as e:
            print(f"❌ Redis削除エラー: {e}")
            return False
    
    def get_magic_link_count(self) -> int:
        """
        Magic Linkトークンの数を取得
        
        Returns:
            トークン数
        """
        try:
            pattern = "magic_link:*"
            keys = self.redis_client.keys(pattern)
            return len(keys)
        except Exception as e:
            print(f"❌ Redisカウント取得エラー: {e}")
            return 0
    
    def cleanup_expired_tokens(self) -> int:
        """
        期限切れトークンをクリーンアップ
        
        Returns:
            削除されたトークン数
        """
        try:
            pattern = "magic_link:*"
            keys = self.redis_client.keys(pattern)
            deleted_count = 0
            
            for key in keys:
                # TTLが0以下の場合は削除
                if self.redis_client.ttl(key) <= 0:
                    if self.redis_client.delete(key):
                        deleted_count += 1
            
            return deleted_count
        except Exception as e:
            print(f"❌ Redisクリーンアップエラー: {e}")
            return 0


# グローバルRedisサービスインスタンス
redis_service = RedisService()
