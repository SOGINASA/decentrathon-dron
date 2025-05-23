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
  