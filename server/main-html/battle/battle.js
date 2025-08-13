/**
 * じゃんけんバトル テストページ JavaScript
 * 
 * WebSocket接続とバトルロジックを管理
 */

class JankenBattleClient {
    constructor() {
        // 状態管理
        this.currentUser = null;
        this.jwtToken = null;
        this.websocket = null;
        this.currentBattle = null;
        this.connectionStatus = 'disconnected';
        
        // 設定
        this.config = {
            apiBase: window.location.protocol.replace('http', 'ws') + '//' + window.location.host,
            httpApiBase: window.location.origin
        };
        
        // 初期化
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.checkExistingAuth();
        this.log('info', 'じゃんけんバトルクライアント初期化完了');
    }
    
    setupEventListeners() {
        // ログイン関連
        document.getElementById('devLoginBtn').addEventListener('click', () => {
            this.handleDevLogin();
        });
        
        document.getElementById('magicLinkBtn').addEventListener('click', () => {
            this.handleMagicLinkRequest();
        });
        
        document.getElementById('logoutBtn').addEventListener('click', () => {
            this.logout();
        });
        
        // WebSocket接続
        document.getElementById('connectBtn').addEventListener('click', () => {
            this.connectWebSocket();
        });
        
        document.getElementById('disconnectBtn').addEventListener('click', () => {
            this.disconnectWebSocket();
        });
        
        // バトル関連
        document.getElementById('startMatchingBtn').addEventListener('click', () => {
            this.startMatching();
        });
        
        document.getElementById('cancelMatchingBtn').addEventListener('click', () => {
            this.cancelMatching();
        });
        
        document.getElementById('readyBtn').addEventListener('click', () => {
            this.setReady();
        });
        
        document.getElementById('quitBattleBtn').addEventListener('click', () => {
            this.quitBattle();
        });
        
        document.getElementById('nextRoundBtn').addEventListener('click', () => {
            this.resetHands();
        });
        
        document.getElementById('newBattleBtn').addEventListener('click', () => {
            this.startNewBattle();
        });
        
        document.getElementById('debugResetBtn').addEventListener('click', () => {
            this.debugReset();
        });
        
        // 統計・ランキング関連
        document.getElementById('loadStatsBtn')?.addEventListener('click', () => {
            this.loadUserStats();
        });
        
        document.getElementById('loadRankingBtn')?.addEventListener('click', () => {
            this.loadDailyRanking();
        });
        
        // 手選択
        document.querySelectorAll('.hand-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const hand = e.currentTarget.dataset.hand;
                this.selectHand(hand);
            });
        });
        
        // ログ関連
        document.getElementById('clearLogBtn').addEventListener('click', () => {
            this.clearLog();
        });
    }
    
    // =====================
    // 認証関連
    // =====================
    
    checkExistingAuth() {
        const token = localStorage.getItem('janken_jwt_token');
        const user = localStorage.getItem('janken_user_info');
        
        if (token && user) {
            try {
                this.jwtToken = token;
                this.currentUser = JSON.parse(user);
                this.showLoggedInState();
                this.log('success', `既存の認証情報で自動ログイン: ${this.currentUser.nickname}`);
            } catch (e) {
                this.log('error', '保存された認証情報が無効です');
                this.logout();
            }
        }
    }
    
    async handleDevLogin() {
        const userId = document.getElementById('devUserSelect').value;
        if (!userId) {
            alert('テストユーザーを選択してください');
            return;
        }
        
        let data = null;
        try {
            this.log('info', `開発用ログイン試行: User${userId}`);
            
            // Laravel風新APIのテストユーザーログインAPIを呼び出し
            const response = await fetch(`${this.config.httpApiBase}/api/auth/test-login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    user_number: parseInt(userId)  // サーバー側のスキーマに合わせる
                })
            });
            
            data = await response.json();
            this.log('info', `テストログインレスポンス:`, data);
            
            if (data.success && data.data) {
                // Laravel風新APIのレスポンス形式に対応
                this.jwtToken = data.data.token;  // 統一されたtoken構造
                this.currentUser = {
                    id: data.data.user.user_id,  // サーバーから返されたuser_idを使用
                    nickname: data.data.user.nickname,
                    email: data.data.user.email
                };
                
                // 認証情報を保存
                localStorage.setItem('janken_jwt_token', this.jwtToken);
                localStorage.setItem('janken_user_info', JSON.stringify(this.currentUser));
                
                this.showLoggedInState();
                this.log('success', `開発用ログイン成功: ${this.currentUser.nickname}`);
                
                // ユーザー統計を取得・表示
                await this.loadUserStats();
            } else {
                throw new Error(data.message || data.error?.details || '認証に失敗しました');
            }
        } catch (error) {
            this.log('error', `開発用ログインエラー: ${error.message}`);
            this.log('error', `詳細レスポンス:`, data || 'レスポンスなし');
            alert(`ログインエラー: ${error.message}`);
        }
    }
    
    async handleMagicLinkRequest() {
        const email = document.getElementById('emailInput').value;
        if (!email) {
            alert('メールアドレスを入力してください');
            return;
        }
        
        try {
            this.log('info', `Magic Link送信試行: ${email}`);
            
            const response = await fetch(`${this.config.httpApiBase}/api/auth/request-magic-link`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    email: email
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                alert('Magic Linkを送信しました。メールを確認してください。');
                this.log('success', `Magic Link送信完了: ${email}`);
                
                // デバッグ用: Magic Link URLをログに表示
                if (data.data && data.data.token) {
                    this.log('info', `Magic Link Token: ${data.data.token}`);
                }
            } else {
                throw new Error(data.message || 'Magic Link送信に失敗しました');
            }
        } catch (error) {
            this.log('error', `Magic Link送信エラー: ${error.message}`);
            alert(`Magic Link送信エラー: ${error.message}`);
        }
    }
    
    logout() {
        this.jwtToken = null;
        this.currentUser = null;
        localStorage.removeItem('janken_jwt_token');
        localStorage.removeItem('janken_user_info');
        
        // WebSocket切断
        this.disconnectWebSocket();
        
        this.showLoggedOutState();
        this.log('info', 'ログアウトしました');
    }
    
    showLoggedInState() {
        document.getElementById('loginSection').style.display = 'none';
        document.getElementById('battleSection').style.display = 'block';
        document.getElementById('userDisplay').textContent = this.currentUser.nickname;
        document.getElementById('logoutBtn').style.display = 'inline-block';
    }
    
    showLoggedOutState() {
        document.getElementById('loginSection').style.display = 'block';
        document.getElementById('battleSection').style.display = 'none';
        document.getElementById('userDisplay').textContent = '未ログイン';
        document.getElementById('logoutBtn').style.display = 'none';
        
        // UI状態リセット
        this.resetUI();
    }
    
    // =====================
    // WebSocket接続管理
    // =====================
    
    connectWebSocket() {
        if (!this.currentUser) {
            alert('先にログインしてください');
            return;
        }
        
        if (this.websocket) {
            this.log('warning', '既にWebSocketが接続されています');
            return;
        }
        
        try {
            const wsUrl = `${this.config.apiBase}/api/battle/ws/${this.currentUser.id}`;
            this.log('info', `WebSocket接続試行: ${wsUrl}`);
            
            this.websocket = new WebSocket(wsUrl);
            this.setupWebSocketHandlers();
            this.updateConnectionStatus('connecting');
            
        } catch (error) {
            this.log('error', `WebSocket接続エラー: ${error.message}`);
            this.updateConnectionStatus('disconnected');
        }
    }
    
    setupWebSocketHandlers() {
        this.websocket.onopen = () => {
            this.log('success', 'WebSocket接続確立');
            this.updateConnectionStatus('connected');
        };
        
        this.websocket.onmessage = (event) => {
            try {
                const message = JSON.parse(event.data);
                this.handleWebSocketMessage(message);
            } catch (error) {
                this.log('error', `メッセージパースエラー: ${error.message}`);
            }
        };
        
        this.websocket.onclose = () => {
            this.log('warning', 'WebSocket接続が閉じられました');
            this.updateConnectionStatus('disconnected');
            this.websocket = null;
        };
        
        this.websocket.onerror = (error) => {
            this.log('error', `WebSocketエラー: ${error.message || 'Unknown error'}`);
            this.updateConnectionStatus('disconnected');
        };
    }
    
    disconnectWebSocket() {
        if (this.websocket) {
            this.websocket.close();
            this.websocket = null;
            this.updateConnectionStatus('disconnected');
            this.log('info', 'WebSocket接続を切断しました');
        }
    }
    
    updateConnectionStatus(status) {
        this.connectionStatus = status;
        const statusElement = document.getElementById('connectionStatus');
        const statusText = document.getElementById('statusText');
        const connectBtn = document.getElementById('connectBtn');
        const disconnectBtn = document.getElementById('disconnectBtn');
        
        const statusDot = statusElement.querySelector('.status-dot');
        statusDot.className = 'status-dot';
        
        switch (status) {
            case 'connected':
                statusDot.classList.add('online');
                statusText.textContent = '接続中';
                connectBtn.style.display = 'none';
                disconnectBtn.style.display = 'inline-block';
                break;
            case 'connecting':
                statusDot.classList.add('connecting');
                statusText.textContent = '接続中...';
                connectBtn.style.display = 'none';
                disconnectBtn.style.display = 'none';
                break;
            case 'disconnected':
            default:
                statusDot.classList.add('offline');
                statusText.textContent = '未接続';
                connectBtn.style.display = 'inline-block';
                disconnectBtn.style.display = 'none';
                break;
        }
    }
    
    // =====================
    // WebSocketメッセージ処理
    // =====================
    
    handleWebSocketMessage(message) {
        this.log('info', `受信: ${message.type}`, message);
        
        const handlers = {
            'connection_established': this.onConnectionEstablished.bind(this),
            'matching_started': this.onMatchingStarted.bind(this),
            'matching_status': this.onMatchingStatus.bind(this),
            'match_found': this.onMatchFound.bind(this),
            'battle_ready_status': this.onBattleReadyStatus.bind(this),
            'battle_start': this.onBattleStart.bind(this),
            'hand_submitted': this.onHandSubmitted.bind(this),
            'battle_result': this.onBattleResult.bind(this),
            'battle_draw': this.onBattleDraw.bind(this),
            'hands_reset': this.onHandsReset.bind(this),
            'battle_quit_confirmed': this.onBattleQuitConfirmed.bind(this),
            'opponent_quit': this.onOpponentQuit.bind(this),
            'error': this.onError.bind(this),
            'pong': this.onPong.bind(this)
        };
        
        const handler = handlers[message.type];
        if (handler) {
            handler(message.data);
        } else {
            this.log('warning', `未処理のメッセージタイプ: ${message.type}`);
        }
    }
    
    onConnectionEstablished(data) {
        this.log('success', `接続確立: ${data.sessionId}`);
        if (data.nickname) {
            this.currentUser.nickname = data.nickname;
            document.getElementById('userDisplay').textContent = data.nickname;
        }
        this.updateStatus('接続完了', 'マッチング開始ボタンを押して対戦を始めてください');
    }
    
    onMatchingStarted(data) {
        this.log('success', `マッチング開始: ${data.matchingId}`);
        this.updateStatus('マッチング中', '対戦相手を探しています...');
        this.showMatchingInfo();
    }
    
    onMatchingStatus(data) {
        this.log('info', `マッチング状況更新 - 位置: ${data.queuePosition}, 待ち時間: ${data.estimatedWaitTime}秒`);
        this.updateMatchingDisplay(data.queuePosition, data.estimatedWaitTime);
    }
    
    onMatchFound(data) {
        this.currentBattle = data;
        this.log('success', `対戦相手発見: ${data.opponent.nickname}`);
        this.updateStatus('対戦相手発見', `${data.opponent.nickname}との対戦が成立しました`);
        this.showOpponentInfo(data.opponent);
        this.hideMatchingInfo();
    }
    
    onBattleReadyStatus(data) {
        this.log('info', `準備状況 - P1: ${data.player1Ready}, P2: ${data.player2Ready}`);
        this.updateReadyStatus(data);
    }
    
    onBattleStart(data) {
        this.log('success', '対戦開始！');
        this.updateStatus('対戦中', '手を選択してください');
        this.showHandSelection();
        this.hideOpponentReady();
    }
    
    onHandSubmitted(data) {
        this.log('success', '手送信完了');
        this.updateStatus('手送信済み', data.waitingForOpponent ? '相手の手を待っています...' : '結果判定中...');
        this.disableHandSelection();
    }
    
    onBattleResult(data) {
        this.log('success', '対戦結果受信');
        this.updateStatus('対戦終了', '結果を確認してください');
        this.showBattleResult(data.result);
        this.hideHandSelection();
    }
    
    onBattleDraw(data) {
        this.log('info', '引き分け！');
        this.updateStatus('引き分け', 'もう一度手を選択してください');
        this.showDrawResult(data.result);
        // 自動で手をリセット
        setTimeout(() => {
            this.resetHands();
        }, 3000);
    }
    
    onHandsReset(data) {
        this.log('info', '手リセット完了');
        this.updateStatus('手選択', '再度手を選択してください');
        this.resetHandSelection();
        this.hideBattleResult();
    }
    
    onBattleQuitConfirmed(data) {
        this.log('info', '対戦辞退確認');
        this.updateStatus('対戦終了', '対戦を辞退しました');
        this.resetBattleState();
    }
    
    onOpponentQuit(data) {
        this.log('warning', '相手が対戦を辞退しました');
        this.updateStatus('対戦終了', '相手が対戦を辞退しました');
        this.resetBattleState();
    }
    
    onError(data) {
        const error = data.error || {};
        this.log('error', `エラー: ${error.code} - ${error.message}`);
        alert(`エラー: ${error.message || '不明なエラーが発生しました'}`);
    }
    
    onPong(data) {
        this.log('info', 'Pong受信', data);
    }
    
    // =====================
    // WebSocketメッセージ送信
    // =====================
    
    sendMessage(type, data = {}) {
        if (!this.websocket || this.websocket.readyState !== WebSocket.OPEN) {
            this.log('error', 'WebSocketが接続されていません');
            return false;
        }
        
        const message = {
            type: type,
            data: data,
            timestamp: new Date().toISOString(),
            messageId: this.generateUUID()
        };
        
        this.websocket.send(JSON.stringify(message));
        this.log('info', `送信: ${type}`, message);
        return true;
    }
    
    // =====================
    // バトル操作
    // =====================
    
    startMatching() {
        if (!this.sendMessage('matching_start', {
            userId: this.currentUser.id
        })) {
            alert('WebSocketに接続してください');
        }
    }
    
    cancelMatching() {
        // TODO: マッチングキャンセル機能実装
        this.log('warning', 'マッチングキャンセル機能は未実装です');
    }
    
    setReady() {
        if (!this.currentBattle) {
            this.log('error', 'バトル情報がありません');
            return;
        }
        
        this.sendMessage('battle_ready', {
            battleId: this.currentBattle.battleId,
            userId: this.currentUser.id
        });
    }
    
    selectHand(hand) {
        if (!this.currentBattle) {
            this.log('error', 'バトル情報がありません');
            return;
        }
        
        this.sendMessage('submit_hand', {
            battleId: this.currentBattle.battleId,
            userId: this.currentUser.id,
            hand: hand
        });
        
        // UI更新
        document.querySelectorAll('.hand-btn').forEach(btn => {
            btn.classList.remove('selected');
            if (btn.dataset.hand === hand) {
                btn.classList.add('selected');
            }
        });
    }
    
    resetHands() {
        if (!this.currentBattle) {
            this.log('error', 'バトル情報がありません');
            return;
        }
        
        this.sendMessage('reset_hands', {
            battleId: this.currentBattle.battleId
        });
    }
    
    quitBattle() {
        if (!this.currentBattle) {
            this.log('error', 'バトル情報がありません');
            return;
        }
        
        if (confirm('対戦を辞退しますか？')) {
            this.sendMessage('battle_quit', {
                battleId: this.currentBattle.battleId,
                userId: this.currentUser.id,
                reason: 'user_action'
            });
        }
    }
    
    startNewBattle() {
        this.resetBattleState();
        this.startMatching();
    }
    
    async debugReset() {
        try {
            this.log('warning', 'デバッグリセット実行中...');
            
            const response = await fetch(`${this.config.httpApiBase}/api/battle/debug/reset-user/${this.currentUser.id}`, {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.log('success', 'デバッグリセット完了');
                this.resetBattleState();
                this.resetUI();
            } else {
                this.log('error', 'デバッグリセット失敗');
            }
        } catch (error) {
            this.log('error', `デバッグリセットエラー: ${error.message}`);
        }
    }
    
    // =====================
    // UI更新メソッド
    // =====================
    
    updateStatus(title, message) {
        document.getElementById('statusTitle').textContent = title;
        document.getElementById('statusMessage').textContent = message;
    }
    
    showMatchingInfo() {
        document.getElementById('matchingInfo').style.display = 'block';
        document.getElementById('startMatchingBtn').style.display = 'none';
    }
    
    hideMatchingInfo() {
        document.getElementById('matchingInfo').style.display = 'none';
        document.getElementById('startMatchingBtn').style.display = 'inline-block';
    }
    
    updateMatchingDisplay(position, waitTime) {
        document.getElementById('queuePosition').textContent = position;
        document.getElementById('estimatedWait').textContent = waitTime;
    }
    
    showOpponentInfo(opponent) {
        document.getElementById('opponentInfo').style.display = 'block';
        document.getElementById('opponentName').textContent = opponent.nickname;
        document.getElementById('opponentId').textContent = opponent.userId;
        document.getElementById('readyBtn').style.display = 'inline-block';
    }
    
    hideOpponentReady() {
        document.getElementById('readyBtn').style.display = 'none';
    }
    
    updateReadyStatus(status) {
        // TODO: 準備状況の詳細表示
    }
    
    showHandSelection() {
        document.getElementById('handSelection').style.display = 'block';
        this.enableHandSelection();
    }
    
    hideHandSelection() {
        document.getElementById('handSelection').style.display = 'none';
    }
    
    enableHandSelection() {
        document.querySelectorAll('.hand-btn').forEach(btn => {
            btn.classList.remove('disabled', 'selected');
            btn.disabled = false;
        });
        document.getElementById('handStatus').textContent = '手を選択してください';
    }
    
    disableHandSelection() {
        document.querySelectorAll('.hand-btn').forEach(btn => {
            btn.classList.add('disabled');
            btn.disabled = true;
        });
        document.getElementById('handStatus').textContent = '相手の手を待っています...';
    }
    
    resetHandSelection() {
        this.enableHandSelection();
    }
    
    showBattleResult(result) {
        document.getElementById('battleResult').style.display = 'block';
        
        // 手の絵文字マッピング
        const handEmojis = {
            rock: '✊',
            scissors: '✌️',
            paper: '✋'
        };
        
        // 自分の結果
        const isPlayer1 = this.currentBattle.playerNumber === 1;
        const myResult = isPlayer1 ? result.player1 : result.player2;
        const opResult = isPlayer1 ? result.player2 : result.player1;
        
        document.getElementById('yourHand').textContent = handEmojis[myResult.hand];
        document.getElementById('opponentHand').textContent = handEmojis[opResult.hand];
        
        // 結果バッジ
        const yourResultBadge = document.getElementById('yourResult');
        const opponentResultBadge = document.getElementById('opponentResult');
        
        yourResultBadge.textContent = this.getResultText(myResult.result);
        yourResultBadge.className = `result-badge ${myResult.result}`;
        
        opponentResultBadge.textContent = this.getResultText(opResult.result);
        opponentResultBadge.className = `result-badge ${opResult.result}`;
        
        // タイトル
        const resultTitle = document.getElementById('resultTitle');
        if (result.isDraw) {
            resultTitle.textContent = '引き分け！';
        } else if (myResult.result === 'win') {
            resultTitle.textContent = '勝利！';
        } else {
            resultTitle.textContent = '敗北...';
        }
        
        // アクションボタン
        if (result.isFinished) {
            document.getElementById('newBattleBtn').style.display = 'inline-block';
            document.getElementById('nextRoundBtn').style.display = 'none';
        } else {
            document.getElementById('newBattleBtn').style.display = 'none';
            document.getElementById('nextRoundBtn').style.display = 'inline-block';
        }
    }
    
    showDrawResult(result) {
        this.showBattleResult(result);
    }
    
    hideBattleResult() {
        document.getElementById('battleResult').style.display = 'none';
    }
    
    getResultText(result) {
        const texts = {
            win: '勝利',
            lose: '敗北',
            draw: '引き分け'
        };
        return texts[result] || result;
    }
    
    resetBattleState() {
        this.currentBattle = null;
        this.hideMatchingInfo();
        document.getElementById('opponentInfo').style.display = 'none';
        this.hideHandSelection();
        this.hideBattleResult();
        this.updateStatus('接続完了', 'マッチング開始ボタンを押して対戦を始めてください');
    }
    
    resetUI() {
        this.resetBattleState();
    }
    
    // =====================
    // ログ管理
    // =====================
    
    log(level, message, data = null) {
        const timestamp = new Date().toLocaleTimeString();
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry ${level}`;
        
        const logTimestamp = document.createElement('div');
        logTimestamp.className = 'log-timestamp';
        logTimestamp.textContent = timestamp;
        
        const logMessage = document.createElement('div');
        logMessage.className = 'log-message';
        logMessage.textContent = message;
        
        if (data) {
            const logData = document.createElement('div');
            logData.className = 'log-data';
            logData.style.fontSize = '11px';
            logData.style.opacity = '0.8';
            logData.style.marginTop = '2px';
            logData.textContent = JSON.stringify(data, null, 2);
            logMessage.appendChild(logData);
        }
        
        logEntry.appendChild(logTimestamp);
        logEntry.appendChild(logMessage);
        
        const logContainer = document.getElementById('logMessages');
        logContainer.appendChild(logEntry);
        
        // 自動スクロール
        if (document.getElementById('autoScrollLog').checked) {
            logContainer.scrollTop = logContainer.scrollHeight;
        }
        
        // ログ制限（最新100件）
        while (logContainer.children.length > 100) {
            logContainer.removeChild(logContainer.firstChild);
        }
        
        // コンソールにも出力
        console.log(`[${level.toUpperCase()}] ${message}`, data || '');
    }
    
    clearLog() {
        document.getElementById('logMessages').innerHTML = '';
        this.log('info', 'ログをクリアしました');
    }
    
    // =====================
    // ユーティリティ
    // =====================
    
    generateUUID() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            const r = Math.random() * 16 | 0;
            const v = c == 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }
    
    // =====================
    // ユーザー統計機能
    // =====================
    
    async loadUserStats() {
        // ユーザー統計情報を読み込んで表示
        if (!this.currentUser) return;
        
        try {
            const response = await fetch(`${this.config.httpApiBase}/api/battle/user/${this.currentUser.id}/stats`);
            const data = await response.json();
            
            if (data.success) {
                this.displayUserStats(data.data);
                this.log('info', 'ユーザー統計を取得しました', data.data);
            } else {
                this.log('warning', `統計取得失敗: ${data.error?.message || 'Unknown error'}`);
            }
        } catch (error) {
            this.log('error', `統計取得エラー: ${error.message}`);
        }
    }
    
    displayUserStats(stats) {
        // ユーザー統計をUIに表示
        // ユーザー情報表示エリアに統計を追加
        const userInfo = document.getElementById('userInfo');
        
        // 既存の統計表示があれば削除
        const existingStats = userInfo.querySelector('.user-stats');
        if (existingStats) {
            existingStats.remove();
        }
        
        // 統計表示要素を作成
        const statsElement = document.createElement('div');
        statsElement.className = 'user-stats';
        statsElement.innerHTML = `
            <div class="stats-summary">
                <span class="stat-item">勝率: ${stats.win_rate.toFixed(1)}%</span>
                <span class="stat-item">ランク: ${this.getRankDisplayName(stats.user_rank)}</span>
                <span class="stat-item">レート: ${stats.rank_points}</span>
                <span class="stat-item">連勝: ${stats.current_win_streak}</span>
            </div>
        `;
        
        userInfo.appendChild(statsElement);
    }
    
    getRankDisplayName(rank) {
        // ランク名を日本語表示に変換
        const rankNames = {
            'bronze': 'ブロンズ',
            'silver': 'シルバー', 
            'gold': 'ゴールド',
            'platinum': 'プラチナ',
            'diamond': 'ダイヤモンド'
        };
        return rankNames[rank] || rank;
    }
    
    async loadDailyRanking() {
        // デイリーランキングを取得して表示
        try {
            const response = await fetch(`${this.config.httpApiBase}/api/battle/ranking/daily?limit=10`);
            const data = await response.json();
            
            if (data.success) {
                this.displayRanking(data.data.ranking);
                this.log('info', 'デイリーランキングを取得しました');
            } else {
                this.log('warning', `ランキング取得失敗: ${data.error?.message}`);
            }
        } catch (error) {
            this.log('error', `ランキング取得エラー: ${error.message}`);
        }
    }
    
    displayRanking(ranking) {
        // ランキングをログに表示（簡易版）
        if (ranking && ranking.length > 0) {
            const rankingText = ranking.slice(0, 5).map((rank, index) => 
                `${index + 1}位: ${rank.user_id} (${rank.daily_wins}勝)`
            ).join(', ');
            
            this.log('info', `本日のランキング TOP5: ${rankingText}`);
        }
    }
}

// アプリケーション初期化
document.addEventListener('DOMContentLoaded', () => {
    window.jankenClient = new JankenBattleClient();
});