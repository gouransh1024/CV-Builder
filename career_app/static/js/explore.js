(function () {
  'use strict';

  function getCsrfToken() {
    var match = document.cookie.match(/csrftoken=([^;]+)/);
    return match ? match[1] : '';
  }

  var grid = document.getElementById('careers-grid');
  var loadingEl = document.getElementById('careers-loading');
  var templateEl = document.getElementById('career-card-template');

  var searchInput = document.getElementById('career-search');
  var domainSelect = document.getElementById('career-domain');
  var expSelect = document.getElementById('career-experience');
  var sortSelect = document.getElementById('career-sort');

  var refreshBtn = document.getElementById('refresh-careers-btn');
  var searchBtn = document.getElementById('career-search-btn');

  function escapeHtml(s) {
    return String(s || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  function showLoading(show) {
    if (!grid || !loadingEl) return;
    if (show) {
      loadingEl.classList.remove('d-none');
    } else {
      loadingEl.classList.add('d-none');
    }
  }

  function roleMatchBadge(matchPercent) {
    var v = Number(matchPercent || 0);
    var cls = v < 50 ? 'bg-danger' : v <= 75 ? 'bg-warning' : 'bg-success';
    return '<span class="badge ' + cls + '"> ' + v.toFixed(1) + '%</span>';
  }

  function renderSkills(list, targetEl, emptyText, badgeClass) {
    if (!targetEl) return;
    var arr = Array.isArray(list) ? list : [];
    if (!arr.length) {
      targetEl.innerHTML = emptyText ? '<span class="text-muted small">' + escapeHtml(emptyText) + '</span>' : '';
      return;
    }
    var cls = badgeClass || 'scg-skill-badge';
    targetEl.innerHTML = arr.map(function (s) {
      return '<span class="badge ' + cls + ' me-1 mb-1">' + escapeHtml(String(s)) + '</span>';
    }).join('');
  }

  function renderLearningPath(list, targetEl) {
    if (!targetEl) return;
    var arr = Array.isArray(list) ? list : [];
    if (!arr.length) {
      targetEl.innerHTML = '<li class="text-muted small">Upload a resume to see a personalized learning path.</li>';
      return;
    }
    targetEl.innerHTML = arr.map(function (t) {
      return '<li class="text-muted small"><i class="fas fa-check me-2 text-success"></i>' + escapeHtml(String(t)) + '</li>';
    }).join('');
  }

  function setBookmarkButton(button, isBookmarked) {
    if (!button) return;
    button.dataset.bookmarked = isBookmarked ? '1' : '0';
    button.innerHTML = isBookmarked
      ? '<i class="fas fa-bookmark me-1"></i>Saved'
      : '<i class="far fa-bookmark me-1"></i>Save';
    button.classList.toggle('btn-primary', !!isBookmarked);
    button.classList.toggle('btn-outline-primary', !isBookmarked);
  }

  function buildCard(role) {
    var clone = templateEl.content.firstElementChild.cloneNode(true);
    var card = clone;
    card.dataset.roleSlug = role.slug;

    var titleEl = card.querySelector('.role-title');
    titleEl.textContent = role.title || '';

    var domainEl = card.querySelector('.domain-pill');
    domainEl.textContent = role.domain || '';

    var expEl = card.querySelector('.exp-pill');
    expEl.textContent = role.experience || '';

    var growthEl = card.querySelector('.growth-pill');
    if (growthEl && role.growth_trend != null) growthEl.textContent = String(role.growth_trend) + '%';

    var salaryEl = card.querySelector('.salary-pill');
    if (salaryEl) {
      var min = role.avg_salary_min;
      var max = role.avg_salary_max;
      salaryEl.textContent = min && max ? '$' + min + ' - $' + max + ' / yr' : 'Salary varies';
    }

    var matchPill = card.querySelector('.match-pill');
    if (matchPill && role.match_percent != null) {
      matchPill.innerHTML = roleMatchBadge(role.match_percent);
    } else if (matchPill) {
      matchPill.textContent = '—';
    }

    // Details
    var descEl = card.querySelector('.role-description');
    if (descEl) descEl.textContent = role.description || '';

    renderSkills(role.required_skills, card.querySelector('.required-skills'), 'No required skills listed', 'scg-skill-badge');

    var missingContainer = card.querySelector('.missing-keywords');
    if (missingContainer) {
      if (role.gap_analysis && Array.isArray(role.gap_analysis.missing_keywords)) {
        renderSkills(role.gap_analysis.missing_keywords, missingContainer, 'No missing keywords', 'scg-missing-badge');
      } else {
        missingContainer.innerHTML = '<span class="text-muted small">Upload a resume to see gap analysis.</span>';
      }
    }

    renderLearningPath(role.learning_path, card.querySelector('.learning-path'));

    // Apply links
    var applyLinks = role.apply_links || {};
    var links = card.querySelectorAll('[data-apply]');
    links.forEach(function (a) {
      var key = a.getAttribute('data-apply');
      if (applyLinks[key]) a.href = applyLinks[key];
    });

    // Bookmark
    var bookmarkBtn = card.querySelector('.bookmark-btn');
    setBookmarkButton(bookmarkBtn, !!role.is_bookmarked);
    bookmarkBtn.addEventListener('click', function (e) {
      e.stopPropagation();
      toggleBookmark(role.slug, bookmarkBtn);
    });

    // Expand collapse and record view
    var collapseEl = card.querySelector('[data-role-details]');
    card.addEventListener('click', function () {
      if (collapseEl && typeof bootstrap !== 'undefined') {
        var bs = bootstrap.Collapse.getOrCreateInstance(collapseEl, { toggle: true });
      }
      viewRole(role.slug);
    });

    card.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        card.click();
      }
    });

    return clone;
  }

  function toggleBookmark(roleSlug, btnEl) {
    fetch('/api/role/' + encodeURIComponent(roleSlug) + '/bookmark/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
      body: JSON.stringify({}),
    })
      .then(function (r) {
        if (r.status === 401 || r.status === 403 || r.redirected) {
          window.location.href = '/login/?next=' + encodeURIComponent(window.location.pathname);
          return null;
        }
        return r.json();
      })
      .then(function (data) {
        if (data && data.ok) {
          setBookmarkButton(btnEl, data.bookmarked);
        }
      })
      .catch(function () {});
  }

  function viewRole(roleSlug) {
    fetch('/api/role/' + encodeURIComponent(roleSlug) + '/view/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
      body: JSON.stringify({}),
    }).catch(function () {});
  }

  function fetchCareers() {
    if (!grid) return;
    showLoading(true);

    var params = new URLSearchParams();
    if (searchInput && searchInput.value) params.set('q', searchInput.value);
    if (domainSelect && domainSelect.value) params.set('domain', domainSelect.value);
    if (expSelect && expSelect.value) params.set('experience', expSelect.value);
    if (sortSelect && sortSelect.value) params.set('sort', sortSelect.value);

    fetch('/api/careers/?' + params.toString(), {
      method: 'GET',
      headers: { 'Accept': 'application/json' }
    })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        showLoading(false);
        grid.innerHTML = '';
        var roles = (data && data.roles) ? data.roles : [];
        if (!roles.length) {
          grid.innerHTML = '<div class="col-12 text-center text-muted py-4">No roles match your filters.</div>';
          return;
        }
        var frag = document.createDocumentFragment();
        roles.forEach(function (role) {
          frag.appendChild(buildCard(role));
        });
        grid.appendChild(frag);
      })
      .catch(function () {
        showLoading(false);
        grid.innerHTML = '<div class="col-12 text-center text-danger py-4">Failed to load roles. Please try again.</div>';
      });
  }

  if (refreshBtn) refreshBtn.addEventListener('click', function () { fetchCareers(); });
  if (searchBtn) searchBtn.addEventListener('click', function () { fetchCareers(); });
  if (searchInput) searchInput.addEventListener('keydown', function (e) {
    if (e.key === 'Enter') fetchCareers();
  });

  // Auto-refresh on filter changes (lightweight debounce)
  var timeoutId = null;
  function schedule() {
    if (timeoutId) clearTimeout(timeoutId);
    timeoutId = setTimeout(function () {
      fetchCareers();
    }, 250);
  }
  if (domainSelect) domainSelect.addEventListener('change', schedule);
  if (expSelect) expSelect.addEventListener('change', schedule);
  if (sortSelect) sortSelect.addEventListener('change', schedule);

  // Initial load
  window.addEventListener('load', function () {
    fetchCareers();
  });
})();

