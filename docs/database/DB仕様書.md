# データベース仕様書（修正版 - 実際のCREATE文準拠）

## テーブル一覧
- **admin_logs**：管理者オペレーションログ  
- **daily_ranking**：デイリーランキング  
- **match_history**：マッチング結果（履歴）  
- **registration_itemdata**：ユーザー端末識別情報  
- **users**：ユーザー情報  
- **user_logs**：ユーザー操作ログ  
- **user_stats**：ユーザー状態  
- **sessions**：セッション管理  
- **refresh_tokens**：リフレッシュトークン管理  
- **oauth_accounts**：OAuth連携アカウント（2025-06現在未使用）  
- **security_events**：セキュリティイベント記録  
- **login_attempts**：ログイン試行記録  
- **two_factor_auth**：2要素認証設定  

---

## テーブル詳細

### 1. admin_logs（管理者オペレーションログ）
管理者の操作履歴を記録するテーブル

| カラム名      | 型                    | NULL許可 | デフォルト            | 説明                       |
|-------------|-----------------------|---------|-----------------------|--------------------------|
| log_id      | BIGINT AUTO_INCREMENT | NO (PK) |                       | ログID（主キー）              |
| admin_user  | VARCHAR(50)           | NO      |                       | 管理者ユーザー名             |
| operation   | VARCHAR(100)          | NO      |                       | 操作内容                   |
| target_id   | VARCHAR(36)           | NO      |                       | 対象エンティティID           |
| details     | TEXT                  | YES     |                       | 詳細                       |
| operated_at | DATETIME              | NO      | CURRENT_TIMESTAMP     | 操作日時                   |

---

## 2. daily_ranking（デイリーランキング）

| 論理名        | カラム名          | データ型     | NOT NULL | デフォルト                                      | 備考             |
|-------------|------------------|------------|-----------|-----------------------------------------------|----------------|
| ランキング順位   | ranking_position | INT        | YES (PK)  |                                               | 主キー           |
| ユーザーID    | user_id          | VARCHAR(36) | YES       |                                               |                 |
| 勝利数       | wins             | INT        | NO        |                                               | NULL許可         |
| 最終勝利日時   | last_win_at      | DATETIME   | NO        |                                               |                 |
| 更新日時     | updated_at       | DATETIME   | NO        | CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新自動更新       |

---

### 3. match_history（マッチング結果）
じゃんけん対戦の結果履歴を管理するテーブル

| カラム名       | 物理名              | 型                           | NULL許可 | デフォルト                   | 説明                                     |
|--------------|--------------------|----------------------------|---------|----------------------------|----------------------------------------|
| 戦い番号       | fight_no           | BIGINT AUTO_INCREMENT      | NO (PK) |                            | 対戦一意ID                                 |
| ユーザー１番    | player1_id         | VARCHAR(36)                | NO      |                            | プレイヤー1のユーザーID                      |
| ユーザー２番    | player2_id         | VARCHAR(36)                | NO      |                            | プレイヤー2のユーザーID                      |
| プレイヤー1ニックネーム | player1_nickname  | VARCHAR(50)              | YES     |                            | プレイヤー1のニックネーム                      |
| プレイヤー2ニックネーム | player2_nickname  | VARCHAR(50)              | YES     |                            | プレイヤー2のニックネーム                      |
| プレイヤー1の手  | player1_hand       | ENUM('rock','paper','scissors') | NO      |                            | プレイヤー1が出した手                         |
| プレイヤー2の手  | player2_hand       | ENUM('rock','paper','scissors') | NO      |                            | プレイヤー2が出した手                         |
| プレイヤー1結果  | player1_result     | ENUM('win','lose','draw')   | NO      |                            | プレイヤー1の対戦結果                         |
| プレイヤー2結果  | player2_result     | ENUM('win','lose','draw')   | NO      |                            | プレイヤー2の対戦結果                         |
| 勝者           | winner            | TINYINT UNSIGNED            | NO      | 0                          | 0:未決、1:player1勝利、2:player2勝利、3:引き分け |
| 引き分け回数     | draw_count        | INT                         | NO      | 0                          | 引き分け回数                                |
| マッチングタイプ  | match_type        | ENUM('random','friend')     | NO      |                            | マッチング方式                              |
| 生成日時        | created_at        | DATETIME(3)                 | NO      | CURRENT_TIMESTAMP(3)       | 対戦生成日時                               |
| 確定日時        | finished_at       | DATETIME(3)                 | YES     |                            | 対戦確定日時                               |

#### インデックス
- **idx_p1**: (player1_id)  
- **idx_p2**: (player2_id)  
- **idx_p1_result**: (player1_id, player1_result)  
- **idx_p2_result**: (player2_id, player2_result)  

---

## 4. users（ユーザー情報）

| 論理名             | カラム名                 | データ型                | NOT NULL | デフォルト                                      | 備考                                       |
|------------------|------------------------|------------------------|-----------|-----------------------------------------------|------------------------------------------|
| 管理コード          | management_code        | BIGINT AUTO_INCREMENT  | YES (PK)  |                                               | 主キー、自動採番                              |
| ユーザーID         | user_id                | VARCHAR(36)            | YES       |                                               | 一意識別子                                   |
| 電子メール          | email                  | VARCHAR(255)           | NO        |                                               |                                             |
| パスワード          | password               | VARCHAR(255)           | YES       |                                               | ハッシュ化パスワード                             |
| 名前              | name                   | VARCHAR(50)            | NO        |                                               |                                             |
| ニックネーム        | nickname               | VARCHAR(50)            | YES       |                                               | **必須項目**                               |
| 郵便番号           | postal_code            | VARCHAR(10)            | NO        |                                               |                                             |
| 住所              | address                | VARCHAR(255)           | NO        |                                               |                                             |
| 電話番号           | phone_number           | VARCHAR(15)            | NO        |                                               |                                             |
| 学校名            | university             | VARCHAR(100)           | NO        |                                               |                                             |
| 生年月日           | birthdate              | DATE                   | NO        |                                               |                                             |
| プロフィール写真URL  | profile_image_url      | VARCHAR(255)           | YES       |                                               | **NOT NULL制約**                          |
| 学生証イメージURL    | student_id_image_url   | VARCHAR(255)           | YES       |                                               | **NOT NULL制約**                          |
| 生成日            | created_at             | DATETIME               | NO        | CURRENT_TIMESTAMP                             | レコード作成日時                                 |
| 更新日            | updated_at             | DATETIME               | NO        | CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | レコード更新日時                                 |
| 登録種別           | register_type          | VARCHAR(20)            | NO        | 'email'                                       | email / google / line / apple               |
| 学生証編集可能      | is_student_id_editable | TINYINT                | NO        | 0                                             | 0: 編集不可、1: 編集可                          |
| BAN状態          | is_banned              | TINYINT                | NO        | 0                                             | 0:未設定、1:設定、2:復帰                        |

### インデックス

| インデックス名    | カラム     | ユニーク |
|------------------|----------|--------|
| idx_user_id      | user_id  | NO     |

---

### 5. registration_itemdata（ユーザー端末識別情報）
ユーザーが利用する端末情報を管理するテーブル

| カラム名         | 物理名           | 型             | NULL許可    | デフォルト | 説明                         |
|----------------|----------------|---------------|-----------|----------|----------------------------|
| ユーザー管理番号   | management_code | BIGINT        | NO (PK)   |          | ユーザー管理コード               |
| 枝番            | subnum         | INT           | NO (PK)   | 1        | 同一ユーザー内での連番            |
| デバイス種       | itemtype       | TINYINT       | NO        | 0        | 0:スマホ以外,1:iOS,2:Android |
| デバイス識別ID    | itemid         | DATETIME      | NO        |          | 端末固有識別子                  |
| 作成日時        | created_at     | DATETIME      | NO        | CURRENT_TIMESTAMP | 作成日時                      |

#### 主キー
- (management_code, subnum)  

#### 外部キー
- management_code → users(management_code)  

---

### 6. user_logs（ユーザー操作ログ）
ユーザーの操作イベントを時系列で記録するテーブル

| カラム名         | 物理名            | 型                    | NULL許可 | デフォルト | 説明                                |
|----------------|------------------|-----------------------|---------|----------|-----------------------------------|
| ログID         | log_id           | BIGINT AUTO_INCREMENT | NO (PK) |          | ログID（主キー）                         |
| ユーザーID      | user_id          | VARCHAR(36)           | NO      | ''       | ユーザー無関係通知時は空文字             |
| 操作コード      | operation_code   | VARCHAR(10)           | YES     |          | 操作コード                             |
| 操作           | operation        | VARCHAR(100)          | YES     |          | 操作内容                               |
| 詳細           | details          | TEXT                  | YES     |          | 詳細説明                               |
| 操作日時        | operated_at      | DATETIME              | NO      | CURRENT_TIMESTAMP | 操作日時                     |

#### インデックス
- **idx_user_logs_uid**: (user_id)  

---

## 7. user_stats（ユーザー状態）

| 論理名               | カラム名                      | データ型    | NOT NULL | デフォルト      | 備考                                               |
|--------------------|------------------------------|-----------|-----------|----------------|--------------------------------------------------|
| 管理コード             | management_code             | BIGINT    | YES (PK)  |                | 主キー（外部キー）                                     |
| ユーザーID            | user_id                     | VARCHAR(36) | YES     |                | ユーザー識別子                                        |
| 通算勝利数            | total_wins                  | INT       | NO        | 0              | 通算の勝利数                                           |
| 現在の連勝数          | current_win_streak          | INT       | NO        | 0              | 現在の連勝数                                           |
| 最大連勝数            | max_win_streak              | INT       | NO        | 0              | 記録された最大連勝数                                       |
| グーの出数           | hand_stats_rock             | INT       | NO        | 0              | グーの出数                                             |
| チョキの出数          | hand_stats_scissors         | INT       | NO        | 0              | チョキの出数                                            |
| パーの出数           | hand_stats_paper            | INT       | NO        | 0              | パーの出数                                             |
| お気に入りの手         | favorite_hand               | VARCHAR(10) | YES     | NULL           | 最も多く出した手（例：'rock'）                                |
| 直近の5手と勝敗        | recent_hand_results_str     | VARCHAR(255) | NO      | ''             | 例："G:W,P:D,S:L"（グー勝ち、パーあいこ、チョキ負け）               |
| 当日勝利数            | daily_wins                  | INT       | NO        | 0              | 当日の勝利数                                           |
| 当日敗北数            | daily_losses                | INT       | NO        | 0              | 当日の敗北数                                           |
| 当日引き分け数         | daily_draws                 | INT       | NO        | 0              | 当日の引き分け数                                         |
| 称号                | title                       | VARCHAR(50) | NO      | ''             | 現在表示中の称号                                         |
| 称号リスト             | available_titles            | VARCHAR(255) | NO     | ''             | 獲得済み称号IDのCSV（例: 'title_001,title_003'）               |
| 二つ名               | alias                       | VARCHAR(50) | NO      | ''             | 現在表示中の二つ名                                         |
| 称号表示              | show_title                  | BOOLEAN   | NO        | TRUE           | 称号を他者に見せるか                                      |
| 二つ名表示            | show_alias                  | BOOLEAN   | NO        | TRUE           | 二つ名を他者に見せるか                                     |
| ユーザーランク         | user_rank                   | VARCHAR(20) | NO      | 'no_rank'      | 表示・報酬用のランク                                      |
| リセット日           | last_reset_at              | DATE      | YES       |                | 日次リセット日時                                         |

#### 主キー
- management_code

#### 外部キー
- management_code → users(management_code)

---

## 重要な注意事項

### 1. profile_image_url と student_id_image_url
- **NOT NULL制約**：これらのフィールドは`NOT NULL`です
- デフォルト画像URLを設定する必要があります
- 実際のシードデータでは以下のデフォルト値が使用されています：
  - `profile_image_url`: `'https://lesson01.myou-kou.com/avatars/defaultAvatar[1-18].png'`
  - `student_id_image_url`: `'https://lesson01.myou-kou.com/avatars/defaultStudentId.png'`

### 2. user_statsテーブル
- `management_code`が主キーです
- `user_id`フィールドも存在しますが、これは参照用です
- JOINクエリでは`users.management_code = user_stats.management_code`を使用します

### 3. 文字エンコーディング
- 全テーブルで`ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci`が設定されています

### 4. 実際のデータ例
シードファイルから確認できる実際のデータパターン：
- `title`: 'title_001', 'title_002', 'title_003', 'title_004', 'title_005'
- `available_titles`: CSVフォーマット（例: 'title_004,title_003,title_004'）
- `recent_hand_results_str`: フォーマット例 'P:D,G:W,P:L,S:W,P:L'
- `user_rank`: 'no_rank', 'bronze', 'silver', 'gold'
- `favorite_hand`: 'rock', 'scissors', 'paper'

---

## 認証関連テーブル

### 8. sessions（セッション管理）
ユーザーセッション管理用。JWT + Redis でのセッション管理を補完し、デバイスごとの詳細な制御を実現。

| カラム名 | 物理名 | 型 | NULL許可 | デフォルト | 説明 |
|---------|--------|-----|----------|------------|------|
| セッションID | session_id | VARCHAR(128) | NO (PK) | | セッション一意識別子 |
| ユーザーID | user_id | VARCHAR(36) | NO | | ユーザー識別子 |
| アクセストークン | access_token | VARCHAR(512) | NO | | JWTアクセストークン |
| リフレッシュトークン | refresh_token | VARCHAR(512) | NO | | JWTリフレッシュトークン |
| デバイスID | device_id | VARCHAR(128) | NO | | 端末識別子 |
| 有効期限 | expires_at | DATETIME | NO | | セッション有効期限 |
| 最終アクティビティ | last_activity | DATETIME | NO | | 最終アクセス日時 |
| IPアドレス | ip_address | VARCHAR(45) | NO | | アクセス元IP |
| ユーザーエージェント | user_agent | VARCHAR(255) | YES | | ブラウザ情報 |
| 作成日時 | created_at | DATETIME | NO | CURRENT_TIMESTAMP | |
| 更新日時 | updated_at | DATETIME | NO | CURRENT_TIMESTAMP | |

#### インデックス
- **idx_sessions_user_id**: (user_id)
- **idx_sessions_device_id**: (device_id)

### 9. refresh_tokens（リフレッシュトークン管理）
リフレッシュトークンの管理とセキュリティ制御用。明示的な失効管理とセキュリティ監査に使用。

| カラム名 | 物理名 | 型 | NULL許可 | デフォルト | 説明 |
|---------|--------|-----|----------|------------|------|
| トークンID | token_id | VARCHAR(128) | NO (PK) | | トークン一意識別子 |
| ユーザーID | user_id | VARCHAR(36) | NO | | ユーザー識別子 |
| トークンハッシュ | refresh_token_hash | VARCHAR(512) | NO | | トークンのハッシュ値 |
| デバイスID | device_id | VARCHAR(128) | NO | | 端末識別子 |
| 発行日時 | issued_at | DATETIME | NO | | トークン発行日時 |
| 有効期限 | expires_at | DATETIME | NO | | トークン有効期限 |
| 失効フラグ | revoked | BOOLEAN | NO | FALSE | 失効状態 |
| 失効理由 | revoked_reason | VARCHAR(100) | YES | | 失効理由 |
| 作成日時 | created_at | DATETIME | NO | CURRENT_TIMESTAMP | |

#### インデックス
- **idx_refresh_tokens_user_id**: (user_id)

### 10. oauth_accounts（OAuth連携アカウント）
将来的なGoogle/LINE/Apple等のOAuth認証連携用。現時点（2025-06）では未使用。

| カラム名 | 物理名 | 型 | NULL許可 | デフォルト | 説明 |
|---------|--------|-----|----------|------------|------|
| OAuth ID | oauth_id | VARCHAR(128) | NO (PK) | | OAuth連携ID |
| ユーザーID | user_id | VARCHAR(36) | NO | | ユーザー識別子 |
| プロバイダー | provider | VARCHAR(20) | NO | | 認証プロバイダー名 |
| プロバイダーユーザーID | provider_user_id | VARCHAR(255) | NO | | プロバイダー側のID |
| アクセストークン | access_token | TEXT | YES | | プロバイダーのトークン |
| リフレッシュトークン | refresh_token | TEXT | YES | | プロバイダーのリフレッシュトークン |
| トークン有効期限 | token_expires_at | DATETIME | YES | | プロバイダートークンの有効期限 |
| プロフィールデータ | profile_data | JSON | YES | | プロバイダーから取得した情報 |
| 作成日時 | created_at | DATETIME | NO | CURRENT_TIMESTAMP | |
| 更新日時 | updated_at | DATETIME | NO | CURRENT_TIMESTAMP | |

### 11. security_events（セキュリティイベント）
セキュリティ関連イベントの記録用。不正アクセスの検知、監査ログ、ユーザーサポート用。

| カラム名 | 物理名 | 型 | NULL許可 | デフォルト | 説明 |
|---------|--------|-----|----------|------------|------|
| イベントID | event_id | BIGINT | NO (PK) | | イベント一意識別子 |
| ユーザーID | user_id | VARCHAR(36) | NO | | ユーザー識別子 |
| イベントタイプ | event_type | VARCHAR(50) | NO | | イベントの種類 |
| ステータス | status | VARCHAR(20) | NO | | イベントの結果 |
| IPアドレス | ip_address | VARCHAR(45) | NO | | アクセス元IP |
| デバイス情報 | device_info | JSON | YES | | デバイスの詳細情報 |
| 作成日時 | created_at | DATETIME | NO | CURRENT_TIMESTAMP | |

#### インデックス
- **idx_security_events_user_id**: (user_id)
- **idx_security_events_created_at**: (created_at)

### 12. login_attempts（ログイン試行）
ログイン試行の記録と制限用。レート制限、ブルートフォース攻撃対策用。

| カラム名 | 物理名 | 型 | NULL許可 | デフォルト | 説明 |
|---------|--------|-----|----------|------------|------|
| 試行ID | attempt_id | BIGINT | NO (PK) | | 試行一意識別子 |
| ユーザーID | user_id | VARCHAR(36) | NO | | ユーザー識別子 |
| IPアドレス | ip_address | VARCHAR(45) | NO | | アクセス元IP |
| 試行日時 | attempt_time | DATETIME | NO | CURRENT_TIMESTAMP | 試行日時 |
| 成功フラグ | success | BOOLEAN | NO | FALSE | 成功/失敗 |
| 失敗理由 | failure_reason | VARCHAR(100) | YES | | 失敗の理由 |

#### インデックス
- **idx_login_attempts_user_id**: (user_id)
- **idx_login_attempts_ip**: (ip_address)
- **idx_login_attempts_time**: (attempt_time)

### 13. two_factor_auth（2要素認証）
2要素認証（2FA）の設定と管理用。TOTP方式での追加認証レイヤーを提供。

| カラム名 | 物理名 | 型 | NULL許可 | デフォルト | 説明 |
|---------|--------|-----|----------|------------|------|
| ユーザーID | user_id | VARCHAR(36) | NO (PK) | | ユーザー識別子 |
| 有効フラグ | enabled | BOOLEAN | NO | FALSE | 2FA有効/無効 |
| 秘密鍵 | secret_key | VARCHAR(32) | NO | | TOTP用の秘密鍵（暗号化） |
| バックアップコード | backup_codes | JSON | YES | | リカバリーコード（暗号化） |
| 最終使用日時 | last_used | DATETIME | YES | | 最後に使用された日時 |
| 作成日時 | created_at | DATETIME | NO | CURRENT_TIMESTAMP | |
| 更新日時 | updated_at | DATETIME | NO | CURRENT_TIMESTAMP | |

---
