/// じゃんけんデバッグ用テストケース定義
/// 
/// このファイルは以下のテストケースを定義します：
/// - 基本勝敗パターン
/// - 引き分けパターン
/// - エッジケースパターン
/// - 連続対戦パターン

class JankenDebugTestCases {
  /// 基本勝敗パターン
  static const Map<String, Map<String, dynamic>> basicPatterns = {
    'rock_vs_scissors': {
      'description': 'グー vs チョキ → グーの勝ち',
      'player1': {'hand': 'rock', 'expected': 'win'},
      'player2': {'hand': 'scissors', 'expected': 'lose'},
      'winner': 1,
      'isDraw': false,
    },
    'scissors_vs_paper': {
      'description': 'チョキ vs パー → チョキの勝ち',
      'player1': {'hand': 'scissors', 'expected': 'win'},
      'player2': {'hand': 'paper', 'expected': 'lose'},
      'winner': 1,
      'isDraw': false,
    },
    'paper_vs_rock': {
      'description': 'パー vs グー → パーの勝ち',
      'player1': {'hand': 'paper', 'expected': 'win'},
      'player2': {'hand': 'rock', 'expected': 'lose'},
      'winner': 1,
      'isDraw': false,
    },
  };

  /// 引き分けパターン
  static const Map<String, Map<String, dynamic>> drawPatterns = {
    'rock_vs_rock': {
      'description': 'グー vs グー → 引き分け',
      'player1': {'hand': 'rock', 'expected': 'draw'},
      'player2': {'hand': 'rock', 'expected': 'draw'},
      'winner': 3,
      'isDraw': true,
    },
    'scissors_vs_scissors': {
      'description': 'チョキ vs チョキ → 引き分け',
      'player1': {'hand': 'scissors', 'expected': 'draw'},
      'player2': {'hand': 'scissors', 'expected': 'draw'},
      'winner': 3,
      'isDraw': true,
    },
    'paper_vs_paper': {
      'description': 'パー vs パー → 引き分け',
      'player1': {'hand': 'paper', 'expected': 'draw'},
      'player2': {'hand': 'paper', 'expected': 'draw'},
      'winner': 3,
      'isDraw': true,
    },
  };

  /// 連続引き分けパターン
  static const Map<String, List<Map<String, dynamic>>> multipleDrawPatterns = {
    'double_rock_draw': [
      {
        'description': '1回目: グー vs グー → 引き分け',
        'player1': {'hand': 'rock', 'expected': 'draw'},
        'player2': {'hand': 'rock', 'expected': 'draw'},
        'winner': 3,
        'isDraw': true,
        'drawCount': 1,
      },
      {
        'description': '2回目: グー vs グー → 引き分け',
        'player1': {'hand': 'rock', 'expected': 'draw'},
        'player2': {'hand': 'rock', 'expected': 'draw'},
        'winner': 3,
        'isDraw': true,
        'drawCount': 2,
      },
      {
        'description': '3回目: グー vs チョキ → グーの勝ち',
        'player1': {'hand': 'rock', 'expected': 'win'},
        'player2': {'hand': 'scissors', 'expected': 'lose'},
        'winner': 1,
        'isDraw': false,
        'drawCount': 2,
      },
    ],
    'mixed_draw_pattern': [
      {
        'description': '1回目: パー vs パー → 引き分け',
        'player1': {'hand': 'paper', 'expected': 'draw'},
        'player2': {'hand': 'paper', 'expected': 'draw'},
        'winner': 3,
        'isDraw': true,
        'drawCount': 1,
      },
      {
        'description': '2回目: チョキ vs チョキ → 引き分け',
        'player1': {'hand': 'scissors', 'expected': 'draw'},
        'player2': {'hand': 'scissors', 'expected': 'draw'},
        'winner': 3,
        'isDraw': true,
        'drawCount': 2,
      },
      {
        'description': '3回目: パー vs グー → パーの勝ち',
        'player1': {'hand': 'paper', 'expected': 'win'},
        'player2': {'hand': 'rock', 'expected': 'lose'},
        'winner': 1,
        'isDraw': false,
        'drawCount': 2,
      },
    ],
  };

  /// エッジケースパターン
  static const Map<String, Map<String, dynamic>> edgeCasePatterns = {
    'hand_submission_timeout': {
      'description': '手送信後のタイムアウト',
      'scenario': '片方のみ手送信 → 相手待ち状態 → タイムアウト',
      'expectedBehavior': 'タイムアウトエラー表示',
    },
    'connection_drop_during_battle': {
      'description': '対戦中の接続断',
      'scenario': '手選択中 → 接続断 → 再接続',
      'expectedBehavior': '再接続処理実行',
    },
    'battle_quit_during_hand_selection': {
      'description': '手選択中の対戦辞退',
      'scenario': '手選択中 → 対戦辞退',
      'expectedBehavior': '辞退確認ダイアログ表示',
    },
  };

  /// テストケース実行順序
  static const List<String> recommendedTestOrder = [
    '基本勝敗テスト',
    '引き分けテスト',
    '連続引き分けテスト',
    'エッジケーステスト',
    '状態管理テスト',
  ];

  /// テストケースの説明を取得
  static String getTestCaseDescription(String patternKey) {
    if (basicPatterns.containsKey(patternKey)) {
      return basicPatterns[patternKey]!['description'] as String;
    } else if (drawPatterns.containsKey(patternKey)) {
      return drawPatterns[patternKey]!['description'] as String;
    } else if (edgeCasePatterns.containsKey(patternKey)) {
      return edgeCasePatterns[patternKey]!['description'] as String;
    }
    return '不明なテストケース';
  }

  /// 全テストケースの概要を取得
  static Map<String, int> getTestCaseSummary() {
    return {
      '基本勝敗パターン': basicPatterns.length,
      '引き分けパターン': drawPatterns.length,
      '連続引き分けパターン': multipleDrawPatterns.length,
      'エッジケースパターン': edgeCasePatterns.length,
    };
  }
}
