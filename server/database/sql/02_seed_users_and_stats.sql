-- ユーザーデータとユーザー統計情報の一括シード
SET NAMES utf8mb4;
SET character_set_client = utf8mb4;
SET character_set_connection = utf8mb4;
SET character_set_results = utf8mb4;

USE janken_db;

BEGIN;

-- 一時テーブルの作成（必要なカラムのみ）
CREATE TEMPORARY TABLE temp_user_data (
    user_id VARCHAR(36),
    email VARCHAR(255),
    password VARCHAR(255),
    name VARCHAR(50),
    nickname VARCHAR(50),
    postal_code VARCHAR(10),
    address VARCHAR(255),
    phone_number VARCHAR(15),
    university VARCHAR(100),
    birthdate DATE,
    profile_image_url VARCHAR(255),
    student_id_image_url VARCHAR(255),
    created_at DATETIME,
    updated_at DATETIME,
    register_type VARCHAR(20),
    is_student_id_editable TINYINT,
    is_banned TINYINT,
    -- user_stats のデータ
    total_wins INT,
    current_win_streak INT,
    max_win_streak INT,
    hand_stats_rock INT,
    hand_stats_scissors INT,
    hand_stats_paper INT,
    favorite_hand VARCHAR(10),
    recent_hand_results_str VARCHAR(255),
    daily_wins INT,
    daily_losses INT,
    daily_draws INT,
    title VARCHAR(50),
    available_titles TEXT,
    alias VARCHAR(50),
    show_title BOOLEAN,
    show_alias BOOLEAN,
    user_rank VARCHAR(20),
    last_reset_at DATE
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- データの挿入
INSERT INTO temp_user_data VALUES (
    'user001', 'user001@example.com', '$2a$10$uBCU2aEMsufCD6OZj4LG4umPWIDBQcGZEo.RtfY7w2u/EhMwvJ/fG', '山田 太郎', 'やまだ', '123-4567', '東京都渋谷区渋谷1-1-1', '090-1234-5678', '東京大学', '1995-05-15', 'https://lesson01.myou-kou.com/avatars/defaultAvatar1.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2023-01-01T00:00:00', '2023-01-01T00:00:00', 'email', 1, 0, 
    153, 1, 18,
    36, 49, 42,
    'scissors', 'P:D,G:W,P:L,S:W,P:L',
    2, 7, 0,
    'title_001', 'title_004,title_003,title_004', 'skill',
    TRUE, TRUE,
    'silver', '2025-05-04'
);
INSERT INTO temp_user_data VALUES (
    'user002', 'user002@example.com', 'password002', '佐藤 花子', 'はなこ', '234-5678', '大阪府大阪市中央区1-2-3', '090-2345-6789', '大阪大学', '1997-07-25', 'https://lesson01.myou-kou.com/avatars/defaultAvatar2.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2023-01-02T00:00:00', '2023-01-02T00:00:00', 'email', 1, 0, 
    4, 1, 0,
    2, 48, 36,
    'scissors', 'S:W,S:L,P:D,S:D,P:L',
    10, 0, 3,
    'title_001', 'title_002,title_001,title_002', 'to',
    TRUE, TRUE,
    'gold', '2025-05-05'
);
INSERT INTO temp_user_data VALUES (
    'user003', 'user003@example.com', 'password003', '鈴木 一郎', 'いちろう', '345-6789', '神奈川県横浜市青葉区2-3-4', '090-3456-7890', '慶應義塾大学', '1996-12-05', 'https://lesson01.myou-kou.com/avatars/defaultAvatar3.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2023-01-03T00:00:00', '2023-01-03T00:00:00', 'email', 1, 0, 
    70, 6, 2,
    24, 36, 50,
    'paper', 'S:L,P:L,G:D,P:W,P:W',
    9, 1, 0,
    'title_003', 'title_001,title_003', 'war',
    TRUE, TRUE,
    'no_rank', '2025-05-01'
);
INSERT INTO temp_user_data VALUES (
    'user004', 'user004@example.com', 'password004', '田中 美咲', 'みさき', '456-7890', '東京都新宿区4-5-6', '090-4567-8901', '早稲田大学', '1998-08-20', 'https://lesson01.myou-kou.com/avatars/defaultAvatar4.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2023-01-04T00:00:00', '2023-01-04T00:00:00', 'email', 1, 0, 
    132, 3, 1,
    6, 9, 32,
    'paper', 'P:L,S:W,P:D,S:W,S:W',
    6, 8, 5,
    'title_003', 'title_005,title_001,title_004', 'away',
    TRUE, TRUE,
    'bronze', '2025-05-02'
);
INSERT INTO temp_user_data VALUES (
    'user005', 'user005@example.com', 'password005', '田中 裕美子', 'ニャンタス', '639-6577', '徳島県昭島市清水 Street8-2-5', '090-8074-1525', '同志社大学', '1995-09-26', 'https://lesson01.myou-kou.com/avatars/defaultAvatar5.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2024-09-09T02:38:52', '2024-09-09T02:38:52', 'email', 1, 0, 
    18, 6, 2,
    7, 8, 49,
    'paper', 'P:W,S:D,P:W,P:D,P:W',
    3, 2, 4,
    'title_002', 'title_005', 'nothing',
    TRUE, TRUE,
    'bronze', '2025-05-04'
);
INSERT INTO temp_user_data VALUES (
    'user006', 'user006@example.com', 'password006', '高橋 真綾', 'ブースター', '933-6806', '奈良県横浜市中区木村 Street7-6-2', '090-2686-3370', '北海道大学', '1995-05-09', 'https://lesson01.myou-kou.com/avatars/defaultAvatar6.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2023-10-01T09:59:20', '2023-10-01T09:59:20', 'email', 1, 0, 
    186, 1, 12,
    5, 10, 8,
    'scissors', 'G:D,S:L,G:W,G:D,P:W',
    5, 7, 3,
    'title_003', 'title_002', 'dinner',
    TRUE, TRUE,
    'gold', '2025-05-03'
);
INSERT INTO temp_user_data VALUES (
    'user007', 'user007@example.com', 'password007', '近藤 花子', 'エレクター', '282-8084', '沖縄県匝瑳市藤田 Street9-2-6', '090-5387-7881', '上智大学', '2000-09-22', 'https://lesson01.myou-kou.com/avatars/defaultAvatar7.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2020-03-10T05:03:51', '2020-03-10T05:03:51', 'email', 1, 0, 
    121, 1, 9,
    9, 12, 48,
    'paper', 'P:D,G:D,G:W,S:L,G:D',
    5, 0, 2,
    'title_001', 'title_003,title_002,title_002', 'computer',
    TRUE, TRUE,
    'bronze', '2025-05-02'
);
INSERT INTO temp_user_data VALUES (
    'user008', 'user008@example.com', 'password008', '山崎 裕美子', 'ナノニクス', '148-8028', '福島県香取市斎藤 Street10-7-4', '090-1440-4617', '北海道大学', '2004-01-08', 'https://lesson01.myou-kou.com/avatars/defaultAvatar8.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2022-10-26T12:10:47', '2022-10-26T12:10:47', 'email', 1, 0, 
    148, 9, 14,
    37, 50, 28,
    'scissors', 'P:W,G:D,S:W,P:L,G:D',
    6, 4, 1,
    'title_001', 'title_001,title_005,title_004', '不屈の魔術師の残響',
    TRUE, TRUE,
    'gold', '2025-05-03'
);
INSERT INTO temp_user_data VALUES (
    'user009', 'user009@example.com', 'password009', '橋本 亮介', 'ネオバード', '144-5134', '富山県杉並区中島 Street8-3-3', '090-9400-1302', '名古屋大学', '1996-01-01', 'https://lesson01.myou-kou.com/avatars/defaultAvatar9.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2024-01-22T17:53:06', '2024-01-22T17:53:06', 'email', 1, 0, 
    141, 6, 16,
    15, 4, 34,
    'paper', 'P:D,G:L,S:L,S:L,S:W',
    10, 7, 0,
    'title_001', 'title_005,title_003,title_001', 'far',
    TRUE, TRUE,
    'silver', '2025-05-04'
);
INSERT INTO temp_user_data VALUES (
    'user010', 'user010@example.com', 'password010', '山崎 英樹', 'ネオバード', '308-8656', '石川県川崎市川崎区橋本 Street3-10-3', '090-3487-3509', '一橋大学', '2004-08-18', 'https://lesson01.myou-kou.com/avatars/defaultAvatar10.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2025-02-16T12:51:25', '2025-02-16T12:51:25', 'email', 1, 0, 
    112, 1, 11,
    2, 24, 44,
    'paper', 'G:L,P:L,P:L,S:L,P:L',
    3, 3, 2,
    'title_004', 'title_003,title_005', 'science',
    TRUE, TRUE,
    'bronze', '2025-05-04'
);
INSERT INTO temp_user_data VALUES (
    'user011', 'user011@example.com', 'password011', '高橋 加奈', 'ポッポロン', '614-9736', '島根県横浜市南区鈴木 Street1-6-9', '090-8735-9379', '明治大学', '2005-03-14', 'https://lesson01.myou-kou.com/avatars/defaultAvatar11.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2021-04-21T19:10:47', '2021-04-21T19:10:47', 'email', 1, 0, 
    48, 0, 13,
    32, 40, 46,
    'paper', 'P:D,S:L,S:L,G:L,G:W',
    3, 10, 2,
    'title_001', 'title_001', 'create',
    TRUE, TRUE,
    'gold', '2025-05-05'
);
INSERT INTO temp_user_data VALUES (
    'user012', 'user012@example.com', 'password012', '青木 健一', 'ブースター', '091-2870', '新潟県長生郡長柄町加藤 Street5-6-1', '090-9767-4075', '東北大学', '2005-09-27', 'https://lesson01.myou-kou.com/avatars/defaultAvatar12.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2024-10-22T05:45:47', '2024-10-22T05:45:47', 'email', 1, 0, 
    24, 8, 19,
    11, 8, 16,
    'paper', 'G:D,P:L,G:W,S:W,S:L',
    0, 4, 4,
    'title_002', 'title_002', 'second',
    TRUE, TRUE,
    'no_rank', '2025-05-04'
);
INSERT INTO temp_user_data VALUES (
    'user013', 'user013@example.com', 'password013', '佐々木 加奈', 'トルネード', '045-8732', '岡山県横浜市南区小林 Street5-1-6', '090-6226-2882', '大阪大学', '1999-10-17', 'https://lesson01.myou-kou.com/avatars/defaultAvatar13.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2020-06-15T14:02:19', '2020-06-15T14:02:19', 'email', 1, 0, 
    185, 2, 0,
    10, 4, 27,
    'paper', 'S:W,S:D,G:W,S:D,S:D',
    10, 4, 4,
    'title_002', 'title_003,title_001', 'myself',
    TRUE, TRUE,
    'silver', '2025-05-06'
);
INSERT INTO temp_user_data VALUES (
    'user014', 'user014@example.com', 'password014', '岡田 学', 'エレクター', '608-4174', '東京都長生郡一宮町小林 Street10-8-6', '090-5120-6489', '琉球大学', '2000-05-22', 'https://lesson01.myou-kou.com/avatars/defaultAvatar14.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2022-09-14T17:11:22', '2022-09-14T17:11:22', 'email', 1, 0, 
    83, 1, 16,
    18, 13, 16,
    'rock', 'S:L,S:L,G:L,P:L,S:L',
    10, 4, 5,
    'title_004', 'title_003', 'current',
    TRUE, TRUE,
    'silver', '2025-05-05'
);
INSERT INTO temp_user_data VALUES (
    'user015', 'user015@example.com', 'password015', '坂本 裕樹', 'サイクロン', '688-7833', '奈良県大網白里市松本 Street5-8-4', '090-1843-9418', '中央大学', '2004-06-26', 'https://lesson01.myou-kou.com/avatars/defaultAvatar15.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2022-08-28T08:28:19', '2022-08-28T08:28:19', 'email', 1, 0, 
    17, 3, 3,
    0, 3, 5,
    'paper', 'G:L,S:D,G:L,G:W,S:L',
    9, 8, 0,
    'title_001', 'title_002,title_003', 'which',
    TRUE, TRUE,
    'gold', '2025-05-04'
);
INSERT INTO temp_user_data VALUES (
    'user016', 'user016@example.com', 'password016', '佐々木 浩', 'アストロン', '983-6874', '静岡県国立市佐藤 Street8-2-1', '090-2661-3217', '中央大学', '2005-01-15', 'https://lesson01.myou-kou.com/avatars/defaultAvatar16.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2023-04-10T14:15:05', '2023-04-10T14:15:05', 'email', 1, 0, 
    158, 7, 0,
    14, 39, 41,
    'paper', 'P:W,S:L,S:D,S:D,G:W',
    0, 2, 3,
    'title_001', 'title_005,title_003,title_002', 'better',
    TRUE, TRUE,
    'no_rank', '2025-05-03'
);
INSERT INTO temp_user_data VALUES (
    'user017', 'user017@example.com', 'password017', '高橋 和也', 'シリウス', '861-7727', '山口県横浜市栄区村上 Street10-10-5', '090-4898-2185', '岡山大学', '1995-11-09', 'https://lesson01.myou-kou.com/avatars/defaultAvatar17.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2020-10-26T08:35:18', '2020-10-26T08:35:18', 'email', 1, 0, 
    51, 1, 13,
    35, 44, 1,
    'scissors', 'P:L,G:D,S:D,P:D,P:W',
    10, 1, 3,
    'title_002', 'title_004,title_005', 'country',
    TRUE, TRUE,
    'silver', '2025-05-02'
);
INSERT INTO temp_user_data VALUES (
    'user018', 'user018@example.com', 'password018', '佐藤 花子', 'ペンギナー', '805-3610', '山口県長生郡白子町山崎 Street8-1-8', '090-1073-5824', '立教大学', '2005-09-15', 'https://lesson01.myou-kou.com/avatars/defaultAvatar18.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2024-08-08T03:52:36', '2024-08-08T03:52:36', 'email', 1, 0, 
    45, 8, 13,
    33, 0, 19,
    'rock', 'S:W,P:L,P:L,P:W,G:W',
    0, 0, 2,
    'title_002', 'title_003,title_001', 'far',
    TRUE, TRUE,
    'no_rank', '2025-05-06'
);
INSERT INTO temp_user_data VALUES (
    'user019', 'user019@example.com', 'password019', '鈴木 陽一', 'パラゴン', '598-5891', '京都府香取郡神崎町渡辺 Street6-7-2', '090-4654-5943', '岡山大学', '1997-07-14', 'https://lesson01.myou-kou.com/avatars/defaultAvatar1.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2023-06-01T18:43:02', '2023-06-01T18:43:02', 'email', 1, 0, 
    45, 3, 8,
    45, 36, 25,
    'rock', 'S:W,G:L,G:L,G:W,P:W',
    6, 7, 2,
    'title_003', 'title_005,title_004,title_005', 'poor',
    TRUE, TRUE,
    'no_rank', '2025-05-03'
);
INSERT INTO temp_user_data VALUES (
    'user020', 'user020@example.com', 'password020', '鈴木 直樹', 'リザルトン', '314-4024', '愛媛県横浜市港南区小林 Street8-1-3', '090-2833-8008', '関西学院大学', '2007-04-16', 'https://lesson01.myou-kou.com/avatars/defaultAvatar2.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2021-04-16T06:24:37', '2021-04-16T06:24:37', 'email', 1, 0, 
    99, 10, 3,
    44, 7, 42,
    'rock', 'S:L,S:L,P:D,G:W,S:W',
    3, 5, 5,
    'title_002', 'title_004,title_001', 'apply',
    TRUE, TRUE,
    'gold', '2025-05-01'
);
INSERT INTO temp_user_data VALUES (
    'user021', 'user021@example.com', 'password021', '渡辺 智也', 'オメガス', '479-1369', '石川県山武市山崎 Street6-4-3', '090-4514-1033', '慶應義塾大学', '2005-03-30', 'https://lesson01.myou-kou.com/avatars/defaultAvatar3.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2020-10-13T18:40:59', '2020-10-13T18:40:59', 'email', 1, 0, 
    138, 0, 16,
    12, 28, 32,
    'paper', 'P:L,S:D,G:D,S:D,G:D',
    1, 5, 1,
    'title_002', 'title_002', 'help',
    TRUE, TRUE,
    'silver', '2025-05-02'
);
INSERT INTO temp_user_data VALUES (
    'user022', 'user022@example.com', 'password022', '小林 篤司', 'トルネード', '513-9900', '宮崎県川崎市川崎区中村 Street7-4-3', '090-5879-3596', '東京工業大学', '2006-04-28', 'https://lesson01.myou-kou.com/avatars/defaultAvatar4.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2023-11-07T22:08:27', '2023-11-07T22:08:27', 'email', 1, 0, 
    12, 1, 1,
    39, 24, 28,
    'rock', 'G:D,S:L,G:D,S:W,G:L',
    7, 1, 5,
    'title_005', 'title_002', 'age',
    TRUE, TRUE,
    'gold', '2025-05-04'
);
INSERT INTO temp_user_data VALUES (
    'user023', 'user023@example.com', 'password023', '木村 桃子', 'ポチマル', '881-0301', '大分県多摩市小川 Street8-9-8', '090-9148-9382', '九州大学', '2002-06-26', 'https://lesson01.myou-kou.com/avatars/defaultAvatar5.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2023-07-04T17:42:32', '2023-07-04T17:42:32', 'email', 1, 0, 
    150, 7, 1,
    44, 20, 35,
    'rock', 'P:L,S:W,G:L,S:D,G:W',
    2, 1, 4,
    'title_001', 'title_004,title_004', 'account',
    TRUE, TRUE,
    'bronze', '2025-05-05'
);
INSERT INTO temp_user_data VALUES (
    'user024', 'user024@example.com', 'password024', '吉田 陽子', 'スカイロア', '076-3550', '三重県長生郡長南町佐藤 Street7-1-3', '090-4659-3764', '北海道大学', '1997-09-04', 'https://lesson01.myou-kou.com/avatars/defaultAvatar6.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2021-06-16T19:12:55', '2021-06-16T19:12:55', 'email', 1, 0, 
    37, 6, 12,
    28, 5, 41,
    'paper', 'P:L,P:D,P:D,S:W,G:W',
    7, 6, 0,
    'title_001', 'title_004,title_001', 'game',
    TRUE, TRUE,
    'bronze', '2025-05-05'
);
INSERT INTO temp_user_data VALUES (
    'user025', 'user025@example.com', 'password025', '長谷川 明美', 'ウィスパー', '189-7105', '熊本県武蔵村山市佐々木 Street3-7-8', '090-3525-1145', '早稲田大学', '2001-10-20', 'https://lesson01.myou-kou.com/avatars/defaultAvatar7.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2023-02-15T21:10:53', '2023-02-15T21:10:53', 'email', 1, 0, 
    182, 4, 9,
    46, 14, 25,
    'rock', 'G:L,P:D,G:W,S:W,S:L',
    2, 0, 4,
    'title_003', 'title_003,title_005,title_005', 'young',
    TRUE, TRUE,
    'gold', '2025-05-01'
);
INSERT INTO temp_user_data VALUES (
    'user026', 'user026@example.com', 'password026', '佐々木 くみ子', 'キャロットン', '895-3613', '兵庫県府中市伊藤 Street2-9-5', '090-3798-4813', '熊本大学', '2003-05-15', 'https://lesson01.myou-kou.com/avatars/defaultAvatar8.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2021-03-22T06:20:17', '2021-03-22T06:20:17', 'email', 1, 0, 
    112, 4, 12,
    34, 44, 16,
    'scissors', 'P:L,G:W,G:L,G:W,G:D',
    10, 7, 2,
    'title_003', 'title_002,title_005', 'our',
    TRUE, TRUE,
    'silver', '2025-05-03'
);
INSERT INTO temp_user_data VALUES (
    'user027', 'user027@example.com', 'password027', '石井 聡太郎', 'サイクロン', '871-8148', '福岡県印旛郡本埜村中村 Street6-8-8', '090-8441-5872', '琉球大学', '2002-03-07', 'https://lesson01.myou-kou.com/avatars/defaultAvatar9.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2021-09-30T00:11:40', '2021-09-30T00:11:40', 'email', 1, 0, 
    158, 2, 7,
    29, 9, 17,
    'rock', 'G:W,P:L,S:W,P:D,P:D',
    6, 7, 2,
    'title_005', 'title_005,title_001', 'important',
    TRUE, TRUE,
    'bronze', '2025-05-05'
);
INSERT INTO temp_user_data VALUES (
    'user028', 'user028@example.com', 'password028', '高橋 裕樹', 'シャイニャ', '111-7315', '秋田県西多摩郡檜原村中川 Street3-2-4', '090-1469-3601', '明治大学', '1996-01-09', 'https://lesson01.myou-kou.com/avatars/defaultAvatar10.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2024-11-14T05:45:49', '2024-11-14T05:45:49', 'email', 1, 0, 
    155, 4, 9,
    23, 32, 18,
    'scissors', 'S:D,S:L,S:D,P:L,P:D',
    7, 4, 4,
    'title_001', 'title_002,title_002', 'edge',
    TRUE, TRUE,
    'gold', '2025-05-02'
);
INSERT INTO temp_user_data VALUES (
    'user029', 'user029@example.com', 'password029', '清水 真綾', 'モービィ', '246-5289', '北海道渋谷区伊藤 Street9-9-5', '090-2411-1195', '法政大学', '1995-10-28', 'https://lesson01.myou-kou.com/avatars/defaultAvatar11.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2021-08-30T05:17:57', '2021-08-30T05:17:57', 'email', 1, 0, 
    29, 9, 0,
    10, 0, 39,
    'paper', 'G:L,P:L,P:D,P:L,S:D',
    4, 10, 0,
    'title_004', 'title_004', 'true',
    TRUE, TRUE,
    'silver', '2025-05-01'
);
INSERT INTO temp_user_data VALUES (
    'user030', 'user030@example.com', 'password030', '橋本 知実', 'ゴーゴン', '550-8152', '富山県横浜市緑区山田 Street4-3-2', '090-6719-5166', '琉球大学', '1997-11-05', 'https://lesson01.myou-kou.com/avatars/defaultAvatar12.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2021-06-08T09:07:36', '2021-06-08T09:07:36', 'email', 1, 0, 
    115, 2, 5,
    23, 34, 2,
    'scissors', 'S:W,P:L,S:W,S:W,G:L',
    10, 7, 5,
    'title_003', 'title_005,title_001', 'federal',
    TRUE, TRUE,
    'silver', '2025-05-06'
);
INSERT INTO temp_user_data VALUES (
    'user031', 'user031@example.com', 'password031', '石川 桃子cyan', 'コスモス', '294-2616', '島根県あきる野市木村 Street2-8-3', '090-1459-1213', '上智大学', '1998-02-02', 'https://lesson01.myou-kou.com/avatars/defaultAvatar13.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2020-12-12T06:57:49', '2020-12-12T06:57:49', 'email', 1, 0, 
    10, 4, 11,
    39, 46, 11,
    'scissors', 'P:W,G:W,G:D,P:W,P:L',
    1, 0, 1,
    'title_002', 'title_002,title_001', '不屈の意志',
    TRUE, TRUE,
    'silver', '2025-05-06'
);
INSERT INTO temp_user_data VALUES (
    'user032', 'user032@example.com', 'password032', '清水 涼平', 'ライトスピア', '303-1347', '愛媛県目黒区山崎 Street5-5-10', '090-3102-7114', '京都大学', '2004-10-06', 'https://lesson01.myou-kou.com/avatars/defaultAvatar14.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2023-12-16T20:45:53', '2023-12-16T20:45:53', 'email', 1, 0, 
    44, 10, 10,
    40, 10, 46,
    'paper', 'G:W,G:W,P:L,P:D,G:W',
    7, 1, 2,
    'title_001', 'title_001', 'rest',
    TRUE, TRUE,
    'silver', '2025-05-02'
);
INSERT INTO temp_user_data VALUES (
    'user033', 'user033@example.com', 'password033', '石川 翼', 'フェザリー', '787-9720', '福島県足立区藤井 Street4-3-10', '090-2820-9356', '同志社大学', '2004-08-27', 'https://lesson01.myou-kou.com/avatars/defaultAvatar15.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2022-03-09T06:23:15', '2022-03-09T06:23:15', 'email', 1, 0, 
    87, 2, 8,
    0, 28, 1,
    'scissors', 'S:L,P:D,P:L,P:D,G:L',
    9, 9, 2,
    'title_003', 'title_005,title_002', 'majority',
    TRUE, TRUE,
    'silver', '2025-05-01'
);
INSERT INTO temp_user_data VALUES (
    'user034', 'user034@example.com', 'password034', '井上 舞', 'エレクター', '468-2175', '福井県長生郡白子町木村 Street7-3-5', '090-2096-1121', '筑波大学', '2003-05-12', 'https://lesson01.myou-kou.com/avatars/defaultAvatar16.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2022-09-26T14:55:38', '2022-09-26T14:55:38', 'email', 1, 0, 
    9, 0, 7,
    15, 18, 16,
    'scissors', 'P:W,G:L,S:L,P:L,S:L',
    4, 3, 1,
    'title_004', 'title_003,title_003', 'within',
    TRUE, TRUE,
    'silver', '2025-05-05'
);
INSERT INTO temp_user_data VALUES (
    'user035', 'user035@example.com', 'password035', '中村 直子', 'ルミナス', '728-9805', '岩手県印西市木村 Street3-3-2', '090-1719-1888', '一橋大学', '2001-06-28', 'https://lesson01.myou-kou.com/avatars/defaultAvatar17.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2024-01-05T03:53:07', '2024-01-05T03:53:07', 'email', 1, 0, 
    153, 8, 4,
    28, 30, 38,
    'paper', 'S:L,S:L,P:W,G:D,P:D',
    7, 3, 3,
    'title_001', 'title_003,title_002', 'although',
    TRUE, TRUE,
    'no_rank', '2025-05-04'
);
INSERT INTO temp_user_data VALUES (
    'user036', 'user036@example.com', 'password036', '田中 稔', 'スプラッシュ', '314-9608', '愛知県御蔵島村佐藤 Street9-7-5', '090-4982-2987', '九州大学', '1999-05-25', 'https://lesson01.myou-kou.com/avatars/defaultAvatar18.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2021-08-01T00:31:57', '2021-08-01T00:31:57', 'email', 1, 0, 
    151, 10, 4,
    41, 38, 9,
    'rock', 'S:W,S:W,S:W,G:D,G:L',
    5, 3, 2,
    'title_002', 'title_002', 'kid',
    TRUE, TRUE,
    'no_rank', '2025-05-02'
);
INSERT INTO temp_user_data VALUES (
    'user037', 'user037@example.com', 'password037', '山田 美加子', 'ビリビリ', '485-2269', '富山県国立市藤田 Street10-7-1', '090-7822-3276', '関西学院大学', '2004-01-06', 'https://lesson01.myou-kou.com/avatars/defaultAvatar1.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2024-03-15T04:49:01', '2024-03-15T04:49:01', 'email', 1, 0, 
    184, 2, 0,
    11, 7, 22,
    'paper', 'S:L,S:D,P:D,G:L,G:D',
    2, 4, 5,
    'title_004', 'title_004,title_004,title_002', 'modern',
    TRUE, TRUE,
    'silver', '2025-05-03'
);
INSERT INTO temp_user_data VALUES (
    'user038', 'user038@example.com', 'password038', '伊藤 裕樹', 'シリウス', '950-8363', '京都府港区斉藤 Street5-9-9', '090-2871-2042', '法政大学', '1996-07-03', 'https://lesson01.myou-kou.com/avatars/defaultAvatar2.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2022-02-16T18:43:39', '2022-02-16T18:43:39', 'email', 1, 0, 
    49, 0, 13,
    23, 19, 29,
    'paper', 'S:D,P:W,S:W,S:W,P:D',
    8, 3, 4,
    'title_002', 'title_001', 'task',
    TRUE, TRUE,
    'bronze', '2025-05-02'
);
INSERT INTO temp_user_data VALUES (
    'user039', 'user039@example.com', 'password039', '岡本 直樹', 'パラゴン', '797-2832', '奈良県横浜市緑区福田 Street4-6-5', '090-6642-1712', '法政大学', '1995-10-06', 'https://lesson01.myou-kou.com/avatars/defaultAvatar3.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2025-01-30T07:21:57', '2025-01-30T07:21:57', 'email', 1, 0, 
    88, 7, 2,
    5, 29, 2,
    'scissors', 'S:L,S:D,P:W,P:W,G:L',
    0, 7, 2,
    'title_003', 'title_003,title_003,title_001', 'fast',
    TRUE, TRUE,
    'silver', '2025-05-01'
);
INSERT INTO temp_user_data VALUES (
    'user040', 'user040@example.com', 'password040', '中島 晃', 'サンライズ', '306-4070', '香川県横浜市鶴見区松本 Street7-7-7', '090-7601-2002', '大阪大学', '2003-12-31', 'https://lesson01.myou-kou.com/avatars/defaultAvatar4.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2024-02-26T09:20:21', '2024-02-26T09:20:21', 'email', 1, 0, 
    74, 1, 9,
    39, 49, 9,
    'scissors', 'G:L,G:L,P:D,S:D,G:L',
    3, 0, 5,
    'title_003', 'title_001,title_003,title_002', 'church',
    TRUE, TRUE,
    'no_rank', '2025-05-05'
);
INSERT INTO temp_user_data VALUES (
    'user041', 'user041@example.com', 'password041', '山崎 幹', 'スノーバード', '136-4653', '群馬県神津島村田中 Street2-6-6', '090-2383-4568', '琉球大学', '2004-05-10', 'https://lesson01.myou-kou.com/avatars/defaultAvatar5.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2025-02-21T20:10:07', '2025-02-21T20:10:07', 'email', 1, 0, 
    40, 10, 6,
    31, 40, 7,
    'scissors', 'S:D,P:D,S:D,G:D,S:L',
    8, 8, 1,
    'title_005', 'title_004', 'either',
    TRUE, TRUE,
    'bronze', '2025-05-02'
);
INSERT INTO temp_user_data VALUES (
    'user042', 'user042@example.com', 'password042', '藤原 香織', 'キャロットン', '382-9825', '兵庫県長生郡長柄町佐藤 Street8-5-6', '090-1178-3228', '慶應義塾大学', '2003-08-20', 'https://lesson01.myou-kou.com/avatars/defaultAvatar6.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2022-12-02T03:48:08', '2022-12-02T03:48:08', 'email', 1, 0, 
    60, 6, 17,
    47, 8, 26,
    'rock', 'G:W,G:D,G:W,S:L,S:W',
    1, 9, 2,
    'title_004', 'title_004,title_004', 'travel',
    TRUE, TRUE,
    'silver', '2025-05-06'
);
INSERT INTO temp_user_data VALUES (
    'user043', 'user043@example.com', 'password043', '藤田 晃', 'フェザリー', '304-5430', '群馬県西多摩郡日の出町伊藤 Street9-5-6', '090-2028-9859', '法政大学', '2002-06-20', 'https://lesson01.myou-kou.com/avatars/defaultAvatar7.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2022-04-02T00:36:43', '2022-04-02T00:36:43', 'email', 1, 0, 
    167, 8, 14,
    45, 7, 28,
    'rock', 'S:L,S:W,P:D,S:L,P:W',
    9, 8, 3,
    'title_001', 'title_001,title_001', 'thank',
    TRUE, TRUE,
    'no_rank', '2025-05-03'
);
INSERT INTO temp_user_data VALUES (
    'user044', 'user044@example.com', 'password044', '藤田 亮介', 'ポッポロン', '177-4789', '香川県長生郡睦沢町鈴木 Street10-5-10', '090-4380-4431', '大阪大学', '2002-04-24', 'https://lesson01.myou-kou.com/avatars/defaultAvatar8.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2022-12-31T06:45:26', '2022-12-31T06:45:26', 'email', 1, 0, 
    163, 6, 2,
    46, 30, 20,
    'rock', 'G:D,S:L,S:D,G:W,S:D',
    9, 6, 0,
    'title_005', 'title_005', 'each',
    TRUE, TRUE,
    'silver', '2025-05-06'
);
INSERT INTO temp_user_data VALUES (
    'user045', 'user045@example.com', 'password045', '石井 あすか', 'ファルコン', '949-8557', '長野県青ヶ島村石川 Street8-4-1', '090-6763-5213', '一橋大学', '2000-09-02', 'https://lesson01.myou-kou.com/avatars/defaultAvatar9.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2025-02-01T02:04:22', '2025-02-01T02:04:22', 'email', 1, 0, 
    187, 5, 2,
    9, 45, 44,
    'scissors', 'S:D,P:D,G:D,P:L,S:W',
    1, 10, 1,
    'title_001', 'title_002', 'recognize',
    TRUE, TRUE,
    'no_rank', '2025-05-04'
);
INSERT INTO temp_user_data VALUES (
    'user046', 'user046@example.com', 'password046', '石川 千代', 'ビートラン', '269-9962', '宮崎県横浜市青葉区藤原 Street3-1-8', '090-2775-4686', '明治大学', '1999-04-19', 'https://lesson01.myou-kou.com/avatars/defaultAvatar10.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2023-03-04T10:48:47', '2023-03-04T10:48:47', 'email', 1, 0, 
    112, 0, 1,
    18, 13, 39,
    'paper', 'S:W,S:W,S:D,P:W,G:W',
    1, 7, 4,
    'title_004', 'title_001', 'decade',
    TRUE, TRUE,
    'gold', '2025-05-03'
);
INSERT INTO temp_user_data VALUES (
    'user047', 'user047@example.com', 'password047', '山崎 さゆり', 'マッハウルフ', '549-1928', '埼玉県印旛郡栄町佐藤 Street7-10-1', '090-8827-4233', '中央大学', '2005-02-07', 'https://lesson01.myou-kou.com/avatars/defaultAvatar11.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2024-03-20T15:43:04', '2024-03-20T15:43:04', 'email', 1, 0, 
    85, 4, 5,
    50, 30, 7,
    'rock', 'P:L,P:D,S:L,S:W,S:W',
    5, 6, 0,
    'title_002', 'title_003,title_001', 'help',
    TRUE, TRUE,
    'bronze', '2025-05-05'
);
INSERT INTO temp_user_data VALUES (
    'user048', 'user048@example.com', 'password048', '高橋 浩', 'ブースター', '562-9523', '大阪府香取郡神崎町木村 Street9-6-3', '090-6119-2578', '慶應義塾大学', '2006-10-27', 'https://lesson01.myou-kou.com/avatars/defaultAvatar12.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2025-03-20T11:41:17', '2025-03-20T11:41:17', 'email', 1, 0, 
    112, 4, 14,
    5, 9, 47,
    'paper', 'S:D,P:W,S:W,S:L,S:W',
    4, 1, 5,
    'title_002', 'title_003,title_004', 'yard',
    TRUE, TRUE,
    'gold', '2025-05-01'
);
INSERT INTO temp_user_data VALUES (
    'user049', 'user049@example.com', 'password049', '加藤 明美', 'ギガコア', '655-9044', '鹿児島県鎌ケ谷市藤田 Street8-2-1', '090-8695-2081', '岡山大学', '1995-10-19', 'https://lesson01.myou-kou.com/avatars/defaultAvatar13.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2022-03-08T21:50:57', '2022-03-08T21:50:57', 'email', 1, 0, 
    184, 1, 17,
    49, 35, 46,
    'rock', 'P:L,S:L,S:D,S:D,G:D',
    2, 7, 2,
    'title_003', 'title_005,title_003,title_004', 'clear',
    TRUE, TRUE,
    'silver', '2025-05-01'
);
INSERT INTO temp_user_data VALUES (
    'user050', 'user050@example.com', 'password050', '鈴木 裕太', 'ライトスピア', '783-5185', '群馬県横浜市青葉区青木 Street6-2-2', '090-1927-7235', '琉球大学', '1999-11-29', 'https://lesson01.myou-kou.com/avatars/defaultAvatar14.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2024-03-28T13:53:09', '2024-03-28T13:53:09', 'email', 1, 0, 
    83, 7, 13,
    40, 25, 8,
    'rock', 'P:W,G:D,G:D,G:W,P:D',
    0, 1, 1,
    'title_004', 'title_002', 'individual',
    TRUE, TRUE,
    'no_rank', '2025-05-02'
);
INSERT INTO temp_user_data VALUES (
    'user051', 'user051@example.com', 'password051', '村上 亮介', 'キャロットン', '460-1646', '岐阜県横浜市都筑区山口 Street3-9-6', '090-7474-3187', '同志社大学', '1997-11-13', 'https://lesson01.myou-kou.com/avatars/defaultAvatar15.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2024-11-29T20:37:33', '2024-11-29T20:37:33', 'email', 1, 0, 
    199, 10, 11,
    15, 40, 28,
    'scissors', 'S:D,G:W,G:L,S:D,G:W',
    0, 7, 4,
    'title_004', 'title_005,title_001', 'again',
    TRUE, TRUE,
    'gold', '2025-05-01'
);
INSERT INTO temp_user_data VALUES (
    'user052', 'user052@example.com', 'password052', '高橋 京助', 'マッハウルフ', '593-1566', '東京都西多摩郡奥多摩町山崎 Street3-8-2', '090-6639-5495', '東京大学', '2001-12-18', 'https://lesson01.myou-kou.com/avatars/defaultAvatar16.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2022-11-12T06:53:37', '2022-11-12T06:53:37', 'email', 1, 0, 
    94, 1, 6,
    37, 40, 25,
    'scissors', 'G:W,G:L,P:D,P:W,P:L',
    4, 7, 5,
    'title_005', 'title_005', 'person',
    TRUE, TRUE,
    'silver', '2025-05-05'
);
INSERT INTO temp_user_data VALUES (
    'user053', 'user053@example.com', 'password053', '中村 花子', 'ブリッツ', '424-6831', '富山県横浜市都筑区山田 Street9-8-10', '090-6942-2727', '同志社大学', '2002-11-01', 'https://lesson01.myou-kou.com/avatars/defaultAvatar17.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2023-10-08T15:34:27', '2023-10-08T15:34:27', 'email', 1, 0, 
    181, 2, 15,
    38, 30, 28,
    'rock', 'S:L,G:W,P:L,S:W,S:L',
    7, 2, 0,
    'title_001', 'title_003,title_004', 'structure',
    TRUE, TRUE,
    'gold', '2025-05-06'
);
INSERT INTO temp_user_data VALUES (
    'user054', 'user054@example.com', 'password054', '小川 くみ子', 'ネオバード', '856-3416', '岡山県西東京市山田 Street5-2-3', '090-2889-8778', '早稲田大学', '2001-08-05', 'https://lesson01.myou-kou.com/avatars/defaultAvatar18.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2023-06-29T21:45:42', '2023-06-29T21:45:42', 'email', 1, 0, 
    162, 10, 19,
    30, 29, 30,
    'rock', 'G:W,S:D,S:L,P:W,P:W',
    0, 4, 4,
    'title_001', 'title_001', 'two',
    TRUE, TRUE,
    'gold', '2025-05-01'
);
INSERT INTO temp_user_data VALUES (
    'user055', 'user055@example.com', 'password055', '伊藤 翔太', 'ポチマル', '850-7300', '高知県品川区岡田 Street1-8-5', '090-5961-9879', '京都大学', '2000-02-01', 'https://lesson01.myou-kou.com/avatars/defaultAvatar1.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2022-05-30T19:44:09', '2022-05-30T19:44:09', 'email', 1, 0, 
    27, 5, 19,
    4, 15, 11,
    'scissors', 'G:L,G:D,P:W,S:D,G:W',
    2, 10, 0,
    'title_001', 'title_001,title_004', 'size',
    TRUE, TRUE,
    'no_rank', '2025-05-01'
);
INSERT INTO temp_user_data VALUES (
    'user056', 'user056@example.com', 'password056', '近藤 里佳', 'ファルコン', '983-9039', '沖縄県安房郡鋸南町小林 Street6-7-1', '090-8718-9716', '早稲田大学', '1999-10-04', 'https://lesson01.myou-kou.com/avatars/defaultAvatar2.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2024-05-07T15:44:53', '2024-05-07T15:44:53', 'email', 1, 0, 
    2, 2, 16,
    45, 25, 26,
    'rock', 'S:D,G:W,P:D,P:L,P:D',
    1, 3, 5,
    'title_003', 'title_005', 'fact',
    TRUE, TRUE,
    'silver', '2025-05-06'
);
INSERT INTO temp_user_data VALUES (
    'user057', 'user057@example.com', 'password057', '佐々木 くみ子', 'オメガス', '957-0789', '石川県長生郡白子町岡本 Street5-4-9', '090-3297-5418', '琉球大学', '2006-04-19', 'https://lesson01.myou-kou.com/avatars/defaultAvatar3.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2023-07-26T17:23:20', '2023-07-26T17:23:20', 'email', 1, 0, 
    88, 5, 0,
    28, 10, 42,
    'paper', 'P:D,P:D,S:W,G:W,G:D',
    0, 5, 3,
    'title_002', 'title_005,title_004,title_001', 'stay',
    TRUE, TRUE,
    'silver', '2025-05-04'
);
INSERT INTO temp_user_data VALUES (
    'user058', 'user058@example.com', 'password058', '斉藤 翔太', 'ノイズラー', '974-9151', '愛知県印旛郡本埜村藤井 Street2-10-6', '090-8205-2678', '立命館大学', '1996-03-03', 'https://lesson01.myou-kou.com/avatars/defaultAvatar4.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2022-08-24T12:14:40', '2022-08-24T12:14:40', 'email', 1, 0, 
    135, 8, 5,
    3, 44, 20,
    'scissors', 'G:D,S:L,G:L,G:D,G:D',
    3, 6, 4,
    'title_002', 'title_001,title_003,title_004', 'weight',
    TRUE, TRUE,
    'bronze', '2025-05-02'
);
INSERT INTO temp_user_data VALUES (
    'user059', 'user059@example.com', 'password059', '渡辺 京助', 'フェザリー', '768-1630', '鹿児島県新宿区山口 Street9-3-4', '090-2002-8262', '熊本大学', '2001-02-10', 'https://lesson01.myou-kou.com/avatars/defaultAvatar5.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2024-03-16T04:16:46', '2024-03-16T04:16:46', 'email', 1, 0, 
    49, 10, 7,
    12, 10, 13,
    'paper', 'S:W,P:D,P:D,S:L,G:W',
    5, 1, 5,
    'title_003', 'title_001', 'will',
    TRUE, TRUE,
    'silver', '2025-05-03'
);
INSERT INTO temp_user_data VALUES (
    'user060', 'user060@example.com', 'password060', '山本 太郎', 'ダンディガー', '837-6622', '滋賀県西多摩郡瑞穂町佐藤 Street2-1-9', '090-4655-5182', '法政大学', '1998-09-26', 'https://lesson01.myou-kou.com/avatars/defaultAvatar6.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2020-08-07T06:47:19', '2020-08-07T06:47:19', 'email', 1, 0, 
    174, 3, 16,
    50, 48, 42,
    'rock', 'G:W,G:D,G:D,P:W,S:D',
    2, 10, 0,
    'title_005', 'title_004', 'word',
    TRUE, TRUE,
    'no_rank', '2025-05-06'
);
INSERT INTO temp_user_data VALUES (
    'user061', 'user061@example.com', 'password061', '中村 翼', 'ウィスパー', '944-5013', '沖縄県香取郡東庄町中村 Street6-8-2', '090-6080-5002', '上智大学', '2005-06-19', 'https://lesson01.myou-kou.com/avatars/defaultAvatar7.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2023-07-25T18:12:53', '2023-07-25T18:12:53', 'email', 1, 0, 
    45, 5, 11,
    13, 1, 10,
    'rock', 'P:W,S:W,G:W,S:L,P:L',
    9, 4, 3,
    'title_004', 'title_005,title_004', 'blue',
    TRUE, TRUE,
    'bronze', '2025-05-02'
);
INSERT INTO temp_user_data VALUES (
    'user062', 'user062@example.com', 'password062', '林 翔太', 'ドラゴネス', '892-0711', '群馬県印旛郡印旛村高橋 Street4-9-10', '090-4249-8208', '熊本大学', '1996-02-26', 'https://lesson01.myou-kou.com/avatars/defaultAvatar8.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2024-03-29T16:08:52', '2024-03-29T16:08:52', 'email', 1, 0, 
    157, 3, 16,
    46, 31, 50,
    'paper', 'P:W,S:L,S:W,P:D,P:W',
    3, 0, 2,
    'title_005', 'title_005,title_005,title_004', 'may',
    TRUE, TRUE,
    'bronze', '2025-05-01'
);
INSERT INTO temp_user_data VALUES (
    'user063', 'user063@example.com', 'password063', '佐藤 英樹', 'スノーバード', '633-4383', '神奈川県足立区三浦 Street7-1-3', '090-8781-3400', '大阪大学', '2006-10-18', 'https://lesson01.myou-kou.com/avatars/defaultAvatar9.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2021-08-07T18:56:09', '2021-08-07T18:56:09', 'email', 1, 0, 
    35, 7, 19,
    22, 2, 23,
    'paper', 'G:L,G:L,S:D,P:D,S:L',
    10, 5, 1,
    'title_001', 'title_001,title_002,title_003', 'here',
    TRUE, TRUE,
    'bronze', '2025-05-04'
);
INSERT INTO temp_user_data VALUES (
    'user064', 'user064@example.com', 'password064', '伊藤 拓真', 'ブリッツ', '705-0875', '長崎県横浜市緑区渡辺 Street1-8-9', '090-8158-4484', '京都大学', '2003-10-20', 'https://lesson01.myou-kou.com/avatars/defaultAvatar10.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2020-04-18T12:49:53', '2020-04-18T12:49:53', 'email', 1, 0, 
    59, 3, 2,
    30, 17, 21,
    'rock', 'P:W,G:W,P:D,G:W,S:D',
    4, 0, 1,
    'title_004', 'title_001', 'step',
    TRUE, TRUE,
    'gold', '2025-05-01'
);
INSERT INTO temp_user_data VALUES (
    'user065', 'user065@example.com', 'password065', '田中 桃子', 'フェザリー', '383-6235', '神奈川県川崎市宮前区佐々木 Street8-9-4', '090-4265-7544', '大阪大学', '1997-06-21', 'https://lesson01.myou-kou.com/avatars/defaultAvatar11.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2023-08-19T15:48:01', '2023-08-19T15:48:01', 'email', 1, 0, 
    151, 7, 4,
    13, 32, 23,
    'scissors', 'S:L,G:L,P:D,S:D,P:L',
    8, 6, 5,
    'title_002', 'title_005,title_003', 'when',
    TRUE, TRUE,
    'no_rank', '2025-05-04'
);
INSERT INTO temp_user_data VALUES (
    'user066', 'user066@example.com', 'password066', '高橋 裕太', 'ライトスピア', '461-7107', '岐阜県武蔵野市石川 Street8-8-10', '090-5481-5327', '九州大学', '1998-07-26', 'https://lesson01.myou-kou.com/avatars/defaultAvatar12.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2025-03-29T18:45:12', '2025-03-29T18:45:12', 'email', 1, 0, 
    71, 5, 2,
    27, 25, 13,
    'rock', 'P:L,S:L,P:L,S:L,S:L',
    9, 1, 3,
    'title_004', 'title_004,title_001', 'executive',
    TRUE, TRUE,
    'silver', '2025-05-05'
);
INSERT INTO temp_user_data VALUES (
    'user067', 'user067@example.com', 'password067', '田中 翼', 'リボルバー', '017-5405', '大分県我孫子市森 Street4-7-7', '090-3095-3949', '慶應義塾大学', '2006-08-15', 'https://lesson01.myou-kou.com/avatars/defaultAvatar13.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2023-06-03T07:38:38', '2023-06-03T07:38:38', 'email', 1, 0, 
    116, 2, 6,
    35, 39, 35,
    'scissors', 'G:D,S:L,G:W,S:D,P:L',
    10, 10, 0,
    'title_004', 'title_001', 'process',
    TRUE, TRUE,
    'bronze', '2025-05-04'
);
INSERT INTO temp_user_data VALUES (
    'user068', 'user068@example.com', 'password068', '太田 里佳', 'ニャンタス', '439-2800', '高知県川崎市川崎区藤井 Street5-5-3', '090-3070-5084', '名古屋大学', '2003-11-11', 'https://lesson01.myou-kou.com/avatars/defaultAvatar14.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2024-10-22T17:39:29', '2024-10-22T17:39:29', 'email', 1, 0, 
    119, 0, 4,
    21, 29, 31,
    'paper', 'G:L,G:W,P:L,S:W,G:D',
    9, 10, 4,
    'title_001', 'title_004,title_005,title_001', 'gas',
    TRUE, TRUE,
    'no_rank', '2025-05-01'
);
INSERT INTO temp_user_data VALUES (
    'user069', 'user069@example.com', 'password069', '伊藤 京助', 'ペンギナー', '568-0387', '山形県横浜市西区斉藤 Street7-3-5', '090-2930-3988', '上智大学', '1997-04-27', 'https://lesson01.myou-kou.com/avatars/defaultAvatar15.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2021-06-03T13:44:46', '2021-06-03T13:44:46', 'email', 1, 0, 
    188, 6, 11,
    11, 35, 30,
    'scissors', 'P:L,P:D,G:W,G:D,P:W',
    5, 5, 3,
    'title_003', 'title_004,title_003', 'explain',
    TRUE, TRUE,
    'no_rank', '2025-05-06'
);
INSERT INTO temp_user_data VALUES (
    'user070', 'user070@example.com', 'password070', '長谷川 さゆり', 'リザルトン', '804-4574', '群馬県横浜市港南区山本 Street7-10-7', '090-1485-3351', '京都大学', '2006-01-19', 'https://lesson01.myou-kou.com/avatars/defaultAvatar16.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2020-02-19T12:20:02', '2020-02-19T12:20:02', 'email', 1, 0, 
    134, 1, 3,
    38, 42, 33,
    'scissors', 'P:L,G:L,G:W,G:L,P:L',
    2, 9, 5,
    'title_004', 'title_002,title_003', 'add',
    TRUE, TRUE,
    'bronze', '2025-05-03'
);
INSERT INTO temp_user_data VALUES (
    'user071', 'user071@example.com', 'password071', '鈴木 稔', 'スカイロア', '298-7667', '大阪府東村山市村上 Street3-4-1', '090-4327-9023', '熊本大学', '1997-05-21', 'https://lesson01.myou-kou.com/avatars/defaultAvatar17.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2023-01-01T16:14:37', '2023-01-01T16:14:37', 'email', 1, 0, 
    176, 7, 15,
    4, 10, 5,
    'scissors', 'S:D,P:W,G:L,P:D,S:W',
    9, 7, 0,
    'title_004', 'title_002,title_005', 'form',
    TRUE, TRUE,
    'gold', '2025-05-02'
);
INSERT INTO temp_user_data VALUES (
    'user072', 'user072@example.com', 'password072', '田中 あすか', 'ファルコン', '526-8587', '鹿児島県横浜市青葉区渡辺 Street9-6-10', '090-1628-3255', '大阪大学', '2002-10-16', 'https://lesson01.myou-kou.com/avatars/defaultAvatar18.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2024-02-21T23:06:59', '2024-02-21T23:06:59', 'email', 1, 0, 
    0, 7, 17,
    25, 29, 11,
    'scissors', 'G:W,S:L,S:W,P:L,S:L',
    6, 3, 3,
    'title_001', 'title_002,title_005,title_003', 'sit',
    TRUE, TRUE,
    'gold', '2025-05-05'
);
INSERT INTO temp_user_data VALUES (
    'user073', 'user073@example.com', 'password073', '鈴木 翼', 'ビートラン', '455-0111', '北海道府中市高橋 Street6-1-6', '090-9222-1543', '京都大学', '2006-11-02', 'https://lesson01.myou-kou.com/avatars/defaultAvatar1.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2024-03-26T20:55:39', '2024-03-26T20:55:39', 'email', 1, 0, 
    126, 7, 7,
    37, 42, 44,
    'paper', 'P:D,G:W,P:D,G:W,S:D',
    3, 3, 4,
    'title_002', 'title_003,title_004,title_005', 'main',
    TRUE, TRUE,
    'no_rank', '2025-05-01'
);
INSERT INTO temp_user_data VALUES (
    'user074', 'user074@example.com', 'password074', '中村 舞', 'コスモス', '712-3756', '兵庫県あきる野市坂本 Street6-7-4', '090-1734-9494', '法政大学', '1998-03-01', 'https://lesson01.myou-kou.com/avatars/defaultAvatar2.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2020-02-04T20:09:13', '2020-02-04T20:09:13', 'email', 1, 0, 
    194, 5, 8,
    6, 48, 49,
    'paper', 'G:D,G:W,P:L,G:W,G:W',
    1, 9, 3,
    'title_003', 'title_005', 'magazine',
    TRUE, TRUE,
    'gold', '2025-05-04'
);
INSERT INTO temp_user_data VALUES (
    'user075', 'user075@example.com', 'password075', '田中 裕太', 'ドラゴネス', '665-1526', '青森県大網白里市斎藤 Street3-3-7', '090-1097-9594', '琉球大学', '2003-03-22', 'https://lesson01.myou-kou.com/avatars/defaultAvatar3.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2022-07-10T15:12:55', '2022-07-10T15:12:55', 'email', 1, 0, 
    47, 0, 17,
    13, 12, 23,
    'paper', 'G:D,P:D,S:D,S:W,G:W',
    5, 10, 5,
    'title_002', 'title_004', 'still',
    TRUE, TRUE,
    'gold', '2025-05-05'
);
INSERT INTO temp_user_data VALUES (
    'user076', 'user076@example.com', 'password076', '池田 康弘', 'ペガサード', '112-3469', '神奈川県我孫子市山本 Street1-4-7', '090-2697-6979', '慶應義塾大学', '1996-06-12', 'https://lesson01.myou-kou.com/avatars/defaultAvatar4.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2023-09-28T08:51:27', '2023-09-28T08:51:27', 'email', 1, 0, 
    153, 9, 4,
    4, 20, 14,
    'scissors', 'P:L,S:L,P:D,S:W,G:W',
    1, 2, 1,
    'title_005', 'title_002', 'anything',
    TRUE, TRUE,
    'bronze', '2025-05-06'
);
INSERT INTO temp_user_data VALUES (
    'user077', 'user077@example.com', 'password077', '青木 直子', 'ニャンタス', '373-2664', '愛知県横浜市保土ケ谷区松本 Street6-6-8', '090-8418-8459', '九州大学', '2002-06-04', 'https://lesson01.myou-kou.com/avatars/defaultAvatar5.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2020-12-17T20:46:42', '2020-12-17T20:46:42', 'email', 1, 0, 
    158, 5, 0,
    39, 39, 1,
    'rock', 'S:D,P:L,S:L,S:L,S:W',
    9, 8, 3,
    'title_004', 'title_005,title_004,title_004', 'million',
    TRUE, TRUE,
    'bronze', '2025-05-06'
);
INSERT INTO temp_user_data VALUES (
    'user078', 'user078@example.com', 'password078', '中島 直樹', 'ギガコア', '903-5028', '茨城県東久留米市池田 Street4-3-3', '090-4217-7718', '立教大学', '1995-08-07', 'https://lesson01.myou-kou.com/avatars/defaultAvatar6.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2023-02-21T05:51:34', '2023-02-21T05:51:34', 'email', 1, 0, 
    70, 7, 8,
    11, 50, 8,
    'scissors', 'P:D,P:D,P:W,P:D,S:L',
    3, 9, 1,
    'title_002', 'title_003', 'middle',
    TRUE, TRUE,
    'no_rank', '2025-05-03'
);
INSERT INTO temp_user_data VALUES (
    'user079', 'user079@example.com', 'password079', '松田 香織', 'スプラッシュ', '582-6720', '兵庫県四街道市青木 Street3-7-1', '090-4012-9253', '琉球大学', '1999-06-20', 'https://lesson01.myou-kou.com/avatars/defaultAvatar7.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2021-03-02T09:00:47', '2021-03-02T09:00:47', 'email', 1, 0, 
    48, 10, 2,
    34, 28, 3,
    'rock', 'P:W,G:L,G:D,P:W,S:L',
    9, 0, 5,
    'title_001', 'title_001,title_003', 'west',
    TRUE, TRUE,
    'gold', '2025-05-06'
);
INSERT INTO temp_user_data VALUES (
    'user080', 'user080@example.com', 'password080', '林 春香', 'ビートラン', '254-2158', '北海道立川市村上 Street1-7-2', '090-1952-4200', '東京大学', '1995-09-08', 'https://lesson01.myou-kou.com/avatars/defaultAvatar8.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2020-12-07T00:27:47', '2020-12-07T00:27:47', 'email', 1, 0, 
    133, 8, 0,
    15, 8, 4,
    'rock', 'G:W,G:L,S:W,S:L,P:D',
    4, 10, 4,
    'title_001', 'title_002,title_005', 'and',
    TRUE, TRUE,
    'gold', '2025-05-04'
);
INSERT INTO temp_user_data VALUES (
    'user081', 'user081@example.com', 'password081', '田中 修平', 'リザルトン', '253-6092', '宮崎県小金井市山口 Street8-5-6', '090-8649-1705', '岡山大学', '1995-06-12', 'https://lesson01.myou-kou.com/avatars/defaultAvatar9.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2020-06-16T10:01:11', '2020-06-16T10:01:11', 'email', 1, 0, 
    6, 4, 10,
    33, 48, 23,
    'scissors', 'P:L,G:D,P:W,S:W,G:L',
    8, 6, 0,
    'title_004', 'title_002,title_001,title_004', 'source',
    TRUE, TRUE,
    'gold', '2025-05-05'
);
INSERT INTO temp_user_data VALUES (
    'user082', 'user082@example.com', 'password082', '佐藤 零', 'ミラクロン', '661-9551', '山梨県山武郡芝山町斉藤 Street3-2-9', '090-7846-3979', '東京大学', '2002-02-28', 'https://lesson01.myou-kou.com/avatars/defaultAvatar10.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2023-09-03T22:06:38', '2023-09-03T22:06:38', 'email', 1, 0, 
    20, 9, 10,
    34, 7, 12,
    'rock', 'S:W,S:W,S:D,G:L,S:D',
    6, 6, 0,
    'title_005', 'title_005,title_004,title_003', 'life',
    TRUE, TRUE,
    'gold', '2025-05-03'
);
INSERT INTO temp_user_data VALUES (
    'user083', 'user083@example.com', 'password083', '斎藤 亮介', 'ミラクロン', '343-0984', '島根県山武郡芝山町佐々木 Street5-2-7', '090-6123-5551', '岡山大学', '2001-05-24', 'https://lesson01.myou-kou.com/avatars/defaultAvatar11.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2020-03-06T04:56:26', '2020-03-06T04:56:26', 'email', 1, 0, 
    83, 3, 15,
    30, 1, 11,
    'rock', 'P:W,P:D,P:L,P:W,S:W',
    1, 7, 4,
    'title_004', 'title_002,title_002', 'point',
    TRUE, TRUE,
    'silver', '2025-05-04'
);
INSERT INTO temp_user_data VALUES (
    'user084', 'user084@example.com', 'password084', '高橋 七夏', 'オメガス', '167-1984', '島根県八丈島八丈町池田 Street3-10-7', '090-1794-3585', '熊本大学', '2000-06-22', 'https://lesson01.myou-kou.com/avatars/defaultAvatar12.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2023-01-15T20:13:33', '2023-01-15T20:13:33', 'email', 1, 0, 
    37, 7, 8,
    5, 24, 44,
    'paper', 'S:D,G:L,S:D,S:L,S:D',
    4, 1, 0,
    'title_003', 'title_004', 'partner',
    TRUE, TRUE,
    'silver', '2025-05-01'
);
INSERT INTO temp_user_data VALUES (
    'user085', 'user085@example.com', 'password085', '高橋 あすか', 'バレットン', '669-2232', '岡山県東村山市伊藤 Street3-5-10', '090-5890-8784', '東北大学', '1998-07-19', 'https://lesson01.myou-kou.com/avatars/defaultAvatar13.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2022-02-04T11:33:34', '2022-02-04T11:33:34', 'email', 1, 0, 
    122, 8, 13,
    35, 43, 32,
    'scissors', 'P:W,P:D,G:D,G:L,P:W',
    4, 2, 3,
    'title_002', 'title_001,title_002', 'gas',
    TRUE, TRUE,
    'bronze', '2025-05-04'
);
INSERT INTO temp_user_data VALUES (
    'user086', 'user086@example.com', 'password086', '後藤 裕樹', 'ファルコン', '784-1204', '京都府あきる野市田中 Street4-6-4', '090-8886-5587', '九州大学', '2001-12-08', 'https://lesson01.myou-kou.com/avatars/defaultAvatar14.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2024-06-20T21:27:21', '2024-06-20T21:27:21', 'email', 1, 0, 
    58, 3, 4,
    3, 16, 2,
    'scissors', 'G:L,G:W,P:W,S:W,S:L',
    3, 0, 2,
    'title_001', 'title_005,title_004,title_001', 'discover',
    TRUE, TRUE,
    'bronze', '2025-05-03'
);
INSERT INTO temp_user_data VALUES (
    'user087', 'user087@example.com', 'password087', '鈴木 七夏', 'ドラゴネス', '508-3510', '奈良県山武郡九十九里町井上 Street8-8-2', '090-6736-4720', '北海道大学', '1996-06-13', 'https://lesson01.myou-kou.com/avatars/defaultAvatar15.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2023-05-09T08:46:43', '2023-05-09T08:46:43', 'email', 1, 0, 
    55, 9, 16,
    7, 10, 11,
    'paper', 'P:D,G:D,S:L,G:D,P:W',
    7, 8, 0,
    'title_004', 'title_005', 'although',
    TRUE, TRUE,
    'bronze', '2025-05-06'
);
INSERT INTO temp_user_data VALUES (
    'user088', 'user088@example.com', 'password088', '佐々木 涼平', 'バレットン', '000-8826', '群馬県横浜市泉区高橋 Street6-9-7', '090-3679-5386', '東北大学', '2005-08-09', 'https://lesson01.myou-kou.com/avatars/defaultAvatar16.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2024-01-02T10:21:57', '2024-01-02T10:21:57', 'email', 1, 0, 
    32, 9, 10,
    39, 34, 28,
    'rock', 'G:D,G:D,S:W,G:D,G:D',
    7, 4, 4,
    'title_002', 'title_003,title_002,title_004', 'particular',
    TRUE, TRUE,
    'gold', '2025-05-05'
);
INSERT INTO temp_user_data VALUES (
    'user089', 'user089@example.com', 'password089', '佐々木 さゆり', 'ノイズラー', '959-2738', '長野県富津市鈴木 Street8-5-4', '090-8388-2408', '熊本大学', '1999-08-23', 'https://lesson01.myou-kou.com/avatars/defaultAvatar17.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2025-04-24T04:34:10', '2025-04-24T04:34:10', 'email', 1, 0, 
    63, 2, 20,
    47, 46, 30,
    'rock', 'P:W,P:D,S:W,P:D,G:D',
    7, 3, 5,
    'title_005', 'title_002', 'bag',
    TRUE, TRUE,
    'silver', '2025-05-02'
);
INSERT INTO temp_user_data VALUES (
    'user090', 'user090@example.com', 'password090', '遠藤 裕美子', 'シャイニャ', '310-8370', '島根県香取郡東庄町林 Street7-7-2', '090-5759-8981', '岡山大学', '2006-03-19', 'https://lesson01.myou-kou.com/avatars/defaultAvatar18.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2024-07-28T09:45:39', '2024-07-28T09:45:39', 'email', 1, 0, 
    31, 7, 4,
    38, 27, 29,
    'rock', 'P:L,P:W,G:W,G:W,S:D',
    3, 9, 1,
    'title_004', 'title_003', 'month',
    TRUE, TRUE,
    'silver', '2025-05-06'
);
INSERT INTO temp_user_data VALUES (
    'user091', 'user091@example.com', 'password091', '青木 花子', 'ニャンタス', '706-9926', '愛知県いすみ市森 Street2-10-3', '090-2419-5867', '明治大学', '1997-12-29', 'https://lesson01.myou-kou.com/avatars/defaultAvatar1.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2022-08-02T00:20:32', '2022-08-02T00:20:32', 'email', 1, 0, 
    128, 9, 20,
    31, 41, 14,
    'scissors', 'P:L,S:L,G:D,S:L,P:L',
    7, 10, 4,
    'title_004', 'title_002,title_002,title_002', 'military',
    TRUE, TRUE,
    'bronze', '2025-05-06'
);
INSERT INTO temp_user_data VALUES (
    'user092', 'user092@example.com', 'password092', '小林 香織', 'ネオバード', '160-5403', '長野県利島村長谷川 Street7-10-3', '090-3402-6447', '岡山大学', '2006-07-02', 'https://lesson01.myou-kou.com/avatars/defaultAvatar2.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2020-02-09T20:05:24', '2020-02-09T20:05:24', 'email', 1, 0, 
    111, 4, 11,
    28, 21, 30,
    'paper', 'P:D,S:D,G:W,S:D,P:L',
    10, 3, 5,
    'title_003', 'title_001,title_001,title_002', 'responsibility',
    TRUE, TRUE,
    'silver', '2025-05-04'
);
INSERT INTO temp_user_data VALUES (
    'user093', 'user093@example.com', 'password093', '鈴木 稔', 'ウィスパー', '571-3234', '栃木県富里市鈴木 Street9-1-2', '090-4743-7860', '名古屋大学', '2003-04-06', 'https://lesson01.myou-kou.com/avatars/defaultAvatar3.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2022-10-26T19:15:34', '2022-10-26T19:15:34', 'email', 1, 0, 
    83, 4, 7,
    40, 45, 10,
    'scissors', 'G:W,S:L,P:W,S:D,S:W',
    6, 7, 3,
    'title_002', 'title_005,title_001,title_003', 'out',
    TRUE, TRUE,
    'no_rank', '2025-05-05'
);
INSERT INTO temp_user_data VALUES (
    'user094', 'user094@example.com', 'password094', '清水 亮介', 'ガラクタス', '754-4367', '長崎県国立市高橋 Street3-4-5', '090-9628-1312', '名古屋大学', '2002-06-21', 'https://lesson01.myou-kou.com/avatars/defaultAvatar4.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2020-01-29T08:33:45', '2020-01-29T08:33:45', 'email', 1, 0, 
    4, 3, 19,
    31, 45, 11,
    'scissors', 'S:L,G:L,P:W,S:L,G:D',
    0, 0, 0,
    'title_004', 'title_003', 'a',
    TRUE, TRUE,
    'gold', '2025-05-01'
);
INSERT INTO temp_user_data VALUES (
    'user095', 'user095@example.com', 'password095', '坂本 直子', 'フェザリー', '258-8051', '兵庫県三鷹市山本 Street4-8-5', '090-6788-2409', '筑波大学', '1996-02-28', 'https://lesson01.myou-kou.com/avatars/defaultAvatar5.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2024-02-09T03:39:18', '2024-02-09T03:39:18', 'email', 1, 0, 
    59, 2, 16,
    17, 1, 5,
    'rock', 'P:L,G:W,G:W,S:L,P:D',
    9, 7, 0,
    'title_002', 'title_001,title_004,title_001', 'cold',
    TRUE, TRUE,
    'gold', '2025-05-04'
);
INSERT INTO temp_user_data VALUES (
    'user096', 'user096@example.com', 'password096', '清水 太一', 'アストロン', '572-7754', '秋田県羽村市佐藤 Street10-10-7', '090-4688-5180', '立命館大学', '2001-09-19', 'https://lesson01.myou-kou.com/avatars/defaultAvatar6.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2021-11-16T20:33:03', '2021-11-16T20:33:03', 'email', 1, 0, 
    95, 5, 19,
    13, 0, 9,
    'rock', 'S:W,P:L,P:W,G:L,P:L',
    9, 4, 2,
    'title_004', 'title_005,title_001', 'price',
    TRUE, TRUE,
    'silver', '2025-05-05'
);
INSERT INTO temp_user_data VALUES (
    'user097', 'user097@example.com', 'password097', '橋本 太郎', 'ブリッツ', '850-9272', '佐賀県横浜市港北区山本 Street4-3-6', '090-2301-8722', '明治大学', '2000-11-18', 'https://lesson01.myou-kou.com/avatars/defaultAvatar7.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2022-06-18T00:05:44', '2022-06-18T00:05:44', 'email', 1, 0, 
    6, 5, 8,
    8, 21, 10,
    'scissors', 'S:L,P:W,P:W,G:D,P:D',
    2, 4, 2,
    'title_001', 'title_005,title_002', 'skill',
    TRUE, TRUE,
    'silver', '2025-05-05'
);
INSERT INTO temp_user_data VALUES (
    'user098', 'user098@example.com', 'password098', '木村 晃', 'ピクシード', '769-0379', '山口県印旛郡栄町井上 Street8-7-2', '090-8042-6060', '中央大学', '2003-11-29', 'https://lesson01.myou-kou.com/avatars/defaultAvatar8.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2021-03-16T18:01:35', '2021-03-16T18:01:35', 'email', 1, 0, 
    116, 7, 11,
    18, 0, 6,
    'rock', 'S:L,G:L,S:D,P:L,G:D',
    6, 8, 2,
    'title_001', 'title_002,title_005', 'should',
    TRUE, TRUE,
    'gold', '2025-05-04'
);
INSERT INTO temp_user_data VALUES (
    'user099', 'user099@example.com', 'password099', '小林 美加子', 'スノーバード', '860-2147', '長崎県大田区橋本 Street10-8-5', '090-5041-7606', '筑波大学', '1998-04-30', 'https://lesson01.myou-kou.com/avatars/defaultAvatar9.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2024-01-28T14:15:46', '2024-01-28T14:15:46', 'email', 1, 0, 
    122, 8, 13,
    38, 6, 45,
    'paper', 'G:W,S:L,P:D,P:W,P:W',
    8, 7, 4,
    'title_002', 'title_003,title_004', 'their',
    TRUE, TRUE,
    'bronze', '2025-05-06'
);
INSERT INTO temp_user_data VALUES (
    'user100', 'user100@example.com', 'password100', '西村 浩', 'ブリッツ', '300-3946', '三重県北区小林 Street3-10-1', '090-1789-3119', '関西学院大学', '1996-02-12', 'https://lesson01.myou-kou.com/avatars/defaultAvatar10.png', 'https://lesson01.myou-kou.com/avatars/defaultStudentId.png', '2021-12-27T05:53:36', '2021-12-27T05:53:36', 'email', 1, 0, 
    25, 7, 13,
    33, 48, 35,
    'scissors', 'G:W,P:L,S:D,G:W,P:D',
    9, 6, 2,
    'title_003', 'title_003', 'mother',
    TRUE, TRUE,
    'silver', '2025-05-01'
);

-- usersテーブルにデータを移行
INSERT INTO users (
    user_id, email, password, name, nickname,
    postal_code, address, phone_number, university,
    birthdate, profile_image_url, student_id_image_url,
    created_at, updated_at, register_type,
    is_student_id_editable, is_banned
)
SELECT
    user_id, email, password, name, nickname,
    postal_code, address, phone_number, university,
    birthdate, profile_image_url, student_id_image_url,
    created_at, updated_at, register_type,
    is_student_id_editable, is_banned
FROM temp_user_data;

-- user_statsテーブルにデータを移行
INSERT INTO user_stats (
    management_code, user_id, total_wins, current_win_streak, max_win_streak,
    hand_stats_rock, hand_stats_scissors, hand_stats_paper,
    favorite_hand, recent_hand_results_str,
    daily_wins, daily_losses, daily_draws,
    title, available_titles, alias, show_title, show_alias,
    user_rank, last_reset_at
)
SELECT
    u.management_code, t.user_id, t.total_wins, t.current_win_streak, t.max_win_streak,
    t.hand_stats_rock, t.hand_stats_scissors, t.hand_stats_paper,
    t.favorite_hand, t.recent_hand_results_str,
    t.daily_wins, t.daily_losses, t.daily_draws,
    t.title, t.available_titles, t.alias, t.show_title, t.show_alias,
    t.user_rank, t.last_reset_at
FROM temp_user_data t
JOIN users u ON u.user_id = t.user_id;

-- 一時テーブルを削除
DROP TEMPORARY TABLE temp_user_data;

COMMIT;