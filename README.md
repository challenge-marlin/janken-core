# Janken Core - じゃんけんゲーム モノレポ

このリポジトリは、じゃんけんゲームアプリケーションのモノレポ構成です。サーバー、クライアントアプリを一元管理し、効率的な開発と保守を実現します。

## 🎯 プロジェクト概要

大規模（最大1万人）のユーザーに対応するじゃんけんゲームプラットフォームです。

### アーキテクチャ

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Game App      │    │   Admin App     │    │     Server      │
│   (Flutter)     │◄──►│   (Flutter)     │◄──►│   (FastAPI)     │
│  iOS/Android    │    │   (Windows)     │    │   + Docker      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 プロジェクト構造

```
janken-core/
├── client/                    # クライアントアプリケーション
│   ├── game-app/             # じゃんけんゲームアプリ (Flutter - iOS/Android)
│   └── admin-app/            # 管理アプリ (Flutter - Windows)
├── server/                   # サーバーアプリケーション (FastAPI + Python + Docker)
├── shared/                   # 共有リソース
│   ├── models/              # データモデル
│   ├── types/               # 型定義
│   └── utils/               # ユーティリティ
├── docs/                     # ドキュメント
│   ├── api/                 # API仕様
│   ├── database/            # データベース仕様
│   └── architecture/        # アーキテクチャ設計
└── scripts/                  # ビルド・デプロイスクリプト
```

## 🚀 技術スタック

### サーバー
- **FastAPI** - 高性能WebAPIフレームワーク
- **Python** - バックエンド言語
- **Docker** - コンテナ化

### クライアント
- **Flutter** - クロスプラットフォーム開発
- **iOS/Android** - ゲームアプリ
- **Windows** - 管理アプリ

## 📱 アプリケーション詳細

### ゲームアプリ (`client/game-app/`)
- **対象プラットフォーム**: iOS、Android
- **開発環境**: Android Studio + Flutter
- **機能**: 
  - じゃんけんゲーム
  - ランキング機能
  - ユーザー管理

### 管理アプリ (`client/admin-app/`)
- **対象プラットフォーム**: Windows
- **開発環境**: Flutter
- **機能**:
  - ユーザーBAN機能
  - リアルタイムランキング確認
  - システム管理

### サーバー (`server/`)
- **インフラ**: FastAPI + Docker
- **機能**:
  - REST API提供
  - リアルタイム処理
  - データ管理
  - 認証・認可

## 🏗️ セットアップガイド

### 前提条件

- Flutter SDK
- Python 3.9+
- Docker & Docker Compose
- Android Studio (Androidアプリ開発用)

### 初期セットアップ

1. **リポジトリのクローン**
   ```bash
   git clone <repository-url>
   cd janken-core
   ```

2. **各プロジェクトの配置**
   - 既存のプロジェクトを対応するフォルダに移動
   - 詳細は下記の「プロジェクト配置ガイド」を参照

## 📦 プロジェクト配置ガイド

### 1. サーバープロジェクトの配置

既存のFastAPI + Pythonプロジェクトを `server/` フォルダに配置してください：

```bash
# 既存のサーバープロジェクトから
cp -r your-fastapi-project/* server/
```

現在の構造：
```
server/
├── src/                   # FastAPIアプリケーションコード
├── requirements.txt       # Python依存関係
├── Dockerfile             # Docker設定
├── docker-compose.yml     # Docker Compose設定
├── alembic.ini           # データベースマイグレーション設定
└── tests/                # テストコード
```

### 2. ゲームアプリの配置

既存のFlutterゲームアプリを `client/game-app/` フォルダに配置してください：

```bash
# 既存のFlutterゲームアプリから
cp -r your-flutter-game/* client/game-app/
```

### 3. 管理アプリの配置

既存のFlutter管理アプリを `client/admin-app/` フォルダに配置してください：

```bash
# 既存のFlutter管理アプリから
cp -r your-flutter-admin/* client/admin-app/
```

## 🛠️ 開発ワークフロー

### サーバー開発
```bash
cd server
docker-compose up --build
```

### Flutter アプリ開発

#### 開発環境（ローカル実行）
サーバーをローカルで実行している場合：
```bash
# 1. サーバー側を先に起動
cd server
docker-compose up -d

# 2. ゲームアプリ（開発環境）
cd client/game-app
flutter run

# 3. 管理アプリ（開発環境）
cd client/admin-app
flutter run -d windows
```

#### プロダクション環境（外部サーバー接続）
外部サーバーに接続する場合：
```bash
# ゲームアプリ（プロダクション環境）
cd client/game-app
flutter run --dart-define=ENV=production

# 管理アプリ（プロダクション環境）
cd client/admin-app
flutter run -d windows --dart-define=ENV=production
```

### API設定について

クライアント側では環境変数により自動的にAPIエンドポイントが切り替わります：

- **開発環境**: `http://localhost` (ローカル実行)
- **プロダクション環境**: `http://160.251.137.105` (VPS/外部サーバー)

詳細は `client/game-app/lib/config/README.md` を参照してください。

## 📚 ドキュメント

- **API仕様**: `docs/api/`
- **データベース設計**: `docs/database/`
- **アーキテクチャ**: `docs/architecture/`

## 🤝 コントリビューション

1. 機能ブランチを作成
2. 変更をコミット
3. プルリクエストを作成

## 📄 ライセンス

このプロジェクトは社内利用のため、外部配布は禁止されています。

---

**Note**: 各アプリケーションの詳細なREADMEは、それぞれのフォルダ内に個別に作成してください。
