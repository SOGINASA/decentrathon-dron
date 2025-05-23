document.addEventListener('DOMContentLoaded', () => {
    // 1) Получение списка миссий (пока статично)
    // В будущем заменить на fetch('/api/missions')
    const missions = [
      {
        id: 1,
        lat: 51.16050,
        lng: 71.47040,
        address: 'проспект Достык 100',
        time: '2025-05-22T15:00:00'
      }
    ];
  
    // 2) Обработчик клика по координатам
    const modal = document.getElementById('mapModal');
    const closeBtn = modal.querySelector('.close');
    const coordsLinks = document.querySelectorAll('.coords');
  
    coordsLinks.forEach(link => {
      link.addEventListener('click', e => {
        e.preventDefault();
        const lat = parseFloat(link.dataset.lat);
        const lng = parseFloat(link.dataset.lng);
  
        // Показать модалку
        modal.style.display = 'block';
  
        // Инициализировать или обновить карту
        setTimeout(() => {
          // если карта ещё не создана
          if (!modal._map) {
            modal._map = L.map('modalMap').setView([lat, lng], 15);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
              maxZoom: 19,
              attribution: '&copy; OSM'
            }).addTo(modal._map);
            modal._marker = L.marker([lat, lng]).addTo(modal._map);
          } else {
            modal._map.setView([lat, lng], 15);
            modal._marker.setLatLng([lat, lng]);
          }
        }, 100);
      });
    });
  
    // Закрытие модалки
    closeBtn.addEventListener('click', () => {
      modal.style.display = 'none';
    });
    window.addEventListener('click', e => {
      if (e.target === modal) modal.style.display = 'none';
    });
  });
  