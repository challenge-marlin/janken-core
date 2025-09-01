import 'dart:convert';
import 'dart:async';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:web_socket_channel/status.dart' as status;

/// バトル画面用WebSocketサービス
/// 
/// このサービスは以下の機能を提供します：
/// - WebSocket接続管理
/// - JWT認証
/// - マッチング・対戦機能
/// - リアルタイム通信
class BattleWebSocketService {
  WebSocketChannel? _channel;
  String? _userId;
  String? _jwtToken;
  bool _isConnected = false;
  int _reconnectAttempts = 0;
  static const int _maxReconnectAttempts = 3;
  static const int _reconnectDelay = 2000; // 2秒
  
  Timer? _reconnectTimer;
  Timer? _heartbeatTimer;
  DateTime? _lastPongTime;
  
  // コールバック関数
  Function(Map<String, dynamic>)? onAuthSuccess;
  Function(Map<String, dynamic>)? onConnectionEstablished;
  Function(Map<String, dynamic>)? onMatchingStarted;
  Function(Map<String, dynamic>)? onMatchingStatus;
  Function(Map<String, dynamic>)? onMatchFound;
  Function(Map<String, dynamic>)? onBattleReadyStatus;
  Function(Map<String, dynamic>)? onBattleStart;
  Function(Map<String, dynamic>)? onHandSubmitted;
  Function(Map<String, dynamic>)? onBattleResult;
  Function(Map<String, dynamic>)? onBattleDraw;
  Function(Map<String, dynamic>)? onHandsReset;
  Function(Map<String, dynamic>)? onBattleQuitConfirmed;
  Function(Map<String, dynamic>)? onOpponentQuit;
  Function(Map<String, dynamic>)? onError;
  Function()? onDisconnected;
  Function()? onConnectionFailed;

  // ゲッター
  bool get isConnected => _isConnected;
  String? get userId => _userId;

  /// WebSocket接続を確立
  Future<bool> connect(String userId, String jwtToken) async {
    try {
      _userId = userId;
      _jwtToken = jwtToken;
      
      final wsUrl = 'ws://192.168.0.150:3000/api/battle/ws/$userId';
      print('[INFO] WebSocket接続試行: $wsUrl');
      
      _channel = WebSocketChannel.connect(Uri.parse(wsUrl));
      
      // 接続確立を待機
      await _channel!.ready;
      _isConnected = true;
      print('[INFO] WebSocket接続確立');
      
      // 接続直後に認証メッセージを送信
      await _sendAuthMessage();
      
      // メッセージリスナーを設定
      _setupMessageListener();
      
      // ハートビートを開始
      _startHeartbeat();
      
      return true;
      
    } catch (e) {
      print('[ERROR] WebSocket接続エラー: $e');
      _isConnected = false;
      return false;
    }
  }

  /// 認証メッセージを送信（接続直後必須）
  Future<void> _sendAuthMessage() async {
    if (_channel == null || !_isConnected) return;
    
    final message = {
      'type': 'auth',
      'data': {
        'token': _jwtToken,
      },
      'timestamp': DateTime.now().toIso8601String(),
      'messageId': _generateMessageId(),
    };
    
    _channel!.sink.add(jsonEncode(message));
    print('[INFO] 認証メッセージ送信: $message');
  }

  /// メッセージリスナーを設定
  void _setupMessageListener() {
    _channel?.stream.listen(
      (data) {
        try {
          final message = jsonDecode(data);
          _handleMessage(message);
        } catch (e) {
          print('[ERROR] メッセージ解析エラー: $e');
        }
      },
      onError: (error) {
        print('[ERROR] WebSocketエラー: $error');
        _handleDisconnected();
      },
      onDone: () {
        print('[INFO] WebSocket接続が切断されました');
        _handleDisconnected();
      },
    );
  }

  /// メッセージハンドラー
  void _handleMessage(Map<String, dynamic> message) {
    final type = message['type'];
    final data = message['data'];
    final success = message['success'];
    
    print('[INFO] 受信: $type $message');
    
    switch (type) {
      case 'auth_success':
        print('[SUCCESS] 認証成功: ${data['userId']}');
        onAuthSuccess?.call(data);
        break;
        
      case 'connection_established':
        print('[SUCCESS] 接続確立: ${data['sessionId']}');
        onConnectionEstablished?.call(data);
        break;
        
      case 'matching_started':
        print('[SUCCESS] マッチング開始: ${data['matchingId']}');
        onMatchingStarted?.call(data);
        break;
        
      case 'matching_status':
        print('[INFO] マッチング状況: $data');
        onMatchingStatus?.call(data);
        break;
        
      case 'match_found':
        print('[SUCCESS] マッチング成立: ${data['battleId']}');
        onMatchFound?.call(data);
        break;
        
      case 'battle_ready_status':
        print('[INFO] 準備状況: $data');
        onBattleReadyStatus?.call(data);
        break;
        
      case 'battle_start':
        print('[SUCCESS] 対戦開始');
        onBattleStart?.call(data);
        break;
        
      case 'hand_submitted':
        print('[INFO] 手送信完了');
        onHandSubmitted?.call(data);
        break;
        
      case 'battle_result':
        print('[SUCCESS] 対戦結果: ${data['result']}');
        onBattleResult?.call(data);
        break;
        
      case 'battle_draw':
        print('[INFO] 引き分け');
        onBattleDraw?.call(data);
        break;
        
      case 'hands_reset':
        print('[INFO] 手リセット完了');
        onHandsReset?.call(data);
        break;
        
      case 'battle_quit_confirmed':
        print('[INFO] 対戦辞退確認');
        onBattleQuitConfirmed?.call(data);
        break;
        
      case 'opponent_quit':
        print('[INFO] 相手辞退通知');
        onOpponentQuit?.call(data);
        break;
        
      case 'pong':
        final latency = DateTime.now().difference(_lastPongTime ?? DateTime.now()).inMilliseconds;
        print('[INFO] ハートビート応答: ${latency.abs()}ms');
        break;
        
      case 'error':
        print('[ERROR] エラー: ${data['code']} - ${data['message']}');
        onError?.call(data);
        break;
        
      default:
        print('[WARN] 未対応のメッセージタイプ: $type');
    }
  }

  /// マッチング開始
  void startMatching() {
    _sendMessage('matching_start', {
      'userId': _userId,
    });
  }

  /// 準備完了
  void setReady(String battleId) {
    _sendMessage('battle_ready', {
      'battleId': battleId,
      'userId': _userId,
    });
  }

  /// 手の送信
  void submitHand(String battleId, String hand) {
    _sendMessage('submit_hand', {
      'battleId': battleId,
      'userId': _userId,
      'hand': hand,
    });
  }

  /// 手のリセット
  void resetHands(String battleId) {
    _sendMessage('reset_hands', {
      'battleId': battleId,
    });
  }

  /// 対戦辞退
  void quitBattle(String battleId) {
    _sendMessage('battle_quit', {
      'battleId': battleId,
      'userId': _userId,
      'reason': 'user_action',
    });
  }

  /// メッセージ送信
  void _sendMessage(String type, Map<String, dynamic> data) {
    if (_channel == null || !_isConnected) {
      print('[ERROR] WebSocketが接続されていません');
      return;
    }
    
    final message = {
      'type': type,
      'data': data,
      'timestamp': DateTime.now().toIso8601String(),
      'messageId': _generateMessageId(),
    };
    
    _channel!.sink.add(jsonEncode(message));
    print('[INFO] 送信: $type $message');
  }

  /// ハートビート開始
  void _startHeartbeat() {
    _heartbeatTimer?.cancel();
    _heartbeatTimer = Timer.periodic(const Duration(seconds: 30), (timer) {
      if (_isConnected) {
        _lastPongTime = DateTime.now();
        _sendMessage('ping', {});
      }
    });
  }

  /// ハートビート停止
  void _stopHeartbeat() {
    _heartbeatTimer?.cancel();
    _heartbeatTimer = null;
  }

  /// 切断処理
  void _handleDisconnected() {
    _isConnected = false;
    _stopHeartbeat();
    
    if (_reconnectAttempts < _maxReconnectAttempts) {
      _reconnectAttempts++;
      print('[INFO] ${_reconnectDelay}ms後に再接続を試行します (${_reconnectAttempts}/${_maxReconnectAttempts})');
      
      _reconnectTimer = Timer(Duration(milliseconds: _reconnectDelay), () async {
        try {
          if (_userId != null && _jwtToken != null) {
            final success = await connect(_userId!, _jwtToken!);
            if (success) {
              print('[SUCCESS] 再接続に成功しました');
              _reconnectAttempts = 0;
            } else {
              _handleDisconnected(); // 再帰的に再試行
            }
          }
        } catch (error) {
          print('[ERROR] 再接続に失敗しました: $error');
          _handleDisconnected(); // 再帰的に再試行
        }
      });
    } else {
      print('[ERROR] 再接続試行回数を超えました');
      _onConnectionFailed();
    }
    
    onDisconnected?.call();
  }

  /// 接続失敗処理
  void _onConnectionFailed() {
    print('[ERROR] WebSocket接続に失敗しました');
    onConnectionFailed?.call();
  }

  /// 接続切断
  void disconnect() {
    // タイマーをクリア
    _reconnectTimer?.cancel();
    _reconnectTimer = null;
    _stopHeartbeat();
    
    if (_channel != null && _isConnected) {
      _sendMessage('disconnect', {
        'reason': 'user_action',
      });
      _channel!.sink.close(status.goingAway, 'Normal closure');
    }
    
    _channel = null;
    _isConnected = false;
    _reconnectAttempts = 0;
  }

  /// メッセージID生成
  String _generateMessageId() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replaceAllMapped(
      RegExp(r'[xy]'),
      (match) {
        final r = (DateTime.now().millisecondsSinceEpoch * 16) % 16;
        final v = match.group(0) == 'x' ? r : (r & 0x3 | 0x8);
        return v.toRadixString(16);
      },
    );
  }
}
