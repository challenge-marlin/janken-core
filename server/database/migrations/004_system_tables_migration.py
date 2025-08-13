"""
システム管理テーブルマイグレーション
Laravel風: 2025_01_13_000004_create_system_tables 相当
"""
from sqlalchemy import text
from typing import Dict, Any

class SystemTablesMigration:
    """システム設定・ログ・監査テーブル"""
    
    @staticmethod
    def up(connection) -> None:
        """マイグレーション実行"""
        
        # 1. システム設定
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS system_settings (
                setting_key VARCHAR(100) PRIMARY KEY,
                setting_value TEXT NOT NULL,
                description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """))
        
        # 2. OAuth連携
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
            )
        """))
        
        # 3. ログイン試行管理
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS login_attempts (
                attempt_id BIGINT PRIMARY KEY AUTO_INCREMENT,
                user_id VARCHAR(50) NULL,
                email VARCHAR(255) NULL,
                ip_address VARCHAR(45) NOT NULL,
                attempt_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                success BOOLEAN NOT NULL DEFAULT FALSE,
                failure_reason VARCHAR(100) NULL,
                user_agent VARCHAR(255),
                INDEX idx_login_user (user_id),
                INDEX idx_login_email (email),
                INDEX idx_login_ip (ip_address),
                INDEX idx_login_time (attempt_time),
                INDEX idx_login_success (success)
            )
        """))
        
        # 4. セキュリティイベントログ
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS security_events (
                event_id BIGINT PRIMARY KEY AUTO_INCREMENT,
                user_id VARCHAR(50) NULL,
                event_type ENUM('magic_link_issued','magic_link_used','login_success','login_failed',
                               'password_set','password_reset','session_revoked','token_rotated',
                               'websocket_connected','websocket_disconnected','2fa_enabled','2fa_disabled',
                               'oauth_linked','oauth_unlinked','device_registered','device_removed') NOT NULL,
                detail JSON NULL,
                ip_address VARCHAR(45),
                user_agent VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_sev_user (user_id),
                INDEX idx_sev_type_time (event_type, created_at),
                INDEX idx_sev_ip (ip_address),
                CONSTRAINT fk_sev_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
            )
        """))
        
        # 5. 管理者操作ログ
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
            )
        """))
        
        # 6. アクティビティログ
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS activity_logs (
                log_id BIGINT PRIMARY KEY AUTO_INCREMENT,
                user_id VARCHAR(50) NULL,
                operation_code VARCHAR(10),
                operation VARCHAR(100),
                activity_type ENUM('login', 'logout', 'battle_start', 'battle_end', 'achievement', 'ranking_update') NOT NULL,
                activity_data JSON NULL,
                details TEXT,
                ip_address VARCHAR(45),
                user_agent VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                operated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL,
                INDEX idx_user_id (user_id),
                INDEX idx_activity_type (activity_type),
                INDEX idx_created_at (created_at),
                INDEX idx_operation_code (operation_code)
            )
        """))
        
        print("✅ システム管理テーブルマイグレーション完了")
    
    @staticmethod
    def down(connection) -> None:
        """マイグレーション取り消し"""
        
        tables = [
            'activity_logs',
            'admin_logs',
            'security_events',
            'login_attempts',
            'oauth_accounts',
            'system_settings'
        ]
        
        for table in tables:
            connection.execute(text(f"DROP TABLE IF EXISTS {table}"))
        
        print("✅ システム管理テーブルマイグレーション取り消し完了")
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        """マイグレーション情報"""
        return {
            'name': '004_system_tables_migration',
            'description': 'システム設定・OAuth・ログ・監査テーブル',
            'tables': ['system_settings', 'oauth_accounts', 'login_attempts', 'security_events', 'admin_logs', 'activity_logs'],
            'dependencies': ['001_initial_migration']
        }
