/**
 * TALK TO YOUR DOCUMENT - FINAL COMPLETE VERSION
 */

const API_URL = 'http://localhost:8000';

let currentDocId = null;
let currentFilename = null;
let currentFileType = null;
let currentSummary = null;
let chatHistory = [];
let uploadedFile = null;

// DOM ELEMENTS
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const uploadContainer = document.getElementById('uploadContainer');
const spinnerContainer = document.getElementById('spinnerContainer');
const mainContent = document.getElementById('mainContent');
const previewContent = document.getElementById('previewContent');
const chatMessages = document.getElementById('chatMessages');
const chatInput = document.getElementById('chatInput');
const sendBtn = document.getElementById('sendBtn');
const summaryOverlay = document.getElementById('summaryOverlay');
const summaryContent = document.getElementById('summaryContent');
const toast = document.getElementById('toast');
const toastMessage = document.getElementById('toastMessage');
const actionsContainer = document.getElementById('actionsContainer');

// EVENT LISTENERS
uploadArea.addEventListener('click', () => fileInput.click());
uploadArea.addEventListener('dragover', handleDragOver);
uploadArea.addEventListener('dragleave', handleDragLeave);
uploadArea.addEventListener('drop', handleDrop);
fileInput.addEventListener('change', handleFileSelect);

sendBtn.addEventListener('click', sendMessage);
chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

document.getElementById('newDocBtn').addEventListener('click', newDocument);
document.getElementById('summarizeBtn').addEventListener('click', showSummary);
document.getElementById('exportBtn').addEventListener('click', exportChat);
document.getElementById('clearBtn').addEventListener('click', clearChat);

window.addEventListener('load', function() {
    
    const closeBtn1 = document.getElementById('summaryCloseBtn');
    const closeBtn2 = document.getElementById('summaryCloseBtn2');
    const closeBtn3 = document.getElementById('summary-close');
    const regenBtn1 = document.getElementById('summaryRegenerateBtn');
    const regenBtn2 = document.getElementById('summary-regenerate');
    const exportBtn1 = document.getElementById('summaryExportBtn');
    const exportBtn2 = document.getElementById('summary-export');
    
    // Close buttons
    if (closeBtn1) {
        closeBtn1.onclick = function() {
            console.log('Close button 1 clicked');
            summaryOverlay.classList.remove('active');
            actionsContainer.classList.remove('disabled');
        };
    }
    
    if (closeBtn2) {
        closeBtn2.onclick = function() {
            console.log('Close button 2 clicked');
            summaryOverlay.classList.remove('active');
            actionsContainer.classList.remove('disabled');
        };
    }
    
    if (closeBtn3) {
        closeBtn3.onclick = function() {
            console.log('Close button 3 clicked');
            summaryOverlay.classList.remove('active');
            actionsContainer.classList.remove('disabled');
        };
    }
    
    // Regenerate buttons
    if (regenBtn1) {
        regenBtn1.onclick = async function() {
            console.log('Regenerate button 1 clicked');
            if (!currentDocId) return;
            
            currentSummary = null;
            localStorage.removeItem(`summary_${currentDocId}`);
            
            summaryContent.innerHTML = '<div class="spinner" style="margin: 40px auto;"></div><p style="text-align: center; color: var(--text-secondary);">Regenerating...</p>';
            
            try {
                const response = await fetch(`${API_URL}/summarize`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ doc_id: currentDocId, length: 'length' })
                });
                
                if (!response.ok) throw new Error('Failed');
                
                const data = await response.json();
                summaryContent.innerHTML = formatText(data.summary);
                currentSummary = data.summary;
                localStorage.setItem(`summary_${currentDocId}`, data.summary);
                showToast('✅ Regenerated!', 'success');
            } catch (error) {
                summaryContent.innerHTML = '<p style="color: var(--danger);">❌ Failed</p>';
                showToast('Failed to regenerate', 'error');
            }
        };
    }
    
    if (regenBtn2) {
        regenBtn2.onclick = regenBtn1.onclick;
    }
    
    // Export buttons
    if (exportBtn1) {
        exportBtn1.onclick = function() {
            console.log('Export button 1 clicked');
            if (!currentSummary) {
                showToast('No summary to export', 'error');
                return;
            }
            
            let text = `Document Summary - ${new Date().toLocaleString()}\n`;
            text += `Document: ${currentFilename}\n`;
            text += '='.repeat(60) + '\n\n';
            text += currentSummary;
            
            const blob = new Blob([text], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `summary_${currentFilename}_${Date.now()}.txt`;
            a.click();
            URL.revokeObjectURL(url);
            showToast('💾 Exported!', 'success');
        };
    }
    
    if (exportBtn2) {
        exportBtn2.onclick = exportBtn1.onclick;
    }
});

// UPLOAD FUNCTIONS
function handleDragOver(e) {
    e.preventDefault();
    uploadArea.classList.add('drag-over');
}

function handleDragLeave() {
    uploadArea.classList.remove('drag-over');
}

function handleDrop(e) {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');
    const file = e.dataTransfer.files[0];
    if (file) processFile(file);
}

function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) processFile(file);
}

async function processFile(file) {
    const allowedTypes = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg'];
    if (!allowedTypes.includes(file.type)) {
        showToast('Please upload a PDF or image file', 'error');
        return;
    }

    uploadedFile = file;
    uploadArea.style.display = 'none';
    spinnerContainer.classList.add('active');

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(`${API_URL}/upload`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Upload failed');
        }

        const data = await response.json();
        currentDocId = data.doc_id;
        currentFilename = data.stats.filename;
        currentFileType = data.stats.file_type;

        uploadContainer.classList.add('fade-out');
        
        setTimeout(() => {
            uploadContainer.style.display = 'none';
            mainContent.classList.add('active');
            showDocumentPreview(file);
            showToast('✅ Document uploaded successfully!', 'success');
            loadChatHistory();
            loadSummaryFromCache();
        }, 500);

    } catch (error) {
        console.error('Upload error:', error);
        showToast(error.message, 'error');
        uploadArea.style.display = 'block';
        spinnerContainer.classList.remove('active');
    }
}

function loadSummaryFromCache() {
    if (currentDocId) {
        const savedSummary = localStorage.getItem(`summary_${currentDocId}`);
        if (savedSummary) {
            currentSummary = savedSummary;
        }
    }
}

function showDocumentPreview(file, targetElement = previewContent) {
    if (file.type === 'application/pdf') {
        const objectUrl = URL.createObjectURL(file);
        
        targetElement.innerHTML = `
            <embed 
                src="${objectUrl}#toolbar=0&navpanes=0&scrollbar=1" 
                type="application/pdf"
                width="100%" 
                height="550px" 
                style="border: none; border-radius: 8px;">
            </embed>
        `;
        
        setTimeout(() => {
            const embed = targetElement.querySelector('embed');
            if (!embed || embed.offsetHeight === 0) {
                targetElement.innerHTML = `
                    <div style="text-align: center; padding: 40px; color: var(--text-secondary); background: var(--bg-elevated); border-radius: 8px; height: 550px; display: flex; flex-direction: column; justify-content: center;">
                        <div style="font-size: 5rem; margin-bottom: 20px;">📄</div>
                        <p style="font-size: 1.3rem; margin-bottom: 15px; font-weight: 600;">PDF Uploaded Successfully</p>
                        <p style="font-size: 1rem; color: var(--text-muted);">${file.name}</p>
                        <p style="font-size: 0.9rem; margin-top: 20px;">
                            <a href="${objectUrl}" target="_blank" 
                               style="color: var(--primary); text-decoration: none; padding: 10px 20px; border: 2px solid var(--primary); border-radius: 8px; display: inline-block;">
                               📥 Open PDF in New Tab
                            </a>
                        </p>
                    </div>
                `;
            }
        }, 500);
    } else {
        const reader = new FileReader();
        reader.onload = function(e) {
            targetElement.innerHTML = `
                <img 
                    src="${e.target.result}" 
                    alt="Document preview"
                    style="width: 100%; height: auto; max-height: 550px; object-fit: contain; 
                           border-radius: 8px; display: block; margin: 0 auto;"
                />
            `;
        };
        reader.readAsDataURL(file);
    }
}

// CHAT FUNCTIONS
async function sendMessage() {
    const question = chatInput.value.trim();
    if (!question || !currentDocId) return;

    addMessage(question, 'user');
    chatInput.value = '';

    const originalHTML = sendBtn.innerHTML;
    sendBtn.innerHTML = '<span>Generating...</span>';
    sendBtn.disabled = true;

    const startTime = Date.now();

    try {
        const response = await fetch(`${API_URL}/query/stream`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                doc_id: currentDocId,
                question: question,
                chat_history: chatHistory
            })
        });

        if (!response.ok) {
            throw new Error('Query failed');
        }

        const messageDiv = document.createElement('div');
        messageDiv.className = 'message message-ai';
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageDiv.appendChild(messageContent);
        chatMessages.appendChild(messageDiv);

        let fullAnswer = '';

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            const chunk = decoder.decode(value);
            fullAnswer += chunk;
            messageContent.innerHTML = formatText(fullAnswer);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        const time = ((Date.now() - startTime) / 1000).toFixed(2);
        
        const timestamp = new Date().toLocaleTimeString('en-US', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
        const timeLabel = document.createElement('div');
        timeLabel.className = 'message-timestamp';
        timeLabel.textContent = `${timestamp} • ${time}s`;
        messageDiv.appendChild(timeLabel);

        chatHistory.push({ role: 'user', content: question, timestamp });
        chatHistory.push({ role: 'assistant', content: fullAnswer, timestamp, responseTime: time });
        saveChatHistory();

    } catch (error) {
        console.error('Query error:', error);
        addMessage('❌ Sorry, an error occurred. Please try again.', 'ai');
        showToast(error.message, 'error');
    } finally {
        sendBtn.innerHTML = originalHTML;
        sendBtn.disabled = false;
    }
}

function addMessage(content, type) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message message-${type}`;
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    
    if (type === 'ai') {
        messageContent.innerHTML = formatText(content);
    } else {
        messageContent.textContent = content;
    }
    
    messageDiv.appendChild(messageContent);
    
    const timestamp = new Date().toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
    const timeLabel = document.createElement('div');
    timeLabel.className = 'message-timestamp';
    timeLabel.textContent = timestamp;
    messageDiv.appendChild(timeLabel);
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function formatText(text) {
    text = text.replace(/\n\n+/g, '\n\n');
    text = text.replace(/^(\d+)\.\s+(.+)$/gm, '<strong>$1.</strong> $2');
    text = text.replace(/^[•\-]\s+(.+)$/gm, '• $1');
    text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    text = text.replace(/\*(.+?)\*/g, '<em>$1</em>');
    text = text.replace(/\n/g, '<br>');
    return text;
}

function saveChatHistory() {
    if (currentDocId) {
        localStorage.setItem(`chat_${currentDocId}`, JSON.stringify(chatHistory));
    }
}

function loadChatHistory() {
    if (currentDocId) {
        const saved = localStorage.getItem(`chat_${currentDocId}`);
        if (saved) {
            chatHistory = JSON.parse(saved);
            chatHistory.forEach(msg => {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message message-${msg.role === 'user' ? 'user' : 'ai'}`;
                const messageContent = document.createElement('div');
                messageContent.className = 'message-content';
                
                if (msg.role === 'assistant') {
                    messageContent.innerHTML = formatText(msg.content);
                } else {
                    messageContent.textContent = msg.content;
                }
                
                messageDiv.appendChild(messageContent);
                
                if (msg.timestamp) {
                    const timeLabel = document.createElement('div');
                    timeLabel.className = 'message-timestamp';
                    timeLabel.textContent = msg.responseTime 
                        ? `${msg.timestamp} • ${msg.responseTime}s`
                        : msg.timestamp;
                    messageDiv.appendChild(timeLabel);
                }
                
                chatMessages.appendChild(messageDiv);
            });
            showToast('💬 Chat history restored', 'success');
        }
    }
}

function clearChat() {
    if (!confirm('Clear chat history?')) return;
    
    chatHistory = [];
    chatMessages.innerHTML = `
        <div class="message message-ai">
            <div class="message-content">👋 Chat cleared! Ask me anything about your document.</div>
        </div>
    `;
    
    localStorage.removeItem(`chat_${currentDocId}`);
    showToast('Chat cleared', 'success');
}

function exportChat() {
    if (chatHistory.length === 0) {
        showToast('No chat history to export', 'error');
        return;
    }

    let text = `Chat History - ${new Date().toLocaleString()}\n`;
    text += `Document: ${currentFilename}\n`;
    text += '='.repeat(60) + '\n\n';
    
    chatHistory.forEach(msg => {
        text += `${msg.role === 'user' ? '👤 You' : '🤖 AI'}: ${msg.content}\n\n`;
    });

    downloadFile(text, `chat_${currentFilename}_${Date.now()}.txt`);
    showToast('💾 Chat exported', 'success');
}

// SUMMARY FUNCTIONS
async function showSummary() {
    if (!currentDocId) return;

    // Disable action buttons
    actionsContainer.classList.add('disabled');
    
    // Show summary overlay
    summaryOverlay.classList.add('active');

    // If summary already exists, just show it
    if (currentSummary) {
        summaryContent.innerHTML = formatText(currentSummary);
        return;
    }

    summaryContent.innerHTML = '<div class="spinner" style="margin: 40px auto;"></div><p style="text-align: center; color: var(--text-secondary);">Generating summary...</p>';

    try {
        const response = await fetch(`${API_URL}/summarize`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                doc_id: currentDocId,
                length: 'length'
            })
        });

        if (!response.ok) throw new Error('Summarization failed');

        const data = await response.json();
        const summary = data.summary;
        
        summaryContent.innerHTML = formatText(summary) + 
            `<p style="margin-top: 20px; color: var(--text-muted); font-size: 0.9rem;">⚡ Generated in ${data.response_time}s</p>`;

        currentSummary = summary;
        localStorage.setItem(`summary_${currentDocId}`, summary);

    } catch (error) {
        summaryContent.innerHTML = '<p style="color: var(--danger); text-align: center;">❌ Failed to generate summary</p>';
        showToast(error.message, 'error');
    }
}

async function regenerateSummary() {
    if (!currentDocId) return;

    // Clear cached summary
    currentSummary = null;
    localStorage.removeItem(`summary_${currentDocId}`);
    
    // Show loading
    summaryContent.innerHTML = '<div class="spinner" style="margin: 40px auto;"></div><p style="text-align: center; color: var(--text-secondary);">Regenerating summary...</p>';

    try {
        const response = await fetch(`${API_URL}/summarize`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                doc_id: currentDocId,
                length: 'length'
            })
        });

        if (!response.ok) throw new Error('Summarization failed');

        const data = await response.json();
        const summary = data.summary;
        
        summaryContent.innerHTML = formatText(summary) + 
            `<p style="margin-top: 20px; color: var(--text-muted); font-size: 0.9rem;">⚡ Generated in ${data.response_time}s</p>`;

        currentSummary = summary;
        localStorage.setItem(`summary_${currentDocId}`, summary);
        showToast('✅ Summary regenerated!', 'success');

    } catch (error) {
        summaryContent.innerHTML = '<p style="color: var(--danger); text-align: center;">❌ Failed to generate summary</p>';
        showToast(error.message, 'error');
    }
}

function closeSummary() {
    summaryOverlay.classList.remove('active');
    actionsContainer.classList.remove('disabled');
}

function exportSummary() {
    if (!currentSummary) {
        showToast('No summary to export', 'error');
        return;
    }

    let text = `Document Summary - ${new Date().toLocaleString()}\n`;
    text += `Document: ${currentFilename}\n`;
    text += '='.repeat(60) + '\n\n';
    text += currentSummary;

    downloadFile(text, `summary_${currentFilename}_${Date.now()}.txt`);
    showToast('💾 Summary exported', 'success');
}

// UTILITY FUNCTIONS
function newDocument() {
    if (!confirm('Start with a new document? Current chat will be saved.')) return;

    currentDocId = null;
    currentFilename = null;
    currentFileType = null;
    currentSummary = null;
    chatHistory = [];
    uploadedFile = null;

    mainContent.classList.remove('active');
    uploadContainer.style.display = 'block';
    uploadContainer.classList.remove('fade-out');
    uploadArea.style.display = 'block';
    spinnerContainer.classList.remove('active');
    fileInput.value = '';
    
    previewContent.innerHTML = '';
    chatMessages.innerHTML = `
        <div class="message message-ai">
            <div class="message-content">👋 Hello! I've analyzed your document. Ask me anything about it!</div>
        </div>
    `;

    showToast('📄 Ready for new document', 'success');
}

function showToast(message, type = 'success') {
    toast.className = `toast toast-${type} active`;
    toastMessage.textContent = message;
    setTimeout(() => toast.classList.remove('active'), 3000);
}

function downloadFile(content, filename) {
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
}

// INITIALIZATION
window.addEventListener('load', async () => {
    try {
        const response = await fetch(`${API_URL}/`);
        if (response.ok) {
            console.log('✅ Backend connected');
            showToast('✅ Connected to backend', 'success');
        }
    } catch (error) {
        console.error('❌ Backend connection failed');
        showToast('⚠️ Backend not connected', 'error');
    }
});

setInterval(() => {
    if (chatHistory.length > 0 && currentDocId) {
        saveChatHistory();
    }
}, 30000);

console.log('🧠 Talk to Your Document - Ready');