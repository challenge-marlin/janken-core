"""
ゲーム・統計システムマイグレーション
Laravel風: 2025_01_13_000003_create_game_tables 相当
"""
from sqlalchemy import text
from typing import Dict, Any

class GameSystemMigration:
    """じゃんけんゲーム・統計・ランキングシステム"""
    
    @staticmethod
    def up(connection) -> None:
        """マイグレーション実行"""
        
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
            )
        """))
        
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
            )
        """))
        
        # 3. ユーザー統計
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS user_stats (
                user_id VARCHAR(50) PRIMARY KEY,
                total_matches INT DEFAULT 0,
                total_wins INT DEFAULT 0,
                total_losses INT DEFAULT 0,
                total_draws INT DEFAULT 0,
                win_rate DECIMAL(5,2) DEFAULT 0.00,
                current_streak INT DEFAULT 0,
                best_streak INT DEFAULT 0,
                total_rounds_played INT DEFAULT 0,
                rock_count INT DEFAULT 0,
                paper_count INT DEFAULT 0,
                scissors_count INT DEFAULT 0,
                favorite_hand VARCHAR(10),
                recent_hand_results_str VARCHAR(255) DEFAULT '',
                average_battle_duration_seconds INT DEFAULT 0,
                last_battle_at TIMESTAMP NULL,
                title VARCHAR(50) DEFAULT '',
                available_titles VARCHAR(255) DEFAULT '',
                alias VARCHAR(50) DEFAULT '',
                show_title BOOLEAN DEFAULT TRUE,
                show_alias BOOLEAN DEFAULT TRUE,
                user_rank VARCHAR(20) DEFAULT 'no_rank',
                last_reset_at DATE NOT NULL DEFAULT (CURDATE()),
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                INDEX idx_win_rate (win_rate),
                INDEX idx_total_matches (total_matches),
                INDEX idx_last_battle (last_battle_at),
                INDEX idx_user_rank (user_rank),
                INDEX idx_favorite_hand (favorite_hand)
            )
        """))
        
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
            )
        """))
        
        print("✅ ゲーム・統計システムマイグレーション完了")
    
    @staticmethod
    def down(connection) -> None:
        """マイグレーション取り消し"""
        
        tables = [
            'daily_rankings',
            'user_stats',
            'battle_rounds',
            'battle_results'
        ]
        
        for table in tables:
            connection.execute(text(f"DROP TABLE IF EXISTS {table}"))
        
        print("✅ ゲーム・統計システムマイグレーション取り消し完了")
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        """マイグレーション情報"""
        return {
            'name': '003_game_system_migration',
            'description': 'じゃんけんゲーム・統計・ランキングシステム',
            'tables': ['battle_results', 'battle_rounds', 'user_stats', 'daily_rankings'],
            'dependencies': ['001_initial_migration']
        }
