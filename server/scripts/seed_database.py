#!/usr/bin/env python3
"""
データベースシードデータ投入スクリプト

使用方法:
    python scripts/seed_database.py [--env local|vps]

既存のSQLシードファイルを使用してデータベースにテストデータを投入します。
"""

import os
import sys
import argparse
from pathlib import Path
import mysql.connector
from mysql.connector import Error

# プロジェクトルートをパスに追加
script_dir = Path(__file__).parent
project_root = script_dir.parent
sys.path.append(str(project_root))


def get_database_config(env: str = "local"):
    """環境に応じたデータベース設定を取得"""
    if env == "local":
        return {
            'host': 'localhost',
            'port': 3306,
            'user': 'root',
            'password': 'password',
            'database': 'janken_db',
            'charset': 'utf8mb4',
            'collation': 'utf8mb4_unicode_ci'
        }
    elif env == "docker":
        return {
            'host': os.getenv('DB_HOST', 'mysql'),
            'port': int(os.getenv('DB_PORT', 3306)),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', 'password'),
            'database': os.getenv('DB_NAME', 'janken_db'),
            'charset': 'utf8mb4',
            'collation': 'utf8mb4_unicode_ci'
        }
    elif env == "vps":
        return {
            'host': '160.251.137.105',
            'port': 3306,
            'user': 'root',
            'password': os.getenv('MYSQL_ROOT_PASSWORD', 'your_vps_password'),
            'database': 'janken_db',
            'charset': 'utf8mb4',
            'collation': 'utf8mb4_unicode_ci'
        }
    else:
        raise ValueError(f"Unknown environment: {env}")


def read_sql_file(file_path: Path) -> str:
    """SQLファイルを読み込み"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"❌ SQLファイルが見つかりません: {file_path}")
        return None
    except Exception as e:
        print(f"❌ SQLファイル読み込みエラー: {e}")
        return None


def execute_sql_statements(cursor, sql_content: str, file_name: str):
    """SQL文を実行（複数文対応）"""
    try:
        # セミコロンでSQL文を分割（ただし文字列内のセミコロンは無視）
        statements = []
        current_statement = ""
        in_string = False
        escape_next = False
        
        for char in sql_content:
            if escape_next:
                current_statement += char
                escape_next = False
                continue
                
            if char == '\\':
                escape_next = True
                current_statement += char
                continue
                
            if char == "'" and not escape_next:
                in_string = not in_string
                
            if char == ';' and not in_string:
                stmt = current_statement.strip()
                if stmt and not stmt.startswith('--'):
                    statements.append(stmt)
                current_statement = ""
            else:
                current_statement += char
        
        # 最後の文が残っている場合
        if current_statement.strip():
            statements.append(current_statement.strip())
        
        executed_count = 0
        for statement in statements:
            if statement and not statement.startswith('--'):
                try:
                    cursor.execute(statement)
                    executed_count += 1
                except Error as e:
                    print(f"⚠️  SQL実行エラー ({file_name}): {e}")
                    print(f"   Problem statement: {statement[:100]}...")
                    continue
        
        print(f"✅ {file_name}: {executed_count}件のSQL文を実行")
        return True
        
    except Exception as e:
        print(f"❌ SQL実行エラー ({file_name}): {e}")
        return False


def seed_database(env: str = "local", force: bool = False):
    """データベースにシードデータを投入"""
    
    print(f"🌱 データベースシード処理開始 (環境: {env})")
    
    # データベース設定取得
    config = get_database_config(env)
    print(f"📡 接続先: {config['host']}:{config['port']}/{config['database']}")
    
    # シードファイルのパス
    sql_dir = project_root / "database" / "sql"
    seed_files = [
        ("01_create_tables.sql", "テーブル作成"),
        ("02_seed_users_and_stats.sql", "ユーザー・統計データ"),
        ("03_seed_daily_ranking.sql", "デイリーランキング"),
        ("04_seed_match_history.sql", "マッチ履歴")
    ]
    
    try:
        # データベース接続
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        
        print("✅ データベース接続成功")
        
        # 既存データ確認
        if not force:
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            if tables:
                print(f"⚠️  {len(tables)}個のテーブルが既に存在します")
                response = input("既存データを削除して続行しますか？ [y/N]: ")
                if response.lower() != 'y':
                    print("💫 処理を中止しました")
                    return False
        
        # データベースの初期化
        if force or (tables and response.lower() == 'y'):
            print("🗑️  既存テーブルを削除中...")
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            cursor.execute("SHOW TABLES")
            existing_tables = [table[0] for table in cursor.fetchall()]
            for table in existing_tables:
                cursor.execute(f"DROP TABLE IF EXISTS {table}")
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            connection.commit()
            print("✅ 既存テーブル削除完了")
        
        # シードファイルの実行
        total_success = 0
        for file_name, description in seed_files:
            file_path = sql_dir / file_name
            print(f"\n📂 {description} ({file_name})")
            
            if not file_path.exists():
                print(f"⚠️  ファイルが見つかりません: {file_path}")
                continue
            
            sql_content = read_sql_file(file_path)
            if sql_content:
                if execute_sql_statements(cursor, sql_content, file_name):
                    total_success += 1
                    connection.commit()
                else:
                    connection.rollback()
        
        print(f"\n🎉 シード処理完了: {total_success}/{len(seed_files)} ファイル成功")
        
        # データ確認
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM match_history")
        match_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM daily_ranking")
        ranking_count = cursor.fetchone()[0]
        
        print(f"\n📊 投入データ統計:")
        print(f"   👤 ユーザー数: {user_count}")
        print(f"   ⚔️  マッチ履歴: {match_count}")
        print(f"   🏆 ランキング: {ranking_count}")
        
        return True
        
    except Error as e:
        print(f"❌ データベースエラー: {e}")
        return False
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        return False
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("🔌 データベース接続を閉じました")


def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(description='データベースシードデータ投入')
    parser.add_argument('--env', choices=['local', 'docker', 'vps'], default='local',
                       help='環境選択 (default: local)')
    parser.add_argument('--force', action='store_true',
                       help='既存データを強制削除')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🌱 じゃんけんゲーム データベースシード")
    print("=" * 60)
    
    success = seed_database(args.env, args.force)
    
    if success:
        print("\n✨ シード処理が正常に完了しました！")
        print("🎮 ゲームを開始できます")
        exit(0)
    else:
        print("\n💥 シード処理に失敗しました")
        exit(1)


if __name__ == "__main__":
    main()