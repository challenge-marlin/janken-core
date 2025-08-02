#!/usr/bin/env python3
"""
Alembicマイグレーション実行スクリプト

Python環境やAlembicコマンドが利用できない場合の代替手段として使用します。
既存のSQLファイルベースでのマイグレーション処理を提供します。
"""

import os
import sys
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


def create_alembic_version_table(cursor):
    """Alembicバージョン管理テーブルの作成"""
    create_sql = """
    CREATE TABLE IF NOT EXISTS alembic_version (
        version_num VARCHAR(32) NOT NULL,
        PRIMARY KEY (version_num)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    
    try:
        cursor.execute(create_sql)
        print("✅ alembic_versionテーブル作成完了")
        return True
    except Error as e:
        print(f"❌ alembic_versionテーブル作成エラー: {e}")
        return False


def set_migration_version(cursor, version: str):
    """マイグレーションバージョンを設定"""
    try:
        # 既存レコードを削除
        cursor.execute("DELETE FROM alembic_version")
        
        # 新しいバージョンを挿入
        cursor.execute("INSERT INTO alembic_version (version_num) VALUES (%s)", (version,))
        print(f"✅ マイグレーションバージョンを {version} に設定")
        return True
    except Error as e:
        print(f"❌ バージョン設定エラー: {e}")
        return False


def check_database_exists(config):
    """データベースの存在確認"""
    try:
        # データベースを指定せずに接続
        temp_config = config.copy()
        del temp_config['database']
        
        connection = mysql.connector.connect(**temp_config)
        cursor = connection.cursor()
        
        cursor.execute(f"SHOW DATABASES LIKE '{config['database']}'")
        result = cursor.fetchone()
        
        exists = result is not None
        
        cursor.close()
        connection.close()
        
        return exists
    except Error as e:
        print(f"❌ データベース確認エラー: {e}")
        return False


def create_database(config):
    """データベースの作成"""
    try:
        # データベースを指定せずに接続
        temp_config = config.copy()
        database_name = temp_config.pop('database')
        
        connection = mysql.connector.connect(**temp_config)
        cursor = connection.cursor()
        
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"✅ データベース '{database_name}' 作成完了")
        
        cursor.close()
        connection.close()
        
        return True
    except Error as e:
        print(f"❌ データベース作成エラー: {e}")
        return False


def run_migration(env: str = "local", target_revision: str = "001"):
    """マイグレーション実行"""
    
    print(f"🚀 マイグレーション実行開始 (環境: {env})")
    print(f"📋 対象リビジョン: {target_revision}")
    
    # データベース設定取得
    config = get_database_config(env)
    print(f"📡 接続先: {config['host']}:{config['port']}/{config['database']}")
    
    # データベース存在確認・作成
    if not check_database_exists(config):
        print(f"📦 データベース '{config['database']}' が存在しません。作成します...")
        if not create_database(config):
            return False
    
    try:
        # データベース接続
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        
        print("✅ データベース接続成功")
        
        # Alembicバージョンテーブル作成
        if not create_alembic_version_table(cursor):
            return False
        
        # 現在のマイグレーションバージョン確認
        try:
            cursor.execute("SELECT version_num FROM alembic_version")
            current_version = cursor.fetchone()
            current_version = current_version[0] if current_version else None
        except Error:
            current_version = None
        
        if current_version:
            print(f"📌 現在のバージョン: {current_version}")
        else:
            print("📌 初回マイグレーション")
        
        if current_version == target_revision:
            print(f"✨ 既に最新バージョン ({target_revision}) です")
            return True
        
        # マイグレーション実行（create_tables.sqlを使用）
        docs_sql_path = project_root / "docs" / "database" / "sql" / "create_tables.sql"
        
        if not docs_sql_path.exists():
            print(f"❌ マイグレーションファイルが見つかりません: {docs_sql_path}")
            return False
        
        print(f"📂 マイグレーションファイル実行: {docs_sql_path.name}")
        
        # SQLファイル読み込み・実行
        with open(docs_sql_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # SQL文を分割して実行
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip() and not stmt.strip().startswith('--')]
        
        executed_count = 0
        for statement in statements:
            if statement:
                try:
                    cursor.execute(statement)
                    executed_count += 1
                except Error as e:
                    print(f"⚠️  SQL実行警告: {e}")
                    # CREATE TABLE IF NOT EXISTS の場合は警告として継続
                    if "already exists" not in str(e).lower():
                        raise
        
        print(f"✅ {executed_count}件のSQL文を実行")
        
        # バージョン設定
        if not set_migration_version(cursor, target_revision):
            return False
        
        connection.commit()
        print(f"🎉 マイグレーション完了: {target_revision}")
        
        # テーブル確認
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"📊 作成済みテーブル数: {len(tables)}")
        
        return True
        
    except Error as e:
        print(f"❌ マイグレーションエラー: {e}")
        if 'connection' in locals():
            connection.rollback()
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
    import argparse
    
    parser = argparse.ArgumentParser(description='Alembicマイグレーション実行')
    parser.add_argument('--env', choices=['local', 'docker', 'vps'], default='local',
                       help='環境選択 (default: local)')
    parser.add_argument('--revision', default='001',
                       help='マイグレーションリビジョン (default: 001)')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🚀 じゃんけんゲーム マイグレーション")
    print("=" * 60)
    
    success = run_migration(args.env, args.revision)
    
    if success:
        print("\n✨ マイグレーションが正常に完了しました！")
        print("🌱 次はシードデータを投入してください:")
        print(f"   python scripts/seed_database.py --env {args.env}")
        exit(0)
    else:
        print("\n💥 マイグレーションに失敗しました")
        exit(1)


if __name__ == "__main__":
    main()