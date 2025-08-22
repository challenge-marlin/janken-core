"""
システム管理・監視マイグレーション
DB仕様書に基づく完全版
"""

from sqlalchemy import text
from sqlalchemy.engine import Connection
from typing import Dict, Any

class SystemManagementMigration:
    """システム管理・監視・アクティビティログ"""
    
    @staticmethod
    def up(connection: Connection) -> None:
        """マイグレーション実行"""
        
        print("✅ システム管理マイグレーション開始: 監視・アクティビティログ")
        
        # 1. アクティビティログ
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
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """))
        print("✅ activity_logsテーブル作成完了")
        
        # 2. システム統計
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS system_stats (
                stat_id BIGINT PRIMARY KEY AUTO_INCREMENT,
                stat_key VARCHAR(100) NOT NULL,
                stat_value TEXT NOT NULL,
                stat_type ENUM('counter', 'gauge', 'histogram') NOT NULL DEFAULT 'counter',
                stat_unit VARCHAR(20),
                description TEXT,
                collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_stat_key (stat_key),
                INDEX idx_stat_type (stat_type),
                INDEX idx_collected_at (collected_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """))
        print("✅ system_statsテーブル作成完了")
        
        # 3. システムヘルスチェック
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS system_health (
                health_id BIGINT PRIMARY KEY AUTO_INCREMENT,
                service_name VARCHAR(100) NOT NULL,
                status ENUM('healthy', 'warning', 'critical', 'unknown') NOT NULL DEFAULT 'unknown',
                response_time_ms INT,
                error_message TEXT,
                last_check_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                next_check_at TIMESTAMP NULL,
                INDEX idx_service_name (service_name),
                INDEX idx_status (status),
                INDEX idx_last_check (last_check_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """))
        print("✅ system_healthテーブル作成完了")
        
        # 4. パフォーマンスメトリクス
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS performance_metrics (
                metric_id BIGINT PRIMARY KEY AUTO_INCREMENT,
                metric_name VARCHAR(100) NOT NULL,
                metric_value DECIMAL(10,4) NOT NULL,
                metric_unit VARCHAR(20),
                tags JSON,
                collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_metric_name (metric_name),
                INDEX idx_collected_at (collected_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """))
        print("✅ performance_metricsテーブル作成完了")
        
        # 5. システムイベント
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS system_events (
                event_id BIGINT PRIMARY KEY AUTO_INCREMENT,
                event_type VARCHAR(100) NOT NULL,
                event_source VARCHAR(100),
                event_severity ENUM('info', 'warning', 'error', 'critical') NOT NULL DEFAULT 'info',
                event_message TEXT NOT NULL,
                event_data JSON,
                ip_address VARCHAR(45),
                user_agent VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_event_type (event_type),
                INDEX idx_event_severity (event_severity),
                INDEX idx_created_at (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """))
        print("✅ system_eventsテーブル作成完了")
        
        print("✅ システム管理マイグレーション完了")
    
    @staticmethod
    def down(connection: Connection) -> None:
        """マイグレーション取り消し"""
        
        tables = [
            'system_events',
            'performance_metrics',
            'system_health',
            'system_stats',
            'activity_logs'
        ]
        
        for table in tables:
            connection.execute(text(f"DROP TABLE IF EXISTS {table}"))
        
        print("✅ システム管理マイグレーション取り消し完了")
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        """マイグレーション情報"""
        return {
            'name': '005_system_management_migration',
            'description': 'システム管理・監視・アクティビティログ',
            'tables': ['activity_logs', 'system_stats', 'system_health', 'performance_metrics', 'system_events'],
            'dependencies': ['001_initial_migration']
        }
