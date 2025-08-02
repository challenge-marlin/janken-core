document.addEventListener('DOMContentLoaded', () => {
    const refreshButton = document.getElementById('refreshButton');
    refreshButton.addEventListener('click', refreshMetrics);

    // 初回読み込み
    refreshMetrics();
    // 30秒ごとに自動更新
    setInterval(refreshMetrics, 30000);
});

async function refreshMetrics() {
    updateLastUpdateTime();
    await Promise.all([
        checkServiceHealth('nginx', '/health'),
        checkServiceHealth('api', '/api/health'),
        checkServiceHealth('mysql', '/api/health/mysql'),
        checkServiceHealth('redis', '/api/health/redis')
    ]);
    await updateMetrics();
}

function updateLastUpdateTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('ja-JP');
    document.getElementById('lastUpdate').textContent = `最終更新: ${timeString}`;
}

async function checkServiceHealth(service, endpoint) {
    const statusElement = document.querySelector(`#${service}Status .status`);
    console.log(`[DEBUG] Checking ${service} health at ${endpoint}`);
    
    try {
        const response = await fetch(endpoint);
        const text = await response.text();
        console.log(`[DEBUG] ${service} response:`, { status: response.status, text: text });
        
        if (service === 'nginx') {
            // Nginxは単純なテキストレスポンス
            const trimmedText = text.trim();
            console.log(`[DEBUG] ${service} trimmed text: "${trimmedText}"`);
            
            if (response.ok && trimmedText === 'healthy') {
                statusElement.textContent = '正常';
                statusElement.className = 'status healthy';
                console.log(`[DEBUG] ${service} status set to healthy`);
            } else {
                statusElement.textContent = '警告';
                statusElement.className = 'status warning';
                console.log(`[DEBUG] ${service} status set to warning`);
            }
        } else {
            // APIエンドポイントはJSONレスポンス
            console.log(`[DEBUG] ${service} attempting JSON parse`);
            try {
                const data = JSON.parse(text);
                console.log(`[DEBUG] ${service} parsed data:`, data);
                
                if (response.ok && data.status === 'healthy') {
                    statusElement.textContent = '正常';
                    statusElement.className = 'status healthy';
                    console.log(`[DEBUG] ${service} status set to healthy`);
                } else {
                    statusElement.textContent = '警告';
                    statusElement.className = 'status warning';
                    console.log(`[DEBUG] ${service} status set to warning`);
                }
            } catch (jsonError) {
                console.error(`[ERROR] ${service} JSON parse error:`, jsonError, 'Response text:', text);
                statusElement.textContent = 'エラー';
                statusElement.className = 'status error';
            }
        }
    } catch (error) {
        statusElement.textContent = 'エラー';
        statusElement.className = 'status error';
        console.error(`[ERROR] Error checking ${service} health:`, error);
    }
}

async function updateMetrics() {
    try {
        const response = await fetch('/api/metrics');
        const result = await response.json();
        
        // APIレスポンス構造に合わせてデータを取得
        const data = result.data || result;
        
        // メトリクスの更新
        updateMetricValue('activeUsers', data.activeUsers || 0);
        updateMetricValue('activeBattles', data.activeBattles || 0);
        updateMetricValue('apiLatency', `${data.apiLatency || 0}ms`);
        updateMetricValue('errorRate', `${(data.errorRate || 0).toFixed(2)}%`);
    } catch (error) {
        console.error('Error updating metrics:', error);
        // エラー時は'-'を表示
        ['activeUsers', 'activeBattles', 'apiLatency', 'errorRate'].forEach(id => {
            updateMetricValue(id, '-');
        });
    }
}

function updateMetricValue(id, value) {
    const element = document.querySelector(`#${id} .value`);
    if (element) {
        element.textContent = value;
    }
} 