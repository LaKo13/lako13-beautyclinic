'use strict';
document.documentElement.classList.replace('no-js', 'js');
const menuButton = document.querySelector('.menu-toggle');
const menu = document.querySelector('#navigation');
if (menuButton && menu) {
  const closeMenu = (restoreFocus = false) => {
    menu.classList.remove('is-open');
    menuButton.setAttribute('aria-expanded', 'false');
    if (restoreFocus) menuButton.focus();
  };
  menuButton.addEventListener('click', () => {
    const open = menuButton.getAttribute('aria-expanded') !== 'true';
    menuButton.setAttribute('aria-expanded', String(open));
    menu.classList.toggle('is-open', open);
  });
  menu.addEventListener('click', event => {
    if (event.target.closest('a')) closeMenu();
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && menu.classList.contains('is-open')) closeMenu(true);
  });
  document.addEventListener('click', event => {
    if (!menu.contains(event.target) && !menuButton.contains(event.target)) closeMenu();
  });
  window.matchMedia('(min-width: 901px)').addEventListener('change', () => closeMenu());
}
// Maps connect to Google only after the visitor explicitly requests the embed.
for (const button of document.querySelectorAll('[data-map-src]')) {
  button.addEventListener('click', () => {
    const frame = document.createElement('iframe');
    frame.title = button.dataset.mapTitle;
    frame.src = button.dataset.mapSrc;
    frame.loading = 'lazy';
    frame.referrerPolicy = 'no-referrer';
    frame.allowFullscreen = true;
    button.after(frame);
    button.hidden = true;
  }, { once: true });
}
