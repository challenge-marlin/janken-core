"""
初期マイグレーション - 基本認証システム
DB仕様書に基づく完全版
"""

from sqlalchemy import text
from sqlalchemy.engine import Connection
from typing import Dict, Any

class InitialMigration:
    """基本認証システムのテーブル作成"""
    
    @staticmethod
    def up(connection: Connection) -> None:
        """マイグレーション実行"""
        
        print("✅ 初期マイグレーション開始: 基本認証システム")
        
        # 1. ユーザー基本情報
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                management_code BIGINT AUTO_INCREMENT UNIQUE,
                user_id VARCHAR(50) PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                nickname VARCHAR(100) NOT NULL,
                name VARCHAR(50),
                role ENUM('user', 'developer', 'admin') DEFAULT 'user',
                profile_image_url VARCHAR(500),
                title VARCHAR(100) DEFAULT 'じゃんけんプレイヤー',
                alias VARCHAR(100),
                is_active BOOLEAN DEFAULT TRUE,
                is_banned TINYINT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_email (email),
                INDEX idx_role (role),
                INDEX idx_created_at (created_at),
                INDEX idx_management_code (management_code)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """))
        print("✅ usersテーブル作成完了")
        
        # 2. ユーザー詳細プロフィール
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id VARCHAR(50) PRIMARY KEY,
                postal_code VARCHAR(10),
                address VARCHAR(255),
                phone_number VARCHAR(15),
                university VARCHAR(100),
                birthdate DATE,
                student_id_image_url VARCHAR(500),
                is_student_id_editable TINYINT DEFAULT 0,
                register_type VARCHAR(20) DEFAULT 'email',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                INDEX idx_university (university),
                INDEX idx_birthdate (birthdate)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """))
        print("✅ user_profilesテーブル作成完了")
        
        # 3. 認証資格情報
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS auth_credentials (
                user_id VARCHAR(50) NOT NULL,
                password_hash VARCHAR(255) NULL,
                password_algo ENUM('argon2id','bcrypt','scrypt') DEFAULT 'argon2id',
                password_version SMALLINT DEFAULT 1,
                password_updated_at TIMESTAMP NULL,
                is_password_enabled BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id),
                CONSTRAINT fk_authcred_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """))
        print("✅ auth_credentialsテーブル作成完了")
        
        # 4. 端末管理
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS user_devices (
                device_id VARCHAR(128) PRIMARY KEY,
                user_id VARCHAR(50) NOT NULL,
                subnum INT NOT NULL DEFAULT 1,
                itemtype TINYINT NOT NULL DEFAULT 0,
                device_name VARCHAR(100),
                device_info JSON,
                is_active BOOLEAN DEFAULT TRUE,
                last_used_at TIMESTAMP NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                UNIQUE KEY uniq_user_subnum (user_id, subnum),
                INDEX idx_user_id (user_id),
                INDEX idx_device_type (itemtype),
                INDEX idx_last_used (last_used_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """))
        print("✅ user_devicesテーブル作成完了")
        
        print("✅ 初期マイグレーション完了: ユーザー・認証基盤")
    
    @staticmethod
    def down(connection: Connection) -> None:
        """マイグレーション取り消し"""
        
        tables = [
            'user_devices',
            'auth_credentials', 
            'user_profiles',
            'users'
        ]
        
        for table in tables:
            connection.execute(text(f"DROP TABLE IF EXISTS {table}"))
        
        print("✅ 初期マイグレーション取り消し完了")
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        """マイグレーション情報"""
        return {
            'name': '001_initial_migration',
            'description': '基本認証システム（ユーザー・プロフィール・認証・端末管理）',
            'tables': ['users', 'user_profiles', 'auth_credentials', 'user_devices'],
            'dependencies': []
        }
