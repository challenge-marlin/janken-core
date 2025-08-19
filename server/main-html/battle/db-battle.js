/**
 * DBありきじゃんけんバトル - メインJavaScript
 * パスワード認証、ユーザープロフィール、統計データ、ランキングの完全DB連携
 */

class DBBattleGame {
    constructor() {
        this.currentUser = null;
        this.websocket = null;
        this.isConnected = false;
        this.currentBattle = null;
        this.selectedHand = null;
        this.battleState = 'idle'; // idle, matching, battling, result
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.log('🎮 DBありきじゃんけんバトルシステム初期化完了');
        this.log('📋 テスト用ログイン情報: test1@example.com 〜 test5@example.com / password123');
        this.log('🔄 ボリュームマウント確認: このメッセージが表示されれば自動反映成功！');
    }
    
    bindEvents() {
        // ログイン関連
        document.getElementById('dbLoginBtn').addEventListener('click', () => this.handleDBLogin());
        document.getElementById('magicLinkBtn').addEventListener('click', () => this.handleMagicLink());
        document.getElementById('logoutBtn').addEventListener('click', () => this.handleLogout());
        
        // バトル関連
        document.getElementById('connectBtn').addEventListener('click', () => this.connectWebSocket());
        document.getElementById('disconnectBtn').addEventListener('click', () => this.disconnectWebSocket());
        document.getElementById('startMatchingBtn').addEventListener('click', () => this.startMatching());
        document.getElementById('cancelMatchingBtn').addEventListener('click', () => this.cancelMatching());
        document.getElementById('readyBtn').addEventListener('click', () => this.sendReady());
        document.getElementById('nextRoundBtn').addEventListener('click', () => this.nextRound());
        document.getElementById('newBattleBtn').addEventListener('click', () => this.newBattle());
        document.getElementById('quitBattleBtn').addEventListener('click', () => this.quitBattle());
        
        // 手選択
        document.querySelectorAll('.hand-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.selectHand(e.target.closest('.hand-btn').dataset.hand));
        });
        
        // 統計・ランキング
        document.getElementById('refreshStatsBtn').addEventListener('click', () => this.refreshUserStats());
        document.getElementById('loadRankingBtn').addEventListener('click', () => this.loadRanking());
        
        // デバッグ
        document.getElementById('debugResetBtn').addEventListener('click', () => this.debugReset());
        document.getElementById('clearLogBtn').addEventListener('click', () => this.clearLog());
    }
    
    // ==================== 認証機能 ====================
    
    async handleDBLogin() {
        const userId = document.getElementById('dbUserSelect').value;
        const password = document.getElementById('passwordInput').value;
        
        if (!userId || !password) {
            this.log('❌ ユーザーIDとパスワードを入力してください', 'error');
            return;
        }
        
        try {
            this.log(`🔐 ${userId} でDB認証を開始...`);
            
            // パスワード認証API呼び出し
            const response = await fetch('/api/auth/db-login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    email: userId.replace('test_user_', 'test') + '@example.com',  // test_user_1 → test1@example.com
                    password: password
                })
            });
            
            const result = await response.json();
            
            // デバッグ情報を追加
            this.log(`🔍 APIレスポンス: ${JSON.stringify(result)}`);
            this.log(`🔍 HTTPステータス: ${response.status}`);
            
            if (response.ok && result.success && result.data && result.data.user) {
                this.currentUser = result.data.user;
                this.log(`✅ ログイン成功: ${this.currentUser.nickname}`);
                this.showUserProfile();
                this.showBattleSection();
                this.loadUserStats();
                this.loadRanking();
            } else {
                this.log(`❌ ログイン失敗: ${result.message || '認証エラー'}`, 'error');
                this.log(`❌ レスポンス詳細: ${JSON.stringify(result)}`, 'error');
            }
            
        } catch (error) {
            this.log(`❌ ログインエラー: ${error.message}`, 'error');
        }
    }
    
    async handleMagicLink() {
        const email = document.getElementById('emailInput').value;
        
        if (!email) {
            this.log('❌ メールアドレスを入力してください', 'error');
            return;
        }
        
        try {
            this.log(`🔗 ${email} にMagic Link送信中...`);
            
            const response = await fetch('/api/auth/request-magic-link', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email: email })
            });
            
            const result = await response.json();
            
            if (response.ok && result.success) {
                this.log(`✅ Magic Link送信完了: ${result.message}`);
            } else {
                this.log(`❌ Magic Link送信失敗: ${result.message || 'エラー'}`, 'error');
            }
            
        } catch (error) {
            this.log(`❌ Magic Link送信エラー: ${error.message}`, 'error');
        }
    }
    
    handleLogout() {
        this.currentUser = null;
        this.disconnectWebSocket();
        this.hideUserProfile();
        this.hideBattleSection();
        this.log('👋 ログアウト完了');
    }
    
    // ==================== ユーザープロフィール ====================
    
    showUserProfile() {
        if (!this.currentUser) return;
        
        // プロフィール情報表示
        document.getElementById('profileNickname').textContent = this.currentUser.nickname;
        document.getElementById('profileUserId').textContent = this.currentUser.user_id;
        document.getElementById('profileTitle').textContent = this.currentUser.title;
        
        // プロフィール画像（デフォルトアバター）
        const avatarElement = document.getElementById('profileAvatar');
        if (this.currentUser.profile_image) {
            avatarElement.textContent = '🖼️';
            avatarElement.title = this.currentUser.profile_image;
        } else {
            avatarElement.textContent = '👤';
        }
        
        document.getElementById('userProfileSection').style.display = 'block';
        document.getElementById('userDisplay').textContent = `${this.currentUser.nickname} (${this.currentUser.user_id})`;
        document.getElementById('logoutBtn').style.display = 'inline-block';
    }
    
    hideUserProfile() {
        document.getElementById('userProfileSection').style.display = 'none';
        document.getElementById('userDisplay').textContent = '未ログイン';
        document.getElementById('logoutBtn').style.display = 'none';
    }
    
    async loadUserStats() {
        if (!this.currentUser) return;
        
        try {
            this.log(`📊 ${this.currentUser.user_id} の統計データを取得中...`);
            
            const response = await fetch(`/api/battle/user-stats/${this.currentUser.user_id}`);
            const result = await response.json();
            
            if (response.ok && result.success) {
                const stats = result.data;
                this.updateStatsDisplay(stats);
                this.log(`✅ 統計データ更新完了: 総バトル数 ${stats.total_battles}`);
            } else {
                this.log(`❌ 統計データ取得失敗: ${result.message || 'エラー'}`, 'error');
            }
            
        } catch (error) {
            this.log(`❌ 統計データ取得エラー: ${error.message}`, 'error');
        }
    }
    
    updateStatsDisplay(stats) {
        document.getElementById('statTotalBattles').textContent = stats.total_battles || 0;
        document.getElementById('statWins').textContent = stats.wins || 0;
        document.getElementById('statLosses').textContent = stats.losses || 0;
        document.getElementById('statWinRate').textContent = `${((stats.win_rate || 0) * 100).toFixed(1)}%`;
        document.getElementById('statCurrentStreak').textContent = stats.current_streak || 0;
        document.getElementById('statBestStreak').textContent = stats.best_streak || 0;
        
        // レベルと経験値も更新
        if (stats.user_profile) {
            document.getElementById('profileLevel').textContent = stats.user_profile.level || 1;
            document.getElementById('profileExperience').textContent = stats.user_profile.experience || 0;
        }
    }
    
    async loadBattleHistory() {
        if (!this.currentUser) return;
        
        try {
            const response = await fetch(`/api/battle/battle-history/${this.currentUser.user_id}?limit=10`);
            const result = await response.json();
            
            if (response.ok && result.success) {
                this.updateBattleHistory(result.data);
            }
            
        } catch (error) {
            this.log(`❌ バトル履歴取得エラー: ${error.message}`, 'error');
        }
    }
    
    updateBattleHistory(battles) {
        const container = document.getElementById('battleHistoryList');
        
        if (!battles || battles.length === 0) {
            container.innerHTML = '<p style="text-align: center; color: #6c757d;">バトル履歴がありません</p>';
            return;
        }
        
        container.innerHTML = battles.map(battle => {
            const isWinner = battle.winner_id === this.currentUser.user_id;
            const resultClass = isWinner ? 'result-win' : 'result-lose';
            const resultText = isWinner ? '勝利' : '敗北';
            
            return `
                <div class="battle-item">
                    <div>
                        <strong>${battle.opponent_nickname || '対戦相手'}</strong><br>
                        <small>${new Date(battle.created_at).toLocaleString()}</small>
                    </div>
                    <div>
                        <span class="battle-result ${resultClass}">${resultText}</span><br>
                        <small>${battle.total_rounds}ラウンド</small>
                    </div>
                </div>
            `;
        }).join('');
    }
    
    // ==================== ランキング ====================
    
    async loadRanking() {
        try {
            this.log('🏆 日次ランキングを取得中...');
            
            const response = await fetch('/api/battle/daily-ranking');
            const result = await response.json();
            
            if (response.ok && result.success) {
                this.updateRankingDisplay(result.data);
                this.log(`✅ ランキング更新完了: ${result.data.length}名のプレイヤー`);
            } else {
                this.log(`❌ ランキング取得失敗: ${result.message || 'エラー'}`, 'error');
            }
            
        } catch (error) {
            this.log(`❌ ランキング取得エラー: ${error.message}`, 'error');
        }
    }
    
    updateRankingDisplay(rankings) {
        const container = document.getElementById('rankingList');
        
        if (!rankings || rankings.length === 0) {
            container.innerHTML = '<p style="text-align: center; color: #6c757d;">ランキングデータがありません</p>';
            return;
        }
        
        container.innerHTML = rankings.map((rank, index) => {
            const medal = index < 3 ? ['🥇', '🥈', '🥉'][index] : `${index + 1}`;
            const isCurrentUser = rank.user_id === this.currentUser?.user_id;
            const userClass = isCurrentUser ? 'font-weight-bold text-primary' : '';
            
            return `
                <div class="battle-item ${userClass}">
                    <div>
                        <strong>${medal} ${rank.nickname || rank.user_id}</strong><br>
                        <small>レベル ${rank.level || 1}</small>
                    </div>
                    <div>
                        <strong>${rank.score || 0}点</strong><br>
                        <small>${rank.battles_won || 0}勝 / ${rank.battles_played || 0}戦</small>
                    </div>
                </div>
            `;
        }).join('');
    }
    
    // ==================== WebSocket接続 ====================
    
    connectWebSocket() {
        if (this.isConnected) return;
        
        try {
            this.websocket = new WebSocket('ws://localhost:3000/ws/battle');
            
            this.websocket.onopen = () => {
                this.isConnected = true;
                this.updateConnectionStatus('connected');
                this.log('🔌 WebSocket接続完了');
            };
            
            this.websocket.onmessage = (event) => {
                this.handleWebSocketMessage(JSON.parse(event.data));
            };
            
            this.websocket.onclose = () => {
                this.isConnected = false;
                this.updateConnectionStatus('disconnected');
                this.log('🔌 WebSocket接続切断');
            };
            
            this.websocket.onerror = (error) => {
                this.log(`❌ WebSocketエラー: ${error}`, 'error');
            };
            
        } catch (error) {
            this.log(`❌ WebSocket接続エラー: ${error.message}`, 'error');
        }
    }
    
    disconnectWebSocket() {
        if (this.websocket) {
            this.websocket.close();
            this.websocket = null;
        }
        this.isConnected = false;
        this.updateConnectionStatus('disconnected');
        this.battleState = 'idle';
        this.resetBattleUI();
    }
    
    updateConnectionStatus(status) {
        const statusDot = document.querySelector('#connectionStatus .status-dot');
        const statusText = document.getElementById('statusText');
        const connectBtn = document.getElementById('connectBtn');
        const disconnectBtn = document.getElementById('disconnectBtn');
        
        statusDot.className = `status-dot ${status}`;
        
        switch (status) {
            case 'connected':
                statusText.textContent = '接続済み';
                connectBtn.style.display = 'none';
                disconnectBtn.style.display = 'inline-block';
                break;
            case 'disconnected':
                statusText.textContent = '未接続';
                connectBtn.style.display = 'inline-block';
                disconnectBtn.style.display = 'none';
                break;
            case 'matching':
                statusText.textContent = 'マッチング中';
                break;
            case 'battling':
                statusText.textContent = '対戦中';
                break;
        }
    }
    
    // ==================== バトル機能 ====================
    
    startMatching() {
        if (!this.isConnected) {
            this.log('❌ WebSocketに接続してください', 'error');
            return;
        }
        
        if (this.battleState !== 'idle') {
            this.log('❌ 既にバトル中です', 'error');
            return;
        }
        
        this.battleState = 'matching';
        this.updateConnectionStatus('matching');
        this.showMatchingInfo();
        
        // マッチング開始メッセージ送信
        this.sendWebSocketMessage({
            type: 'start_matching',
            user_id: this.currentUser.user_id
        });
        
        this.log('🔍 マッチング開始');
    }
    
    cancelMatching() {
        this.battleState = 'idle';
        this.updateConnectionStatus('connected');
        this.hideMatchingInfo();
        
        this.sendWebSocketMessage({
            type: 'cancel_matching',
            user_id: this.currentUser.user_id
        });
        
        this.log('❌ マッチングキャンセル');
    }
    
    selectHand(hand) {
        this.selectedHand = hand;
        document.getElementById('handStatus').textContent = `選択済み: ${this.getHandDisplayName(hand)}`;
        
        // 手選択ボタンの状態更新
        document.querySelectorAll('.hand-btn').forEach(btn => {
            btn.classList.remove('selected');
            if (btn.dataset.hand === hand) {
                btn.classList.add('selected');
            }
        });
        
        this.log(`✋ 手を選択: ${this.getHandDisplayName(hand)}`);
    }
    
    sendReady() {
        if (!this.selectedHand) {
            this.log('❌ 手を選択してください', 'error');
            return;
        }
        
        this.sendWebSocketMessage({
            type: 'ready',
            user_id: this.currentUser.user_id,
            hand: this.selectedHand
        });
        
        this.log('✅ 準備完了を送信');
    }
    
    nextRound() {
        this.battleState = 'battling';
        this.hideBattleResult();
        this.showHandSelection();
        this.selectedHand = null;
        this.log('🔄 次のラウンド開始');
    }
    
    newBattle() {
        this.battleState = 'idle';
        this.resetBattleUI();
        this.log('🆕 新しい対戦を開始');
    }
    
    quitBattle() {
        this.battleState = 'idle';
        this.resetBattleUI();
        this.log('🏁 対戦終了');
    }
    
    // ==================== WebSocketメッセージ処理 ====================
    
    handleWebSocketMessage(data) {
        this.log(`📨 WebSocket受信: ${data.type}`);
        
        switch (data.type) {
            case 'matching_started':
                this.handleMatchingStarted(data);
                break;
            case 'opponent_found':
                this.handleOpponentFound(data);
                break;
            case 'battle_start':
                this.handleBattleStart(data);
                break;
            case 'round_result':
                this.handleRoundResult(data);
                break;
            case 'battle_result':
                this.handleBattleResult(data);
                break;
            case 'error':
                this.log(`❌ WebSocketエラー: ${data.message}`, 'error');
                break;
            default:
                this.log(`❓ 未知のメッセージタイプ: ${data.type}`);
        }
    }
    
    handleMatchingStarted(data) {
        this.log(`🔍 マッチング開始: キュー位置 ${data.queue_position || '不明'}`);
        // キュー位置表示の更新
        if (data.queue_position) {
            document.getElementById('queuePosition').textContent = data.queue_position;
        }
    }
    
    handleOpponentFound(data) {
        this.battleState = 'battling';
        this.currentBattle = data.battle_id;
        this.hideMatchingInfo();
        this.showOpponentInfo(data.opponent);
        this.log(`👤 対戦相手発見: ${data.opponent.nickname}`);
    }
    
    handleBattleStart(data) {
        this.showHandSelection();
        this.log('⚔️ バトル開始');
    }
    
    handleRoundResult(data) {
        this.hideHandSelection();
        this.showRoundResult(data);
        this.log(`📊 ラウンド結果: ${data.result}`);
    }
    
    handleBattleResult(data) {
        this.battleState = 'result';
        this.showBattleResult(data);
        this.log(`🏆 バトル終了: ${data.winner_id === this.currentUser.user_id ? '勝利' : '敗北'}`);
        
        // 統計データ更新
        setTimeout(() => this.loadUserStats(), 1000);
    }
    
    // ==================== UI制御 ====================
    
    showMatchingInfo() {
        document.getElementById('matchingInfo').style.display = 'block';
        document.getElementById('startMatchingBtn').style.display = 'none';
    }
    
    hideMatchingInfo() {
        document.getElementById('matchingInfo').style.display = 'none';
        document.getElementById('startMatchingBtn').style.display = 'inline-block';
    }
    
    showOpponentInfo(opponent) {
        document.getElementById('opponentName').textContent = opponent.nickname || opponent.user_id;
        document.getElementById('opponentId').textContent = opponent.user_id;
        document.getElementById('opponentLevel').textContent = opponent.level || '不明';
        document.getElementById('opponentInfo').style.display = 'block';
        document.getElementById('readyBtn').style.display = 'inline-block';
    }
    
    showHandSelection() {
        document.getElementById('handSelection').style.display = 'block';
        document.getElementById('readyBtn').style.display = 'none';
    }
    
    hideHandSelection() {
        document.getElementById('handSelection').style.display = 'none';
    }
    
    showRoundResult(data) {
        // ラウンド結果表示（簡易版）
        this.log(`📊 ラウンド結果: あなた(${this.getHandDisplayName(data.your_hand)}) vs 相手(${this.getHandDisplayName(data.opponent_hand)})`);
    }
    
    showBattleResult(data) {
        const yourHand = document.getElementById('yourHand');
        const opponentHand = document.getElementById('opponentHand');
        const yourResult = document.getElementById('yourResult');
        const opponentResult = document.getElementById('opponentResult');
        const resultTitle = document.getElementById('resultTitle');
        
        // 手の表示
        yourHand.textContent = this.getHandDisplayName(data.your_hand);
        opponentHand.textContent = this.getHandDisplayName(data.opponent_hand);
        
        // 結果表示
        const isWinner = data.winner_id === this.currentUser.user_id;
        if (isWinner) {
            resultTitle.textContent = '🎉 勝利！';
            yourResult.textContent = '勝';
            opponentResult.textContent = '負';
            yourResult.className = 'result-badge result-win';
            opponentResult.className = 'result-badge result-lose';
        } else {
            resultTitle.textContent = '😢 敗北...';
            yourResult.textContent = '負';
            opponentResult.textContent = '勝';
            yourResult.className = 'result-badge result-lose';
            opponentResult.className = 'result-badge result-win';
        }
        
        // 次のアクションボタン表示
        if (data.total_rounds > 1) {
            document.getElementById('nextRoundBtn').style.display = 'inline-block';
        }
        document.getElementById('newBattleBtn').style.display = 'inline-block';
        
        document.getElementById('battleResult').style.display = 'block';
    }
    
    hideBattleResult() {
        document.getElementById('battleResult').style.display = 'none';
    }
    
    showBattleSection() {
        document.getElementById('battleSection').style.display = 'block';
    }
    
    hideBattleSection() {
        document.getElementById('battleSection').style.display = 'none';
    }
    
    resetBattleUI() {
        this.hideMatchingInfo();
        this.hideHandSelection();
        this.hideBattleResult();
        document.getElementById('opponentInfo').style.display = 'none';
        document.getElementById('startMatchingBtn').style.display = 'inline-block';
        document.getElementById('nextRoundBtn').style.display = 'none';
        document.getElementById('newBattleBtn').style.display = 'none';
        
        // 手選択ボタンのリセット
        document.querySelectorAll('.hand-btn').forEach(btn => {
            btn.classList.remove('selected');
        });
        
        document.getElementById('handStatus').textContent = '手を選択してください';
    }
    
    // ==================== ユーティリティ ====================
    
    getHandDisplayName(hand) {
        const handNames = {
            'rock': '✊ グー',
            'scissors': '✌️ チョキ',
            'paper': '✋ パー'
        };
        return handNames[hand] || hand;
    }
    
    sendWebSocketMessage(data) {
        if (this.websocket && this.isConnected) {
            this.websocket.send(JSON.stringify(data));
        } else {
            this.log('❌ WebSocketが接続されていません', 'error');
        }
    }
    
    refreshUserStats() {
        this.loadUserStats();
        this.loadBattleHistory();
    }
    
    debugReset() {
        this.log('🔄 デバッグ: 状態リセット実行');
        this.battleState = 'idle';
        this.selectedHand = null;
        this.currentBattle = null;
        this.resetBattleUI();
        this.log('✅ 状態リセット完了');
    }
    
    // ==================== ログ機能 ====================
    
    log(message, type = 'info') {
        const logContainer = document.getElementById('logMessages');
        const timestamp = new Date().toLocaleTimeString();
        const logClass = type === 'error' ? 'log-error' : 'log-info';
        
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry ${logClass}`;
        logEntry.innerHTML = `<span class="log-time">[${timestamp}]</span> ${message}`;
        
        logContainer.appendChild(logEntry);
        
        // 自動スクロール
        if (document.getElementById('autoScrollLog').checked) {
            logContainer.scrollTop = logContainer.scrollHeight;
        }
        
        // コンソールにも出力
        console.log(`[${timestamp}] ${message}`);
    }
    
    clearLog() {
        document.getElementById('logMessages').innerHTML = '';
        this.log('📋 ログをクリアしました');
    }
}

// ページ読み込み完了後に初期化
document.addEventListener('DOMContentLoaded', () => {
    window.dbBattleGame = new DBBattleGame();
});
