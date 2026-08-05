/* ============================================================
   MyIdeApp Website — Main JS
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {
  I18n.init();
  initScrollAnimations();
  initMobileMenu();
  initLegalTabs();
  initNavbarScroll();
  initCarouselDrag();
});

/* ─── Scroll Animations ──────────────────────────────────── */
function initScrollAnimations() {
  const els = document.querySelectorAll('.fade-up');
  if (!els.length) return;
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.classList.add('visible');
        observer.unobserve(e.target);
      }
    });
  }, { threshold: 0.12 });
  els.forEach(el => observer.observe(el));
}

/* ─── Navbar Scroll ──────────────────────────────────────── */
function initNavbarScroll() {
  const navbar = document.querySelector('.navbar');
  if (!navbar) return;
  window.addEventListener('scroll', () => {
    navbar.style.background = window.scrollY > 20
      ? 'rgba(8, 9, 26, 0.92)'
      : 'rgba(8, 9, 26, 0.72)';
  }, { passive: true });
}

/* ─── Mobile Menu ────────────────────────────────────────── */
function initMobileMenu() {
  const hamburger = document.querySelector('.hamburger');
  const mobileNav = document.querySelector('.mobile-nav');
  if (!hamburger || !mobileNav) return;

  hamburger.addEventListener('click', () => {
    const isOpen = mobileNav.classList.toggle('open');
    hamburger.setAttribute('aria-expanded', isOpen);
    document.body.style.overflow = isOpen ? 'hidden' : '';
  });

  mobileNav.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
      mobileNav.classList.remove('open');
      document.body.style.overflow = '';
    });
  });
}

/* ─── Legal Page Tabs ────────────────────────────────────── */
function initLegalTabs() {
  const tabs = document.querySelectorAll('.legal-tab');
  if (!tabs.length) return;

  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      // Un onglet légal change la langue de toute la page : garder deux
      // sélecteurs désynchronisés (en-tête en anglais, corps en français)
      // était précisément le défaut à corriger.
      I18n.apply(tab.dataset.legalTab);

      const body = document.querySelector('.legal-body');
      if (body) body.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });

  // L'affichage initial est posé par I18n.apply(), appelé avant nous : rien à
  // déclencher ici. Simuler un clic ferait défiler la page dès son ouverture.
}

/* ─── Carousel drag-to-scroll ────────────────────────────── */
function initCarouselDrag() {
  const carousel = document.querySelector('.apps-carousel');
  if (!carousel) return;
  let isDown = false, startX, scrollLeft;
  carousel.addEventListener('mousedown', e => {
    isDown = true;
    startX = e.pageX - carousel.offsetLeft;
    scrollLeft = carousel.scrollLeft;
  });
  carousel.addEventListener('mouseleave', () => { isDown = false; });
  carousel.addEventListener('mouseup', () => { isDown = false; });
  carousel.addEventListener('mousemove', e => {
    if (!isDown) return;
    e.preventDefault();
    const x = e.pageX - carousel.offsetLeft;
    carousel.scrollLeft = scrollLeft - (x - startX) * 1.2;
  });
}
