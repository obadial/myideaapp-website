/* ============================================================
   MyIdeApp Website — Main JS
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {
  I18n.init();
  initScrollAnimations();
  initMobileMenu();
  initLegalTabs();
  initNavbarScroll();
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
      const lang = tab.dataset.legalTab;

      // Update tabs
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');

      // Update content panels
      document.querySelectorAll('.legal-content').forEach(c => {
        c.classList.toggle('active', c.dataset.legalContent === lang);
      });

      // Scroll to top of content
      const body = document.querySelector('.legal-body');
      if (body) body.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });

  // Auto-select based on current language
  const currentLang = I18n.current;
  const matchingTab = document.querySelector(`[data-legal-tab="${currentLang}"]`);
  if (matchingTab) matchingTab.click();
  else {
    // Default to first tab if language not available
    const firstTab = document.querySelector('.legal-tab');
    if (firstTab) firstTab.classList.add('active');
    const firstContent = document.querySelector('.legal-content');
    if (firstContent) firstContent.classList.add('active');
  }
}
