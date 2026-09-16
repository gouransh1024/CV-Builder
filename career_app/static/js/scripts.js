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

  // ========== Theme toggle ==========
  var themeToggleBtn = document.getElementById('theme-toggle-btn');
  var savedTheme = localStorage.getItem('scg-theme');
  if (savedTheme) {
    document.documentElement.setAttribute('data-theme', savedTheme);
  }
  if (themeToggleBtn) {
    themeToggleBtn.addEventListener('click', function () {
      var current = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', current);
      localStorage.setItem('scg-theme', current);
      themeToggleBtn.innerHTML = current === 'dark'
        ? '<i class="fas fa-sun me-2"></i>Light'
        : '<i class="fas fa-moon me-2"></i>Dark';
    });
  }

  // ========== Analyzer progress animation ==========
  var analyzerForm = document.getElementById('analyzer-form');
  if (analyzerForm) {
    analyzerForm.addEventListener('submit', function () {
      var panel = document.getElementById('analysis-progress');
      var stepsEl = document.getElementById('analysis-steps');
      var bar = panel ? panel.querySelector('.progress-bar') : null;
      if (!panel || !stepsEl || !bar) return;
      panel.classList.remove('d-none');
      var steps = ['Parsing resume file...', 'Extracting keywords...', 'Scoring ATS compatibility...', 'Generating feedback...'];
      stepsEl.innerHTML = '';
      var idx = 0;
      var timer = setInterval(function () {
        if (idx >= steps.length) {
          clearInterval(timer);
          return;
        }
        var li = document.createElement('li');
        li.textContent = steps[idx];
        stepsEl.appendChild(li);
        bar.style.width = Math.min(95, (idx + 1) * 24) + '%';
        idx += 1;
      }, 350);
    });
  }

  // ========== Score ring ==========
  var scoreWrapper = document.querySelector('.score-ring-wrapper');
  if (scoreWrapper) {
    var raw = Number(scoreWrapper.getAttribute('data-score') || 0);
    var score = Math.max(0, Math.min(100, raw));
    var circle = scoreWrapper.querySelector('.score-ring-progress');
    if (circle) {
      var radius = 50;
      var circumference = 2 * Math.PI * radius;
      circle.style.strokeDasharray = circumference;
      circle.style.strokeDashoffset = circumference * (1 - score / 100);
      circle.classList.remove('score-low', 'score-mid', 'score-high');
      circle.classList.add(score < 50 ? 'score-low' : score <= 75 ? 'score-mid' : 'score-high');
    }
  }

  // ========== Skills pie chart (Chart.js + SkillCategorizer) ==========
  // Root-cause fixes:
  // 1) Chart.js must load BEFORE this file — use {% block before_app_scripts %} in dashboard.
  // 2) Init when "Skills Analysis" tab is shown — hidden panes get zero size otherwise.
  var g = typeof window !== 'undefined' ? window : {};
  var skillsPieChartInstance = null;

  function parseAnalysisJson() {
    var analysisNode = document.getElementById('analysis-json');
    if (!analysisNode) return {};
    try {
      return JSON.parse(analysisNode.textContent);
    } catch (e) {
      console.warn('[SkillChart] Invalid analysis JSON', e);
      return {};
    }
  }

  function renderCategoryList(analysisData, chartRows) {
    var list = document.getElementById('skills-category-list');
    if (!list) return;
    var cats = analysisData.skill_categories;
    if (cats && typeof cats === 'object') {
      var keys = Object.keys(cats).filter(function (k) { return (cats[k] || []).length > 0; });
      if (keys.length > 0) {
        list.innerHTML = keys.map(function (k) {
          var items = cats[k].slice(0, 10).join(', ');
          return '<div class="mb-2"><strong class="text-capitalize">' + k + '</strong><div class="small text-muted">' + (items || '—') + '</div></div>';
        }).join('');
        return;
      }
    }
    if (chartRows.length > 0) {
      list.innerHTML = chartRows.map(function (row) {
        return '<div class="mb-2"><strong>' + row.name + '</strong><div class="small text-muted">Count: ' + row.value + '</div></div>';
      }).join('');
      return;
    }
    list.innerHTML = '<span class="text-muted small">No categories to list.</span>';
  }

  function initSkillsPieChart() {
    var pieCanvas = document.getElementById('skillsPieChart');
    var emptyEl = document.getElementById('skills-chart-empty');
    var wrapEl = document.getElementById('skills-chart-wrap');
    if (!pieCanvas || typeof Chart === 'undefined') {
      console.warn('[SkillChart] Missing canvas or Chart.js');
      return;
    }
    var sc = g.SkillCategorizer;
    if (!sc || typeof sc.buildChartData !== 'function') {
      console.warn('[SkillChart] SkillCategorizer not loaded');
      return;
    }

    var analysisData = parseAnalysisJson();
    var chartRows = sc.buildChartData(analysisData);
    var total = chartRows.reduce(function (a, b) { return a + (b.value || 0); }, 0);

    if (total === 0) {
      if (emptyEl) emptyEl.classList.remove('d-none');
      if (wrapEl) wrapEl.classList.add('d-none');
      renderCategoryList(analysisData, chartRows);
      return;
    }
    if (emptyEl) emptyEl.classList.add('d-none');
    if (wrapEl) wrapEl.classList.remove('d-none');

    renderCategoryList(analysisData, chartRows);

    var labels = chartRows.map(function (r) { return r.name; });
    var values = chartRows.map(function (r) { return r.value; });

    if (skillsPieChartInstance) {
      skillsPieChartInstance.destroy();
      skillsPieChartInstance = null;
    }

    skillsPieChartInstance = new Chart(pieCanvas, {
      type: 'pie',
      data: {
        labels: labels,
        datasets: [{
          data: values,
          backgroundColor: ['#4f46e5', '#06b6d4', '#16a34a', '#f59e0b', '#ef4444'],
          borderWidth: 1,
          hoverOffset: 8
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        animation: {
          animateRotate: true,
          animateScale: true,
          duration: 600,
          easing: 'easeOutQuart'
        },
        plugins: {
          legend: { position: 'bottom' },
          tooltip: {
            callbacks: {
              label: function (context) {
                var v = context.raw || 0;
                var sum = values.reduce(function (a, b) { return a + b; }, 0) || 1;
                var pct = ((v / sum) * 100).toFixed(1);
                return context.label + ': ' + v + ' (' + pct + '%)';
              }
            }
          }
        }
      }
    });

    requestAnimationFrame(function () {
      if (skillsPieChartInstance) skillsPieChartInstance.resize();
    });
  }

  document.querySelectorAll('[data-bs-toggle="pill"][data-bs-target="#skills-pane"]').forEach(function (btn) {
    btn.addEventListener('shown.bs.tab', function () {
      initSkillsPieChart();
    });
  });
  window.addEventListener('load', function () {
    var skillsPane = document.getElementById('skills-pane');
    if (skillsPane && skillsPane.classList.contains('active')) {
      initSkillsPieChart();
    }
  });

  // ========== Interactive history ==========
  var historyNode = document.getElementById('resume-history-json');
  var history = [];
  try { history = historyNode ? JSON.parse(historyNode.textContent) : []; } catch (e) {}
  var historyList = document.getElementById('history-list');
  var historySearch = document.getElementById('history-search');
  var historySort = document.getElementById('history-sort');

  function renderHistory() {
    if (!historyList) return;
    var q = (historySearch && historySearch.value ? historySearch.value : '').trim().toLowerCase();
    var sortBy = historySort ? historySort.value : 'latest';
    var items = history.filter(function (r) { return !q || r.name.toLowerCase().indexOf(q) >= 0; });
    items.sort(function (a, b) {
      if (sortBy === 'highest') return (b.score || 0) - (a.score || 0);
      if (sortBy === 'name') return (a.name || '').localeCompare(b.name || '');
      return new Date(b.uploaded_at) - new Date(a.uploaded_at);
    });
    if (!items.length) {
      historyList.innerHTML = '<p class="text-muted small mb-0">No uploads matched your filters.</p>';
      return;
    }
    historyList.innerHTML = items.map(function (r) {
      return (
        '<div class="history-row">' +
        '<div><div class="fw-semibold">' + r.name + '</div><div class="small text-muted">' + r.uploaded_display + '</div></div>' +
        '<div class="text-end">' +
        '<span class="badge bg-primary me-2">Score ' + (r.score || 0) + '%</span>' +
        '<a class="btn btn-sm btn-outline-secondary me-1" target="_blank" href="' + (r.download_url || r.url || '#') + '" title="Download / View"><i class="fas fa-download"></i></a>' +
        '<button class="btn btn-sm btn-outline-danger js-delete-resume" data-id="' + r.id + '" title="Delete"><i class="fas fa-trash"></i></button>' +
        '</div></div>'
      );
    }).join('');
  }

  if (historySearch) historySearch.addEventListener('input', renderHistory);
  if (historySort) historySort.addEventListener('change', renderHistory);
  renderHistory();

  document.addEventListener('click', function (e) {
    var btn = e.target.closest('.js-delete-resume');
    if (!btn) return;
    var id = btn.getAttribute('data-id');
    if (!id || !confirm('Delete this resume from history?')) return;
    fetch('/resume/' + id + '/delete/', {
      method: 'POST',
      headers: { 'X-CSRFToken': getCsrfToken() }
    })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        if (!data.ok) return;
        history = history.filter(function (x) { return String(x.id) !== String(id); });
        renderHistory();
      })
      .catch(function () {});
  });

  function getCsrfToken() {
    var match = document.cookie.match(/csrftoken=([^;]+)/);
    return match ? match[1] : '';
  }

  // ========== Mobile Sidebar Navigation Drawer ==========
  var mobileToggleBtn = document.getElementById('scg-mobile-sidebar-toggle');
  var sidebarCloseBtn = document.getElementById('scg-sidebar-close');
  var sidebar = document.getElementById('scg-sidebar');
  var sidebarBackdrop = document.getElementById('scg-sidebar-backdrop');

  function openMobileSidebar() {
    if (sidebar) sidebar.classList.add('show-mobile');
    if (sidebarBackdrop) sidebarBackdrop.classList.add('show');
    document.body.style.overflow = 'hidden';
  }

  function closeMobileSidebar() {
    if (sidebar) sidebar.classList.remove('show-mobile');
    if (sidebarBackdrop) sidebarBackdrop.classList.remove('show');
    document.body.style.overflow = '';
  }

  if (mobileToggleBtn) {
    mobileToggleBtn.addEventListener('click', openMobileSidebar);
  }
  if (sidebarCloseBtn) {
    sidebarCloseBtn.addEventListener('click', closeMobileSidebar);
  }
  if (sidebarBackdrop) {
    sidebarBackdrop.addEventListener('click', closeMobileSidebar);
  }

  // ========== Universal Theme Engine (Automatic Browser Detection + Manual Toggle) ==========
  var themeToggles = document.querySelectorAll('#global-theme-toggle, #theme-toggle-btn');
  var darkMediaQuery = window.matchMedia ? window.matchMedia('(prefers-color-scheme: dark)') : null;

  function getAutoTheme() {
    return (darkMediaQuery && darkMediaQuery.matches) ? 'dark' : 'light';
  }

  function getInitialTheme() {
    var manual = localStorage.getItem('scg-theme-manual');
    var saved = localStorage.getItem('scg-theme');
    if (manual && saved) return saved;
    return getAutoTheme();
  }

  function applyTheme(theme, isManual) {
    document.documentElement.setAttribute('data-theme', theme);
    document.documentElement.setAttribute('data-bs-theme', theme);
    if (isManual) {
      localStorage.setItem('scg-theme', theme);
      localStorage.setItem('scg-theme-manual', '1');
    }

    // Update global navbar theme toggle icon
    document.querySelectorAll('#global-theme-icon').forEach(function (icon) {
      if (theme === 'dark') {
        icon.className = 'fas fa-sun text-warning';
      } else {
        icon.className = 'fas fa-moon text-white-50';
      }
    });

    // Update dashboard theme button if present
    document.querySelectorAll('#theme-toggle-btn').forEach(function (btn) {
      if (theme === 'dark') {
        btn.innerHTML = '<i class="fas fa-sun me-2 text-warning"></i>Light Mode';
      } else {
        btn.innerHTML = '<i class="fas fa-moon me-2 text-secondary"></i>Dark Mode';
      }
    });
  }

  // Initial apply
  var currentTheme = getInitialTheme();
  applyTheme(currentTheme, false);

  // Dynamic browser system theme listener: auto-update if user hasn't forced manual override
  if (darkMediaQuery) {
    var onSystemThemeChange = function (e) {
      var manual = localStorage.getItem('scg-theme-manual');
      if (!manual) {
        var autoTheme = e.matches ? 'dark' : 'light';
        applyTheme(autoTheme, false);
      }
    };
    if (darkMediaQuery.addEventListener) {
      darkMediaQuery.addEventListener('change', onSystemThemeChange);
    } else if (darkMediaQuery.addListener) {
      darkMediaQuery.addListener(onSystemThemeChange);
    }
  }

  // Click listener for all toggle buttons
  themeToggles.forEach(function (toggle) {
    toggle.addEventListener('click', function () {
      var activeTheme = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      applyTheme(activeTheme, true);
    });
  });

})();

