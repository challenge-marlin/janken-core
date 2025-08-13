# データベース仕様書（完全認証システム統合版）

## 概要

本システムはMySQLデータベースを使用し、**Magic Link + JWT + パスワード（任意）**の併用認証システムを採用しています。
既存のじゃんけんゲーム機能との完全な互換性を保ちながら、最新のセキュリティ要件を満たす認証基盤を提供します。

### 主要な特徴
- **Magic Link認証**: パスワードレス認証をメイン方式として採用
- **JWT認証**: アクセストークン（15分）+ リフレッシュトークン（30日）の組み合わせ
- **パスワード認証**: 非常口として任意で設定可能
- **Redis連携**: リアルタイム処理とセッション管理
- **マルチデバイス対応**: 端末ごとの細かいセッション制御
- **セキュリティ強化**: 2FA、レート制限、ブルートフォース対策

---

## テーブル一覧

### 🔐 認証・セッション管理
| テーブル名 | 用途 | 重要度 |
|-----------|------|--------|
| `users` | ユーザー基本情報 | ⭐⭐⭐ |
| `user_profiles` | ユーザー詳細プロフィール | ⭐⭐ |
| `auth_credentials` | パスワード認証情報 | ⭐⭐ |
| `user_devices` | 端末管理 | ⭐⭐ |
| `magic_link_tokens` | Magic Link認証トークン | ⭐⭐⭐ |
| `sessions` | セッション管理 | ⭐⭐⭐ |
| `refresh_tokens` | リフレッシュトークン管理 | ⭐⭐⭐ |
| `jwt_blacklist` | JWT即時失効管理 | ⭐⭐ |
| `two_factor_auth` | 2要素認証設定 | ⭐⭐ |
| `oauth_accounts` | OAuth連携（将来用） | ⭐ |

### 🛡️ セキュリティ・監査
| テーブル名 | 用途 | 重要度 |
|-----------|------|--------|
| `login_attempts` | ログイン試行記録 | ⭐⭐⭐ |
| `security_events` | セキュリティイベント記録 | ⭐⭐⭐ |
| `admin_logs` | 管理者操作ログ | ⭐⭐ |

### 🎮 ゲーム機能
| テーブル名 | 用途 | 重要度 |
|-----------|------|--------|
| `battle_results` | バトル結果記録 | ⭐⭐⭐ |
| `battle_rounds` | バトルラウンド詳細 | ⭐⭐ |
| `user_stats` | ユーザー統計 | ⭐⭐⭐ |
| `daily_rankings` | 日次ランキング | ⭐⭐ |
| `weekly_rankings` | 週次ランキング | ⭐⭐ |

### ⚙️ システム管理
| テーブル名 | 用途 | 重要度 |
|-----------|------|--------|
| `system_settings` | システム設定 | ⭐⭐ |
| `activity_logs` | アクティビティログ | ⭐⭐ |
| `system_stats` | システム統計 | ⭐ |

---

## 認証・セッション管理テーブル詳細

### 1. users（ユーザー基本情報）⭐⭐⭐

**用途**: 認証システムの中核となるユーザー基本情報管理

| カラム名 | 物理名 | 型 | NULL許可 | デフォルト | 説明・用途 |
|---------|--------|-----|----------|------------|------------|
| 管理コード | management_code | BIGINT AUTO_INCREMENT | NO | | 既存システム互換用、内部管理・連携 |
| ユーザーID | user_id | VARCHAR(50) | NO (PK) | | JWTのsubクレーム、セッション管理、外部キー参照用 |
| メールアドレス | email | VARCHAR(255) | NO (UNIQUE) | | Magic Link送信先、ログイン識別子、重複防止 |
| ニックネーム | nickname | VARCHAR(100) | NO | | ゲーム内表示名、ランキング表示 |
| 権限レベル | role | ENUM | NO | 'user' | アクセス制御、機能制限（user/developer/admin） |
| アクティブ状態 | is_active | BOOLEAN | NO | TRUE | アカウント有効性、BANユーザー管理 |
| 作成日時 | created_at | TIMESTAMP | NO | CURRENT_TIMESTAMP | アカウント作成日時、統計・監査用 |
| 更新日時 | updated_at | TIMESTAMP | NO | CURRENT_TIMESTAMP | 最終更新日時、アクティビティ監視 |

#### インデックス
- **PRIMARY KEY**: user_id
- **UNIQUE KEY**: management_code, email
- **INDEX**: role, is_active, created_at

#### 特記事項
- Magic Link認証では`email`が主要な識別子
- `management_code`は既存システムとの互換性維持用
- `user_id`はJWTトークンの`sub`クレームとして使用

---

### 2. user_profiles（ユーザー詳細プロフィール）⭐⭐

**用途**: ユーザーの詳細情報管理（個人情報含む）

| カラム名 | 物理名 | 型 | NULL許可 | デフォルト | 説明・用途 |
|---------|--------|-----|----------|------------|------------|
| ユーザーID | user_id | VARCHAR(50) | NO (PK) | | users.user_idとの紐付け |
| 実名 | full_name | VARCHAR(100) | YES | | 本人確認、公的手続き用 |
| 電話番号 | phone_number | VARCHAR(15) | YES | | 連絡先、緊急時連絡用 |
| 郵便番号 | postal_code | VARCHAR(10) | YES | | 住所情報、配送・統計用 |
| 住所 | address | VARCHAR(255) | YES | | 住所情報、配送・統計用 |
| 生年月日 | birthdate | DATE | YES | | 年齢制限、統計分析用 |
| 学校名 | university | VARCHAR(100) | YES | | 学生認証、コミュニティ機能用 |
| プロフィール画像 | profile_image_url | VARCHAR(500) | YES | | アバター表示、個性化 |
| 学生証画像 | student_id_image_url | VARCHAR(500) | YES | | 学生認証、本人確認用 |
| 学生証編集可否 | is_student_id_editable | BOOLEAN | NO | FALSE | 編集制御、不正防止 |
| タイトル | title | VARCHAR(100) | YES | | ゲーム内称号、達成感演出 |
| 別名 | alias | VARCHAR(100) | YES | | ニックネーム補完、個性化 |

#### 外部キー
- **user_id** → users(user_id) ON DELETE CASCADE

---

### 3. auth_credentials（パスワード認証情報）⭐⭐

**用途**: パスワード認証の資格情報管理（任意設定）

| カラム名 | 物理名 | 型 | NULL許可 | デフォルト | 説明・用途 |
|---------|--------|-----|----------|------------|------------|
| ユーザーID | user_id | VARCHAR(50) | NO (PK) | | users.user_idとの紐付け |
| パスワードハッシュ | password_hash | VARCHAR(255) | YES | | Argon2idハッシュ値、認証時検証用 |
| ハッシュアルゴリズム | password_algo | ENUM | NO | 'argon2id' | 将来のアルゴリズム移行対応 |
| パスワードバージョン | password_version | SMALLINT | NO | 1 | ハッシュ強度変更履歴管理 |
| パスワード更新日時 | password_updated_at | TIMESTAMP | YES | | 最終パスワード変更日時、強制変更判定 |
| パスワード有効化 | is_password_enabled | BOOLEAN | NO | FALSE | パスワード認証の有効無効制御 |

#### 外部キー
- **user_id** → users(user_id) ON DELETE CASCADE

#### 特記事項
- Magic Link主体でも「非常口」として有効化可能
- パスワード未設定でも`is_password_enabled=FALSE`で運用可能

---

### 4. user_devices（端末管理）⭐⭐

**用途**: ユーザーの利用端末情報管理とセッション制御

| カラム名 | 物理名 | 型 | NULL許可 | デフォルト | 説明・用途 |
|---------|--------|-----|----------|------------|------------|
| デバイスID | device_id | VARCHAR(100) | NO (PK) | | 端末一意識別子、セッション管理用 |
| ユーザーID | user_id | VARCHAR(50) | NO | | users.user_idとの紐付け |
| デバイス名 | device_name | VARCHAR(100) | YES | | ユーザー設定の端末名、管理画面表示用 |
| デバイス種別 | device_type | ENUM | NO | 'unknown' | 端末種別識別、UI最適化用 |
| OS情報 | os_info | VARCHAR(100) | YES | | OS詳細情報、互換性確認用 |
| ブラウザ情報 | browser_info | VARCHAR(100) | YES | | ブラウザ詳細、機能対応確認用 |
| 信頼済み | is_trusted | BOOLEAN | NO | FALSE | 信頼済み端末、2FA省略判定用 |
| アクティブ | is_active | BOOLEAN | NO | TRUE | 端末有効性、利用制御用 |
| 最終アクセス | last_accessed_at | TIMESTAMP | YES | | 最終アクセス日時、非アクティブ端末検知 |

#### インデックス
- **INDEX**: user_id, device_type, is_active, last_accessed_at

---

### 5. magic_link_tokens（Magic Link認証トークン）⭐⭐⭐

**用途**: Magic Link認証のワンタイムトークン管理

| カラム名 | 物理名 | 型 | NULL許可 | デフォルト | 説明・用途 |
|---------|--------|-----|----------|------------|------------|
| トークンハッシュ | token_hash | VARCHAR(128) | NO (PK) | | SHA-256ハッシュ値、改ざん防止・検索用 |
| メールアドレス | email | VARCHAR(255) | NO | | 送信先メール、ユーザー識別用 |
| ユーザーID | user_id | VARCHAR(50) | YES | | 既存ユーザーの場合の紐付け |
| 発行日時 | issued_at | DATETIME | NO | | トークン生成日時、監査・統計用 |
| 有効期限 | expires_at | DATETIME | NO | | 15分後設定、セキュリティ確保 |
| 使用日時 | used_at | DATETIME | YES | | 使用済み日時、ワンタイム制御用 |
| IPアドレス | ip_address | VARCHAR(45) | YES | | 発行元IP、不正検知用 |
| ユーザーエージェント | user_agent | VARCHAR(255) | YES | | 発行環境情報、異常検知用 |

#### インデックス
- **PRIMARY KEY**: token_hash
- **INDEX**: email, expires_at, user_id

#### 特記事項
- トークンは15分間有効（`expires_at`）
- ワンタイム使用（`used_at`更新で無効化）
- DBには生トークンではなくハッシュ値のみ保存

---

### 6. sessions（セッション管理）⭐⭐⭐

**用途**: 端末ごとのセッション状態管理と制御

| カラム名 | 物理名 | 型 | NULL許可 | デフォルト | 説明・用途 |
|---------|--------|-----|----------|------------|------------|
| セッションID | session_id | VARCHAR(100) | NO (PK) | | セッション一意識別子、Redis連携用 |
| ユーザーID | user_id | VARCHAR(50) | NO | | users.user_idとの紐付け |
| デバイスID | device_id | VARCHAR(100) | NO | | 端末識別、同時ログイン制御用 |
| IPアドレス | ip_address | VARCHAR(45) | YES | | アクセス元IP、セキュリティ監視用 |
| ユーザーエージェント | user_agent | VARCHAR(255) | YES | | ブラウザ情報、環境識別用 |
| 作成日時 | created_at | TIMESTAMP | NO | CURRENT_TIMESTAMP | セッション開始日時 |
| 最終アクセス | last_seen_at | TIMESTAMP | YES | | 最終活動日時、非アクティブ検知 |
| 失効フラグ | is_revoked | BOOLEAN | NO | FALSE | セッション無効化、強制ログアウト用 |

#### インデックス
- **UNIQUE KEY**: (user_id, device_id) - 台数制限・重複防止
- **INDEX**: user_id, device_id, last_seen_at

---

### 7. refresh_tokens（リフレッシュトークン管理）⭐⭐⭐

**用途**: JWTリフレッシュトークンの管理と回転制御

| カラム名 | 物理名 | 型 | NULL許可 | デフォルト | 説明・用途 |
|---------|--------|-----|----------|------------|------------|
| トークンID | token_id | VARCHAR(100) | NO (PK) | | サーバー生成ID、JTI相当、ローテーション管理用 |
| セッションID | session_id | VARCHAR(100) | NO | | sessions.session_idとの紐付け |
| トークンハッシュ | token_hash | VARCHAR(255) | NO | | ハッシュ化されたトークン値、検証用 |
| 発行日時 | issued_at | DATETIME | NO | | トークン発行日時、監査用 |
| 有効期限 | expires_at | DATETIME | NO | | 30〜90日後設定、長期認証用 |
| 回転元ID | rotated_from | VARCHAR(100) | YES | | 旧トークンID、ローテーション履歴追跡 |
| 失効フラグ | is_revoked | BOOLEAN | NO | FALSE | 失効状態、セキュリティ制御用 |

#### インデックス
- **UNIQUE KEY**: token_hash
- **INDEX**: session_id, expires_at, is_revoked

#### 特記事項
- 「回転式」トークン採用（使用時に新しいトークンを発行）
- `rotated_from`でローテーション履歴を追跡可能

---

## セキュリティ・監査テーブル詳細

### 8. login_attempts（ログイン試行記録）⭐⭐⭐

**用途**: ログイン試行の記録とブルートフォース攻撃対策

| カラム名 | 物理名 | 型 | NULL許可 | デフォルト | 説明・用途 |
|---------|--------|-----|----------|------------|------------|
| 試行ID | attempt_id | BIGINT AUTO_INCREMENT | NO (PK) | | 試行一意識別子 |
| ユーザーID | user_id | VARCHAR(50) | YES | | 対象ユーザー（存在しない場合はNULL） |
| メールアドレス | email | VARCHAR(255) | NO | | 試行されたメールアドレス |
| 認証方式 | auth_method | ENUM | NO | | 認証方式（magic_link/password/2fa） |
| IPアドレス | ip_address | VARCHAR(45) | NO | | アクセス元IP、レート制限用 |
| 成功フラグ | success | BOOLEAN | NO | FALSE | 認証成功・失敗 |
| 失敗理由 | failure_reason | ENUM | YES | | 失敗理由詳細 |
| ユーザーエージェント | user_agent | VARCHAR(255) | YES | | ブラウザ情報 |
| 試行日時 | attempted_at | TIMESTAMP | NO | CURRENT_TIMESTAMP | 試行日時 |

#### インデックス
- **INDEX**: user_id, email, ip_address, attempted_at

---

### 9. security_events（セキュリティイベント記録）⭐⭐⭐

**用途**: セキュリティ関連イベントの記録と監査

| カラム名 | 物理名 | 型 | NULL許可 | デフォルト | 説明・用途 |
|---------|--------|-----|----------|------------|------------|
| イベントID | event_id | BIGINT AUTO_INCREMENT | NO (PK) | | イベント一意識別子 |
| ユーザーID | user_id | VARCHAR(50) | YES | | 関連ユーザー（システムイベントはNULL） |
| イベントタイプ | event_type | ENUM | NO | | イベント種別詳細 |
| 重要度 | severity | ENUM | NO | 'info' | イベント重要度（low/medium/high/critical） |
| IPアドレス | ip_address | VARCHAR(45) | YES | | 関連IPアドレス |
| デバイス情報 | device_info | JSON | YES | | 端末詳細情報 |
| イベント詳細 | event_details | JSON | YES | | 追加情報・コンテキスト |
| 作成日時 | created_at | TIMESTAMP | NO | CURRENT_TIMESTAMP | イベント発生日時 |

#### イベントタイプ一覧
- `magic_link_issued`: Magic Link発行
- `magic_link_used`: Magic Link使用
- `login_success`: ログイン成功
- `login_failed`: ログイン失敗
- `password_set`: パスワード設定
- `password_reset`: パスワードリセット
- `session_revoked`: セッション失効
- `token_rotated`: トークンローテーション
- `2fa_enabled`: 2FA有効化
- `2fa_disabled`: 2FA無効化
- `suspicious_activity`: 不審なアクティビティ

---

## ゲーム機能テーブル詳細

### 10. battle_results（バトル結果記録）⭐⭐⭐

**用途**: じゃんけんバトルの結果記録と統計データ管理

| カラム名 | 物理名 | 型 | NULL許可 | デフォルト | 説明・用途 |
|---------|--------|-----|----------|------------|------------|
| 戦闘番号 | fight_no | BIGINT AUTO_INCREMENT | NO | | 既存システム互換用、内部管理 |
| バトルID | battle_id | VARCHAR(100) | NO (PK) | | バトル一意識別子、Redis連携用 |
| プレイヤー1ID | player1_id | VARCHAR(50) | NO | | 参加者1のユーザーID |
| プレイヤー2ID | player2_id | VARCHAR(50) | NO | | 参加者2のユーザーID |
| 勝者ID | winner_id | VARCHAR(50) | YES | | 勝利者のユーザーID（引き分けはNULL） |
| 総ラウンド数 | total_rounds | INT | NO | 0 | 実行されたラウンド数 |
| プレイヤー1勝利数 | player1_wins | INT | NO | 0 | プレイヤー1の勝利ラウンド数 |
| プレイヤー2勝利数 | player2_wins | INT | NO | 0 | プレイヤー2の勝利ラウンド数 |
| 引き分け数 | draws | INT | NO | 0 | 引き分けラウンド数 |
| バトル形式 | battle_type | ENUM | NO | 'standard' | バトル種別（standard/tournament/friend） |
| 開始日時 | started_at | TIMESTAMP | YES | | バトル開始日時 |
| 終了日時 | finished_at | TIMESTAMP | YES | | バトル終了日時 |
| 作成日時 | created_at | TIMESTAMP | NO | CURRENT_TIMESTAMP | レコード作成日時 |

#### 外部キー
- **player1_id** → users(user_id) ON DELETE CASCADE
- **player2_id** → users(user_id) ON DELETE CASCADE
- **winner_id** → users(user_id) ON DELETE SET NULL

---

### 11. user_stats（ユーザー統計）⭐⭐⭐

**用途**: ユーザーの対戦成績と統計情報管理

| カラム名 | 物理名 | 型 | NULL許可 | デフォルト | 説明・用途 |
|---------|--------|-----|----------|------------|------------|
| ユーザーID | user_id | VARCHAR(50) | NO (PK) | | users.user_idとの紐付け |
| 総試合数 | total_matches | INT | NO | 0 | 参加した総試合数 |
| 総勝利数 | total_wins | INT | NO | 0 | 勝利した試合数 |
| 総敗北数 | total_losses | INT | NO | 0 | 敗北した試合数 |
| 総引き分け数 | total_draws | INT | NO | 0 | 引き分けた試合数 |
| 勝率 | win_rate | DECIMAL(5,2) | NO | 0.00 | 勝率（％）、ランキング用 |
| 現在連勝数 | current_streak | INT | NO | 0 | 現在の連勝記録 |
| 最高連勝数 | best_streak | INT | NO | 0 | 過去最高の連勝記録 |
| グー使用回数 | rock_count | INT | NO | 0 | グーを出した回数 |
| パー使用回数 | paper_count | INT | NO | 0 | パーを出した回数 |
| チョキ使用回数 | scissors_count | INT | NO | 0 | チョキを出した回数 |
| お気に入りの手 | favorite_hand | ENUM | YES | | 最も多く使用する手 |
| 直近戦績 | recent_results | VARCHAR(255) | NO | '' | 直近5戦の結果文字列 |
| 当日勝利数 | daily_wins | INT | NO | 0 | 当日の勝利数（日次リセット） |
| 当日敗北数 | daily_losses | INT | NO | 0 | 当日の敗北数（日次リセット） |
| 当日引き分け数 | daily_draws | INT | NO | 0 | 当日の引き分け数（日次リセット） |
| 称号 | title | VARCHAR(50) | NO | '' | 現在の表示称号 |
| 獲得称号一覧 | available_titles | VARCHAR(255) | NO | '' | 獲得済み称号のCSV |
| 二つ名 | alias | VARCHAR(50) | NO | '' | 現在の二つ名 |
| 称号表示設定 | show_title | BOOLEAN | NO | TRUE | 称号の公開設定 |
| 二つ名表示設定 | show_alias | BOOLEAN | NO | TRUE | 二つ名の公開設定 |
| ユーザーランク | user_rank | ENUM | NO | 'no_rank' | ランク（no_rank/bronze/silver/gold/platinum/diamond） |
| 最終リセット日 | last_reset_at | DATE | YES | | 日次統計リセット日 |
| 最終対戦日時 | last_battle_at | TIMESTAMP | YES | | 最後に対戦した日時 |
| 更新日時 | updated_at | TIMESTAMP | NO | CURRENT_TIMESTAMP | 統計更新日時 |

#### インデックス
- **INDEX**: win_rate DESC, total_matches DESC（ランキング用）
- **INDEX**: user_rank, daily_wins DESC（デイリーランキング用）

---

## ビュー（仮想テーブル）一覧

### 1. user_auth_summary（ユーザー認証サマリー）
**用途**: ユーザーの認証設定状況を一覧表示

```sql
SELECT 
    u.user_id,
    u.email,
    u.nickname,
    ac.is_password_enabled,
    tfa.enabled as two_factor_enabled,
    COUNT(s.session_id) as active_sessions,
    u.last_login_at
FROM users u
LEFT JOIN auth_credentials ac ON u.user_id = ac.user_id
LEFT JOIN two_factor_auth tfa ON u.user_id = tfa.user_id
LEFT JOIN sessions s ON u.user_id = s.user_id AND s.is_revoked = FALSE
```

### 2. today_rankings（今日のランキング）
**用途**: 当日のユーザーランキング表示

```sql
SELECT 
    us.user_id,
    u.nickname,
    us.daily_wins,
    us.daily_losses + us.daily_draws as daily_total,
    CASE 
        WHEN (us.daily_wins + us.daily_losses + us.daily_draws) = 0 THEN 0
        ELSE ROUND(us.daily_wins * 100.0 / (us.daily_wins + us.daily_losses + us.daily_draws), 2)
    END as daily_win_rate
FROM user_stats us
JOIN users u ON us.user_id = u.user_id
WHERE us.daily_wins > 0
ORDER BY daily_win_rate DESC, us.daily_wins DESC
```

### 3. battle_history（バトル履歴）
**用途**: バトル履歴の詳細表示

```sql
SELECT 
    br.battle_id,
    p1.nickname as player1_nickname,
    p2.nickname as player2_nickname,
    COALESCE(winner.nickname, '引き分け') as result,
    br.total_rounds,
    br.started_at,
    br.finished_at
FROM battle_results br
JOIN users p1 ON br.player1_id = p1.user_id
JOIN users p2 ON br.player2_id = p2.user_id
LEFT JOIN users winner ON br.winner_id = winner.user_id
ORDER BY br.created_at DESC
```

---

## インデックス設計

### パフォーマンス重視の複合インデックス

| テーブル | インデックス名 | カラム | 用途 |
|---------|---------------|--------|------|
| sessions | idx_sessions_user_device | (user_id, device_id) | ユーザー・端末別セッション検索 |
| refresh_tokens | idx_refresh_tokens_session_expires | (session_id, expires_at) | セッション・期限別トークン検索 |
| magic_link_tokens | idx_magic_link_email_expires | (email, expires_at) | メール・期限別トークン検索 |
| security_events | idx_security_events_user_type | (user_id, event_type) | ユーザー・イベント種別検索 |
| battle_results | idx_battle_results_players_created | (player1_id, player2_id, created_at) | プレイヤー・作成日別バトル検索 |
| user_stats | idx_user_stats_win_rate_matches | (win_rate DESC, total_matches DESC) | 勝率・試合数別統計検索 |
| login_attempts | idx_login_attempts_ip_time | (ip_address, attempt_time) | IP・時刻別ログイン試行検索 |

---

## データ保持・クリーンアップポリシー

### 定期クリーンアップ（自動化推奨）

#### 日次処理
```sql
-- 期限切れMagic Linkトークンの削除
DELETE FROM magic_link_tokens 
WHERE expires_at < DATE_SUB(NOW(), INTERVAL 1 DAY);

-- 期限切れリフレッシュトークンの削除
DELETE FROM refresh_tokens 
WHERE expires_at < NOW() AND is_revoked = TRUE;

-- 古いJWTブラックリストエントリの削除
DELETE FROM jwt_blacklist 
WHERE expires_at < NOW();
```

#### 週次処理
```sql
-- 古いログイン試行記録の削除（30日以上）
DELETE FROM login_attempts 
WHERE attempted_at < DATE_SUB(NOW(), INTERVAL 30 DAY);

-- 非アクティブセッションの削除（7日以上アクセスなし）
DELETE FROM sessions 
WHERE last_seen_at < DATE_SUB(NOW(), INTERVAL 7 DAY);
```

#### 月次処理
```sql
-- 古いセキュリティイベントの削除（6ヶ月以上）
DELETE FROM security_events 
WHERE created_at < DATE_SUB(NOW(), INTERVAL 6 MONTH);

-- 古いアクティビティログの削除（3ヶ月以上）
DELETE FROM activity_logs 
WHERE created_at < DATE_SUB(NOW(), INTERVAL 3 MONTH);
```

---

## セキュリティ設定

### パスワード要件
- **最小長**: 8文字以上
- **文字種**: 英数字 + 特殊文字推奨
- **ハッシュアルゴリズム**: Argon2id（デフォルト）
- **ソルト**: 自動生成（Argon2idに内包）

### レート制限設定
| エンドポイント | 制限 | 窓時間 |
|---------------|------|--------|
| Magic Link要求 | 5回 | 5分間 |
| ログイン試行 | 10回 | 15分間 |
| パスワードリセット | 3回 | 30分間 |
| 2FA検証 | 5回 | 10分間 |

### セッション管理
- **アクセストークン有効期限**: 15分
- **リフレッシュトークン有効期限**: 30日
- **同時ログイン端末数**: 5台まで（設定可能）
- **非アクティブセッションタイムアウト**: 7日

---

## Redis連携設計

### Redisで管理されるデータ

#### セッション関連
```redis
# セッション情報（TTL: アクセストークンと同期）
SET session:{session_id} '{"user_id":"user_123","device_id":"device_abc","last_seen":"2024-01-01T12:00:00Z"}' EX 900

# WebSocket接続状態
SET websocket:user:{user_id} '{"session_id":"session_123","socket_id":"socket_789"}' EX 3600
```

#### レート制限
```redis
# Magic Link送信制限
SET ratelimit:magiclink:{email} 1 EX 300

# ログイン試行制限
INCR ratelimit:login:{ip_address} EX 900
```

#### ゲーム関連
```redis
# マッチングキュー
LPUSH matching_queue "{user_id}"

# リアルタイムバトル状態
HSET battle:{battle_id} "status" "active" "round" "2"
```

---

## 既存システムとの互換性

### レガシーデータマッピング

| 旧フィールド | 新フィールド | 変換方法 |
|-------------|-------------|----------|
| users.management_code | users.management_code | 直接マッピング |
| users.password | auth_credentials.password_hash | ハッシュ変換が必要 |
| users.profile_image_url | user_profiles.profile_image_url | 直接マッピング |
| users.student_id_image_url | user_profiles.student_id_image_url | 直接マッピング |
| match_history.fight_no | battle_results.fight_no | 直接マッピング |

### 移行時の注意点
1. **パスワードの再ハッシュ化**: 既存のハッシュアルゴリズムからArgon2idへの移行
2. **プロフィール画像URL**: デフォルト画像の設定とNOT NULL制約への対応
3. **統計データの整合性**: user_statsテーブルの既存データとの整合性確保

---

## トラブルシューティング

### よくある問題と対処法

#### 1. Magic Linkが届かない
- `magic_link_tokens`テーブルでトークン生成を確認
- `security_events`テーブルで送信ログを確認
- レート制限（Redis）の状況確認

#### 2. セッションが無効になる
- `sessions`テーブルの`is_revoked`フラグ確認
- `refresh_tokens`テーブルの有効期限確認
- Redis内のセッションキャッシュ状況確認

#### 3. ログインできない
- `login_attempts`テーブルで試行履歴確認
- `security_events`テーブルでエラー詳細確認
- アカウント状態（`users.is_active`）確認

### 監視すべきメトリクス
- **アクティブセッション数**: `SELECT COUNT(*) FROM sessions WHERE is_revoked = FALSE`
- **Magic Link使用率**: security_eventsの成功率
- **異常ログイン**: 複数地点からの短時間アクセス
- **レート制限発動回数**: Redis内のレート制限カウンタ

---

**作成日**: 2024年12月  
**バージョン**: 1.0  
**対応システム**: Magic Link + JWT + パスワード（任意）認証システム  
**データベース**: MySQL 8.0+  
**文字エンコーディング**: utf8mb4_unicode_ci
