# じゃんけんゲーム - 管理アプリ

Windows向けデスクトップ管理アプリケーション（Flutter Desktop）

## 🎯 概要

じゃんけんゲームシステムの管理・監視を行うWindows向けデスクトップアプリケーションです。

### 主な機能
- ユーザーBAN機能
- リアルタイムランキング確認
- システム監視・メトリクス表示
- データベース管理
- ゲーム統計・分析
- サーバー状態監視

## 🚀 技術スタック

- **Flutter Desktop** - Windows向けデスクトップアプリ
- **HTTP** - API通信
- **Data Table 2** - データテーブル表示
- **FL Chart** - グラフ・チャート表示
- **SharedPreferences** - 設定保存

## 🖥️ 対応プラットフォーム

- Windows（メイン対象）
- macOS（開発・テスト用）
- Linux（開発・テスト用）

## 🛠️ セットアップ

### 前提条件
- Flutter SDK（3.7.2以上）
- Visual Studio（Windows向けビルド用）
- Windows 10/11

### 依存関係のインストール
```bash
flutter pub get
```

### アプリの実行

#### 起動中のデバイス確認
```bash
flutter devices
```

#### 実行コマンド
```bash
# Windowsで実行
flutter run -d windows

# macOSで実行（Mac環境）
flutter run -d macos

# Linuxで実行（Linux環境）
flutter run -d linux
```

### 環境設定

#### 開発環境（ローカルサーバー接続）
```bash
flutter run -d windows
```

#### プロダクション環境（外部サーバー接続）
```bash
flutter run -d windows --dart-define=ENV=production
```

## 🔧 ビルド

### Windows実行ファイル
```bash
flutter build windows --release
```

### macOS アプリ
```bash
flutter build macos --release
```

### Linux実行ファイル
```bash
flutter build linux --release
```

## 🧪 テスト

```bash
# 単体テスト実行
flutter test

# ウィジェットテスト実行
flutter test test/widget_test.dart
```

## 🎨 UI構成

### メイン画面
- ダッシュボード - システム全体の状況表示
- ユーザー管理 - BAN/解除、プロフィール確認
- ランキング - リアルタイムランキング表示
- 統計・分析 - ゲームデータの分析

### 管理機能
- サーバー監視 - CPU、メモリ、レスポンス時間
- データベース管理 - データ確認・バックアップ
- ログ監視 - エラーログ、アクセスログ
- システム設定 - 各種設定の変更

## 📊 監視項目

### システムメトリクス
- サーバーパフォーマンス
- データベース接続状況
- アクティブユーザー数
- ゲーム対戦数

### ユーザー管理
- 登録ユーザー数
- BAN・警告状況
- 不正行為検出
- ランキング変動

## 🔐 セキュリティ

### 認証
- 管理者専用認証
- 権限レベル管理
- 操作ログ記録
- セッション管理

### アクセス制御
- IP制限
- 操作権限制限
- 重要操作の承認フロー
- 監査ログ

## 📱 開発時のヒント

### ホットリロード
- **r**: ホットリロード（状態を保持したままUI更新）
- **R**: ホットリスタート（アプリを完全再起動）
- **q**: アプリケーション終了

### デバッグ
```bash
# デバッグモードで実行
flutter run -d windows --debug

# プロファイルモードで実行
flutter run -d windows --profile
```

### Windows特有の設定
```bash
# Windows向けの最適化
flutter config --enable-windows-desktop

# Visual Studio Build Toolsの確認
flutter doctor
```

## 🔗 関連リンク

- [サーバーAPI仕様](../../docs/api/)
- [データベース設計](../../docs/database/)
- [プロジェクト全体README](../../README.md)
- [ゲームアプリ](../game-app/README.md)

## 📋 トラブルシューティング

### よくある問題
1. **Windows Build Toolsエラー**
   ```bash
   flutter doctor
   # Visual Studio Build Toolsを再インストール
   ```

2. **依存関係エラー**
   ```bash
   flutter clean
   flutter pub get
   ```

3. **実行権限エラー**
   - 管理者権限でTerminalを実行
   - Windows Defender除外設定を確認