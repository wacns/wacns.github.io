// wacns.com — shared behaviour for every page.
// Each block checks for the elements it needs, so pages only get what they use.
(function () {
  'use strict';

  var doc = document.documentElement;
  var AR = doc.lang === 'ar';
  var LINKEDIN = 'https://www.linkedin.com/in/abdullah-mohammed-137928219';
  var GITHUB = 'https://github.com/wacns';
  var HOUR = 3600000;
  // Google Analytics 4 measurement ID (e.g. 'G-ABC123XYZ'). Empty = no banner, no tracking.
  var GA_ID = 'G-V7XNEPYZM1';
  // true = ask first (cookie banner). false = load Google Analytics for every visitor, no banner.
  // TEMPORARILY false at the owner's request; switch back to true when asked.
  var CONSENT_REQUIRED = false;
  // On unknown *.wacns.com hosts (which show the 404 page) site links must point back to wacns.com
  var BASE = (/\.wacns\.com$/.test(location.hostname) && location.hostname !== 'www.wacns.com') ? 'https://wacns.com' : '';

  // TIL entries listed in the command palette (newest first)
  var NOTES = [
    { title: '<bdi> stops .NET from turning into NET. in Arabic text', url: '/til/bdi-rtl/' },
    { title: 'One Worker, one site, and a 404 for every unknown subdomain', url: '/til/worker-subdomain-catch-all/' },
    { title: '.assetsignore decides what a Cloudflare Worker publishes', url: '/til/assetsignore/' }
  ];

  var T = AR ? {
    updated: 'آخر تحديث', contribOn: function (n, d) { return n + ' مساهمة في ' + d; },
    pages: 'الصفحات', sections: 'الأقسام', notes: 'تعلّمت اليوم', actions: 'إجراءات', links: 'روابط',
    home: 'الرئيسية', notesIndex: 'كل التدوينات', uses: 'أدواتي',
    themeToLight: 'التبديل إلى الوضع الفاتح', themeToDark: 'التبديل إلى الوضع الداكن',
    language: 'English', copyLink: 'نسخ رابط الصفحة', copied: 'تم النسخ',
    search: 'اكتب أمرًا أو ابحث…', empty: 'لا توجد نتائج', navigate: 'تنقّل', open: 'فتح', close: 'إغلاق',
    deployed: 'آخر تحديث للموقع'
  } : {
    updated: 'Updated', contribOn: function (n, d) { return n + (n === 1 ? ' contribution on ' : ' contributions on ') + d; },
    pages: 'Pages', sections: 'On this page', notes: 'Today I learned', actions: 'Actions', links: 'Links',
    home: 'Home', notesIndex: 'All TIL entries', uses: 'Uses',
    themeToLight: 'Switch to light theme', themeToDark: 'Switch to dark theme',
    language: 'العربية', copyLink: 'Copy page link', copied: 'Copied',
    search: 'Type a command or search…', empty: 'No results', navigate: 'navigate', open: 'open', close: 'close',
    deployed: 'Last updated'
  };

  function $(sel, root) { return (root || document).querySelector(sel); }
  function $all(sel, root) { return [].slice.call((root || document).querySelectorAll(sel)); }
  function store(key, val) { try { if (val === undefined) return localStorage.getItem(key); localStorage.setItem(key, val); } catch (e) { return null; } }
  function cacheGet(key, maxAge) {
    try { var c = JSON.parse(sessionStorage.getItem(key)); if (c && Date.now() - c.t < maxAge) return c.v; } catch (e) {}
    return null;
  }
  function cacheSet(key, v) { try { sessionStorage.setItem(key, JSON.stringify({ t: Date.now(), v: v })); } catch (e) {} }
  function getJSON(url) {
    return fetch(url).then(function (r) { return r.ok ? r.json() : null; }).catch(function () { return null; });
  }
  function ago(iso) {
    var secs = (new Date(iso) - Date.now()) / 1000;
    var units = [['year', 31536000], ['month', 2592000], ['week', 604800], ['day', 86400], ['hour', 3600], ['minute', 60]];
    try {
      var rtf = new Intl.RelativeTimeFormat(AR ? 'ar' : 'en', { numeric: 'auto' });
      for (var i = 0; i < units.length; i++) {
        if (Math.abs(secs) >= units[i][1]) return rtf.format(Math.round(secs / units[i][1]), units[i][0]);
      }
      return rtf.format(0, 'minute');
    } catch (e) { return new Date(iso).toISOString().slice(0, 10); }
  }

  // ── Toast ──
  var toastTimer;
  function toast(msg) {
    var el = $('#toast');
    if (!el) { el = document.createElement('div'); el.id = 'toast'; el.className = 'toast'; el.setAttribute('role', 'status'); document.body.appendChild(el); }
    el.textContent = msg;
    el.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { el.classList.remove('show'); }, 1800);
  }

  // ── Theme ──
  function setTheme(t) {
    doc.setAttribute('data-theme', t);
    store('theme', t);
    var meta = $('meta[name="theme-color"]');
    if (meta) meta.setAttribute('content', t === 'light' ? '#fafafc' : '#0a0a0f');
    var btn = $('#themeBtn');
    if (btn) btn.setAttribute('aria-label', t === 'light' ? T.themeToDark : T.themeToLight);
  }
  function toggleTheme() { setTheme(doc.getAttribute('data-theme') === 'light' ? 'dark' : 'light'); }
  setTheme(doc.getAttribute('data-theme') || 'dark');
  var themeBtn = $('#themeBtn');
  if (themeBtn) themeBtn.addEventListener('click', toggleTheme);

  // ── Reveal on scroll (and highlighter marks) ──
  (function () {
    var items = $all('.reveal, mark');
    if (!('IntersectionObserver' in window)) { items.forEach(function (el) { el.classList.add('in'); }); return; }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
    }, { rootMargin: '0px 0px -8% 0px' });
    items.forEach(function (el) { io.observe(el); });
  })();

  // ── Top bar: border once scrolled, highlight the section in view ──
  (function () {
    var bar = $('#topbar');
    if (!bar) return;
    var links = $all('.topnav a[href^="#"]');
    function onScroll() {
      bar.classList.toggle('scrolled', window.scrollY > 8);
      var current = null;
      links.forEach(function (a) {
        var sec = document.getElementById(a.getAttribute('href').slice(1));
        if (sec && sec.offsetParent !== null && sec.getBoundingClientRect().top <= 120) current = a;
      });
      links.forEach(function (a) { a.classList.toggle('active', a === current); });
    }
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  })();

  // ── Short / long intro ──
  (function () {
    var toggle = $('#introToggle');
    if (!toggle) return;
    var buttons = $all('button', toggle);
    function show(which) {
      buttons.forEach(function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-intro') === which)); });
      $all('[data-intro-text]').forEach(function (p) { p.hidden = p.getAttribute('data-intro-text') !== which; });
      $all('[data-intro-text="' + which + '"] mark').forEach(function (m) { m.classList.add('in'); });
      store('intro', which);
      if (which === 'long') doc.setAttribute('data-intro', 'long'); else doc.removeAttribute('data-intro');
    }
    buttons.forEach(function (b) { b.addEventListener('click', function () { show(b.getAttribute('data-intro')); }); });
    show(store('intro') === 'long' ? 'long' : 'short');
  })();

  // ── Code cards: fade hint when the code scrolls sideways ──
  function markScrollers() {
    $all('.code-card').forEach(function (c) {
      var pre = $('pre', c);
      if (pre) c.classList.toggle('scrolls', pre.scrollWidth > pre.clientWidth + 2);
    });
  }
  markScrollers();
  window.addEventListener('resize', markScrollers);

  // ── Live GitHub stats on project cards ──
  $all('.card[data-repo]').forEach(function (card) {
    var repo = card.getAttribute('data-repo'), key = 'gh:' + repo;
    function render(r) {
      var meta = $('.card-meta', card);
      if (!meta || !r) return;
      var parts = [];
      if (r.language) parts.push('<span><span class="lang-dot"></span>' + r.language + '</span>');
      if (r.stargazers_count > 0) parts.push('<span>★ ' + r.stargazers_count + '</span>');
      if (r.pushed_at) parts.push('<span>' + T.updated + ' ' + ago(r.pushed_at) + '</span>');
      meta.innerHTML = parts.join('');
    }
    var cached = cacheGet(key, HOUR);
    if (cached) { render(cached); return; }
    getJSON('https://api.github.com/repos/' + repo).then(function (r) {
      if (!r) return;
      var slim = { language: r.language, stargazers_count: r.stargazers_count, pushed_at: r.pushed_at };
      cacheSet(key, slim);
      render(slim);
    });
  });

  // ── Stats row: project count + GitHub join year ──
  (function () {
    var n = $('#statProjects');
    if (n) n.textContent = $all('#projects .card').length;
    var since = $('#statSince');
    if (!since) return;
    function show(y) { if (!y) return; $('#statSinceN').textContent = y; since.classList.remove('pending'); }
    var cached = cacheGet('gh:user:wacns', 24 * HOUR);
    if (cached) { show(cached); return; }
    getJSON('https://api.github.com/users/' + 'wacns').then(function (u) {
      if (!u || !u.created_at) return;
      var y = new Date(u.created_at).getUTCFullYear();
      cacheSet('gh:user:wacns', y);
      show(y);
    });
  })();

  // ── GitHub contribution heatmap (hidden if the data can't be loaded) ──
  (function () {
    var graph = $('#activityGraph');
    if (!graph) return;
    function draw(data) {
      var days = ((data && data.contributions) || []).filter(function (d) { return d && d.date; });
      if (!days.length) return;
      days.sort(function (a, b) { return a.date < b.date ? -1 : 1; });
      var total = (data.total && data.total.lastYear) || days.reduce(function (s, d) { return s + (d.count || 0); }, 0);
      var cell = 10, gap = 3, step = cell + gap;
      var firstDow = new Date(days[0].date + 'T00:00:00Z').getUTCDay();
      var weeks = Math.ceil((days.length + firstDow) / 7);
      var w = weeks * step - gap, h = 7 * step - gap;
      var rects = days.map(function (d, i) {
        var idx = i + firstDow, lvl = Math.max(0, Math.min(4, d.level || 0));
        return '<rect class="h' + lvl + '" x="' + Math.floor(idx / 7) * step + '" y="' + (idx % 7) * step +
          '" width="' + cell + '" height="' + cell + '" rx="2"><title>' + T.contribOn(d.count, d.date) + '</title></rect>';
      }).join('');
      graph.innerHTML = '<svg class="hm" viewBox="0 0 ' + w + ' ' + h + '" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">' + rects + '</svg>';
      var totalText = total.toLocaleString('en-US');
      $('#activityCount').textContent = totalText;
      var stat = $('#statContrib');
      if (stat) { $('#statContribN').textContent = totalText; stat.classList.remove('pending'); }
      var band = $('#activityBand');
      if (band) band.hidden = false;
    }
    var cached = cacheGet('gh:contrib:wacns', HOUR);
    if (cached) { draw(cached); return; }
    getJSON('https://github-contributions-api.jogruber.de/v4/wacns?y=last').then(function (d) {
      if (!d) return;
      cacheSet('gh:contrib:wacns', d);
      draw(d);
    });
  })();

  // ── Colophon: last site update from the repo's latest commit ──
  (function () {
    var el = $('#lastDeploy');
    if (!el) return;
    function show(c) {
      if (!c) return;
      el.innerHTML = '';
      el.append(T.deployed + ' ' + ago(c.date) + ' · ');
      var a = document.createElement('a');
      a.href = 'https://github.com/wacns/wacns.github.io/commit/' + c.sha;
      a.target = '_blank';
      a.rel = 'noopener';
      a.textContent = c.sha.slice(0, 7);
      el.appendChild(a);
      el.hidden = false;
    }
    var cached = cacheGet('gh:site-commit', HOUR);
    if (cached) { show(cached); return; }
    getJSON('https://api.github.com/repos/wacns/wacns.github.io/commits/main').then(function (r) {
      if (!r || !r.sha) return;
      var c = { sha: r.sha, date: r.commit && r.commit.committer && r.commit.committer.date };
      if (!c.date) return;
      cacheSet('gh:site-commit', c);
      show(c);
    });
  })();

  // ── Command palette (Ctrl/⌘+K, "/" or the topbar button) ──
  (function () {
    var root = $('#palette'), openBtn = $('#paletteBtn');
    if (!root) return;
    var input = $('.palette-input', root), list = $('.palette-list', root);
    var items = [], filtered = [], selected = 0, lastFocus = null;
    var homePath = AR ? '/ar/' : '/';

    function go(url) { return function () { window.location.href = BASE + url; }; }
    function build() {
      items = [];
      $all('.topnav a[href^="#"]').forEach(function (a) {
        var id = a.getAttribute('href');
        items.push({ group: T.sections, label: a.textContent.trim(), run: function () { var t = document.getElementById(id.slice(1)); if (t) t.scrollIntoView(); history.replaceState(null, '', id); } });
      });
      items.push({ group: T.pages, label: T.home, hint: homePath, run: go(homePath) });
      items.push({ group: T.pages, label: T.notesIndex, hint: '/til/', run: go('/til/') });
      items.push({ group: T.pages, label: T.uses, hint: '/uses/', run: go('/uses/') });
      NOTES.forEach(function (n) { items.push({ group: T.notes, label: n.title, run: go(n.url) }); });
      items.push({ group: T.actions, label: doc.getAttribute('data-theme') === 'light' ? T.themeToDark : T.themeToLight, run: toggleTheme });
      items.push({ group: T.actions, label: T.language, hint: AR ? '/' : '/ar/', run: go(AR ? '/' : '/ar/') });
      items.push({ group: T.actions, label: T.copyLink, run: function () {
        if (navigator.clipboard) navigator.clipboard.writeText(location.href.split('#')[0]).then(function () { toast(T.copied); });
      } });
      items.push({ group: T.links, label: 'GitHub', hint: 'github.com/wacns', run: function () { window.open(GITHUB, '_blank', 'noopener'); } });
      items.push({ group: T.links, label: 'LinkedIn', run: function () { window.open(LINKEDIN, '_blank', 'noopener'); } });
    }
    function render() {
      var q = input.value.trim().toLowerCase();
      filtered = items.filter(function (it) { return !q || (it.label + ' ' + it.group + ' ' + (it.hint || '')).toLowerCase().indexOf(q) >= 0; });
      if (selected >= filtered.length) selected = Math.max(0, filtered.length - 1);
      list.innerHTML = '';
      if (!filtered.length) { var e = document.createElement('li'); e.className = 'palette-empty'; e.textContent = T.empty; list.appendChild(e); input.removeAttribute('aria-activedescendant'); return; }
      var group = null;
      filtered.forEach(function (it, i) {
        if (it.group !== group) {
          group = it.group;
          var g = document.createElement('li'); g.className = 'palette-group'; g.setAttribute('role', 'presentation'); g.textContent = group; list.appendChild(g);
        }
        var li = document.createElement('li');
        li.className = 'palette-item';
        li.id = 'pal-' + i;
        li.setAttribute('role', 'option');
        li.setAttribute('aria-selected', String(i === selected));
        var label = document.createElement('span'); label.textContent = it.label; li.appendChild(label);
        if (it.hint) { var s = document.createElement('small'); s.textContent = it.hint; li.appendChild(s); }
        li.addEventListener('mousemove', function () { if (selected !== i) { selected = i; mark(); } });
        li.addEventListener('click', function () { run(i); });
        list.appendChild(li);
      });
      mark();
    }
    function mark() {
      $all('.palette-item', list).forEach(function (li) { li.setAttribute('aria-selected', String(li.id === 'pal-' + selected)); });
      var cur = $('#pal-' + selected);
      if (cur) { input.setAttribute('aria-activedescendant', cur.id); cur.scrollIntoView({ block: 'nearest' }); }
    }
    function run(i) { var it = filtered[i]; if (!it) return; close(); it.run(); }
    function open() {
      if (!root.hidden) return;
      lastFocus = document.activeElement;
      build();
      input.value = '';
      selected = 0;
      root.hidden = false;
      render();
      input.focus();
    }
    function close() {
      root.hidden = true;
      if (lastFocus && lastFocus.focus) lastFocus.focus();
    }
    input.setAttribute('placeholder', T.search);
    input.addEventListener('input', function () { selected = 0; render(); });
    input.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowDown') { e.preventDefault(); selected = (selected + 1) % Math.max(1, filtered.length); mark(); }
      else if (e.key === 'ArrowUp') { e.preventDefault(); selected = (selected - 1 + filtered.length) % Math.max(1, filtered.length); mark(); }
      else if (e.key === 'Enter') { e.preventDefault(); run(selected); }
      else if (e.key === 'Escape') { e.preventDefault(); close(); }
      else if (e.key === 'Tab') { e.preventDefault(); }
    });
    root.addEventListener('mousedown', function (e) { if (e.target === root) close(); });
    if (openBtn) openBtn.addEventListener('click', open);
    document.addEventListener('keydown', function (e) {
      var typing = /^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName) || document.activeElement.isContentEditable;
      if ((e.key === 'k' || e.key === 'K') && (e.metaKey || e.ctrlKey)) { e.preventDefault(); root.hidden ? open() : close(); }
      else if (e.key === '/' && !typing && root.hidden) { e.preventDefault(); open(); }
    });
    var hint = $('.palette-hint', root);
    if (hint) hint.innerHTML = '<span><kbd>↑↓</kbd> ' + T.navigate + '</span><span><kbd>↵</kbd> ' + T.open + '</span><span><kbd>esc</kbd> ' + T.close + '</span>';
  })();

  // ── Cookie consent + Google Analytics (loads only after "Allow") ──
  (function () {
    var banner = $('#consent'), settings = $('#cookieSettings');
    if (!GA_ID || !banner || BASE) return;   // not configured, or on a 404 subdomain
    var KEY = 'consent:analytics';

    function loadGA() {
      if (window.__gaLoaded) return;
      window.__gaLoaded = true;
      window['ga-disable-' + GA_ID] = false;
      window.dataLayer = window.dataLayer || [];
      window.gtag = function () { window.dataLayer.push(arguments); };
      window.gtag('js', new Date());
      window.gtag('config', GA_ID);
      var sc = document.createElement('script');
      sc.async = true;
      sc.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(GA_ID);
      document.head.appendChild(sc);
    }
    function stopGA() {
      window['ga-disable-' + GA_ID] = true;
      // Remove Google Analytics cookies on this host and the parent domain
      document.cookie.split(';').forEach(function (c) {
        var name = c.split('=')[0].trim();
        if (!/^_ga/.test(name)) return;
        var host = location.hostname, parts = host.split('.');
        [host, '.' + host, '.' + parts.slice(-2).join('.')].forEach(function (d) {
          document.cookie = name + '=; Max-Age=0; path=/; domain=' + d;
        });
        document.cookie = name + '=; Max-Age=0; path=/';
      });
    }
    function decide(choice) {
      store(KEY, choice);
      banner.hidden = true;
      if (choice === 'granted') loadGA(); else stopGA();
    }

    $all('[data-consent]', banner).forEach(function (b) {
      b.addEventListener('click', function () { decide(b.getAttribute('data-consent')); });
    });
    if (settings) {
      settings.hidden = false;
      settings.addEventListener('click', function () { banner.hidden = false; var first = $('button', banner); if (first) first.focus(); });
    }

    if (!CONSENT_REQUIRED) {
      if (settings) settings.hidden = true;
      loadGA();
      return;
    }
    var saved = store(KEY);
    if (saved === 'granted') loadGA();
    else if (saved !== 'denied') banner.hidden = false;
  })();
})();
