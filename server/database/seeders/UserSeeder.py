"""
ユーザーシーダー
Laravel風: UserSeeder 相当
DBありきの認証・バトルテスト用に拡張
"""
from sqlalchemy import text
from typing import Dict, Any
import hashlib
import secrets

class UserSeeder:
    """テストユーザーとシステム設定の初期データ投入（DBありき認証・バトル対応）"""
    
    @staticmethod
    def run(connection) -> None:
        """シーダー実行 (php artisan db:seed --class=UserSeeder 相当)"""
        
        print("🌱 ユーザーシーダー実行中...")
        
        # 1. テストユーザー作成（パスワードハッシュ付き）
        test_users = [
            {
                'user_id': 'test_user_1',
                'email': 'test1@example.com',
                'nickname': 'じゃんけんマスター',
                'role': 'developer',
                'title': 'テストプレイヤー',
                'alias': 'じゃんけんテスター1',
                'password_hash': hashlib.sha256('password123'.encode()).hexdigest(),
                'profile_image': 'defaultAvatar1.png',
                'level': 10,
                'experience': 1500
            },
            {
                'user_id': 'test_user_2',
                'email': 'test2@example.com',
                'nickname': 'バトルクイーン',
                'role': 'developer',
                'title': 'テストプレイヤー',
                'alias': 'じゃんけんテスター2',
                'password_hash': hashlib.sha256('password123'.encode()).hexdigest(),
                'profile_image': 'defaultAvatar2.png',
                'level': 8,
                'experience': 1200
            },
            {
                'user_id': 'test_user_3',
                'email': 'test3@example.com',
                'nickname': '勝負師',
                'role': 'developer',
                'title': 'テストプレイヤー',
                'alias': 'じゃんけんテスター3',
                'password_hash': hashlib.sha256('password123'.encode()).hexdigest(),
                'profile_image': 'defaultAvatar3.png',
                'level': 15,
                'experience': 2500
            },
            {
                'user_id': 'test_user_4',
                'email': 'test4@example.com',
                'nickname': '新米戦士',
                'role': 'developer',
                'title': 'テストプレイヤー',
                'alias': 'じゃんけんテスター4',
                'password_hash': hashlib.sha256('password123'.encode()).hexdigest(),
                'profile_image': 'defaultAvatar4.png',
                'level': 3,
                'experience': 300
            },
            {
                'user_id': 'test_user_5',
                'email': 'test5@example.com',
                'nickname': '伝説のプレイヤー',
                'role': 'developer',
                'title': 'テストプレイヤー',
                'alias': 'じゃんけんテスター5',
                'password_hash': hashlib.sha256('password123'.encode()).hexdigest(),
                'profile_image': 'defaultAvatar5.png',
                'level': 25,
                'experience': 5000
            }
        ]
        
        for user in test_users:
            # ユーザー基本情報
            connection.execute(text("""
                INSERT IGNORE INTO users (user_id, email, nickname, role, title, alias, created_at, updated_at)
                VALUES (:user_id, :email, :nickname, :role, :title, :alias, NOW(), NOW())
            """), user)
            
            # ユーザープロフィール（既存のテーブル構造に合わせて）
            connection.execute(text("""
                INSERT IGNORE INTO user_profiles (user_id, register_type, created_at, updated_at)
                VALUES (:user_id, 'email', NOW(), NOW())
            """), user)
            
            # 認証資格情報
            connection.execute(text("""
                INSERT IGNORE INTO auth_credentials (user_id, password_hash, created_at, updated_at)
                VALUES (:user_id, :password_hash, NOW(), NOW())
            """), user)
        
        connection.commit()
        print(f"✅ {len(test_users)}名のテストユーザーを作成（プロフィール・認証情報含む）")
        
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
            ('oauth_providers_enabled', 'google,line,apple', '有効化するOAuthプロバイダー'),
            ('battle_rating_system', 'true', 'バトルレーティングシステム有効化'),
            ('daily_ranking_reset_hour', '0', '日次ランキングリセット時刻（0-23時）'),
            ('min_battles_for_ranking', '5', 'ランキング対象となる最小バトル数'),
            ('experience_gain_per_battle', '10', '1バトルあたりの経験値獲得量'),
            ('level_up_experience_base', '100', 'レベルアップに必要な基本経験値')
        ]
        
        for setting_key, setting_value, description in system_settings:
            connection.execute(text("""
                INSERT IGNORE INTO system_settings (setting_key, setting_value, description)
                VALUES (:key, :value, :desc)
            """), {"key": setting_key, "value": setting_value, "desc": description})
        
        connection.commit()
        print(f"✅ {len(system_settings)}件のシステム設定を作成")
        
        # 3. ユーザー統計初期化（既存のテーブル構造に合わせて）
        for user in test_users:
            # 基本統計
            connection.execute(text("""
                INSERT IGNORE INTO user_stats (user_id)
                VALUES (:user_id)
            """), user)
            
            # 初期ランキングデータ
            connection.execute(text("""
                INSERT IGNORE INTO daily_rankings (user_id, ranking_date)
                VALUES (:user_id, CURDATE())
            """), user)
        
        connection.commit()
        print("✅ テストユーザーの統計データを初期化（詳細統計・ランキング含む）")
        
        # 4. サンプルバトル結果（テスト用）
        sample_battles = [
            {
                'battle_id': f'battle_{secrets.token_hex(8)}',
                'player1_id': 'test_user_1',
                'player2_id': 'test_user_2',
                'winner_id': 'test_user_1',
                'total_rounds': 3,
                'battle_duration_seconds': 45,
                'created_at': '2024-01-15 10:00:00'
            },
            {
                'battle_id': f'battle_{secrets.token_hex(8)}',
                'player1_id': 'test_user_3',
                'player2_id': 'test_user_4',
                'winner_id': 'test_user_3',
                'total_rounds': 5,
                'battle_duration_seconds': 78,
                'created_at': '2024-01-15 11:00:00'
            }
        ]
        
        for battle in sample_battles:
            connection.execute(text("""
                INSERT IGNORE INTO battle_results (battle_id, player1_id, player2_id, winner_id, 
                                                 total_rounds, battle_duration_seconds, created_at)
                VALUES (:battle_id, :player1_id, :player2_id, :winner_id, 
                       :total_rounds, :battle_duration_seconds, :created_at)
            """), battle)
            
            # バトルラウンド詳細
            for round_num in range(1, battle['total_rounds'] + 1):
                connection.execute(text("""
                    INSERT IGNORE INTO battle_rounds (battle_id, round_number, player1_hand, player2_hand, 
                                                    winner_id, round_duration_seconds)
                    VALUES (:battle_id, :round_num, 'rock', 'scissors', :winner_id, 15)
                """), {
                    'battle_id': battle['battle_id'],
                    'round_num': round_num,
                    'winner_id': battle['winner_id']
                })
        
        connection.commit()
        print(f"✅ {len(sample_battles)}件のサンプルバトル結果を作成")
        
        print("🎉 ユーザーシーダー実行完了（DBありき認証・バトル対応）")
        print("📋 テスト用ログイン情報:")
        print("   メール: test1@example.com 〜 test5@example.com")
        print("   パスワード: password123")
        print("   プロフィール画像: defaultAvatar1.png 〜 defaultAvatar5.png")
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        """シーダー情報"""
        return {
            'name': 'UserSeeder',
            'description': 'DBありき認証・バトルテスト用のテストユーザー・システム設定・統計データの初期投入',
            'tables': ['users', 'user_profiles', 'auth_credentials', 'system_settings', 'user_stats', 'daily_rankings', 'battle_results', 'battle_rounds']
        }
