import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

/// 認証サービス
/// 
/// このサービスは以下の機能を提供します：
/// - サーバーAPIとの通信
/// - JWTトークンの管理
/// - ユーザー情報の取得・保存
class AuthService {
  static const String _baseUrl = 'http://192.168.0.150:3000'; // 開発環境のサーバーURL
  
  /// ログイン処理
  /// 
  /// 既存のサーバーAPI（/api/auth/db-login）を使用してログインを実行
  /// テストユーザー（test1@example.com〜test5@example.com、password123）に対応
  Future<Map<String, dynamic>> login(String email, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/api/auth/db-login'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'email': email,
          'password': password,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        
        if (data['success'] == true) {
          // ログイン成功
          final userData = data['data']['user'];
          final token = data['data']['token'];
          
          // JWTトークンを保存
          await _saveToken(token);
          
          // ユーザー情報を保存
          await _saveUserData(userData);
          
          return {
            'success': true,
            'user': userData,
            'token': token,
          };
        } else {
          // ログイン失敗
          return {
            'success': false,
            'message': data['message'] ?? 'ログインに失敗しました',
          };
        }
      } else {
        // HTTPエラー
        return {
          'success': false,
          'message': 'サーバーエラーが発生しました (${response.statusCode})',
        };
      }
    } catch (e) {
      // ネットワークエラー
      return {
        'success': false,
        'message': 'ネットワークエラーが発生しました: $e',
      };
    }
  }

  /// ログアウト処理
  Future<void> logout() async {
    try {
      // ローカルストレージからトークンとユーザー情報を削除
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove('jwt_token');
      await prefs.remove('user_data');
    } catch (e) {
      print('ログアウトエラー: $e');
    }
  }

  /// 保存されたトークンを取得
  Future<String?> getToken() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      return prefs.getString('jwt_token');
    } catch (e) {
      print('トークン取得エラー: $e');
      return null;
    }
  }

  /// 保存されたユーザー情報を取得
  Future<Map<String, dynamic>?> getUserData() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final userDataString = prefs.getString('user_data');
      if (userDataString != null) {
        return jsonDecode(userDataString);
      }
      return null;
    } catch (e) {
      print('ユーザー情報取得エラー: $e');
      return null;
    }
  }

  /// JWTトークンを保存
  Future<void> _saveToken(String token) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('jwt_token', token);
    } catch (e) {
      print('トークン保存エラー: $e');
    }
  }

  /// ユーザー情報を保存
  Future<void> _saveUserData(Map<String, dynamic> userData) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('user_data', jsonEncode(userData));
    } catch (e) {
      print('ユーザー情報保存エラー: $e');
    }
  }

  /// トークンの有効性を検証
  Future<bool> validateToken(String token) async {
    try {
      final response = await http.get(
        Uri.parse('$_baseUrl/api/auth/verify-token'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );

      return response.statusCode == 200;
    } catch (e) {
      print('トークン検証エラー: $e');
      return false;
    }
  }

  /// 保存された認証状態を復元
  Future<Map<String, dynamic>?> restoreAuthState() async {
    try {
      final token = await getToken();
      if (token == null) return null;

      // トークンの有効性を検証
      final isValid = await validateToken(token);
      if (!isValid) {
        // 無効なトークンは削除
        await logout();
        return null;
      }

      // ユーザー情報を取得
      final userData = await getUserData();
      if (userData == null) return null;

      return {
        'success': true,
        'user': userData,
        'token': token,
      };
    } catch (e) {
      print('認証状態復元エラー: $e');
      return null;
    }
  }
}
