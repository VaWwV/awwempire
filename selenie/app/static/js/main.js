const socket = io();

// Обновление статуса голосового управления
function updateVoiceStatus(active) {
    const statusElement = document.getElementById('voiceStatus');
    statusElement.className = 'status-indicator ' + (active ? 'active' : '');
    statusElement.querySelector('span').textContent = active ? 'Активно' : 'Неактивно';
}

// Обновление статуса браузера
function updateBrowserStatus(active) {
    const statusElement = document.getElementById('browserStatus');
    statusElement.className = 'status-indicator ' + (active ? 'active' : '');
    statusElement.querySelector('span').textContent = active ? 'Запущен' : 'Не запущен';
}

// Добавление сообщения в лог
function addLog(message) {
    const logContainer = document.getElementById('logContainer');
    const logEntry = document.createElement('div');
    logEntry.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
    logContainer.appendChild(logEntry);
    logContainer.scrollTop = logContainer.scrollHeight;
}

// Обработка событий от сервера
socket.on('voice_status', (data) => {
    updateVoiceStatus(data.active);
    addLog(`Голосовое управление ${data.active ? 'включено' : 'выключено'}`);
});

socket.on('browser_status', (data) => {
    updateBrowserStatus(data.active);
    addLog(`Браузер ${data.active ? 'запущен' : 'остановлен'}`);
});

socket.on('command_recognized', (data) => {
    addLog(`Распознана команда: ${data.command}`);
}); 