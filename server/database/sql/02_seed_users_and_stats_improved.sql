-- ========================================================
-- じゃんけんバトル シードデータ（改善版）
-- WebSocketバトル対応 - テストユーザーとリアルなデータ生成
-- ========================================================

USE janken_db;

-- ============================================
-- テストユーザーデータ投入
-- 開発用ログインとリアルな統計データを含む
-- ============================================

-- usersテーブル（簡素化版）
INSERT INTO users (user_id, email, password, nickname, profile_image_url, student_id_image_url, register_type, created_at) VALUES
-- 開発用テストユーザー（1-5）
('test-user-1', 'test1@example.com', 'hashed_password_1', 'テストユーザー1', '/storage/proxy/profile-images/avatar1.png', '/storage/proxy/student-ids/student1.png', 'dev', '2024-01-15 10:00:00'),
('test-user-2', 'test2@example.com', 'hashed_password_2', 'テストユーザー2', '/storage/proxy/profile-images/avatar2.png', '/storage/proxy/student-ids/student2.png', 'dev', '2024-01-15 10:01:00'),
('test-user-3', 'test3@example.com', 'hashed_password_3', 'テストユーザー3', '/storage/proxy/profile-images/avatar3.png', '/storage/proxy/student-ids/student3.png', 'dev', '2024-01-15 10:02:00'),
('test-user-4', 'test4@example.com', 'hashed_password_4', 'テストユーザー4', '/storage/proxy/profile-images/avatar4.png', '/storage/proxy/student-ids/student4.png', 'dev', '2024-01-15 10:03:00'),
('test-user-5', 'test5@example.com', 'hashed_password_5', 'テストユーザー5', '/storage/proxy/profile-images/avatar5.png', '/storage/proxy/student-ids/student5.png', 'dev', '2024-01-15 10:04:00'),

-- 追加のテストユーザー（より多様な統計用）
('user-6-rookie', 'rookie@example.com', 'hashed_password_6', 'ルーキー太郎', '/storage/proxy/profile-images/avatar6.png', '/storage/proxy/student-ids/student6.png', 'email', '2024-01-20 14:30:00'),
('user-7-veteran', 'veteran@example.com', 'hashed_password_7', 'ベテラン花子', '/storage/proxy/profile-images/avatar7.png', '/storage/proxy/student-ids/student7.png', 'email', '2024-01-10 09:15:00'),
('user-8-champion', 'champion@example.com', 'hashed_password_8', 'チャンピオン', '/storage/proxy/profile-images/avatar8.png', '/storage/proxy/student-ids/student8.png', 'email', '2024-01-05 11:45:00'),
('user-9-strategist', 'strategist@example.com', 'hashed_password_9', '戦略家みどり', '/storage/proxy/profile-images/avatar9.png', '/storage/proxy/student-ids/student9.png', 'email', '2024-01-25 16:20:00'),
('user-10-lucky', 'lucky@example.com', 'hashed_password_10', 'ラッキー', '/storage/proxy/profile-images/avatar10.png', '/storage/proxy/student-ids/student10.png', 'email', '2024-02-01 13:10:00'),

-- バランス調整用ユーザー
('user-11-balanced', 'balanced@example.com', 'hashed_password_11', 'バランサー', '/storage/proxy/profile-images/avatar11.png', '/storage/proxy/student-ids/student11.png', 'email', '2024-01-28 08:30:00'),
('user-12-drawking', 'drawking@example.com', 'hashed_password_12', '引き分けキング', '/storage/proxy/profile-images/avatar12.png', '/storage/proxy/student-ids/student12.png', 'email', '2024-01-18 19:45:00'),
('user-13-rockmaster', 'rockmaster@example.com', 'hashed_password_13', 'グーマスター', '/storage/proxy/profile-images/avatar13.png', '/storage/proxy/student-ids/student13.png', 'email', '2024-01-22 12:00:00'),
('user-14-scissorqueen', 'scissorqueen@example.com', 'hashed_password_14', 'チョキクイーン', '/storage/proxy/profile-images/avatar14.png', '/storage/proxy/student-ids/student14.png', 'email', '2024-01-19 15:30:00'),
('user-15-paperace', 'paperace@example.com', 'hashed_password_15', 'パーエース', '/storage/proxy/profile-images/avatar15.png', '/storage/proxy/student-ids/student15.png', 'email', '2024-01-26 10:15:00'),



-- ============================================
-- user_stats（戦績データ）
-- リアルな戦績分布を作成
-- ============================================

INSERT INTO user_stats (
    user_id, total_wins, current_win_streak, max_win_streak,
    hand_stats_rock, hand_stats_scissors, hand_stats_paper, favorite_hand,
    daily_wins, daily_losses, daily_draws, title, last_reset_at
) VALUES
-- テストユーザー1（バランス型）
('test-user-1', 45, 3, 8, 35, 32, 33, 'rock', 5, 2, 1, 'バランサー', CURRENT_DATE),

-- テストユーザー2（攻撃型）
('test-user-2', 67, 5, 12, 28, 45, 37, 'scissors', 7, 1, 0, '攻撃者', CURRENT_DATE),

-- テストユーザー3（守備型）
('test-user-3', 38, 1, 6, 52, 31, 32, 'rock', 4, 3, 3, '守備者', CURRENT_DATE),

-- テストユーザー4（新参者）
('test-user-4', 15, 0, 4, 15, 12, 13, 'paper', 2, 2, 1, '新参者', CURRENT_DATE),

-- テストユーザー5（中級者）
('test-user-5', 52, 2, 9, 42, 38, 40, 'rock', 6, 2, 2, '中級者', CURRENT_DATE);

-- ============================================
-- daily_ranking（本日のランキング）
-- user_statsのデータに基づいて生成
-- ============================================

INSERT INTO daily_ranking (
    ranking_date, ranking_position, user_id, daily_wins, daily_matches, 
    daily_win_rate, rating_points, rank_change
)
SELECT 
    CURRENT_DATE,
    ROW_NUMBER() OVER (ORDER BY daily_wins DESC, daily_matches ASC, rank_points DESC),
    user_id,
    daily_wins,
    daily_matches,
    CASE 
        WHEN daily_matches > 0 THEN (daily_wins * 100.0 / daily_matches)
        ELSE 0.00
    END as daily_win_rate,
    rank_points,
    0 as rank_change  -- 初回なので変動なし
FROM user_stats
WHERE is_active = TRUE AND daily_matches > 0
ORDER BY daily_wins DESC, daily_matches ASC, rank_points DESC;

-- ============================================
-- 過去数日のランキングデータ（履歴用）
-- ============================================

-- 昨日のランキング
INSERT INTO daily_ranking (ranking_date, ranking_position, user_id, daily_wins, daily_matches, daily_win_rate, rating_points, rank_change)
SELECT 
    DATE_SUB(CURRENT_DATE, INTERVAL 1 DAY),
    ROW_NUMBER() OVER (ORDER BY (daily_wins - FLOOR(RAND() * 3)) DESC, rank_points DESC),
    user_id,
    GREATEST(0, daily_wins - FLOOR(RAND() * 3)),
    GREATEST(1, daily_matches - FLOOR(RAND() * 2)),
    CASE 
        WHEN (daily_matches - FLOOR(RAND() * 2)) > 0 
        THEN ((daily_wins - FLOOR(RAND() * 3)) * 100.0 / (daily_matches - FLOOR(RAND() * 2)))
        ELSE 0.00
    END,
    rank_points - FLOOR(RAND() * 100) + FLOOR(RAND() * 50),
    FLOOR(RAND() * 5) - 2  -- -2から+2の変動
FROM user_stats
WHERE is_active = TRUE
ORDER BY (daily_wins - FLOOR(RAND() * 3)) DESC;

-- 一昨日のランキング
INSERT INTO daily_ranking (ranking_date, ranking_position, user_id, daily_wins, daily_matches, daily_win_rate, rating_points, rank_change)
SELECT 
    DATE_SUB(CURRENT_DATE, INTERVAL 2 DAY),
    ROW_NUMBER() OVER (ORDER BY (daily_wins - FLOOR(RAND() * 4)) DESC, rank_points DESC),
    user_id,
    GREATEST(0, daily_wins - FLOOR(RAND() * 4)),
    GREATEST(1, daily_matches - FLOOR(RAND() * 3)),
    CASE 
        WHEN (daily_matches - FLOOR(RAND() * 3)) > 0 
        THEN ((daily_wins - FLOOR(RAND() * 4)) * 100.0 / (daily_matches - FLOOR(RAND() * 3)))
        ELSE 0.00
    END,
    rank_points - FLOOR(RAND() * 150) + FLOOR(RAND() * 75),
    FLOOR(RAND() * 6) - 3  -- -3から+3の変動
FROM user_stats
WHERE is_active = TRUE
ORDER BY (daily_wins - FLOOR(RAND() * 4)) DESC;

-- ============================================
-- sample_match_history（サンプル対戦履歴）
-- リアルな対戦データを生成
-- ============================================

-- 最近の対戦履歴（過去1週間分）
INSERT INTO match_history (
    battle_id, player1_id, player2_id, player1_nickname, player2_nickname,
    player1_hand, player2_hand, player1_result, player2_result, winner,
    total_rounds, draw_count, match_type, battle_duration_seconds,
    player1_rating_before, player1_rating_after, player1_rating_change,
    player2_rating_before, player2_rating_after, player2_rating_change,
    created_at, finished_at
) VALUES
-- Test User 1 vs Test User 2
('battle-001', 'test-user-1', 'test-user-2', 'テストユーザー1', 'テストユーザー2',
 'rock', 'scissors', 'win', 'lose', 1, 1, 0, 'random', 45,
 1430, 1450, 20, 1700, 1680, -20, '2024-02-15 18:30:00', '2024-02-15 18:31:15'),

-- Champion vs Veteran
('battle-002', 'user-8-champion', 'user-7-veteran', 'チャンピオン', 'ベテラン花子',
 'scissors', 'paper', 'win', 'lose', 1, 1, 0, 'random', 38,
 2080, 2100, 20, 1870, 1850, -20, '2024-02-15 21:45:00', '2024-02-15 21:46:23'),

-- Rock Master vs Scissor Queen
('battle-003', 'user-13-rockmaster', 'user-14-scissorqueen', 'グーマスター', 'チョキクイーン',
 'rock', 'scissors', 'win', 'lose', 1, 1, 0, 'random', 52,
 1400, 1420, 20, 1500, 1480, -20, '2024-02-15 16:15:00', '2024-02-15 16:17:07'),

-- 引き分け多めの試合
('battle-004', 'user-11-balanced', 'user-12-drawking', 'バランサー', '引き分けキング',
 'rock', 'rock', 'draw', 'draw', 3, 3, 2, 'random', 156,
 1230, 1250, 20, 1160, 1180, 20, '2024-02-15 17:00:00', '2024-02-15 17:02:36'),

-- 新規ユーザー同士
('battle-005', 'user-16-newbie', 'user-17-fresh', 'ニューカマー', 'フレッシュ',
 'paper', 'rock', 'win', 'lose', 1, 1, 0, 'random', 67,
 960, 980, 20, 1040, 1020, -20, '2024-02-15 13:30:00', '2024-02-15 13:31:37'),

-- テストユーザー3 vs 戦略家
('battle-006', 'test-user-3', 'user-9-strategist', 'テストユーザー3', '戦略家みどり',
 'rock', 'rock', 'draw', 'draw', 3, 1, 0, 'random', 42,
 1260, 1280, 20, 1300, 1320, 20, '2024-02-15 17:30:00', '2024-02-15 17:31:12'),

-- ラッキー vs Paper Ace
('battle-007', 'user-10-lucky', 'user-15-paperace', 'ラッキー', 'パーエース',
 'scissors', 'paper', 'win', 'lose', 1, 1, 0, 'random', 33,
 1180, 1200, 20, 1380, 1360, -20, '2024-02-15 15:00:00', '2024-02-15 15:01:33'),

-- Test User 4 vs Test User 5
('battle-008', 'test-user-4', 'test-user-5', 'テストユーザー4', 'テストユーザー5',
 'paper', 'scissors', 'lose', 'win', 2, 1, 0, 'random', 28,
 1170, 1150, -20, 1360, 1380, 20, '2024-02-15 16:00:00', '2024-02-15 16:01:28'),

-- Rookie vs Beginner
('battle-009', 'user-6-rookie', 'user-18-beginner', 'ルーキー太郎', 'ビギナー',
 'rock', 'scissors', 'win', 'lose', 1, 1, 0, 'random', 71,
 930, 950, 20, 960, 940, -20, '2024-02-15 14:15:00', '2024-02-15 14:16:41'),

-- Champion vs Test User 1 (チャンピオンの圧勝)
('battle-010', 'user-8-champion', 'test-user-1', 'チャンピオン', 'テストユーザー1',
 'paper', 'rock', 'win', 'lose', 1, 1, 0, 'random', 31,
 2060, 2080, 20, 1450, 1430, -20, '2024-02-15 22:00:00', '2024-02-15 22:01:31');

-- ============================================
-- sessions（アクティブセッション）
-- テストユーザー用の認証セッション
-- ============================================

INSERT INTO sessions (
    session_id, user_id, access_token_hash, refresh_token_hash, 
    device_info, expires_at, ip_address, is_active, created_at
) VALUES
('session-test-1', 'test-user-1', 
 SHA2('test-token-1', 256), SHA2('refresh-token-1', 256),
 '{"type": "test", "browser": "Chrome", "os": "Windows"}',
 DATE_ADD(NOW(), INTERVAL 7 DAY), '127.0.0.1', TRUE, NOW()),

('session-test-2', 'test-user-2',
 SHA2('test-token-2', 256), SHA2('refresh-token-2', 256),
 '{"type": "test", "browser": "Firefox", "os": "Mac"}',
 DATE_ADD(NOW(), INTERVAL 7 DAY), '127.0.0.1', TRUE, NOW()),

('session-test-3', 'test-user-3',
 SHA2('test-token-3', 256), SHA2('refresh-token-3', 256),
 '{"type": "test", "browser": "Safari", "os": "iOS"}',
 DATE_ADD(NOW(), INTERVAL 7 DAY), '127.0.0.1', TRUE, NOW()),

('session-test-4', 'test-user-4',
 SHA2('test-token-4', 256), SHA2('refresh-token-4', 256),
 '{"type": "test", "browser": "Chrome", "os": "Android"}',
 DATE_ADD(NOW(), INTERVAL 7 DAY), '127.0.0.1', TRUE, NOW()),

('session-test-5', 'test-user-5',
 SHA2('test-token-5', 256), SHA2('refresh-token-5', 256),
 '{"type": "test", "browser": "Edge", "os": "Windows"}',
 DATE_ADD(NOW(), INTERVAL 7 DAY), '127.0.0.1', TRUE, NOW());

-- ============================================
-- データ整合性確認
-- ============================================

-- 統計確認用クエリ
SELECT 
    '=== USER STATS SUMMARY ===' as info,
    COUNT(*) as total_users,
    AVG(win_rate) as avg_win_rate,
    MIN(rank_points) as min_rating,
    MAX(rank_points) as max_rating,
    SUM(total_matches) as total_all_matches
FROM user_stats;

SELECT 
    '=== RANKING SUMMARY ===' as info,
    ranking_date,
    COUNT(*) as ranked_users,
    MAX(daily_wins) as max_daily_wins,
    AVG(daily_win_rate) as avg_daily_win_rate
FROM daily_ranking 
GROUP BY ranking_date 
ORDER BY ranking_date DESC;

SELECT 
    '=== MATCH HISTORY SUMMARY ===' as info,
    COUNT(*) as total_battles,
    COUNT(CASE WHEN winner = 1 THEN 1 END) as player1_wins,
    COUNT(CASE WHEN winner = 2 THEN 1 END) as player2_wins,
    COUNT(CASE WHEN winner = 3 THEN 1 END) as draws
FROM match_history;