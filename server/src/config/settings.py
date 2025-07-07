"""
アプリケーション設定

Pydantic Settingsを使用した設定管理
"""

import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """アプリケーション設定クラス"""
    
    # アプリケーション基本設定
    app_name: str = Field(default="Kaminote Janken API", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    # データベース設定
    db_host: str = Field(default="localhost", env="DB_HOST")
    db_port: int = Field(default=3306, env="DB_PORT")
    db_user: str = Field(default="root", env="DB_USER")
    db_password: str = Field(default="password", env="DB_PASSWORD")
    db_name: str = Field(default="kaminote_janken", env="DB_NAME")
    db_echo: bool = Field(default=False, env="DB_ECHO")
    
    # Redis設定
    redis_host: str = Field(default="localhost", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    redis_db: int = Field(default=0, env="REDIS_DB")
    
    # MinIO設定
    minio_endpoint: str = Field(default="localhost:9000", env="MINIO_ENDPOINT")
    minio_access_key: str = Field(default="minioadmin", env="MINIO_ACCESS_KEY")
    minio_secret_key: str = Field(default="minioadmin", env="MINIO_SECRET_KEY")
    minio_secure: bool = Field(default=False, env="MINIO_SECURE")
    minio_bucket: str = Field(default="kaminote-janken", env="MINIO_BUCKET")
    
    # JWT設定
    jwt_secret_key: str = Field(default="your-secret-key-here", env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_expire_minutes: int = Field(default=1440, env="JWT_EXPIRE_MINUTES")  # 24時間
    
    # API設定
    api_title: str = Field(default="Kaminote Janken API", env="API_TITLE")
    api_description: str = Field(default="じゃんけんゲームAPI - 画面単位API分離原則", env="API_DESCRIPTION")
    api_version: str = Field(default="1.0.0", env="API_VERSION")
    
    # CORS設定
    cors_origins: list = Field(default=["*"], env="CORS_ORIGINS")
    cors_methods: list = Field(default=["GET", "POST", "PUT", "DELETE"], env="CORS_METHODS")
    cors_headers: list = Field(default=["*"], env="CORS_HEADERS")
    
    # OCR設定
    ocr_enabled: bool = Field(default=True, env="OCR_ENABLED")
    tesseract_path: Optional[str] = Field(default=None, env="TESSERACT_PATH")
    
    # ログ設定
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")
    
    @property
    def database_url(self) -> str:
        """データベースURL"""
        return f"mysql+aiomysql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    @property
    def redis_url(self) -> str:
        """Redis URL"""
        password_part = f":{self.redis_password}@" if self.redis_password else ""
        return f"redis://{password_part}{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# グローバル設定インスタンス
settings = Settings() 