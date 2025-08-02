-- データベース作成
CREATE DATABASE IF NOT EXISTS janken_db;
USE janken_db;

-- admin_logs（管理者オペレーションログ）
CREATE TABLE IF NOT EXISTS admin_logs (
    log_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    admin_user VARCHAR(50) NOT NULL,
    operation VARCHAR(100) NOT NULL,
    target_id VARCHAR(36) NOT NULL,
    details TEXT,
    operated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- daily_ranking（デイリーランキング）
CREATE TABLE IF NOT EXISTS daily_ranking (
    ranking_position INT PRIMARY KEY,
    user_id VARCHAR(36),
    wins INT,
    last_win_at DATETIME,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- match_history（マッチング結果）
CREATE TABLE IF NOT EXISTS match_history (
    fight_no BIGINT AUTO_INCREMENT PRIMARY KEY,
    player1_id VARCHAR(36) NOT NULL,
    player2_id VARCHAR(36) NOT NULL,
    player1_nickname VARCHAR(50),
    player2_nickname VARCHAR(50),
    player1_hand ENUM('rock','paper','scissors') NOT NULL,
    player2_hand ENUM('rock','paper','scissors') NOT NULL,
    player1_result ENUM('win','lose','draw') NOT NULL,
    player2_result ENUM('win','lose','draw') NOT NULL,
    winner TINYINT UNSIGNED NOT NULL DEFAULT 0,
    draw_count INT NOT NULL DEFAULT 0,
    match_type ENUM('random','friend') NOT NULL,
    created_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    finished_at DATETIME(3),
    INDEX idx_p1 (player1_id),
    INDEX idx_p2 (player2_id),
    INDEX idx_p1_result (player1_id, player1_result),
    INDEX idx_p2_result (player2_id, player2_result)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- users（ユーザー情報）
CREATE TABLE IF NOT EXISTS users (
    management_code BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    email VARCHAR(255),
    password VARCHAR(255) NOT NULL,
    name VARCHAR(50),
    nickname VARCHAR(50) NOT NULL,
    postal_code VARCHAR(10),
    address VARCHAR(255),
    phone_number VARCHAR(15),
    university VARCHAR(100),
    birthdate DATE,
    profile_image_url VARCHAR(255) NOT NULL,
    student_id_image_url VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    register_type VARCHAR(20) DEFAULT 'email',
    is_student_id_editable TINYINT DEFAULT 0,
    is_banned TINYINT DEFAULT 0,
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- registration_itemdata（ユーザー端末識別情報）
CREATE TABLE IF NOT EXISTS registration_itemdata (
    management_code BIGINT NOT NULL,
    subnum INT NOT NULL DEFAULT 1,
    itemtype TINYINT NOT NULL DEFAULT 0,
    itemid VARCHAR(128) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (management_code, subnum),
    FOREIGN KEY (management_code) REFERENCES users(management_code),
    INDEX idx_registration_itemdata_itemid (itemid)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- user_logs（ユーザー操作ログ）
CREATE TABLE IF NOT EXISTS user_logs (
    log_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL DEFAULT '',
    operation_code VARCHAR(10),
    operation VARCHAR(100),
    details TEXT,
    operated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_logs_uid (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- user_stats（ユーザー状態）
CREATE TABLE IF NOT EXISTS user_stats (
    management_code BIGINT NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    total_wins INT DEFAULT 0,
    current_win_streak INT DEFAULT 0,
    max_win_streak INT DEFAULT 0,
    hand_stats_rock INT DEFAULT 0,
    hand_stats_scissors INT DEFAULT 0,
    hand_stats_paper INT DEFAULT 0,
    favorite_hand VARCHAR(10),
    recent_hand_results_str VARCHAR(255) DEFAULT '',
    daily_wins INT DEFAULT 0,
    daily_losses INT DEFAULT 0,
    daily_draws INT DEFAULT 0,
    title VARCHAR(50) DEFAULT '',
    available_titles VARCHAR(255) DEFAULT '',
    alias VARCHAR(50) DEFAULT '',
    show_title BOOLEAN DEFAULT TRUE,
    show_alias BOOLEAN DEFAULT TRUE,
    user_rank VARCHAR(20) DEFAULT 'no_rank',
    last_reset_at DATE NOT NULL,
    PRIMARY KEY (management_code),
    FOREIGN KEY (management_code) REFERENCES users(management_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- sessions テーブル
-- ユーザーセッション管理用
-- JWT + Redis でのセッション管理を補完し、デバイスごとの詳細な制御を実現
-- 2025-06 現在：アクティブに使用中
-- ============================================

CREATE TABLE IF NOT EXISTS sessions (
    session_id VARCHAR(128) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    access_token VARCHAR(512) NOT NULL,
    refresh_token VARCHAR(512) NOT NULL,
    device_id VARCHAR(128) NOT NULL,
    expires_at DATETIME NOT NULL,
    last_activity DATETIME NOT NULL,
    ip_address VARCHAR(45) NOT NULL,
    user_agent VARCHAR(255),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (device_id) REFERENCES registration_itemdata(itemid),
    INDEX idx_sessions_user_id (user_id),
    INDEX idx_sessions_device_id (device_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- refresh_tokens テーブル
-- リフレッシュトークンの管理とセキュリティ制御
-- 明示的な失効管理とセキュリティ監査に使用
-- 2025-06 現在：アクティブに使用中
-- ============================================

CREATE TABLE IF NOT EXISTS refresh_tokens (
    token_id VARCHAR(128) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    refresh_token_hash VARCHAR(512) NOT NULL,
    device_id VARCHAR(128) NOT NULL,
    issued_at DATETIME NOT NULL,
    expires_at DATETIME NOT NULL,
    revoked BOOLEAN NOT NULL DEFAULT FALSE,
    revoked_reason VARCHAR(100),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (device_id) REFERENCES registration_itemdata(itemid),
    INDEX idx_refresh_tokens_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- oauth_accounts テーブル
-- 将来 Google/LINE/Apple などの OAuth 認証連携を行う場合に使用
-- 現時点（2025-06）では未使用。ユーザー登録/認証はJWT+reCAPTCHAのみ
-- ============================================

CREATE TABLE IF NOT EXISTS oauth_accounts (
    oauth_id VARCHAR(128) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    provider VARCHAR(20) NOT NULL,
    provider_user_id VARCHAR(255) NOT NULL,
    access_token TEXT,
    refresh_token TEXT,
    token_expires_at DATETIME,
    profile_data JSON,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- security_events テーブル
-- セキュリティ関連イベントの記録
-- 不正アクセスの検知、監査ログ、ユーザーサポート用
-- 2025-06 現在：アクティブに使用中
-- ============================================

CREATE TABLE IF NOT EXISTS security_events (
    event_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    ip_address VARCHAR(45) NOT NULL,
    device_info JSON,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    INDEX idx_security_events_user_id (user_id),
    INDEX idx_security_events_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- login_attempts テーブル
-- ログイン試行の記録と制限
-- レート制限、ブルートフォース攻撃対策用
-- 2025-06 現在：アクティブに使用中
-- ============================================

CREATE TABLE IF NOT EXISTS login_attempts (
    attempt_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    ip_address VARCHAR(45) NOT NULL,
    attempt_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN NOT NULL DEFAULT FALSE,
    failure_reason VARCHAR(100),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    INDEX idx_login_attempts_user_id (user_id),
    INDEX idx_login_attempts_ip (ip_address),
    INDEX idx_login_attempts_time (attempt_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- two_factor_auth テーブル
-- 2要素認証（2FA）の設定と管理
-- TOTP方式での追加認証レイヤーを提供
-- 2025-06 現在：アクティブに使用中
-- ============================================

CREATE TABLE IF NOT EXISTS two_factor_auth (
    user_id VARCHAR(36) PRIMARY KEY,
    enabled BOOLEAN NOT NULL DEFAULT FALSE,
    secret_key VARCHAR(32) NOT NULL,
    backup_codes JSON,
    last_used DATETIME,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci; 