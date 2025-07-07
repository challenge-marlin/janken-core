# Janken Core - じゃんけんゲーム モノレポ

このリポジトリは、じゃんけんゲームアプリケーションのモノレポ構成です。サーバー、クライアントアプリを一元管理し、効率的な開発と保守を実現します。

## 🎯 プロジェクト概要

大規模（最大1万人）のユーザーに対応するじゃんけんゲームプラットフォームです。

### アーキテクチャ

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Game App      │    │   Admin App     │    │     Server      │
│   (Flutter)     │◄──►│   (Flutter)     │◄──►│  (AWS Lambda)   │
│  iOS/Android    │    │   (Windows)     │    │    + SAM        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 プロジェクト構造

```
janken-core/
├── client/                    # クライアントアプリケーション
│   ├── game-app/             # じゃんけんゲームアプリ (Flutter - iOS/Android)
│   └── admin-app/            # 管理アプリ (Flutter - Windows)
├── server/                   # サーバーアプリケーション (AWS SAM + Python + Lambda)
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
- **AWS SAM (Serverless Application Model)**
- **Python** - Lambda関数
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
- **インフラ**: AWS Lambda + SAM
- **機能**:
  - API提供
  - リアルタイム処理
  - データ管理

## 🏗️ セットアップガイド

### 前提条件

- Flutter SDK
- Python 3.9+
- AWS CLI
- SAM CLI
- Docker
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

既存のSAM + Pythonプロジェクトを `server/` フォルダに配置してください：

```bash
# 既存のサーバープロジェクトから
cp -r your-sam-project/* server/
```

推奨構造：
```
server/
├── template.yaml          # SAM テンプレート
├── requirements.txt       # Python依存関係
├── src/                   # Lambda関数ソースコード
├── tests/                 # テストコード
├── Dockerfile             # Docker設定
└── samconfig.toml         # SAM設定
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
sam build
sam local start-api
```

### Flutter アプリ開発
```bash
# ゲームアプリ
cd client/game-app
flutter run

# 管理アプリ
cd client/admin-app
flutter run -d windows
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
