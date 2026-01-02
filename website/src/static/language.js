document.addEventListener('DOMContentLoaded', function () {
  (function () {
    var currentLang = 'en';

    function setLanguage(lang) {
      currentLang = lang;
      document.documentElement.setAttribute('lang', lang);

      document.querySelectorAll('[data-lang]').forEach(function (el) {
        el.style.display = el.getAttribute('data-lang') === lang ? '' : 'none';
      });

      document.querySelectorAll('.lang-btn').forEach(function (btn) {
        var isActive = btn.getAttribute('data-lang') === lang;
        btn.classList.toggle('is-active', isActive);
        btn.setAttribute('aria-pressed', isActive ? 'true' : 'false');
      });
    }

    function handleLangClick(e) {
      var btn = e.target.closest('.lang-btn');
      if (!btn) return;
      var lang = btn.getAttribute('data-lang');
      if (!lang) return;
      setLanguage(lang);
      if (window.localStorage) {
        localStorage.setItem('nasLang', lang);
      }
    }

    document.addEventListener('click', handleLangClick);

    var saved = window.localStorage && localStorage.getItem('nasLang');
    if (saved === 'en' || saved === 'cs') {
      setLanguage(saved);
    } else {
      setLanguage('en');
    }
  })();
});
