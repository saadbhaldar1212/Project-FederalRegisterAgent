
// --- Welcome Page Logic ---
const welcomePage = document.getElementById('welcomePage');
const getStartedBtn = document.getElementById('getStartedBtn');
const updatePipelineBtn = document.getElementById('updatePipelineBtn');
const chatbox = document.getElementById('chatbox');
const chatlogs = document.getElementById('chatlogs');
const clearChatBtn = document.getElementById('clearChatBtn');
const dbModal = document.getElementById('dbModal');
const dbTableContainer = document.getElementById('dbTableContainer');
const closeDbModal = document.getElementById('closeDbModal');

// --- Chat Logic ---
const userInput = document.getElementById('userInput');
const sendButton = document.getElementById('sendButton');

const backHomeBtn = document.getElementById('backHomeBtn');
const backHomeModalId = 'backHomeModal';

// Helper to check if there is any user message in chatHistory
function hasUserConversation() {
    return chatHistory.some(msg => msg.role === 'user');
}

// Show a modal for back-to-home confirmation
function showBackHomeModal() {
    let modal = document.getElementById(backHomeModalId);
    if (!modal) {
        modal = document.createElement('div');
        modal.id = backHomeModalId;
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-title">Go Back to Home?</div>
                <div class="modal-message">All the chats will disappear. Are you sure you want to go back to the home page?</div>
                <div class="modal-actions">
                    <button id="confirmBackHome" class="modal-btn danger">Yes, Go Home</button>
                    <button id="cancelBackHome" class="modal-btn">Cancel</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        document.getElementById('cancelBackHome').onclick = () => {
            modal.style.display = 'none';
        };
        document.getElementById('confirmBackHome').onclick = () => {
            modal.style.display = 'none';
            chatbox.style.display = 'none';
            welcomePage.style.display = 'flex';
            // Optionally clear chat history:
            chatHistory = [{ role: "assistant", content: "👋 <strong>Welcome!</strong> How can I help you with Federal Registry documents today?" }];
        };
    }
    modal.style.display = 'flex';
}

if (backHomeBtn) {
    backHomeBtn.onclick = () => {
        if (hasUserConversation()) {
            showBackHomeModal();
        } else {
            chatbox.style.display = 'none';
            welcomePage.style.display = 'flex';
        }
    };
}


let chatHistory = [{ role: "assistant", content: "👋 <strong>Welcome!</strong> How can I help you with Federal Registry documents today?" }];

function formatAssistantText(text) {
    // Bold: **word**
    text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    // Markdown link: [name](url)
    text = text.replace(/\[([^\]]+)\]\((https?:\/\/[^\)]+)\)/g, '<a href="$2" target="_blank">$1</a>');
    // Newlines to <br>
    return text.replace(/\n/g, '<br>');
}

function addMessage(role, text) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', role, 'fade-in');
    if (role === 'assistant') {
        messageDiv.innerHTML = `<strong>Assistant:</strong> ${formatAssistantText(text)}`;
    } else {
        messageDiv.innerHTML = `<strong>You:</strong> ${text.replace(/\n/g, '<br>')}`;
    }
    chatlogs.appendChild(messageDiv);
    chatlogs.scrollTop = chatlogs.scrollHeight;
}

function renderChatHistory() {
    chatlogs.innerHTML = '';
    chatHistory.forEach(msg => addMessage(msg.role, msg.content));
}

async function sendMessage() {
    const query = userInput.value.trim();
    if (!query) return;

    addMessage('user', query);
    chatHistory.push({ role: 'user', content: query });
    userInput.value = '';

    const thinkingDiv = document.createElement('div');
    thinkingDiv.classList.add('thinking');
    thinkingDiv.textContent = 'Assistant is thinking...';
    chatlogs.appendChild(thinkingDiv);
    chatlogs.scrollTop = chatlogs.scrollHeight;

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: query, history: chatHistory }),
        });

        chatlogs.removeChild(thinkingDiv);

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: "Unknown error" }));
            addMessage('assistant', `Error: ${response.status} - ${errorData.detail || "Could not get response."}`);
            return;
        }

        const data = await response.json();
        addMessage('assistant', data.answer);
        chatHistory = data.history;
    } catch (error) {
        chatlogs.removeChild(thinkingDiv);
        addMessage('assistant', 'Sorry, there was an error connecting to the server.');
    }
}

// --- Event Listeners ---
sendButton.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', function (e) {
    if (e.key === 'Enter') sendMessage();
});

getStartedBtn.onclick = () => {
    welcomePage.style.display = 'none';
    chatbox.style.display = 'flex';
    renderChatHistory();
    setTimeout(() => userInput.focus(), 300);
};

clearChatBtn.onclick = () => {
    chatHistory = [{ role: "assistant", content: "👋 <strong>Welcome!</strong> How can I help you with Federal Registry documents today?" }];
    renderChatHistory();
};

// --- Data Pipeline & Database Table ---
updatePipelineBtn.onclick = async () => {
    updatePipelineBtn.disabled = true;
    updatePipelineBtn.textContent = "Updating...";
    try {
        // Run pipeline and get database (implement /run_pipeline backend endpoint)
        const resp = await fetch('/run_data_pipeline', { method: 'POST' });
        if (!resp.ok) throw new Error('Pipeline failed');
        const dbData = await resp.json();
        showDbModal(dbData);
    } catch (e) {
        showDbModal({ error: "Failed to update pipeline or fetch database." });
    }
    updatePipelineBtn.disabled = false;
    updatePipelineBtn.textContent = "Update Data Pipeline";
};

function showDbModal(dbData) {
    dbTableContainer.innerHTML = '';
    if (dbData.error) {
        dbTableContainer.innerHTML = `<div style="color:#dc2626;font-weight:600;">${dbData.error}</div>`;
    } else if (Array.isArray(dbData) && dbData.length > 0) {
        // Render table
        const keys = Object.keys(dbData[0]);
        let html = '<table class="db-table"><thead><tr>';
        keys.forEach(k => html += `<th>${k}</th>`);
        html += '</tr></thead><tbody>';
        dbData.forEach(row => {
            html += '<tr>';
            keys.forEach(k => html += `<td>${row[k]}</td>`);
            html += '</tr>';
        });
        html += '</tbody></table>';
        dbTableContainer.innerHTML = html;
    } else {
        dbTableContainer.innerHTML = '<div>No data found in database.</div>';
    }
    dbModal.style.display = 'flex';
}
closeDbModal.onclick = () => { dbModal.style.display = 'none'; };
dbModal.onclick = (e) => { if (e.target === dbModal) dbModal.style.display = 'none'; };

// --- Optional: ESC to close modal ---
window.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') dbModal.style.display = 'none';
});

// --- Clear Chat Confirmation Modal ---
document.getElementById('clearChatBtn').onclick = function () {
    document.getElementById('clearChatModal').style.display = 'flex';
};
document.getElementById('cancelClearChat').onclick = function () {
    document.getElementById('clearChatModal').style.display = 'none';
};
document.getElementById('confirmClearChat').onclick = function () {
    document.getElementById('clearChatModal').style.display = 'none';
    // Actual clear chat logic:
    chatHistory = [{ role: "assistant", content: "👋 <strong>Welcome!</strong> How can I help you with Federal Registry documents today?" }];
    renderChatHistory();
};

const pipelineProgressContainer = document.getElementById('pipelineProgressContainer');
const pipelineProgressBar = document.getElementById('pipelineProgressBar');
const pipelineProgressFill = document.getElementById('pipelineProgressFill');
const pipelineProgressText = document.getElementById('pipelineProgressText');
const pipelineResultContainer = document.getElementById('pipelineResultContainer');
const pipelineSummary = document.getElementById('pipelineSummary');
const viewDataBtn = document.getElementById('viewDataBtn');

updatePipelineBtn.onclick = async () => {
    updatePipelineBtn.disabled = true;
    pipelineResultContainer.style.display = 'none';
    pipelineProgressContainer.style.display = 'block';
    pipelineProgressFill.style.width = '0%';
    pipelineProgressText.textContent = 'Updating data pipeline...';

    // Animate progress bar (fake progress for UX)
    let progress = 0;
    const progressInterval = setInterval(() => {
        if (progress < 90) {
            progress += Math.random() * 10;
            pipelineProgressFill.style.width = Math.min(progress, 90) + '%';
        }
    }, 300);

    let error = null;
    let total = 0;
    try {
        const resp = await fetch('/run_data_pipeline', { method: 'POST' });
        if (!resp.ok) throw new Error('Pipeline failed');
        // After pipeline, fetch the real row count from database
        const dbResp = await fetch('/get_database', { method: 'GET' });
        if (!dbResp.ok) throw new Error('Could not fetch database');
        const dbData = await dbResp.json();
        total = Array.isArray(dbData) ? dbData.length : 0;
    } catch (e) {
        error = "Failed to update pipeline or fetch database.";
    }
    clearInterval(progressInterval);
    pipelineProgressFill.style.width = '100%';
    pipelineProgressText.textContent = error ? error : 'Pipeline updated successfully!';
    updatePipelineBtn.disabled = false;

    // Show summary and View Data button
    pipelineResultContainer.style.display = 'block';
    if (error) {
        pipelineSummary.textContent = error;
        viewDataBtn.style.display = 'none';
    } else {
        pipelineSummary.textContent = `Total records fetched: ${total}`;
        viewDataBtn.style.display = 'inline-block';
    }
    pipelineProgressContainer.style.display = 'none';
};

// View Data button logic
viewDataBtn.onclick = async () => {
    // Try to fetch real data from database
    let dbData = null;
    let error = null;
    try {
        const resp = await fetch('/get_database', { method: 'GET' });
        if (!resp.ok) throw new Error('Could not fetch database');
        dbData = await resp.json();
    } catch (e) {
        error = "Failed to fetch database.";
    }
    if (error) {
        showDbModal({ error });
    } else {
        showDbModal(dbData);
    }
};