import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import 'pages/auth/login_page.dart';
import 'pages/lobby/lobby_page.dart';
import 'pages/battle/battle_page.dart';
import 'providers/auth_provider.dart';
import 'providers/battle_provider.dart';
import 'utils/constants.dart';

void main() {
  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (context) => AuthProvider()..initialize()),
        ChangeNotifierProvider(create: (context) => BattleProvider()),
      ],
      child: const JankenGameApp(),
    ),
  );
}

/// 神の手じゃんけんゲームアプリのメインクラス
/// 
/// このアプリは以下の機能を提供します：
/// - ユーザー認証（ログイン・登録）
/// - ロビー画面（対戦相手検索・待機）
/// - じゃんけんバトル
/// - ランキング・統計表示
/// - 設定・プロフィール管理
class JankenGameApp extends StatelessWidget {
  const JankenGameApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: '神の手じゃんけん',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        fontFamily: 'M PLUS 1p',
        useMaterial3: true,
      ),
      home: Consumer<AuthProvider>(
        builder: (context, auth, child) {
          if (auth.isLoading) {
            return const Scaffold(
              body: Center(
                child: CircularProgressIndicator(),
              ),
            );
          }
          
          if (auth.isAuthenticated) {
            return const LobbyPage();
          }
          
          return const LoginPage();
        },
      ),
      routes: {
        '/login': (context) => const LoginPage(),
        '/lobby': (context) => const LobbyPage(),
        '/battle': (context) => const BattlePage(),
      },
    );
  }
}

/// 認証状態に基づいて適切な画面を表示するラッパー
/// 
/// 認証状態を監視し、以下の画面を表示します：
/// - 未認証: ログイン画面
/// - 認証済み: ロビー画面
class AuthWrapper extends StatelessWidget {
  const AuthWrapper({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer<AuthProvider>(
      builder: (context, auth, child) {
        if (auth.isLoading) {
          return const LoadingScreen();
        }
        
        if (auth.isAuthenticated) {
          return const LobbyPage();
        }
        
        return const LoginPage();
      },
    );
  }
}

/// ローディング画面
/// 
/// アプリ起動時や認証処理中の表示画面
class LoadingScreen extends StatelessWidget {
  const LoadingScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Image.asset(
              'assets/images/logo/logo.png',
              width: 200,
              height: 200,
              errorBuilder: (context, error, stackTrace) {
                return const Icon(
                  Icons.games,
                  size: 200,
                  color: Colors.blue,
                );
              },
            ),
            const SizedBox(height: 32),
            const CircularProgressIndicator(
              valueColor: AlwaysStoppedAnimation<Color>(Colors.blue),
            ),
            const SizedBox(height: 16),
            const Text(
              '神の手じゃんけん',
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: Colors.white,
              ),
            ),
            const SizedBox(height: 8),
            const Text(
              '読み込み中...',
              style: TextStyle(
                fontSize: 16,
                color: Colors.grey,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
