#!/usr/bin/env python3
"""
Laravel風シーダー実行スクリプト
php artisan db:seed 相当の機能

使用方法:
    python seed.py --class UserSeeder    # 特定のシーダーを実行
    python seed.py --all                 # 全シーダーを実行
    python seed.py --list                # 利用可能なシーダー一覧表示
"""

import sys
import os
import argparse
from typing import Dict, Any, List
import importlib.util

# プロジェクトルートをパスに追加
sys.path.append('.')

def load_seeder(seeder_name: str):
    """シーダーファイルを動的に読み込み"""
    try:
        # シーダーファイルのパス
        seeder_path = f'database/seeders/{seeder_name}.py'
        
        if not os.path.exists(seeder_path):
            print(f"❌ シーダーファイルが見つかりません: {seeder_path}")
            return None
        
        # モジュールとして読み込み
        spec = importlib.util.spec_from_file_location(seeder_name, seeder_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # シーダークラスを取得
        seeder_class = getattr(module, seeder_name, None)
        if not seeder_class:
            print(f"❌ シーダークラスが見つかりません: {seeder_name}")
            return None
        
        return seeder_class
        
    except Exception as e:
        print(f"❌ シーダー読み込みエラー: {e}")
        return None

def get_available_seeders() -> List[str]:
    """利用可能なシーダー一覧を取得"""
    seeders_dir = 'database/seeders'
    if not os.path.exists(seeders_dir):
        return []
    
    seeders = []
    for file in os.listdir(seeders_dir):
        if file.endswith('.py') and not file.startswith('__'):
            seeder_name = file[:-3]  # .pyを除去
            seeders.append(seeder_name)
    
    return seeders

def run_seeder(seeder_name: str, connection) -> bool:
    """特定のシーダーを実行"""
    print(f"🌱 シーダー実行開始: {seeder_name}")
    print("=" * 50)
    
    try:
        # シーダークラスを読み込み
        seeder_class = load_seeder(seeder_name)
        if not seeder_class:
            return False
        
        # シーダー情報を表示
        if hasattr(seeder_class, 'get_info'):
            info = seeder_class.get_info()
            print(f"📋 シーダー情報:")
            print(f"   名前: {info.get('name', seeder_name)}")
            print(f"   説明: {info.get('description', '説明なし')}")
            print(f"   対象テーブル: {', '.join(info.get('tables', []))}")
            print()
        
        # シーダー実行
        seeder_class.run(connection)
        
        print("=" * 50)
        print(f"✅ シーダー実行完了: {seeder_name}")
        return True
        
    except Exception as e:
        print(f"❌ シーダー実行エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_all_seeders(connection) -> bool:
    """全シーダーを実行"""
    print("🌱 全シーダー実行開始")
    print("=" * 50)
    
    available_seeders = get_available_seeders()
    if not available_seeders:
        print("❌ 利用可能なシーダーが見つかりません")
        return False
    
    print(f"📋 実行対象シーダー: {', '.join(available_seeders)}")
    print()
    
    success_count = 0
    total_count = len(available_seeders)
    
    for seeder_name in available_seeders:
        if run_seeder(seeder_name, connection):
            success_count += 1
        print()  # 空行を追加
    
    print("=" * 50)
    print(f"🎉 全シーダー実行完了: {success_count}/{total_count} 成功")
    
    return success_count == total_count

def list_seeders():
    """利用可能なシーダー一覧を表示"""
    print("📋 利用可能なシーダー一覧")
    print("=" * 30)
    
    available_seeders = get_available_seeders()
    if not available_seeders:
        print("❌ 利用可能なシーダーが見つかりません")
        return
    
    for i, seeder_name in enumerate(available_seeders, 1):
        print(f"{i:2d}. {seeder_name}")
        
        # シーダー情報を表示
        try:
            seeder_class = load_seeder(seeder_name)
            if seeder_class and hasattr(seeder_class, 'get_info'):
                info = seeder_class.get_info()
                print(f"    📝 {info.get('description', '説明なし')}")
                print(f"    🗄️  {', '.join(info.get('tables', []))}")
        except:
            pass
        
        print()

def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description='Laravel風シーダー実行スクリプト',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
    python seed.py --class UserSeeder    # UserSeederを実行
    python seed.py --all                 # 全シーダーを実行
    python seed.py --list                # シーダー一覧表示
        """
    )
    
    parser.add_argument(
        '--class', '-c',
        dest='seeder_class',
        help='実行するシーダークラス名'
    )
    
    parser.add_argument(
        '--all', '-a',
        action='store_true',
        help='全シーダーを実行'
    )
    
    parser.add_argument(
        '--list', '-l',
        action='store_true',
        help='利用可能なシーダー一覧を表示'
    )
    
    args = parser.parse_args()
    
    # 引数チェック
    if not any([args.seeder_class, args.all, args.list]):
        parser.print_help()
        return
    
    # シーダー一覧表示
    if args.list:
        list_seeders()
        return
    
    # データベース接続
    try:
        from sqlalchemy import create_engine
        # 環境変数からデータベースURLを取得、デフォルトはMySQL
        db_url = os.getenv('DATABASE_URL', 'mysql+pymysql://root:password@mysql:3306/janken_db')
        engine = create_engine(db_url)
        connection = engine.connect()
        print("🔌 データベース接続完了")
        print()
    except Exception as e:
        print(f"❌ データベース接続エラー: {e}")
        print("💡 ヒント: データベースが起動しているか確認してください")
        return
    
    try:
        # 特定のシーダー実行
        if args.seeder_class:
            success = run_seeder(args.seeder_class, connection)
            if not success:
                sys.exit(1)
        
        # 全シーダー実行
        elif args.all:
            success = run_all_seeders(connection)
            if not success:
                sys.exit(1)
        
    finally:
        # 接続を閉じる
        try:
            connection.close()
            print("🔌 データベース接続を閉じました")
        except:
            pass

if __name__ == '__main__':
    main()
