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

## 🏗️ アーキテクチャ設計

### 画面単位API分離原則

本プロジェクトは **画面単位でのAPI分離原則** を採用しています：

#### 🎯 **基本方針**
1. **画面専用API**: 各画面（認証、ロビー、設定、バトル等）には専用のAPIエンドポイントを用意
2. **機能横断の禁止**: あるAPIの修正が他画面に影響することを防ぐため、APIの機能横断的な使用は禁止
3. **代替案の回避**: クライアントが既存APIの組み合わせで代替実装することは避け、必要な機能は専用APIとして実装
4. **独立性の保証**: 各画面のAPIは独立して動作し、他画面のAPIに依存しない設計

#### 🏗️ **実装責任**
- **サーバーサイド**: 画面ごとに必要な専用APIを実装する責任
- **クライアントサイド**: 画面に対応する専用APIのみを使用する責任

## 📋 Flutterコーディングルール

### 基本設計思想

#### **1. ウィジェット単位の責任分離**
- **画面単位**: 各画面は独立したディレクトリで管理
- **機能単位**: 再利用可能なウィジェットは`widgets/`配下に配置
- **状態管理**: 各画面の状態は画面内で完結、必要に応じてProvider/Bloc使用

#### **2. AI連携のための一貫性**
- **命名規則**: 統一された命名パターンでAIの理解を促進
- **ファイル構造**: 予測可能なディレクトリ構成
- **コメント**: 日本語での意図説明でAIの理解をサポート

### ディレクトリ構造ルール

```
lib/
├── pages/                    # 画面単位のページ
│   ├── auth/                # 認証関連画面
│   │   ├── login_page.dart
│   │   ├── register_page.dart
│   │   └── forgot_password_page.dart
│   ├── lobby/               # ロビー画面
│   │   └── lobby_page.dart
│   ├── battle/              # バトル画面
│   │   ├── battle_page.dart
│   │   └── battle_result_page.dart
│   └── settings/            # 設定画面
│       └── settings_page.dart
├── widgets/                  # 再利用可能ウィジェット
│   ├── common/              # 共通ウィジェット
│   │   ├── custom_button.dart
│   │   ├── custom_text_field.dart
│   │   └── loading_indicator.dart
│   ├── auth/                # 認証専用ウィジェット
│   ├── battle/              # バトル専用ウィジェット
│   └── lobby/               # ロビー専用ウィジェット
├── services/                 # 外部サービス連携
│   ├── api_service.dart
│   ├── auth_service.dart
│   └── websocket_service.dart
├── models/                   # データモデル
│   ├── user.dart
│   ├── battle.dart
│   └── game_state.dart
├── providers/                # 状態管理
│   ├── auth_provider.dart
│   └── game_provider.dart
└── utils/                    # ユーティリティ
    ├── constants.dart
    ├── helpers.dart
    └── validators.dart
```

### コーディング規約

#### **1. ファイル命名規則**
```dart
// ✅ GOOD: 明確で一貫性のある命名
login_page.dart          // 画面ページ
custom_button.dart       // 再利用可能ウィジェット
auth_service.dart        // サービス
user_model.dart          // データモデル

// ❌ BAD: 曖昧で一貫性のない命名
page.dart               // 何のページか不明
button.dart             // どのボタンか不明
service.dart            // どのサービスか不明
```

#### **2. クラス命名規則**
```dart
// ✅ GOOD: 目的が明確
class LoginPage extends StatefulWidget
class CustomButton extends StatelessWidget
class AuthService
class UserModel

// ❌ BAD: 曖昧
class Page extends StatefulWidget
class Button extends StatelessWidget
class Service
class Model
```

#### **3. 変数・関数命名規則**
```dart
// ✅ GOOD: 日本語的な理解を促進
bool _isLoading = false;
bool _isAuthenticated = false;
String _userName = '';
int _battleCount = 0;

void _handleLogin() {}
void _startBattle() {}
void _updateUserProfile() {}

// ❌ BAD: 英語的すぎて意図が不明
bool _loading = false;
bool _auth = false;
String _name = '';
int _count = 0;

void _login() {}
void _battle() {}
void _update() {}
```

### ウィジェット設計ルール

#### **1. 単一責任の原則**
```dart
// ✅ GOOD: 1つのウィジェットに1つの責任
class UserProfileWidget extends StatelessWidget {
  final User user;
  
  const UserProfileWidget({super.key, required this.user});
  
  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        _buildProfileImage(),
        _buildUserInfo(),
        _buildStats(),
      ],
    );
  }
  
  Widget _buildProfileImage() { /* プロフィール画像のみ */ }
  Widget _buildUserInfo() { /* ユーザー情報のみ */ }
  Widget _buildStats() { /* 統計情報のみ */ }
}

// ❌ BAD: 複数の責任を持つウィジェット
class UserWidget extends StatelessWidget {
  // プロフィール、統計、設定、友達リストなど全てを含む
}
```

#### **2. 再利用性の考慮**
```dart
// ✅ GOOD: 汎用的で再利用可能
class CustomButton extends StatelessWidget {
  final String text;
  final VoidCallback? onPressed;
  final Color? backgroundColor;
  final double? width;
  final double? height;
  
  const CustomButton({
    super.key,
    required this.text,
    this.onPressed,
    this.backgroundColor,
    this.width,
    this.height,
  });
  
  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: width,
      height: height,
      child: ElevatedButton(
        onPressed: onPressed,
        style: ElevatedButton.styleFrom(
          backgroundColor: backgroundColor,
        ),
        child: Text(text),
      ),
    );
  }
}

// ❌ BAD: 特定の用途に固定
class LoginButton extends StatelessWidget {
  // ログイン専用で他の場所では使えない
}
```

### 状態管理ルール

#### **1. 画面内完結の原則**
```dart
// ✅ GOOD: 画面内で状態を管理
class BattlePage extends StatefulWidget {
  @override
  State<BattlePage> createState() => _BattlePageState();
}

class _BattlePageState extends State<BattlePage> {
  bool _isPlaying = false;
  String _selectedHand = '';
  int _score = 0;
  
  void _startGame() {
    setState(() {
      _isPlaying = true;
      _score = 0;
    });
  }
}

// ❌ BAD: グローバル状態に過度に依存
class BattlePage extends StatelessWidget {
  // 全ての状態をProvider/Blocで管理
}
```

#### **2. 必要最小限の状態管理**
```dart
// ✅ GOOD: 必要な時だけProvider使用
class LobbyPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Consumer<AuthProvider>(
      builder: (context, auth, child) {
        if (auth.isLoading) return LoadingWidget();
        if (!auth.isAuthenticated) return LoginWidget();
        return LobbyContent(user: auth.currentUser);
      },
    );
  }
}

// ❌ BAD: 全ての状態をProviderで管理
class LobbyPage extends StatelessWidget {
  // ローディング、ユーザー、設定、統計など全てProvider
}
```

## 🔄 非同期処理ガイドライン

### WebSocket接続管理

#### **1. 接続状態の管理**
```dart
// ✅ GOOD: 明確な接続状態管理
class WebSocketService {
  WebSocket? _socket;
  bool _isConnected = false;
  StreamController<String>? _messageController;
  
  // 接続状態の監視
  Stream<bool> get connectionStatus => _connectionStatusController.stream;
  
  Future<bool> connect(String userId, String room) async {
    try {
      _socket = await WebSocket.connect(_buildUrl(userId, room));
      _isConnected = true;
      _setupMessageHandling();
      _connectionStatusController.add(true);
      return true;
    } catch (e) {
      _isConnected = false;
      _connectionStatusController.add(false);
      return false;
    }
  }
  
  void disconnect() {
    _socket?.close();
    _isConnected = false;
    _connectionStatusController.add(false);
  }
}
```

#### **2. メッセージ処理の非同期化**
```dart
// ✅ GOOD: 非同期メッセージ処理
class WebSocketService {
  void _setupMessageHandling() {
    _socket?.listen(
      (data) {
        _handleMessage(data);
      },
      onError: (error) {
        _handleError(error);
      },
      onDone: () {
        _handleDisconnect();
      },
    );
  }
  
  void _handleMessage(dynamic data) {
    try {
      final message = jsonDecode(data);
      _messageController?.add(message);
    } catch (e) {
      print('メッセージ解析エラー: $e');
    }
  }
}
```

#### **3. エラーハンドリングとリトライ**
```dart
// ✅ GOOD: 適切なエラーハンドリング
class WebSocketService {
  Timer? _reconnectTimer;
  int _reconnectAttempts = 0;
  static const int maxReconnectAttempts = 5;
  
  void _handleError(dynamic error) {
    print('WebSocketエラー: $error');
    _isConnected = false;
    _connectionStatusController.add(false);
    
    if (_reconnectAttempts < maxReconnectAttempts) {
      _scheduleReconnect();
    }
  }
  
  void _scheduleReconnect() {
    _reconnectTimer?.cancel();
    final delay = Duration(seconds: pow(2, _reconnectAttempts).toInt());
    _reconnectTimer = Timer(delay, () {
      _reconnectAttempts++;
      connect(_userId, _room);
    });
  }
}
```

### API通信の非同期処理

#### **1. 適切なFuture/async-await使用**
```dart
// ✅ GOOD: 明確な非同期処理
class ApiService {
  Future<Map<String, dynamic>> getUserProfile(String userId) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/users/$userId'),
        headers: await _getAuthHeaders(),
      );
      
      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw ApiException('プロフィール取得に失敗: ${response.statusCode}');
      }
    } catch (e) {
      throw ApiException('ネットワークエラー: $e');
    }
  }
}
```

#### **2. ローディング状態の管理**
```dart
// ✅ GOOD: ローディング状態の適切な管理
class UserProfilePage extends StatefulWidget {
  @override
  State<UserProfilePage> createState() => _UserProfilePageState();
}

class _UserProfilePageState extends State<UserProfilePage> {
  bool _isLoading = false;
  User? _user;
  String? _error;
  
  @override
  void initState() {
    super.initState();
    _loadUserProfile();
  }
  
  Future<void> _loadUserProfile() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });
    
    try {
      final userData = await ApiService().getUserProfile(widget.userId);
      setState(() {
        _user = User.fromJson(userData);
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }
}
```

### 非同期処理のベストプラクティス

#### **1. 適切なエラーハンドリング**
```dart
// ✅ GOOD: 包括的なエラーハンドリング
Future<void> _performAction() async {
  try {
    setState(() => _isLoading = true);
    
    // 非同期処理
    await _apiService.performAction();
    
    // 成功時の処理
    _showSuccessMessage();
    
  } catch (e) {
    // エラーの種類に応じた処理
    if (e is NetworkException) {
      _showNetworkErrorDialog();
    } else if (e is AuthException) {
      _redirectToLogin();
    } else {
      _showGenericErrorDialog(e.toString());
    }
  } finally {
    setState(() => _isLoading = false);
  }
}
```

#### **2. 非同期処理のキャンセル**
```dart
// ✅ GOOD: 適切なキャンセル処理
class _MyPageState extends State<MyPage> {
  Future<void>? _currentOperation;
  
  @override
  void dispose() {
    _currentOperation?.ignore();
    super.dispose();
  }
  
  Future<void> _startOperation() async {
    // 前の操作をキャンセル
    _currentOperation?.ignore();
    
    // 新しい操作を開始
    _currentOperation = _performOperation();
    await _currentOperation;
  }
}
```

#### **3. 並行処理の管理**
```dart
// ✅ GOOD: 並行処理の適切な管理
Future<void> _loadInitialData() async {
  setState(() => _isLoading = true);
  
  try {
    // 並行してデータを読み込み
    final results = await Future.wait([
      _loadUserProfile(),
      _loadUserStats(),
      _loadRecentBattles(),
    ]);
    
    setState(() {
      _userProfile = results[0];
      _userStats = results[1];
      _recentBattles = results[2];
      _isLoading = false;
    });
    
  } catch (e) {
    setState(() {
      _error = e.toString();
      _isLoading = false;
    });
  }
}
```

### 避けるべき非同期処理パターン

#### **1. 非同期処理の無視**
```dart
// ❌ BAD: 非同期処理の結果を無視
void _handleButtonPress() {
  _apiService.performAction(); // Futureの結果を無視
  _showSuccessMessage(); // 実際には失敗している可能性
}

// ✅ GOOD: 適切な非同期処理
Future<void> _handleButtonPress() async {
  try {
    await _apiService.performAction();
    _showSuccessMessage();
  } catch (e) {
    _showErrorMessage(e.toString());
  }
}
```

#### **2. 過度なネスト**
```dart
// ❌ BAD: 過度にネストした非同期処理
void _loadData() {
  _apiService.getUser().then((user) {
    _apiService.getUserProfile(user.id).then((profile) {
      _apiService.getUserStats(user.id).then((stats) {
        setState(() {
          _user = user;
          _profile = profile;
          _stats = stats;
        });
      });
    });
  });
}

// ✅ GOOD: async-awaitを使用した読みやすい処理
Future<void> _loadData() async {
  try {
    final user = await _apiService.getUser();
    final profile = await _apiService.getUserProfile(user.id);
    final stats = await _apiService.getUserStats(user.id);
    
    setState(() {
      _user = user;
      _profile = profile;
      _stats = stats;
    });
  } catch (e) {
    _handleError(e);
  }
}
```

## 🧪 テスト戦略

### ウィジェットテスト
```dart
// ✅ GOOD: 各ウィジェットの独立テスト
void main() {
  group('CustomButton Widget Tests', () {
    testWidgets('ボタンが正しく表示される', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: CustomButton(
            text: 'テスト',
            onPressed: () {},
          ),
        ),
      );
      
      expect(find.text('テスト'), findsOneWidget);
      expect(find.byType(ElevatedButton), findsOneWidget);
    });
  });
}
```

## 📚 AI連携のためのコメント規約

### 日本語での意図説明
```dart
/// ユーザープロフィール表示ウィジェット
/// 
/// このウィジェットは以下の要素を表示します：
/// - プロフィール画像（円形、100x100）
/// - ユーザー名（最大20文字、省略表示対応）
/// - 称号（オプション、オレンジ色）
/// - 統計情報（勝利数、敗北数、引分数）
/// 
/// 使用例：
/// ```dart
/// UserProfileWidget(user: currentUser)
/// ```
class UserProfileWidget extends StatelessWidget {
  // ... 実装
}
```

### 複雑なロジックの説明
```dart
/// じゃんけんの勝敗判定ロジック
/// 
/// 判定ルール：
/// 1. グー(0) vs チョキ(1) → グーの勝ち
/// 2. チョキ(1) vs パー(2) → チョキの勝ち  
/// 3. パー(2) vs グー(0) → パーの勝ち
/// 4. 同じ手 → 引き分け
/// 
/// 戻り値：
/// - 1: プレイヤーの勝ち
/// - -1: 相手の勝ち
/// - 0: 引き分け
int _determineWinner(int playerHand, int opponentHand) {
  // ... 実装
}
```

## 🚫 避けるべきパターン

### 過度な抽象化
```dart
// ❌ BAD: 必要以上に抽象化
class GameStateManager {
  static GameStateManager? _instance;
  static GameStateManager get instance => _instance ??= GameStateManager._();
  
  // シングルトンパターンで複雑化
}

// ✅ GOOD: シンプルで理解しやすい
class GameState extends ChangeNotifier {
  // 必要な状態のみ管理
}
```

### マジックナンバー・文字列
```dart
// ❌ BAD: マジックナンバー
Container(width: 100, height: 100)
Text('ログイン', style: TextStyle(fontSize: 16))

// ✅ GOOD: 定数で管理
class AppConstants {
  static const double profileImageSize = 100.0;
  static const double buttonHeight = 100.0;
  static const double defaultFontSize = 16.0;
}
```

## 💡 AIへの指示例

```
このプロジェクトは以下のFlutterコーディングルールに従っています：

1. 画面単位の責任分離（pages/配下に配置）
2. 再利用可能ウィジェットはwidgets/配下に配置
3. 日本語での意図説明コメント必須
4. 単一責任の原則（1ウィジェット1責任）
5. 必要最小限の状態管理
6. レスポンシブデザイン対応
7. 適切な非同期処理（WebSocket、API通信）
8. 包括的なエラーハンドリング

新機能追加時は、既存のディレクトリ構造と命名規則に従い、
適切な場所に配置してください。非同期処理が必要な場合は、
適切なエラーハンドリングとローディング状態管理を実装してください。
```

## 🚨 既存コードとの衝突回避（最重要）

### 命名衝突の回避ルール

#### **1. 汎用名の使用制限**
```dart
// ❌ BAD: 汎用的すぎる名前（既存コードと衝突しやすい）
class Button extends StatelessWidget
class Card extends StatelessWidget
class Input extends StatelessWidget
class List extends StatelessWidget

// ✅ GOOD: 具体的で機能を表す名前
class PrimaryButton extends StatelessWidget
class UserProfileCard extends StatelessWidget
class EmailInputField extends StatelessWidget
class BattleHistoryList extends StatelessWidget
```

#### **2. 既存コードとの重複チェック**
```dart
// AIへの指示例：
// 「新しいウィジェットや変数名を生成する際は、既存のプロジェクト内で
// 同名のものが存在しないことを確認し、もし衝突する場合は、
// より具体的な名前を提案してください」

// 例：UserListが既に存在する場合
// ❌ 衝突: UserList
// ✅ 回避: UserDetailList, AdminUserList, BattleUserList
```

#### **3. ファイル配置の優先順位**
```dart
// 1. 画面専用ウィジェット: pages/{画面名}/widgets/
// 2. 機能専用ウィジェット: widgets/{機能名}/
// 3. 共通ウィジェット: widgets/common/（最後の手段）

// 例：
// pages/battle/widgets/battle_result_card.dart
// widgets/auth/login_form.dart
// widgets/common/custom_button.dart（既存のButtonと衝突する場合のみ）
```

### ファイル管理とバージョン管理

#### **1. 新規作成の原則**
```dart
// ✅ GOOD: 既存コンポーネントを継承・ラップ
class EnhancedUserProfileCard extends UserProfileCard {
  // 既存のUserProfileCardを拡張
}

class BattleUserProfileCard extends StatelessWidget {
  // 既存のUserProfileCardをラップ
  @override
  Widget build(BuildContext context) {
    return UserProfileCard(
      user: widget.user,
      showBattleStats: true, // バトル専用の追加機能
    );
  }
}

// ❌ BAD: 既存ファイルの直接修正
// 既存のuser_profile_card.dartを直接編集しない
```

#### **2. ファイル命名の一意性確保**
```dart
// ファイル名の例（機能を明確化）
user_profile_card.dart           // 基本プロフィールカード
battle_user_profile_card.dart    // バトル用プロフィールカード
admin_user_profile_card.dart     // 管理者用プロフィールカード
compact_user_profile_card.dart   // コンパクト版プロフィールカード

// クラス名も一意性を確保
class UserProfileCard extends StatelessWidget
class BattleUserProfileCard extends StatelessWidget
class AdminUserProfileCard extends StatelessWidget
class CompactUserProfileCard extends StatelessWidget
```

#### **3. 既存コード参照の重要性**
```dart
// AIへの指示例：
// 「新しい機能を依頼する際は、関連する既存のウィジェットや
// データ構造のコードスニペットをプロンプトに含めるか、
// 参照するよう指示してください」

// 既存コードの例：
class UserProfileCard extends StatelessWidget {
  final User user;
  final bool showStats;
  final VoidCallback? onTap;
  
  const UserProfileCard({
    super.key,
    required this.user,
    this.showStats = true,
    this.onTap,
  });
  
  // ... 実装
}

// 新機能追加時は、この既存コードを参照して
// 衝突しない名前と構造を提案する
```

### 衝突回避のチェックリスト

#### **1. 新規ウィジェット作成時**
- [ ] 既存の`lib/`配下で同名ファイルを検索
- [ ] 既存のクラス名との重複をチェック
- [ ] より具体的で機能を表す名前を検討
- [ ] 適切なディレクトリに配置

#### **2. 既存コード修正時**
- [ ] 修正対象ファイルのバックアップを作成
- [ ] 変更内容を明確に文書化
- [ ] 影響範囲を最小限に抑制
- [ ] テストで動作確認を実施

#### **3. ファイル管理**
- [ ] 新規ファイルは適切なディレクトリに配置
- [ ] 既存ファイルの直接編集は避ける
- [ ] 継承・ラップによる拡張を優先
- [ ] ファイル名とクラス名の一意性を確保

### 実用的な命名パターン

#### **1. 機能別プレフィックス**
```dart
// 認証関連
class AuthLoginButton extends StatelessWidget
class AuthRegisterForm extends StatelessWidget
class AuthForgotPasswordLink extends StatelessWidget

// バトル関連
class BattleStartButton extends StatelessWidget
class BattleResultDisplay extends StatelessWidget
class BattleHandSelector extends StatelessWidget

// ロビー関連
class LobbyUserList extends StatelessWidget
class LobbyChatWindow extends StatelessWidget
class LobbySettingsPanel extends StatelessWidget
```

#### **2. サイズ・バリエーション別サフィックス**
```dart
// サイズ別
class UserProfileCardLarge extends StatelessWidget
class UserProfileCardMedium extends StatelessWidget
class UserProfileCardSmall extends StatelessWidget

// バリエーション別
class UserProfileCardCompact extends StatelessWidget
class UserProfileCardDetailed extends StatelessWidget
class UserProfileCardMinimal extends StatelessWidget
```

#### **3. 状態・モード別サフィックス**
```dart
// 状態別
class UserProfileCardLoading extends StatelessWidget
class UserProfileCardError extends StatelessWidget
class UserProfileCardEmpty extends StatelessWidget

// モード別
class UserProfileCardEditMode extends StatelessWidget
class UserProfileCardViewMode extends StatelessWidget
class UserProfileCardAdminMode extends StatelessWidget
```

### AIへの具体的指示例

```
新しいウィジェットを作成する際は、以下の点を必ず確認してください：

1. 既存のlib/配下で同名ファイルが存在しないか検索
2. 既存のクラス名と重複しないかチェック
3. 衝突する場合は、より具体的で機能を表す名前を提案
4. 適切なディレクトリに配置（pages/{画面名}/widgets/を優先）
5. 既存コードとの整合性を保つ

例：
- Button → PrimaryButton, SubmitButton, CancelButton
- Card → UserProfileCard, BattleResultCard, SettingsCard
- List → UserList, BattleHistoryList, RankingList

既存のコードを直接修正するのではなく、新しいウィジェットを作成するか、
継承・ラップによる拡張を検討してください。
```

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
cd .\client\game-app\
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
