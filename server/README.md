# かみのてじゃんけん - バックエンドAPIサーバー

じゃんけんゲームのバックエンドAPIサーバーです。画像OCR処理機能を含み、VPS環境での開発/テストを経て、AWS環境への移行を前提とした設計となっています。

## 技術スタック

### 現行環境（VPS）
- Python 3.11+
- FastAPI (APIフレームワーク)
- Mangum (ASGI/Lambda adapter)
- AWS SAM (Serverless Application Model)
- SQLAlchemy 2.0 (ORM)
- Alembic (データベースマイグレーション)
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
│   │   │   ├── models.py         # SQLAlchemyモデル
│   │   │   └── migrations/       # Alembicマイグレーション
│   │   │       ├── alembic.ini
│   │   │       ├── env.py
│   │   │       └── versions/
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
├── template.yaml                 # SAM テンプレート
├── requirements.txt              # Python依存関係
├── alembic.ini                  # Alembic設定
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

## データベース管理（SQLAlchemy + Alembic）

### 基本的な使用方法

```python
# SQLAlchemy 2.0 + 非同期処理
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# 非同期エンジンの作成
engine = create_async_engine(
    "mysql+aiomysql://user:pass@localhost/dbname",
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True
)

# セッションファクトリー
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
```

### Alembicマイグレーション

```bash
# Alembicの初期化
alembic init migrations

# マイグレーションファイルの生成
alembic revision --autogenerate -m "Add user table"

# マイグレーションの実行
alembic upgrade head

# マイグレーション履歴の確認
alembic history

# 特定のリビジョンへの適用
alembic upgrade <revision_id>

# ダウングレード
alembic downgrade -1
```

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
    endpoint="192.168.100.10:9000",
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
- MinIO管理画面: `http://192.168.100.10:9000/`

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
   - 非同期ドライバー（aiomysql）のインストール確認
   - コネクションプールの設定確認

3. Alembicマイグレーションエラー
   - alembic.ini の設定確認
   - データベース接続権限の確認
   - マイグレーションファイルの構文確認
   - `alembic current` でマイグレーション状態を確認

4. OCR処理エラー
   - Tesseract のインストール確認
   - 画像形式の確認
   - ファイルサイズの確認

5. MinIO接続エラー
   - MinIOサーバーの状態確認
   - 接続情報の確認（別サーバー）
   - ネットワーク接続の確認

6. ストレージファイル表示エラー
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
