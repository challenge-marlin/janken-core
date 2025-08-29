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
            apiBase: 'ws://localhost:3000',  // デフォルトWebSocket URL
            httpApiBase: 'http://localhost:3000'  // デフォルトHTTP URL
        };
        
        // 初期化
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.checkExistingAuth();
        this.initializeConfig();
        this.log('info', 'じゃんけんバトルクライアント初期化完了');
    }
    
    initializeConfig() {
        // 環境設定の初期化
        const select = document.getElementById('apiBaseUrl');
        if (select) {
            select.value = 'http://localhost:3000';  // デフォルト値を設定
            this.updateApiBaseUrl();
        }
    }
    
    setupEventListeners() {
        // ログイン関連
        document.getElementById('devLoginBtn').addEventListener('click', () => {
            this.handleDevLogin();
        });
        

        
        document.getElementById('logoutBtn').addEventListener('click', () => {
            this.logout();
        });
        
        // 環境設定関連
        document.getElementById('apiBaseUrl').addEventListener('change', (e) => {
            if (e.target.value === 'custom') {
                document.getElementById('customUrlGroup').style.display = 'block';
            } else {
                document.getElementById('customUrlGroup').style.display = 'none';
            }
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
        const userNumber = document.getElementById('devUserSelect').value;
        if (!userNumber) {
            alert('テストユーザーを選択してください');
            return;
        }
        
        let data = null;
        try {
            this.log('info', `開発用ログイン試行: テストユーザー${userNumber}`);
            this.log('info', `API URL: ${this.config.httpApiBase}/api/auth/test-login`);
            
            // Laravel風新APIのテストユーザーログインAPIを呼び出し
            const response = await fetch(`${this.config.httpApiBase}/api/auth/test-login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    user_number: parseInt(userNumber)  // サーバー側のスキーマに合わせる
                })
            });
            
            this.log('info', `HTTP Status: ${response.status} ${response.statusText}`);
            
            // レスポンスの内容を確認
            const responseText = await response.text();
            this.log('info', `レスポンス本文: ${responseText.substring(0, 200)}...`);
            
            try {
                data = JSON.parse(responseText);
                this.log('info', `テストログインレスポンス:`, data);
            } catch (parseError) {
                this.log('error', `JSONパースエラー: ${parseError.message}`);
                this.log('error', `レスポンス本文: ${responseText}`);
                throw new Error(`サーバーから無効なレスポンスが返されました: ${responseText.substring(0, 100)}...`);
            }
            
            if (data.success && data.data) {
                // サーバー側のレスポンス形式に対応
                this.jwtToken = data.data.token;  // JWTトークン
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
                
                // ユーザー統計を取得・表示（一時的に無効化）
                // await this.loadUserStats();
                this.log('info', '統計取得は一時的に無効化されています');
            } else {
                throw new Error(data.message || data.error?.details || '認証に失敗しました');
            }
        } catch (error) {
            this.log('error', `開発用ログインエラー: ${error.message}`);
            this.log('error', `詳細レスポンス:`, data || 'レスポンスなし');
            alert(`ログインエラー: ${error.message}`);
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
        
        // 接続状態を初期化（接続ボタンを有効化）
        this.updateConnectionStatus('disconnected');
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
        
        if (!this.jwtToken) {
            alert('JWTトークンがありません。先にログインしてください。');
            return;
        }
        
        if (this.websocket) {
            this.log('warning', '既にWebSocketが接続されています');
            return;
        }
        
        this.attemptWebSocketConnection();
    }

    attemptWebSocketConnection() {
        try {
            // WebSocket URL（ユーザーIDをURLパラメータに含める）
            const wsUrl = `${this.config.apiBase}/api/battle/ws/${this.currentUser.id}`;
            this.log('info', `WebSocket接続試行: ${wsUrl}`);
            this.log('info', `API Base URL: ${this.config.apiBase}`);
            this.log('info', `ユーザーID: ${this.currentUser.id}`);
            this.log('info', `JWTトークン長: ${this.jwtToken.length}文字`);
            this.log('info', `JWTトークン先頭: ${this.jwtToken.substring(0, 30)}...`);

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
            this.log('info', 'WebSocket接続確立');
            this.updateConnectionStatus('connecting');

            // 接続確立後に認証メッセージを送信
            this.sendAuthMessage();
        };
        
        this.websocket.onmessage = (event) => {
            try {
                const message = JSON.parse(event.data);
                this.handleWebSocketMessage(message);
            } catch (error) {
                this.log('error', `メッセージパースエラー: ${error.message}`);
            }
        };
        
        this.websocket.onclose = (event) => {
            this.log('warning', `WebSocket接続が閉じられました: ${event.code} - ${event.reason}`);

            // エラーコードに基づいて適切な処理
            switch (event.code) {
                case 4001:
                    this.log('error', '認証エラー: トークンまたはユーザーIDがありません');
                    alert('認証エラー: トークンまたはユーザーIDがありません。再度ログインしてください。');
                    this.logout();
                    break;
                case 4002:
                    this.log('error', '認証エラー: 無効なトークンです');
                    alert('認証エラー: 無効なトークンです。再度ログインしてください。');
                    this.logout();
                    break;
                case 4003:
                    this.log('error', '認証エラー: ユーザーIDが一致しません');
                    alert('認証エラー: ユーザーIDが一致しません。再度ログインしてください。');
                    this.logout();
                    break;
                case 1000:
                    this.log('info', '正常な切断');
                    break;
                default:
                    this.log('warning', `予期しない切断: ${event.code} - ${event.reason}`);
                    break;
            }

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
    // WebSocket認証
    // =====================

    sendAuthMessage() {
        if (!this.websocket || this.websocket.readyState !== WebSocket.OPEN) {
            this.log('error', 'WebSocketが接続されていません');
            return false;
        }

        const authMessage = {
            type: 'auth',
            data: {
                token: this.jwtToken
            },
            timestamp: new Date().toISOString(),
            messageId: this.generateUUID()
        };

        this.websocket.send(JSON.stringify(authMessage));
        this.log('info', '認証メッセージ送信', authMessage);
        return true;
    }

    // =====================
    // WebSocketメッセージ処理
    // =====================

    handleWebSocketMessage(message) {
        this.log('info', `受信: ${message.type}`, message);

        const handlers = {
            'auth_success': this.onAuthSuccess.bind(this),
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

    onAuthSuccess(data) {
        this.log('success', `認証成功: ${data.user_id || this.currentUser.id}`);
        if (data.nickname) {
            this.currentUser.nickname = data.nickname;
            document.getElementById('userDisplay').textContent = data.nickname;
        }
        this.updateConnectionStatus('connected');
        this.updateStatus('接続完了', 'マッチング開始ボタンを押して対戦を始めてください');
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

        // 認証エラーの場合、ログアウトして再ログインを促す
        if (error.code === 'INVALID_TOKEN' || error.code === 'USER_ID_MISMATCH' ||
            error.code === 'MISSING_AUTH_DATA' || error.code === 'INVALID_AUTH_FORMAT') {
            alert(`認証エラー: ${error.message || '認証に失敗しました'}\n再度ログインしてください。`);
            this.logout();
            return;
        }

        alert(`エラー: ${error.message || '不明なエラーが発生しました'}`);
    }
    
    onPong(data) {
        this.log('info', 'Pong受信', data);
    }
    
    // =====================
    // UI更新メソッド
    // =====================
    
    updateStatus(title, message) {
        const titleElement = document.getElementById('statusTitle');
        const messageElement = document.getElementById('statusMessage');
        if (titleElement) titleElement.textContent = title;
        if (messageElement) messageElement.textContent = message;
    }
    
    showMatchingInfo() {
        const matchingInfo = document.getElementById('matchingInfo');
        if (matchingInfo) matchingInfo.style.display = 'block';
    }
    
    hideMatchingInfo() {
        const matchingInfo = document.getElementById('matchingInfo');
        if (matchingInfo) matchingInfo.style.display = 'none';
    }
    
    updateMatchingDisplay(position, waitTime) {
        const queuePosition = document.getElementById('queuePosition');
        const estimatedWait = document.getElementById('estimatedWait');
        if (queuePosition) queuePosition.textContent = position || '-';
        if (estimatedWait) estimatedWait.textContent = waitTime || '-';
    }
    
    showOpponentInfo(opponent) {
        const opponentInfo = document.getElementById('opponentInfo');
        const opponentName = document.getElementById('opponentName');
        const opponentId = document.getElementById('opponentId');
        const readyBtn = document.getElementById('readyBtn');
        
        if (opponentInfo) opponentInfo.style.display = 'block';
        if (opponentName) opponentName.textContent = opponent.nickname || 'Unknown';
        if (opponentId) opponentId.textContent = opponent.userId || 'Unknown';
        
        // 準備完了ボタンを表示
        if (readyBtn) readyBtn.style.display = 'inline-block';
    }
    
    hideOpponentInfo() {
        const opponentInfo = document.getElementById('opponentInfo');
        if (opponentInfo) opponentInfo.style.display = 'none';
    }
    
    hideOpponentReady() {
        const readyBtn = document.getElementById('readyBtn');
        if (readyBtn) readyBtn.style.display = 'none';
    }
    
    showHandSelection() {
        const handSelection = document.getElementById('handSelection');
        if (handSelection) handSelection.style.display = 'block';
        this.enableHandSelection();
    }
    
    hideHandSelection() {
        const handSelection = document.getElementById('handSelection');
        if (handSelection) handSelection.style.display = 'none';
    }
    
    enableHandSelection() {
        document.querySelectorAll('.hand-btn').forEach(btn => {
            btn.classList.remove('disabled', 'selected');
            btn.disabled = false;
        });
        const handStatus = document.getElementById('handStatus');
        if (handStatus) handStatus.textContent = '手を選択してください';
    }
    
    disableHandSelection() {
        document.querySelectorAll('.hand-btn').forEach(btn => {
            btn.disabled = true;
        });
        const handStatus = document.getElementById('handStatus');
        if (handStatus) handStatus.textContent = '手を送信しました。相手を待っています...';
    }
    
    resetHandSelection() {
        document.querySelectorAll('.hand-btn').forEach(btn => {
            btn.disabled = false;
            btn.classList.remove('selected');
        });
        const handStatus = document.getElementById('handStatus');
        if (handStatus) handStatus.textContent = '手を選択してください';
    }
    
    showBattleResult(result) {
        const battleResult = document.getElementById('battleResult');
        const resultTitle = document.getElementById('resultTitle');
        const yourHand = document.getElementById('yourHand');
        const opponentHand = document.getElementById('opponentHand');
        const yourResult = document.getElementById('yourResult');
        const opponentResult = document.getElementById('opponentResult');
        const nextRoundBtn = document.getElementById('nextRoundBtn');
        const newBattleBtn = document.getElementById('newBattleBtn');
        
        if (battleResult) battleResult.style.display = 'block';
        
        // 結果表示
        if (result.player1 && result.player1.userId === this.currentUser.id) {
            if (yourHand) yourHand.textContent = this.getHandEmoji(result.player1.hand);
            if (yourResult) yourResult.textContent = this.getResultText(result.player1.result);
            if (opponentHand) opponentHand.textContent = this.getHandEmoji(result.player2.hand);
            if (opponentResult) opponentResult.textContent = this.getResultText(result.player2.result);
        } else {
            if (yourHand) yourHand.textContent = this.getHandEmoji(result.player2.hand);
            if (yourResult) yourResult.textContent = this.getResultText(result.player2.result);
            if (opponentHand) opponentHand.textContent = this.getHandEmoji(result.player1.hand);
            if (opponentResult) opponentResult.textContent = this.getResultText(result.player1.result);
        }
        
        // ボタン表示制御
        if (nextRoundBtn) nextRoundBtn.style.display = 'none';
        if (newBattleBtn) newBattleBtn.style.display = 'block';
    }
    
    showDrawResult(result) {
        const battleResult = document.getElementById('battleResult');
        const resultTitle = document.getElementById('resultTitle');
        const yourHand = document.getElementById('yourHand');
        const opponentHand = document.getElementById('opponentHand');
        const yourResult = document.getElementById('yourResult');
        const opponentResult = document.getElementById('opponentResult');
        const nextRoundBtn = document.getElementById('nextRoundBtn');
        const newBattleBtn = document.getElementById('newBattleBtn');
        
        if (battleResult) battleResult.style.display = 'block';
        if (resultTitle) resultTitle.textContent = '引き分け！';
        
        // 引き分け結果表示
        if (result.player1 && result.player1.userId === this.currentUser.id) {
            if (yourHand) yourHand.textContent = this.getHandEmoji(result.player1.hand);
            if (yourResult) yourResult.textContent = '引き分け';
            if (opponentHand) opponentHand.textContent = this.getHandEmoji(result.player2.hand);
            if (opponentResult) opponentResult.textContent = '引き分け';
        } else {
            if (yourHand) yourHand.textContent = this.getHandEmoji(result.player2.hand);
            if (yourResult) yourResult.textContent = '引き分け';
            if (opponentHand) opponentHand.textContent = this.getHandEmoji(result.player1.hand);
            if (opponentResult) opponentResult.textContent = '引き分け';
        }
        
        // ボタン表示制御
        if (nextRoundBtn) nextRoundBtn.style.display = 'block';
        if (newBattleBtn) newBattleBtn.style.display = 'none';
    }
    
    hideBattleResult() {
        const battleResult = document.getElementById('battleResult');
        if (battleResult) battleResult.style.display = 'none';
    }
    
    resetBattleState() {
        this.currentBattle = null;
        this.hideMatchingInfo();
        this.hideOpponentInfo();
        this.hideHandSelection();
        this.hideBattleResult();
        this.updateStatus('対戦待機中', 'WebSocketに接続してマッチングを開始してください');
    }
    
    resetUI() {
        this.resetBattleState();
        // 接続状態もリセット
        this.updateConnectionStatus('disconnected');
    }
    
    getHandEmoji(hand) {
        const handEmojis = {
            'rock': '✊',
            'scissors': '✌️',
            'paper': '✋'
        };
        return handEmojis[hand] || '?';
    }
    
    getResultText(result) {
        const resultTexts = {
            'win': '勝ち',
            'lose': '負け',
            'draw': '引き分け'
        };
        return resultTexts[result] || result;
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
        
        this.sendMessage('battle_quit', {
            battleId: this.currentBattle.battleId,
            userId: this.currentUser.id,
            reason: 'user_action'
        });
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
    
    // =====================
    // 環境設定管理
    // =====================
    
    updateApiBaseUrl() {
        const select = document.getElementById('apiBaseUrl');
        const customUrlGroup = document.getElementById('customUrlGroup');
        const currentApiUrl = document.getElementById('currentApiUrl');
        
        if (select.value === 'custom') {
            customUrlGroup.style.display = 'block';
            const customUrl = document.getElementById('customUrl').value;
            if (customUrl) {
                this.config.httpApiBase = customUrl;
                this.config.apiBase = customUrl.replace('http', 'ws');
                currentApiUrl.textContent = customUrl;
            }
        } else {
            customUrlGroup.style.display = 'none';
            this.config.httpApiBase = select.value;
            this.config.apiBase = select.value.replace('http', 'ws');
            currentApiUrl.textContent = select.value;
        }
        
        this.log('info', `APIベースURLを更新: ${this.config.httpApiBase}`);
        this.log('info', `WebSocketベースURL: ${this.config.apiBase}`);
    }
}

// グローバル関数として環境設定更新関数を公開
window.updateApiBaseUrl = function() {
    if (window.jankenClient) {
        window.jankenClient.updateApiBaseUrl();
    }
};

// アプリケーション初期化
document.addEventListener('DOMContentLoaded', () => {
    window.jankenClient = new JankenBattleClient();
});