"""
Redisサービス

Redisを使用したデータ管理サービス（バトルシステム対応版）
"""

import json
import redis
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from ..config.settings import settings


class RedisService:
    """Redisサービスクラス（バトルシステム対応版）"""
    
    def __init__(self):
        """Redis接続を初期化"""
        self.redis_client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            password=settings.redis_password,
            db=settings.redis_db,
            decode_responses=True,  # 文字列として自動デコード
            socket_connect_timeout=5,  # 接続タイムアウト
            socket_timeout=5,  # ソケットタイムアウト
            retry_on_timeout=True,  # タイムアウト時のリトライ
            health_check_interval=30  # ヘルスチェック間隔
        )
    
    def ping(self) -> bool:
        """Redis接続テスト"""
        try:
            return self.redis_client.ping()
        except Exception:
            return False
    
    def get_info(self) -> Dict[str, Any]:
        """Redis情報取得"""
        try:
            info = self.redis_client.info()
            return {
                "version": info.get("redis_version", "unknown"),
                "uptime": info.get("uptime_in_seconds", 0),
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory_human", "unknown"),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """メモリ使用量取得"""
        try:
            info = self.redis_client.info("memory")
            return {
                "used_memory": info.get("used_memory_human", "unknown"),
                "used_memory_peak": info.get("used_memory_peak_human", "unknown"),
                "used_memory_rss": info.get("used_memory_rss_human", "unknown"),
                "mem_fragmentation_ratio": info.get("mem_fragmentation_ratio", 0)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_keys_count(self, pattern: str = "*") -> int:
        """キー数取得"""
        try:
            return len(self.redis_client.keys(pattern))
        except Exception:
            return 0
    
    def cleanup_expired_keys(self, pattern: str = "*") -> int:
        """期限切れキーのクリーンアップ"""
        try:
            keys = self.redis_client.keys(pattern)
            deleted_count = 0
            
            for key in keys:
                if self.redis_client.ttl(key) <= 0:
                    if self.redis_client.delete(key):
                        deleted_count += 1
            
            return deleted_count
        except Exception:
            return 0
    
    # Magic Link関連機能
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
    
    # バトルシステム関連機能
    def set_battle_connection_state(
        self, 
        user_id: str, 
        connection_data: Dict[str, Any], 
        expire_seconds: int = 300
    ) -> bool:
        """
        バトル接続状態をRedisに保存
        
        Args:
            user_id: ユーザーID
            connection_data: 接続データ
            expire_seconds: 有効期限（秒）
            
        Returns:
            保存成功フラグ
        """
        try:
            key = f"battle:connection:{user_id}"
            data_json = json.dumps(connection_data, default=str)
            self.redis_client.setex(key, expire_seconds, data_json)
            return True
        except Exception as e:
            print(f"❌ バトル接続状態保存エラー: {e}")
            return False
    
    def get_battle_connection_state(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        バトル接続状態をRedisから取得
        
        Args:
            user_id: ユーザーID
            
        Returns:
            接続状態データ
        """
        try:
            key = f"battle:connection:{user_id}"
            data_json = self.redis_client.get(key)
            return json.loads(data_json) if data_json else None
        except Exception as e:
            print(f"❌ バトル接続状態取得エラー: {e}")
            return None
    
    def delete_battle_connection_state(self, user_id: str) -> bool:
        """
        バトル接続状態をRedisから削除
        
        Args:
            user_id: ユーザーID
            
        Returns:
            削除成功フラグ
        """
        try:
            key = f"battle:connection:{user_id}"
            return bool(self.redis_client.delete(key))
        except Exception as e:
            print(f"❌ バトル接続状態削除エラー: {e}")
            return False
    
    def set_battle_matching_state(
        self, 
        user_id: str, 
        matching_data: Dict[str, Any], 
        expire_seconds: int = 300
    ) -> bool:
        """
        バトルマッチング状態をRedisに保存
        
        Args:
            user_id: ユーザーID
            matching_data: マッチングデータ
            expire_seconds: 有効期限（秒）
            
        Returns:
            保存成功フラグ
        """
        try:
            key = f"battle:matching:{user_id}"
            data_json = json.dumps(matching_data, default=str)
            self.redis_client.setex(key, expire_seconds, data_json)
            return True
        except Exception as e:
            print(f"❌ バトルマッチング状態保存エラー: {e}")
            return False
    
    def get_battle_matching_state(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        バトルマッチング状態をRedisから取得
        
        Args:
            user_id: ユーザーID
            
        Returns:
            マッチング状態データ
        """
        try:
            key = f"battle:matching:{user_id}"
            data_json = self.redis_client.get(key)
            return json.loads(data_json) if data_json else None
        except Exception as e:
            print(f"❌ バトルマッチング状態取得エラー: {e}")
            return None
    
    def set_battle_session_state(
        self, 
        battle_id: str, 
        session_data: Dict[str, Any], 
        expire_seconds: int = 1800
    ) -> bool:
        """
        バトルセッション状態をRedisに保存
        
        Args:
            battle_id: バトルID
            session_data: セッションデータ
            expire_seconds: 有効期限（秒）
            
        Returns:
            保存成功フラグ
        """
        try:
            key = f"battle:session:{battle_id}"
            data_json = json.dumps(session_data, default=str)
            self.redis_client.setex(key, expire_seconds, data_json)
            return True
        except Exception as e:
            print(f"❌ バトルセッション状態保存エラー: {e}")
            return False
    
    def get_battle_session_state(self, battle_id: str) -> Optional[Dict[str, Any]]:
        """
        バトルセッション状態をRedisから取得
        
        Args:
            battle_id: バトルID
            
        Returns:
            セッション状態データ
        """
        try:
            key = f"battle:session:{battle_id}"
            data_json = self.redis_client.get(key)
            return json.loads(data_json) if data_json else None
        except Exception as e:
            print(f"❌ バトルセッション状態取得エラー: {e}")
            return None
    
    def delete_battle_session_state(self, battle_id: str) -> bool:
        """
        バトルセッション状態をRedisから削除
        
        Args:
            battle_id: バトルID
            
        Returns:
            削除成功フラグ
        """
        try:
            key = f"battle:session:{battle_id}"
            return bool(self.redis_client.delete(key))
        except Exception as e:
            print(f"❌ バトルセッション状態削除エラー: {e}")
            return False
    
    def set_battle_stats(
        self, 
        user_id: str, 
        stats_data: Dict[str, Any], 
        expire_seconds: int = 3600
    ) -> bool:
        """
        バトル統計をRedisに保存
        
        Args:
            user_id: ユーザーID
            stats_data: 統計データ
            expire_seconds: 有効期限（秒）
            
        Returns:
            保存成功フラグ
        """
        try:
            key = f"battle:stats:{user_id}"
            data_json = json.dumps(stats_data, default=str)
            self.redis_client.setex(key, expire_seconds, data_json)
            return True
        except Exception as e:
            print(f"❌ バトル統計保存エラー: {e}")
            return False
    
    def get_battle_stats(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        バトル統計をRedisから取得
        
        Args:
            user_id: ユーザーID
            
        Returns:
            統計データ
        """
        try:
            key = f"battle:stats:{user_id}"
            data_json = self.redis_client.get(key)
            return json.loads(data_json) if data_json else None
        except Exception as e:
            print(f"❌ バトル統計取得エラー: {e}")
            return None
    
    def push_offline_message(
        self, 
        user_id: str, 
        message: Dict[str, Any], 
        expire_seconds: int = 3600
    ) -> bool:
        """
        オフラインメッセージをRedisに保存
        
        Args:
            user_id: ユーザーID
            message: メッセージデータ
            expire_seconds: 有効期限（秒）
            
        Returns:
            保存成功フラグ
        """
        try:
            key = f"battle:offline_messages:{user_id}"
            data_json = json.dumps(message, default=str)
            self.redis_client.lpush(key, data_json)
            self.redis_client.expire(key, expire_seconds)
            return True
        except Exception as e:
            print(f"❌ オフラインメッセージ保存エラー: {e}")
            return False
    
    def get_offline_messages(self, user_id: str) -> List[Dict[str, Any]]:
        """
        オフラインメッセージをRedisから取得
        
        Args:
            user_id: ユーザーID
            
        Returns:
            メッセージリスト
        """
        try:
            key = f"battle:offline_messages:{user_id}"
            messages = self.redis_client.lrange(key, 0, -1)
            self.redis_client.delete(key)  # 取得後は削除
            return [json.loads(msg) for msg in messages]
        except Exception as e:
            print(f"❌ オフラインメッセージ取得エラー: {e}")
            return []
    
    def get_battle_system_stats(self) -> Dict[str, Any]:
        """
        バトルシステム全体の統計を取得
        
        Returns:
            システム統計データ
        """
        try:
            stats = {
                "connections": self.get_keys_count("battle:connection:*"),
                "matching": self.get_keys_count("battle:matching:*"),
                "sessions": self.get_keys_count("battle:session:*"),
                "stats": self.get_keys_count("battle:stats:*"),
                "offline_messages": self.get_keys_count("battle:offline_messages:*"),
                "magic_links": self.get_keys_count("magic_link:*"),
                "total_keys": self.get_keys_count("*")
            }
            
            # メモリ使用量も追加
            memory_info = self.get_memory_usage()
            if "error" not in memory_info:
                stats["memory"] = memory_info
            
            return stats
        except Exception as e:
            return {"error": str(e)}
    
    def cleanup_battle_system_data(self) -> Dict[str, int]:
        """
        バトルシステムの期限切れデータをクリーンアップ
        
        Returns:
            削除されたデータ数
        """
        try:
            cleanup_results = {
                "connections": self.cleanup_expired_keys("battle:connection:*"),
                "matching": self.cleanup_expired_keys("battle:matching:*"),
                "sessions": self.cleanup_expired_keys("battle:session:*"),
                "stats": self.cleanup_expired_keys("battle:stats:*"),
                "offline_messages": self.cleanup_expired_keys("battle:offline_messages:*"),
                "magic_links": self.cleanup_expired_tokens()
            }
            
            total_cleaned = sum(cleanup_results.values())
            cleanup_results["total"] = total_cleaned
            
            return cleanup_results
        except Exception as e:
            return {"error": str(e)}


# グローバルRedisサービスインスタンス
redis_service = RedisService()
