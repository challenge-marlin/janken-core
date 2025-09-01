import 'package:flutter/material.dart';
import '../services/battle_websocket_service.dart';
import '../services/auth_service.dart';

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
      _battleResult = data['result'];
      _isInBattle = false;
      _isDraw = false;
      notifyListeners();
    };

    _webSocketService.onBattleDraw = (data) {
      _battleResult = data['result'];
      _isDraw = true;
      _drawCount = data['result']['drawCount'] ?? 0;
      _isHandSubmitted = false;
      _selectedHand = null;
      notifyListeners();
    };

    _webSocketService.onHandsReset = (data) {
      _isHandSubmitted = false;
      _selectedHand = null;
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
      notifyListeners();
    };

    _webSocketService.onConnectionFailed = () {
      _isConnecting = false;
      _connectionError = '接続に失敗しました';
      notifyListeners();
    };
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
    notifyListeners();
  }

  /// 対戦結果をクリア
  void clearBattleResult() {
    _battleResult = null;
    _isDraw = false;
    _drawCount = 0;
    notifyListeners();
  }

  @override
  void dispose() {
    _webSocketService.disconnect();
    super.dispose();
  }
}
