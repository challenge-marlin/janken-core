#!/bin/bash
set -e

echo "🐳 Docker環境でのデータベースセットアップ開始"
echo "=" * 60

# MySQLの起動を待機
echo "⏳ MySQLサーバーの起動を待機中..."
while ! mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASSWORD" -e "SELECT 1" >/dev/null 2>&1; do
    echo "   MySQL接続試行中... (host: $DB_HOST:$DB_PORT)"
    sleep 2
done

echo "✅ MySQL接続確認完了"

# 引数に応じた処理実行
case "${1:-setup}" in
    "setup")
        echo "🚀 フルセットアップ実行（マイグレーション + シードデータ）"
        python scripts/setup_database.py --env docker --force
        ;;
    "migration")
        echo "📋 マイグレーションのみ実行"
        python scripts/run_migrations.py --env docker
        ;;
    "seed")
        echo "🌱 シードデータのみ投入"
        python scripts/seed_database.py --env docker --force
        ;;
    "reset")
        echo "💥 データベースリセット + フルセットアップ"
        python scripts/setup_database.py --env docker --force
        ;;
    *)
        echo "❌ 不明なコマンド: $1"
        echo "利用可能なコマンド: setup, migration, seed, reset"
        exit 1
        ;;
esac

echo "🎉 データベースセットアップ完了！"