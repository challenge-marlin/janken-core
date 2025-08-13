# かみのてじゃんけん - バックエンドAPIサーバー

じゃんけんゲームのバックエンドAPIサーバーです。画像OCR処理機能を含み、VPS環境での開発/テストを経て、AWS環境への移行を前提とした設計となっています。

## 技術スタック

### 現行環境（VPS）
- Python 3.11+
- FastAPI (APIフレームワーク)
- Mangum (ASGI/Lambda adapter)
- AWS SAM (Serverless Application Model)
- SQLAlchemy 2.0 (ORM)
- MySQL 8.0 (メインDB)
- Redis 6.2 (セッション/キャッシュ)
- MinIO (S3互換ストレージ) - 別サーバー
- Docker & Docker Compose
- Nginx (リバースプロキシ)
- Tesseract OCR (画像OCR処理)
- Pillow (画像処理)

### 移行先環境（AWS）
- AWS Lambda (サーバーレス実行環境)
- Amazon RDS for MySQL (SQLAlchemy対応)
- Amazon ElastiCache (Redis)
- Amazon S3 (オブジェクトストレージ)
- Amazon API Gateway
- AWS SAM (開発/デプロイ)
- Amazon Textract (画像OCR処理)
- AWS Secrets Manager (DB認証情報管理)
- Amazon RDS Proxy (コネクションプール)

## 開発環境のセットアップ

### 1. 前提条件

```bash
# Python 3.11+ のインストール確認
python --version

# AWS SAM CLI のインストール
pip install aws-sam-cli

# Docker のインストール確認
docker --version
```

### 2. 依存関係のインストール

```bash
# 仮想環境の作成
python -m venv venv

# 仮想環境の有効化
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 依存関係のインストール
pip install -r requirements.txt
```

### 3. 環境変数の設定

```bash
# ローカル開発環境用
cp environments/environment.local.template environments/.env.local

# VPS環境用
cp environments/environment.vps.template environments/.env.vps
```

各環境ファイルを編集し、必要な値を設定してください。

### 4. 開発環境の起動

```bash
# SAM ローカル開発環境の起動
sam local start-api --port 3000

# または Docker Compose での起動
docker-compose up -d   # localhost:80 でアクセス可能

# VPS環境の起動
docker-compose -f docker-compose-vps.yml up -d
```

### 5. 動作確認

以下のエンドポイントにアクセスして機能を確認できます：

- ヘルスチェック: `/api/health`
- MySQL状態: `/api/health/mysql`
- Redis状態: `/api/health/redis`
- MinIO状態: `/api/health/minio`
- OCR処理: `/api/ocr/process`

## プロジェクト設計思想とアーキテクチャ

### 🎯 **基本設計方針**

このプロジェクトはFastAPIベースですが、**可能な限りLaravelの設計思想と命名規則を適用し、一貫性のあるコードベースとAIとの効率的な連携を目指します**。FastAPIの特性とPythonの慣習を尊重しつつ、Laravelのベストプラクティスを効果的に融合させます。

#### 🏗️ **設計思想の融合**
- **FastAPIの強み**: 高速な実行速度、自動APIドキュメント生成、型ヒントによる安全性
- **Laravelの強み**: 明確なMVC構造、豊富なパターン、開発者にとって直感的な設計
- **目標**: 両者の利点を活かした、保守性と開発効率を兼ね備えたアーキテクチャ

#### 🎨 **AI連携における利点**
- **一貫した構造**: AIが予測しやすいディレクトリ構造とファイル配置
- **明確な責任分離**: 各層の役割が明確で、AIへの指示が効率的
- **パターンの標準化**: Laravelのベストプラクティスにより、AIの学習効率向上

### 🏛️ **プロジェクト構造と役割分担（MVCライクなアプローチ）**

FastAPIの柔軟性を活かしつつ、LaravelのMVCに似た役割分担を適用します：

#### **📁 ディレクトリ構造と責任**
```
src/screens/{画面名}/
├── router.py      # ルーティング/コントローラー層 - APIエンドポイント定義
├── models.py      # モデル層 - SQLAlchemyモデル配置  
├── schemas.py     # スキーマ層 - Pydantic入出力データ構造・バリデーション
├── services.py    # サービス層 - ビジネスロジックのカプセル化
└── handlers.py    # Lambda handlers（AWS対応）

src/shared/
├── database/      # データベース設定とモデル
├── cache/         # Redis設定
├── storage/       # MinIO/S3設定
└── exceptions/    # 共通例外処理

src/infrastructure/
├── database/      # SQLAlchemyモデル
├── monitoring/    # ヘルスチェック
└── ocr/          # OCR処理
```

#### **🔄 各層の詳細責任**

##### **ルーティング/コントローラー（router.py）**
```python
# LaravelのControllerに相当
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/login")
async def login(request: LoginRequest, service: AuthService = Depends()):
    """ログイン処理 - ビジネスロジックはサービス層に委譲"""
    return await service.authenticate(request)
```

##### **モデル層（models.py）**
```python
# LaravelのEloquentモデルに相当（SQLAlchemy）
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class User(DeclarativeBase):
    __tablename__ = 'users'
    
    user_id: Mapped[str] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    nickname: Mapped[str]
```

##### **スキーマ層（schemas.py）**
```python
# LaravelのRequestクラス・Resourceクラスに相当
from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    """ログインリクエスト - 入力バリデーション"""
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    """ユーザーレスポンス - 出力データ構造"""
    user_id: str
    email: str
    nickname: str
```

##### **サービス層（services.py）**
```python
# LaravelのServiceクラスに相当 - ビジネスロジック
class AuthService:
    def __init__(self, user_repo: UserRepository = Depends()):
        self.user_repo = user_repo
    
    async def authenticate(self, request: LoginRequest) -> UserResponse:
        """認証ビジネスロジック"""
        # 複雑なビジネスルールをここに実装
        pass
```

#### **💡 AIへの指示のコツ**
> 「このプロジェクトは、LaravelのMVCにインスパイアされた構造を採用しています。新しいAPIエンドポイントを生成する際は、`src/screens/{画面名}/router.py` にルーティング、`schemas.py` に入出力Pydanticモデル、`services.py` にビジネスロジックを配置してください。」

### 🎯 **コーディング規約**

#### **📝 命名規則**
- **クラス名**: `CamelCase` (例: `UserService`, `AuthController`)
- **関数名・変数**: `snake_case` (例: `get_user_by_id`, `user_data`)
- **定数**: `UPPER_SNAKE_CASE` (例: `MAX_LOGIN_ATTEMPTS`)
- **ファイル名**: `snake_case` (例: `auth_service.py`, `user_models.py`)

#### **📦 インポート順序（PEP 8準拠）**
```python
# 1. 標準ライブラリ
import os
import sys
from datetime import datetime

# 2. サードパーティライブラリ
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import redis

# 3. プロジェクト内モジュール
from src.shared.database import get_db_session
from src.screens.auth.schemas import LoginRequest
from src.screens.auth.services import AuthService
```

#### **📋 型ヒント（必須）**
```python
from typing import Optional, List, Dict, Any

async def get_user_by_id(user_id: str, db: Session) -> Optional[User]:
    """ユーザーID検索 - 型ヒントで安全性確保"""
    return db.query(User).filter(User.user_id == user_id).first()

async def get_users_list(limit: int = 10) -> List[Dict[str, Any]]:
    """ユーザー一覧取得 - 戻り値の型も明示"""
    pass
```

### 🗄️ **データ操作とORM（SQLAlchemyとリポジトリパターン）**

#### **🔧 ORMとモデル定義**
```python
# src/screens/auth/models.py
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    """ユーザーモデル - LaravelのEloquentライクな定義"""
    __tablename__ = 'users'
    
    user_id = Column(String(50), primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    nickname = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
```

#### **🏪 リポジトリパターン実装**
```python
# src/screens/auth/repositories.py
from typing import Optional, List
from sqlalchemy.orm import Session
from .models import User

class UserRepository:
    """ユーザーリポジトリ - LaravelのEloquentの代替"""
    
    def __init__(self, db: Session = Depends(get_db_session)):
        self.db = db
    
    async def find_by_id(self, user_id: str) -> Optional[User]:
        """ID検索 - LaravelのUser::find()相当"""
        return self.db.query(User).filter(User.user_id == user_id).first()
    
    async def find_by_email(self, email: str) -> Optional[User]:
        """メール検索 - LaravelのUser::where('email', $email)->first()相当"""
        return self.db.query(User).filter(User.email == email).first()
    
    async def create(self, user_data: dict) -> User:
        """ユーザー作成 - LaravelのUser::create()相当"""
        user = User(**user_data)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    async def update(self, user_id: str, update_data: dict) -> Optional[User]:
        """ユーザー更新 - LaravelのUser::where()->update()相当"""
        user = await self.find_by_id(user_id)
        if user:
            for key, value in update_data.items():
                setattr(user, key, value)
            self.db.commit()
            self.db.refresh(user)
        return user
```

#### **💡 AIへの指示のコツ**
> 「データベース操作にはSQLAlchemy ORMを使用します。LaravelのEloquentのように直接モデルにCRUDメソッドを持たせず、`UserRepository`のようなリポジトリ層またはサービス層でカプセル化し、FastAPIのDependsでセッションを注入してください。」

### 🚨 **エラーハンドリングとレスポンス**

#### **統一されたエラーレスポンス**
LaravelのException HandlerやValidationのように、一貫したJSON形式のエラーレスポンスを返却します：

```python
# src/shared/exceptions/handlers.py
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

class APIException(Exception):
    """Laravel風のカスタム例外クラス"""
    def __init__(self, message: str, status_code: int = 400, details: dict = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}

async def api_exception_handler(request: Request, exc: APIException):
    """カスタム例外ハンドラー - Laravel的なエラーレスポンス"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.message,
            "details": exc.details,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """バリデーションエラーハンドラー - LaravelのFormRequest風"""
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "Validation failed",
            "errors": exc.errors(),
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# アプリケーション登録
app.add_exception_handler(APIException, api_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
```

#### **サービス層でのエラーハンドリング**
```python
# src/screens/auth/services.py
class AuthService:
    async def authenticate(self, request: LoginRequest) -> UserResponse:
        user = await self.user_repo.find_by_email(request.email)
        
        if not user:
            raise APIException(
                message="認証に失敗しました",
                status_code=401,
                details={"field": "email", "code": "USER_NOT_FOUND"}
            )
        
        if not self.verify_password(request.password, user.password_hash):
            raise APIException(
                message="認証に失敗しました", 
                status_code=401,
                details={"field": "password", "code": "INVALID_PASSWORD"}
            )
        
        return UserResponse.from_orm(user)
```

### 🧪 **テスト戦略**

#### **テストフレームワーク構成**
```python
# tests/conftest.py - LaravelのTestCaseに相当する基盤
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.main import app
from src.shared.database import get_db_session, Base

# テスト用データベース
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

@pytest.fixture
def client():
    """テストクライアント - LaravelのHTTPテスト相当"""
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db_session] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(bind=engine)
```

#### **統合テスト（LaravelのFeatureTestに相当）**
```python
# tests/screens/test_auth.py
def test_login_success(client):
    """ログイン成功テスト - Laravel的な統合テスト"""
    # Given: ユーザーデータの準備
    user_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    
    # When: ログインAPIを実行
    response = client.post("/api/auth/login", json=user_data)
    
    # Then: レスポンスを検証
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert "access_token" in response.json()["data"]

def test_login_invalid_credentials(client):
    """ログイン失敗テスト"""
    response = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "wrong_password"
    })
    
    assert response.status_code == 401
    assert response.json()["success"] is False
    assert response.json()["details"]["code"] == "INVALID_PASSWORD"
```

#### **ユニットテスト（サービス層）**
```python
# tests/screens/auth/test_auth_service.py
from unittest.mock import Mock
import pytest
from src.screens.auth.services import AuthService
from src.shared.exceptions.handlers import APIException

@pytest.fixture
def mock_user_repo():
    return Mock()

def test_authenticate_success(mock_user_repo):
    """認証サービス単体テスト"""
    # Given
    service = AuthService(user_repo=mock_user_repo)
    mock_user_repo.find_by_email.return_value = Mock(
        user_id="test_user",
        email="test@example.com",
        password_hash="hashed_password"
    )
    
    # When & Then
    # テストロジック実装
```

### 🌍 **環境管理とデータベースマイグレーション**

#### **環境変数管理（LaravelのConfig風）**
```python
# src/config/settings.py
from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Laravel風の設定管理 - python-dotenv + Pydantic BaseSettings"""
    
    # アプリケーション設定
    app_name: str = "じゃんけんバトル"
    app_env: str = "local"
    debug: bool = True
    
    # データベース設定
    database_url: str
    db_echo: bool = False
    
    # Redis設定
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: Optional[str] = None
    
    # JWT設定
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440
    
    # MinIO/S3設定
    minio_endpoint: str
    minio_access_key: str
    minio_secret_key: str
    minio_secure: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# グローバル設定インスタンス
settings = Settings()
```

#### **初期データ/シード（LaravelのSeeder風）**
```python
# scripts/seeds/user_seeder.py
class UserSeeder:
    """LaravelのSeederクラスに相当"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def run(self):
        """シードデータ投入"""
        users = [
            {
                "user_id": "test_user_1",
                "email": "test1@example.com", 
                "nickname": "テストユーザー1",
                "role": "developer"
            },
            # 追加のテストデータ...
        ]
        
        for user_data in users:
            user = User(**user_data)
            self.db.add(user)
        
        self.db.commit()
        print(f"✅ {len(users)}名のユーザーを作成しました")

# scripts/seed.py - 実行スクリプト
def main():
    """Laravel風のシード実行"""
    db = SessionLocal()
    try:
        UserSeeder(db).run()
        # 他のSeederも実行...
    finally:
        db.close()
```

### ⚠️ **AIに特に注意してほしいこと（避けたいパターン）**

以下のパターンは、FastAPIの設計思想とバッティングし、保守性やテスト容易性を損なう可能性があるため**避けます**：

#### **🚫 避けるべきパターン1: 過度なマジックメソッドやグローバルな状態**
```python
# ❌ BAD: Laravel風のファサードライクなグローバルアクセス
class Auth:
    @staticmethod
    def user():
        return current_user  # グローバル変数に依存

class DB:
    @staticmethod  
    def table(name):
        return global_session.query(...)  # 隠れた依存関係

# ✅ GOOD: FastAPIのDependsを活用した明示的な依存注入
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends()
) -> User:
    return await user_service.get_user_by_token(token)

@router.get("/profile")
async def get_profile(current_user: User = Depends(get_current_user)):
    return UserResponse.from_orm(current_user)
```

#### **🚫 避けるべきパターン2: 非Python的なコーディングスタイル**
```python
# ❌ BAD: PHP風の命名規則
class userController:  # snake_case（Python非推奨）
    def getUserById($userId):  # PHP風の変数名
        pass

# ✅ GOOD: Python PEP 8準拠
class UserController:  # CamelCase
    async def get_user_by_id(self, user_id: str) -> Optional[User]:  # snake_case
        pass
```

#### **🚫 避けるべきパターン3: 過度な機能の隠蔽**
```python
# ❌ BAD: 過度に抽象化されたマジックメソッド
class Model:
    def save(self):
        # 内部で何が起こるか不明
        magic_orm_save(self)

# ✅ GOOD: 明示的なセッション管理
class UserService:
    async def create_user(self, user_data: dict, db: Session) -> User:
        user = User(**user_data)
        db.add(user)
        db.commit()  # 明示的なコミット
        db.refresh(user)
        return user
```

#### **💡 AIへの総合指示**
> 「このプロジェクトでは、LaravelのMVC設計思想とFastAPIの明示的な依存注入を融合させています。新機能追加時は、Laravel風の明確な層分離（router/service/repository）を保ちつつ、FastAPIのDependsとPydantic型安全性を活用してください。グローバル状態やマジックメソッドは避け、常に明示的で型安全なコードを心がけてください。」

## アーキテクチャ

### コンテナ構成

- nginx: リバースプロキシ（80番ポート公開）
- api: バックエンドAPI（FastAPI + Mangum, 3000番ポート）
- mysql: データベース
- redis: セッション/キャッシュ
- minio: S3互換ストレージ（別サーバー）

### ルーティング設計

すべてのAPIリクエストは、nginxリバースプロキシ経由でアクセスします：

- `/api/*` - バックエンドAPIへのプロキシ
- `/health` - Nginxのヘルスチェック
- `/` - 静的ファイル（テストページなど）

### FastAPI + Mangum + SAM パターン

FastAPIアプリケーションをMangumでラップしてAWS Lambda対応：

```python
from fastapi import FastAPI
from mangum import Mangum

app = FastAPI()

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

# Lambda handler
handler = Mangum(app)
```

## プロジェクト構造

### 画面単位API分離原則による設計

本プロジェクトは **画面単位でのAPI分離原則** を採用しています：

#### 🎯 **基本方針**
1. **画面専用API**: 各画面（認証、ロビー、設定、バトル等）には専用のAPIエンドポイントを用意
2. **機能横断の禁止**: あるAPIの修正が他画面に影響することを防ぐため、APIの機能横断的な使用は禁止
3. **代替案の回避**: クライアントが既存APIの組み合わせで代替実装することは避け、必要な機能は専用APIとして実装
4. **独立性の保証**: 各画面のAPIは独立して動作し、他画面のAPIに依存しない設計

#### 🏗️ **実装責任**
- **サーバーサイド**: 画面ごとに必要な専用APIを実装する責任
- **クライアントサイド**: 画面に対応する専用APIのみを使用する責任

#### 📁 **フォルダ構成の特徴**
- `src/screens/` 配下に画面単位でディレクトリを分離
- 各画面ディレクトリは完全に独立した機能を持つ
- `src/shared/` は画面横断を許可された共通機能のみ
- テストも画面単位で分離してテスト容易性を確保

```
/
├── src/                           # ソースコード
│   ├── screens/                   # 画面単位API分離原則による構成
│   │   ├── auth/                 # 認証画面専用API
│   │   │   ├── __init__.py
│   │   │   ├── router.py         # FastAPIルーター
│   │   │   ├── handlers.py       # Lambda handlers
│   │   │   ├── models.py         # 画面専用データモデル
│   │   │   ├── services.py       # 画面専用ビジネスロジック
│   │   │   └── schemas.py        # Pydantic schemas
│   │   │
│   │   ├── register/             # 登録画面専用API
│   │   │   ├── __init__.py
│   │   │   ├── router.py
│   │   │   ├── handlers.py
│   │   │   ├── models.py
│   │   │   ├── services.py
│   │   │   └── schemas.py
│   │   │
│   │   ├── lobby/                # ロビー画面専用API
│   │   │   ├── __init__.py
│   │   │   ├── router.py
│   │   │   ├── handlers.py
│   │   │   ├── models.py
│   │   │   ├── services.py
│   │   │   └── schemas.py
│   │   │
│   │   ├── battle/               # バトル画面専用API
│   │   │   ├── __init__.py
│   │   │   ├── router.py
│   │   │   ├── handlers.py
│   │   │   ├── models.py
│   │   │   ├── services.py
│   │   │   └── schemas.py
│   │   │
│   │   ├── ranking/              # ランキング画面専用API
│   │   │   ├── __init__.py
│   │   │   ├── router.py
│   │   │   ├── handlers.py
│   │   │   ├── models.py
│   │   │   ├── services.py
│   │   │   └── schemas.py
│   │   │
│   │   └── settings/             # 設定画面専用API
│   │       ├── __init__.py
│   │       ├── router.py
│   │       ├── handlers.py
│   │       ├── models.py
│   │       ├── services.py
│   │       └── schemas.py
│   │
│   ├── shared/                   # 共通機能（画面横断禁止の例外）
│   │   ├── __init__.py
│   │   ├── auth/                 # 認証ミドルウェア
│   │   │   ├── __init__.py
│   │   │   ├── middleware.py
│   │   │   └── jwt_handler.py
│   │   ├── database/             # データベース接続
│   │   │   ├── __init__.py
│   │   │   ├── connection.py
│   │   │   └── session.py
│   │   ├── cache/                # Redis接続
│   │   │   ├── __init__.py
│   │   │   └── redis_client.py
│   │   ├── storage/              # MinIO/S3接続
│   │   │   ├── __init__.py
│   │   │   └── minio_client.py
│   │   └── exceptions/           # 共通例外
│   │       ├── __init__.py
│   │       └── handlers.py
│   │
│   ├── infrastructure/           # インフラ層
│   │   ├── __init__.py
│   │   ├── database/
│   │   │   ├── __init__.py
│   │   │   └── models.py         # SQLAlchemyモデル
│   │   ├── ocr/                  # OCR処理
│   │   │   ├── __init__.py
│   │   │   ├── tesseract.py
│   │   │   └── textract.py
│   │   └── monitoring/           # ヘルスチェック
│   │       ├── __init__.py
│   │       └── health.py
│   │
│   ├── config/                   # 設定
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   └── environments.py
│   │
│   ├── main.py                   # FastAPIアプリケーション
│   └── lambda_handler.py         # Lambda エントリーポイント
│
├── database/                    # 🆕 Laravel風データベース管理
│   ├── migrations/              # マイグレーションファイル
│   │   ├── 001_initial_migration.py         # 基本認証システム
│   │   ├── 002_auth_system_migration.py     # Magic Link + JWT
│   │   ├── 003_game_system_migration.py     # ゲーム・統計
│   │   └── 004_system_tables_migration.py   # システム管理
│   ├── seeders/                 # シーダーファイル
│   │   └── UserSeeder.py        # テストユーザー・設定
├── scripts/                     # 🆕 Laravel風管理スクリプト
│   ├── migrate.py               # php artisan migrate 相当
│   └── setup_database.py        # Docker環境セットアップ
├── template.yaml                # SAM テンプレート
├── requirements.txt             # Python依存関係
├── nginx/                       # Nginx設定
├── environments/                # 環境変数
├── docs/                        # ドキュメント
├── tests/                       # テスト
│   ├── screens/                 # 画面単位テスト
│   │   ├── test_auth.py
│   │   ├── test_register.py
│   │   ├── test_lobby.py
│   │   ├── test_battle.py
│   │   ├── test_ranking.py
│   │   └── test_settings.py
│   ├── shared/                  # 共通機能テスト
│   └── integration/             # 統合テスト
├── Dockerfile                   # アプリケーションのDockerfile
└── docker-compose.yml           # Docker Compose設定
```

### 画面単位API分離の利点

#### 🔧 **開発効率**
- **並行開発**: 各画面担当者が独立して開発可能
- **影響範囲の限定**: 変更が他画面に影響しない
- **テスト容易性**: 画面単位での独立したテスト実行

#### 🛡️ **保守性・安定性**
- **保守性**: 各画面の修正が他画面に影響しない
- **安定性**: 画面固有の要件に最適化された専用API
- **デバッグ**: 問題の発生源を特定しやすい

#### 📊 **実装例**
```python
# src/screens/lobby/router.py
from fastapi import APIRouter

router = APIRouter(prefix="/api/lobby", tags=["lobby"])

@router.get("/user-stats/{user_id}")
async def get_lobby_user_stats(user_id: str):
    """ロビー画面専用のユーザーステータス取得"""
    # ロビー画面に最適化された専用実装
    pass

# src/screens/settings/router.py  
from fastapi import APIRouter

router = APIRouter(prefix="/api/settings", tags=["settings"])

@router.get("/user-profile/{user_id}")
async def get_settings_user_profile(user_id: str):
    """設定画面専用のユーザープロフィール取得"""
    # 設定画面に最適化された専用実装
    pass
```

#### 🎨 **API命名規則**
```
/api/{画面名}/{機能名}/{パラメータ}
```

例：
- `/api/lobby/user-stats/{userId}` - ロビー画面専用のユーザーステータス取得
- `/api/settings/user-profile/{userId}` - 設定画面専用のユーザープロフィール取得
- `/api/battle/hand` - バトル画面専用の手送信

## SAM コマンド

```bash
# SAM アプリケーションのビルド
sam build

# ローカル開発環境の起動
sam local start-api

# Lambda関数の個別テスト
sam local invoke "FunctionName" -e events/test-event.json

# AWS環境へのデプロイ
sam deploy --guided
```

## データベース管理（Laravel風マイグレーション + SQLAlchemy）

### 🏆 Laravel風マイグレーションシステム

#### ✨ **主な特徴**
- **📁 ファイル分割**: 機能別にマイグレーションファイルを分離
- **📊 履歴管理**: `migrations`テーブルで実行履歴を自動管理
- **⏪ ロールバック**: 安全なデータベース状態の巻き戻し
- **🔗 依存関係**: マイグレーション間の依存関係を明確化
- **🌱 シーダー**: テストデータの一括投入

#### 🚀 **基本的な使用方法**

##### ⚠️ **重要**: マイグレーションファイルの事前準備

マイグレーションを実行する前に、必要なファイルをAPIコンテナにコピーする必要があります：

```bash
# 1. 必要なディレクトリをコンテナ内に作成
docker-compose exec api mkdir -p /app/scripts /app/database/migrations /app/database/seeders

# 2. マイグレーション管理スクリプトをコピー
docker cp scripts/migrate.py kaminote-janken-api:/app/scripts/

# 3. マイグレーションファイルを順次コピー
docker cp database/migrations/001_initial_migration.py kaminote-janken-api:/app/database/migrations/
docker cp database/migrations/002_auth_system_migration.py kaminote-janken-api:/app/database/migrations/
docker cp database/migrations/003_game_system_migration.py kaminote-janken-api:/app/database/migrations/
docker cp database/migrations/004_system_tables_migration.py kaminote-janken-api:/app/database/migrations/

# 4. シーダーファイルをコピー
docker cp database/seeders/UserSeeder.py kaminote-janken-api:/app/database/seeders/
```

##### 📋 **マイグレーション実行手順**

```bash
# マイグレーション実行 (php artisan migrate)
docker-compose exec api python /app/scripts/migrate.py migrate

# 状況確認 (php artisan migrate:status)  
docker-compose exec api python /app/scripts/migrate.py status

# ロールバック (php artisan migrate:rollback)
docker-compose exec api python /app/scripts/migrate.py rollback --steps 1

# 特定のマイグレーションまで実行
docker-compose exec api python /app/scripts/migrate.py migrate --target 002_auth_system_migration
```

##### 🔍 **データベース状態確認**

```bash
# 作成されたテーブル一覧
docker-compose exec mysql mysql -u root -ppassword janken_db -e "SHOW TABLES;"

# マイグレーション履歴確認
docker-compose exec mysql mysql -u root -ppassword janken_db -e "SELECT migration, batch, executed_at FROM migrations;"

# 特定テーブルの構造確認
docker-compose exec mysql mysql -u root -ppassword janken_db -e "DESCRIBE users;"
```

#### 🗂️ **マイグレーションファイル構成**

**1. 001_initial_migration.py** - 基本認証システム
- `users` - ユーザー基本情報
- `user_profiles` - ユーザー詳細情報
- `auth_credentials` - パスワード資格情報
- `user_devices` - 端末管理

**2. 002_auth_system_migration.py** - Magic Link + JWT認証
- `magic_link_tokens` - Magic Linkトークン
- `sessions` - セッション管理
- `refresh_tokens` - リフレッシュトークン
- `jwt_blacklist` - JWTブラックリスト
- `two_factor_auth` - 2要素認証

**3. 003_game_system_migration.py** - ゲーム・統計システム
- `battle_results` - バトル結果記録
- `battle_rounds` - バトルラウンド詳細
- `user_stats` - ユーザー統計
- `daily_rankings` - 日次ランキング

**4. 004_system_tables_migration.py** - システム管理
- `system_settings` - システム設定
- `oauth_accounts` - OAuth連携
- `login_attempts` - ログイン試行管理
- `security_events` - セキュリティイベントログ
- `admin_logs` - 管理者操作ログ
- `activity_logs` - アクティビティログ

#### 🌱 **シーダーシステム**

```bash
# シーダー実行（テストユーザー・システム設定投入）
python scripts/seed.py --class UserSeeder

# 全シーダー実行
python scripts/seed.py --all
```

**UserSeeder.py の内容:**
- 5名のテスト開発者ユーザー（test_user_1〜5）
- システム設定（タイムアウト・有効期限等）
- ユーザー統計の初期化

### SQLAlchemy 基本的な使用方法

```python
# SQLAlchemy 2.0 + 非同期処理
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# 非同期エンジンの作成
engine = create_async_engine(
    "mysql+aiomysql://user:pass@localhost/janken_battle_complete",
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True
)

# セッションファクトリー
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
```

### データベースセットアップ（推奨方法）

#### 🏆 **Laravel風マイグレーションシステム（最推奨 - 2025年最新）**

##### 📋 **ステップ1: 環境準備**
```bash
# サーバーディレクトリに移動
cd server

# Docker環境起動
docker-compose up -d
```

##### 📋 **ステップ2: マイグレーションファイル準備**
```bash
# APIコンテナ内にディレクトリ作成
docker-compose exec api mkdir -p /app/scripts /app/database/migrations /app/database/seeders

# マイグレーション管理スクリプトをコピー
docker cp scripts/migrate.py kaminote-janken-api:/app/scripts/

# マイグレーションファイルを順次コピー
docker cp database/migrations/001_initial_migration.py kaminote-janken-api:/app/database/migrations/
docker cp database/migrations/002_auth_system_migration.py kaminote-janken-api:/app/database/migrations/
docker cp database/migrations/003_game_system_migration.py kaminote-janken-api:/app/database/migrations/
docker cp database/migrations/004_system_tables_migration.py kaminote-janken-api:/app/database/migrations/

# シーダーファイルをコピー
docker cp database/seeders/UserSeeder.py kaminote-janken-api:/app/database/seeders/
```

##### 📋 **ステップ3: マイグレーション実行**
```bash
# Laravel風マイグレーション実行 (php artisan migrate 相当)
docker-compose exec api python /app/scripts/migrate.py migrate

# マイグレーション状況確認 (php artisan migrate:status 相当)
docker-compose exec api python /app/scripts/migrate.py status

# データベースの確認
docker-compose exec mysql mysql -u root -ppassword janken_db -e "SHOW TABLES;"
```

##### 📋 **ステップ4: シーダー実行（オプション）**
```bash
# テストユーザー・設定データの投入
docker-compose exec api python /app/scripts/seed.py --class UserSeeder

# ロールバック実行 (php artisan migrate:rollback 相当)
docker-compose exec api python /app/scripts/migrate.py rollback --steps 1
```

**🎯 Laravel風マイグレーションの利点:**
- **🔄 段階的管理**: 機能別にマイグレーションを分割
- **📊 履歴追跡**: 実行済みマイグレーションの完全管理
- **⏪ ロールバック**: 問題発生時の安全な取り消し機能
- **🌱 シーダー対応**: テストデータの自動投入
- **🏗️ 依存関係**: マイグレーション間の依存管理

##### 🔧 **トラブルシューティング**

**❌ 問題**: `No such file or directory: /app/scripts/migrate.py`
```bash
# 解決策: 必要なファイルをコンテナにコピー
docker cp scripts/migrate.py kaminote-janken-api:/app/scripts/
docker cp database/migrations/ kaminote-janken-api:/app/database/migrations/
```

**❌ 問題**: `ModuleNotFoundError: No module named 'sqlalchemy'`
```bash
# 解決策: APIコンテナ内で実行（SQLAlchemyが事前インストール済み）
docker-compose exec api python /app/scripts/migrate.py migrate
```

**❌ 問題**: 既存テーブルとの競合
```bash
# 解決策: テーブルを一旦削除して再実行
docker-compose exec mysql mysql -u root -ppassword janken_db -e "DROP TABLE IF EXISTS migrations, users, user_profiles;"
docker-compose exec api python /app/scripts/migrate.py migrate
```

**✅ 動作確認コマンド**
```bash
# マイグレーション状態確認
docker-compose exec api python /app/scripts/migrate.py status

# テーブル確認
docker-compose exec mysql mysql -u root -ppassword janken_db -e "SHOW TABLES;"

# マイグレーション履歴確認
docker-compose exec mysql mysql -u root -ppassword janken_db -e "SELECT migration, batch, executed_at FROM migrations;"
```

#### 📁 **マイグレーション構造**
```
database/
├── migrations/                    # Laravel風マイグレーション
│   ├── 001_initial_migration.py   # 基本認証システム（ユーザー・プロフィール）
│   ├── 002_auth_system_migration.py # Magic Link + JWT + セッション
│   ├── 003_game_system_migration.py # ゲーム・統計・ランキング
│   └── 004_system_tables_migration.py # システム設定・OAuth・ログ
├── seeders/                       # Laravel風シーダー
│   └── UserSeeder.py              # テストユーザー・システム設定
└── sql/                           # レガシー（移行中）
    ├── create_tables.sql          # 一括SQL（非推奨）
    └── quick_db_setup.sql         # 差分SQL（非推奨）
```

#### 🚀 **従来のSQLセットアップ（互換性維持・移行期間中）**
```bash
# 完全認証システム対応のセットアップ
cd server

# 方法1: 完全なcreate_tables.sqlを使用
docker cp database/sql/create_tables.sql kaminote-janken-mysql:/tmp/
docker-compose exec mysql mysql -u root -ppassword -e "source /tmp/create_tables.sql"

# 方法2: 既存テーブルに不足分を追加
docker cp database/sql/quick_db_setup.sql kaminote-janken-mysql:/tmp/
docker-compose exec mysql mysql -u root -ppassword janken_db -e "source /tmp/quick_db_setup.sql"
```

**⚠️ 移行方針:**
- **新規プロジェクト**: Laravel風マイグレーションシステムを使用
- **既存環境**: 従来のSQL方式で継続可能（互換性あり）
- **将来計画**: 段階的にLaravel風マイグレーションに移行

#### 🐳 **Docker Compose手動セットアップ**
```bash
# 1. MySQLサービス起動（データベース自動作成）
docker-compose up -d mysql

# 2. MySQLの起動完了を待機（重要：約30秒）
echo "MySQLの起動を待機中..."
sleep 30

# 3. 完全認証システムテーブル作成
docker cp database/sql/create_tables.sql kaminote-janken-mysql:/tmp/
docker-compose exec mysql mysql -u root -ppassword -e "source /tmp/create_tables.sql"

# 4. テーブル作成確認
echo "=== テーブル作成確認 ==="
docker-compose exec mysql mysql -u root -ppassword janken_battle_complete -e "SHOW TABLES;"

# 5. 基本テーブル内容確認
echo "=== 基本データ確認 ==="
docker-compose exec mysql mysql -u root -ppassword janken_battle_complete -e "
SELECT 'ユーザー数' as item, COUNT(*) as count FROM users
UNION ALL
SELECT 'システム設定数', COUNT(*) FROM system_settings
UNION ALL
SELECT 'テストユーザー数', COUNT(*) FROM users WHERE role = 'developer';
"

# 6. 認証テーブル確認
echo "=== 認証システムテーブル確認 ==="
docker-compose exec mysql mysql -u root -ppassword janken_battle_complete -e "
SELECT 
    table_name, 
    table_rows,
    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS 'Size (MB)'
FROM information_schema.tables 
WHERE table_schema = 'janken_battle_complete'
ORDER BY table_name;
"

# 7. 全サービス起動
docker-compose up -d

# 8. 動作確認
echo "=== 動作確認 ==="
echo "API ヘルスチェック: http://localhost/api/health"
echo "phpMyAdmin: http://localhost:8080 (root/password)"
echo "Redis Commander: http://localhost:8081"
```

#### 🚀 **新規リポジトリ展開時の完全セットアップ**
```bash
# 1. リポジトリクローン後、serverディレクトリに移動
cd server

# 2. MySQLサービス起動
docker-compose up -d mysql

# 3. MySQL起動待機
sleep 30

# 4. 完全認証システムセットアップ
docker cp database/sql/create_tables.sql kaminote-janken-mysql:/tmp/
docker-compose exec mysql mysql -u root -ppassword -e "source /tmp/create_tables.sql"

# 5. セットアップ確認
docker-compose exec mysql mysql -u root -ppassword janken_battle_complete -e "SHOW TABLES;"

# 6. 全サービス起動
docker-compose up -d

# 7. 動作確認
curl http://localhost/api/health
echo "セットアップ完了！"
echo "ブラウザで http://localhost にアクセスしてください"
echo "データベース管理: http://localhost:8080 (root/password)"
```

#### 📊 **投入されるデータ**
- **ユーザー**: 5名のテスト開発者ユーザー（test_user_1～5）
- **認証システム**: 完全認証テーブル（Magic Link、JWT、セッション管理）
- **ゲームシステム**: バトル結果、ランキング、統計テーブル
- **システム設定**: セキュリティ・認証・ゲーム設定値
- **監査ログ**: セキュリティイベント、ログイン試行、管理操作ログ

### AWS環境での設定

```python
# AWS RDS + Secrets Manager
import boto3
from sqlalchemy.ext.asyncio import create_async_engine

async def get_db_connection():
    # Secrets Manager から認証情報を取得
    secrets_client = boto3.client('secretsmanager')
    secret = secrets_client.get_secret_value(SecretId='rds-credentials')
    
    # RDS Proxy経由での接続（推奨）
    engine = create_async_engine(
        f"mysql+aiomysql://{username}:{password}@{rds_proxy_endpoint}/{dbname}",
        pool_size=1,  # Lambda では小さく設定
        max_overflow=0,
        pool_pre_ping=True,
        pool_recycle=3600
    )
    return engine
```

## MinIO → AWS S3 移行ガイド

### 移行時の主な変更点

#### 1. ストレージクライアントの変更
```python
# MinIO (現行)
from minio import Minio
client = Minio(
    endpoint="192.168.0.155:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

# AWS S3 (移行後)
import boto3
s3_client = boto3.client(
    's3',
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key,
    region_name=settings.aws_region
)
```

#### 2. 署名付きURL生成の違い
```python
# MinIO
def get_presigned_url(self, object_name: str, expires: int = 3600) -> str:
    return self.client.presigned_get_object(
        self.bucket_name,
        object_name,
        expires=timedelta(seconds=expires)
    )

# AWS S3
def get_presigned_url(self, object_name: str, expires: int = 3600) -> str:
    return self.s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': self.bucket_name, 'Key': object_name},
        ExpiresIn=expires
    )
```

#### 3. プロキシエンドポイントの互換性

**現在の実装の利点（移行時）:**
- プロキシエンドポイント（`/storage/proxy/`）は内部実装の変更に依存しない
- MinIO → S3 移行時もクライアント側の変更不要
- 統一されたアクセス制御とCORS設定を維持

**移行時の考慮事項:**
1. **パフォーマンス**: AWS Lambda環境でのプロキシ配信
   - ファイルサイズ制限（Lambda: 6MB応答制限）
   - 大きなファイルは署名付きURL方式を推奨

2. **コスト**: プロキシ配信 vs 直接アクセス
   - プロキシ: Lambda実行時間課金
   - 直接: S3転送課金のみ

3. **セキュリティ**: 
   - S3バケットポリシーでアクセス制御
   - CloudFront + S3 の組み合わせを検討

#### 4. 推奨移行戦略

**段階的移行アプローチ:**
```python
# 設定による切り替え対応
class StorageClient:
    def __init__(self):
        if settings.storage_type == "minio":
            self.client = MinIOClient()
        elif settings.storage_type == "s3":
            self.client = S3Client()
    
    def get_file_url(self, object_name: str, method: str = "proxy"):
        if method == "proxy":
            # プロキシ経由（互換性重視）
            return f"/storage/proxy/{object_name}"
        else:
            # 直接アクセス（パフォーマンス重視）
            return self.client.get_presigned_url(object_name)
```

**移行チェックリスト:**
- [ ] S3バケット作成・権限設定
- [ ] IAM ロール・ポリシー設定
- [ ] 環境変数の更新
- [ ] ストレージクライアント実装の切り替え
- [ ] 既存ファイルの移行
- [ ] プロキシエンドポイントの動作確認
- [ ] 署名付きURL方式の動作確認
- [ ] パフォーマンステスト実施

#### 5. AWS特有の設定

**S3バケットポリシー例:**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowLambdaAccess",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::ACCOUNT-ID:role/lambda-execution-role"
            },
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject"
            ],
            "Resource": "arn:aws:s3:::kaminote-janken/*"
        }
    ]
}
```

**CloudFront設定（オプション）:**
- 画像配信の高速化
- キャッシュ設定によるコスト削減
- カスタムドメイン対応

### 現在の実装がAWS移行に有利な理由

#### 1. アーキテクチャの互換性
- **FastAPI + Mangum**: 既にLambda対応済み
- **SQLAlchemy 2.0**: RDS/Aurora対応
- **非同期処理**: Lambda環境で効率的
- **環境変数管理**: AWS Systems Manager Parameter Store対応容易

#### 2. ストレージ抽象化
- **プロキシエンドポイント**: 内部実装に依存しないAPI設計
- **統一インターフェース**: MinIO/S3の差異を吸収
- **メタデータ管理**: バケットタイプによる論理分離

#### 3. セキュリティ設計
- **JWT認証**: AWS Cognito移行可能
- **CORS設定**: API Gateway + Lambda対応
- **アクセス制御**: IAMロール・ポリシー対応

#### 4. 監視・運用
- **ヘルスチェック**: ALB/CloudWatch対応
- **ログ設計**: CloudWatch Logs対応
- **メトリクス**: CloudWatch メトリクス対応

#### 移行時の非互換性リスク（低）
1. **ファイルサイズ制限**: Lambda 6MB制限（プロキシ使用時）
   - **対策**: 大きなファイルは署名付きURL方式に自動切り替え
2. **同期処理**: MinIOの同期クライアント
   - **対策**: boto3も同期/非同期両対応
3. **エンドポイント形式**: MinIOとS3のURL形式差異
   - **対策**: プロキシエンドポイントで差異を吸収済み

**結論**: 現在の実装は AWS 移行に対して高い互換性を持ち、大きな変更なしに移行可能です。

### モデル定義例

```python
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class GameSession(Base):
    __tablename__ = 'game_sessions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    game_data = Column(Text)
    created_at = Column(DateTime, default=func.now())
```

## クイック確認コマンド

### 📋 **データベース状態確認**
```bash
# テーブル一覧表示
docker-compose exec mysql mysql -u root -ppassword janken_battle_complete -e "SHOW TABLES;"

# ユーザー確認
docker-compose exec mysql mysql -u root -ppassword janken_battle_complete -e "SELECT user_id, email, nickname, role FROM users;"

# システム設定確認
docker-compose exec mysql mysql -u root -ppassword janken_battle_complete -e "SELECT setting_key, setting_value FROM system_settings;"

# 認証テーブル構造確認
docker-compose exec mysql mysql -u root -ppassword janken_battle_complete -e "DESCRIBE users; DESCRIBE sessions; DESCRIBE magic_link_tokens;"
```

### 🔧 **トラブルシューティング確認**
```bash
# データベース接続確認
docker-compose exec mysql mysql -u root -ppassword -e "SHOW DATABASES;"

# テーブル数確認
docker-compose exec mysql mysql -u root -ppassword janken_battle_complete -e "SELECT COUNT(*) as table_count FROM information_schema.tables WHERE table_schema='janken_battle_complete';"

# コンテナ状態確認
docker-compose ps

# ログ確認
docker-compose logs mysql | tail -20
```

## Docker環境の管理

```bash
# コンテナの状態確認
docker-compose ps

# ログの確認
docker-compose logs

# 特定のサービスのログ確認
docker-compose logs api

# コンテナの停止
docker-compose down

# コンテナの再起動
docker-compose restart
```

## OCR処理機能

### サポートする画像形式
- JPEG, PNG, GIF, BMP, TIFF
- 最大ファイルサイズ: 10MB

### OCR処理フロー
1. 画像アップロード（MinIO）
2. 画像前処理（Pillow）
3. OCR処理（Tesseract/Textract）
4. 結果の返却

### 使用例

```python
import requests

# 画像アップロード & OCR処理
with open("image.jpg", "rb") as f:
    response = requests.post(
        "http://localhost/api/ocr/process",
        files={"image": f}
    )
    
result = response.json()
print(result["text"])
```

## ファイル操作・ストレージ管理

### MinIOストレージ操作

#### 基本的なファイル操作
```bash
# ファイルアップロード
curl -X POST "http://localhost/storage/upload/profile-images" \
  -F "file=@image.png"

# ファイル一覧取得
curl "http://localhost/storage/files/profile-images"

# ファイル表示（プロキシ経由）
curl "http://localhost/storage/proxy/profile-images/filename.png"

# ファイル削除
curl -X DELETE "http://localhost/storage/delete/profile-images/filename.png"

# ストレージ統計取得
curl "http://localhost/storage/stats"
```

#### 利用可能なバケットタイプ
- `profile-images`: プロフィール画像
- `student-ids`: 学生証画像  
- `temp-uploads`: 一時ファイル

#### ファイル表示の仕組み
1. **署名付きURL方式** (`/storage/view/`): MinIOの署名付きURLを取得
2. **プロキシ方式** (`/storage/proxy/`): APIサーバー経由でファイル配信

プロキシ方式の利点：
- 外部エンドポイント依存なし
- 統一されたCORS設定
- アクセス制御の一元化

### ストレージ管理用WebUI

#### アクセス方法
- ストレージ管理: `http://localhost/storage-html/`
- テストページ: `http://localhost/storage-html/storage-test.html`
- MinIO管理画面: `http://192.168.0.155:9000/`

#### 主な機能
- ファイルアップロード・削除・表示
- バケット別統計表示
- ファイル一覧表示
- 画像プレビュー機能

## トラブルシューティング

### よくある問題と解決策

1. SAMビルドエラー
   - Python バージョンの確認
   - 依存関係の確認: `pip install -r requirements.txt`
   - template.yaml の構文確認

2. データベース接続エラー
   - SQLAlchemy接続文字列の確認
   - MySQL/MariaDBサーバーの状態確認
   - データベース名の確認（`janken_battle_complete`）
   - 非同期ドライバー（aiomysql）のインストール確認

3. OCR処理エラー
   - Tesseract のインストール確認
   - 画像形式の確認
   - ファイルサイズの確認

4. MinIO接続エラー
   - MinIOサーバーの状態確認
   - 接続情報の確認（別サーバー）
   - ネットワーク接続の確認

5. ストレージファイル表示エラー
   - Nginx設定の確認（`/storage/` プロキシ設定）
   - APIサーバーの動作確認（`http://localhost:3000/storage/health`）
   - MinIOサーバーの接続確認
   - プロキシエンドポイント使用を推奨（`/storage/proxy/`）

### デバッグモード

```bash
# 詳細なログ出力の有効化
DEBUG=true sam local start-api

# または
DEBUG=true docker-compose up -d
```

## ライセンス

MIT

## コントリビューション

Issue、Pull Requestは歓迎します。
