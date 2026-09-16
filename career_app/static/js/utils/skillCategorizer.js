/**
 * Maps raw skill strings (from resume tokens) into chart-ready category counts.
 * Used by the dashboard Skill Distribution pie chart.
 *
 * @param {string[]} skillsArray - e.g. ["react", "node", "mongodb", "docker"]
 * @returns {{ name: string, value: number }[]}
 */
(function (global) {
  'use strict';

  var CATEGORY_ORDER = ['Frontend', 'Backend', 'Database', 'Tools', 'Others'];

  function normalizeToken(s) {
    if (s == null || typeof s !== 'string') return '';
    return s
      .toLowerCase()
      .trim()
      .replace(/\s+/g, ' ')
      .replace(/\.js$/i, '')
      .replace(/\./g, '');
  }

  /** Multi-token phrases and aliases → category */
  var RULES = [
    { cat: 'Frontend', patterns: [/^(react|vue|angular|svelte|next|nuxt|gatsby|webpack|vite|parcel|html|css|sass|scss|less|tailwind|bootstrap|redux|mobx|javascript|typescript|jsx|tsx|jquery|d3)$/i] },
    { cat: 'Backend', patterns: [/^(node|nodejs|express|django|flask|fastapi|spring|laravel|rails|aspnet|graphql|rest|api|microservices|kafka|rabbitmq)$/i] },
    { cat: 'Database', patterns: [/^(sql|mysql|postgresql|postgres|mongodb|mongo|redis|sqlite|oracle|cassandra|dynamodb|elasticsearch|nosql)$/i] },
    { cat: 'Tools', patterns: [/^(git|github|gitlab|bitbucket|docker|kubernetes|k8s|jenkins|ci|cd|terraform|ansible|aws|azure|gcp|gcloud|linux|bash|jira|figma|slack)$/i] }
  ];

  function categorizeOne(skill) {
    var n = normalizeToken(skill);
    if (!n) return null;

    for (var i = 0; i < RULES.length; i++) {
      var cat = RULES[i].cat;
      var pats = RULES[i].patterns;
      for (var j = 0; j < pats.length; j++) {
        if (pats[j].test(n)) return cat;
      }
    }

    // Heuristic single-token fallbacks
    if (/^(js|ts|html5?|css3?)$/.test(n)) return 'Frontend';
    if (/^(python|java|go|rust|php|ruby|swift|kotlin|scala)$/.test(n)) return 'Backend';
    if (/(sql|db|database)/.test(n)) return 'Database';

    return 'Others';
  }

  /**
   * @param {string[]} skillsArray
   * @returns {{ name: string, value: number }[]}
   */
  function categorizeSkills(skillsArray) {
    var counts = { Frontend: 0, Backend: 0, Database: 0, Tools: 0, Others: 0 };
    if (!Array.isArray(skillsArray)) return [];

    var seen = Object.create(null);
    skillsArray.forEach(function (raw) {
      var cat = categorizeOne(String(raw));
      if (!cat) return;
      var key = normalizeToken(raw) + '|' + cat;
      if (seen[key]) return;
      seen[key] = true;
      counts[cat] = (counts[cat] || 0) + 1;
    });

    return CATEGORY_ORDER.map(function (name) {
      return { name: name, value: counts[name] || 0 };
    }).filter(function (row) {
      return row.value > 0;
    });
  }

  /**
   * Merge server-side skill_categories (arrays of strings per bucket) into chart rows.
   * @param {Record<string, string[]>} skillCategories
   * @returns {{ name: string, value: number }[]}
   */
  function fromServerCategories(skillCategories) {
    if (!skillCategories || typeof skillCategories !== 'object') return [];
    var labelMap = {
      frontend: 'Frontend',
      backend: 'Backend',
      database: 'Database',
      tools: 'Tools',
      others: 'Others'
    };
    var out = [];
    Object.keys(labelMap).forEach(function (key) {
      var arr = skillCategories[key];
      var n = Array.isArray(arr) ? arr.length : 0;
      if (n > 0) out.push({ name: labelMap[key], value: n });
    });
    return out;
  }

  /**
   * Prefer server buckets; if empty, derive from skills + optional keyword fallback.
   */
  function buildChartData(analysis) {
    var server = fromServerCategories(analysis && analysis.skill_categories);
    if (server.length > 0) return server;

    var skills = (analysis && analysis.found_skills) || [];
    var fromSkills = categorizeSkills(skills);
    if (fromSkills.length > 0) return fromSkills;

    var kws = (analysis && analysis.keywords) || [];
    if (kws.length > 0) return categorizeSkills(kws);

    return [];
  }

  global.SkillCategorizer = {
    categorizeSkills: categorizeSkills,
    fromServerCategories: fromServerCategories,
    buildChartData: buildChartData,
    normalizeToken: normalizeToken
  };
})(typeof window !== 'undefined' ? window : this);
