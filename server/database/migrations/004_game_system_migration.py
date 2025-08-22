"""
ゲーム・統計システムマイグレーション
DB仕様書に基づく完全版
"""

from sqlalchemy import text
from sqlalchemy.engine import Connection
from typing import Dict, Any

class GameSystemMigration:
    """じゃんけんゲーム・統計・ランキングシステム"""
    
    @staticmethod
    def up(connection: Connection) -> None:
        """マイグレーション実行"""
        
        print("✅ ゲームシステムマイグレーション開始: じゃんけん・統計・ランキング")
        
        # 1. バトル結果記録
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS battle_results (
                battle_id VARCHAR(100) PRIMARY KEY,
                fight_no BIGINT AUTO_INCREMENT UNIQUE,
                player1_id VARCHAR(50) NOT NULL,
                player2_id VARCHAR(50) NOT NULL,
                player1_nickname VARCHAR(50),
                player2_nickname VARCHAR(50),
                winner_id VARCHAR(50) NULL,
                total_rounds INT DEFAULT 0,
                player1_wins INT DEFAULT 0,
                player2_wins INT DEFAULT 0,
                draws INT DEFAULT 0,
                battle_duration_seconds INT DEFAULT 0,
                match_type ENUM('random','friend') NOT NULL DEFAULT 'random',
                started_at TIMESTAMP NULL,
                finished_at TIMESTAMP NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (player1_id) REFERENCES users(user_id) ON DELETE CASCADE,
                FOREIGN KEY (player2_id) REFERENCES users(user_id) ON DELETE CASCADE,
                FOREIGN KEY (winner_id) REFERENCES users(user_id) ON DELETE SET NULL,
                INDEX idx_player1 (player1_id),
                INDEX idx_player2 (player2_id),
                INDEX idx_winner (winner_id),
                INDEX idx_created_at (created_at),
                INDEX idx_fight_no (fight_no),
                INDEX idx_match_type (match_type)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """))
        print("✅ battle_resultsテーブル作成完了")
        
        # 2. バトルラウンド詳細
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS battle_rounds (
                round_id VARCHAR(100) PRIMARY KEY,
                battle_id VARCHAR(100) NOT NULL,
                round_number INT NOT NULL,
                player1_hand ENUM('rock', 'paper', 'scissors') NULL,
                player2_hand ENUM('rock', 'paper', 'scissors') NULL,
                player1_result ENUM('win', 'lose', 'draw') NULL,
                player2_result ENUM('win', 'lose', 'draw') NULL,
                winner_id VARCHAR(50) NULL,
                round_result ENUM('player1_win', 'player2_win', 'draw') NULL,
                round_duration_seconds INT DEFAULT 0,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (battle_id) REFERENCES battle_results(battle_id) ON DELETE CASCADE,
                FOREIGN KEY (winner_id) REFERENCES users(user_id) ON DELETE SET NULL,
                INDEX idx_battle_id (battle_id),
                INDEX idx_round_number (round_number),
                INDEX idx_submitted_at (submitted_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """))
        print("✅ battle_roundsテーブル作成完了")
        
        # 3. ユーザー統計テーブルは006_user_stats_migrationで作成
        print("ℹ️  user_statsテーブルは006_user_stats_migrationで作成されます")
        
        # 4. 日次ランキング
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS daily_rankings (
                ranking_id VARCHAR(100) PRIMARY KEY,
                ranking_position INT NOT NULL,
                ranking_date DATE NOT NULL,
                user_id VARCHAR(50) NOT NULL,
                daily_wins INT DEFAULT 0,
                daily_matches INT DEFAULT 0,
                daily_win_rate DECIMAL(5,2) DEFAULT 0.00,
                last_win_at DATETIME NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                UNIQUE KEY unique_daily_rank (ranking_date, user_id),
                INDEX idx_ranking_date (ranking_date),
                INDEX idx_ranking_position (ranking_position),
                INDEX idx_last_win (last_win_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """))
        print("✅ daily_rankingsテーブル作成完了")
        
        # 5. 週次ランキング
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS weekly_rankings (
                ranking_id VARCHAR(100) PRIMARY KEY,
                ranking_position INT NOT NULL,
                ranking_week DATE NOT NULL,
                user_id VARCHAR(50) NOT NULL,
                weekly_wins INT DEFAULT 0,
                weekly_matches INT DEFAULT 0,
                weekly_win_rate DECIMAL(5,2) DEFAULT 0.00,
                last_win_at DATETIME NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                UNIQUE KEY unique_weekly_rank (ranking_week, user_id),
                INDEX idx_ranking_week (ranking_week),
                INDEX idx_ranking_position (ranking_position),
                INDEX idx_last_win (last_win_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """))
        print("✅ weekly_rankingsテーブル作成完了")
        
        print("✅ ゲームシステムマイグレーション完了")
    
    @staticmethod
    def down(connection: Connection) -> None:
        """マイグレーション取り消し"""
        
        tables = [
            'weekly_rankings',
            'daily_rankings',
            'battle_rounds',
            'battle_results'
        ]
        
        for table in tables:
            connection.execute(text(f"DROP TABLE IF EXISTS {table}"))
        
        print("✅ ゲームシステムマイグレーション取り消し完了")
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        """マイグレーション情報"""
        return {
            'name': '004_game_system_migration',
            'description': 'じゃんけんゲーム・統計・ランキングシステム',
            'tables': ['battle_results', 'battle_rounds', 'daily_rankings', 'weekly_rankings'],
            'dependencies': ['001_initial_migration']
        }

if __name__ == "__main__":
    # データベース接続とマイグレーション実行
    from sqlalchemy import create_engine
    from sqlalchemy.engine import Connection
    
    # データベース接続
    engine = create_engine("mysql+pymysql://root:password@mysql:3306/janken_db")
    
    with engine.connect() as connection:
        GameSystemMigration.up(connection)
        connection.commit()
