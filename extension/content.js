console.log("Video RAG Tutor: Script injetado na página!");

const API_URL = "http://localhost:8000";
let currentVideoId = null;
let currentTaskId = null;
let isReady = false;

// Helper to inject the UI
function injectUI() {
    if (document.getElementById('vrag-tutor-container')) {
        return;
    }
    
    console.log("Video RAG Tutor: Construindo interface...");
    if (document.getElementById('vrag-tutor-container')) return;

    const container = document.createElement('div');
    container.id = 'vrag-tutor-container';

    container.innerHTML = `
        <div id="vrag-header">
            <h3>Video RAG Tutor</h3>
            <div id="vrag-controls">
                <button id="vrag-process-btn">Processar</button>
                <button id="vrag-collapse-btn" title="Recolher/Expandir">&#8211;</button>
                <button id="vrag-close-btn" title="Fechar Tutor">&#10005;</button>
            </div>
        </div>
        <div id="vrag-chat-area">
            <div class="vrag-message bot">Olá! Clique em processar para extrair e estudar este vídeo.</div>
        </div>
        <div id="vrag-input-container">
            <input type="text" id="vrag-input" placeholder="Faça uma pergunta..." disabled />
            <button id="vrag-send-btn" disabled>&#10148;</button>
        </div>
    `;

    document.body.appendChild(container);
    attachListeners();
}

function attachListeners() {
    document.getElementById('vrag-process-btn').addEventListener('click', startProcessing);
    document.getElementById('vrag-send-btn').addEventListener('click', sendMessage);
    
    // Botão de Recolher
    document.getElementById('vrag-collapse-btn').addEventListener('click', () => {
        document.getElementById('vrag-tutor-container').classList.toggle('vrag-collapsed');
    });

    // Botão de Fechar
    document.getElementById('vrag-close-btn').addEventListener('click', () => {
        document.getElementById('vrag-tutor-container').remove();
    });

    document.getElementById('vrag-input').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
}

// Escuta a requisição vinda do background.js (quando clica no ícone da extensão)
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "toggle_vrag_tutor") {
        const existing = document.getElementById('vrag-tutor-container');
        if (existing) {
            existing.remove(); // Fecha se já estiver aberto
        } else {
            injectUI(); // Abre se estiver fechado
        }
    }
});

function addMessage(text, sender, timeText = "") {
    const chatArea = document.getElementById('vrag-chat-area');
    const msg = document.createElement('div');
    msg.className = `vrag-message ${sender}`;
    
    let content = "";
    if (timeText) {
        content += `<span class="vrag-timestamp">${timeText}</span>`;
    }
    
    // Tratamento de markdown básico
    text = text.replace(/\*\*(.*?)\*\*/g, '<b>$1</b>');
    text = text.replace(/^### (.*$)/gim, '<h4>$1</h4>');
    text = text.replace(/^## (.*$)/gim, '<h3>$1</h3>');
    text = text.replace(/^# (.*$)/gim, '<h2>$1</h2>');
    text = text.replace(/^\* (.*$)/gim, '<li>$1</li>');
    text = text.replace(/^- (.*$)/gim, '<li>$1</li>');
    text = text.replace(/\n/g, '<br>');
    
    content += text;
    
    msg.innerHTML = content;
    chatArea.appendChild(msg);
    chatArea.scrollTop = chatArea.scrollHeight;
}

async function startProcessing() {
    const url = window.location.href;
    const btn = document.getElementById('vrag-process-btn');
    btn.disabled = true;
    btn.innerText = "Iniciando...";

    try {
        const response = await fetch(`${API_URL}/process`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: url })
        });
        
        const data = await response.json();
        currentTaskId = data.task_id;
        
        addMessage("Processando áudio (Download > Whisper > Embeddings)... Isso pode levar alguns minutos.", "bot");
        pollStatus();
        
    } catch (error) {
        console.error(error);
        addMessage("Erro ao conectar com a API local (O Docker está rodando?).", "bot");
        btn.disabled = false;
        btn.innerText = "Processar Vídeo";
    }
}

async function pollStatus() {
    const btn = document.getElementById('vrag-process-btn');
    
    try {
        const response = await fetch(`${API_URL}/status/${currentTaskId}`);
        const data = await response.json();
        
        if (data.status === "completed") {
            currentVideoId = data.video_id;
            isReady = true;
            btn.innerText = "Concluído";
            document.getElementById('vrag-input').disabled = false;
            document.getElementById('vrag-send-btn').disabled = false;
            addMessage("Transcrição finalizada e vetorizada! O que você quer saber sobre a aula?", "bot");
        } else if (data.status === "failed") {
            addMessage(`Erro no backend: ${data.error}`, "bot");
            btn.disabled = false;
            btn.innerText = "Tentar Novamente";
        } else {
            // "downloading", "transcribing", "vectorizing"
            btn.innerText = data.status;
            setTimeout(pollStatus, 3000); 
        }
    } catch (e) {
        setTimeout(pollStatus, 3000);
    }
}

async function sendMessage() {
    if (!isReady) return;
    
    const input = document.getElementById('vrag-input');
    const text = input.value.trim();
    if (!text) return;

    input.value = "";
    
    // Pega o tempo atual do player se estiver tocando
    const videoElement = document.querySelector('video');
    let currentTime = null;
    let timeText = "Visão Global";
    
    // Se o player estiver rodando ou não estiver no início (mesmo pausado)
    if (videoElement && (videoElement.currentTime > 0)) {
        currentTime = videoElement.currentTime;
        const minutes = Math.floor(currentTime / 60);
        const seconds = Math.floor(currentTime % 60).toString().padStart(2, '0');
        timeText = `@${minutes}:${seconds}`;
    }

    addMessage(text, "user", timeText);
    
    const typingId = "typing-" + Date.now();
    const chatArea = document.getElementById('vrag-chat-area');
    const msg = document.createElement('div');
    msg.id = typingId;
    msg.className = `vrag-message bot`;
    msg.innerText = "Tutor analisando...";
    chatArea.appendChild(msg);
    chatArea.scrollTop = chatArea.scrollHeight;

    try {
        const response = await fetch(`${API_URL}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                video_id: currentVideoId,
                query: text,
                current_time: currentTime // Se null, backend faz Busca Global
            })
        });
        
        const data = await response.json();
        document.getElementById(typingId).remove();
        addMessage(data.response, "bot");
        
    } catch (error) {
        document.getElementById(typingId).remove();
        addMessage("Falha ao comunicar com o Tutor local.", "bot");
    }
}

// YouTube usa navegação SPA, precisamos ouvir o evento deles
document.addEventListener('yt-navigate-finish', () => {
    console.log("Video RAG Tutor: Navegação SPA detectada.");
    isReady = false;
    injectUI();
});

// Tenta injetar com tentativas repetidas caso o DOM do Youtube esteja lento
let attempts = 0;
const interval = setInterval(() => {
    if (document.getElementById('vrag-tutor-container')) {
        clearInterval(interval);
    } else {
        injectUI();
        attempts++;
        if (attempts > 10) clearInterval(interval);
    }
}, 1000);
