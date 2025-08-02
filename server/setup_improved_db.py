#!/usr/bin/env python3
"""
改善版データベースセットアップスクリプト

WebSocket対応のじゃんけんバトルDBを構築
"""

import asyncio
import sys
import argparse
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.shared.database.connection_improved import (
    init_database, close_database, get_async_session, db_manager
)
from src.shared.database.models_improved import create_all_tables, drop_all_tables


class DatabaseSetup:
    """データベースセットアップクラス"""
    
    def __init__(self):
        self.sql_dir = project_root / "database" / "sql"
    
    async def run_sql_file(self, file_path: Path):
        """SQLファイルを実行"""
        if not file_path.exists():
            print(f"❌ SQLファイルが見つかりません: {file_path}")
            return False
        
        try:
            print(f"📄 実行中: {file_path.name}")
            
            # SQLファイル読み込み
            with open(file_path, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            # セミコロンで分割して実行
            statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
            
            async with get_async_session() as session:
                for statement in statements:
                    if statement.upper().startswith(('SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER')):
                        try:
                            await session.execute(statement)
                        except Exception as e:
                            print(f"⚠️  SQL実行警告 ({statement[:50]}...): {e}")
                
                await session.commit()
            
            print(f"✅ 完了: {file_path.name}")
            return True
            
        except Exception as e:
            print(f"❌ エラー ({file_path.name}): {e}")
            return False
    
    async def setup_database(self, force: bool = False):
        """データベース全体をセットアップ"""
        try:
            print("🚀 データベースセットアップ開始")
            
            # データベース接続初期化
            await init_database()
            
            if force:
                print("🗑️  既存テーブルを削除")
                drop_all_tables(db_manager.engine.sync_engine)
            
            # 改善版テーブル作成SQLを実行
            improved_sql = self.sql_dir / "01_create_tables_improved.sql"
            if await self.run_sql_file(improved_sql):
                print("✅ 改善版テーブル作成完了")
            else:
                print("❌ 改善版テーブル作成失敗")
                return False
            
            # 改善版シードデータを実行
            seed_sql = self.sql_dir / "02_seed_users_and_stats_improved.sql"
            if await self.run_sql_file(seed_sql):
                print("✅ 改善版シードデータ投入完了")
            else:
                print("❌ 改善版シードデータ投入失敗")
                return False
            
            # 接続テスト
            if await db_manager.test_connection():
                print("✅ データベース接続テスト成功")
            else:
                print("❌ データベース接続テスト失敗")
                return False
            
            print("🎉 データベースセットアップ完了！")
            
            # 作成されたテーブル一覧を表示
            await self.show_tables()
            
            return True
            
        except Exception as e:
            print(f"❌ セットアップエラー: {e}")
            return False
        finally:
            await close_database()
    
    async def show_tables(self):
        """作成されたテーブル一覧を表示"""
        try:
            async with get_async_session() as session:
                result = await session.execute("SHOW TABLES")
                tables = [row[0] for row in result.fetchall()]
                
                print(f"\n📋 作成されたテーブル ({len(tables)}個):")
                for table in sorted(tables):
                    print(f"  - {table}")
                
                # テストデータ件数確認
                print(f"\n📊 データ件数:")
                for table in ['users', 'user_stats', 'match_history', 'daily_ranking']:
                    if table in tables:
                        count_result = await session.execute(f"SELECT COUNT(*) FROM {table}")
                        count = count_result.scalar()
                        print(f"  - {table}: {count}件")
                        
        except Exception as e:
            print(f"⚠️  テーブル確認エラー: {e}")
    
    async def verify_setup(self):
        """セットアップ検証"""
        try:
            print("🔍 セットアップ検証中...")
            
            await init_database()
            
            # 主要テーブルの存在確認
            required_tables = [
                'users', 'user_stats', 'battle_sessions', 'websocket_connections',
                'match_history', 'daily_ranking', 'sessions', 'magic_links'
            ]
            
            async with get_async_session() as session:
                result = await session.execute("SHOW TABLES")
                existing_tables = [row[0] for row in result.fetchall()]
                
                missing_tables = []
                for table in required_tables:
                    if table not in existing_tables:
                        missing_tables.append(table)
                
                if missing_tables:
                    print(f"❌ 不足テーブル: {missing_tables}")
                    return False
                
                # テストユーザーの存在確認
                user_result = await session.execute(
                    "SELECT COUNT(*) FROM users WHERE user_id LIKE 'test-user-%'"
                )
                test_users = user_result.scalar()
                
                if test_users < 5:
                    print(f"❌ テストユーザー不足: {test_users}/5")
                    return False
                
                print(f"✅ 必要テーブル: {len(required_tables)}個すべて存在")
                print(f"✅ テストユーザー: {test_users}個存在")
                print("🎉 セットアップ検証成功！")
                
                return True
                
        except Exception as e:
            print(f"❌ 検証エラー: {e}")
            return False
        finally:
            await close_database()


async def main():
    """メイン実行関数"""
    parser = argparse.ArgumentParser(description='改善版データベースセットアップ')
    parser.add_argument('--force', action='store_true', 
                       help='既存テーブルを強制削除してから作成')
    parser.add_argument('--verify-only', action='store_true',
                       help='セットアップ検証のみ実行')
    parser.add_argument('--show-tables', action='store_true',
                       help='テーブル一覧表示のみ')
    
    args = parser.parse_args()
    
    setup = DatabaseSetup()
    
    if args.show_tables:
        await init_database()
        await setup.show_tables()
        await close_database()
        return
    
    if args.verify_only:
        success = await setup.verify_setup()
        sys.exit(0 if success else 1)
    
    # 通常のセットアップ実行
    success = await setup.setup_database(force=args.force)
    
    if success:
        print("\n" + "="*50)
        print("🎮 じゃんけんバトルDBセットアップ完了！")
        print("="*50)
        print("次のステップ:")
        print("1. サーバー起動: cd server && docker-compose up -d")
        print("2. テストページ: http://localhost/battle/")
        print("3. APIドキュメント: http://localhost/api/docs")
        print("="*50)
        sys.exit(0)
    else:
        print("\n❌ セットアップに失敗しました")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())