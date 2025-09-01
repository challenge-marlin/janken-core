import 'package:flutter/material.dart';

/// アプリ全体で使用する定数クラス
/// 
/// 色、サイズ、文字列などの定数を一元管理します
class AppConstants {
  // プライベートコンストラクタ（インスタンス化を防ぐ）
  AppConstants._();
  
  // アプリ情報
  static const String appName = '神の手じゃんけん';
  static const String appVersion = '1.0.0';
  
  // 画面サイズ
  static const double screenPadding = 16.0;
  static const double buttonHeight = 56.0;
  static const double cardRadius = 12.0;
  
  // フォントサイズ
  static const double titleFontSize = 24.0;
  static const double subtitleFontSize = 18.0;
  static const double bodyFontSize = 16.0;
  static const double captionFontSize = 14.0;
  
  // アニメーション時間
  static const Duration shortAnimation = Duration(milliseconds: 200);
  static const Duration mediumAnimation = Duration(milliseconds: 300);
  static const Duration longAnimation = Duration(milliseconds: 500);
}

/// アプリで使用する色の定数クラス
/// 
/// テーマカラーやUI要素の色を一元管理します
class AppColors {
  // プライベートコンストラクタ（インスタンス化を防ぐ）
  AppColors._();
  
  // 基本色
  static const Color primary = Color(0xFF2196F3);
  static const Color primaryDark = Color(0xFF1976D2);
  static const Color primaryLight = Color(0xFFBBDEFB);
  
  // 背景色
  static const Color background = Color(0xFF121212);
  static const Color surface = Color(0xFF1E1E1E);
  static const Color card = Color(0xFF2D2D2D);
  
  // テキスト色
  static const Color textPrimary = Color(0xFFFFFFFF);
  static const Color textSecondary = Color(0xFFB3B3B3);
  static const Color textDisabled = Color(0xFF666666);
  
  // 状態色
  static const Color success = Color(0xFF4CAF50);
  static const Color warning = Color(0xFFFF9800);
  static const Color error = Color(0xFFF44336);
  static const Color info = Color(0xFF2196F3);
  
  // じゃんけん関連色
  static const Color rock = Color(0xFF795548);      // グー
  static const Color scissors = Color(0xFF607D8B);  // チョキ
  static const Color paper = Color(0xFF9E9E9E);    // パー
  
  // ランク色
  static const Color rankBronze = Color(0xFFCD7F32);
  static const Color rankSilver = Color(0xFFC0C0C0);
  static const Color rankGold = Color(0xFFFFD700);
  static const Color rankPlatinum = Color(0xFFE5E4E2);
  static const Color rankDiamond = Color(0xFFB9F2FF);
}

/// アプリで使用する文字列の定数クラス
/// 
/// メッセージやラベルなどの文字列を一元管理します
class AppStrings {
  // プライベートコンストラクタ（インスタンス化を防ぐ）
  AppStrings._();
  
  // 共通
  static const String loading = '読み込み中...';
  static const String error = 'エラー';
  static const String success = '成功';
  static const String cancel = 'キャンセル';
  static const String confirm = '確認';
  static const String back = '戻る';
  static const String next = '次へ';
  static const String save = '保存';
  static const String delete = '削除';
  static const String edit = '編集';
  
  // 認証
  static const String login = 'ログイン';
  static const String register = '登録';
  static const String logout = 'ログアウト';
  static const String email = 'メールアドレス';
  static const String password = 'パスワード';
  static const String forgotPassword = 'パスワードを忘れた方';
  
  // ゲーム
  static const String rock = 'グー';
  static const String scissors = 'チョキ';
  static const String paper = 'パー';
  static const String win = '勝利';
  static const String lose = '敗北';
  static const String draw = '引き分け';
  static const String battle = 'バトル';
  static const String lobby = 'ロビー';
  
  // エラーメッセージ
  static const String networkError = 'ネットワークエラーが発生しました';
  static const String serverError = 'サーバーエラーが発生しました';
  static const String authError = '認証に失敗しました';
  static const String unknownError = '予期しないエラーが発生しました';
}
