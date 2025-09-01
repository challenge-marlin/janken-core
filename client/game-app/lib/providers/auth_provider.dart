import 'package:flutter/material.dart';
import '../services/auth_service.dart';

/// 認証状態を管理するプロバイダークラス
/// 
/// このクラスは以下の認証状態を管理します：
/// - ローディング状態
/// - 認証状態（ログイン済み/未ログイン）
/// - 現在のユーザー情報
/// - エラー状態
class AuthProvider extends ChangeNotifier {
  final AuthService _authService = AuthService();
  
  bool _isLoading = false;
  bool _isAuthenticated = false;
  Map<String, dynamic>? _currentUser;
  String? _error;

  // ゲッター
  bool get isLoading => _isLoading;
  bool get isAuthenticated => _isAuthenticated;
  Map<String, dynamic>? get currentUser => _currentUser;
  String? get error => _error;

  /// ローディング状態を設定
  void setLoading(bool loading) {
    _isLoading = loading;
    notifyListeners();
  }

  /// エラー状態を設定
  void setError(String? error) {
    _error = error;
    notifyListeners();
  }

  /// ログイン処理
  /// 
  /// 既存のサーバーAPI（/api/auth/db-login）を使用してログインを実行
  /// テストユーザー（test1@example.com〜test5@example.com、password123）に対応
  Future<bool> login(String email, String password) async {
    try {
      setLoading(true);
      setError(null);
      
      final result = await _authService.login(email, password);
      
      if (result['success'] == true) {
        // ログイン成功
        _currentUser = result['user'];
        _isAuthenticated = true;
        notifyListeners();
        return true;
      } else {
        // ログイン失敗
        setError(result['message'] ?? 'ログインに失敗しました');
        return false;
      }
    } catch (e) {
      setError('ログインに失敗しました: $e');
      return false;
    } finally {
      setLoading(false);
    }
  }

  /// ログアウト処理
  Future<void> logout() async {
    try {
      await _authService.logout();
      _isAuthenticated = false;
      _currentUser = null;
      _error = null;
      notifyListeners();
    } catch (e) {
      print('ログアウトエラー: $e');
      // エラーが発生してもローカル状態はクリア
      _isAuthenticated = false;
      _currentUser = null;
      _error = null;
      notifyListeners();
    }
  }

  /// ユーザー登録処理
  Future<bool> register(String email, String password, String name) async {
    try {
      setLoading(true);
      setError(null);
      
      // 現在の実装では、ログインと同じ処理を行う
      // 将来的に専用の登録APIを実装する予定
      final result = await _authService.login(email, password);
      
      if (result['success'] == true) {
        // 登録成功（ログイン処理で代替）
        _currentUser = result['user'];
        _isAuthenticated = true;
        notifyListeners();
        return true;
      } else {
        // 登録失敗
        setError(result['message'] ?? '登録に失敗しました');
        return false;
      }
    } catch (e) {
      setError('登録に失敗しました: $e');
      return false;
    } finally {
      setLoading(false);
    }
  }

  /// 初期化処理
  /// 
  /// アプリ起動時に認証状態を復元します
  Future<void> initialize() async {
    try {
      setLoading(true);
      
      // 保存された認証状態を復元
      final authState = await _authService.restoreAuthState();
      
      if (authState != null && authState['success'] == true) {
        // 有効な認証状態を復元
        _currentUser = authState['user'];
        _isAuthenticated = true;
      } else {
        // 認証状態なし
        _isAuthenticated = false;
        _currentUser = null;
      }
      
    } catch (e) {
      setError('初期化に失敗しました: $e');
      _isAuthenticated = false;
      _currentUser = null;
    } finally {
      setLoading(false);
    }
  }
}
