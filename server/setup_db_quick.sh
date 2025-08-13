#!/bin/bash
# じゃんけんアプリ データベース クイックセットアップスクリプト
# create_tables.sql 対応版

echo "=== じゃんけんアプリ データベースセットアップ開始 ==="

# 1. MySQLサービス起動
echo "1. MySQLサービス起動中..."
docker-compose up -d mysql

# 2. MySQL起動待機
echo "2. MySQL起動待機中（30秒）..."
sleep 30

# 3. テーブル作成
echo "3. 完全認証システムテーブル作成中..."
docker cp database/sql/create_tables.sql kaminote-janken-mysql:/tmp/
docker-compose exec mysql mysql -u root -ppassword -e "source /tmp/create_tables.sql"

if [ $? -eq 0 ]; then
    echo "✅ テーブル作成成功"
else
    echo "❌ テーブル作成失敗"
    exit 1
fi

# 4. テーブル作成確認
echo "4. テーブル作成確認..."
echo "=== 作成されたテーブル一覧 ==="
docker-compose exec mysql mysql -u root -ppassword janken_battle_complete -e "SHOW TABLES;"

# 5. 基本データ確認
echo "=== 基本データ確認 ==="
docker-compose exec mysql mysql -u root -ppassword janken_battle_complete -e "
SELECT 'ユーザー数' as item, COUNT(*) as count FROM users
UNION ALL
SELECT 'システム設定数', COUNT(*) FROM system_settings
UNION ALL
SELECT 'テストユーザー数', COUNT(*) FROM users WHERE role = 'developer';
"

# 6. 認証テーブル詳細確認
echo "=== 認証システムテーブル情報 ==="
docker-compose exec mysql mysql -u root -ppassword janken_battle_complete -e "
SELECT 
    table_name, 
    table_rows,
    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS 'Size (MB)'
FROM information_schema.tables 
WHERE table_schema = 'janken_battle_complete'
AND table_name IN ('users', 'sessions', 'magic_link_tokens', 'refresh_tokens', 'user_stats')
ORDER BY table_name;
"

# 7. 全サービス起動
echo "7. 全サービス起動中..."
docker-compose up -d

# 8. 起動確認
echo "8. サービス起動確認..."
sleep 10
docker-compose ps

echo ""
echo "=== セットアップ完了 ==="
echo "🎉 じゃんけんアプリのデータベースセットアップが完了しました！"
echo ""
echo "📋 アクセス情報:"
echo "- アプリケーション: http://localhost"
echo "- API ヘルスチェック: http://localhost/api/health"
echo "- phpMyAdmin: http://localhost:8080 (root/password)"
echo "- Redis Commander: http://localhost:8081"
echo ""
echo "🔧 確認コマンド:"
echo "docker-compose exec mysql mysql -u root -ppassword janken_battle_complete -e \"SHOW TABLES;\""
echo "docker-compose exec mysql mysql -u root -ppassword janken_battle_complete -e \"SELECT user_id, email, nickname FROM users;\""
