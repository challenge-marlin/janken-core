#!/usr/bin/env python3
"""
データベースセットアップスクリプト
Docker環境でのcreate_tables.sql実行
"""
import os
import sys
import time
import argparse
import mysql.connector
from mysql.connector import Error

def wait_for_mysql(host, port, user, password, max_retries=30):
    """MySQLの起動を待機"""
    print(f"⏳ MySQL接続待機中... (host: {host}:{port})")
    
    for attempt in range(max_retries):
        try:
            connection = mysql.connector.connect(
                host=host,
                port=port,
                user=user,
                password=password
            )
            if connection.is_connected():
                connection.close()
                print("✅ MySQL接続確認完了")
                return True
        except Error:
            print(f"   試行 {attempt + 1}/{max_retries}...")
            time.sleep(2)
    
    raise Exception("MySQL接続タイムアウト")

def execute_sql_file(host, port, user, password, database, sql_file_path):
    """SQLファイルを実行"""
    print(f"📋 SQLファイル実行: {sql_file_path}")
    
    try:
        connection = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password
        )
        
        cursor = connection.cursor()
        
        # SQLファイルを読み込み
        with open(sql_file_path, 'r', encoding='utf-8') as file:
            sql_content = file.read()
        
        # セミコロンで分割して個別実行
        sql_statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        for i, statement in enumerate(sql_statements):
            if statement:
                try:
                    cursor.execute(statement)
                    connection.commit()
                    print(f"   ✅ ステートメント {i+1}/{len(sql_statements)} 完了")
                except Error as e:
                    if "already exists" in str(e).lower():
                        print(f"   ⚠️  ステートメント {i+1}: 既存テーブル（スキップ）")
                    else:
                        print(f"   ❌ ステートメント {i+1} エラー: {e}")
                        # create_tables.sqlの場合は一部エラーを許容
                        continue
        
        print("✅ SQLファイル実行完了")
        
    except Error as e:
        print(f"❌ データベースエラー: {e}")
        raise
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

def main():
    parser = argparse.ArgumentParser(description='データベースセットアップ')
    parser.add_argument('--env', choices=['local', 'docker'], default='docker',
                       help='実行環境')
    parser.add_argument('--force', action='store_true',
                       help='強制実行（確認をスキップ）')
    
    args = parser.parse_args()
    
    # 環境変数から設定取得
    db_config = {
        'host': os.getenv('DB_HOST', 'mysql'),
        'port': int(os.getenv('DB_PORT', '3306')),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', 'password'),
        'database': os.getenv('DB_NAME', 'janken_db')
    }
    
    print("🐳 じゃんけんゲーム - データベースセットアップ")
    print("=" * 50)
    print(f"環境: {args.env}")
    print(f"データベース: {db_config['host']}:{db_config['port']}/{db_config['database']}")
    
    if not args.force:
        confirm = input("セットアップを開始しますか？ (y/N): ")
        if confirm.lower() != 'y':
            print("セットアップをキャンセルしました")
            return
    
    try:
        # MySQL接続待機
        wait_for_mysql(
            db_config['host'], 
            db_config['port'], 
            db_config['user'], 
            db_config['password']
        )
        
        # create_tables.sql実行
        sql_file = '/app/database/sql/create_tables.sql'
        if os.path.exists(sql_file):
            execute_sql_file(
                db_config['host'],
                db_config['port'],
                db_config['user'],
                db_config['password'],
                db_config['database'],
                sql_file
            )
        else:
            print(f"❌ SQLファイルが見つかりません: {sql_file}")
            return
        
        print("🎉 データベースセットアップ完了！")
        
        # テーブル数確認
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = '{db_config['database']}'")
        table_count = cursor.fetchone()[0]
        print(f"📊 作成されたテーブル数: {table_count}")
        
    except Exception as e:
        print(f"❌ セットアップエラー: {e}")
        sys.exit(1)
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    main()
