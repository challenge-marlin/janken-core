"""
改善版データベース接続管理

WebSocket対応の非同期データベース接続
"""

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
import logging

# 設定を読み込み
try:
    from ..config.settings import settings
except ImportError:
    # フォールバック設定
    class MockSettings:
        db_host = "localhost"
        db_port = 3306
        db_name = "janken_db"
        db_user = "root"
        db_password = "password"
        environment = "local"
        debug = True
    settings = MockSettings()

logger = logging.getLogger(__name__)


class DatabaseManager:
    """データベース接続管理クラス"""
    
    def __init__(self):
        self.engine = None
        self.session_factory = None
        self.is_initialized = False
    
    def initialize(self):
        """データベース接続を初期化"""
        if self.is_initialized:
            return
        
        try:
            # MySQL用の接続URL構築
            database_url = (
                f"mysql+aiomysql://{settings.db_user}:{settings.db_password}"
                f"@{settings.db_host}:{settings.db_port}/{settings.db_name}"
                f"?charset=utf8mb4"
            )
            
            logger.info(f"Database URL: mysql+aiomysql://{settings.db_user}:***@{settings.db_host}:{settings.db_port}/{settings.db_name}")
            
            # エンジン設定
            engine_kwargs = {
                "echo": settings.debug,
                "pool_size": 5,
                "max_overflow": 10,
                "pool_pre_ping": True,
                "pool_recycle": 3600,
                "connect_args": {
                    "charset": "utf8mb4",
                    "autocommit": False
                }
            }
            
            # 開発環境では追加設定
            if settings.environment == "local":
                engine_kwargs.update({
                    "pool_size": 3,
                    "max_overflow": 5
                })
            
            self.engine = create_async_engine(database_url, **engine_kwargs)
            
            # セッションファクトリー作成
            self.session_factory = async_sessionmaker(
                bind=self.engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autoflush=True,
                autocommit=False
            )
            
            self.is_initialized = True
            logger.info("Database connection initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database connection: {e}")
            raise
    
    async def close(self):
        """データベース接続を閉じる"""
        if self.engine:
            await self.engine.dispose()
            logger.info("Database connection closed")
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """セッションコンテキストマネージャー"""
        if not self.is_initialized:
            self.initialize()
        
        async with self.session_factory() as session:
            try:
                yield session
            except Exception as e:
                await session.rollback()
                logger.error(f"Database session error: {e}")
                raise
            finally:
                await session.close()
    
    async def test_connection(self) -> bool:
        """データベース接続テスト"""
        try:
            if not self.is_initialized:
                self.initialize()
            
            async with self.get_session() as session:
                result = await session.execute("SELECT 1")
                return result.scalar() == 1
                
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False


# グローバルデータベース管理インスタンス
db_manager = DatabaseManager()


@asynccontextmanager
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """非同期セッション取得（グローバル）"""
    async with db_manager.get_session() as session:
        yield session


async def init_database():
    """データベース初期化（アプリケーション起動時）"""
    try:
        db_manager.initialize()
        
        # 接続テスト
        if await db_manager.test_connection():
            logger.info("Database connection test passed")
        else:
            logger.error("Database connection test failed")
            
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


async def close_database():
    """データベース接続クリーンアップ（アプリケーション終了時）"""
    await db_manager.close()


# 便利関数
async def execute_query(query: str, params: dict = None) -> any:
    """クエリ実行用ヘルパー"""
    async with get_async_session() as session:
        result = await session.execute(query, params or {})
        await session.commit()
        return result


async def fetch_one(query: str, params: dict = None) -> any:
    """1行取得用ヘルパー"""
    async with get_async_session() as session:
        result = await session.execute(query, params or {})
        return result.first()


async def fetch_all(query: str, params: dict = None) -> list:
    """全行取得用ヘルパー"""
    async with get_async_session() as session:
        result = await session.execute(query, params or {})
        return result.fetchall()


# 設定確認用
def get_database_info() -> dict:
    """データベース設定情報を取得"""
    return {
        "host": settings.db_host,
        "port": settings.db_port,
        "database": settings.db_name,
        "user": settings.db_user,
        "environment": settings.environment,
        "is_initialized": db_manager.is_initialized
    }