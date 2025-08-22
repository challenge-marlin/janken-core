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

## 📱 アプリケーションの実行

### 起動中のエミュレータ確認
```bash
flutter devices
```

### 1. game-app (モバイルクライアント)

```bash
cd client/game-app
flutter run               # デフォルトデバイスで実行
flutter run -d chrome     # Webブラウザで実行
flutter run -d android    # Androidエミュレータで実行  
flutter run -d ios        # iOSシミュレータで実行（Mac環境）
```

### 2. admin-app (デスクトップ管理アプリ)

```bash
cd client/admin-app
flutter run -d windows    # Windows向け
flutter run -d macos      # macOS向け（Mac環境）
flutter run -d linux      # Linux向け（Linux環境）
```

### 環境別実行オプション

#### 開発環境（ローカルサーバー接続）
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
```bash
# ゲームアプリ（プロダクション環境）
cd client/game-app
flutter run --dart-define=ENV=production

# 管理アプリ（プロダクション環境）
cd client/admin-app
flutter run -d windows --dart-define=ENV=production
```

### ホットリロード機能

Flutter開発中は以下のショートカットが利用できます：
- **r**: ホットリロード（状態を保持したままUI更新）
- **R**: ホットリスタート（アプリを完全再起動）
- **q**: アプリケーション終了
- **h**: ヘルプ表示

### API設定について

クライアント側では環境変数により自動的にAPIエンドポイントが切り替わります：

- **開発環境**: `http://localhost` (ローカル実行)
- **プロダクション環境**: `http://160.251.137.105` (VPS/外部サーバー)

詳細は `client/game-app/lib/config/README.md` を参照してください。

## 🔐 認証テスト環境

### 認証テストページ

認証機能のテスト用Webページが用意されています：

#### アクセス方法
```
# Docker環境（推奨）
http://localhost/auth/       # 認証テストページ
http://localhost/monitor/    # モニタリングページ  
http://localhost/storage-html/ # ストレージ管理ページ

# 直接アクセス（開発時）
http://localhost:3000/auth/
http://localhost:3000/monitor/
http://localhost:3000/storage-html/
```

#### 利用可能なテスト機能
1. **Magic Link認証**: メール認証によるパスワードレスログイン
2. **開発用認証**: テストユーザー(1-5)での簡易ログイン  
3. **従来形式認証**: ID/パスワード方式（互換性維持）
4. **JWT管理**: トークンの表示・検証・管理
5. **システムモニタリング**: パフォーマンスメトリクス表示
6. **ストレージ管理**: ファイルアップロード・管理機能

#### Docker環境での起動
```bash
# サーバーディレクトリに移動
cd server

# Docker環境を起動
docker-compose up -d

# 環境確認
docker-compose ps
```

#### 環境別アクセス設定
- **開発環境（Docker）**: `http://localhost` (Nginx経由)
- **開発環境（直接）**: `http://localhost:3000` 
- **VPS環境**: `http://160.251.137.105`

#### トラブルシューティング
- **接続エラー**: Docker環境が起動しているか確認
- **404エラー**: Nginx設定とmain-htmlマウントを確認
- **JavaScript関数エラー**: ブラウザでハードリフレッシュ (Ctrl+Shift+R)

### Docker環境構成
```
localhost:80     → Nginx → APIサーバー
localhost:3000   → APIサーバー（直接）
localhost:8080   → phpMyAdmin
localhost:8081   → Redis Commander
```

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
