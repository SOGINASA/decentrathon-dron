function lerp(a, b, t) {
  return a + (b - a) * t;
}

function getDistance(lat1, lon1, lat2, lon2) {
  const R = 6371000;
  const toRad = x => x * Math.PI / 180;
  const dLat = toRad(lat2 - lat1);
  const dLon = toRad(lon2 - lon1);
  const a = Math.sin(dLat / 2) ** 2 +
            Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) *
            Math.sin(dLon / 2) ** 2;
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

function animateRoute(points, speed) {
  let index = 0;
  let t = 0;
  const marker = L.marker(points[0], {
    icon: L.icon({
      iconUrl: '/static/4320278.png',
      iconSize: [30, 30]
    })
  }).addTo(map).bindPopup('CoDrone').openPopup();

  function moveToNextSegment() {
    if (index >= points.length - 1) {
      marker.setLatLng(points[points.length - 1]); // установить точно в финальную точку
      marker.bindPopup('Дрон прибыл').openPopup(); // опционально: попап
      return;
    }
  
    const [startLat, startLng] = points[index];
    const [endLat, endLng] = points[index + 1];
    const segmentDistance = getDistance(startLat, startLng, endLat, endLng);
    const segmentDuration = segmentDistance / speed;
    t = 0;
  
    function step() {
      t += 1 / (60 * segmentDuration);
      if (t >= 1) {
        marker.setLatLng([endLat, endLng]); // точно в конец отрезка
        index++;
        moveToNextSegment();
        return;
      }
      const lat = lerp(startLat, endLat, t);
      const lng = lerp(startLng, endLng, t);
      marker.setLatLng([lat, lng]);
      map.setView([lat, lng]);
      requestAnimationFrame(step);
    }
  
    step();
  }
  

  moveToNextSegment();
}

document.addEventListener('DOMContentLoaded', () => {
  const socket = io();
  socket.on('connect', () => console.log('Socket.IO connected:', socket.id));

  const coords = [54.865556, 69.133889]; // Первая точка маршрута
  window.map = L.map('map').setView(coords, 18);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19, attribution: '&copy; OpenStreetMap'
  }).addTo(map);

  // Координаты рассчитаны заранее
  const routePoints = [
    [54.865556, 69.133889],  // A
    [54.865683, 69.134047],  // B
    [54.865918, 69.133639]   // Новый C: ~30 метров от B по направлению 315.03°
  ];
  
  const droneSpeed = 1;

  animateRoute(routePoints, droneSpeed);

  // Телеметрия (если актуально)
  socket.on('telemetry', data => {
    document.getElementById('altitude') && (document.getElementById('altitude').textContent = data.altitude);
    document.getElementById('speed') && (document.getElementById('speed').textContent = data.speed);
    document.getElementById('battery') && (document.getElementById('battery').textContent = data.battery);
    document.getElementById('coords') && (document.getElementById('coords').textContent =
      `${data.lat.toFixed(5)}, ${data.lng.toFixed(5)}`);
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