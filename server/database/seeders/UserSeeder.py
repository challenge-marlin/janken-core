"""
ユーザーシーダー
Laravel風: UserSeeder 相当
"""
from sqlalchemy import text
from typing import Dict, Any

class UserSeeder:
    """テストユーザーとシステム設定の初期データ投入"""
    
    @staticmethod
    def run(connection) -> None:
        """シーダー実行 (php artisan db:seed --class=UserSeeder 相当)"""
        
        print("🌱 ユーザーシーダー実行中...")
        
        # 1. テストユーザー作成
        test_users = [
            {
                'user_id': 'test_user_1',
                'email': 'test1@example.com',
                'nickname': 'テストユーザー1',
                'role': 'developer',
                'title': 'テストプレイヤー',
                'alias': 'じゃんけんテスター1'
            },
            {
                'user_id': 'test_user_2',
                'email': 'test2@example.com',
                'nickname': 'テストユーザー2',
                'role': 'developer',
                'title': 'テストプレイヤー',
                'alias': 'じゃんけんテスター2'
            },
            {
                'user_id': 'test_user_3',
                'email': 'test3@example.com',
                'nickname': 'テストユーザー3',
                'role': 'developer',
                'title': 'テストプレイヤー',
                'alias': 'じゃんけんテスター3'
            },
            {
                'user_id': 'test_user_4',
                'email': 'test4@example.com',
                'nickname': 'テストユーザー4',
                'role': 'developer',
                'title': 'テストプレイヤー',
                'alias': 'じゃんけんテスター4'
            },
            {
                'user_id': 'test_user_5',
                'email': 'test5@example.com',
                'nickname': 'テストユーザー5',
                'role': 'developer',
                'title': 'テストプレイヤー',
                'alias': 'じゃんけんテスター5'
            }
        ]
        
        for user in test_users:
            connection.execute(text("""
                INSERT IGNORE INTO users (user_id, email, nickname, role, title, alias)
                VALUES (:user_id, :email, :nickname, :role, :title, :alias)
            """), user)
        
        connection.commit()
        print(f"✅ {len(test_users)}名のテストユーザーを作成")
        
        # 2. システム設定
        system_settings = [
            ('max_concurrent_battles', '100', '同時実行可能なバトル数'),
            ('battle_timeout_seconds', '300', 'バトルセッションのタイムアウト時間（秒）'),
            ('magic_link_expiry_minutes', '15', 'Magic Linkの有効期限（分）'),
            ('jwt_access_token_expiry_minutes', '15', 'JWTアクセストークンの有効期限（分）'),
            ('jwt_refresh_token_expiry_days', '30', 'JWTリフレッシュトークンの有効期限（日）'),
            ('session_timeout_minutes', '60', 'セッションタイムアウト（分）'),
            ('max_concurrent_sessions_per_user', '5', 'ユーザーあたりの最大同時セッション数'),
            ('max_login_attempts_per_ip', '10', 'IP別最大ログイン試行数'),
            ('login_attempt_lockout_minutes', '30', 'ログイン試行失敗時のロックアウト時間（分）'),
            ('2fa_required_for_admin', 'true', '管理者に2FA必須化'),
            ('oauth_providers_enabled', 'google,line,apple', '有効化するOAuthプロバイダー')
        ]
        
        for setting_key, setting_value, description in system_settings:
            connection.execute(text("""
                INSERT IGNORE INTO system_settings (setting_key, setting_value, description)
                VALUES (:key, :value, :desc)
            """), {"key": setting_key, "value": setting_value, "desc": description})
        
        connection.commit()
        print(f"✅ {len(system_settings)}件のシステム設定を作成")
        
        # 3. ユーザー統計初期化
        connection.execute(text("""
            INSERT IGNORE INTO user_stats (user_id) 
            SELECT user_id FROM users WHERE user_id LIKE 'test_user_%'
        """))
        
        connection.commit()
        print("✅ テストユーザーの統計データを初期化")
        
        print("🎉 ユーザーシーダー実行完了")
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        """シーダー情報"""
        return {
            'name': 'UserSeeder',
            'description': 'テストユーザー・システム設定・統計データの初期投入',
            'tables': ['users', 'system_settings', 'user_stats']
        }
