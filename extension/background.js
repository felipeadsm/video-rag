chrome.action.onClicked.addListener((tab) => {
    // Só manda a mensagem se estiver em uma página de vídeo do YouTube
    if (tab.url && tab.url.includes("youtube.com/watch")) {
        chrome.tabs.sendMessage(tab.id, { action: "toggle_vrag_tutor" }).catch(() => {
            // Ignora o erro se a aba ainda não carregou o content script
        });
    }
});
