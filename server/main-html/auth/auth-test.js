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
        statusText.textContent = '接続失敗';
        console.error('接続テストエラー:', error);
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

// クリップボードにコピーする関数
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        // 一時的な成功メッセージを表示
        const button = event.target;
        const originalText = button.textContent;
        button.textContent = '✅ コピー完了！';
        button.style.background = '#4CAF50';
        setTimeout(() => {
            button.textContent = originalText;
            button.style.background = '#667eea';
        }, 2000);
    } catch (err) {
        // フォールバック: 古いブラウザ対応
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        try {
            document.execCommand('copy');
            const button = event.target;
            const originalText = button.textContent;
            button.textContent = '✅ コピー完了！';
            button.style.background = '#4CAF50';
            setTimeout(() => {
                button.textContent = originalText;
                button.style.background = '#667eea';
            }, 2000);
        } catch (fallbackErr) {
            console.error('コピーに失敗しました:', fallbackErr);
            alert('コピーに失敗しました。手動でコピーしてください。');
        }
        document.body.removeChild(textArea);
    }
}

// レスポンス表示関数
function displayResponse(elementId, data, error = null) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    if (error) {
        element.textContent = `❌ エラー: ${error.message}`;
        element.style.color = '#f44336';
        element.style.backgroundColor = '#ffebee';
    } else if (data) {
        // 新しいAPIレスポンス形式に対応
        let responseText = '';
        
        if (data.message) {
            responseText += `📋 メッセージ: ${data.message}\n\n`;
        }
        
        if (data.success !== undefined) {
            responseText += `✅ 成功: ${data.success ? 'はい' : 'いいえ'}\n\n`;
        }
        
        if (data.data) {
            responseText += `📊 データ:\n`;
            if (data.data.user) {
                responseText += `   👤 ユーザー: ${JSON.stringify(data.data.user, null, 2)}\n`;
            }
            if (data.data.token) {
                // トークンを完全表示（長い場合は改行で見やすく）
                const token = data.data.token;
                if (token.length > 80) {
                    responseText += `   🎫 トークン:\n      ${token.substring(0, 80)}\n      ${token.substring(80)}\n`;
                } else {
                    responseText += `   🎫 トークン: ${token}\n`;
                }
                // トークンコピーボタンを追加
                responseText += `   📋 <button onclick="copyToClipboard('${token}')" style="background: #667eea; color: white; border: none; padding: 5px 10px; border-radius: 3px; cursor: pointer; font-size: 12px;">トークンをコピー</button>\n`;
            }
            if (data.data.magic_link_url) {
                // Magic Link URLを完全表示（長い場合は改行で見やすく）
                const url = data.data.magic_link_url;
                if (url.length > 80) {
                    responseText += `   🔗 Magic Link URL:\n      ${url.substring(0, 80)}\n      ${url.substring(80)}\n`;
                } else {
                    responseText += `   🔗 Magic Link URL: ${url}\n`;
                }
                // URLコピーボタンを追加
                responseText += `   📋 <button onclick="copyToClipboard('${url}')" style="background: #667eea; color: white; border: none; padding: 5px 10px; border-radius: 3px; cursor: pointer; font-size: 12px;">URLをコピー</button>\n`;
            }
            // その他のデータフィールド
            Object.keys(data.data).forEach(key => {
                if (!['user', 'token', 'magic_link_url'].includes(key)) {
                    responseText += `   📝 ${key}: ${JSON.stringify(data.data[key])}\n`;
                }
            });
        }
        
        if (data.errors) {
            responseText += `❌ エラー詳細:\n${JSON.stringify(data.errors, null, 2)}\n`;
        }
        
        if (data.details) {
            responseText += `🔍 詳細情報:\n${JSON.stringify(data.details, null, 2)}\n`;
        }
        
        element.innerHTML = responseText || JSON.stringify(data, null, 2);
        element.style.color = '#2e7d32';
        element.style.backgroundColor = '#e8f5e8';
    } else {
        element.textContent = 'レスポンスがありません';
        element.style.color = '#666';
        element.style.backgroundColor = '#f5f5f5';
    }
}

// Magic Link リクエスト
async function requestMagicLink() {
    const email = document.getElementById('magicEmail').value;
    const selectedHand = document.getElementById('selectedHand').value;
    const recaptchaToken = document.getElementById('recaptchaToken').value;
    
    if (!email) {
        displayResponse('magicLinkResponse', null, new Error('メールアドレスを入力してください'));
        return;
    }
    
    if (!selectedHand) {
        displayResponse('magicLinkResponse', null, new Error('CAPTCHAを完了してください'));
        return;
    }
    
    try {
        const baseUrl = getBaseUrl();
        displayResponse('magicLinkResponse', { message: 'Magic Link送信中...' });
    
    const requestData = {
        email: email,
            captcha_token: captchaChallenge.token,
            selected_hand: selectedHand
        };
        
    if (recaptchaToken) {
        requestData.recaptcha_token = recaptchaToken;
    }
    
        const response = await fetch(`${baseUrl}/api/auth/request-magic-link`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
        displayResponse('magicLinkResponse', data);
        
            // Magic Link URL表示
            if (data.data && data.data.magic_link_url) {
                document.getElementById('magicLinkUrl').textContent = data.data.magic_link_url;
                document.getElementById('magicLinkUrlSection').style.display = 'block';
            }
            
            // 次のCAPTCHA生成
        generateCaptcha();
        } else {
            displayResponse('magicLinkResponse', null, new Error(data.message || 'Magic Link送信に失敗しました'));
        }
        
    } catch (error) {
        displayResponse('magicLinkResponse', null, error);
    }
}

// Magic Link URL表示
function showMagicLinkUrl(token) {
    const baseUrl = getBaseUrl();
    const magicLinkUrl = `${baseUrl}/auth/magic-link-verify.html?token=${token}`;
    
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
    const token = document.getElementById('magicToken').value;
    
    if (!token) {
        displayResponse('verifyResponse', null, new Error('Magic Link Tokenを入力してください'));
        return;
    }
    
    try {
        const baseUrl = getBaseUrl();
        displayResponse('verifyResponse', { message: 'Magic Link検証中...' });
        
        console.log('🔍 Magic Link検証開始:', { token: token.substring(0, 20) + '...', baseUrl });
        
        const response = await fetch(`${baseUrl}/api/auth/verify-magic-link`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ token: token })
        });
        
        console.log('🔍 HTTPレスポンス:', { status: response.status, statusText: response.statusText });
        
        const responseText = await response.text();
        console.log('🔍 レスポンステキスト:', responseText);
        
        let data;
        try {
            data = JSON.parse(responseText);
            console.log('🔍 パースされたデータ:', data);
        } catch (parseError) {
            console.error('❌ JSONパースエラー:', parseError);
            displayResponse('verifyResponse', null, new Error(`JSONパースエラー: ${parseError.message}\nレスポンス: ${responseText}`));
            return;
        }
        
        if (response.ok && data.success) {
            displayResponse('verifyResponse', data);
            
            // JWTトークンを保存
            if (data.data && data.data.token) {
                currentJWT = data.data.token;
                document.getElementById('jwtToken').value = data.data.token;
                localStorage.setItem('jwt_token', data.data.token);
                
                // ユーザー情報も保存
                if (data.data.user) {
                    localStorage.setItem('magic_link_user', JSON.stringify(data.data.user));
                }
            }
        } else {
            displayResponse('verifyResponse', null, new Error(data.message || 'Magic Link検証に失敗しました'));
        }
        
    } catch (error) {
        console.error('❌ Magic Link検証エラー:', error);
        displayResponse('verifyResponse', null, error);
    }
}

// テストユーザーログイン
async function testUserLogin() {
    const userNumber = document.getElementById('testUserNumber').value;
    
    if (!userNumber) {
        displayResponse('testUserResponse', null, new Error('テストユーザー番号を選択してください'));
        return;
    }
    
    try {
        const baseUrl = getBaseUrl();
        displayResponse('testUserResponse', { message: 'テストユーザーログイン中...' });
        
        // テストユーザーのメールアドレスを生成
        const email = `test${userNumber}@example.com`;
        const password = 'password123';
        
        const response = await fetch(`${baseUrl}/api/auth/db-login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email: email,
                password: password
            })
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
        displayResponse('testUserResponse', data);
            
            // JWTトークンを保存
            if (data.data && data.data.token) {
                currentJWT = data.data.token;
                document.getElementById('jwtToken').value = data.data.token;
                localStorage.setItem('jwt_token', data.data.token);
                
                // ユーザー情報も保存
                if (data.data.user) {
                    localStorage.setItem('test_user_data', JSON.stringify(data.data.user));
                }
            }
        } else {
            displayResponse('testUserResponse', null, new Error(data.message || 'テストユーザーログインに失敗しました'));
        }
        
    } catch (error) {
        displayResponse('testUserResponse', null, error);
    }
}

// 開発用ログイン
async function devLogin() {
    const email = document.getElementById('devEmail').value;
    const mode = document.getElementById('devMode').value;
    
    if (!email) {
        displayResponse('devLoginResponse', null, new Error('メールアドレスを入力してください'));
        return;
    }
    
    try {
        const baseUrl = getBaseUrl();
        displayResponse('devLoginResponse', { message: '開発用ログイン中...' });
        
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
        
        if (response.ok && data.success) {
        displayResponse('devLoginResponse', data);
            
            // JWTトークンを保存
            if (data.data && data.data.token) {
                currentJWT = data.data.token;
                document.getElementById('jwtToken').value = data.data.token;
                localStorage.setItem('jwt_token', data.data.token);
                
                // ユーザー情報も保存
                if (data.data.user) {
                    localStorage.setItem('dev_user_data', JSON.stringify(data.data.user));
                }
            }
        } else {
            displayResponse('devLoginResponse', null, new Error(data.message || '開発用ログインに失敗しました'));
        }
        
    } catch (error) {
        displayResponse('devLoginResponse', null, error);
    }
}

// ユーザー情報認証テスト（新形式）
async function userInfoLogin() {
    const userId = document.getElementById('userId').value;
    const password = document.getElementById('password').value;
    
    if (!userId || !password) {
        displayResponse('userInfoResponse', null, new Error('ユーザーIDとパスワードを入力してください'));
        return;
    }
    
    try {
        const baseUrl = getBaseUrl();
        displayResponse('userInfoResponse', { message: 'ユーザー情報認証中...' });
        
        // ユーザーIDからメールアドレスを生成（test_user_1 → test1@example.com）
        const email = userId.replace('test_user_', 'test') + '@example.com';
        
        const response = await fetch(`${baseUrl}/api/auth/db-login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email: email,
                password: password
            })
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
        displayResponse('userInfoResponse', data);
            
            // JWTトークンを保存
            if (data.data && data.data.token) {
                currentJWT = data.data.token;
                document.getElementById('jwtToken').value = data.data.token;
                localStorage.setItem('jwt_token', data.data.token);
                
                // ユーザー情報も保存
                if (data.data.user) {
                    localStorage.setItem('user_info_data', JSON.stringify(data.data.user));
                }
            }
        } else {
            displayResponse('userInfoResponse', null, new Error(data.message || 'ユーザー情報認証に失敗しました'));
        }
        
    } catch (error) {
        displayResponse('userInfoResponse', null, error);
    }
}

// ユーザー情報認証テスト（旧形式 - 非推奨）
async function userInfoLoginLegacy() {
    const userId = document.getElementById('userId').value;
    const password = document.getElementById('password').value;
    
    if (!userId || !password) {
        displayResponse('userInfoResponse', null, new Error('ユーザーIDとパスワードを入力してください'));
        return;
    }
    
    try {
        const baseUrl = getBaseUrl();
        displayResponse('userInfoResponse', { message: '旧形式APIでユーザー情報認証中...（非推奨）' });
        
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
        
        if (response.ok && data.success) {
        displayResponse('userInfoResponse', data);
            
            // JWTトークンを保存
            if (data.data && data.data.token) {
                currentJWT = data.data.token;
                document.getElementById('jwtToken').value = data.data.token;
                localStorage.setItem('jwt_token', data.data.token);
                
                // ユーザー情報も保存
                if (data.data.user) {
                    localStorage.setItem('user_info_data_legacy', JSON.stringify(data.data.user));
                }
            }
        } else {
            displayResponse('userInfoResponse', null, new Error(data.message || '旧形式APIでのユーザー情報認証に失敗しました'));
        }
        
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
        const response = await fetch(`${baseUrl}/api/auth/verify-token`, {
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
    
    try {
        displayResponse('magicLinkResponse', { message: 'シンプルAPIテスト実行中...' });
        
        const response = await fetch(`${baseUrl}/api/health`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayResponse('magicLinkResponse', {
                success: true,
                message: 'シンプルAPIテスト成功',
                data: data
            });
        } else {
            throw new Error(`HTTP ${response.status}: ${data.message || 'Unknown error'}`);
        }
    } catch (error) {
        displayResponse('magicLinkResponse', null, error);
    }
}

// シンプル開発ログイン（DB連携版対応）
async function simpleDevLogin() {
    try {
        const baseUrl = getBaseUrl();
        displayResponse('devLoginResponse', { message: 'シンプル開発ログイン中...' });
        
        const response = await fetch(`${baseUrl}/api/auth/dev-login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email: 'dev@example.com',
                mode: 'dev'
            })
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            displayResponse('devLoginResponse', data);
            
            // JWTトークンを保存
            if (data.data && data.data.token) {
                currentJWT = data.data.token;
                document.getElementById('jwtToken').value = currentJWT;
            }
        } else {
            throw new Error(data.message || '開発用ログインに失敗しました');
        }
    } catch (error) {
        displayResponse('devLoginResponse', null, error);
    }
}

// グローバル関数として公開
window.testConnection = testConnection;
window.simpleApiTest = simpleApiTest;
window.simpleDevLogin = simpleDevLogin;