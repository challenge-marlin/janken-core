"""
ユーザーステータステーブル専用マイグレーション
既存のuser_statsテーブルを削除して正しい構造で再作成
"""

from sqlalchemy import text
from sqlalchemy.engine import Connection
from typing import Dict, Any

class UserStatsMigration:
    """ユーザーステータステーブルの正しい構造での再作成"""
    
    @staticmethod
    def up(connection: Connection) -> None:
        """マイグレーション実行"""
        
        print("✅ ユーザーステータスマイグレーション開始: user_statsテーブル再作成")
        
        # 1. 既存のuser_statsテーブルを削除
        connection.execute(text("DROP TABLE IF EXISTS user_stats"))
        print("✅ 既存のuser_statsテーブルを削除")
        
        # 2. 正しい構造でuser_statsテーブルを作成
        connection.execute(text("""
            CREATE TABLE user_stats (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id VARCHAR(50) NOT NULL,
                
                # 基本統計
                total_matches INT DEFAULT 0,
                total_wins INT DEFAULT 0,
                total_losses INT DEFAULT 0,
                total_draws INT DEFAULT 0,
                win_rate DECIMAL(5,2) DEFAULT 0.00,
                current_streak INT DEFAULT 0,
                best_streak INT DEFAULT 0,
                total_rounds_played INT DEFAULT 0,
                
                # 手の統計
                rock_count INT DEFAULT 0,
                paper_count INT DEFAULT 0,
                scissors_count INT DEFAULT 0,
                favorite_hand VARCHAR(10),
                
                # バトル詳細
                average_battle_duration_seconds INT DEFAULT 0,
                last_battle_at TIMESTAMP NULL,
                
                # 称号・二つ名
                title VARCHAR(100) DEFAULT '',
                available_titles VARCHAR(255) DEFAULT '',
                alias VARCHAR(100) DEFAULT '',
                show_title BOOLEAN DEFAULT TRUE,
                show_alias BOOLEAN DEFAULT TRUE,
                
                # ランキング
                user_rank VARCHAR(20) DEFAULT 'no_rank',
                
                # 日次統計
                daily_wins INT DEFAULT 0,
                daily_ranking INT NULL,
                
                # 最近の結果
                recent_hand_results_str VARCHAR(255) DEFAULT '',
                
                # リセット管理
                last_reset_at DATE NOT NULL DEFAULT (CURDATE()),
                
                # タイムスタンプ
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                
                # インデックス
                INDEX idx_user_id (user_id),
                INDEX idx_total_matches (total_matches),
                INDEX idx_win_rate (win_rate),
                INDEX idx_user_rank (user_rank),
                INDEX idx_daily_ranking (daily_ranking),
                INDEX idx_last_battle (last_battle_at),
                INDEX idx_favorite_hand (favorite_hand)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """))
        print("✅ user_statsテーブルを正しい構造で作成完了")
        
        print("✅ ユーザーステータスマイグレーション完了")
    
    @staticmethod
    def down(connection: Connection) -> None:
        """マイグレーション取り消し"""
        
        connection.execute(text("DROP TABLE IF EXISTS user_stats"))
        print("✅ user_statsテーブルを削除")
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        """マイグレーション情報"""
        return {
            'name': '006_user_stats_migration',
            'description': 'ユーザーステータステーブルの正しい構造での再作成',
            'tables': ['user_stats'],
            'dependencies': ['001_initial_migration']
        }

if __name__ == "__main__":
    # データベース接続とマイグレーション実行
    from sqlalchemy import create_engine
    from sqlalchemy.engine import Connection
    
    # データベース接続
    engine = create_engine("mysql+pymysql://root:password@mysql:3306/janken_db")
    
    with engine.connect() as connection:
        UserStatsMigration.up(connection)
        connection.commit()
