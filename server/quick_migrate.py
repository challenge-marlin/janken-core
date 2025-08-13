#!/usr/bin/env python3
"""
簡易マイグレーション実行スクリプト（テスト用）
"""
import os
import sys
import importlib.util
from pathlib import Path

# MySQLコネクタの確認
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    print("❌ pymysql が必要です")
    print("インストール: pip install pymysql")
    sys.exit(1)

def execute_sql(host, port, user, password, database, sql_statement):
    """SQLステートメントを実行"""
    try:
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        
        cursor = connection.cursor()
        cursor.execute(sql_statement)
        connection.commit()
        return True
        
    except Exception as e:
        if "already exists" in str(e).lower():
            print(f"   ⚠️  テーブル既存（スキップ）: {e}")
            return True
        else:
            print(f"   ❌ SQLエラー: {e}")
            return False
    finally:
        if 'connection' in locals() and connection.open:
            cursor.close()
            connection.close()

def run_migration():
    """マイグレーション実行"""
    print("🚀 簡易マイグレーション実行開始")
    print("=" * 50)
    
    # データベース設定
    db_config = {
        'host': 'mysql',
        'port': 3306,
        'user': 'root',
        'password': 'password',
        'database': 'janken_db'
    }
    
    # 1. マイグレーション履歴テーブル作成
    print("📋 マイグレーション履歴テーブル作成中...")
    migrations_table_sql = """
        CREATE TABLE IF NOT EXISTS migrations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            migration VARCHAR(255) NOT NULL,
            batch INT NOT NULL,
            executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    
    if not execute_sql(db_config['host'], db_config['port'], db_config['user'], 
                      db_config['password'], db_config['database'], migrations_table_sql):
        return
    
    print("✅ マイグレーション履歴テーブル作成完了")
    
    # 2. 基本認証システムテーブル作成
    print("📋 基本認証システムテーブル作成中...")
    
    # usersテーブル
    users_sql = """
        CREATE TABLE IF NOT EXISTS users (
            management_code BIGINT AUTO_INCREMENT UNIQUE,
            user_id VARCHAR(50) PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            nickname VARCHAR(100) NOT NULL,
            name VARCHAR(50),
            role ENUM('user', 'developer', 'admin') DEFAULT 'user',
            profile_image_url VARCHAR(500),
            title VARCHAR(100) DEFAULT 'じゃんけんプレイヤー',
            alias VARCHAR(100),
            is_active BOOLEAN DEFAULT TRUE,
            is_banned TINYINT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_email (email),
            INDEX idx_role (role),
            INDEX idx_created_at (created_at),
            INDEX idx_management_code (management_code)
        )
    """
    
    if not execute_sql(db_config['host'], db_config['port'], db_config['user'], 
                      db_config['password'], db_config['database'], users_sql):
        return
    
    # user_statsテーブル
    user_stats_sql = """
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
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    """
    
    if not execute_sql(db_config['host'], db_config['port'], db_config['user'], 
                      db_config['password'], db_config['database'], user_stats_sql):
        return
    
    # system_settingsテーブル
    system_settings_sql = """
        CREATE TABLE IF NOT EXISTS system_settings (
            setting_key VARCHAR(100) PRIMARY KEY,
            setting_value TEXT NOT NULL,
            description TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
    """
    
    if not execute_sql(db_config['host'], db_config['port'], db_config['user'], 
                      db_config['password'], db_config['database'], system_settings_sql):
        return
    
    print("✅ 基本テーブル作成完了")
    
    # 3. テストデータ投入
    print("🌱 テストデータ投入中...")
    
    # テストユーザー
    test_users = [
        "('test_user_1', 'test1@example.com', 'テストユーザー1', 'developer', 'テストプレイヤー', 'じゃんけんテスター1')",
        "('test_user_2', 'test2@example.com', 'テストユーザー2', 'developer', 'テストプレイヤー', 'じゃんけんテスター2')",
        "('test_user_3', 'test3@example.com', 'テストユーザー3', 'developer', 'テストプレイヤー', 'じゃんけんテスター3')"
    ]
    
    users_insert_sql = f"""
        INSERT IGNORE INTO users (user_id, email, nickname, role, title, alias)
        VALUES {', '.join(test_users)}
    """
    
    execute_sql(db_config['host'], db_config['port'], db_config['user'], 
               db_config['password'], db_config['database'], users_insert_sql)
    
    # システム設定
    settings_insert_sql = """
        INSERT IGNORE INTO system_settings (setting_key, setting_value, description) VALUES
        ('magic_link_expiry_minutes', '15', 'Magic Linkの有効期限（分）'),
        ('jwt_access_token_expiry_minutes', '15', 'JWTアクセストークンの有効期限（分）'),
        ('battle_timeout_seconds', '300', 'バトルセッションのタイムアウト時間（秒）')
    """
    
    execute_sql(db_config['host'], db_config['port'], db_config['user'], 
               db_config['password'], db_config['database'], settings_insert_sql)
    
    # ユーザー統計初期化
    stats_insert_sql = """
        INSERT IGNORE INTO user_stats (user_id) 
        SELECT user_id FROM users WHERE user_id LIKE 'test_user_%'
    """
    
    execute_sql(db_config['host'], db_config['port'], db_config['user'], 
               db_config['password'], db_config['database'], stats_insert_sql)
    
    print("✅ テストデータ投入完了")
    
    # 4. マイグレーション履歴記録
    migration_record_sql = """
        INSERT IGNORE INTO migrations (migration, batch) VALUES
        ('001_initial_migration', 1),
        ('002_basic_tables', 1)
    """
    
    execute_sql(db_config['host'], db_config['port'], db_config['user'], 
               db_config['password'], db_config['database'], migration_record_sql)
    
    print("🎉 簡易マイグレーション完了！")
    
    # 5. 結果確認
    print("\n📊 作成されたテーブル:")
    try:
        connection = pymysql.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        for table in tables:
            print(f"   ✅ {table[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"\n👥 作成されたユーザー数: {user_count}")
        
    except Exception as e:
        print(f"❌ 確認エラー: {e}")
    finally:
        if 'connection' in locals() and connection.open:
            cursor.close()
            connection.close()

if __name__ == "__main__":
    run_migration()
