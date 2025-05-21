document.addEventListener('DOMContentLoaded', () => {
  // 1) Подключаем Socket.IO (если бэкенд на том же хосте и порту)
  const socket = io(); // либо io('http://localhost:3000')

  socket.on('connect', () => {
    console.log('Socket.IO connected:', socket.id);
  });

  // 2) Инициализация карты
  const map = L.map('map').setView([51.0, 71.4], 13);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19, attribution: '&copy; OSM'
  }).addTo(map);
  window.droneMarker = L.marker([51.0, 71.4]).addTo(map);

  // 3) Обработка телеметрии
  socket.on('telemetry', data => {
    document.getElementById('altitude').textContent = data.altitude;
    document.getElementById('speed').textContent    = data.speed;
    document.getElementById('battery').textContent  = data.battery;
    document.getElementById('coords').textContent   =
      `${data.lat.toFixed(5)}, ${data.lng.toFixed(5)}`;

    // Обновляем маркер
    const latlng = [data.lat, data.lng];
    window.droneMarker.setLatLng(latlng);
  });

  // 4) Переключение режимов ввода
  let inputMode = 'joystick';
  const toggleBtn = document.getElementById('toggleInput');
  toggleBtn.addEventListener('click', () => {
    inputMode = inputMode === 'joystick' ? 'keyboard' : 'joystick';
    toggleBtn.textContent = inputMode === 'joystick'
      ? 'Использовать клавиатуру'
      : 'Использовать джойстик';
    toggleBtn.classList.toggle('active', inputMode === 'keyboard');
    console.log('Input mode:', inputMode);
  });

  // 5) Джойстик-кнопки
  document.querySelectorAll('.controls button[data-cmd]').forEach(btn => {
    btn.addEventListener('click', () => {
      if (inputMode !== 'joystick') return;
      const cmd = btn.dataset.cmd;
      socket.emit('control', { command: cmd });
      console.log('Joystick command:', cmd);
    });
  });

  // 6) Клавиатурные команды
  window.addEventListener('keydown', e => {
    if (inputMode !== 'keyboard') return;
    const key = e.key.toUpperCase();
    const mapKeyToCmd = {
      W: 'UP',
      S: 'DOWN',
      A: 'RIGHT',
      D: 'LEFT',
      Z: 'TILT_FORWARD',
      X: 'TILT_BACK',
      C: 'TILT_LEFT',
      V: 'TILT_RIGHT'
    };
    const cmd = mapKeyToCmd[key];
    if (cmd) {
      socket.emit('control', { command: cmd });
      console.log(`Keyboard command: ${key} → ${cmd}`);
    }
  });
});
