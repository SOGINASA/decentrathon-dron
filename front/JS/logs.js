document.addEventListener('DOMContentLoaded', () => {
    const socket = io(); // или io('http://localhost:3000')
    const logList = document.getElementById('logList');
  
    // Пример: при подключении добавим сообщение
    appendLog(`Connected as ${socket.id}`);
  
    // Получаем события лога от сервера
    socket.on('log', msg => {
      appendLog(msg);
    });
  
    // Также можем локально логировать управление
    socket.on('telemetry', data => {
      // если не нужно, закомментируйте
      appendLog(`[Telemetry] Alt:${data.altitude}m Spd:${data.speed}m/s Bat:${data.battery}%`);
    });
  
    function appendLog(text) {
      const entry = document.createElement('div');
      entry.className = 'log-entry';
      entry.textContent = `[${new Date().toLocaleTimeString()}] ${text}`;
      logList.appendChild(entry);
      // Прокрутка вниз
      logList.scrollTop = logList.scrollHeight;
    }
  });
  