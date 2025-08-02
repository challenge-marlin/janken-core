document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const refreshButton = document.getElementById('refreshButton');
    const modal = document.getElementById('previewModal');
    const closeButton = modal ? modal.querySelector('.close-button') : null;

    // ドラッグ＆ドロップイベントの設定（要素が存在する場合のみ）
    if (dropZone) {
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });

        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('dragover');
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            const files = e.dataTransfer.files;
            handleFiles(files);
        });
    }

    // ファイル選択イベントの設定（要素が存在する場合のみ）
    if (fileInput) {
        fileInput.addEventListener('change', () => {
            handleFiles(fileInput.files);
        });
    }

    // 更新ボタンのイベント設定（要素が存在する場合のみ）
    if (refreshButton) {
        refreshButton.addEventListener('click', async () => {
            await updateBucketStats();
            await updateFileList();
        });
    }

    // モーダルを閉じるボタンのイベント設定（要素が存在する場合のみ）
    if (closeButton) {
        closeButton.addEventListener('click', () => {
            modal.style.display = 'none';
        });
    }

    // バケット選択の変更イベント
    const bucketSelect = document.getElementById('bucketSelect');
    if (bucketSelect) {
        bucketSelect.addEventListener('change', updateFileList);
    }

    // 初期データの読み込み
    updateBucketStats();
    updateFileList();
});

async function handleFiles(files) {
    const uploadProgress = document.getElementById('uploadProgress');
    const progressFill = uploadProgress ? uploadProgress.querySelector('.progress-fill') : null;
    const progressText = uploadProgress ? uploadProgress.querySelector('.progress-text') : null;

    if (uploadProgress) {
        uploadProgress.style.display = 'block';
    }

    for (const file of files) {
        try {
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch('/storage/upload', {
                method: 'POST',
                body: formData,
                onUploadProgress: (progressEvent) => {
                    if (progressFill && progressText) {
                        const progress = (progressEvent.loaded / progressEvent.total) * 100;
                        progressFill.style.width = `${progress}%`;
                        progressText.textContent = `${Math.round(progress)}%`;
                    }
                }
            });

            if (!response.ok) {
                throw new Error(`アップロードエラー: ${response.statusText}`);
            }

            // アップロード成功後、ファイル一覧を更新
            await updateFileList();
        } catch (error) {
            console.error('ファイルアップロードエラー:', error);
            alert(`ファイルのアップロードに失敗しました: ${error.message}`);
        }
    }

    // プログレスバーをリセット
    if (uploadProgress && progressFill && progressText) {
        setTimeout(() => {
            uploadProgress.style.display = 'none';
            progressFill.style.width = '0';
            progressText.textContent = '0%';
        }, 1000);
    }
}



function createFileItem(file) {
    const fileItem = document.createElement('div');
    fileItem.className = 'file-item';

    fileItem.innerHTML = `
        <div class="file-name">${file.name}</div>
        <div class="file-size">${formatFileSize(file.size)}</div>
        <div class="file-date">${formatDate(file.lastModified)}</div>
        <div class="file-actions">
            <button class="action-button preview-button" onclick="previewFile('${file.name}')">表示</button>
            <button class="action-button delete-button" onclick="deleteFile('${file.name}')">削除</button>
        </div>
    `;

    return fileItem;
}

async function previewFile(fileName) {
    const modal = document.getElementById('previewModal');
    const previewContent = document.getElementById('previewContent');
    const previewFileName = document.getElementById('previewFileName');

    if (!modal || !previewContent || !previewFileName) {
        console.warn('Preview modal elements not found');
        return;
    }

    try {
        const response = await fetch(`/storage/preview/${fileName}`);
        const content = await response.text();

        previewFileName.textContent = fileName;
        previewContent.innerHTML = `<pre>${escapeHtml(content)}</pre>`;
        modal.style.display = 'block';
    } catch (error) {
        console.error('ファイルのプレビューに失敗:', error);
        alert('ファイルのプレビューに失敗しました。');
    }
}



function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatDate(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString('ja-JP');
}

function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// ユーティリティ関数
function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

// バケット統計の更新
async function updateBucketStats() {
    try {
        const response = await fetch('/storage/stats');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const result = await response.json();
        const stats = result.data; // APIレスポンスの構造に合わせて修正

        // プロフィール画像の統計
        const profileImagesCount = document.getElementById('profileImagesCount');
        const profileImagesSize = document.getElementById('profileImagesSize');
        if (profileImagesCount && stats.profileImages) {
            profileImagesCount.textContent = stats.profileImages.count;
        }
        if (profileImagesSize && stats.profileImages) {
            profileImagesSize.textContent = formatBytes(stats.profileImages.totalSize);
        }

        // 学生証画像の統計
        const studentIdsCount = document.getElementById('studentIdsCount');
        const studentIdsSize = document.getElementById('studentIdsSize');
        if (studentIdsCount && stats.studentIds) {
            studentIdsCount.textContent = stats.studentIds.count;
        }
        if (studentIdsSize && stats.studentIds) {
            studentIdsSize.textContent = formatBytes(stats.studentIds.totalSize);
        }

        // 一時ファイルの統計
        const tempUploadsCount = document.getElementById('tempUploadsCount');
        const tempUploadsSize = document.getElementById('tempUploadsSize');
        if (tempUploadsCount && stats.tempUploads) {
            tempUploadsCount.textContent = stats.tempUploads.count;
        }
        if (tempUploadsSize && stats.tempUploads) {
            tempUploadsSize.textContent = formatBytes(stats.tempUploads.totalSize);
        }

        // 最終更新時刻の更新
        updateLastUpdateTime();
    } catch (error) {
        console.error('Failed to fetch bucket stats:', error);
    }
}

// ファイル一覧の更新
async function updateFileList() {
    const bucketSelect = document.getElementById('bucketSelect');
    const bucketName = bucketSelect ? bucketSelect.value : 'profile-images';
    const fileList = document.getElementById('fileList');
    
    if (!fileList) {
        console.warn('fileList element not found');
        return;
    }
    
    fileList.innerHTML = '';

    try {
        const response = await fetch(`/storage/files/${bucketName}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const result = await response.json();
        const files = result.data || result; // APIレスポンスの構造に合わせて修正

        if (Array.isArray(files)) {
            files.forEach(file => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${file.name}</td>
                    <td>${formatBytes(file.size)}</td>
                    <td>${formatDate(file.lastModified)}</td>
                    <td class="file-actions">
                        ${bucketName !== 'student-ids' ? `
                            <button class="action-button view-button" onclick="viewFile('${bucketName}', '${file.name}')">
                                表示
                            </button>
                        ` : ''}
                        <button class="action-button delete-button" onclick="deleteFile('${bucketName}', '${file.name}')">
                            削除
                        </button>
                    </td>
                `;
                fileList.appendChild(row);
            });
        } else {
            console.warn('Files data is not an array:', files);
        }
    } catch (error) {
        console.error('Failed to fetch file list:', error);
    }
}

// ファイルの表示
async function viewFile(bucketName, fileName) {
    try {
        const response = await fetch(`/storage/view/${bucketName}/${fileName}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        window.open(data.url, '_blank');
    } catch (error) {
        console.error('Failed to view file:', error);
        alert('ファイルの表示に失敗しました');
    }
}

// ファイルの削除
async function deleteFile(bucketName, fileName) {
    if (!confirm(`${fileName} を削除してもよろしいですか？`)) {
        return;
    }

    try {
        const response = await fetch(`/storage/delete/${bucketName}/${fileName}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            await updateBucketStats();
            await updateFileList();
        } else {
            throw new Error('Delete failed');
        }
    } catch (error) {
        console.error('Failed to delete file:', error);
        alert('ファイルの削除に失敗しました');
    }
}

// 最終更新時刻の更新
function updateLastUpdateTime() {
    const lastUpdateElement = document.getElementById('lastUpdate');
    if (lastUpdateElement) {
        const now = new Date();
        const timeString = now.toLocaleTimeString('ja-JP');
        lastUpdateElement.textContent = `最終更新: ${timeString}`;
    }
}
