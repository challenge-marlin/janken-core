#!/usr/bin/env python3
"""
データベース総合セットアップスクリプト

マイグレーション実行 + シードデータ投入を一括で行います。
開発環境の構築やリセット時に使用します。

使用方法:
    python scripts/setup_database.py [--env local|vps] [--force]
"""

import sys
import argparse
from pathlib import Path

# プロジェクトルートをパスに追加
script_dir = Path(__file__).parent
project_root = script_dir.parent
sys.path.append(str(project_root))

# スクリプトをインポート
from scripts.run_migrations import run_migration
from scripts.seed_database import seed_database


def setup_database(env: str = "local", force: bool = False):
    """データベースの総合セットアップ"""
    
    print("=" * 60)
    print("🏗️  じゃんけんゲーム データベースセットアップ")
    print("=" * 60)
    print(f"🌍 環境: {env}")
    print(f"💪 強制モード: {'ON' if force else 'OFF'}")
    print()
    
    # Phase 1: マイグレーション実行
    print("📋 PHASE 1: マイグレーション実行")
    print("-" * 40)
    
    if not run_migration(env, "001"):
        print("❌ マイグレーションに失敗しました")
        return False
    
    print("\n✅ マイグレーション完了")
    
    # Phase 2: シードデータ投入
    print("\n🌱 PHASE 2: シードデータ投入")
    print("-" * 40)
    
    if not seed_database(env, force):
        print("❌ シードデータ投入に失敗しました")
        return False
    
    print("\n✅ シードデータ投入完了")
    
    # セットアップ完了
    print("\n" + "=" * 60)
    print("🎉 データベースセットアップ完了！")
    print("=" * 60)
    print()
    print("🎮 ゲームの動作確認方法:")
    print("   1. サーバー起動: docker-compose up -d")
    print("   2. ヘルスチェック: curl http://localhost/api/health")
    print("   3. MySQL確認: curl http://localhost/api/health/mysql")
    print()
    print("📊 利用可能なAPIエンドポイント:")
    print("   • 認証: /api/auth/")
    print("   • ロビー: /api/lobby/")
    print("   • バトル: /api/battle/")
    print("   • ランキング: /api/ranking/")
    print("   • 設定: /api/settings/")
    print()
    
    return True


def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(description='データベース総合セットアップ')
    parser.add_argument('--env', choices=['local', 'docker', 'vps'], default='local',
                       help='環境選択 (default: local)')
    parser.add_argument('--force', action='store_true',
                       help='既存データを強制削除してセットアップ')
    
    args = parser.parse_args()
    
    # 確認プロンプト（強制モードでない場合）
    if not args.force:
        print("⚠️  この操作により既存のデータベースが変更される可能性があります。")
        response = input("続行しますか？ [y/N]: ")
        if response.lower() != 'y':
            print("💫 操作をキャンセルしました")
            return
    
    # セットアップ実行
    success = setup_database(args.env, args.force)
    
    if success:
        exit(0)
    else:
        print("\n💥 セットアップに失敗しました")
        print("🔍 エラーログを確認してください")
        exit(1)


if __name__ == "__main__":
    main()