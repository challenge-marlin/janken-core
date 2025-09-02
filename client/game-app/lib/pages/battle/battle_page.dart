import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/battle_provider.dart';
import '../../providers/auth_provider.dart';
import '../../utils/constants.dart';
import '../../widgets/common/custom_button.dart';
import 'package:flutter/foundation.dart'; // kDebugModeを追加

/// バトル画面
/// 
/// この画面は以下の機能を提供します：
/// - WebSocket接続・認証
/// - マッチング・対戦相手検索
/// - リアルタイムじゃんけん対戦
/// - 対戦結果表示
class BattlePage extends StatefulWidget {
  const BattlePage({super.key});

  @override
  State<BattlePage> createState() => _BattlePageState();
}

class _BattlePageState extends State<BattlePage> {
  @override
  void initState() {
    super.initState();
    // 画面表示時にWebSocket接続を開始
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<BattleProvider>().connect();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: _buildAppBar(),
      body: _buildBody(),
    );
  }

  /// アプリバーを構築
  PreferredSizeWidget _buildAppBar() {
    return AppBar(
      title: const Text(
        'じゃんけんバトル',
        style: TextStyle(
          color: AppColors.textPrimary,
          fontWeight: FontWeight.bold,
        ),
      ),
      backgroundColor: AppColors.surface,
      elevation: 0,
      actions: [
        Consumer<BattleProvider>(
          builder: (context, battle, child) {
            if (battle.isConnected) {
              return IconButton(
                icon: const Icon(Icons.wifi, color: AppColors.success),
                onPressed: () {
                  // 接続状態表示
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('WebSocket接続中'),
                      backgroundColor: AppColors.success,
                    ),
                  );
                },
              );
            } else {
              return IconButton(
                icon: const Icon(Icons.wifi_off, color: AppColors.error),
                onPressed: () {
                  // 再接続
                  battle.reconnect();
                },
              );
            }
          },
        ),
      ],
    );
  }

  /// メインコンテンツを構築
  Widget _buildBody() {
    return Consumer<BattleProvider>(
      builder: (context, battle, child) {
        if (battle.isConnecting) {
          return _buildConnectingView();
        }

        if (battle.connectionError != null) {
          return _buildErrorView(battle);
        }

        if (!battle.isConnected) {
          return _buildDisconnectedView(battle);
        }

        if (battle.isMatching) {
          return _buildMatchingView(battle);
        }

        // 引き分け結果表示中（最優先で表示）
        if (battle.isShowingDrawResult && battle.battleResult != null) {
          print('[DEBUG] 引き分け結果表示画面を表示');
          return _buildDrawResultView(battle);
        }

        if (battle.isInBattle) {
          return _buildBattleView(battle);
        }

        // 最終結果表示（勝敗が決まった場合）
        if (battle.battleResult != null && !battle.isDraw) {
          print('[DEBUG] 最終結果表示画面を表示');
          return _buildFinalResultView(battle);
        }

        return _buildMainView(battle);
      },
    );
  }

  /// 接続中画面
  Widget _buildConnectingView() {
    return const Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          CircularProgressIndicator(
            valueColor: AlwaysStoppedAnimation<Color>(AppColors.primary),
          ),
          SizedBox(height: 16),
          Text(
            'WebSocket接続中...',
            style: TextStyle(
              fontSize: AppConstants.bodyFontSize,
              color: AppColors.textSecondary,
            ),
          ),
        ],
      ),
    );
  }

  /// エラー画面
  Widget _buildErrorView(BattleProvider battle) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(AppConstants.screenPadding),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.error_outline,
              size: 64,
              color: AppColors.error,
            ),
            const SizedBox(height: 16),
            Text(
              '接続エラー',
              style: TextStyle(
                fontSize: AppConstants.titleFontSize,
                fontWeight: FontWeight.bold,
                color: AppColors.error,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              battle.connectionError ?? '不明なエラー',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: AppConstants.bodyFontSize,
                color: AppColors.textSecondary,
              ),
            ),
            const SizedBox(height: 24),
            CustomButton(
              text: '再接続',
              onPressed: () => battle.reconnect(),
              backgroundColor: AppColors.primary,
            ),
          ],
        ),
      ),
    );
  }

  /// 切断画面
  Widget _buildDisconnectedView(BattleProvider battle) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(AppConstants.screenPadding),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.wifi_off,
              size: 64,
              color: AppColors.warning,
            ),
            const SizedBox(height: 16),
            Text(
              '接続が切断されました',
              style: TextStyle(
                fontSize: AppConstants.titleFontSize,
                fontWeight: FontWeight.bold,
                color: AppColors.warning,
              ),
            ),
            const SizedBox(height: 8),
            const Text(
              'WebSocket接続を再確立してください',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: AppConstants.bodyFontSize,
                color: AppColors.textSecondary,
              ),
            ),
            const SizedBox(height: 24),
            CustomButton(
              text: '再接続',
              onPressed: () => battle.reconnect(),
              backgroundColor: AppColors.primary,
            ),
          ],
        ),
      ),
    );
  }

  /// メイン画面（接続済み・待機中）
  Widget _buildMainView(BattleProvider battle) {
    return Padding(
      padding: const EdgeInsets.all(AppConstants.screenPadding),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          // 接続状態表示
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: AppColors.success.withOpacity(0.1),
              borderRadius: BorderRadius.circular(AppConstants.cardRadius),
              border: Border.all(color: AppColors.success.withOpacity(0.3)),
            ),
            child: Row(
              children: [
                Icon(
                  Icons.check_circle,
                  color: AppColors.success,
                  size: 24,
                ),
                const SizedBox(width: 8),
                const Text(
                  'WebSocket接続済み',
                  style: TextStyle(
                    fontSize: AppConstants.bodyFontSize,
                    fontWeight: FontWeight.bold,
                    color: AppColors.success,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 48),
          
          // マッチング開始ボタン
          CustomButton(
            text: 'マッチング開始',
            onPressed: () => battle.startMatching(),
            width: double.infinity,
            height: AppConstants.buttonHeight,
            backgroundColor: AppColors.primary,
          ),
          const SizedBox(height: 16),
          
          // デバッグ用ボタン（開発時のみ表示）
          if (kDebugMode) ...[
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: AppColors.warning.withOpacity(0.1),
                borderRadius: BorderRadius.circular(AppConstants.cardRadius),
                border: Border.all(color: AppColors.warning.withOpacity(0.3)),
              ),
              child: Column(
                children: [
                  Text(
                    '🧪 デバッグ用テストケース',
                    style: TextStyle(
                      fontSize: AppConstants.subtitleFontSize,
                      fontWeight: FontWeight.bold,
                      color: AppColors.warning,
                    ),
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Expanded(
                        child: CustomButton(
                          text: '引き分けテスト',
                          onPressed: () => battle.debugSimulateDraw(),
                          backgroundColor: AppColors.warning,
                          height: 40,
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: CustomButton(
                          text: '勝利テスト',
                          onPressed: () => battle.debugSimulateWin(),
                          backgroundColor: AppColors.success,
                          height: 40,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      Expanded(
                        child: CustomButton(
                          text: '敗北テスト',
                          onPressed: () => battle.debugSimulateLose(),
                          backgroundColor: AppColors.error,
                          height: 40,
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: CustomButton(
                          text: '連続引き分け',
                          onPressed: () => battle.debugSimulateMultipleDraws(),
                          backgroundColor: AppColors.info,
                          height: 40,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      Expanded(
                        child: CustomButton(
                          text: '状態ログ',
                          onPressed: () => battle.debugLogCurrentState(),
                          backgroundColor: AppColors.surface,
                          height: 40,
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: CustomButton(
                          text: '状態リセット',
                          onPressed: () => battle.debugResetState(),
                          backgroundColor: AppColors.textSecondary,
                          height: 40,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),
          ],
          
          // 説明
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: AppColors.card,
              borderRadius: BorderRadius.circular(AppConstants.cardRadius),
            ),
            child: Column(
              children: [
                Text(
                  '対戦の流れ',
                  style: TextStyle(
                    fontSize: AppConstants.subtitleFontSize,
                    fontWeight: FontWeight.bold,
                    color: AppColors.textPrimary,
                  ),
                ),
                const SizedBox(height: 12),
                _buildStepItem('1', 'マッチング開始', '対戦相手を探します'),
                _buildStepItem('2', '対戦相手発見', '相手の準備完了を待ちます'),
                _buildStepItem('3', '手を選択', 'グー・チョキ・パーから選択'),
                _buildStepItem('4', '結果判定', '勝敗が決定されます'),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// ステップ項目を構築
  Widget _buildStepItem(String number, String title, String description) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Container(
            width: 24,
            height: 24,
            decoration: BoxDecoration(
              color: AppColors.primary,
              borderRadius: BorderRadius.circular(12),
            ),
            child: Center(
              child: Text(
                number,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: AppConstants.bodyFontSize,
                    fontWeight: FontWeight.bold,
                    color: AppColors.textPrimary,
                  ),
                ),
                Text(
                  description,
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

  /// マッチング画面
  Widget _buildMatchingView(BattleProvider battle) {
    return Padding(
      padding: const EdgeInsets.all(AppConstants.screenPadding),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          // マッチング中表示
          Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: AppColors.primary.withOpacity(0.1),
              borderRadius: BorderRadius.circular(AppConstants.cardRadius),
              border: Border.all(color: AppColors.primary.withOpacity(0.3)),
            ),
            child: Column(
              children: [
                const CircularProgressIndicator(
                  valueColor: AlwaysStoppedAnimation<Color>(AppColors.primary),
                ),
                const SizedBox(height: 16),
                Text(
                  'マッチング中...',
                  style: TextStyle(
                    fontSize: AppConstants.titleFontSize,
                    fontWeight: FontWeight.bold,
                    color: AppColors.primary,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  '対戦相手を探しています',
                  style: TextStyle(
                    fontSize: AppConstants.bodyFontSize,
                    color: AppColors.textSecondary,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),
          
          // キュー情報
          if (battle.queuePosition > 0)
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: AppColors.card,
                borderRadius: BorderRadius.circular(AppConstants.cardRadius),
              ),
              child: Column(
                children: [
                  Text(
                    '待機状況',
                    style: TextStyle(
                      fontSize: AppConstants.subtitleFontSize,
                      fontWeight: FontWeight.bold,
                      color: AppColors.textPrimary,
                    ),
                  ),
                  const SizedBox(height: 12),
                  Text(
                    '順番: ${battle.queuePosition}番目',
                    style: TextStyle(
                      fontSize: AppConstants.bodyFontSize,
                      color: AppColors.textSecondary,
                    ),
                  ),
                  if (battle.estimatedWaitTime > 0)
                    Text(
                      '予想待機時間: 約${battle.estimatedWaitTime}秒',
                      style: TextStyle(
                        fontSize: AppConstants.bodyFontSize,
                        color: AppColors.textSecondary,
                      ),
                    ),
                ],
              ),
            ),
          
          const SizedBox(height: 24),
          
          // キャンセルボタン
          CustomButton(
            text: 'マッチングキャンセル',
            onPressed: () => _showCancelMatchingDialog(battle),
            backgroundColor: AppColors.error,
          ),
        ],
      ),
    );
  }

  /// バトル画面
  Widget _buildBattleView(BattleProvider battle) {
    return Padding(
      padding: const EdgeInsets.all(AppConstants.screenPadding),
      child: Column(
        children: [
          // 対戦相手情報
          _buildOpponentInfo(battle),
          const SizedBox(height: 24),
          
          // 準備状態
          if (!battle.isReady || !battle.isOpponentReady)
            _buildPreparationView(battle),
          
          // 手選択画面
          if (battle.isReady && battle.isOpponentReady)
            _buildHandSelectionView(battle),
          
          // 手送信済み表示
          if (battle.isHandSubmitted)
            _buildHandSubmittedView(battle),
          
          const SizedBox(height: 24),
          
          // 対戦辞退ボタン
          CustomButton(
            text: '対戦辞退',
            onPressed: () => _showQuitConfirmDialog(battle),
            backgroundColor: AppColors.error,
          ),
        ],
      ),
    );
  }

  /// 対戦相手情報を構築
  Widget _buildOpponentInfo(BattleProvider battle) {
    if (battle.opponent == null) return const SizedBox.shrink();
    
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.card,
        borderRadius: BorderRadius.circular(AppConstants.cardRadius),
      ),
      child: Row(
        children: [
          // 相手のプロフィール画像
          CircleAvatar(
            radius: 40,
            backgroundColor: AppColors.primary,
            child: Text(
              battle.opponent!['nickname']?.substring(0, 1) ?? 'O',
              style: const TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: Colors.white,
              ),
            ),
          ),
          const SizedBox(width: 16),
          
          // 相手の情報
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  battle.opponent!['nickname'] ?? '対戦相手',
                  style: const TextStyle(
                    fontSize: AppConstants.subtitleFontSize,
                    fontWeight: FontWeight.bold,
                    color: AppColors.textPrimary,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'プレイヤー${battle.playerNumber == 1 ? "2" : "1"}',
                  style: TextStyle(
                    fontSize: AppConstants.bodyFontSize,
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

  /// 準備画面を構築
  Widget _buildPreparationView(BattleProvider battle) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppColors.warning.withOpacity(0.1),
        borderRadius: BorderRadius.circular(AppConstants.cardRadius),
        border: Border.all(color: AppColors.warning.withOpacity(0.3)),
      ),
      child: Column(
        children: [
          Icon(
            Icons.hourglass_empty,
            size: 48,
            color: AppColors.warning,
          ),
          const SizedBox(height: 16),
          Text(
            '対戦準備中...',
            style: TextStyle(
              fontSize: AppConstants.titleFontSize,
              fontWeight: FontWeight.bold,
              color: AppColors.warning,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            '両者の準備完了を待っています',
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: AppConstants.bodyFontSize,
              color: AppColors.textSecondary,
            ),
          ),
          const SizedBox(height: 16),
          
          // 準備状況
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildPlayerStatus('あなた', battle.isReady),
              _buildPlayerStatus('相手', battle.isOpponentReady),
            ],
          ),
          
          const SizedBox(height: 16),
          
          // 準備完了ボタン
          if (!battle.isReady)
            CustomButton(
              text: '準備完了',
              onPressed: () => battle.setReady(),
              backgroundColor: AppColors.success,
            ),
        ],
      ),
    );
  }

  /// プレイヤー状態を構築
  Widget _buildPlayerStatus(String name, bool isReady) {
    return Column(
      children: [
        Text(
          name,
          style: TextStyle(
            fontSize: AppConstants.bodyFontSize,
            color: AppColors.textSecondary,
          ),
        ),
        const SizedBox(height: 4),
        Icon(
          isReady ? Icons.check_circle : Icons.schedule,
          color: isReady ? AppColors.success : AppColors.warning,
          size: 24,
        ),
        Text(
          isReady ? '準備完了' : '準備中',
          style: TextStyle(
            fontSize: AppConstants.captionFontSize,
            color: isReady ? AppColors.success : AppColors.warning,
          ),
        ),
      ],
    );
  }

  /// 手選択画面を構築
  Widget _buildHandSelectionView(BattleProvider battle) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppColors.primary.withOpacity(0.1),
        borderRadius: BorderRadius.circular(AppConstants.cardRadius),
        border: Border.all(color: AppColors.primary.withOpacity(0.3)),
      ),
      child: Column(
        children: [
          Text(
            '手を選択してください',
            style: TextStyle(
              fontSize: AppConstants.titleFontSize,
              fontWeight: FontWeight.bold,
              color: AppColors.primary,
            ),
          ),
          const SizedBox(height: 16),
          
          // 手選択ボタン
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: [
              _buildHandButton('✊', 'グー', 'rock', battle),
              _buildHandButton('✌️', 'チョキ', 'scissors', battle),
              _buildHandButton('✋', 'パー', 'paper', battle),
            ],
          ),
          
          const SizedBox(height: 16),
          
          // 選択された手
          if (battle.selectedHand != null)
            Text(
              '選択: ${_getHandDisplayName(battle.selectedHand!)}',
              style: TextStyle(
                fontSize: AppConstants.bodyFontSize,
                color: AppColors.primary,
                fontWeight: FontWeight.bold,
              ),
            ),
          
          const SizedBox(height: 16),
          
          // 手送信ボタン
          CustomButton(
            text: '手を送信',
            onPressed: battle.selectedHand != null ? () => battle.submitHand() : null,
            backgroundColor: AppColors.primary,
          ),
        ],
      ),
    );
  }

  /// 手ボタンを構築
  Widget _buildHandButton(String emoji, String name, String value, BattleProvider battle) {
    final isSelected = battle.selectedHand == value;
    
    return GestureDetector(
      onTap: () => battle.selectHand(value),
      child: Container(
        width: 80,
        height: 80,
        decoration: BoxDecoration(
          color: isSelected ? AppColors.primary : AppColors.card,
          borderRadius: BorderRadius.circular(40),
          border: Border.all(
            color: isSelected ? AppColors.primary : AppColors.textSecondary.withOpacity(0.3),
            width: 2,
          ),
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              emoji,
              style: const TextStyle(fontSize: 32),
            ),
            Text(
              name,
              style: TextStyle(
                fontSize: AppConstants.captionFontSize,
                color: isSelected ? Colors.white : AppColors.textSecondary,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// 手の表示名を取得
  String _getHandDisplayName(String hand) {
    switch (hand) {
      case 'rock':
        return '✊ グー';
      case 'scissors':
        return '✌️ チョキ';
      case 'paper':
        return '✋ パー';
      default:
        return hand;
    }
  }

  /// 手送信済み画面を構築
  Widget _buildHandSubmittedView(BattleProvider battle) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppColors.info.withOpacity(0.1),
        borderRadius: BorderRadius.circular(AppConstants.cardRadius),
        border: Border.all(color: AppColors.info.withOpacity(0.3)),
      ),
      child: Column(
        children: [
          Icon(
            Icons.hourglass_bottom,
            size: 48,
            color: AppColors.info,
          ),
          const SizedBox(height: 16),
          Text(
            '手を送信しました',
            style: TextStyle(
              fontSize: AppConstants.titleFontSize,
              fontWeight: FontWeight.bold,
              color: AppColors.info,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            '相手の手を待っています...',
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

  /// 引き分け結果画面を構築
  Widget _buildDrawResultView(BattleProvider battle) {
    if (battle.battleResult == null) return const SizedBox.shrink();
    
    final result = battle.battleResult!;
    final player1 = result['player1'];
    final player2 = result['player2'];
    
    print('[DEBUG] 引き分け結果画面構築: result=$result, drawCount=${battle.drawCount}');
    
    return Padding(
      padding: const EdgeInsets.all(AppConstants.screenPadding),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          // 引き分け結果表示
          Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: AppColors.warning.withOpacity(0.1),
              borderRadius: BorderRadius.circular(AppConstants.cardRadius),
              border: Border.all(color: AppColors.warning.withOpacity(0.3)),
            ),
            child: Column(
              children: [
                Icon(
                  Icons.emoji_events,
                  size: 64,
                  color: AppColors.warning,
                ),
                const SizedBox(height: 16),
                Text(
                  '引き分け！',
                  style: TextStyle(
                    fontSize: AppConstants.titleFontSize,
                    fontWeight: FontWeight.bold,
                    color: AppColors.warning,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  '同じ相手と勝負がつくまで続けます',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: AppConstants.bodyFontSize,
                    color: AppColors.textSecondary,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  '3秒後に次のラウンドに進みます...',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: AppConstants.captionFontSize,
                    color: AppColors.textSecondary,
                    fontStyle: FontStyle.italic,
                  ),
                ),
              ],
            ),
          ),
          
          const SizedBox(height: 24),
          
          // 詳細結果
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: AppColors.card,
              borderRadius: BorderRadius.circular(AppConstants.cardRadius),
            ),
            child: Column(
              children: [
                Text(
                  'ラウンド結果',
                  style: TextStyle(
                    fontSize: AppConstants.subtitleFontSize,
                    fontWeight: FontWeight.bold,
                    color: AppColors.textPrimary,
                  ),
                ),
                const SizedBox(height: 16),
                
                // プレイヤー1の手
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'あなた (P${battle.playerNumber})',
                      style: TextStyle(
                        fontSize: AppConstants.bodyFontSize,
                        color: AppColors.textSecondary,
                      ),
                    ),
                    Text(
                      _getHandDisplayName(player1['hand']),
                      style: TextStyle(
                        fontSize: AppConstants.bodyFontSize,
                        color: AppColors.textPrimary,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                
                const SizedBox(height: 8),
                
                // プレイヤー2の手
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      '相手 (P${battle.playerNumber == 1 ? "2" : "1"})',
                      style: TextStyle(
                        fontSize: AppConstants.bodyFontSize,
                        color: AppColors.textSecondary,
                      ),
                    ),
                    Text(
                      _getHandDisplayName(player2['hand']),
                      style: TextStyle(
                        fontSize: AppConstants.bodyFontSize,
                        color: AppColors.textPrimary,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                
                const SizedBox(height: 16),
                
                // 引き分け回数
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                  decoration: BoxDecoration(
                    color: AppColors.warning.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: AppColors.warning.withOpacity(0.3)),
                  ),
                  child: Text(
                    '引き分け回数: ${battle.drawCount}回',
                    style: TextStyle(
                      fontSize: AppConstants.captionFontSize,
                      color: AppColors.warning,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
          ),
          
          const SizedBox(height: 24),
          
          // 次のラウンド準備中メッセージ
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            decoration: BoxDecoration(
              color: AppColors.info.withOpacity(0.1),
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: AppColors.info.withOpacity(0.3)),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                const SizedBox(
                  width: 16,
                  height: 16,
                  child: CircularProgressIndicator(
                    strokeWidth: 2,
                    valueColor: AlwaysStoppedAnimation<Color>(AppColors.info),
                  ),
                ),
                const SizedBox(width: 8),
                Text(
                  '次のラウンドを準備中...',
                  style: TextStyle(
                    fontSize: AppConstants.captionFontSize,
                    color: AppColors.info,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// 最終結果画面を構築（勝敗が決まった場合）
  Widget _buildFinalResultView(BattleProvider battle) {
    if (battle.battleResult == null) return const SizedBox.shrink();
    
    final result = battle.battleResult!;
    final player1 = result['player1'];
    final player2 = result['player2'];
    final winner = result['winner'];
    
    // プレイヤー番号から結果を判定
    String resultText;
    Color resultColor;
    
    if (winner == battle.playerNumber) {
      resultText = '勝利！';
      resultColor = AppColors.success;
    } else {
      resultText = '敗北...';
      resultColor = AppColors.error;
    }
    
    return Padding(
      padding: const EdgeInsets.all(AppConstants.screenPadding),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          // 結果表示
          Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: resultColor.withOpacity(0.1),
              borderRadius: BorderRadius.circular(AppConstants.cardRadius),
              border: Border.all(color: resultColor.withOpacity(0.3)),
            ),
            child: Column(
              children: [
                Icon(
                  winner == battle.playerNumber ? Icons.emoji_events : Icons.sentiment_dissatisfied,
                  size: 64,
                  color: resultColor,
                ),
                const SizedBox(height: 16),
                Text(
                  resultText,
                  style: TextStyle(
                    fontSize: AppConstants.titleFontSize,
                    fontWeight: FontWeight.bold,
                    color: resultColor,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),
          
          // 詳細結果
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: AppColors.card,
              borderRadius: BorderRadius.circular(AppConstants.cardRadius),
            ),
            child: Column(
              children: [
                Text(
                  '対戦結果',
                  style: TextStyle(
                    fontSize: AppConstants.subtitleFontSize,
                    fontWeight: FontWeight.bold,
                    color: AppColors.textPrimary,
                  ),
                ),
                const SizedBox(height: 16),
                
                // プレイヤー1の手
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'あなた (P${battle.playerNumber})',
                      style: TextStyle(
                        fontSize: AppConstants.bodyFontSize,
                        color: AppColors.textSecondary,
                      ),
                    ),
                    Text(
                      _getHandDisplayName(player1['hand']),
                      style: TextStyle(
                        fontSize: AppConstants.bodyFontSize,
                        color: AppColors.textPrimary,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                
                const SizedBox(height: 8),
                
                // プレイヤー2の手
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      '相手 (P${battle.playerNumber == 1 ? "2" : "1"})',
                      style: TextStyle(
                        fontSize: AppConstants.bodyFontSize,
                        color: AppColors.textSecondary,
                      ),
                    ),
                    Text(
                      _getHandDisplayName(player2['hand']),
                      style: TextStyle(
                        fontSize: AppConstants.bodyFontSize,
                        color: AppColors.textPrimary,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                
                if (battle.drawCount > 0) ...[
                  const SizedBox(height: 8),
                  Text(
                    '引き分け回数: ${battle.drawCount}回',
                    style: TextStyle(
                      fontSize: AppConstants.captionFontSize,
                      color: AppColors.warning,
                    ),
                  ),
                ],
              ],
            ),
          ),
          
          const SizedBox(height: 24),
          
          // アクションボタン
          Row(
            children: [
              Expanded(
                child: CustomButton(
                  text: 'もう一度対戦',
                  onPressed: () {
                    battle.clearBattleResult();
                    battle.startMatching();
                  },
                  backgroundColor: AppColors.primary,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: CustomButton(
                  text: 'ロビーに戻る',
                  onPressed: () => _showReturnToLobbyDialog(battle),
                  backgroundColor: AppColors.surface,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  /// マッチングキャンセル確認ダイアログを表示
  void _showCancelMatchingDialog(BattleProvider battle) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('マッチングキャンセル'),
        content: const Text('マッチングをキャンセルしますか？\nWebSocket接続も切断されます。'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text(AppStrings.cancel),
          ),
          TextButton(
            onPressed: () {
              Navigator.of(context).pop();
              _cancelMatchingAndDisconnect(battle);
            },
            child: const Text(AppStrings.confirm),
          ),
        ],
      ),
    );
  }

  /// ロビーに戻る確認ダイアログを表示
  void _showReturnToLobbyDialog(BattleProvider battle) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('ロビーに戻る'),
        content: const Text('ロビーに戻りますか？\nWebSocket接続も切断されます。'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text(AppStrings.cancel),
          ),
          TextButton(
            onPressed: () {
              Navigator.of(context).pop();
              _returnToLobbyWithDisconnect(battle);
            },
            child: const Text(AppStrings.confirm),
          ),
        ],
      ),
    );
  }

  /// 対戦辞退確認ダイアログを表示
  void _showQuitConfirmDialog(BattleProvider battle) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('対戦辞退'),
        content: const Text('本当に対戦を辞退しますか？'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text(AppStrings.cancel),
          ),
          TextButton(
            onPressed: () {
              Navigator.of(context).pop();
              battle.quitBattle();
            },
            child: const Text(AppStrings.confirm),
          ),
        ],
      ),
    );
  }

  /// マッチングキャンセルとWebSocket切断
  void _cancelMatchingAndDisconnect(BattleProvider battle) {
    // マッチングキャンセル
    battle.cancelMatching();
    
    // WebSocket接続を切断
    battle.disconnect();
    
    // 成功メッセージを表示
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('マッチングをキャンセルしました'),
        backgroundColor: AppColors.info,
      ),
    );
    
    // メイン画面に戻る（接続状態が更新される）
  }

  /// ロビーに戻る際のWebSocket切断
  void _returnToLobbyWithDisconnect(BattleProvider battle) {
    // WebSocket接続を切断
    battle.disconnect();
    
    // 成功メッセージを表示
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('ロビーに戻ります'),
        backgroundColor: AppColors.info,
      ),
    );
    
    // ロビー画面に戻る
    Navigator.of(context).pop();
  }

  @override
  void dispose() {
    // 画面を離れる際にWebSocket接続を切断
    context.read<BattleProvider>().disconnect();
    super.dispose();
  }
}
