"""
認証システム拡張マイグレーション
DB仕様書に基づく完全版
"""

from sqlalchemy import text
from sqlalchemy.engine import Connection
from typing import Dict, Any

class AuthSystemMigration:
    """Magic Link + JWT + セッション管理システム"""
    
    @staticmethod
    def up(connection: Connection) -> None:
        """マイグレーション実行"""
        
        print("✅ 認証システムマイグレーション開始: Magic Link + JWT")
        
        # 1. Magic Link トークン
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS magic_link_tokens (
                token_hash VARCHAR(128) PRIMARY KEY,
                email VARCHAR(255) NOT NULL,
                user_id VARCHAR(50) NULL,
                issued_at DATETIME NOT NULL,
                expires_at DATETIME NOT NULL,
                used_at DATETIME NULL,
                ip_address VARCHAR(45),
                user_agent VARCHAR(255),
                INDEX idx_ml_email (email),
                INDEX idx_ml_expires (expires_at),
                INDEX idx_ml_user (user_id),
                CONSTRAINT fk_ml_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """))
        print("✅ magic_link_tokensテーブル作成完了")
        
        # 2. セッション管理
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id VARCHAR(100) PRIMARY KEY,
                user_id VARCHAR(50) NOT NULL,
                device_id VARCHAR(100) NOT NULL,
                ip_address VARCHAR(45) NULL,
                user_agent VARCHAR(255) NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_seen_at TIMESTAMP NULL,
                is_revoked BOOLEAN DEFAULT FALSE,
                CONSTRAINT fk_sessions_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                CONSTRAINT fk_sessions_device FOREIGN KEY (device_id) REFERENCES user_devices(device_id) ON DELETE CASCADE,
                UNIQUE KEY uniq_user_device (user_id, device_id),
                INDEX idx_sessions_user (user_id),
                INDEX idx_sessions_seen (last_seen_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """))
        print("✅ sessionsテーブル作成完了")
        
        # 3. リフレッシュトークン
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS refresh_tokens (
                token_id VARCHAR(100) PRIMARY KEY,
                session_id VARCHAR(100) NOT NULL,
                token_hash VARCHAR(255) NOT NULL,
                issued_at DATETIME NOT NULL,
                expires_at DATETIME NOT NULL,
                rotated_from VARCHAR(100) NULL,
                is_revoked BOOLEAN DEFAULT FALSE,
                CONSTRAINT fk_rt_session FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE,
                UNIQUE KEY uniq_rt_hash (token_hash),
                INDEX idx_rt_session (session_id),
                INDEX idx_rt_expires (expires_at),
                INDEX idx_rt_revoked (is_revoked)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """))
        print("✅ refresh_tokensテーブル作成完了")
        
        # 4. JWTブラックリスト
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS jwt_blacklist (
                jti_hash VARCHAR(128) PRIMARY KEY,
                user_id VARCHAR(50) NOT NULL,
                reason VARCHAR(100) NULL,
                revoked_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                expires_at DATETIME NOT NULL,
                INDEX idx_jwtbl_user (user_id),
                INDEX idx_jwtbl_expires (expires_at),
                CONSTRAINT fk_jwtbl_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """))
        print("✅ jwt_blacklistテーブル作成完了")
        
        # 5. 2要素認証
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS two_factor_auth (
                user_id VARCHAR(50) PRIMARY KEY,
                enabled BOOLEAN NOT NULL DEFAULT FALSE,
                secret_key VARCHAR(32),
                backup_codes JSON,
                last_used DATETIME NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                CONSTRAINT fk_2fa_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                INDEX idx_2fa_enabled (enabled)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """))
        print("✅ two_factor_authテーブル作成完了")
        
        print("✅ 認証システムマイグレーション完了")
    
    @staticmethod
    def down(connection: Connection) -> None:
        """マイグレーション取り消し"""
        
        tables = [
            'two_factor_auth',
            'jwt_blacklist',
            'refresh_tokens',
            'sessions',
            'magic_link_tokens'
        ]
        
        for table in tables:
            connection.execute(text(f"DROP TABLE IF EXISTS {table}"))
        
        print("✅ 認証システムマイグレーション取り消し完了")
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        """マイグレーション情報"""
        return {
            'name': '002_auth_system_migration',
            'description': 'Magic Link + JWT認証システム',
            'tables': ['magic_link_tokens', 'sessions', 'refresh_tokens', 'jwt_blacklist', 'two_factor_auth'],
            'dependencies': ['001_initial_migration']
        }
