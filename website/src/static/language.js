document.addEventListener('DOMContentLoaded', function () {

  (function () {
    var currentLang = 'cs'; // preferred default
    var currentTheme = 'dark';

    function setLanguage(lang) {
      currentLang = lang;

      // <html lang="...">
      document.documentElement.setAttribute('lang', lang);

      // Show/hide content
      document.querySelectorAll('[data-lang]').forEach(function (el) {
        el.style.display = el.getAttribute('data-lang') === lang ? '' : 'none';
      });

      // Update buttons (never hide them)
      document.querySelectorAll('.lang-btn').forEach(function (btn) {
        var isActive = btn.getAttribute('data-lang-btn') === lang;
        btn.classList.toggle('is-active', isActive);
        btn.setAttribute('aria-pressed', isActive ? 'true' : 'false');
      });
    }

    function getPreferredTheme() {
      if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        return 'dark';
      }
      return 'light';
    }

    function setTheme(theme) {
      currentTheme = theme;
      document.documentElement.setAttribute('data-theme', theme);

      document.querySelectorAll('.theme-btn').forEach(function (btn) {
        var isActive = btn.getAttribute('data-theme-btn') === theme;
        btn.classList.toggle('is-active', isActive);
        btn.setAttribute('aria-pressed', isActive ? 'true' : 'false');
      });

      document.dispatchEvent(new CustomEvent('nas:themechange', {
        detail: { theme: theme }
      }));
    }

    function handleLangClick(e) {
      var btn = e.target.closest('.lang-btn');
      if (!btn) return;
      var lang = btn.getAttribute('data-lang-btn');
      if (!lang) return;
      setLanguage(lang);
      if (window.localStorage) {
        localStorage.setItem('nasLang', lang);
      }
    }

    function handleThemeClick(e) {
      var btn = e.target.closest('.theme-btn');
      if (!btn) return;
      var theme = btn.getAttribute('data-theme-btn');
      if (theme !== 'light' && theme !== 'dark') return;
      setTheme(theme);
      if (window.localStorage) {
        localStorage.setItem('nasTheme', theme);
      }
    }

    document.addEventListener('click', handleLangClick);
    document.addEventListener('click', handleThemeClick);

    var saved = window.localStorage && localStorage.getItem('nasLang');
    var savedTheme = window.localStorage && localStorage.getItem('nasTheme');

    // If saved, use it; otherwise use currentLang ('cs')
    if (saved === 'en' || saved === 'cs') {
      setLanguage(saved);
    } else {
      setLanguage(currentLang); // << this is the important change
    }

    if (savedTheme === 'light' || savedTheme === 'dark') {
      setTheme(savedTheme);
    } else {
      setTheme(getPreferredTheme());
    }
  })();
});
