# 神の手じゃんけん - ゲームアプリ

じゃんけんゲームのメインクライアントアプリケーション（Flutter - iOS/Android対応）

## 🎯 概要

大規模（最大1万人）のユーザーに対応するじゃんけんゲームプラットフォームのクライアントアプリです。

### 主な機能
- じゃんけんゲーム対戦
- ランキング機能
- ユーザー管理・プロフィール
- トーナメント機能
- フレンドマッチ
- 戦歴・統計表示

## 🚀 技術スタック

- **Flutter** - クロスプラットフォーム開発
- **Flame Engine** - ゲームエンジン
- **HTTP** - API通信
- **SharedPreferences** - ローカルストレージ
- **AudioPlayers** - 音響効果

## 📱 対応プラットフォーム

- iOS
- Android
- Web（開発・テスト用）

## 🛠️ セットアップ

### 前提条件
- Flutter SDK（3.1.3以上）
- Android Studio（Android開発用）
- Xcode（iOS開発用、Mac環境のみ）

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
# デフォルトデバイスで実行
flutter run

# 特定のデバイスで実行
flutter run -d android    # Androidエミュレータ
flutter run -d ios        # iOSシミュレータ（Mac環境）
flutter run -d chrome     # Webブラウザ
```
flutter run -d emulator-5556
### 環境設定

#### 開発環境（ローカルサーバー接続）
```bash
flutter run
```

#### プロダクション環境（外部サーバー接続）
```bash
flutter run --dart-define=ENV=production
```

## 🎨 アセット構成

### 画像
- `assets/images/backgrounds/` - 背景画像
- `assets/images/goddess/` - 女神キャラクター画像
- `assets/images/button/` - ボタン画像
- `assets/images/rank/` - ランクアイコン
- `assets/images/default_profiles/` - デフォルトプロフィール画像

### 音声
- `assets/sounds/BGM/` - 背景音楽
- `assets/sounds/Button/` - ボタン効果音

### フォント
- `M PLUS 1p` - メインフォント
- `Kosugi Maru` - 装飾用フォント
- `Cinzel` - タイトル用フォント

### データ
- `assets/json/` - ゲームメッセージデータ
- `assets/policy/` - 利用規約・プライバシーポリシー

## 🔧 ビルド

### Android APK
```bash
flutter build apk --release
```

### iOS IPA
```bash
flutter build ios --release
```

### Web
```bash
flutter build web --release
```

## 🧪 テスト

```bash
# 単体テスト実行
flutter test

# ウィジェットテスト実行
flutter test test/widget_test.dart
```

## 📱 開発時のヒント

### ホットリロード
- **r**: ホットリロード（状態を保持したままUI更新）
- **R**: ホットリスタート（アプリを完全再起動）
- **q**: アプリケーション終了

### デバッグ
```bash
# デバッグモードで実行
flutter run --debug

# プロファイルモードで実行
flutter run --profile
```

## 🔗 関連リンク

- [サーバーAPI仕様](../../docs/api/)
- [データベース設計](../../docs/database/)
- [プロジェクト全体README](../../README.md)
