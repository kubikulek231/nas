document.addEventListener('DOMContentLoaded', function () {

  (function () {
    var currentLang = 'cs'; // preferred default

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

    document.addEventListener('click', handleLangClick);

    var saved = window.localStorage && localStorage.getItem('nasLang');

    // If saved, use it; otherwise use currentLang ('cs')
    if (saved === 'en' || saved === 'cs') {
      setLanguage(saved);
    } else {
      setLanguage(currentLang); // << this is the important change
    }
  })();
});
