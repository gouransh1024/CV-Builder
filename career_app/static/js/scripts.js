(function () {
  'use strict';

  // ========== Tab activation from URL ==========
  var hash = window.location.hash;
  var params = new URLSearchParams(window.location.search);
  var tabParam = params.get('tab');
  if (tabParam === 'analyzer' || hash === '#analyzer') {
    var analyzerTab = document.getElementById('analyzer-tab');
    if (analyzerTab && typeof bootstrap !== 'undefined') {
      var tab = new bootstrap.Tab(analyzerTab);
      tab.show();
    }
  }

  // ========== Auto-dismiss alerts after 5s ==========
  document.querySelectorAll('.alert-dismissible').forEach(function (el) {
    setTimeout(function () {
      if (typeof bootstrap !== 'undefined') {
        var bsAlert = bootstrap.Alert.getOrCreateInstance(el);
        if (bsAlert) bsAlert.close();
      }
    }, 5000);
  });

  // ========== PWA Install Prompt ==========
  var deferredPrompt = null;
  window.addEventListener('beforeinstallprompt', function (e) {
    e.preventDefault();
    deferredPrompt = e;
    // Show install button if exists
    var installBtn = document.getElementById('pwa-install-btn');
    if (installBtn) {
      installBtn.style.display = 'inline-block';
      installBtn.addEventListener('click', function () {
        if (deferredPrompt) {
          deferredPrompt.prompt();
          deferredPrompt.userChoice.then(function () {
            deferredPrompt = null;
            installBtn.style.display = 'none';
          });
        }
      });
    }
  });

  // ========== Viewport height fix for mobile browsers ==========
  function setVH() {
    var vh = window.innerHeight * 0.01;
    document.documentElement.style.setProperty('--vh', vh + 'px');
  }
  setVH();
  window.addEventListener('resize', setVH);

  // ========== Prevent double-tap zoom on buttons (iOS fix) ==========
  var lastTouchEnd = 0;
  document.addEventListener('touchend', function (e) {
    var now = Date.now();
    if (now - lastTouchEnd <= 300) {
      if (e.target.tagName === 'BUTTON' || e.target.tagName === 'A' || e.target.closest('button, a')) {
        e.preventDefault();
      }
    }
    lastTouchEnd = now;
  }, false);

  // ========== Close mobile nav on link click ==========
  var navbarCollapse = document.querySelector('.navbar-collapse');
  if (navbarCollapse) {
    navbarCollapse.querySelectorAll('.nav-link').forEach(function (link) {
      link.addEventListener('click', function () {
        if (navbarCollapse.classList.contains('show') && typeof bootstrap !== 'undefined') {
          var bsCollapse = bootstrap.Collapse.getInstance(navbarCollapse);
          if (bsCollapse) bsCollapse.hide();
        }
      });
    });
  }

  // ========== File input: show filename on mobile ==========
  document.querySelectorAll('input[type="file"]').forEach(function (input) {
    input.addEventListener('change', function () {
      var label = input.closest('.mb-3, .form-group')?.querySelector('.form-label, label');
      if (this.files && this.files.length > 0 && label) {
        var origText = label.dataset.origText || label.textContent;
        label.dataset.origText = origText;
        label.textContent = 'Selected: ' + this.files[0].name;
      }
    });
  });

  // ========== Online/Offline indicator ==========
  function updateOnlineStatus() {
    var indicator = document.getElementById('offline-indicator');
    if (!navigator.onLine) {
      if (!indicator) {
        indicator = document.createElement('div');
        indicator.id = 'offline-indicator';
        indicator.style.cssText = 'position:fixed;bottom:0;left:0;right:0;background:#dc3545;color:#fff;text-align:center;padding:8px;font-size:14px;z-index:9999;';
        indicator.textContent = 'You are offline. Some features may not work.';
        document.body.appendChild(indicator);
      }
    } else if (indicator) {
      indicator.remove();
    }
  }
  window.addEventListener('online', updateOnlineStatus);
  window.addEventListener('offline', updateOnlineStatus);
  updateOnlineStatus();

})();
