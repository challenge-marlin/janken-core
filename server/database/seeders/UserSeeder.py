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
        
        # UTF-8文字エンコーディングを明示的に設定
        connection.execute(text("SET NAMES utf8mb4"))
        connection.execute(text("SET CHARACTER SET utf8mb4"))
        connection.execute(text("SET character_set_connection=utf8mb4"))
        print("✅ UTF-8文字エンコーディングを設定")
        
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
                INSERT IGNORE INTO users (user_id, email, nickname, role, title, alias, profile_image_url, created_at, updated_at)
                VALUES (:user_id, :email, :nickname, :role, :title, :alias, :profile_image, NOW(), NOW())
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
        
        # 既存のテストユーザーにプロフィール画像URLを設定（既存データの更新）
        for user in test_users:
            connection.execute(text("""
                UPDATE users 
                SET profile_image_url = :profile_image 
                WHERE user_id = :user_id AND (profile_image_url IS NULL OR profile_image_url = '')
            """), user)
        
        connection.commit()
        print("✅ 既存テストユーザーのプロフィール画像URLを更新")
        
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
        
        # 3.1 ユーザー統計にサンプルデータを設定
        sample_stats = [
            {
                'user_id': 'test_user_1',
                'total_matches': 45,
                'total_wins': 32,
                'total_losses': 10,
                'total_draws': 3,
                'win_rate': 71.11,
                'current_streak': 5,
                'best_streak': 12,
                'total_rounds_played': 135,
                'rock_count': 45,
                'paper_count': 38,
                'scissors_count': 52,
                'favorite_hand': 'scissors',
                'average_battle_duration_seconds': 67,
                'title': 'じゃんけんマスター',
                'alias': '連勝の帝王',
                'user_rank': 'gold',
                'daily_wins': 3,
                'daily_ranking': 2,
                'recent_hand_results_str': 'win,win,win,win,win,loss,win,win,win,win'
            },
            {
                'user_id': 'test_user_2',
                'total_matches': 38,
                'total_wins': 25,
                'total_losses': 11,
                'total_draws': 2,
                'win_rate': 65.79,
                'current_streak': 2,
                'best_streak': 8,
                'total_rounds_played': 114,
                'rock_count': 52,
                'paper_count': 35,
                'scissors_count': 27,
                'favorite_hand': 'rock',
                'average_battle_duration_seconds': 72,
                'title': 'バトルクイーン',
                'alias': '石の女王',
                'user_rank': 'silver',
                'daily_wins': 2,
                'daily_ranking': 5,
                'recent_hand_results_str': 'win,loss,win,win,loss,win,win,loss,win,win'
            },
            {
                'user_id': 'test_user_3',
                'total_matches': 67,
                'total_wins': 48,
                'total_losses': 15,
                'total_draws': 4,
                'win_rate': 71.64,
                'current_streak': 7,
                'best_streak': 15,
                'total_rounds_played': 201,
                'rock_count': 67,
                'paper_count': 58,
                'scissors_count': 76,
                'favorite_hand': 'scissors',
                'average_battle_duration_seconds': 89,
                'title': '勝負師',
                'alias': '戦術の達人',
                'user_rank': 'diamond',
                'daily_wins': 4,
                'daily_ranking': 1,
                'recent_hand_results_str': 'win,win,win,win,win,win,win,loss,win,win'
            },
            {
                'user_id': 'test_user_4',
                'total_matches': 12,
                'total_wins': 6,
                'total_losses': 5,
                'total_draws': 1,
                'win_rate': 50.00,
                'current_streak': 1,
                'best_streak': 3,
                'total_rounds_played': 36,
                'rock_count': 12,
                'paper_count': 8,
                'scissors_count': 16,
                'favorite_hand': 'scissors',
                'average_battle_duration_seconds': 45,
                'title': '新米戦士',
                'alias': '成長中の戦士',
                'user_rank': 'bronze',
                'daily_wins': 1,
                'daily_ranking': 12,
                'recent_hand_results_str': 'win,loss,loss,win,loss,win'
            },
            {
                'user_id': 'test_user_5',
                'total_matches': 89,
                'total_wins': 67,
                'total_losses': 18,
                'total_draws': 4,
                'win_rate': 75.28,
                'current_streak': 12,
                'best_streak': 23,
                'total_rounds_played': 267,
                'rock_count': 89,
                'paper_count': 76,
                'scissors_count': 102,
                'favorite_hand': 'scissors',
                'average_battle_duration_seconds': 95,
                'title': '伝説のプレイヤー',
                'alias': '無敗の伝説',
                'user_rank': 'diamond',
                'daily_wins': 5,
                'daily_ranking': 1,
                'recent_hand_results_str': 'win,win,win,win,win,win,win,win,win,win,win,win'
            }
        ]
        
        for stats in sample_stats:
            connection.execute(text("""
                UPDATE user_stats SET
                    total_matches = :total_matches,
                    total_wins = :total_wins,
                    total_losses = :total_losses,
                    total_draws = :total_draws,
                    win_rate = :win_rate,
                    current_streak = :current_streak,
                    best_streak = :best_streak,
                    total_rounds_played = :total_rounds_played,
                    rock_count = :rock_count,
                    paper_count = :paper_count,
                    scissors_count = :scissors_count,
                    favorite_hand = :favorite_hand,
                    average_battle_duration_seconds = :average_battle_duration_seconds,
                    title = :title,
                    alias = :alias,
                    user_rank = :user_rank,
                    daily_wins = :daily_wins,
                    daily_ranking = :daily_ranking,
                    recent_hand_results_str = :recent_hand_results_str,
                    updated_at = NOW()
                WHERE user_id = :user_id
            """), stats)
        
        connection.commit()
        print("✅ テストユーザーの詳細統計データを設定（戦績・ランキング・手の統計等）")
        
        # 3.2 日次ランキングにサンプルデータを設定
        daily_rankings_data = [
            ('test_user_3', 1, 4, 89.5),
            ('test_user_5', 2, 5, 87.2),
            ('test_user_1', 3, 3, 85.8),
            ('test_user_2', 4, 2, 82.1),
            ('test_user_4', 5, 1, 78.3)
        ]
        
        for user_id, rank, daily_wins, rating in daily_rankings_data:
            connection.execute(text("""
                UPDATE daily_rankings SET
                    ranking_position = :rank,
                    daily_wins = :daily_wins,
                    daily_win_rate = :rating,
                    updated_at = NOW()
                WHERE user_id = :user_id AND ranking_date = CURDATE()
            """), {"user_id": user_id, "rank": rank, "daily_wins": daily_wins, "rating": rating})
        
        connection.commit()
        print("✅ 日次ランキングデータを設定")
        
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
        
        # 4.1 より現実的なサンプルバトル結果を追加
        realistic_battles = [
            # test_user_3 vs test_user_5 (伝説の対決)
            {
                'battle_id': f'battle_{secrets.token_hex(8)}',
                'player1_id': 'test_user_3',
                'player2_id': 'test_user_5',
                'winner_id': 'test_user_5',
                'total_rounds': 7,
                'battle_duration_seconds': 156,
                'created_at': '2024-01-15 14:30:00'
            },
            # test_user_1 vs test_user_3 (中堅対決)
            {
                'battle_id': f'battle_{secrets.token_hex(8)}',
                'player1_id': 'test_user_1',
                'player2_id': 'test_user_3',
                'winner_id': 'test_user_3',
                'total_rounds': 6,
                'battle_duration_seconds': 134,
                'created_at': '2024-01-15 16:15:00'
            },
            # test_user_2 vs test_user_4 (新米vs中堅)
            {
                'battle_id': f'battle_{secrets.token_hex(8)}',
                'player1_id': 'test_user_2',
                'player2_id': 'test_user_4',
                'winner_id': 'test_user_2',
                'total_rounds': 4,
                'battle_duration_seconds': 89,
                'created_at': '2024-01-15 18:45:00'
            },
            # test_user_5 vs test_user_1 (伝説vsマスター)
            {
                'battle_id': f'battle_{secrets.token_hex(8)}',
                'player1_id': 'test_user_5',
                'player2_id': 'test_user_1',
                'winner_id': 'test_user_5',
                'total_rounds': 8,
                'battle_duration_seconds': 178,
                'created_at': '2024-01-15 20:20:00'
            }
        ]
        
        for battle in realistic_battles:
            connection.execute(text("""
                INSERT IGNORE INTO battle_results (battle_id, player1_id, player2_id, winner_id, 
                                                 total_rounds, battle_duration_seconds, created_at)
                VALUES (:battle_id, :player1_id, :player2_id, :winner_id, 
                       :total_rounds, :battle_duration_seconds, :created_at)
            """), battle)
            
            # より現実的なバトルラウンド詳細
            hands = ['rock', 'paper', 'scissors']
            for round_num in range(1, battle['total_rounds'] + 1):
                import random
                player1_hand = random.choice(hands)
                player2_hand = random.choice(hands)
                
                # 勝者を決定（じゃんけんのルールに従って）
                if player1_hand == player2_hand:
                    winner_id = None  # 引き分け
                elif (
                    (player1_hand == 'rock' and player2_hand == 'scissors') or
                    (player1_hand == 'paper' and player2_hand == 'rock') or
                    (player1_hand == 'scissors' and player2_hand == 'paper')
                ):
                    winner_id = battle['player1_id']
                else:
                    winner_id = battle['player2_id']
                
                round_duration = random.randint(12, 25)
                
                connection.execute(text("""
                    INSERT IGNORE INTO battle_rounds (battle_id, round_number, player1_hand, player2_hand, 
                                                    winner_id, round_duration_seconds)
                    VALUES (:battle_id, :round_num, :player1_hand, :player2_hand, :winner_id, :round_duration)
                """), {
                    'battle_id': battle['battle_id'],
                    'round_num': round_num,
                    'player1_hand': player1_hand,
                    'player2_hand': player2_hand,
                    'winner_id': winner_id,
                    'round_duration': round_duration
                })
        
        connection.commit()
        print(f"✅ {len(realistic_battles)}件の現実的なサンプルバトル結果を追加")
        
        # 4.2 過去のバトル履歴（より多くのデータ）
        past_battles = [
            # 1週間前のバトル
            ('test_user_1', 'test_user_4', 'test_user_1', 3, 67, '2024-01-08 15:30:00'),
            ('test_user_2', 'test_user_3', 'test_user_3', 5, 112, '2024-01-09 10:15:00'),
            ('test_user_5', 'test_user_2', 'test_user_5', 4, 89, '2024-01-10 14:45:00'),
            ('test_user_4', 'test_user_1', 'test_user_1', 3, 56, '2024-01-11 16:20:00'),
            ('test_user_3', 'test_user_5', 'test_user_5', 6, 134, '2024-01-12 11:30:00'),
            # 2週間前のバトル
            ('test_user_1', 'test_user_5', 'test_user_5', 7, 156, '2024-01-01 13:15:00'),
            ('test_user_2', 'test_user_4', 'test_user_2', 4, 78, '2024-01-02 17:45:00'),
            ('test_user_3', 'test_user_1', 'test_user_3', 5, 98, '2024-01-03 09:30:00'),
            ('test_user_4', 'test_user_3', 'test_user_3', 4, 87, '2024-01-04 20:15:00'),
            ('test_user_5', 'test_user_1', 'test_user_5', 6, 123, '2024-01-05 12:00:00')
        ]
        
        for player1_id, player2_id, winner_id, total_rounds, duration, created_at in past_battles:
            battle_id = f'battle_{secrets.token_hex(8)}'
            connection.execute(text("""
                INSERT IGNORE INTO battle_results (battle_id, player1_id, player2_id, winner_id, 
                                                 total_rounds, battle_duration_seconds, created_at)
                VALUES (:battle_id, :player1_id, :player2_id, :winner_id, 
                       :total_rounds, :battle_duration_seconds, :created_at)
            """), {
                'battle_id': battle_id,
                'player1_id': player1_id,
                'player2_id': player2_id,
                'winner_id': winner_id,
                'total_rounds': total_rounds,
                'battle_duration_seconds': duration,
                'created_at': created_at
            })
            
            # 過去のバトルラウンド詳細（簡略化）
            for round_num in range(1, total_rounds + 1):
                connection.execute(text("""
                    INSERT IGNORE INTO battle_rounds (battle_id, round_number, player1_hand, player2_hand, 
                                                    winner_id, round_duration_seconds)
                    VALUES (:battle_id, :round_num, 'rock', 'scissors', :winner_id, 15)
                """), {
                    'battle_id': battle_id,
                    'round_num': round_num,
                    'winner_id': winner_id
                })
        
        connection.commit()
        print(f"✅ {len(past_battles)}件の過去のバトル履歴を追加")
        
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
            'tables': ['users', 'user_profiles', 'auth_credentials', 'system_settings', 'user_stats', 'daily_rankings', 'battle_results', 'battle_rounds'],
            'sample_data': {
                'users': '5名のテストユーザー（各段階のスキルレベル）',
                'user_stats': '現実的な戦績・統計データ（勝率、連勝記録、手の統計等）',
                'daily_rankings': '日次ランキングデータ（1-5位）',
                'battle_results': '16件のサンプルバトル（現在・過去・現実的な対戦結果）',
                'battle_rounds': '詳細なラウンド情報（じゃんけんの手、勝者、時間等）',
                'system_settings': 'ゲーム・セキュリティ・認証設定'
            }
        }
