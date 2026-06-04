/* Re Jobs — main.js */

(function () {
  'use strict';

  // Map Django message levels to Bootstrap alert classes
  document.querySelectorAll('.alert').forEach(function (el) {
    if (el.classList.contains('alert-error')) {
      el.classList.remove('alert-error');
      el.classList.add('alert-danger');
    }
    if (el.classList.contains('alert-debug')) {
      el.classList.remove('alert-debug');
      el.classList.add('alert-secondary');
    }
  });

  // Auto-dismiss success alerts after 4 seconds
  document.querySelectorAll('.alert-success').forEach(function (el) {
    setTimeout(function () {
      var bsAlert = bootstrap.Alert.getOrCreateInstance(el);
      bsAlert.close();
    }, 4000);
  });

  // Dark / light theme toggle
  var html = document.documentElement;
  var toggleBtn = document.getElementById('theme-toggle');
  var themeIcon = document.getElementById('theme-icon');

  function applyTheme(theme) {
    html.setAttribute('data-bs-theme', theme);
    localStorage.setItem('rj-theme', theme);
    if (themeIcon) {
      themeIcon.className = theme === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-fill';
    }
  }

  // Set icon to match current theme on load
  applyTheme(localStorage.getItem('rj-theme') || 'light');

  if (toggleBtn) {
    toggleBtn.addEventListener('click', function () {
      var current = html.getAttribute('data-bs-theme');
      applyTheme(current === 'dark' ? 'light' : 'dark');
    });
  }

})();
