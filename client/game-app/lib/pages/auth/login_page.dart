import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';
import '../../utils/constants.dart';
import '../../widgets/common/custom_button.dart';
import '../../widgets/common/custom_text_field.dart';

/// ログイン画面
/// 
/// この画面は以下の機能を提供します：
/// - メールアドレス・パスワード入力
/// - テストユーザー情報の表示
/// - ログイン処理
/// - ユーザー登録画面への遷移
/// - パスワードリセット画面への遷移
class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _isPasswordVisible = false;

  @override
  void initState() {
    super.initState();
    // テストユーザーの情報を初期値として設定
    _emailController.text = 'test1@example.com';
    _passwordController.text = 'password123';
  }

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  /// ログイン処理を実行
  Future<void> _handleLogin() async {
    if (_formKey.currentState!.validate()) {
      final authProvider = context.read<AuthProvider>();
      final success = await authProvider.login(
        _emailController.text.trim(),
        _passwordController.text,
      );
      
      if (!success && mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(authProvider.error ?? 'ログインに失敗しました'),
            backgroundColor: AppColors.error,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          image: DecorationImage(
            image: AssetImage('assets/images/backgrounds/background_login.png'),
            fit: BoxFit.cover,
          ),
        ),
        child: SafeArea(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(AppConstants.screenPadding),
            child: Form(
              key: _formKey,
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const SizedBox(height: 48),
                  
                  // ロゴ・タイトル
                  _buildHeader(),
                  const SizedBox(height: 48),
                  
                  // テストユーザー情報
                  _buildTestUserInfo(),
                  const SizedBox(height: 24),
                  
                  // ログインフォーム
                  _buildLoginForm(),
                  const SizedBox(height: 24),
                  
                  // ログインボタン
                  _buildLoginButton(),
                  const SizedBox(height: 16),
                  
                  // その他のオプション
                  _buildOptions(),
                  const SizedBox(height: 32),
                  
                  // 登録リンク
                  _buildRegisterLink(),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  /// ヘッダー部分（ロゴ・タイトル）を構築
  Widget _buildHeader() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.black.withOpacity(0.7),
        borderRadius: BorderRadius.circular(AppConstants.cardRadius),
      ),
      child: Column(
        children: [
          // ロゴ画像
          Image.asset(
            'assets/images/logo/logo.png',
            width: 120,
            height: 120,
            errorBuilder: (context, error, stackTrace) {
              return Container(
                width: 120,
                height: 120,
                decoration: BoxDecoration(
                  color: AppColors.primary,
                  borderRadius: BorderRadius.circular(60),
                ),
                child: const Icon(
                  Icons.games,
                  size: 60,
                  color: Colors.white,
                ),
              );
            },
          ),
          const SizedBox(height: 16),
          
          // アプリタイトル
          const Text(
            '神の手じゃんけん',
            style: TextStyle(
              fontSize: AppConstants.titleFontSize,
              fontWeight: FontWeight.bold,
              color: AppColors.textPrimary,
            ),
          ),
          const SizedBox(height: 8),
          
          // サブタイトル
          const Text(
            'ログインして対戦を開始',
            style: TextStyle(
              fontSize: AppConstants.bodyFontSize,
              color: AppColors.textSecondary,
            ),
          ),
        ],
      ),
    );
  }

  /// テストユーザー情報を構築
  Widget _buildTestUserInfo() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.black.withOpacity(0.8),
        borderRadius: BorderRadius.circular(AppConstants.cardRadius),
        border: Border.all(color: AppColors.primary.withOpacity(0.5)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                Icons.info_outline,
                color: AppColors.primary,
                size: 20,
              ),
              const SizedBox(width: 8),
              Text(
                'テストユーザー情報',
                style: TextStyle(
                  fontSize: AppConstants.subtitleFontSize,
                  fontWeight: FontWeight.bold,
                  color: AppColors.primary,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          
          // テストユーザー一覧
          _buildTestUserItem('テストユーザー1', 'test1@example.com', 'じゃんけんマスター'),
          _buildTestUserItem('テストユーザー2', 'test2@example.com', 'バトルクイーン'),
          _buildTestUserItem('テストユーザー3', 'test3@example.com', '勝負師'),
          _buildTestUserItem('テストユーザー4', 'test4@example.com', '新米戦士'),
          _buildTestUserItem('テストユーザー5', 'test5@example.com', '伝説のプレイヤー'),
          
          const SizedBox(height: 8),
          Text(
            'パスワード: password123（全ユーザー共通）',
            style: TextStyle(
              fontSize: AppConstants.captionFontSize,
              color: AppColors.textSecondary,
              fontStyle: FontStyle.italic,
            ),
          ),
        ],
      ),
    );
  }

  /// テストユーザー項目を構築
  Widget _buildTestUserItem(String name, String email, String nickname) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        children: [
          Text(
            '• $name: ',
            style: TextStyle(
              fontSize: AppConstants.captionFontSize,
              color: AppColors.textSecondary,
            ),
          ),
          Expanded(
            child: Text(
              '$email ($nickname)',
              style: TextStyle(
                fontSize: AppConstants.captionFontSize,
                color: AppColors.textPrimary,
                fontFamily: 'monospace',
              ),
            ),
          ),
        ],
      ),
    );
  }

  /// ログインフォームを構築
  Widget _buildLoginForm() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.black.withOpacity(0.8),
        borderRadius: BorderRadius.circular(AppConstants.cardRadius),
      ),
      child: Column(
        children: [
          // メールアドレス入力フィールド
          CustomTextField(
            controller: _emailController,
            labelText: AppStrings.email,
            hintText: 'example@email.com',
            keyboardType: TextInputType.emailAddress,
            validator: (value) {
              if (value == null || value.isEmpty) {
                return 'メールアドレスを入力してください';
              }
              if (!value.contains('@')) {
                return '有効なメールアドレスを入力してください';
              }
              return null;
            },
          ),
          const SizedBox(height: 16),
          
          // パスワード入力フィールド
          CustomTextField(
            controller: _passwordController,
            labelText: AppStrings.password,
            hintText: 'パスワードを入力',
            obscureText: !_isPasswordVisible,
            suffixIcon: IconButton(
              icon: Icon(
                _isPasswordVisible ? Icons.visibility : Icons.visibility_off,
                color: AppColors.textSecondary,
              ),
              onPressed: () {
                setState(() {
                  _isPasswordVisible = !_isPasswordVisible;
                });
              },
            ),
            validator: (value) {
              if (value == null || value.isEmpty) {
                return 'パスワードを入力してください';
              }
              if (value.length < 6) {
                return 'パスワードは6文字以上で入力してください';
              }
              return null;
            },
          ),
        ],
      ),
    );
  }

  /// ログインボタンを構築
  Widget _buildLoginButton() {
    return Consumer<AuthProvider>(
      builder: (context, auth, child) {
        return CustomButton(
          text: AppStrings.login,
          onPressed: auth.isLoading ? null : _handleLogin,
          isLoading: auth.isLoading,
          width: double.infinity,
          height: AppConstants.buttonHeight,
        );
      },
    );
  }

  /// オプション（パスワードリセットなど）を構築
  Widget _buildOptions() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.black.withOpacity(0.6),
        borderRadius: BorderRadius.circular(AppConstants.cardRadius),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          TextButton(
            onPressed: () {
              // TODO: パスワードリセット画面に遷移
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('パスワードリセット機能は準備中です'),
                ),
              );
            },
            child: const Text(
              AppStrings.forgotPassword,
              style: TextStyle(
                color: AppColors.primary,
                fontSize: AppConstants.captionFontSize,
              ),
            ),
          ),
        ],
      ),
    );
  }

  /// 登録リンクを構築
  Widget _buildRegisterLink() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.black.withOpacity(0.6),
        borderRadius: BorderRadius.circular(AppConstants.cardRadius),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Text(
            'アカウントをお持ちでない方は',
            style: TextStyle(
              color: AppColors.textSecondary,
              fontSize: AppConstants.captionFontSize,
            ),
          ),
          TextButton(
            onPressed: () {
              // TODO: 登録画面に遷移
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('登録画面は準備中です'),
                ),
              );
            },
            child: const Text(
              'こちら',
              style: TextStyle(
                color: AppColors.primary,
                fontSize: AppConstants.captionFontSize,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
