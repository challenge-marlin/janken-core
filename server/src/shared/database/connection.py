"""
データベース接続設定

SQLAlchemy 2.0 + 非同期処理でMySQL接続を提供
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from ..exceptions.handlers import DatabaseConnectionError
from ..config.settings import settings


class DatabaseConnection:
    """データベース接続管理クラス"""
    
    def __init__(self):
        self.engine = None
        self.async_session_local = None
        self._initialize_connection()
    
    def _initialize_connection(self):
        """データベース接続の初期化"""
        try:
            # settingsから接続情報を取得
            database_url = settings.database_url
            
            # 非同期エンジンの作成
            self.engine = create_async_engine(
                database_url,
                poolclass=NullPool,  # Lambda環境では接続プールを使用しない
                pool_pre_ping=True,
                echo=settings.db_echo,
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


# コンテキストマネージャー用の関数
async def get_db_session_context():
    """データベースセッションのコンテキストマネージャー"""
    if not db_connection.async_session_local:
        raise DatabaseConnectionError("データベース接続が初期化されていません")
    
    session = db_connection.async_session_local()
    try:
        yield session
    except Exception as e:
        await session.rollback()
        raise e
    finally:
        await session.close()


# コンテキストマネージャークラス
class DatabaseSessionContext:
    """データベースセッションのコンテキストマネージャークラス"""
    
    def __init__(self):
        if not db_connection.async_session_local:
            raise DatabaseConnectionError("データベース接続が初期化されていません")
        self.session = db_connection.async_session_local()
    
    async def __aenter__(self):
        return self.session
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.session.rollback()
        await self.session.close()


# コンテキストマネージャー用の関数（クラス版）
def get_db_session_context_class():
    """データベースセッションのコンテキストマネージークラスを返す"""
    return DatabaseSessionContext 