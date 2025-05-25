// main.js

// Линейная интерполяция
function lerp(a, b, t) {
  return a + (b - a) * t;
}

// Вычисление расстояния между двумя геокоординатами (метры)
function getDistance(lat1, lon1, lat2, lon2) {
  const R = 6371000, toRad = x => x * Math.PI / 180;
  const dLat = toRad(lat2 - lat1), dLon = toRad(lon2 - lon1);
  const a = Math.sin(dLat/2)**2 +
            Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) *
            Math.sin(dLon/2)**2;
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

// Анимация маршрута для маркера дрона
function animateRoute(points, speed) {
  let idx = 0, t = 0;
  const marker = L.marker(points[0], {
    icon: L.icon({ iconUrl: '/static/4320278.png', iconSize: [30, 30] })
  }).addTo(map).bindPopup('CoDrone').openPopup();

  function moveNext() {
    if (idx >= points.length - 1) {
      marker.setLatLng(points[points.length - 1])
            .bindPopup('Дрон прибыл').openPopup();
      return;
    }
    const [sLat, sLng] = points[idx],
          [eLat, eLng] = points[idx+1],
          dist = getDistance(sLat, sLng, eLat, eLng),
          duration = dist / speed;
    t = 0;

    function step() {
      t += 1 / (60 * duration);
      if (t >= 1) {
        marker.setLatLng([eLat, eLng]);
        idx++;
        moveNext();
        return;
      }
      const lat = lerp(sLat, eLat, t),
            lng = lerp(sLng, eLng, t);
      marker.setLatLng([lat, lng]);
      map.setView([lat, lng]);
      requestAnimationFrame(step);
    }
    step();
  }

  moveNext();
}

document.addEventListener('DOMContentLoaded', () => {
  // ===== Socket.IO =====
  const socket = io();
  socket.on('connect', () => console.log('Socket.IO connected:', socket.id));

  // Центр карт
  const coords = [54.865556, 69.133889];

  // ===== Карта осадков (RainViewer) =====
  const weatherMap = L.map('weather', {
    zoomControl: false,
    attributionControl: false
  }).setView(coords, 6);

  // 1) базовый слой OpenStreetMap
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap'
  }).addTo(weatherMap);

  // 2) пробуем дождевой радар RainViewer
  fetch('https://api.rainviewer.com/public/maps.json')
    .then(res => res.json())
    .then(data => {
      const host = data.host;             // например "tilecache.rainviewer.com"
      const past = (data.radar.past || []);
      const now = (data.radar.nowcast || []);
      const frames = past.concat(now);
      if (!frames.length) {
        console.warn('RainViewer: нет ни past, ни nowcast кадров');
        L.control
         .attribution({ prefix: false })
         .addAttribution('Нет данных осадков')
         .addTo(weatherMap);
        return;
      }
      const lastTime = frames[frames.length - 1].time;
      L.tileLayer(
        `https://${host}/v2/radar/${lastTime}/256/{z}/{x}/{y}/2/1_1.png`, {
          opacity: 0.5,
          attribution: '&copy; RainViewer'
        }
      ).addTo(weatherMap);
    })
    .catch(err => {
      console.error('Не удалось загрузить RainViewer:', err);
      L.control
        .attribution({ prefix: false })
        .addAttribution('Ошибка загрузки осадков')
        .addTo(weatherMap);
    });

  // ===== Карта дрона (OpenStreetMap) =====
  window.map = L.map('map').setView(coords, 18);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap'
  }).addTo(map);

  // ===== Анимация маршрута =====
  const routePoints = [
    [54.865556, 69.133889],
    [54.865683, 69.134047],
    [54.865918, 69.133639]
  ];
  animateRoute(routePoints, 1);

  // ===== Телеметрия =====
  socket.on('telemetry', data => {
    document.getElementById('speed')   && (document.getElementById('speed').textContent   = data.speed);
    document.getElementById('battery') && (document.getElementById('battery').textContent = data.battery);
    map.setView([data.lat, data.lng]);
  });

  // ===== Управление =====
  let inputMode = 'joystick';
  const toggleBtn = document.getElementById('toggleInput');
  toggleBtn?.addEventListener('click', () => {
    inputMode = inputMode === 'joystick' ? 'keyboard' : 'joystick';
    toggleBtn.textContent = inputMode === 'joystick'
      ? 'Использовать клавиатуру'
      : 'Использовать джойстик';
    toggleBtn.classList.toggle('active', inputMode === 'keyboard');
  });

  document.querySelectorAll('.controls button[data-cmd]')
    .forEach(btn => btn.addEventListener('click', () => {
      if (inputMode !== 'joystick') return;
      socket.emit('control', { command: btn.dataset.cmd });
    }));

  window.addEventListener('keydown', e => {
    if (inputMode !== 'keyboard') return;
    const keyMap = {
      W: 'UP', S: 'DOWN', A: 'RIGHT', D: 'LEFT',
      Z: 'TILT_FORWARD', X: 'TILT_BACK',
      C: 'TILT_LEFT', V: 'TILT_RIGHT',
      Q: 'TAKE_OFF',   E: 'LAND'
    };
    const cmd = keyMap[e.key.toUpperCase()];
    if (cmd) socket.emit('control', { command: cmd });
  });
});
