/* =================================================
   main.js - 핵심 인터랙션 (TOC 하이라이트, 헤더 스크롤, 다크모드, 모바일 메뉴)
   ================================================= */

document.addEventListener('DOMContentLoaded', () => {

  // ── 1. 헤더 스크롤 감지 ─────────────────────
  const header = document.getElementById('site-header');
  if (header) {
    window.addEventListener('scroll', () => {
      header.classList.toggle('is-scrolled', window.scrollY > 10);
    }, { passive: true });
  }

  // ── 2. 모바일 햄버거 메뉴 ────────────────────
  const btnHamburger = document.getElementById('btn-hamburger');
  const mobileNav    = document.getElementById('mobile-nav');
  if (btnHamburger && mobileNav) {
    btnHamburger.addEventListener('click', () => {
      const isOpen = mobileNav.classList.toggle('is-open');
      btnHamburger.classList.toggle('is-open', isOpen);
      btnHamburger.setAttribute('aria-expanded', String(isOpen));
      mobileNav.setAttribute('aria-hidden', String(!isOpen));
    });
  }

  // ── 3. 다크/라이트 모드 토글 ─────────────────
  const btnTheme  = document.getElementById('btn-theme');
  const iconMoon  = btnTheme?.querySelector('.icon-moon');
  const iconSun   = btnTheme?.querySelector('.icon-sun');
  const savedTheme = localStorage.getItem('theme') || 'dark';
  document.documentElement.setAttribute('data-theme', savedTheme);
  if (savedTheme === 'light' && iconMoon && iconSun) {
    iconMoon.style.display = 'none';
    iconSun.style.display  = 'block';
  }
  if (btnTheme) {
    btnTheme.addEventListener('click', () => {
      const current = document.documentElement.getAttribute('data-theme');
      const next    = current === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', next);
      localStorage.setItem('theme', next);
      if (iconMoon && iconSun) {
        iconMoon.style.display = next === 'dark' ? 'block' : 'none';
        iconSun.style.display  = next === 'light' ? 'block' : 'none';
      }
    });
  }

  // ── 4. TOC 스크롤 하이라이트 ─────────────────
  const tocLinks = document.querySelectorAll('#toc-nav a');
  if (tocLinks.length > 0) {
    const headings = Array.from(
      document.querySelectorAll('.post-content h2, .post-content h3')
    );
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const id = entry.target.getAttribute('id');
            tocLinks.forEach((link) => {
              link.classList.toggle(
                'is-active',
                link.getAttribute('href') === `#${id}`
              );
            });
          }
        });
      },
      { rootMargin: '-64px 0px -70% 0px' }
    );
    headings.forEach((h) => { if (h.id) observer.observe(h); });
  }

});
