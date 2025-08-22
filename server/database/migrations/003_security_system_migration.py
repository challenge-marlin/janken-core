"""
セキュリティ・監査システムマイグレーション
DB仕様書に基づく完全版
"""

from sqlalchemy import text
from sqlalchemy.engine import Connection
from typing import Dict, Any

class SecuritySystemMigration:
    """セキュリティ・監査・ログ管理システム"""
    
    @staticmethod
    def up(connection: Connection) -> None:
        """マイグレーション実行"""
        
        print("✅ セキュリティシステムマイグレーション開始: 監査・ログ管理")
        
        # 1. ログイン試行記録
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS login_attempts (
                attempt_id BIGINT PRIMARY KEY AUTO_INCREMENT,
                user_id VARCHAR(50) NULL,
                email VARCHAR(255) NULL,
                auth_method ENUM('magic_link','password','2fa') NOT NULL,
                ip_address VARCHAR(45) NOT NULL,
                success BOOLEAN NOT NULL DEFAULT FALSE,
                failure_reason VARCHAR(100) NULL,
                user_agent VARCHAR(255),
                attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_login_user (user_id),
                INDEX idx_login_email (email),
                INDEX idx_login_ip (ip_address),
                INDEX idx_login_time (attempted_at),
                INDEX idx_login_success (success)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """))
        print("✅ login_attemptsテーブル作成完了")
        
        # 2. セキュリティイベントログ
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS security_events (
                event_id BIGINT PRIMARY KEY AUTO_INCREMENT,
                user_id VARCHAR(50) NULL,
                event_type ENUM('magic_link_issued','magic_link_used','login_success','login_failed',
                               'password_set','password_reset','session_revoked','token_rotated',
                               '2fa_enabled','2fa_disabled','suspicious_activity') NOT NULL,
                severity ENUM('low','medium','high','critical') NOT NULL DEFAULT 'low',
                ip_address VARCHAR(45),
                device_info JSON,
                event_details JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_sev_user (user_id),
                INDEX idx_sev_type (event_type),
                INDEX idx_sev_severity (severity),
                INDEX idx_sev_ip (ip_address),
                INDEX idx_sev_time (created_at),
                CONSTRAINT fk_sev_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """))
        print("✅ security_eventsテーブル作成完了")
        
        # 3. 管理者操作ログ
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS admin_logs (
                log_id BIGINT PRIMARY KEY AUTO_INCREMENT,
                admin_user VARCHAR(50) NOT NULL,
                operation VARCHAR(100) NOT NULL,
                target_id VARCHAR(50) NULL,
                target_type VARCHAR(50) NULL,
                details TEXT,
                ip_address VARCHAR(45),
                user_agent VARCHAR(255),
                operated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_admin_user (admin_user),
                INDEX idx_admin_operation (operation),
                INDEX idx_admin_target (target_id, target_type),
                INDEX idx_admin_time (operated_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """))
        print("✅ admin_logsテーブル作成完了")
        
        # 4. システム設定
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS system_settings (
                setting_key VARCHAR(100) PRIMARY KEY,
                setting_value TEXT NOT NULL,
                description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """))
        print("✅ system_settingsテーブル作成完了")
        
        # 5. OAuth連携（将来用）
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS oauth_accounts (
                oauth_id VARCHAR(128) PRIMARY KEY,
                user_id VARCHAR(50) NOT NULL,
                provider ENUM('google','line','apple','github') NOT NULL,
                provider_user_id VARCHAR(255) NOT NULL,
                access_token TEXT,
                refresh_token TEXT,
                token_expires_at DATETIME,
                profile_data JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                CONSTRAINT fk_oauth_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                UNIQUE KEY uniq_provider_user (provider, provider_user_id),
                INDEX idx_oauth_user (user_id),
                INDEX idx_oauth_provider (provider)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """))
        print("✅ oauth_accountsテーブル作成完了")
        
        print("✅ セキュリティシステムマイグレーション完了")
    
    @staticmethod
    def down(connection: Connection) -> None:
        """マイグレーション取り消し"""
        
        tables = [
            'oauth_accounts',
            'system_settings',
            'admin_logs',
            'security_events',
            'login_attempts'
        ]
        
        for table in tables:
            connection.execute(text(f"DROP TABLE IF EXISTS {table}"))
        
        print("✅ セキュリティシステムマイグレーション取り消し完了")
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        """マイグレーション情報"""
        return {
            'name': '003_security_system_migration',
            'description': 'セキュリティ・監査・ログ管理システム',
            'tables': ['login_attempts', 'security_events', 'admin_logs', 'system_settings', 'oauth_accounts'],
            'dependencies': ['001_initial_migration']
        }
