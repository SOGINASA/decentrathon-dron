// order.js

let map;
let route;
let startCoords = null, endCoords = null;
let picking = null;  // 'start' или 'end'

// Ограничивающий прямоугольник Петропавловска
const cityBounds = [
  [54.70, 68.90],  // юго-запад
  [55.05, 69.50]   // северо-восток
];

ymaps.ready(init);

function init() {
  map = new ymaps.Map('map', {
    center: [54.8796, 69.1754],
    zoom: 12,
    controls: []
  });

  // Клик по карте для выбора точки
  map.events.add('click', onMapClick);

  // Кнопки «Выбрать на карте»
  document.getElementById('pick-start')
          .addEventListener('click', () => { picking = 'start'; });
  document.getElementById('pick-end')
          .addEventListener('click', () => { picking = 'end'; });

  // Ручной ввод адресов
  document.getElementById('start-address')
          .addEventListener('change', onAddressChange);
  document.getElementById('end-address')
          .addEventListener('change', onAddressChange);
}

// Обработка клика на карте
function onMapClick(e) {
  if (!picking) return;

  const coords = e.get('coords');
  ymaps.geocode(coords, {
    boundedBy: cityBounds,
    strictBounds: true,
    results: 1
  }).then(res => {
    if (!res.geoObjects.getLength()) {
      alert('Метка за пределами Петропавловска');
      picking = null;
      return;
    }
    const first = res.geoObjects.get(0);
    applyGeocodeResult(picking, coords, first.getAddressLine());
  });
}

// Обработка ручного ввода адреса
function onAddressChange(e) {
  const id    = e.target.id;      // 'start-address' или 'end-address'
  const value = e.target.value;
  if (!value) return;

  ymaps.geocode(value, {
    boundedBy: cityBounds,
    strictBounds: true,
    results: 1
  }).then(res => {
    if (!res.geoObjects.getLength()) {
      alert('Адрес не найден в Петропавловске');
      return;
    }
    const geo = res.geoObjects.get(0);
    const coords = geo.geometry.getCoordinates();
    const type = id === 'start-address' ? 'start' : 'end';
    applyGeocodeResult(type, coords, geo.getAddressLine());
  });
}

// Общий код применения результатов геокодинга
function applyGeocodeResult(type, coords, address) {
  if (type === 'start') {
    startCoords = coords;
    document.getElementById('start-address').value = address;
    setPlacemark('start', coords);
  } else {
    endCoords = coords;
    document.getElementById('end-address').value = address;
    setPlacemark('end', coords);
  }
  picking = null;
  tryBuildRoute();
}

// Установка метки на карте
function setPlacemark(type, coords) {
  const existing = (type === 'start') ? window.startMark : window.endMark;
  if (existing) {
    map.geoObjects.remove(existing);
  }
  const mark = new ymaps.Placemark(coords, {}, {
    preset: type === 'start'
      ? 'islands#greenDotIcon'
      : 'islands#redDotIcon'
  });
  map.geoObjects.add(mark);
  if (type === 'start') window.startMark = mark;
  else                  window.endMark   = mark;
}

// Построение маршрута, если обе точки заданы
function tryBuildRoute() {
  if (!startCoords || !endCoords) return;

  // Удаляем предыдущий маршрут
  if (route) {
    map.geoObjects.remove(route);
  }

  ymaps.route([startCoords, endCoords], { mapStateAutoApply: true })
    .then(r => {
      route = r;
      map.geoObjects.add(route);
      updatePrice(route.getLength());
    });
}

// Расчёт и отображение цены
function updatePrice(lengthMeters) {
  const km    = lengthMeters / 1000;
  const price = Math.ceil(km * 100); // например, 100₸ за км
  document.getElementById('price').textContent = price + '₸';
  document.getElementById('order-btn').disabled = false;
}
