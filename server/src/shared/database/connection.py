"""
データベース接続設定

SQLAlchemy 2.0 + 非同期処理でMySQL接続を提供
"""

import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from ..exceptions.handlers import DatabaseConnectionError


class DatabaseConnection:
    """データベース接続管理クラス"""
    
    def __init__(self):
        self.engine = None
        self.async_session_local = None
        self._initialize_connection()
    
    def _initialize_connection(self):
        """データベース接続の初期化"""
        try:
            # 環境変数から接続情報を取得
            db_host = os.getenv("DB_HOST", "localhost")
            db_port = os.getenv("DB_PORT", "3306")
            db_user = os.getenv("DB_USER", "root")
            db_password = os.getenv("DB_PASSWORD", "password")
            db_name = os.getenv("DB_NAME", "kaminote_janken")
            
            # 非同期MySQL接続文字列
            database_url = f"mysql+aiomysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
            
            # 非同期エンジンの作成
            self.engine = create_async_engine(
                database_url,
                poolclass=NullPool,  # Lambda環境では接続プールを使用しない
                pool_pre_ping=True,
                echo=os.getenv("DB_ECHO", "false").lower() == "true",
                future=True
            )
            
            # セッションファクトリーの作成
            self.async_session_local = sessionmaker(
                bind=self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
        except Exception as e:
            raise DatabaseConnectionError(f"データベース接続の初期化に失敗しました: {str(e)}")
    
    async def get_session(self) -> AsyncSession:
        """非同期セッションを取得"""
        if not self.async_session_local:
            raise DatabaseConnectionError("データベース接続が初期化されていません")
        
        async with self.async_session_local() as session:
            try:
                yield session
            except Exception as e:
                await session.rollback()
                raise e
            finally:
                await session.close()
    
    async def close(self):
        """データベース接続を閉じる"""
        if self.engine:
            await self.engine.dispose()


# グローバルインスタンス
db_connection = DatabaseConnection()

# 依存性注入用の関数
async def get_db_session():
    """データベースセッションの依存性注入"""
    async for session in db_connection.get_session():
        yield session 