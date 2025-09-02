import 'package:flutter/material.dart';
import '../services/battle_websocket_service.dart';
import '../services/auth_service.dart';
import 'dart:async'; // Timerを追加

/// バトル画面の状態を管理するプロバイダークラス
/// 
/// このクラスは以下の状態を管理します：
/// - WebSocket接続状態
/// - マッチング状態
/// - 対戦状態
/// - ユーザーの手の選択
/// - 対戦結果
class BattleProvider extends ChangeNotifier {
  final BattleWebSocketService _webSocketService = BattleWebSocketService();
  final AuthService _authService = AuthService();
  
  // 接続状態
  bool _isConnected = false;
  bool _isConnecting = false;
  String? _connectionError;
  
  // マッチング状態
  bool _isMatching = false;
  String? _matchingId;
  int _queuePosition = 0;
  int _estimatedWaitTime = 0;
  
  // 対戦状態
  bool _isInBattle = false;
  String? _battleId;
  Map<String, dynamic>? _opponent;
  int _playerNumber = 0;
  String? _selectedHand;
  bool _isHandSubmitted = false;
  bool _isOpponentReady = false;
  bool _isReady = false;
  
  // 対戦結果
  Map<String, dynamic>? _battleResult;
  bool _isDraw = false;
  int _drawCount = 0;
  
  // 引き分け結果表示用の状態管理
  Timer? _drawResultTimer;
  bool _showingDrawResult = false;
  
  // ゲッター
  bool get isConnected => _isConnected;
  bool get isConnecting => _isConnecting;
  String? get connectionError => _connectionError;
  bool get isMatching => _isMatching;
  String? get matchingId => _matchingId;
  int get queuePosition => _queuePosition;
  int get estimatedWaitTime => _estimatedWaitTime;
  bool get isInBattle => _isInBattle;
  String? get battleId => _battleId;
  Map<String, dynamic>? get opponent => _opponent;
  int get playerNumber => _playerNumber;
  String? get selectedHand => _selectedHand;
  bool get isHandSubmitted => _isHandSubmitted;
  bool get isOpponentReady => _isOpponentReady;
  bool get isReady => _isReady;
  Map<String, dynamic>? get battleResult => _battleResult;
  bool get isDraw => _isDraw;
  int get drawCount => _drawCount;
  bool get isShowingDrawResult => _showingDrawResult;

  /// 初期化
  BattleProvider() {
    _setupWebSocketCallbacks();
  }

  /// WebSocketコールバックを設定
  void _setupWebSocketCallbacks() {
    _webSocketService.onAuthSuccess = (data) {
      print('[INFO] 認証成功: ${data['userId']}');
    };

    _webSocketService.onConnectionEstablished = (data) {
      _isConnected = true;
      _isConnecting = false;
      _connectionError = null;
      notifyListeners();
    };

    _webSocketService.onMatchingStarted = (data) {
      _isMatching = true;
      _matchingId = data['matchingId'];
      notifyListeners();
    };

    _webSocketService.onMatchingStatus = (data) {
      _queuePosition = data['queuePosition'] ?? 0;
      _estimatedWaitTime = data['estimatedWaitTime'] ?? 0;
      notifyListeners();
    };

    _webSocketService.onMatchFound = (data) {
      _isMatching = false;
      _isInBattle = true;
      _battleId = data['battleId'];
      _opponent = data['opponent'];
      _playerNumber = data['playerNumber'];
      _isReady = false;
      _isOpponentReady = false;
      _selectedHand = null;
      _isHandSubmitted = false;
      notifyListeners();
    };

    _webSocketService.onBattleReadyStatus = (data) {
      if (data['player1Ready'] != null && data['player2Ready'] != null) {
        _isReady = data['player1Ready'] == true && _playerNumber == 1 ||
                   data['player2Ready'] == true && _playerNumber == 2;
        _isOpponentReady = data['player1Ready'] == true && _playerNumber == 2 ||
                           data['player2Ready'] == true && _playerNumber == 1;
      }
      notifyListeners();
    };

    _webSocketService.onBattleStart = (data) {
      // 対戦開始時の処理
      notifyListeners();
    };

    _webSocketService.onHandSubmitted = (data) {
      _isHandSubmitted = true;
      notifyListeners();
    };

    _webSocketService.onBattleResult = (data) {
      final result = data['result'];
      print('[DEBUG] バトル結果受信: $result');
      
      // 引き分けかどうかを判定
      final isDraw = result['isDraw'] == true || result['winner'] == 3;
      
      if (isDraw) {
        // 引き分けの場合は特別な処理
        print('[DEBUG] 引き分けを検出: $result');
        _handleDraw(result);
      } else {
        // 勝敗が決まった場合は通常の結果表示
        print('[DEBUG] 勝敗決定: $result');
        _battleResult = result;
        _isInBattle = false;
        _isDraw = false;
        _showingDrawResult = false;
        notifyListeners();
      }
    };

    _webSocketService.onBattleDraw = (data) {
      // 引き分け時の処理（明示的な引き分けメッセージ）
      print('[DEBUG] 引き分けメッセージ受信: $data');
      final result = data['result'];
      _handleDraw(result);
    };

    _webSocketService.onHandsReset = (data) {
      print('[DEBUG] 手リセット完了');
      _isHandSubmitted = false;
      _selectedHand = null;
      // 引き分け結果表示を終了して次のラウンドに進む
      _goToNextRound();
      notifyListeners();
    };

    _webSocketService.onBattleQuitConfirmed = (data) {
      _isInBattle = false;
      _battleId = null;
      _opponent = null;
      _isReady = false;
      _isOpponentReady = false;
      _selectedHand = null;
      _isHandSubmitted = false;
      _showingDrawResult = false;
      _drawResultTimer?.cancel();
      notifyListeners();
    };

    _webSocketService.onOpponentQuit = (data) {
      _isInBattle = false;
      _battleId = null;
      _opponent = null;
      _isReady = false;
      _isOpponentReady = false;
      _selectedHand = null;
      _isHandSubmitted = false;
      _showingDrawResult = false;
      _drawResultTimer?.cancel();
      notifyListeners();
    };

    _webSocketService.onError = (data) {
      _connectionError = '${data['code']}: ${data['message']}';
      notifyListeners();
    };

    _webSocketService.onDisconnected = () {
      _isConnected = false;
      _isConnecting = false;
      _isMatching = false;
      _isInBattle = false;
      _showingDrawResult = false;
      _drawResultTimer?.cancel();
      notifyListeners();
    };

    _webSocketService.onConnectionFailed = () {
      _isConnecting = false;
      _connectionError = '接続に失敗しました';
      notifyListeners();
    };
  }

  /// 引き分け時の処理
  void _handleDraw(Map<String, dynamic> result) {
    print('[DEBUG] 引き分け処理開始: $result');
    
    // 既存のタイマーをクリア
    _drawResultTimer?.cancel();
    
    _battleResult = result;
    _isDraw = true;
    _drawCount = result['drawCount'] ?? 0;
    _isHandSubmitted = false;
    _selectedHand = null;
    _showingDrawResult = true;
    
    print('[DEBUG] 引き分け状態設定完了: drawCount=$_drawCount, showingDrawResult=$_showingDrawResult');
    
    // 3秒後に結果表示を終了して次のラウンドに進む
    _drawResultTimer = Timer(const Duration(seconds: 3), () {
      print('[DEBUG] 引き分け表示タイマー完了、次のラウンドに進む');
      _goToNextRound();
    });
    
    notifyListeners();
  }
  
  /// 次のラウンドに進む
  void _goToNextRound() {
    print('[DEBUG] 次のラウンドに進む処理開始');
    
    // 結果表示を終了
    _showingDrawResult = false;
    _battleResult = null;
    
    // バトル状態に戻す
    _isInBattle = true;
    _isReady = false;
    _isOpponentReady = false;
    
    // タイマーをクリア
    _drawResultTimer?.cancel();
    _drawResultTimer = null;
    
    print('[DEBUG] 次のラウンド状態設定完了: isInBattle=$_isInBattle, showingDrawResult=$_showingDrawResult');
    
    notifyListeners();
  }
  
  /// 手動で次のラウンドに進む
  void goToNextRound() {
    _goToNextRound();
  }

  // =====================
  // デバッグ用テストケース
  // =====================

  /// デバッグ用：引き分けシミュレーション
  void debugSimulateDraw() {
    print('[DEBUG] 引き分けシミュレーション開始');
    
    // 引き分け結果をシミュレート
    final mockDrawResult = {
      'player1': {
        'userId': 'test_user_1',
        'hand': 'rock',
        'result': 'draw'
      },
      'player2': {
        'userId': 'test_user_2', 
        'hand': 'rock',
        'result': 'draw'
      },
      'winner': 3,
      'isDraw': true,
      'drawCount': 1,
      'isFinished': false
    };
    
    _handleDraw(mockDrawResult);
  }

  /// デバッグ用：勝敗シミュレーション
  void debugSimulateWin() {
    print('[DEBUG] 勝利シミュレーション開始');
    
    // 勝利結果をシミュレート
    final mockWinResult = {
      'player1': {
        'userId': 'test_user_1',
        'hand': 'rock',
        'result': 'win'
      },
      'player2': {
        'userId': 'test_user_2',
        'hand': 'scissors', 
        'result': 'lose'
      },
      'winner': 1,
      'isDraw': false,
      'drawCount': 0,
      'isFinished': true
    };
    
    _battleResult = mockWinResult;
    _isInBattle = false;
    _isDraw = false;
    notifyListeners();
  }

  /// デバッグ用：敗北シミュレーション
  void debugSimulateLose() {
    print('[DEBUG] 敗北シミュレーション開始');
    
    // 敗北結果をシミュレート
    final mockLoseResult = {
      'player1': {
        'userId': 'test_user_2',
        'hand': 'paper',
        'result': 'win'
      },
      'player2': {
        'userId': 'test_user_1',
        'hand': 'rock',
        'result': 'lose'
      },
      'winner': 1,
      'isDraw': false,
      'drawCount': 0,
      'isFinished': true
    };
    
    _battleResult = mockLoseResult;
    _isInBattle = false;
    _isDraw = false;
    notifyListeners();
  }

  /// デバッグ用：連続引き分けシミュレーション
  void debugSimulateMultipleDraws() {
    print('[DEBUG] 連続引き分けシミュレーション開始');
    
    // 1回目の引き分け
    final mockDraw1 = {
      'player1': {
        'userId': 'test_user_1',
        'hand': 'rock',
        'result': 'draw'
      },
      'player2': {
        'userId': 'test_user_2',
        'hand': 'rock',
        'result': 'draw'
      },
      'winner': 3,
      'isDraw': true,
      'drawCount': 1,
      'isFinished': false
    };
    
    _handleDraw(mockDraw1);
    
    // 3秒後に2回目の引き分けをシミュレート
    Timer(const Duration(seconds: 4), () {
      final mockDraw2 = {
        'player1': {
          'userId': 'test_user_1',
          'hand': 'paper',
          'result': 'draw'
        },
        'player2': {
          'userId': 'test_user_2',
          'hand': 'paper',
          'result': 'draw'
        },
        'winner': 3,
        'isDraw': true,
        'drawCount': 2,
        'isFinished': false
      };
      
      _handleDraw(mockDraw2);
    });
  }

  /// デバッグ用：状態リセット
  void debugResetState() {
    print('[DEBUG] 状態リセット実行');
    _resetState();
  }

  /// デバッグ用：現在の状態をログ出力
  void debugLogCurrentState() {
    print('[DEBUG] === 現在の状態 ===');
    print('接続状態: $_isConnected');
    print('マッチング中: $_isMatching');
    print('バトル中: $_isInBattle');
    print('引き分け: $_isDraw');
    print('引き分け回数: $_drawCount');
    print('引き分け結果表示中: $_showingDrawResult');
    print('バトル結果: $_battleResult');
    print('選択された手: $_selectedHand');
    print('手送信済み: $_isHandSubmitted');
    print('準備完了: $_isReady');
    print('相手準備完了: $_isOpponentReady');
    print('========================');
  }

  /// WebSocket接続を開始
  Future<bool> connect() async {
    try {
      _isConnecting = true;
      _connectionError = null;
      notifyListeners();

      // JWTトークンを取得
      final token = await _authService.getToken();
      if (token == null) {
        _connectionError = 'JWTトークンが取得できません';
        _isConnecting = false;
        notifyListeners();
        return false;
      }

      // ユーザー情報を取得
      final userData = await _authService.getUserData();
      if (userData == null) {
        _connectionError = 'ユーザー情報が取得できません';
        _isConnecting = false;
        notifyListeners();
        return false;
      }

      final userId = userData['user_id'];
      if (userId == null) {
        _connectionError = 'ユーザーIDが取得できません';
        _isConnecting = false;
        notifyListeners();
        return false;
      }

      // WebSocket接続
      final success = await _webSocketService.connect(userId, token);
      if (!success) {
        _connectionError = 'WebSocket接続に失敗しました';
        _isConnecting = false;
        notifyListeners();
        return false;
      }

      return true;

    } catch (e) {
      _connectionError = '接続エラー: $e';
      _isConnecting = false;
      notifyListeners();
      return false;
    }
  }

  /// マッチング開始
  void startMatching() {
    if (!_isConnected) return;
    
    _webSocketService.startMatching();
  }

  /// マッチングキャンセル
  void cancelMatching() {
    if (!_isConnected || !_isMatching) return;
    
    // WebSocketサービスにマッチングキャンセルを送信
    _webSocketService.cancelMatching();
    
    // マッチング状態をリセット
    _isMatching = false;
    _matchingId = null;
    _queuePosition = 0;
    _estimatedWaitTime = 0;
    
    notifyListeners();
  }

  /// 準備完了
  void setReady() {
    if (!_isConnected || _battleId == null) return;
    
    _webSocketService.setReady(_battleId!);
  }

  /// 手を選択
  void selectHand(String hand) {
    if (_isHandSubmitted) return;
    
    _selectedHand = hand;
    notifyListeners();
  }

  /// 手を送信
  void submitHand() {
    if (!_isConnected || _battleId == null || _selectedHand == null || _isHandSubmitted) return;
    
    _webSocketService.submitHand(_battleId!, _selectedHand!);
  }

  /// 手をリセット（引き分け時）
  void resetHands() {
    if (!_isConnected || _battleId == null) return;
    
    _webSocketService.resetHands(_battleId!);
  }

  /// 対戦辞退
  void quitBattle() {
    if (!_isConnected || _battleId == null) return;
    
    _webSocketService.quitBattle(_battleId!);
  }

  /// 再接続
  Future<bool> reconnect() async {
    return await connect();
  }

  /// 接続切断
  void disconnect() {
    _webSocketService.disconnect();
    _resetState();
  }

  /// 状態をリセット
  void _resetState() {
    _isConnected = false;
    _isConnecting = false;
    _connectionError = null;
    _isMatching = false;
    _matchingId = null;
    _queuePosition = 0;
    _estimatedWaitTime = 0;
    _isInBattle = false;
    _battleId = null;
    _opponent = null;
    _playerNumber = 0;
    _selectedHand = null;
    _isHandSubmitted = false;
    _isOpponentReady = false;
    _isReady = false;
    _battleResult = null;
    _isDraw = false;
    _drawCount = 0;
    _showingDrawResult = false;
    _drawResultTimer?.cancel();
    _drawResultTimer = null;
    notifyListeners();
  }

  /// 対戦結果をクリア
  void clearBattleResult() {
    _battleResult = null;
    _isInBattle = false;
    _isDraw = false;
    _drawCount = 0;
    _showingDrawResult = false;
    _drawResultTimer?.cancel();
    _drawResultTimer = null;
    notifyListeners();
  }

  @override
  void dispose() {
    _drawResultTimer?.cancel();
    _webSocketService.disconnect();
    super.dispose();
  }
}
