// Инициализация карты
const map = L.map('map').setView([54.865699, 69.134297], 13);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  maxZoom: 19, attribution: '&copy; OSM'
}).addTo(map);

// Маркер дрона
const droneMarker = L.marker([54.865699, 69.134297]).addTo(map);

// Подключаем Socket.IO
const socket = io();  // предполагается тот же хост

socket.on('connect', () => {
  console.log('Connected, id=', socket.id);
});

// Раз в секунду ожидаем обновления позиции:
// backend должен эмитить событие "drone:telemetry" с { lat, lng, altitude, speed, battery }
socket.on('drone:telemetry', data => {
  const { lat, lng, altitude, speed, battery } = data;
  droneMarker.setLatLng([lat, lng]);
  document.getElementById('drone-coords').textContent = `${lat.toFixed(5)}, ${lng.toFixed(5)}`;
  document.getElementById('drone-alt').textContent    = `${altitude} м`;
  document.getElementById('drone-speed').textContent  = `${speed} м/с`;
  document.getElementById('drone-batt').textContent   = `${battery} %`;
});

// Для примера: если хотите вручную протестировать без бэкенда:
// setInterval(() => {
//   const lat = 54.865699 + (Math.random()-0.5)*0.01;
//   const lng = 69.134297 + (Math.random()-0.5)*0.01;
//   socket.emit('drone:telemetry', { lat, lng, altitude:50, speed:10, battery:80 });
// }, 2000);

// sidebar.js

document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.querySelector('.dg-sidebar');
    const overlay = document.querySelector('.dg-overlay');
    const btnMenu = document.querySelector('.dg-btn-menu');
    const btnClose = document.querySelector('.dg-close-sidebar');
  
    function openMenu() {
      sidebar.classList.add('open');
      overlay.classList.add('open');
    }
    function closeMenu() {
      sidebar.classList.remove('open');
      overlay.classList.remove('open');
    }
  
    btnMenu.addEventListener('click', openMenu);
    btnClose.addEventListener('click', closeMenu);
    overlay.addEventListener('click', closeMenu);
  });
  