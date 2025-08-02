-- ========================================================
-- じゃんけんバトル特化型データベース設計（改善版）
-- 2024年バージョン - WebSocketバトル対応
-- ========================================================

-- データベース作成
CREATE DATABASE IF NOT EXISTS janken_db;
USE janken_db;

-- ============================================
-- users（ユーザー情報）- 簡素化版
-- じゃんけんゲームに必要な情報のみに絞り込み
-- ============================================
CREATE TABLE IF NOT EXISTS users (
    user_id VARCHAR(36) PRIMARY KEY,           -- UUID形式のユーザーID
    email VARCHAR(255) UNIQUE,                 -- メールアドレス（認証用）
    nickname VARCHAR(50) NOT NULL,             -- 表示名（バトルで使用）
    profile_image_url VARCHAR(255),            -- プロフィール画像URL
    is_banned TINYINT DEFAULT 0,               -- BANフラグ
    register_type VARCHAR(20) DEFAULT 'email', -- 登録方法
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_email (email),
    INDEX idx_user_banned (is_banned)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- user_stats（ユーザー戦績）- 強化版
-- バトル統計とランキング用データ
-- ============================================
CREATE TABLE IF NOT EXISTS user_stats (
    user_id VARCHAR(36) PRIMARY KEY,
    -- 基本戦績
    total_wins INT DEFAULT 0,
    total_losses INT DEFAULT 0,
    total_draws INT DEFAULT 0,
    total_matches INT DEFAULT 0,
    win_rate DECIMAL(5,2) DEFAULT 0.00,        -- 勝率（自動計算）
    
    -- 連勝記録
    current_win_streak INT DEFAULT 0,
    max_win_streak INT DEFAULT 0,
    current_lose_streak INT DEFAULT 0,
    max_lose_streak INT DEFAULT 0,
    
    -- 手の使用統計
    hand_stats_rock INT DEFAULT 0,
    hand_stats_scissors INT DEFAULT 0,
    hand_stats_paper INT DEFAULT 0,
    favorite_hand VARCHAR(10) DEFAULT 'rock',   -- 最も使用する手
    
    -- デイリー統計（毎日リセット）
    daily_wins INT DEFAULT 0,
    daily_losses INT DEFAULT 0,
    daily_draws INT DEFAULT 0,
    daily_matches INT DEFAULT 0,
    last_daily_reset DATE NOT NULL DEFAULT (CURRENT_DATE),
    
    -- ランキング関連
    user_rank VARCHAR(20) DEFAULT 'bronze',     -- bronze, silver, gold, platinum, diamond
    rank_points INT DEFAULT 1000,               -- レーティングポイント
    highest_rank VARCHAR(20) DEFAULT 'bronze',
    highest_rank_points INT DEFAULT 1000,
    
    -- 活動状況
    last_battle_at DATETIME,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_stats_rank_points (rank_points DESC),
    INDEX idx_user_stats_daily_wins (daily_wins DESC),
    INDEX idx_user_stats_total_wins (total_wins DESC),
    INDEX idx_user_stats_win_rate (win_rate DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- battle_sessions（バトルセッション管理）- 新規追加
-- 現在進行中のWebSocketバトルの状態管理
-- ============================================
CREATE TABLE IF NOT EXISTS battle_sessions (
    battle_id VARCHAR(36) PRIMARY KEY,
    status ENUM('waiting', 'matched', 'preparing', 'ready', 'playing', 'judging', 'finished', 'cancelled') NOT NULL DEFAULT 'waiting',
    
    -- プレイヤー情報
    player1_id VARCHAR(36),
    player2_id VARCHAR(36),
    player1_ready BOOLEAN DEFAULT FALSE,
    player2_ready BOOLEAN DEFAULT FALSE,
    
    -- ゲーム状態
    player1_hand ENUM('rock', 'scissors', 'paper'),
    player2_hand ENUM('rock', 'scissors', 'paper'),
    current_round INT DEFAULT 1,
    draw_count INT DEFAULT 0,
    
    -- タイムスタンプ
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    started_at DATETIME,
    finished_at DATETIME,
    expires_at DATETIME NOT NULL,               -- セッション有効期限
    
    FOREIGN KEY (player1_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (player2_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_battle_sessions_status (status),
    INDEX idx_battle_sessions_expires (expires_at),
    INDEX idx_battle_sessions_player1 (player1_id),
    INDEX idx_battle_sessions_player2 (player2_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- websocket_connections（WebSocket接続管理）- 新規追加
-- アクティブなWebSocket接続の追跡
-- ============================================
CREATE TABLE IF NOT EXISTS websocket_connections (
    connection_id VARCHAR(128) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    session_id VARCHAR(128),                   -- セッション管理との連携
    battle_id VARCHAR(36),                     -- 現在参加中のバトル
    status ENUM('connected', 'in_queue', 'in_battle', 'disconnected') DEFAULT 'connected',
    
    -- 接続情報
    ip_address VARCHAR(45),
    user_agent VARCHAR(255),
    connected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_activity DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (battle_id) REFERENCES battle_sessions(battle_id) ON DELETE SET NULL,
    INDEX idx_ws_connections_user_id (user_id),
    INDEX idx_ws_connections_status (status),
    INDEX idx_ws_connections_battle_id (battle_id),
    INDEX idx_ws_connections_activity (last_activity)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- match_history（対戦履歴）- 改良版
-- 完了したバトルの記録
-- ============================================
CREATE TABLE IF NOT EXISTS match_history (
    match_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    battle_id VARCHAR(36) UNIQUE,              -- battle_sessionsとの連携
    
    -- プレイヤー情報
    player1_id VARCHAR(36) NOT NULL,
    player2_id VARCHAR(36) NOT NULL,
    player1_nickname VARCHAR(50),
    player2_nickname VARCHAR(50),
    
    -- ゲーム結果
    player1_hand ENUM('rock','paper','scissors') NOT NULL,
    player2_hand ENUM('rock','paper','scissors') NOT NULL,
    player1_result ENUM('win','lose','draw') NOT NULL,
    player2_result ENUM('win','lose','draw') NOT NULL,
    winner TINYINT UNSIGNED NOT NULL DEFAULT 0, -- 1=player1, 2=player2, 3=draw
    
    -- ゲーム詳細
    total_rounds INT DEFAULT 1,
    draw_count INT NOT NULL DEFAULT 0,
    match_type ENUM('random','friend','tournament') NOT NULL DEFAULT 'random',
    battle_duration_seconds INT,               -- バトル継続時間
    
    -- レーティング変動
    player1_rating_before INT,
    player1_rating_after INT,
    player1_rating_change INT DEFAULT 0,
    player2_rating_before INT,
    player2_rating_after INT,
    player2_rating_change INT DEFAULT 0,
    
    -- タイムスタンプ
    created_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    finished_at DATETIME(3),
    
    FOREIGN KEY (player1_id) REFERENCES users(user_id),
    FOREIGN KEY (player2_id) REFERENCES users(user_id),
    FOREIGN KEY (battle_id) REFERENCES battle_sessions(battle_id),
    INDEX idx_match_history_p1 (player1_id),
    INDEX idx_match_history_p2 (player2_id),
    INDEX idx_match_history_created (created_at),
    INDEX idx_match_history_winner (winner),
    INDEX idx_match_history_type (match_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- daily_ranking（デイリーランキング）- 改良版
-- 自動更新対応の日次ランキング
-- ============================================
CREATE TABLE IF NOT EXISTS daily_ranking (
    ranking_date DATE NOT NULL,
    ranking_position INT NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    daily_wins INT NOT NULL DEFAULT 0,
    daily_matches INT NOT NULL DEFAULT 0,
    daily_win_rate DECIMAL(5,2) DEFAULT 0.00,
    rating_points INT NOT NULL DEFAULT 1000,
    rank_change INT DEFAULT 0,                 -- 前日からの順位変動
    
    PRIMARY KEY (ranking_date, ranking_position),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    INDEX idx_daily_ranking_user (user_id),
    INDEX idx_daily_ranking_date_wins (ranking_date, daily_wins DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- 認証関連テーブル（簡素化・WebSocket対応）
-- ============================================

-- magic_links（Magic Link認証）
CREATE TABLE IF NOT EXISTS magic_links (
    token_id VARCHAR(128) PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    token_hash VARCHAR(512) NOT NULL,
    user_id VARCHAR(36),
    expires_at DATETIME NOT NULL,
    used_at DATETIME NULL,
    ip_address VARCHAR(45) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL,
    INDEX idx_magic_links_email (email),
    INDEX idx_magic_links_expires (expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- sessions（セッション管理）- WebSocket連携強化
CREATE TABLE IF NOT EXISTS sessions (
    session_id VARCHAR(128) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    access_token_hash VARCHAR(512) NOT NULL,   -- ハッシュ化して保存
    refresh_token_hash VARCHAR(512),
    device_info JSON,                          -- デバイス識別情報
    expires_at DATETIME NOT NULL,
    last_activity DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    ip_address VARCHAR(45) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    websocket_connection_id VARCHAR(128),      -- WebSocket接続との紐付け
    
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_sessions_user_id (user_id),
    INDEX idx_sessions_expires (expires_at),
    INDEX idx_sessions_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- rate_limits（レート制限）
CREATE TABLE IF NOT EXISTS rate_limits (
    limit_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    ip_address VARCHAR(45) NOT NULL,
    endpoint VARCHAR(100) NOT NULL,
    request_count INT NOT NULL DEFAULT 1,
    window_start DATETIME NOT NULL,
    window_end DATETIME NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE KEY unique_ip_endpoint_window (ip_address, endpoint, window_start),
    INDEX idx_rate_limits_ip (ip_address),
    INDEX idx_rate_limits_window (window_end)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- security_events（セキュリティイベント）
CREATE TABLE IF NOT EXISTS security_events (
    event_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(36),
    event_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    ip_address VARCHAR(45) NOT NULL,
    details JSON,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL,
    INDEX idx_security_events_user_id (user_id),
    INDEX idx_security_events_type (event_type),
    INDEX idx_security_events_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- トリガーとプロシージャ（統計自動更新）
-- ============================================

-- user_stats自動更新トリガー
DELIMITER $$

CREATE TRIGGER update_user_stats_after_match
AFTER INSERT ON match_history
FOR EACH ROW
BEGIN
    -- Player1の統計更新
    UPDATE user_stats SET
        total_matches = total_matches + 1,
        total_wins = total_wins + CASE WHEN NEW.player1_result = 'win' THEN 1 ELSE 0 END,
        total_losses = total_losses + CASE WHEN NEW.player1_result = 'lose' THEN 1 ELSE 0 END,
        total_draws = total_draws + CASE WHEN NEW.player1_result = 'draw' THEN 1 ELSE 0 END,
        daily_matches = daily_matches + 1,
        daily_wins = daily_wins + CASE WHEN NEW.player1_result = 'win' THEN 1 ELSE 0 END,
        daily_losses = daily_losses + CASE WHEN NEW.player1_result = 'lose' THEN 1 ELSE 0 END,
        daily_draws = daily_draws + CASE WHEN NEW.player1_result = 'draw' THEN 1 ELSE 0 END,
        hand_stats_rock = hand_stats_rock + CASE WHEN NEW.player1_hand = 'rock' THEN 1 ELSE 0 END,
        hand_stats_scissors = hand_stats_scissors + CASE WHEN NEW.player1_hand = 'scissors' THEN 1 ELSE 0 END,
        hand_stats_paper = hand_stats_paper + CASE WHEN NEW.player1_hand = 'paper' THEN 1 ELSE 0 END,
        current_win_streak = CASE 
            WHEN NEW.player1_result = 'win' THEN current_win_streak + 1
            ELSE 0
        END,
        max_win_streak = GREATEST(max_win_streak, 
            CASE WHEN NEW.player1_result = 'win' THEN current_win_streak + 1 ELSE current_win_streak END),
        win_rate = CASE 
            WHEN (total_wins + CASE WHEN NEW.player1_result = 'win' THEN 1 ELSE 0 END + 
                  total_losses + CASE WHEN NEW.player1_result = 'lose' THEN 1 ELSE 0 END) > 0
            THEN ((total_wins + CASE WHEN NEW.player1_result = 'win' THEN 1 ELSE 0 END) * 100.0) / 
                 (total_wins + CASE WHEN NEW.player1_result = 'win' THEN 1 ELSE 0 END + 
                  total_losses + CASE WHEN NEW.player1_result = 'lose' THEN 1 ELSE 0 END)
            ELSE 0.00
        END,
        last_battle_at = NEW.finished_at,
        updated_at = CURRENT_TIMESTAMP
    WHERE user_id = NEW.player1_id;
    
    -- Player2の統計更新
    UPDATE user_stats SET
        total_matches = total_matches + 1,
        total_wins = total_wins + CASE WHEN NEW.player2_result = 'win' THEN 1 ELSE 0 END,
        total_losses = total_losses + CASE WHEN NEW.player2_result = 'lose' THEN 1 ELSE 0 END,
        total_draws = total_draws + CASE WHEN NEW.player2_result = 'draw' THEN 1 ELSE 0 END,
        daily_matches = daily_matches + 1,
        daily_wins = daily_wins + CASE WHEN NEW.player2_result = 'win' THEN 1 ELSE 0 END,
        daily_losses = daily_losses + CASE WHEN NEW.player2_result = 'lose' THEN 1 ELSE 0 END,
        daily_draws = daily_draws + CASE WHEN NEW.player2_result = 'draw' THEN 1 ELSE 0 END,
        hand_stats_rock = hand_stats_rock + CASE WHEN NEW.player2_hand = 'rock' THEN 1 ELSE 0 END,
        hand_stats_scissors = hand_stats_scissors + CASE WHEN NEW.player2_hand = 'scissors' THEN 1 ELSE 0 END,
        hand_stats_paper = hand_stats_paper + CASE WHEN NEW.player2_hand = 'paper' THEN 1 ELSE 0 END,
        current_win_streak = CASE 
            WHEN NEW.player2_result = 'win' THEN current_win_streak + 1
            ELSE 0
        END,
        max_win_streak = GREATEST(max_win_streak, 
            CASE WHEN NEW.player2_result = 'win' THEN current_win_streak + 1 ELSE current_win_streak END),
        win_rate = CASE 
            WHEN (total_wins + CASE WHEN NEW.player2_result = 'win' THEN 1 ELSE 0 END + 
                  total_losses + CASE WHEN NEW.player2_result = 'lose' THEN 1 ELSE 0 END) > 0
            THEN ((total_wins + CASE WHEN NEW.player2_result = 'win' THEN 1 ELSE 0 END) * 100.0) / 
                 (total_wins + CASE WHEN NEW.player2_result = 'win' THEN 1 ELSE 0 END + 
                  total_losses + CASE WHEN NEW.player2_result = 'lose' THEN 1 ELSE 0 END)
            ELSE 0.00
        END,
        last_battle_at = NEW.finished_at,
        updated_at = CURRENT_TIMESTAMP
    WHERE user_id = NEW.player2_id;
END$$

DELIMITER ;

-- ============================================
-- インデックス最適化
-- ============================================

-- 複合インデックス（パフォーマンス向上）
CREATE INDEX idx_user_stats_composite_ranking ON user_stats(is_active, rank_points DESC, daily_wins DESC);
CREATE INDEX idx_match_history_recent ON match_history(created_at DESC, match_type);
CREATE INDEX idx_websocket_connections_active_users ON websocket_connections(status, user_id, last_activity);

-- ============================================
-- パーティション設定（将来の拡張用）
-- ============================================

-- match_historyテーブルの月次パーティション化（オプション）
-- 大量データ対応時に有効化
/*
ALTER TABLE match_history 
PARTITION BY RANGE (YEAR(created_at) * 100 + MONTH(created_at)) (
    PARTITION p202401 VALUES LESS THAN (202402),
    PARTITION p202402 VALUES LESS THAN (202403),
    -- 必要に応じて追加
    PARTITION pMax VALUES LESS THAN MAXVALUE
);
*/

-- ============================================
-- 実行時間測定用ビュー
-- ============================================

-- アクティブユーザー統計ビュー
CREATE VIEW active_users_stats AS
SELECT 
    COUNT(*) as total_active_users,
    COUNT(CASE WHEN last_battle_at >= DATE_SUB(NOW(), INTERVAL 1 DAY) THEN 1 END) as daily_active_users,
    COUNT(CASE WHEN last_battle_at >= DATE_SUB(NOW(), INTERVAL 7 DAY) THEN 1 END) as weekly_active_users,
    AVG(win_rate) as avg_win_rate,
    MAX(max_win_streak) as global_max_streak
FROM user_stats 
WHERE is_active = TRUE;

-- バトル統計ビュー
CREATE VIEW battle_stats AS
SELECT 
    DATE(created_at) as battle_date,
    COUNT(*) as total_battles,
    COUNT(CASE WHEN winner = 3 THEN 1 END) as total_draws,
    AVG(battle_duration_seconds) as avg_duration,
    COUNT(CASE WHEN match_type = 'random' THEN 1 END) as random_matches,
    COUNT(CASE WHEN match_type = 'friend' THEN 1 END) as friend_matches
FROM match_history 
GROUP BY DATE(created_at)
ORDER BY battle_date DESC;