// 認証API テスト用 JavaScript

let currentJWT = null;
let captchaChallenge = {
    opponent: '✌️',
    token: generateCaptchaToken()
};

// 初期化
document.addEventListener('DOMContentLoaded', function() {
    console.log('Auth test page loaded');
    console.log('Available functions:', {
        simpleApiTest: typeof simpleApiTest,
        simpleDevLogin: typeof simpleDevLogin
    });
    
    // URLパラメータをチェック
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('login_success') === 'true') {
        showLoginSuccessMessage();
    }
    
    // カスタムURL表示制御
    document.getElementById('apiBaseUrl').addEventListener('change', function() {
        const customGroup = document.getElementById('customUrlGroup');
        if (this.value === 'custom') {
            customGroup.style.display = 'block';
        } else {
            customGroup.style.display = 'none';
        }
    });

    // 初期CAPTCHA生成
    generateCaptcha();
    
    // 保存されたJWTがあれば復元
    const savedJWT = localStorage.getItem('jwt_token');
    if (savedJWT) {
        currentJWT = savedJWT;
        document.getElementById('jwtToken').value = savedJWT;
    }
});

// ログイン成功メッセージ表示
function showLoginSuccessMessage() {
    const magicLinkUser = localStorage.getItem('magic_link_user');
    if (magicLinkUser) {
        const user = JSON.parse(magicLinkUser);
        alert(`🎉 Magic Link認証が完了しました！\n\nユーザー: ${user.email}\nJWTトークンが保存されました。`);
        
        // URLパラメータをクリア
        const url = new URL(window.location);
        url.searchParams.delete('login_success');
        window.history.replaceState({}, document.title, url);
    }
}

// ベースURL取得
function getBaseUrl() {
    const selector = document.getElementById('apiBaseUrl');
    if (selector.value === 'custom') {
        return document.getElementById('customUrl').value;
    }
    return selector.value;
}

// 接続テスト
async function testConnection() {
    const baseUrl = getBaseUrl();
    const statusIndicator = document.getElementById('connectionStatus');
    const statusText = document.getElementById('connectionText');
    
    try {
        statusIndicator.className = 'status-indicator status-warning';
        statusText.textContent = '接続中...';
        
        const response = await fetch(`${baseUrl}/api/health`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            statusIndicator.className = 'status-indicator status-success';
            statusText.textContent = '接続成功';
        } else {
            throw new Error(`HTTP ${response.status}`);
        }
    } catch (error) {
        statusIndicator.className = 'status-indicator status-error';
        statusText.textContent = `接続失敗: ${error.message}`;
    }
}

// CAPTCHA生成
function generateCaptcha() {
    const hands = ['✊', '✌️', '✋'];
    const opponent = hands[Math.floor(Math.random() * hands.length)];
    captchaChallenge.opponent = opponent;
    captchaChallenge.token = generateCaptchaToken();
    
    document.getElementById('opponentHand').textContent = opponent;
    
    // 選択状態をリセット
    document.querySelectorAll('.hand-btn').forEach(btn => {
        btn.classList.remove('selected');
    });
    document.getElementById('selectedHand').value = '';
}

// 手を選択
function selectHand(hand) {
    document.querySelectorAll('.hand-btn').forEach(btn => {
        btn.classList.remove('selected');
    });
    
    const selectedBtn = document.querySelector(`[data-hand="${hand}"]`);
    selectedBtn.classList.add('selected');
    document.getElementById('selectedHand').value = hand;
}

// CAPTCHAトークン生成（簡易版）
function generateCaptchaToken() {
    return 'captcha_' + Math.random().toString(36).substring(2, 15);
}

// レスポンス表示関数
function displayResponse(elementId, response, error = null) {
    const element = document.getElementById(elementId);
    if (error) {
        element.textContent = `エラー: ${error.message}\n\nResponse: ${JSON.stringify(response, null, 2)}`;
        element.style.backgroundColor = '#2d1b1b';
        element.style.color = '#ff9999';
    } else {
        element.textContent = JSON.stringify(response, null, 2);
        element.style.backgroundColor = '#1e1e1e';
        element.style.color = '#f8f8f2';
        
        // JWTが含まれている場合は保存
        if (response.data && response.data.token) {
            currentJWT = response.data.token;
            document.getElementById('jwtToken').value = currentJWT;
            localStorage.setItem('jwt_token', currentJWT);
        }
    }
}

// Magic Link リクエスト
async function requestMagicLink() {
    const baseUrl = getBaseUrl();
    const email = document.getElementById('magicEmail').value;
    const selectedHand = document.getElementById('selectedHand').value;
    const recaptchaToken = document.getElementById('recaptchaToken').value;
    
    if (!selectedHand) {
        alert('CAPTCHAの手を選択してください');
        return;
    }
    
    const requestData = {
        email: email,
        captcha: {
            opponent: captchaChallenge.opponent,
            answer: selectedHand,
            token: captchaChallenge.token
        }
    };
    
    // reCAPTCHAトークンがある場合は追加
    if (recaptchaToken) {
        requestData.recaptcha_token = recaptchaToken;
    }
    
    try {
        const response = await fetch(`${baseUrl}/api/auth/request-link`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });
        
        const data = await response.json();
        displayResponse('magicLinkResponse', data);
        
        // Magic Link URLを生成・表示
        if (data.success && data.data && data.data.token) {
            showMagicLinkUrl(data.data.token);
        }
        
        // CAPTCHA更新
        generateCaptcha();
        
    } catch (error) {
        displayResponse('magicLinkResponse', null, error);
    }
}

// Magic Link URL表示
function showMagicLinkUrl(token) {
    const baseUrl = getBaseUrl();
    const magicLinkUrl = `${baseUrl}/monitoring/auth/magic-link-verify.html?token=${token}`;
    
    document.getElementById('magicLinkUrl').textContent = magicLinkUrl;
    document.getElementById('magicLinkUrlSection').style.display = 'block';
    
    // グローバル変数に保存
    window.currentMagicLinkUrl = magicLinkUrl;
    window.currentMagicToken = token;
}

// Magic Linkを開く（メール代替）
function openMagicLink() {
    if (window.currentMagicLinkUrl) {
        window.open(window.currentMagicLinkUrl, '_blank');
    } else {
        alert('Magic Link URLがありません。先にMagic Linkをリクエストしてください。');
    }
}

// Magic Link URLをコピー
function copyMagicLink() {
    if (window.currentMagicLinkUrl) {
        navigator.clipboard.writeText(window.currentMagicLinkUrl).then(() => {
            alert('Magic Link URLがクリップボードにコピーされました');
        });
    } else {
        alert('コピーするMagic Link URLがありません');
    }
}

// Magic Link 検証
async function verifyMagicLink() {
    const baseUrl = getBaseUrl();
    const token = document.getElementById('magicToken').value;
    
    if (!token) {
        alert('Magic Link トークンを入力してください');
        return;
    }
    
    try {
        const response = await fetch(`${baseUrl}/api/auth/verify-magic-link`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ token: token })
        });
        
        const data = await response.json();
        displayResponse('verifyResponse', data);
        
    } catch (error) {
        displayResponse('verifyResponse', null, error);
    }
}

// テストユーザーログイン
async function testUserLogin() {
    const baseUrl = getBaseUrl();
    const userNumber = parseInt(document.getElementById('testUserNumber').value);
    
    try {
        const response = await fetch(`${baseUrl}/api/auth/test-login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ user_number: userNumber })
        });
        
        const data = await response.json();
        displayResponse('testUserResponse', data);
        
    } catch (error) {
        displayResponse('testUserResponse', null, error);
    }
}

// 開発用ログイン
async function devLogin() {
    const baseUrl = getBaseUrl();
    const email = document.getElementById('devEmail').value;
    const mode = document.getElementById('devMode').value;
    
    try {
        const response = await fetch(`${baseUrl}/api/auth/dev-login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email: email,
                mode: mode
            })
        });
        
        const data = await response.json();
        displayResponse('devLoginResponse', data);
        
    } catch (error) {
        displayResponse('devLoginResponse', null, error);
    }
}

// 従来形式ログイン
async function userInfoLogin() {
    const baseUrl = getBaseUrl();
    const userId = document.getElementById('userId').value;
    const password = document.getElementById('password').value;
    
    try {
        const response = await fetch(`${baseUrl}/api/auth/UserInfo`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                userId: userId,
                password: password
            })
        });
        
        const data = await response.json();
        displayResponse('userInfoResponse', data);
        
    } catch (error) {
        displayResponse('userInfoResponse', null, error);
    }
}

// JWTトークンコピー
function copyToken() {
    const token = document.getElementById('jwtToken').value;
    if (token) {
        navigator.clipboard.writeText(token).then(() => {
            alert('トークンがクリップボードにコピーされました');
        });
    } else {
        alert('コピーするトークンがありません');
    }
}

// JWTトークンクリア
function clearToken() {
    currentJWT = null;
    document.getElementById('jwtToken').value = '';
    localStorage.removeItem('jwt_token');
    alert('トークンがクリアされました');
}

// JWTトークン検証
async function validateToken() {
    const baseUrl = getBaseUrl();
    const token = document.getElementById('jwtToken').value;
    
    if (!token) {
        alert('検証するトークンがありません');
        return;
    }
    
    try {
        // 保護されたエンドポイントにアクセスしてトークンを検証
        const response = await fetch(`${baseUrl}/api/protected-test`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        displayResponse('tokenValidationResponse', data);
        
    } catch (error) {
        displayResponse('tokenValidationResponse', null, error);
    }
}

// APIテスト用のヘルパー関数
async function makeAuthenticatedRequest(endpoint, method = 'GET', body = null) {
    const baseUrl = getBaseUrl();
    const token = document.getElementById('jwtToken').value;
    
    const headers = {
        'Content-Type': 'application/json'
    };
    
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    const options = {
        method: method,
        headers: headers
    };
    
    if (body) {
        options.body = JSON.stringify(body);
    }
    
    try {
        const response = await fetch(`${baseUrl}${endpoint}`, options);
        return await response.json();
    } catch (error) {
        throw error;
    }
}

// シンプルAPIテスト
async function simpleApiTest() {
    const baseUrl = getBaseUrl();
    const statusIndicator = document.getElementById('connectionStatus');
    const statusText = document.getElementById('connectionText');
    
    try {
        statusIndicator.className = 'status-indicator status-warning';
        statusText.textContent = 'APIテスト中...';
        
        const response = await fetch(`${baseUrl}/api/auth/simple-test`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            statusIndicator.className = 'status-indicator status-success';
            statusText.textContent = 'APIテスト成功';
            alert(`APIテスト成功: ${data.message}`);
        } else {
            throw new Error(`API Error: ${JSON.stringify(data)}`);
        }
    } catch (error) {
        statusIndicator.className = 'status-indicator status-error';
        statusText.textContent = `APIテスト失敗: ${error.message}`;
        alert(`APIテスト失敗: ${error.message}`);
    }
}

// シンプル開発ログイン
async function simpleDevLogin() {
    const baseUrl = getBaseUrl();
    
    try {
        const response = await fetch(`${baseUrl}/api/auth/simple-dev-login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email: 'dev@example.com'
            })
        });
        
        const data = await response.json();
        displayResponse('devLoginResponse', data);
        
        if (data.success && data.data && data.data.token) {
            alert('シンプル開発ログイン成功！JWTが発行されました。');
        }
        
    } catch (error) {
        displayResponse('devLoginResponse', null, error);
        alert(`シンプル開発ログイン失敗: ${error.message}`);
    }
}

// デバッグ用のグローバル関数
window.debugAuth = {
    getCurrentJWT: () => currentJWT,
    getCaptchaChallenge: () => captchaChallenge,
    testAPI: async (endpoint, method, body) => {
        return await makeAuthenticatedRequest(endpoint, method, body);
    },
    simpleTest: simpleApiTest,
    simpleLogin: simpleDevLogin
}; 