-- =====================================================
-- じゃんけんバトルシステム - 完全認証版（Redis + JWT + Magic Link）
-- データベーステーブル作成スクリプト（既存システム統合版）
-- =====================================================

-- データベース作成
CREATE DATABASE IF NOT EXISTS janken_db;
USE janken_db;

-- =====================================================
-- 1. 認証・セッション管理テーブル
-- =====================================================

-- ユーザー基本情報（既存システムとの互換性を保持）
CREATE TABLE users (
    management_code BIGINT AUTO_INCREMENT UNIQUE,             -- 既存システム互換用管理コード、内部管理・連携、ユニーク制約
    user_id VARCHAR(50) PRIMARY KEY,                         -- JWTのsubクレーム、セッション管理、外部キー参照用
    email VARCHAR(255) UNIQUE NOT NULL,                      -- Magic Link送信先、ログイン識別子、重複防止
    nickname VARCHAR(100) NOT NULL,                          -- ゲーム内表示名、ランキング表示、フレンド検索用
    name VARCHAR(50),                                        -- 実名、本人確認、管理画面表示
    role ENUM('user', 'developer', 'admin') DEFAULT 'user', -- 権限管理、管理画面アクセス制御、機能制限
    profile_image_url VARCHAR(500),                          -- プロフィール画像、アバター表示、S3/MinIO保存パス
    title VARCHAR(100) DEFAULT 'じゃんけんプレイヤー',       -- ユーザー称号、ランキング表示、実績システム
    alias VARCHAR(100),                                      -- 別名、ニックネーム変更履歴、検索用
    is_active BOOLEAN DEFAULT TRUE,                          -- アカウント有効性、BAN機能、ログイン制限
    is_banned TINYINT DEFAULT 0,                            -- BAN状態、既存システム互換、管理画面制御
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,          -- アカウント作成日時、統計分析、監査ログ
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, -- 最終更新日時、データ整合性確認
    INDEX idx_email (email),                                -- メール検索、Magic Link処理高速化
    INDEX idx_role (role),                                  -- 権限別ユーザー検索、管理画面表示
    INDEX idx_created_at (created_at),                      -- 新規ユーザー分析、成長率計算
    INDEX idx_management_code (management_code)              -- 既存システム連携、管理コード検索
);

-- ユーザー詳細情報（個人情報・学生情報）
CREATE TABLE user_profiles (
    user_id VARCHAR(50) PRIMARY KEY,                         -- ユーザーとの紐付け、外部キー参照
    postal_code VARCHAR(10),                                 -- 郵便番号、住所管理、配送対応
    address VARCHAR(255),                                    -- 住所、本人確認、管理画面表示
    phone_number VARCHAR(15),                                -- 電話番号、本人確認、サポート対応
    university VARCHAR(100),                                 -- 大学名、学生証確認、学割対応
    birthdate DATE,                                          -- 生年月日、年齢確認、制限機能
    student_id_image_url VARCHAR(500),                       -- 学生証画像、本人確認、S3/MinIO保存パス
    is_student_id_editable TINYINT DEFAULT 0,               -- 学生証編集可否、既存システム互換、管理制御
    register_type VARCHAR(20) DEFAULT 'email',               -- 登録方式、認証方式管理、統計分析
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,          -- プロフィール作成日時、監査ログ
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, -- 最終更新日時、変更履歴
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE, -- ユーザー削除時の連動削除
    INDEX idx_university (university),                       -- 大学別ユーザー検索、統計分析
    INDEX idx_birthdate (birthdate)                          -- 年齢別検索、制限機能、統計分析
);

-- パスワード資格情報（任意）
CREATE TABLE auth_credentials (
    user_id VARCHAR(50) NOT NULL,                            -- ユーザーとの紐付け、外部キー参照
    password_hash VARCHAR(255) NULL,                         -- ハッシュ化パスワード、セキュリティ要件
    password_algo ENUM('argon2id','bcrypt','scrypt') DEFAULT 'argon2id', -- ハッシュアルゴリズム、将来的な強度向上
    password_version SMALLINT DEFAULT 1,                    -- パスワードポリシー変更時の移行管理
    password_updated_at TIMESTAMP NULL,                     -- パスワード変更日時、セキュリティ監査
    is_password_enabled BOOLEAN DEFAULT FALSE,               -- パスワード認証有効化フラグ、非常口としての利用
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,          -- レコード作成日時、監査ログ
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, -- 最終更新日時、変更履歴
    PRIMARY KEY (user_id),                                   -- 1ユーザー1レコード、重複防止
    CONSTRAINT fk_authcred_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE -- ユーザー削除時の連動削除
);

-- 端末管理（複数端末対応）
CREATE TABLE user_devices (
    device_id VARCHAR(128) PRIMARY KEY,                      -- 端末識別子、セッション管理、重複防止
    user_id VARCHAR(50) NOT NULL,                            -- 端末所有者、ユーザー別端末管理
    subnum INT NOT NULL DEFAULT 1,                          -- 端末番号、同一ユーザーの複数端末管理
    itemtype TINYINT NOT NULL DEFAULT 0,                    -- 端末種別、デバイス分類、統計分析
    device_name VARCHAR(100),                                -- 端末名、管理画面表示、ユーザー識別
    device_info JSON,                                        -- 端末詳細情報、柔軟なデータ保存、後方互換性
    is_active BOOLEAN DEFAULT TRUE,                          -- 端末有効性、無効化・削除管理
    last_used_at TIMESTAMP NULL,                            -- 最終使用日時、アクティブ端末判定
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,          -- 端末登録日時、監査ログ
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, -- 最終更新日時、変更履歴
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE, -- ユーザー削除時の連動削除
    UNIQUE KEY uniq_user_subnum (user_id, subnum),          -- ユーザー・端末番号重複防止、データ整合性
    INDEX idx_user_id (user_id),                             -- ユーザー別端末検索、管理
    INDEX idx_device_type (itemtype),                        -- 端末種別検索、統計分析
    INDEX idx_last_used (last_used_at)                      -- 最終使用日時検索、クリーンアップ処理
);

-- Magic Link トークン
CREATE TABLE magic_link_tokens (
    token_hash VARCHAR(128) PRIMARY KEY,                     -- トークンのハッシュ値、セキュリティ（生トークンは保存しない）
    email VARCHAR(255) NOT NULL,                             -- 送信先メールアドレス、トークン検証時の照合
    user_id VARCHAR(50) NULL,                                -- 既存ユーザーの場合の紐付け、新規作成時のNULL
    issued_at DATETIME NOT NULL,                             -- トークン発行日時、有効期限計算の基準
    expires_at DATETIME NOT NULL,                            -- トークン有効期限、自動失効処理
    used_at DATETIME NULL,                                   -- トークン使用日時、重複使用防止、監査ログ
    ip_address VARCHAR(45),                                  -- 発行元IPアドレス、セキュリティ監査、不正アクセス検知
    user_agent VARCHAR(255),                                 -- 発行元ブラウザ情報、デバイス識別、セキュリティ監査
    INDEX idx_ml_email (email),                             -- メール別トークン検索、重複発行防止
    INDEX idx_ml_expires (expires_at),                      -- 期限切れトークン削除、クリーンアップ処理
    INDEX idx_ml_user (user_id),                            -- ユーザー別トークン履歴、監査ログ
    CONSTRAINT fk_ml_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL -- ユーザー削除時の参照整合性
);

-- セッション管理（端末ごと）
CREATE TABLE sessions (
    session_id VARCHAR(100) PRIMARY KEY,                     -- セッション識別子、JWTのjtiクレーム、Redisキー
    user_id VARCHAR(50) NOT NULL,                            -- セッション所有者、ユーザー別セッション管理
    device_id VARCHAR(128) NOT NULL,                         -- 端末識別子、複数端末同時ログイン制御
    ip_address VARCHAR(45) NULL,                             -- 接続元IP、セキュリティ監査、不正アクセス検知
    user_agent VARCHAR(255) NULL,                            -- ブラウザ情報、デバイス識別、セッション復旧
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,          -- セッション作成日時、有効期限計算
    last_seen_at TIMESTAMP NULL,                             -- 最終アクセス日時、セッションタイムアウト判定
    is_revoked BOOLEAN DEFAULT FALSE,                        -- セッション無効化フラグ、強制ログアウト、セキュリティ対応
    CONSTRAINT fk_sessions_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE, -- ユーザー削除時の連動削除
    CONSTRAINT fk_sessions_device FOREIGN KEY (device_id) REFERENCES user_devices(device_id) ON DELETE CASCADE, -- 端末削除時の連動削除
    UNIQUE KEY uniq_user_device (user_id, device_id),       -- 端末別セッション制限、重複セッション防止
    INDEX idx_sessions_user (user_id),                       -- ユーザー別セッション検索、アクティブセッション管理
    INDEX idx_sessions_seen (last_seen_at)                   -- タイムアウトセッション検索、クリーンアップ処理
);

-- リフレッシュトークン
CREATE TABLE refresh_tokens (
    token_id VARCHAR(100) PRIMARY KEY,                       -- トークン識別子、ローテーション履歴管理
    session_id VARCHAR(100) NOT NULL,                        -- セッションとの紐付け、セッション無効化時の連動
    token_hash VARCHAR(255) NOT NULL,                        -- トークンのハッシュ値、セキュリティ（生トークンは保存しない）
    issued_at DATETIME NOT NULL,                             -- トークン発行日時、有効期限計算
    expires_at DATETIME NOT NULL,                            -- トークン有効期限、自動失効処理
    rotated_from VARCHAR(100) NULL,                          -- 前回トークンID、ローテーション履歴、セキュリティ監査
    is_revoked BOOLEAN DEFAULT FALSE,                        -- トークン無効化フラグ、強制失効、セキュリティ対応
    revoked_reason VARCHAR(100) NULL,                        -- 失効理由、セキュリティ監査、運用管理
    CONSTRAINT fk_rt_session FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE, -- セッション削除時の連動削除
    UNIQUE KEY uniq_rt_hash (token_hash),                   -- トークンハッシュ重複防止、セキュリティ
    INDEX idx_rt_session (session_id),                       -- セッション別トークン検索、管理
    INDEX idx_rt_expires (expires_at),                       -- 期限切れトークン削除、クリーンアップ処理
    INDEX idx_rt_revoked (is_revoked)                        -- 無効化トークン検索、監査ログ
);

-- JWTブラックリスト（即時失効用）
CREATE TABLE jwt_blacklist (
    jti_hash VARCHAR(128) PRIMARY KEY,                       -- JWTのJTIハッシュ、即時失効処理、セキュリティ
    user_id VARCHAR(50) NOT NULL,                            -- 失効対象ユーザー、監査ログ、統計分析
    reason VARCHAR(100) NULL,                                -- 失効理由、セキュリティ監査、運用管理
    revoked_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,  -- 失効日時、監査ログ、統計分析
    expires_at DATETIME NOT NULL,                            -- JWT有効期限、自動クリーンアップ、ストレージ最適化
    INDEX idx_jwtbl_user (user_id),                          -- ユーザー別失効履歴、監査ログ
    INDEX idx_jwtbl_expires (expires_at),                    -- 期限切れレコード削除、クリーンアップ処理
    CONSTRAINT fk_jwtbl_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE -- ユーザー削除時の連動削除
);

-- 2要素認証（TOTP）
CREATE TABLE two_factor_auth (
    user_id VARCHAR(50) PRIMARY KEY,                         -- ユーザーとの紐付け、外部キー参照
    enabled BOOLEAN NOT NULL DEFAULT FALSE,                  -- 2FA有効化フラグ、セキュリティ設定管理
    secret_key VARCHAR(32),                                  -- TOTP秘密鍵、認証コード生成、セキュリティ（enabledがtrueの場合のみ必須）
    backup_codes JSON,                                       -- バックアップコード、緊急時アクセス、セキュリティ
    last_used DATETIME NULL,                                 -- 最終使用日時、セキュリティ監査、統計
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,           -- 2FA設定日時、監査ログ
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, -- 最終更新日時、変更履歴
    CONSTRAINT fk_2fa_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE, -- ユーザー削除時の連動削除
    INDEX idx_2fa_enabled (enabled)                          -- 2FA有効化状態検索、統計分析
);

-- OAuth連携（将来的な外部認証対応）
CREATE TABLE oauth_accounts (
    oauth_id VARCHAR(128) PRIMARY KEY,                       -- OAuth識別子、外部認証管理
    user_id VARCHAR(50) NOT NULL,                            -- ユーザーとの紐付け、外部キー参照
    provider ENUM('google','line','apple','github') NOT NULL, -- 認証プロバイダー、連携先管理
    provider_user_id VARCHAR(255) NOT NULL,                  -- プロバイダー側ユーザーID、連携管理
    access_token TEXT,                                       -- アクセストークン、API連携、権限管理
    refresh_token TEXT,                                      -- リフレッシュトークン、トークン更新、連携維持
    token_expires_at DATETIME,                               -- トークン有効期限、自動更新、連携管理
    profile_data JSON,                                       -- プロフィールデータ、連携情報、統計分析
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,           -- 連携開始日時、監査ログ
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, -- 最終更新日時、変更履歴
    CONSTRAINT fk_oauth_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE, -- ユーザー削除時の連動削除
    UNIQUE KEY uniq_provider_user (provider, provider_user_id), -- プロバイダー・ユーザー重複防止、連携管理
    INDEX idx_oauth_user (user_id),                          -- ユーザー別OAuth連携検索、管理
    INDEX idx_oauth_provider (provider)                      -- プロバイダー別検索、統計分析
);

-- ログイン試行管理（ブルートフォース攻撃対策）
CREATE TABLE login_attempts (
    attempt_id BIGINT PRIMARY KEY AUTO_INCREMENT,             -- 試行識別子、ログ管理、監査
    user_id VARCHAR(50) NULL,                                -- 試行対象ユーザー、ユーザー別監査ログ
    email VARCHAR(255) NULL,                                 -- 試行対象メール、メール別監査ログ
    ip_address VARCHAR(45) NOT NULL,                         -- 試行元IP、不正アクセス検知、制限管理
    attempt_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, -- 試行日時、レート制限、統計分析
    success BOOLEAN NOT NULL DEFAULT FALSE,                  -- 試行結果、成功・失敗判定、統計分析
    failure_reason VARCHAR(100) NULL,                        -- 失敗理由、セキュリティ監査、ユーザーサポート
    user_agent VARCHAR(255),                                 -- ブラウザ情報、デバイス識別、セキュリティ監査
    INDEX idx_login_user (user_id),                          -- ユーザー別試行履歴、監査ログ
    INDEX idx_login_email (email),                           -- メール別試行履歴、監査ログ
    INDEX idx_login_ip (ip_address),                         -- IP別試行履歴、不正アクセス検知
    INDEX idx_login_time (attempt_time),                     -- 時系列試行履歴、レート制限
    INDEX idx_login_success (success)                        -- 成功・失敗別統計、セキュリティ分析
);

-- セキュリティイベントログ
CREATE TABLE security_events (
    event_id BIGINT PRIMARY KEY AUTO_INCREMENT,               -- イベント識別子、ログ管理、監査
    user_id VARCHAR(50) NULL,                                -- イベント対象ユーザー、ユーザー別監査ログ
    event_type ENUM('magic_link_issued','magic_link_used','login_success','login_failed',
                    'password_set','password_reset','session_revoked','token_rotated',
                    'websocket_connected','websocket_disconnected','2fa_enabled','2fa_disabled',
                    'oauth_linked','oauth_unlinked','device_registered','device_removed') NOT NULL, -- イベント種別、分類・集計、監査
    detail JSON NULL,                                        -- イベント詳細情報、柔軟なデータ保存、後方互換性
    ip_address VARCHAR(45),                                  -- イベント発生元IP、セキュリティ監査、不正アクセス検知
    user_agent VARCHAR(255),                                 -- ブラウザ情報、デバイス識別、セキュリティ監査
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,           -- イベント発生日時、時系列分析、監査ログ
    INDEX idx_sev_user (user_id),                            -- ユーザー別イベント検索、監査ログ
    INDEX idx_sev_type_time (event_type, created_at),        -- イベント種別・時系列検索、統計分析
    INDEX idx_sev_ip (ip_address),                           -- IP別イベント検索、セキュリティ監査
    CONSTRAINT fk_sev_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL -- ユーザー削除時はNULL保持（監査ログ維持）
);

-- 管理者操作ログ
CREATE TABLE admin_logs (
    log_id BIGINT PRIMARY KEY AUTO_INCREMENT,                 -- ログ識別子、ログ管理、監査
    admin_user VARCHAR(50) NOT NULL,                         -- 管理者ユーザー、操作者識別、監査ログ
    operation VARCHAR(100) NOT NULL,                         -- 操作内容、管理操作分類、監査
    target_id VARCHAR(50) NULL,                              -- 操作対象、対象識別、監査ログ
    target_type VARCHAR(50) NULL,                            -- 対象種別、操作分類、統計分析
    details TEXT,                                            -- 操作詳細、詳細情報、監査ログ
    ip_address VARCHAR(45),                                  -- 操作元IP、セキュリティ監査、不正操作検知
    user_agent VARCHAR(255),                                 -- ブラウザ情報、デバイス識別、セキュリティ監査
    operated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,          -- 操作日時、時系列分析、監査ログ
    INDEX idx_admin_user (admin_user),                       -- 管理者別操作履歴、監査ログ
    INDEX idx_admin_operation (operation),                   -- 操作種別検索、統計分析
    INDEX idx_admin_target (target_id, target_type),         -- 対象別操作履歴、監査ログ
    INDEX idx_admin_time (operated_at)                       -- 時系列操作履歴、監査ログ
);

-- =====================================================
-- 2. ゲーム・バトル関連テーブル（既存から継承・拡張）
-- =====================================================

-- バトル結果記録（既存match_historyとの互換性を保持）
CREATE TABLE battle_results (
    battle_id VARCHAR(100) PRIMARY KEY,                      -- バトル識別子、WebSocket接続、結果照合
    fight_no BIGINT AUTO_INCREMENT UNIQUE,                   -- 既存システム互換用戦闘番号、連番管理、ユニーク制約
    player1_id VARCHAR(50) NOT NULL,                         -- プレイヤー1、勝敗判定、統計計算
    player2_id VARCHAR(50) NOT NULL,                         -- プレイヤー2、勝敗判定、統計計算
    player1_nickname VARCHAR(50),                            -- プレイヤー1ニックネーム、既存システム互換、表示用
    player2_nickname VARCHAR(50),                            -- プレイヤー2ニックネーム、既存システム互換、表示用
    winner_id VARCHAR(50) NULL,                              -- 勝者、ランキング計算、実績システム
    total_rounds INT DEFAULT 0,                              -- 総ラウンド数、バトル統計、分析
    player1_wins INT DEFAULT 0,                              -- プレイヤー1勝利数、勝率計算、統計
    player2_wins INT DEFAULT 0,                              -- プレイヤー2勝利数、勝率計算、統計
    draws INT DEFAULT 0,                                     -- 引き分け数、統計分析、ゲームバランス調整
    battle_duration_seconds INT DEFAULT 0,                   -- バトル時間、統計分析、パフォーマンス監視
    match_type ENUM('random','friend') NOT NULL DEFAULT 'random', -- マッチング種別、既存システム互換、統計分析
    started_at TIMESTAMP NULL,                               -- 開始時刻、統計分析、タイムアウト処理
    finished_at TIMESTAMP NULL,                              -- 終了時刻、統計分析、パフォーマンス監視
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,           -- レコード作成時刻、履歴管理、監査
    FOREIGN KEY (player1_id) REFERENCES users(user_id) ON DELETE CASCADE, -- ユーザー削除時の連動削除
    FOREIGN KEY (player2_id) REFERENCES users(user_id) ON DELETE CASCADE, -- ユーザー削除時の連動削除
    FOREIGN KEY (winner_id) REFERENCES users(user_id) ON DELETE SET NULL, -- 勝者削除時はNULL保持（統計維持）
    INDEX idx_player1 (player1_id),                          -- プレイヤー1別バトル履歴、統計計算
    INDEX idx_player2 (player2_id),                          -- プレイヤー2別バトル履歴、統計計算
    INDEX idx_winner (winner_id),                            -- 勝者別統計、ランキング計算
    INDEX idx_created_at (created_at),                       -- 時系列検索、履歴管理、統計分析
    INDEX idx_fight_no (fight_no),                           -- 既存システム互換、戦闘番号検索
    INDEX idx_match_type (match_type)                        -- マッチング種別検索、統計分析
);

-- バトルラウンド詳細（既存match_historyとの互換性を保持）
CREATE TABLE battle_rounds (
    round_id VARCHAR(100) PRIMARY KEY,                       -- ラウンド識別子、詳細管理、分析
    battle_id VARCHAR(100) NOT NULL,                         -- バトルとの紐付け、外部キー参照
    round_number INT NOT NULL,                               -- ラウンド番号、順序管理、統計分析
    player1_hand ENUM('rock', 'paper', 'scissors') NULL,    -- プレイヤー1の手、勝敗判定、統計分析
    player2_hand ENUM('rock', 'paper', 'scissors') NULL,    -- プレイヤー2の手、勝敗判定、統計分析
    player1_result ENUM('win', 'lose', 'draw') NULL,        -- プレイヤー1結果、既存システム互換、統計分析
    player2_result ENUM('win', 'lose', 'draw') NULL,        -- プレイヤー2結果、既存システム互換、統計分析
    winner_id VARCHAR(50) NULL,                              -- ラウンド勝者、統計計算、分析
    round_result ENUM('player1_win', 'player2_win', 'draw') NULL, -- ラウンド結果、統計分類、分析
    round_duration_seconds INT DEFAULT 0,                    -- ラウンド時間、統計分析、パフォーマンス監視
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,        -- 提出時刻、統計分析、不正検知
    FOREIGN KEY (battle_id) REFERENCES battle_results(battle_id) ON DELETE CASCADE, -- バトル削除時の連動削除
    FOREIGN KEY (winner_id) REFERENCES users(user_id) ON DELETE SET NULL, -- 勝者削除時はNULL保持
    INDEX idx_battle_id (battle_id),                         -- バトル別ラウンド検索、統計計算
    INDEX idx_round_number (round_number),                   -- ラウンド番号順検索、順序管理
    INDEX idx_submitted_at (submitted_at)                    -- 提出時刻検索、統計分析、不正検知
);

-- =====================================================
-- 3. 統計・ランキングテーブル（既存システムとの互換性を保持）
-- =====================================================

-- ユーザー統計（既存user_statsとの互換性を保持）
CREATE TABLE user_stats (
    user_id VARCHAR(50) PRIMARY KEY,                         -- ユーザーとの紐付け、統計管理
    total_matches INT DEFAULT 0,                             -- 総試合数、ランキング計算、実績システム
    total_wins INT DEFAULT 0,                                -- 総勝利数、勝率計算、ランキング
    total_losses INT DEFAULT 0,                              -- 総敗北数、勝率計算、統計分析
    total_draws INT DEFAULT 0,                               -- 総引き分け数、統計分析、ゲームバランス
    win_rate DECIMAL(5,2) DEFAULT 0.00,                     -- 勝率、ランキング計算、実績判定
    current_streak INT DEFAULT 0,                            -- 現在の連勝数、実績システム、モチベーション
    best_streak INT DEFAULT 0,                               -- 最高連勝数、実績システム、統計分析
    total_rounds_played INT DEFAULT 0,                       -- 総ラウンド数、統計分析、パフォーマンス監視
    rock_count INT DEFAULT 0,                                -- グー使用回数、統計分析、戦略分析
    paper_count INT DEFAULT 0,                               -- パー使用回数、統計分析、戦略分析
    scissors_count INT DEFAULT 0,                            -- チョキ使用回数、統計分析、戦略分析
    favorite_hand VARCHAR(10),                               -- お気に入りの手、既存システム互換、統計分析
    recent_hand_results_str VARCHAR(255) DEFAULT '',         -- 最近の手の結果、既存システム互換、統計分析
    average_battle_duration_seconds INT DEFAULT 0,           -- 平均バトル時間、統計分析、パフォーマンス監視
    last_battle_at TIMESTAMP NULL,                           -- 最終バトル時刻、アクティブユーザー判定、統計
    title VARCHAR(50) DEFAULT '',                            -- 現在の称号、既存システム互換、実績システム
    available_titles VARCHAR(255) DEFAULT '',                -- 利用可能称号、既存システム互換、実績システム
    alias VARCHAR(50) DEFAULT '',                            -- 現在の別名、既存システム互換、表示設定
    show_title BOOLEAN DEFAULT TRUE,                         -- 称号表示設定、既存システム互換、ユーザー設定
    show_alias BOOLEAN DEFAULT TRUE,                         -- 別名表示設定、既存システム互換、ユーザー設定
    user_rank VARCHAR(20) DEFAULT 'no_rank',                 -- ユーザーランク、既存システム互換、ランキングシステム
    last_reset_at DATE NOT NULL DEFAULT CURRENT_DATE,        -- 最終リセット日、既存システム互換、統計管理
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, -- 最終更新時刻、データ整合性確認
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE, -- ユーザー削除時の連動削除
    INDEX idx_win_rate (win_rate),                           -- 勝率順検索、ランキング計算
    INDEX idx_total_matches (total_matches),                 -- 試合数順検索、ランキング計算
    INDEX idx_last_battle (last_battle_at),                  -- 最終バトル時刻検索、アクティブユーザー判定
    INDEX idx_user_rank (user_rank),                         -- ランク別検索、ランキング管理
    INDEX idx_favorite_hand (favorite_hand)                  -- お気に入りの手別検索、統計分析
);

-- 日次・週次ランキング（既存daily_rankingとの互換性を保持）
CREATE TABLE daily_rankings (
    ranking_id VARCHAR(100) PRIMARY KEY,                     -- ランキング識別子、管理・更新
    ranking_position INT NOT NULL,                           -- 順位、既存システム互換、ランキング表示
    ranking_date DATE NOT NULL,                              -- ランキング対象日、日次集計、履歴管理
    user_id VARCHAR(50) NOT NULL,                            -- ランキング対象ユーザー、外部キー参照
    daily_wins INT DEFAULT 0,                                -- 日次勝利数、ランキング計算、統計
    daily_matches INT DEFAULT 0,                             -- 日次試合数、ランキング計算、統計
    daily_win_rate DECIMAL(5,2) DEFAULT 0.00,               -- 日次勝率、ランキング計算、統計
    last_win_at DATETIME NULL,                               -- 最終勝利時刻、既存システム互換、統計分析
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,           -- レコード作成時刻、履歴管理、監査
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, -- 最終更新時刻、既存システム互換
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE, -- ユーザー削除時の連動削除
    UNIQUE KEY unique_daily_rank (ranking_date, user_id),    -- 日次・ユーザー重複防止、データ整合性
    INDEX idx_ranking_date (ranking_date),                   -- 日別ランキング検索、履歴管理
    INDEX idx_ranking_position (ranking_position),            -- 順位別検索、ランキング表示
    INDEX idx_last_win (last_win_at)                         -- 最終勝利時刻検索、統計分析
);

CREATE TABLE weekly_rankings (
    ranking_id VARCHAR(100) PRIMARY KEY,                     -- ランキング識別子、管理・更新
    ranking_week DATE NOT NULL,                              -- ランキング対象週、週次集計、履歴管理
    user_id VARCHAR(50) NOT NULL,                            -- ランキング対象ユーザー、外部キー参照
    rank_position INT NOT NULL,                              -- 順位、ランキング表示、実績システム
    weekly_wins INT DEFAULT 0,                               -- 週次勝利数、ランキング計算、統計
    weekly_matches INT DEFAULT 0,                            -- 週次試合数、ランキング計算、統計
    weekly_win_rate DECIMAL(5,2) DEFAULT 0.00,              -- 週次勝率、ランキング計算、統計
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,           -- レコード作成時刻、履歴管理、監査
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE, -- ユーザー削除時の連動削除
    UNIQUE KEY unique_weekly_rank (ranking_week, user_id),   -- 週次・ユーザー重複防止、データ整合性
    INDEX idx_ranking_week (ranking_week),                   -- 週別ランキング検索、履歴管理
    INDEX idx_rank_position (rank_position)                  -- 順位別検索、ランキング表示
);

-- =====================================================
-- 4. システム管理テーブル
-- =====================================================

-- システム設定
CREATE TABLE system_settings (
    setting_key VARCHAR(100) PRIMARY KEY,                    -- 設定キー、設定管理、動的設定変更
    setting_value TEXT NOT NULL,                             -- 設定値、柔軟なデータ型対応、JSON設定も可能
    description TEXT,                                        -- 設定説明、運用管理、開発者向けドキュメント
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP -- 最終更新時刻、変更履歴、監査
);

-- アクティビティログ（既存user_logsとの互換性を保持）
CREATE TABLE activity_logs (
    log_id BIGINT PRIMARY KEY AUTO_INCREMENT,                -- ログ識別子、ログ管理、監査
    user_id VARCHAR(50) NULL,                                -- アクティビティ対象ユーザー、ユーザー別ログ
    operation_code VARCHAR(10),                              -- 操作コード、既存システム互換、操作分類
    operation VARCHAR(100),                                  -- 操作内容、既存システム互換、操作分類
    activity_type ENUM('login', 'logout', 'battle_start', 'battle_end', 'achievement', 'ranking_update') NOT NULL, -- アクティビティ種別、分類・集計、監査
    activity_data JSON NULL,                                 -- アクティビティ詳細、柔軟なデータ保存、後方互換性
    details TEXT,                                            -- 操作詳細、既存システム互換、監査ログ
    ip_address VARCHAR(45),                                  -- アクティビティ発生元IP、セキュリティ監査、不正アクセス検知
    user_agent VARCHAR(255),                                 -- ブラウザ情報、デバイス識別、セキュリティ監査
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,           -- アクティビティ発生時刻、時系列分析、監査ログ
    operated_at DATETIME DEFAULT CURRENT_TIMESTAMP,           -- 操作時刻、既存システム互換、監査ログ
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL, -- ユーザー削除時はNULL保持（監査ログ維持）
    INDEX idx_user_id (user_id),                             -- ユーザー別アクティビティ検索、監査ログ
    INDEX idx_activity_type (activity_type),                 -- アクティビティ種別検索、統計分析
    INDEX idx_created_at (created_at),                       -- 時系列検索、履歴管理、統計分析
    INDEX idx_operation_code (operation_code)                -- 操作コード別検索、既存システム互換
);

-- システム統計
CREATE TABLE system_stats (
    stat_id VARCHAR(100) PRIMARY KEY,                        -- 統計識別子、統計管理、更新
    stat_date DATE NOT NULL,                                 -- 統計対象日、日次集計、履歴管理
    total_users INT DEFAULT 0,                               -- 総ユーザー数、成長率計算、KPI管理
    active_users INT DEFAULT 0,                              -- アクティブユーザー数、エンゲージメント測定、KPI管理
    total_battles INT DEFAULT 0,                             -- 総バトル数、ゲーム活性度測定、KPI管理
    total_rounds INT DEFAULT 0,                              -- 総ラウンド数、ゲーム活性度測定、統計分析
    average_battle_duration_seconds INT DEFAULT 0,           -- 平均バトル時間、パフォーマンス監視、ユーザー体験分析
    peak_concurrent_users INT DEFAULT 0,                     -- ピーク同時接続数、インフラ容量計画、スケーリング判断
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,           -- レコード作成時刻、履歴管理、監査
    UNIQUE KEY unique_daily_stat (stat_date),                -- 日次重複防止、データ整合性
    INDEX idx_stat_date (stat_date)                          -- 日別統計検索、履歴管理、分析
);

-- =====================================================
-- 5. 初期データ挿入
-- =====================================================

-- システム設定
INSERT INTO system_settings (setting_key, setting_value, description) VALUES
('max_concurrent_battles', '100', '同時実行可能なバトル数（Redis接続プール制限）'),
('battle_timeout_seconds', '300', 'バトルセッションのタイムアウト時間（秒）（WebSocket接続管理）'),
('magic_link_expiry_minutes', '15', 'Magic Linkの有効期限（分）（セキュリティ・ユーザビリティ）'),
('jwt_access_token_expiry_minutes', '15', 'JWTアクセストークンの有効期限（分）（セキュリティ・パフォーマンス）'),
('jwt_refresh_token_expiry_days', '30', 'JWTリフレッシュトークンの有効期限（日）（ユーザビリティ・セキュリティ）'),
('session_timeout_minutes', '60', 'セッションタイムアウト（分）（セキュリティ・リソース管理）'),
('max_concurrent_sessions_per_user', '5', 'ユーザーあたりの最大同時セッション数（セキュリティ・リソース制限）'),
('max_login_attempts_per_ip', '10', 'IP別最大ログイン試行数（ブルートフォース攻撃対策）'),
('login_attempt_lockout_minutes', '30', 'ログイン試行失敗時のロックアウト時間（分）（セキュリティ）'),
('2fa_required_for_admin', 'true', '管理者に2FA必須化（セキュリティ強化）'),
('oauth_providers_enabled', 'google,line,apple', '有効化するOAuthプロバイダー（認証方式管理）');

-- テストユーザー
INSERT INTO users (user_id, email, nickname, role, title, alias) VALUES
('test_user_1', 'test1@example.com', 'テストユーザー1', 'developer', 'テストプレイヤー', 'じゃんけんテスター1'),
('test_user_2', 'test2@example.com', 'テストユーザー2', 'developer', 'テストプレイヤー', 'じゃんけんテスター2'),
('test_user_3', 'test3@example.com', 'テストユーザー3', 'developer', 'テストプレイヤー', 'じゃんけんテスター3'),
('test_user_4', 'test4@example.com', 'テストユーザー4', 'developer', 'テストプレイヤー', 'じゃんけんテスター4'),
('test_user_5', 'test5@example.com', 'テストユーザー5', 'developer', 'テストプレイヤー', 'じゃんけんテスター5');

-- ユーザー統計初期化
INSERT INTO user_stats (user_id) VALUES
('test_user_1'), ('test_user_2'), ('test_user_3'), ('test_user_4'), ('test_user_5');

-- =====================================================
-- 6. ビュー作成
-- =====================================================

-- ユーザー認証状態サマリー（拡張版）
CREATE VIEW user_auth_summary AS
SELECT 
    u.management_code,                                       -- 管理コード、既存システム互換
    u.user_id,                                               -- ユーザー識別子、管理画面表示
    u.email,                                                 -- メールアドレス、管理画面表示
    u.nickname,                                              -- ニックネーム、管理画面表示
    u.name,                                                  -- 実名、管理画面表示
    u.role,                                                  -- 権限、管理画面表示・制御
    u.is_active,                                             -- アカウント状態、管理画面表示・制御
    u.is_banned,                                             -- BAN状態、既存システム互換、管理画面制御
    up.university,                                           -- 大学名、管理画面表示
    up.phone_number,                                         -- 電話番号、管理画面表示
    ac.is_password_enabled,                                  -- パスワード認証有効化状態、管理画面表示
    tfa.enabled as two_factor_enabled,                       -- 2FA有効化状態、管理画面表示
    COUNT(s.session_id) as active_sessions,                  -- アクティブセッション数、管理画面表示・制御
    u.created_at,                                            -- アカウント作成日時、管理画面表示
    u.updated_at                                             -- 最終更新日時、管理画面表示
FROM users u
LEFT JOIN user_profiles up ON u.user_id = up.user_id
LEFT JOIN auth_credentials ac ON u.user_id = ac.user_id
LEFT JOIN two_factor_auth tfa ON u.user_id = tfa.user_id
LEFT JOIN sessions s ON u.user_id = s.user_id AND s.is_revoked = FALSE
GROUP BY u.management_code, u.user_id, u.email, u.nickname, u.name, u.role, u.is_active, u.is_banned, 
         up.university, up.phone_number, ac.is_password_enabled, tfa.enabled, u.created_at, u.updated_at;

-- セッション状態ビュー（拡張版）
CREATE VIEW active_sessions_view AS
SELECT 
    s.session_id,                                            -- セッション識別子、管理画面表示・制御
    s.user_id,                                               -- ユーザーID、管理画面表示・制御
    u.nickname,                                              -- ユーザー名、管理画面表示
    s.device_id,                                             -- 端末識別子、管理画面表示・制御
    ud.device_name,                                          -- 端末名、管理画面表示
    ud.itemtype,                                             -- 端末種別、管理画面表示
    s.ip_address,                                            -- IPアドレス、管理画面表示・セキュリティ監査
    s.user_agent,                                            -- ブラウザ情報、管理画面表示・セキュリティ監査
    s.created_at,                                            -- セッション作成時刻、管理画面表示
    s.last_seen_at,                                          -- 最終アクセス時刻、管理画面表示・タイムアウト判定
    TIMESTAMPDIFF(MINUTE, s.last_seen_at, NOW()) as minutes_since_last_seen -- 最終アクセスからの経過時間、管理画面表示・タイムアウト判定
FROM sessions s
JOIN users u ON s.user_id = u.user_id
JOIN user_devices ud ON s.device_id = ud.device_id
WHERE s.is_revoked = FALSE
ORDER BY s.last_seen_at DESC;

-- ユーザー統計サマリービュー（既存システム互換）
CREATE VIEW user_stats_summary AS
SELECT 
    u.management_code,                                       -- 管理コード、既存システム互換
    u.user_id,                                               -- ユーザー識別子、管理画面表示
    u.nickname,                                              -- ニックネーム、管理画面表示
    u.email,                                                 -- メールアドレス、管理画面表示
    u.title,                                                 -- 称号、管理画面表示
    u.alias,                                                 -- 別名、管理画面表示
    us.total_matches,                                        -- 総試合数、管理画面表示
    us.total_wins,                                           -- 総勝利数、管理画面表示
    us.total_losses,                                         -- 総敗北数、管理画面表示
    us.total_draws,                                          -- 総引き分け数、管理画面表示
    us.win_rate,                                             -- 勝率、管理画面表示
    us.current_streak,                                       -- 現在の連勝数、管理画面表示
    us.best_streak,                                          -- 最高連勝数、管理画面表示
    us.rock_count,                                           -- グー使用回数、管理画面表示
    us.paper_count,                                          -- パー使用回数、管理画面表示
    us.scissors_count,                                       -- チョキ使用回数、管理画面表示
    us.favorite_hand,                                        -- お気に入りの手、管理画面表示
    us.last_battle_at,                                       -- 最終バトル時刻、管理画面表示
    us.user_rank,                                            -- ユーザーランク、管理画面表示
    us.last_reset_at                                         -- 最終リセット日、管理画面表示
FROM users u
LEFT JOIN user_stats us ON u.user_id = us.user_id
WHERE u.is_active = TRUE;

-- 今日のランキングビュー（既存システム互換）
CREATE VIEW today_rankings AS
SELECT 
    dr.ranking_position,                                     -- 順位、ランキング表示
    u.nickname,                                              -- ユーザー名、ランキング表示
    u.title,                                                 -- 称号、ランキング表示
    dr.daily_wins,                                           -- 日次勝利数、ランキング表示
    dr.daily_matches,                                        -- 日次試合数、ランキング表示
    dr.daily_win_rate,                                       -- 日次勝率、ランキング表示
    dr.last_win_at                                           -- 最終勝利時刻、ランキング表示
FROM daily_rankings dr
JOIN users u ON dr.user_id = u.user_id
WHERE dr.ranking_date = CURDATE()
ORDER BY dr.ranking_position;

-- 今週のランキングビュー
CREATE VIEW this_week_rankings AS
SELECT 
    wr.rank_position,                                        -- 順位、ランキング表示
    u.nickname,                                              -- ユーザー名、ランキング表示
    u.title,                                                 -- 称号、ランキング表示
    wr.weekly_wins,                                          -- 週次勝利数、ランキング表示
    wr.weekly_matches,                                       -- 週次試合数、ランキング表示
    wr.weekly_win_rate                                       -- 週次勝率、ランキング表示
FROM weekly_rankings wr
JOIN users u ON wr.user_id = u.user_id
WHERE wr.ranking_week = DATE_SUB(CURDATE(), INTERVAL WEEKDAY(CURDATE()) DAY)
ORDER BY wr.rank_position;

-- バトル履歴ビュー（既存システム互換）
CREATE VIEW battle_history AS
SELECT 
    br.battle_id,                                            -- バトル識別子、履歴表示
    br.fight_no,                                             -- 戦闘番号、既存システム互換
    p1.nickname as player1_nickname,                         -- プレイヤー1名、履歴表示
    p2.nickname as player2_nickname,                         -- プレイヤー2名、履歴表示
    winner.nickname as winner_nickname,                       -- 勝者名、履歴表示
    br.total_rounds,                                         -- 総ラウンド数、履歴表示
    br.player1_wins,                                         -- プレイヤー1勝利数、履歴表示
    br.player2_wins,                                         -- プレイヤー2勝利数、履歴表示
    br.draws,                                                -- 引き分け数、履歴表示
    br.battle_duration_seconds,                              -- バトル時間、履歴表示
    br.match_type,                                           -- マッチング種別、履歴表示
    br.started_at,                                           -- 開始時刻、履歴表示
    br.finished_at                                            -- 終了時刻、履歴表示
FROM battle_results br
JOIN users p1 ON br.player1_id = p1.user_id
JOIN users p2 ON br.player2_id = p2.user_id
LEFT JOIN users winner ON br.winner_id = winner.user_id
ORDER BY br.created_at DESC;

-- セキュリティ監査ビュー
CREATE VIEW security_audit_summary AS
SELECT 
    se.event_type,                                           -- イベント種別、監査分析
    se.user_id,                                              -- 対象ユーザー、監査分析
    u.nickname,                                              -- ユーザー名、監査分析
    se.ip_address,                                           -- IPアドレス、監査分析
    DATE(se.created_at) as event_date,                       -- イベント日、監査分析
    COUNT(*) as event_count                                  -- イベント数、監査分析
FROM security_events se
LEFT JOIN users u ON se.user_id = u.user_id
WHERE se.created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
GROUP BY se.event_type, se.user_id, u.nickname, se.ip_address, DATE(se.created_at)
ORDER BY event_date DESC, event_count DESC;

-- ログイン試行監視ビュー
CREATE VIEW login_attempt_monitoring AS
SELECT 
    la.ip_address,                                           -- IPアドレス、監視対象
    la.user_id,                                              -- 対象ユーザー、監視対象
    u.nickname,                                              -- ユーザー名、監視対象
    la.success,                                              -- 成功・失敗、監視対象
    la.failure_reason,                                       -- 失敗理由、監視対象
    DATE_FORMAT(la.attempt_time, '%Y-%m-%d %H:%i') as attempt_hour, -- 試行時間（時間単位）、監視対象
    COUNT(*) as attempt_count                                -- 試行回数、監視対象
FROM login_attempts la
LEFT JOIN users u ON la.user_id = u.user_id
WHERE la.attempt_time >= DATE_SUB(NOW(), INTERVAL 1 HOUR)
GROUP BY la.ip_address, la.user_id, u.nickname, la.success, la.failure_reason, 
         DATE_FORMAT(la.attempt_time, '%Y-%m-%d %H:%i')
ORDER BY attempt_count DESC, attempt_hour DESC;

-- =====================================================
-- 7. インデックス最適化
-- =====================================================

-- 複合インデックス（パフォーマンス向上）
-- 注意: UNIQUE KEYで既に作成されているインデックスは重複しないよう調整
CREATE INDEX idx_refresh_tokens_session_expires ON refresh_tokens(session_id, expires_at); -- セッション・期限別トークン検索高速化
CREATE INDEX idx_magic_link_email_expires ON magic_link_tokens(email, expires_at); -- メール・期限別トークン検索高速化
CREATE INDEX idx_security_events_user_type ON security_events(user_id, event_type); -- ユーザー・イベント種別検索高速化
CREATE INDEX idx_battle_results_players_created ON battle_results(player1_id, player2_id, created_at); -- プレイヤー・作成日別バトル検索高速化
CREATE INDEX idx_user_stats_win_rate_matches ON user_stats(win_rate DESC, total_matches DESC); -- 勝率・試合数別統計検索高速化
CREATE INDEX idx_battle_rounds_battle_round ON battle_rounds(battle_id, round_number); -- バトル・ラウンド別検索高速化
CREATE INDEX idx_activity_logs_user_type_date ON activity_logs(user_id, activity_type, created_at); -- ユーザー・種別・日時別ログ検索高速化
CREATE INDEX idx_admin_logs_admin_target_time ON admin_logs(admin_user, target_id, operated_at); -- 管理者・対象・時刻別ログ検索高速化
CREATE INDEX idx_login_attempts_ip_time ON login_attempts(ip_address, attempt_time); -- IP・時刻別ログイン試行検索高速化

-- =====================================================
-- 8. データ同期フロー設計
-- =====================================================

/*
認証・セッション管理フロー（既存システム統合版）：

1. Magic Link認証
   - メール入力 → magic_link_tokensに保存（セキュリティ・監査）
   - リンククリック → 検証 → ユーザー作成/認証（セキュリティ・ユーザビリティ）
   - セッション作成 → Redis + DB両方に保存（パフォーマンス・永続化）

2. JWT認証
   - アクセストークン: 短命（15分）、Redisで検証（パフォーマンス・セキュリティ）
   - リフレッシュトークン: 長命（30日）、DBで管理（永続化・セキュリティ）
   - トークンローテーション: 旧トークンをブラックリスト化（セキュリティ・監査）

3. セッション管理
   - Redis: リアルタイム接続状態、WebSocket管理（パフォーマンス・リアルタイム性）
   - DB: 永続化セッション情報、監査ログ（永続化・監査）
   - 定期的な同期: Redis → DB（統計・ログ・データ整合性）

4. セキュリティ
   - セッション無効化: DB更新 → Redis削除（セキュリティ・データ整合性）
   - トークン失効: JWTブラックリスト + Redis削除（セキュリティ・即時対応）
   - 監査ログ: 全認証イベントをDBに記録（監査・コンプライアンス・セキュリティ）

5. 既存システム互換性
   - management_code: 既存システムとの連携維持
   - テーブル構造: 既存クエリとの互換性保持
   - データ型: 既存アプリケーションとの互換性維持

Redis管理データ（リアルタイム・一時的）：
- セッション状態: session:{session_id}（WebSocket接続管理・認証状態）
- WebSocket接続: websocket:{user_id}（リアルタイム通信・接続状態）
- アクティブユーザー: user:active:{user_id}（オンライン状態・統計）
- マッチングキュー: match_queue（リアルタイムマッチング・待機状態）
- リアルタイム統計: stats:user:{user_id}（キャッシュ・パフォーマンス）

DB管理データ（永続化・履歴・既存システム互換）：
- ユーザー基本情報（認証・管理・統計・既存システム互換）
- ユーザー詳細情報（個人情報・学生情報・本人確認）
- 認証資格情報（セキュリティ・認証方式管理）
- 端末管理（複数端末対応・セキュリティ制御）
- セッション履歴（監査・セキュリティ・分析）
- トークン管理（セキュリティ・監査・失効管理）
- 2要素認証（TOTP・セキュリティ強化）
- OAuth連携（将来的な外部認証対応）
- 統計・ランキング（分析・実績・KPI・既存システム互換）
- 監査ログ（コンプライアンス・セキュリティ・運用・既存システム互換）
- 管理ログ（管理者操作・監査・セキュリティ）

データ移行・統合フロー：
1. 既存システムデータの読み込み
2. 新テーブル構造への変換・移行
3. データ整合性の検証
4. 段階的な切り替え
5. 旧システムの廃止・クリーンアップ
*/

-- =====================================================
-- 9. データ移行・互換性維持のためのヘルパー関数
-- =====================================================

-- 既存システムからのデータ移行用ビュー
CREATE VIEW legacy_compatibility AS
SELECT 
    u.management_code,                                       -- 既存システム互換用管理コード
    u.user_id,                                               -- 新システム用ユーザーID
    u.email,                                                 -- メールアドレス
    u.nickname,                                              -- ニックネーム
    u.name,                                                  -- 実名
    u.is_banned,                                             -- BAN状態
    up.university,                                           -- 大学名
    up.phone_number,                                         -- 電話番号
    up.postal_code,                                          -- 郵便番号
    up.address,                                              -- 住所
    up.birthdate,                                            -- 生年月日
    up.student_id_image_url,                                 -- 学生証画像
    us.total_wins,                                           -- 総勝利数
    us.total_losses,                                         -- 総敗北数
    us.win_rate,                                             -- 勝率
    us.user_rank,                                            -- ユーザーランク
    u.created_at,                                            -- 作成日時
    u.updated_at                                             -- 更新日時
FROM users u
LEFT JOIN user_profiles up ON u.user_id = up.user_id
LEFT JOIN user_stats us ON u.user_id = us.user_id;

-- =====================================================
-- 完了メッセージ
-- =====================================================

SELECT 'じゃんけんDBテーブル作成完了' AS status;                                 