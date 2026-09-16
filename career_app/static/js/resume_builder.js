/**
 * Interactive Resume & CV Builder Studio Engine
 * Provides live real-time preview, template switching, color theming,
 * dynamic item generation, PDF download, and direct ATS analysis.
 */

(function () {
  'use strict';

  function getCsrfToken() {
    var match = document.cookie.match(/csrftoken=([^;]+)/);
    return match ? match[1] : '';
  }

  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  // Initial State Definition
  var DEFAULT_STATE = {
    title: 'My Professional Resume',
    template: 'modern',
    color: '#2563eb',
    font: 'Inter',
    personal: {
      name: '',
      title: '',
      email: '',
      phone: '',
      location: '',
      website: '',
      linkedin: '',
      github: ''
    },
    summary: '',
    experiences: [],
    education: [],
    skills: {
      technical: '',
      soft: ''
    },
    projects: [],
    certifications: [],
    languages: ''
  };

  var SAMPLE_STATE = {
    title: 'Full Stack Engineer Resume',
    template: 'modern',
    color: '#2563eb',
    font: 'Inter',
    personal: {
      name: 'Alex Morgan',
      title: 'Senior Software Engineer',
      email: 'alex.morgan@example.com',
      phone: '+1 (555) 234-5678',
      location: 'San Francisco, CA',
      website: 'https://alexmorgan.dev',
      linkedin: 'linkedin.com/in/alexmorgan',
      github: 'github.com/alexmorgan'
    },
    summary: 'Results-driven Full Stack Engineer with 5+ years of experience architecting high-scale web platforms and cloud microservices. Proven track record optimizing backend performance by 40% and leading agile development teams.',
    experiences: [
      {
        role: 'Senior Software Engineer',
        company: 'CloudScale Technologies',
        location: 'San Francisco, CA',
        start: '2022',
        end: 'Present',
        current: true,
        points: 'Architected distributed REST and gRPC microservices using Python, FastAPI, and PostgreSQL handling 15M+ daily requests.\nReduced API p99 latency by 35% through Redis caching and PostgreSQL query indexing.\nLed a cross-functional squad of 6 engineers across sprint cycles and automated CI/CD deployments via Docker and Kubernetes.'
      },
      {
        role: 'Software Developer',
        company: 'Apex Digital Solutions',
        location: 'San Jose, CA',
        start: '2020',
        end: '2022',
        current: false,
        points: 'Built responsive client web applications using React, TypeScript, and Redux with 99.8% uptime.\nImplemented automated test suites with PyTest and Jest, boosting test coverage from 62% to 88%.\nCollaborated with UI/UX designers to deliver accessible, WCAG-compliant design components.'
      }
    ],
    education: [
      {
        degree: 'B.S. in Computer Science',
        school: 'University of California, Berkeley',
        location: 'Berkeley, CA',
        year: '2020',
        details: 'GPA 3.8 / 4.0 — Focus on Distributed Systems, Algorithms, and Software Engineering'
      }
    ],
    skills: {
      technical: 'Python, Django, FastAPI, React, TypeScript, JavaScript, SQL, PostgreSQL, Docker, Kubernetes, AWS, Git, CI/CD, Redis',
      soft: 'Technical Leadership, Agile/Scrum, Problem Solving, Cross-Functional Collaboration, Mentorship'
    },
    projects: [
      {
        name: 'OpenMetrics Dashboard',
        tools: 'Python, React, Docker, Chart.js',
        link: 'github.com/alexmorgan/openmetrics',
        description: 'Real-time telemetry and monitoring tool visualizing server CPU/memory performance with WebSocket sync.'
      },
      {
        name: 'Smart Search Pipeline',
        tools: 'Python, Elasticsearch, FastAPI',
        link: 'alexmorgan.dev/search',
        description: 'NLP-powered fuzzy search engine indexing over 200,000 documents with sub-50ms query turnaround.'
      }
    ],
    certifications: [
      { name: 'AWS Certified Solutions Architect - Associate', issuer: 'Amazon Web Services', year: '2023' }
    ],
    languages: 'English (Native), Spanish (Conversational)'
  };

  var resumeState = JSON.parse(JSON.stringify(DEFAULT_STATE));

  // Initialize from server payload if present
  var serverDataEl = document.getElementById('initial-draft-json');
  if (serverDataEl && serverDataEl.textContent.trim()) {
    try {
      var parsed = JSON.parse(serverDataEl.textContent);
      if (parsed && typeof parsed === 'object' && Object.keys(parsed).length > 0) {
        resumeState = Object.assign({}, DEFAULT_STATE, parsed);
      }
    } catch (e) {
      console.warn('[ResumeBuilder] Failed parsing server data:', e);
    }
  }

  // ==============================================================================
  // DOM References
  // ==============================================================================
  var previewContainer = document.getElementById('resume-preview-pane');
  var formEl = document.getElementById('resume-form');
  var draftTitleInput = document.getElementById('draft-title');
  var templateSelect = document.getElementById('template-select');
  var fontSelect = document.getElementById('font-select');
  var saveBtn = document.getElementById('save-draft-btn');
  var printBtn = document.getElementById('print-resume-btn');
  var sampleBtn = document.getElementById('load-sample-btn');
  var clearBtn = document.getElementById('clear-all-btn');
  var analyzeBtn = document.getElementById('analyze-resume-btn');

  var expListEl = document.getElementById('experiences-list');
  var eduListEl = document.getElementById('education-list');
  var projListEl = document.getElementById('projects-list');
  var certListEl = document.getElementById('certifications-list');

  // ==============================================================================
  // RENDER LIVE PREVIEW
  // ==============================================================================
  function renderLivePreview() {
    if (!previewContainer) return;

    var s = resumeState;
    var tplClass = 'tpl-' + (s.template || 'modern');
    var themeColor = s.color || '#2563eb';
    var fontFamily = s.font || 'Inter';

    previewContainer.style.setProperty('--theme-primary', themeColor);
    previewContainer.style.setProperty('--resume-font', fontFamily + ', sans-serif');

    // Split skills string into badges
    var techSkills = (s.skills.technical || '')
      .split(/[,|\n]+/)
      .map(function (x) { return x.trim(); })
      .filter(Boolean);

    var softSkills = (s.skills.soft || '')
      .split(/[,|\n]+/)
      .map(function (x) { return x.trim(); })
      .filter(Boolean);

    var allSkills = techSkills.concat(softSkills);

    var html = '';

    if (s.template === 'creative') {
      // 2-Column Split Template
      html += '<div class="resume-paper ' + tplClass + '">';
      // Sidebar
      html += '<aside class="creative-sidebar">';
      html += '<div class="resume-name">' + escapeHtml(s.personal.name || 'Your Name') + '</div>';
      html += '<div class="resume-target-title">' + escapeHtml(s.personal.title || 'Professional Title') + '</div>';

      html += '<div class="sidebar-section-title"><i class="fas fa-address-card me-1"></i>Contact</div>';
      html += '<div class="small text-muted mb-3" style="line-height: 1.8;">';
      if (s.personal.email) html += '<div><i class="fas fa-envelope me-2"></i>' + escapeHtml(s.personal.email) + '</div>';
      if (s.personal.phone) html += '<div><i class="fas fa-phone me-2"></i>' + escapeHtml(s.personal.phone) + '</div>';
      if (s.personal.location) html += '<div><i class="fas fa-map-marker-alt me-2"></i>' + escapeHtml(s.personal.location) + '</div>';
      if (s.personal.linkedin) html += '<div><i class="fab fa-linkedin me-2"></i>' + escapeHtml(s.personal.linkedin) + '</div>';
      if (s.personal.github) html += '<div><i class="fab fa-github me-2"></i>' + escapeHtml(s.personal.github) + '</div>';
      if (s.personal.website) html += '<div><i class="fas fa-globe me-2"></i>' + escapeHtml(s.personal.website) + '</div>';
      html += '</div>';

      if (allSkills.length > 0) {
        html += '<div class="sidebar-section-title"><i class="fas fa-code me-1"></i>Core Skills</div>';
        allSkills.forEach(function (sk) {
          html += '<div class="skill-badge">• ' + escapeHtml(sk) + '</div>';
        });
      }

      if (s.education && s.education.length > 0) {
        html += '<div class="sidebar-section-title"><i class="fas fa-graduation-cap me-1"></i>Education</div>';
        s.education.forEach(function (edu) {
          html += '<div class="mb-2">';
          html += '<div class="fw-bold small">' + escapeHtml(edu.degree) + '</div>';
          html += '<div class="small text-muted">' + escapeHtml(edu.school) + (edu.year ? ' (' + escapeHtml(edu.year) + ')' : '') + '</div>';
          html += '</div>';
        });
      }

      if (s.languages) {
        html += '<div class="sidebar-section-title"><i class="fas fa-language me-1"></i>Languages</div>';
        html += '<div class="small text-muted">' + escapeHtml(s.languages) + '</div>';
      }

      html += '</aside>';

      // Main content
      html += '<main class="creative-main">';
      if (s.summary) {
        html += '<section class="resume-section">';
        html += '<div class="section-title"><i class="fas fa-user me-2"></i>Profile Summary</div>';
        html += '<div class="resume-summary-text">' + escapeHtml(s.summary) + '</div>';
        html += '</section>';
      }

      if (s.experiences && s.experiences.length > 0) {
        html += '<section class="resume-section">';
        html += '<div class="section-title"><i class="fas fa-briefcase me-2"></i>Experience</div>';
        s.experiences.forEach(function (exp) {
          html += '<div class="mb-3 experience-item">';
          html += '<div class="item-row">';
          html += '<span class="item-title">' + escapeHtml(exp.role) + '</span>';
          html += '<span class="item-date">' + escapeHtml(exp.start) + ' - ' + escapeHtml(exp.current ? 'Present' : exp.end) + '</span>';
          html += '</div>';
          html += '<div class="item-subtitle mb-1">' + escapeHtml(exp.company) + (exp.location ? ' • ' + escapeHtml(exp.location) : '') + '</div>';
          if (exp.points) {
            html += '<ul class="resume-bullets">';
            exp.points.split('\n').forEach(function (pt) {
              if (pt.trim()) html += '<li>' + escapeHtml(pt.trim()) + '</li>';
            });
            html += '</ul>';
          }
          html += '</div>';
        });
        html += '</section>';
      }

      if (s.projects && s.projects.length > 0) {
        html += '<section class="resume-section">';
        html += '<div class="section-title"><i class="fas fa-diagram-project me-2"></i>Key Projects</div>';
        s.projects.forEach(function (proj) {
          html += '<div class="mb-2 project-item">';
          html += '<div class="item-row">';
          html += '<span class="item-title">' + escapeHtml(proj.name) + '</span>';
          if (proj.link) html += '<span class="small text-muted">' + escapeHtml(proj.link) + '</span>';
          html += '</div>';
          if (proj.tools) html += '<div class="small text-primary mb-1">' + escapeHtml(proj.tools) + '</div>';
          if (proj.description) html += '<div class="small text-muted">' + escapeHtml(proj.description) + '</div>';
          html += '</div>';
        });
        html += '</section>';
      }
      html += '</main>';
      html += '</div>';

    } else {
      // Standard 1-Column Layouts (Modern, Executive, Minimalist)
      html += '<div class="resume-paper ' + tplClass + '">';

      // Header
      html += '<header class="resume-header">';
      html += '<h1 class="resume-name">' + escapeHtml(s.personal.name || 'Your Name') + '</h1>';
      if (s.personal.title) {
        html += '<div class="resume-target-title">' + escapeHtml(s.personal.title) + '</div>';
      }
      html += '<div class="resume-contact-bar">';
      if (s.personal.email) html += '<span class="resume-contact-item"><i class="fas fa-envelope"></i>' + escapeHtml(s.personal.email) + '</span>';
      if (s.personal.phone) html += '<span class="resume-contact-item"><i class="fas fa-phone"></i>' + escapeHtml(s.personal.phone) + '</span>';
      if (s.personal.location) html += '<span class="resume-contact-item"><i class="fas fa-map-marker-alt"></i>' + escapeHtml(s.personal.location) + '</span>';
      if (s.personal.linkedin) html += '<span class="resume-contact-item"><i class="fab fa-linkedin"></i>' + escapeHtml(s.personal.linkedin) + '</span>';
      if (s.personal.github) html += '<span class="resume-contact-item"><i class="fab fa-github"></i>' + escapeHtml(s.personal.github) + '</span>';
      if (s.personal.website) html += '<span class="resume-contact-item"><i class="fas fa-globe"></i>' + escapeHtml(s.personal.website) + '</span>';
      html += '</div>';
      html += '</header>';

      // Summary
      if (s.summary) {
        html += '<section class="resume-section">';
        html += '<h2 class="section-title"><i class="fas fa-user me-2"></i>Professional Summary</h2>';
        html += '<div class="resume-summary-text">' + escapeHtml(s.summary) + '</div>';
        html += '</section>';
      }

      // Work Experience
      if (s.experiences && s.experiences.length > 0) {
        html += '<section class="resume-section">';
        html += '<h2 class="section-title"><i class="fas fa-briefcase me-2"></i>Work Experience</h2>';
        s.experiences.forEach(function (exp) {
          html += '<div class="mb-3 experience-item">';
          html += '<div class="item-row">';
          html += '<span class="item-title">' + escapeHtml(exp.role) + '</span>';
          html += '<span class="item-date">' + escapeHtml(exp.start) + ' – ' + escapeHtml(exp.current ? 'Present' : exp.end) + '</span>';
          html += '</div>';
          html += '<div class="item-subtitle mb-1">' + escapeHtml(exp.company) + (exp.location ? ' • ' + escapeHtml(exp.location) : '') + '</div>';
          if (exp.points) {
            html += '<ul class="resume-bullets">';
            exp.points.split('\n').forEach(function (pt) {
              if (pt.trim()) html += '<li>' + escapeHtml(pt.trim()) + '</li>';
            });
            html += '</ul>';
          }
          html += '</div>';
        });
        html += '</section>';
      }

      // Education
      if (s.education && s.education.length > 0) {
        html += '<section class="resume-section">';
        html += '<h2 class="section-title"><i class="fas fa-graduation-cap me-2"></i>Education</h2>';
        s.education.forEach(function (edu) {
          html += '<div class="mb-2 education-item">';
          html += '<div class="item-row">';
          html += '<span class="item-title">' + escapeHtml(edu.degree) + '</span>';
          if (edu.year) html += '<span class="item-date">' + escapeHtml(edu.year) + '</span>';
          html += '</div>';
          html += '<div class="item-subtitle">' + escapeHtml(edu.school) + (edu.location ? ' • ' + escapeHtml(edu.location) : '') + '</div>';
          if (edu.details) html += '<div class="small text-muted mt-1">' + escapeHtml(edu.details) + '</div>';
          html += '</div>';
        });
        html += '</section>';
      }

      // Skills
      if (allSkills.length > 0) {
        html += '<section class="resume-section">';
        html += '<h2 class="section-title"><i class="fas fa-code me-2"></i>Skills & Competencies</h2>';
        html += '<div class="d-flex flex-wrap gap-1">';
        allSkills.forEach(function (sk) {
          html += '<span class="skill-badge">' + escapeHtml(sk) + '</span>';
        });
        html += '</div>';
        html += '</section>';
      }

      // Key Projects
      if (s.projects && s.projects.length > 0) {
        html += '<section class="resume-section">';
        html += '<h2 class="section-title"><i class="fas fa-diagram-project me-2"></i>Key Projects</h2>';
        s.projects.forEach(function (proj) {
          html += '<div class="mb-2 project-item">';
          html += '<div class="item-row">';
          html += '<span class="item-title">' + escapeHtml(proj.name) + '</span>';
          if (proj.link) html += '<span class="small text-muted">' + escapeHtml(proj.link) + '</span>';
          html += '</div>';
          if (proj.tools) html += '<div class="small fw-semibold text-primary mb-1">' + escapeHtml(proj.tools) + '</div>';
          if (proj.description) html += '<div class="small text-muted">' + escapeHtml(proj.description) + '</div>';
          html += '</div>';
        });
        html += '</section>';
      }

      // Certifications
      if (s.certifications && s.certifications.length > 0) {
        html += '<section class="resume-section">';
        html += '<h2 class="section-title"><i class="fas fa-award me-2"></i>Certifications</h2>';
        s.certifications.forEach(function (cert) {
          html += '<div class="d-flex justify-content-between small text-muted mb-1">';
          html += '<span><strong class="text-dark">' + escapeHtml(cert.name) + '</strong> (' + escapeHtml(cert.issuer) + ')</span>';
          if (cert.year) html += '<span>' + escapeHtml(cert.year) + '</span>';
          html += '</div>';
        });
        html += '</section>';
      }

      // Languages
      if (s.languages) {
        html += '<section class="resume-section">';
        html += '<h2 class="section-title"><i class="fas fa-language me-2"></i>Languages</h2>';
        html += '<div class="small text-muted">' + escapeHtml(s.languages) + '</div>';
        html += '</section>';
      }

      html += '</div>'; // close resume-paper
    }

    previewContainer.innerHTML = html;
  }

  // ==============================================================================
  // FORM BINDINGS & DYNAMIC FIELDS
  // ==============================================================================
  function syncFormFromState() {
    var s = resumeState;
    if (draftTitleInput) draftTitleInput.value = s.title || '';
    if (templateSelect) templateSelect.value = s.template || 'modern';
    if (fontSelect) fontSelect.value = s.font || 'Inter';

    // Highlight active color pill
    document.querySelectorAll('.color-picker-pill').forEach(function (el) {
      el.classList.toggle('active', el.dataset.color === s.color);
    });

    // Personal info
    var fields = ['name', 'title', 'email', 'phone', 'location', 'website', 'linkedin', 'github'];
    fields.forEach(function (f) {
      var inp = document.getElementById('personal-' + f);
      if (inp) inp.value = s.personal[f] || '';
    });

    var sumEl = document.getElementById('summary-input');
    if (sumEl) sumEl.value = s.summary || '';

    var techEl = document.getElementById('skills-technical');
    if (techEl) techEl.value = s.skills.technical || '';

    var softEl = document.getElementById('skills-soft');
    if (softEl) softEl.value = s.skills.soft || '';

    var langEl = document.getElementById('languages-input');
    if (langEl) langEl.value = s.languages || '';

    renderDynamicFormItems();
    renderLivePreview();
  }

  function renderDynamicFormItems() {
    // Experiences
    if (expListEl) {
      expListEl.innerHTML = (resumeState.experiences || []).map(function (exp, idx) {
        return (
          '<div class="card border p-3 mb-3 bg-light-subtle" data-idx="' + idx + '">' +
          '<div class="d-flex justify-content-between align-items-center mb-2">' +
          '<strong class="small text-muted">Position #' + (idx + 1) + '</strong>' +
          '<button type="button" class="btn btn-sm btn-outline-danger js-remove-exp"><i class="fas fa-trash"></i></button>' +
          '</div>' +
          '<div class="row g-2 mb-2">' +
          '<div class="col-md-6"><input type="text" class="form-control form-control-sm exp-role" placeholder="Job Title" value="' + escapeHtml(exp.role) + '"></div>' +
          '<div class="col-md-6"><input type="text" class="form-control form-control-sm exp-company" placeholder="Company" value="' + escapeHtml(exp.company) + '"></div>' +
          '<div class="col-md-4"><input type="text" class="form-control form-control-sm exp-location" placeholder="Location" value="' + escapeHtml(exp.location) + '"></div>' +
          '<div class="col-md-4"><input type="text" class="form-control form-control-sm exp-start" placeholder="Start Date" value="' + escapeHtml(exp.start) + '"></div>' +
          '<div class="col-md-4"><input type="text" class="form-control form-control-sm exp-end" placeholder="End Date" value="' + escapeHtml(exp.end) + '" ' + (exp.current ? 'disabled' : '') + '></div>' +
          '</div>' +
          '<div class="form-check mb-2">' +
          '<input type="checkbox" class="form-check-input exp-current" id="exp-current-' + idx + '" ' + (exp.current ? 'checked' : '') + '>' +
          '<label class="form-check-label small" for="exp-current-' + idx + '">I currently work here</label>' +
          '</div>' +
          '<textarea class="form-control form-control-sm exp-points" rows="3" placeholder="Accomplishments & bullet points (one per line)">' + escapeHtml(exp.points) + '</textarea>' +
          '</div>'
        );
      }).join('');
    }

    // Education
    if (eduListEl) {
      eduListEl.innerHTML = (resumeState.education || []).map(function (edu, idx) {
        return (
          '<div class="card border p-3 mb-3 bg-light-subtle" data-idx="' + idx + '">' +
          '<div class="d-flex justify-content-between align-items-center mb-2">' +
          '<strong class="small text-muted">Education #' + (idx + 1) + '</strong>' +
          '<button type="button" class="btn btn-sm btn-outline-danger js-remove-edu"><i class="fas fa-trash"></i></button>' +
          '</div>' +
          '<div class="row g-2 mb-2">' +
          '<div class="col-md-6"><input type="text" class="form-control form-control-sm edu-degree" placeholder="Degree / Certificate" value="' + escapeHtml(edu.degree) + '"></div>' +
          '<div class="col-md-6"><input type="text" class="form-control form-control-sm edu-school" placeholder="School / University" value="' + escapeHtml(edu.school) + '"></div>' +
          '<div class="col-md-6"><input type="text" class="form-control form-control-sm edu-location" placeholder="Location" value="' + escapeHtml(edu.location) + '"></div>' +
          '<div class="col-md-6"><input type="text" class="form-control form-control-sm edu-year" placeholder="Graduation Year" value="' + escapeHtml(edu.year) + '"></div>' +
          '</div>' +
          '<input type="text" class="form-control form-control-sm edu-details" placeholder="Honors, GPA, or specializations" value="' + escapeHtml(edu.details) + '">' +
          '</div>'
        );
      }).join('');
    }

    // Projects
    if (projListEl) {
      projListEl.innerHTML = (resumeState.projects || []).map(function (proj, idx) {
        return (
          '<div class="card border p-3 mb-3 bg-light-subtle" data-idx="' + idx + '">' +
          '<div class="d-flex justify-content-between align-items-center mb-2">' +
          '<strong class="small text-muted">Project #' + (idx + 1) + '</strong>' +
          '<button type="button" class="btn btn-sm btn-outline-danger js-remove-proj"><i class="fas fa-trash"></i></button>' +
          '</div>' +
          '<div class="row g-2 mb-2">' +
          '<div class="col-md-6"><input type="text" class="form-control form-control-sm proj-name" placeholder="Project Name" value="' + escapeHtml(proj.name) + '"></div>' +
          '<div class="col-md-6"><input type="text" class="form-control form-control-sm proj-tools" placeholder="Technologies Used" value="' + escapeHtml(proj.tools) + '"></div>' +
          '</div>' +
          '<input type="text" class="form-control form-control-sm mb-2 proj-link" placeholder="Demo or GitHub Link" value="' + escapeHtml(proj.link) + '">' +
          '<textarea class="form-control form-control-sm proj-desc" rows="2" placeholder="Brief description & impact">' + escapeHtml(proj.description) + '</textarea>' +
          '</div>'
        );
      }).join('');
    }

    // Certifications
    if (certListEl) {
      certListEl.innerHTML = (resumeState.certifications || []).map(function (cert, idx) {
        return (
          '<div class="card border p-3 mb-3 bg-light-subtle" data-idx="' + idx + '">' +
          '<div class="d-flex justify-content-between align-items-center mb-2">' +
          '<strong class="small text-muted">Certification #' + (idx + 1) + '</strong>' +
          '<button type="button" class="btn btn-sm btn-outline-danger js-remove-cert"><i class="fas fa-trash"></i></button>' +
          '</div>' +
          '<div class="row g-2">' +
          '<div class="col-md-5"><input type="text" class="form-control form-control-sm cert-name" placeholder="Certification Name" value="' + escapeHtml(cert.name) + '"></div>' +
          '<div class="col-md-4"><input type="text" class="form-control form-control-sm cert-issuer" placeholder="Issuing Organization" value="' + escapeHtml(cert.issuer) + '"></div>' +
          '<div class="col-md-3"><input type="text" class="form-control form-control-sm cert-year" placeholder="Year" value="' + escapeHtml(cert.year) + '"></div>' +
          '</div>' +
          '</div>'
        );
      }).join('');
    }
  }

  // Bind Listeners
  function bindFormListeners() {
    if (!formEl) return;

    // Single input sync
    formEl.addEventListener('input', function (e) {
      var id = e.target.id;
      if (id.startsWith('personal-')) {
        var field = id.replace('personal-', '');
        resumeState.personal[field] = e.target.value;
      } else if (id === 'summary-input') {
        resumeState.summary = e.target.value;
      } else if (id === 'skills-technical') {
        resumeState.skills.technical = e.target.value;
      } else if (id === 'skills-soft') {
        resumeState.skills.soft = e.target.value;
      } else if (id === 'languages-input') {
        resumeState.languages = e.target.value;
      } else if (e.target.closest('#experiences-list')) {
        var card = e.target.closest('[data-idx]');
        var idx = Number(card.dataset.idx);
        if (resumeState.experiences[idx]) {
          resumeState.experiences[idx].role = card.querySelector('.exp-role').value;
          resumeState.experiences[idx].company = card.querySelector('.exp-company').value;
          resumeState.experiences[idx].location = card.querySelector('.exp-location').value;
          resumeState.experiences[idx].start = card.querySelector('.exp-start').value;
          resumeState.experiences[idx].end = card.querySelector('.exp-end').value;
          resumeState.experiences[idx].current = card.querySelector('.exp-current').checked;
          resumeState.experiences[idx].points = card.querySelector('.exp-points').value;
        }
      } else if (e.target.closest('#education-list')) {
        var card = e.target.closest('[data-idx]');
        var idx = Number(card.dataset.idx);
        if (resumeState.education[idx]) {
          resumeState.education[idx].degree = card.querySelector('.edu-degree').value;
          resumeState.education[idx].school = card.querySelector('.edu-school').value;
          resumeState.education[idx].location = card.querySelector('.edu-location').value;
          resumeState.education[idx].year = card.querySelector('.edu-year').value;
          resumeState.education[idx].details = card.querySelector('.edu-details').value;
        }
      } else if (e.target.closest('#projects-list')) {
        var card = e.target.closest('[data-idx]');
        var idx = Number(card.dataset.idx);
        if (resumeState.projects[idx]) {
          resumeState.projects[idx].name = card.querySelector('.proj-name').value;
          resumeState.projects[idx].tools = card.querySelector('.proj-tools').value;
          resumeState.projects[idx].link = card.querySelector('.proj-link').value;
          resumeState.projects[idx].description = card.querySelector('.proj-desc').value;
        }
      } else if (e.target.closest('#certifications-list')) {
        var card = e.target.closest('[data-idx]');
        var idx = Number(card.dataset.idx);
        if (resumeState.certifications[idx]) {
          resumeState.certifications[idx].name = card.querySelector('.cert-name').value;
          resumeState.certifications[idx].issuer = card.querySelector('.cert-issuer').value;
          resumeState.certifications[idx].year = card.querySelector('.cert-year').value;
        }
      }

      renderLivePreview();
      saveToLocalStorage();
    });

    // Experience Currently Working Toggle
    formEl.addEventListener('change', function (e) {
      if (e.target.classList.contains('exp-current')) {
        var card = e.target.closest('[data-idx]');
        var endInput = card.querySelector('.exp-end');
        if (endInput) {
          endInput.disabled = e.target.checked;
          if (e.target.checked) endInput.value = '';
        }
        var idx = Number(card.dataset.idx);
        if (resumeState.experiences[idx]) {
          resumeState.experiences[idx].current = e.target.checked;
          if (e.target.checked) resumeState.experiences[idx].end = '';
        }
        renderLivePreview();
      }
    });

    // Remove buttons delegation
    document.addEventListener('click', function (e) {
      var rmExp = e.target.closest('.js-remove-exp');
      if (rmExp) {
        var idx = Number(rmExp.closest('[data-idx]').dataset.idx);
        resumeState.experiences.splice(idx, 1);
        renderDynamicFormItems();
        renderLivePreview();
        return;
      }
      var rmEdu = e.target.closest('.js-remove-edu');
      if (rmEdu) {
        var idx = Number(rmEdu.closest('[data-idx]').dataset.idx);
        resumeState.education.splice(idx, 1);
        renderDynamicFormItems();
        renderLivePreview();
        return;
      }
      var rmProj = e.target.closest('.js-remove-proj');
      if (rmProj) {
        var idx = Number(rmProj.closest('[data-idx]').dataset.idx);
        resumeState.projects.splice(idx, 1);
        renderDynamicFormItems();
        renderLivePreview();
        return;
      }
      var rmCert = e.target.closest('.js-remove-cert');
      if (rmCert) {
        var idx = Number(rmCert.closest('[data-idx]').dataset.idx);
        resumeState.certifications.splice(idx, 1);
        renderDynamicFormItems();
        renderLivePreview();
        return;
      }
    });

    // Add buttons
    var addExpBtn = document.getElementById('add-exp-btn');
    if (addExpBtn) {
      addExpBtn.addEventListener('click', function () {
        resumeState.experiences.push({ role: '', company: '', location: '', start: '', end: '', current: false, points: '' });
        renderDynamicFormItems();
      });
    }

    var addEduBtn = document.getElementById('add-edu-btn');
    if (addEduBtn) {
      addEduBtn.addEventListener('click', function () {
        resumeState.education.push({ degree: '', school: '', location: '', year: '', details: '' });
        renderDynamicFormItems();
      });
    }

    var addProjBtn = document.getElementById('add-proj-btn');
    if (addProjBtn) {
      addProjBtn.addEventListener('click', function () {
        resumeState.projects.push({ name: '', tools: '', link: '', description: '' });
        renderDynamicFormItems();
      });
    }

    var addCertBtn = document.getElementById('add-cert-btn');
    if (addCertBtn) {
      addCertBtn.addEventListener('click', function () {
        resumeState.certifications.push({ name: '', issuer: '', year: '' });
        renderDynamicFormItems();
      });
    }

    // Title input
    if (draftTitleInput) {
      draftTitleInput.addEventListener('input', function () {
        resumeState.title = draftTitleInput.value;
      });
    }

    // Template selection
    if (templateSelect) {
      templateSelect.addEventListener('change', function () {
        resumeState.template = templateSelect.value;
        renderLivePreview();
      });
    }

    // Font selection
    if (fontSelect) {
      fontSelect.addEventListener('change', function () {
        resumeState.font = fontSelect.value;
        renderLivePreview();
      });
    }

    // Color picker pills
    document.querySelectorAll('.color-picker-pill').forEach(function (pill) {
      pill.addEventListener('click', function () {
        document.querySelectorAll('.color-picker-pill').forEach(function (p) { p.classList.remove('active'); });
        pill.classList.add('active');
        resumeState.color = pill.dataset.color;
        renderLivePreview();
      });
    });

    // Load Sample Data Button
    if (sampleBtn) {
      sampleBtn.addEventListener('click', function () {
        if (confirm('Load sample professional data? This will replace current form fields.')) {
          resumeState = JSON.parse(JSON.stringify(SAMPLE_STATE));
          syncFormFromState();
        }
      });
    }

    // Clear All Button
    if (clearBtn) {
      clearBtn.addEventListener('click', function () {
        if (confirm('Clear all resume fields and start fresh?')) {
          resumeState = JSON.parse(JSON.stringify(DEFAULT_STATE));
          syncFormFromState();
        }
      });
    }

    // Print / Download PDF
    if (printBtn) {
      printBtn.addEventListener('click', function () {
        window.print();
      });
    }

    // Save Draft to Server
    if (saveBtn) {
      saveBtn.addEventListener('click', saveDraftToServer);
    }

    // Analyze with ATS
    if (analyzeBtn) {
      analyzeBtn.addEventListener('click', analyzeDraftWithATS);
    }
  }

  // ==============================================================================
  // AUTO-SAVE & SERVER SYNC
  // ==============================================================================
  function saveToLocalStorage() {
    try {
      localStorage.setItem('scg_resume_draft', JSON.stringify(resumeState));
    } catch (e) {}
  }

  function saveDraftToServer() {
    if (!saveBtn) return;
    saveBtn.disabled = true;
    saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Saving...';

    var draftId = document.getElementById('active-draft-id')?.value || null;

    fetch('/api/builder/save/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken()
      },
      body: JSON.stringify({
        id: draftId ? Number(draftId) : null,
        title: resumeState.title,
        template_name: resumeState.template,
        theme_color: resumeState.color,
        font_family: resumeState.font,
        data: resumeState
      })
    })
      .then(function (r) {
        if (r.status === 403 || r.status === 401) {
          throw new Error('Please sign in or create an account to save drafts.');
        }
        return r.json();
      })
      .then(function (res) {
        saveBtn.disabled = false;
        saveBtn.innerHTML = '<i class="fas fa-check me-2"></i>Saved';
        setTimeout(function () {
          saveBtn.innerHTML = '<i class="fas fa-floppy-disk me-2"></i>Save Draft';
        }, 2000);

        if (res.ok && res.id) {
          var idField = document.getElementById('active-draft-id');
          if (idField) idField.value = res.id;
          // Update URL without reload
          if (!window.location.pathname.includes(String(res.id))) {
            window.history.replaceState(null, '', '/builder/' + res.id + '/');
          }
        }
      })
      .catch(function (err) {
        saveBtn.disabled = false;
        saveBtn.innerHTML = '<i class="fas fa-floppy-disk me-2"></i>Save Draft';
        alert(err.message || 'Error saving draft');
      });
  }

  // ==============================================================================
  // DIRECT ATS ANALYSIS
  // ==============================================================================
  function compileResumeText() {
    var s = resumeState;
    var parts = [];

    if (s.personal.name) parts.push(s.personal.name);
    if (s.personal.title) parts.push(s.personal.title);
    if (s.summary) parts.push('Summary: ' + s.summary);

    if (s.experiences && s.experiences.length > 0) {
      parts.push('Experience:');
      s.experiences.forEach(function (exp) {
        parts.push(exp.role + ' at ' + exp.company);
        if (exp.points) parts.push(exp.points);
      });
    }

    if (s.education && s.education.length > 0) {
      parts.push('Education:');
      s.education.forEach(function (edu) {
        parts.push(edu.degree + ' ' + edu.school + ' ' + (edu.details || ''));
      });
    }

    if (s.skills.technical || s.skills.soft) {
      parts.push('Skills: ' + s.skills.technical + ' ' + s.skills.soft);
    }

    if (s.projects && s.projects.length > 0) {
      parts.push('Projects:');
      s.projects.forEach(function (proj) {
        parts.push(proj.name + ': ' + proj.tools + ' - ' + proj.description);
      });
    }

    return parts.join('\n');
  }

  function analyzeDraftWithATS() {
    var text = compileResumeText();
    var modalEl = document.getElementById('ats-modal');
    if (!modalEl || typeof bootstrap === 'undefined') return;

    var bsModal = bootstrap.Modal.getOrCreateInstance(modalEl);
    bsModal.show();

    var scoreRing = document.getElementById('ats-modal-score');
    var scoreText = document.getElementById('ats-modal-score-text');
    var skillsContainer = document.getElementById('ats-modal-skills');
    var feedbackList = document.getElementById('ats-modal-feedback');

    if (scoreText) scoreText.textContent = '...';
    if (skillsContainer) skillsContainer.innerHTML = '<div class="spinner-border spinner-border-sm text-primary"></div> Analyzing keywords...';
    if (feedbackList) feedbackList.innerHTML = '';

    fetch('/api/builder/analyze/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken()
      },
      body: JSON.stringify({
        text: text,
        target_role: document.getElementById('ats-target-role')?.value || ''
      })
    })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        if (!data.ok || !data.analysis) {
          if (skillsContainer) skillsContainer.innerHTML = '<span class="text-danger">' + escapeHtml(data.message || 'Analysis error') + '</span>';
          return;
        }
        var a = data.analysis;
        var score = Number(a.score || 0);

        if (scoreText) scoreText.textContent = score.toFixed(1) + '%';
        if (scoreRing) {
          scoreRing.style.setProperty('--score-deg', (score * 3.6) + 'deg');
          scoreRing.className = 'ats-circle ' + (score < 50 ? 'border-danger' : score < 75 ? 'border-warning' : 'border-success');
        }

        // Skills
        if (skillsContainer) {
          var found = a.found_skills || [];
          if (!found.length) {
            skillsContainer.innerHTML = '<span class="text-muted small">No recognized skill keywords detected. Add more technical or domain keywords.</span>';
          } else {
            skillsContainer.innerHTML = found.map(function (s) {
              return '<span class="badge bg-success-subtle text-success border border-success me-1 mb-1">' + escapeHtml(s) + '</span>';
            }).join('');
          }
        }

        // Recommendations
        if (feedbackList) {
          var suggestions = a.suggestions_list || [];
          if (!suggestions.length) {
            feedbackList.innerHTML = '<li class="list-group-item text-success"><i class="fas fa-check-circle me-2"></i>Your resume has high keyword density and structure!</li>';
          } else {
            feedbackList.innerHTML = suggestions.map(function (tip) {
              return '<li class="list-group-item small"><i class="fas fa-arrow-right text-primary me-2"></i>' + escapeHtml(tip) + '</li>';
            }).join('');
          }
        }
      })
      .catch(function () {
        if (skillsContainer) skillsContainer.innerHTML = '<span class="text-danger">Failed to run analysis. Please try again.</span>';
      });
  }

  // Check for auto-saved draft if starting fresh
  if (!serverDataEl || !serverDataEl.textContent.trim()) {
    try {
      var saved = localStorage.getItem('scg_resume_draft');
      if (saved) {
        var parsedDraft = JSON.parse(saved);
        if (parsedDraft && parsedDraft.personal && parsedDraft.personal.name) {
          resumeState = Object.assign({}, DEFAULT_STATE, parsedDraft);
        }
      }
    } catch (e) {}
  }

  // ========== Mobile View Switcher & Preview Scaler ==========
  var toggleEditorBtn = document.getElementById('toggle-view-editor');
  var togglePreviewBtn = document.getElementById('toggle-view-preview');
  var editorCol = document.getElementById('builder-editor-col');
  var previewCol = document.getElementById('builder-preview-col');
  var scalerEl = document.getElementById('resume-paper-scaler');
  var zoomBtns = document.querySelectorAll('.preview-scale-btn');
  var autoFitBtn = document.getElementById('preview-auto-fit-btn');

  function setPreviewScale(scale) {
    if (!scalerEl) return;
    scalerEl.style.transform = 'scale(' + scale + ')';
    if (scale < 1) {
      var heightReduction = (1 - scale) * 1100;
      scalerEl.style.marginBottom = '-' + Math.round(heightReduction) + 'px';
    } else {
      scalerEl.style.marginBottom = '0';
    }
  }

  function autoFitPreview() {
    if (!scalerEl) return;
    var container = scalerEl.parentElement;
    if (!container) return;
    var availWidth = container.clientWidth - 24;
    var paperWidth = 800;
    if (availWidth < paperWidth && availWidth > 200) {
      var scale = Math.min(1, Math.max(0.4, Number((availWidth / paperWidth).toFixed(2))));
      setPreviewScale(scale);
      zoomBtns.forEach(function (b) { b.classList.remove('active'); });
      if (autoFitBtn) autoFitBtn.classList.add('active');
    } else {
      setPreviewScale(1);
    }
  }

  if (toggleEditorBtn && togglePreviewBtn && editorCol && previewCol) {
    toggleEditorBtn.addEventListener('click', function () {
      toggleEditorBtn.className = 'btn btn-sm btn-primary rounded-pill px-4';
      togglePreviewBtn.className = 'btn btn-sm btn-outline-primary rounded-pill px-4';
      editorCol.classList.remove('d-none');
      previewCol.classList.add('d-none');
    });

    togglePreviewBtn.addEventListener('click', function () {
      togglePreviewBtn.className = 'btn btn-sm btn-primary rounded-pill px-4';
      toggleEditorBtn.className = 'btn btn-sm btn-outline-primary rounded-pill px-4';
      editorCol.classList.add('d-none');
      previewCol.classList.remove('d-none');
      setTimeout(autoFitPreview, 50);
    });

    window.addEventListener('resize', function () {
      if (window.innerWidth >= 1200) {
        editorCol.classList.remove('d-none');
        previewCol.classList.remove('d-none');
      }
    });
  }

  zoomBtns.forEach(function (btn) {
    btn.addEventListener('click', function () {
      zoomBtns.forEach(function (b) { b.classList.remove('active'); });
      if (autoFitBtn) autoFitBtn.classList.remove('active');
      btn.classList.add('active');
      var scale = parseFloat(btn.getAttribute('data-scale') || '1');
      setPreviewScale(scale);
    });
  });

  if (autoFitBtn) {
    autoFitBtn.addEventListener('click', autoFitPreview);
  }

  if (window.innerWidth < 880) {
    setTimeout(autoFitPreview, 300);
  }

  // Initialize
  syncFormFromState();
  bindFormListeners();

})();

