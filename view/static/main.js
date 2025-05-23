document.addEventListener('DOMContentLoaded', () => {
  // Socket.IO
  const socket = io(); 
  socket.on('connect', () => console.log('Socket.IO connected:', socket.id));

  // Инициализация карты на фиксированных координатах
  const coords = [54.865699, 69.134297];
  const map = L.map('map').setView(coords, 15);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19, attribution: '&copy; OpenStreetMap'
  }).addTo(map);
  L.marker(coords).addTo(map)
    .bindPopup('Текущее положение дрона')
    .openPopup();

  // Обновление телеметрии и карты при новых данных
  socket.on('telemetry', data => {
    document.getElementById('altitude').textContent = data.altitude;
    document.getElementById('speed').textContent    = data.speed;
    document.getElementById('battery').textContent  = data.battery;
    document.getElementById('coords').textContent   =
      `${data.lat.toFixed(5)}, ${data.lng.toFixed(5)}`;
    map.setView([data.lat, data.lng]);
  });

  // Код управления (клавиатура/джойстик) без изменений...
  let inputMode = 'joystick';
  const toggleBtn = document.getElementById('toggleInput');
  toggleBtn && toggleBtn.addEventListener('click', () => {
    inputMode = inputMode === 'joystick' ? 'keyboard' : 'joystick';
    toggleBtn.textContent = inputMode === 'joystick'
      ? 'Использовать клавиатуру'
      : 'Использовать джойстик';
    toggleBtn.classList.toggle('active', inputMode === 'keyboard');
    console.log('Input mode:', inputMode);
  });
  document.querySelectorAll('.controls button[data-cmd]')
    .forEach(btn => btn.addEventListener('click', () => {
      if (inputMode !== 'joystick') return;
      const cmd = btn.dataset.cmd;
      socket.emit('control', { command: cmd });
      console.log('Joystick command:', cmd);
    }));
  window.addEventListener('keydown', e => {
    if (inputMode !== 'keyboard') return;
    const M = { W:'UP', S:'DOWN', A:'RIGHT', D:'LEFT',
                Z:'TILT_FORWARD', X:'TILT_BACK',
                C:'TILT_LEFT', V:'TILT_RIGHT' };
    const cmd = M[e.key.toUpperCase()];
    if (cmd) {
      socket.emit('control', { command: cmd });
      console.log(`Keyboard command: ${e.key.toUpperCase()} → ${cmd}`);
    }
  });
});
