import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';
import '../../utils/constants.dart';
import '../../widgets/common/custom_button.dart';

/// ロビー画面
/// 
/// この画面は以下の機能を提供します：
/// - ユーザー情報表示
/// - ログアウト機能
/// - シンプルなロビー表示
/// - バトル画面への遷移
class LobbyPage extends StatefulWidget {
  const LobbyPage({super.key});

  @override
  State<LobbyPage> createState() => _LobbyPageState();
}

class _LobbyPageState extends State<LobbyPage> {
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
        child: Column(
          children: [
            // AppBar
            AppBar(
              title: const Text(
                AppStrings.lobby,
                style: TextStyle(
                  color: AppColors.textPrimary,
                  fontWeight: FontWeight.bold,
                ),
              ),
              backgroundColor: Colors.transparent,
              elevation: 0,
              actions: [
                IconButton(
                  icon: const Icon(Icons.logout, color: AppColors.textPrimary),
                  onPressed: _handleLogout,
                ),
              ],
            ),
            // メインコンテンツ
            Expanded(child: _buildBody()),
          ],
        ),
      ),
    );
  }

  /// メインコンテンツを構築
  Widget _buildBody() {
    return Consumer<AuthProvider>(
      builder: (context, auth, child) {
        if (auth.currentUser == null) {
          return const Center(
            child: Text(
              'ユーザー情報が取得できません',
              style: TextStyle(color: AppColors.textSecondary),
            ),
          );
        }

        return SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(AppConstants.screenPadding),
            child: Column(
              children: [
                const SizedBox(height: 20),
                
                // ユーザー情報カード
                _buildUserInfoCard(auth.currentUser!),
                const SizedBox(height: 24),
                
                // ウェルカムメッセージ
                _buildWelcomeMessage(),
                const SizedBox(height: 24),
                
                // アクションボタン
                _buildActionButtons(),
                const SizedBox(height: 24),
                
                // シンプルなメニュー
                _buildSimpleMenu(),
              ],
            ),
          ),
        );
      },
    );
  }

  /// ユーザー情報カードを構築
  Widget _buildUserInfoCard(Map<String, dynamic> user) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.black.withOpacity(0.8),
        borderRadius: BorderRadius.circular(AppConstants.cardRadius),
        border: Border.all(color: AppColors.primary.withOpacity(0.5)),
      ),
      child: Row(
        children: [
          // プロフィール画像
          CircleAvatar(
            radius: 40,
            backgroundColor: AppColors.primary,
            child: Text(
              user['nickname']?.substring(0, 1) ?? 'U',
              style: const TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: Colors.white,
              ),
            ),
          ),
          const SizedBox(width: 16),
          
          // ユーザー情報
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  user['nickname'] ?? '不明なユーザー',
                  style: const TextStyle(
                    fontSize: AppConstants.subtitleFontSize,
                    fontWeight: FontWeight.bold,
                    color: AppColors.textPrimary,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  '称号: ${user['title'] ?? '初心者'}',
                  style: const TextStyle(
                    fontSize: AppConstants.bodyFontSize,
                    color: AppColors.textSecondary,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  user['email'] ?? '',
                  style: const TextStyle(
                    fontSize: AppConstants.captionFontSize,
                    color: AppColors.textSecondary,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// ウェルカムメッセージを構築
  Widget _buildWelcomeMessage() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.black.withOpacity(0.7),
        borderRadius: BorderRadius.circular(AppConstants.cardRadius),
        border: Border.all(color: AppColors.primary.withOpacity(0.3)),
      ),
      child: Column(
        children: [
          Icon(
            Icons.celebration,
            size: 48,
            color: AppColors.primary,
          ),
          const SizedBox(height: 16),
          Text(
            'ロビーへようこそ！',
            style: TextStyle(
              fontSize: AppConstants.titleFontSize,
              fontWeight: FontWeight.bold,
              color: AppColors.primary,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'じゃんけんバトルを開始できます',
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: AppConstants.bodyFontSize,
              color: AppColors.textSecondary,
            ),
          ),
        ],
      ),
    );
  }

  /// アクションボタンを構築
  Widget _buildActionButtons() {
    return Column(
      children: [
        // バトル開始ボタン
        CustomButton(
          text: 'じゃんけんバトル開始',
          onPressed: () => _startBattle(),
          width: double.infinity,
          height: AppConstants.buttonHeight,
          backgroundColor: AppColors.primary,
        ),
        const SizedBox(height: 16),
        
        // ログアウトボタン
        CustomButton(
          text: 'ログアウト',
          onPressed: _handleLogout,
          width: double.infinity,
          height: AppConstants.buttonHeight,
          backgroundColor: AppColors.error,
        ),
      ],
    );
  }

  /// シンプルなメニューを構築
  Widget _buildSimpleMenu() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.black.withOpacity(0.8),
        borderRadius: BorderRadius.circular(AppConstants.cardRadius),
      ),
      child: Column(
        children: [
          Text(
            '開発状況',
            style: TextStyle(
              fontSize: AppConstants.subtitleFontSize,
              fontWeight: FontWeight.bold,
              color: AppColors.textPrimary,
            ),
          ),
          const SizedBox(height: 12),
          _buildDevStatusItem('ログイン機能', '✅ 完了'),
          _buildDevStatusItem('ロビー画面', '✅ 完了'),
          _buildDevStatusItem('バトル画面', '✅ 完了'),
          _buildDevStatusItem('WebSocket通信', '✅ 完了'),
          _buildDevStatusItem('ランキング', '⏳ 未実装'),
        ],
      ),
    );
  }

  /// 開発状況項目を構築
  Widget _buildDevStatusItem(String feature, String status) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            feature,
            style: TextStyle(
              fontSize: AppConstants.bodyFontSize,
              color: AppColors.textSecondary,
            ),
          ),
          Text(
            status,
            style: TextStyle(
              fontSize: AppConstants.bodyFontSize,
              color: AppColors.textPrimary,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  /// バトル開始処理
  void _startBattle() {
    Navigator.of(context).pushNamed('/battle');
  }

  /// ログアウト処理
  void _handleLogout() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('ログアウト'),
        content: const Text('ログアウトしますか？'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text(AppStrings.cancel),
          ),
          TextButton(
            onPressed: () {
              Navigator.of(context).pop();
              context.read<AuthProvider>().logout();
            },
            child: const Text(AppStrings.confirm),
          ),
        ],
      ),
    );
  }
}
