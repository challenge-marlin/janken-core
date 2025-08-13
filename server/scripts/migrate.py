#!/usr/bin/env python3
"""
Laravel風マイグレーションシステム
php artisan migrate 相当
"""
import os
import sys
import importlib.util
from pathlib import Path
from sqlalchemy import create_engine, text
from typing import List, Dict, Any
import argparse

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class MigrationRunner:
    """Laravel風マイグレーション実行器"""
    
    def __init__(self, db_url: str):
        """
        Args:
            db_url: データベース接続URL
        """
        self.engine = create_engine(db_url)
        self.migrations_dir = Path(__file__).parent.parent / "database" / "migrations"
        
        # マイグレーション履歴テーブル作成
        self._ensure_migrations_table()
    
    def _ensure_migrations_table(self):
        """マイグレーション履歴テーブル作成（Laravel migrations テーブル相当）"""
        with self.engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS migrations (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    migration VARCHAR(255) NOT NULL,
                    batch INT NOT NULL,
                    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.commit()
    
    def _get_migration_files(self) -> List[Path]:
        """マイグレーションファイル一覧を取得（番号順）"""
        files = list(self.migrations_dir.glob("*.py"))
        files = [f for f in files if not f.name.startswith("__")]
        return sorted(files)
    
    def _load_migration_class(self, file_path: Path):
        """マイグレーションクラスを動的ロード"""
        spec = importlib.util.spec_from_file_location("migration", file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # クラス名を推測（ファイル名から）
        class_name = self._file_to_class_name(file_path.stem)
        return getattr(module, class_name)
    
    def _file_to_class_name(self, filename: str) -> str:
        """ファイル名からクラス名を生成"""
        # 001_initial_migration -> InitialMigration
        parts = filename.split('_')[1:]  # 番号部分を除外
        return ''.join(word.capitalize() for word in parts)
    
    def _get_executed_migrations(self) -> List[str]:
        """実行済みマイグレーション一覧"""
        with self.engine.connect() as conn:
            result = conn.execute(text("SELECT migration FROM migrations ORDER BY id"))
            return [row[0] for row in result]
    
    def _mark_migration_executed(self, migration_name: str, batch: int):
        """マイグレーション実行履歴を記録"""
        with self.engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO migrations (migration, batch) VALUES (:migration, :batch)
            """), {"migration": migration_name, "batch": batch})
            conn.commit()
    
    def migrate(self, target: str = None) -> None:
        """マイグレーション実行 (php artisan migrate)"""
        print("🚀 Laravel風マイグレーション実行開始")
        print("=" * 50)
        
        migration_files = self._get_migration_files()
        executed_migrations = self._get_executed_migrations()
        
        # 次のバッチ番号を決定
        with self.engine.connect() as conn:
            result = conn.execute(text("SELECT COALESCE(MAX(batch), 0) + 1 FROM migrations"))
            next_batch = result.scalar()
        
        executed_count = 0
        
        for file_path in migration_files:
            migration_name = file_path.stem
            
            # 指定されたターゲットまで実行
            if target and migration_name > target:
                break
            
            # 未実行のマイグレーションのみ実行
            if migration_name not in executed_migrations:
                try:
                    print(f"📋 実行中: {migration_name}")
                    
                    # マイグレーションクラスをロードして実行
                    migration_class = self._load_migration_class(file_path)
                    
                    with self.engine.connect() as conn:
                        migration_class.up(conn)
                        conn.commit()
                    
                    # 実行履歴を記録
                    self._mark_migration_executed(migration_name, next_batch)
                    
                    print(f"✅ 完了: {migration_name}")
                    executed_count += 1
                    
                except Exception as e:
                    print(f"❌ エラー: {migration_name} - {e}")
                    raise
            else:
                print(f"⏭️  スキップ: {migration_name} (実行済み)")
        
        if executed_count == 0:
            print("📝 実行するマイグレーションはありません")
        else:
            print(f"🎉 {executed_count}個のマイグレーションを実行しました")
    
    def rollback(self, steps: int = 1) -> None:
        """マイグレーション取り消し (php artisan migrate:rollback)"""
        print(f"🔄 マイグレーション取り消し (最新{steps}バッチ)")
        print("=" * 50)
        
        with self.engine.connect() as conn:
            # 取り消し対象バッチを特定
            result = conn.execute(text("""
                SELECT DISTINCT batch FROM migrations 
                ORDER BY batch DESC 
                LIMIT :steps
            """), {"steps": steps})
            target_batches = [row[0] for row in result]
            
            if not target_batches:
                print("📝 取り消すマイグレーションはありません")
                return
            
            # 各バッチのマイグレーションを取り消し
            for batch in target_batches:
                result = conn.execute(text("""
                    SELECT migration FROM migrations 
                    WHERE batch = :batch 
                    ORDER BY id DESC
                """), {"batch": batch})
                
                migrations_to_rollback = [row[0] for row in result]
                
                for migration_name in migrations_to_rollback:
                    try:
                        print(f"🔄 取り消し中: {migration_name}")
                        
                        # マイグレーションファイルを見つけて実行
                        file_path = self.migrations_dir / f"{migration_name}.py"
                        if file_path.exists():
                            migration_class = self._load_migration_class(file_path)
                            migration_class.down(conn)
                        
                        # 履歴から削除
                        conn.execute(text("""
                            DELETE FROM migrations WHERE migration = :migration
                        """), {"migration": migration_name})
                        
                        print(f"✅ 取り消し完了: {migration_name}")
                        
                    except Exception as e:
                        print(f"❌ 取り消しエラー: {migration_name} - {e}")
                        raise
            
            conn.commit()
            print("🎉 マイグレーション取り消し完了")
    
    def status(self) -> None:
        """マイグレーション状況表示 (php artisan migrate:status)"""
        print("📊 マイグレーション状況")
        print("=" * 50)
        
        migration_files = self._get_migration_files()
        executed_migrations = self._get_executed_migrations()
        
        for file_path in migration_files:
            migration_name = file_path.stem
            status = "✅ 実行済み" if migration_name in executed_migrations else "⏳ 未実行"
            print(f"{status} | {migration_name}")

def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='Laravel風マイグレーションシステム')
    parser.add_argument('command', choices=['migrate', 'rollback', 'status'],
                       help='実行コマンド')
    parser.add_argument('--steps', type=int, default=1,
                       help='rollback時のステップ数')
    parser.add_argument('--target', type=str,
                       help='migrate時のターゲットマイグレーション')
    parser.add_argument('--db-url', type=str,
                       default='mysql+pymysql://root:password@mysql:3306/janken_db',
                       help='データベース接続URL')
    
    args = parser.parse_args()
    
    runner = MigrationRunner(args.db_url)
    
    if args.command == 'migrate':
        runner.migrate(args.target)
    elif args.command == 'rollback':
        runner.rollback(args.steps)
    elif args.command == 'status':
        runner.status()

if __name__ == "__main__":
    main()
