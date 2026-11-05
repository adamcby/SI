/* SI marketing — lancement de l'iPhone Duo. Logique front commune (Alpine.js + Chart.js), 100 % hors-ligne. */
(function () {
  'use strict';
  const SI = (window.SI = window.SI || {});
  const params = new URLSearchParams(location.search);
  SI.capture = params.get('capture') === '1';

  // ------------------------------------------------------------------ palette validée (daltonisme) et statuts
  SI.palette = ['#0071e3', '#eb6834', '#1baf7a', '#eda100', '#e87ba4', '#008300', '#6250d6', '#e34948'];
  SI.statuts = { ok: '#0ca30c', warn: '#fab219', serious: '#ec835a', crit: '#d03b3b' };
  SI.encre = { primaire: '#1d1d1f', secondaire: '#424245', douce: '#6e6e73', grille: '#e8e8ed', axe: '#d2d2d7' };

  // ------------------------------------------------------------------ formats français
  const nf = (d) => new Intl.NumberFormat('fr-FR', { minimumFractionDigits: d, maximumFractionDigits: d });
  SI.fmt = {
    n(v, d = 0) { return v === null || v === undefined || isNaN(v) ? '—' : nf(d).format(v); },
    eur(v, d = 0) { return v === null || v === undefined || isNaN(v) ? '—' : nf(d).format(v) + ' €'; },
    pct(v, d = 1) { return v === null || v === undefined || isNaN(v) ? '—' : nf(d).format(v) + ' %'; },
    compact(v) {
      if (v === null || v === undefined || isNaN(v)) return '—';
      const a = Math.abs(v);
      if (a >= 1e6) return nf(a >= 1e7 ? 1 : 2).format(v / 1e6) + ' M';
      if (a >= 1e4) return nf(1).format(v / 1e3) + ' k';
      return nf(0).format(v);
    },
    date(iso) {
      if (!iso) return '—';
      const d = new Date(iso.length === 10 ? iso + 'T00:00:00' : iso);
      return d.toLocaleDateString('fr-FR', { weekday: 'short', day: 'numeric', month: 'short' });
    },
    jour(iso) { if (!iso) return '—'; const d = new Date(iso.slice(0, 10) + 'T00:00:00'); return d.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' }); },
    heure(iso) { return iso ? iso.slice(11, 16) : '—'; },
    dh(iso) { if (!iso) return '—'; return SI.fmt.jour(iso) + ' · ' + iso.slice(11, 16); },
  };

  // ------------------------------------------------------------------ API
  SI.acteur = () => document.body.dataset.acteur;
  SI.api = async function (methode, url, corps) {
    const opts = { method: methode, headers: { 'Content-Type': 'application/json' } };
    if (corps !== undefined) opts.body = JSON.stringify(corps);
    const r = await fetch(url, opts);
    let data = null;
    try { data = await r.json(); } catch (e) { data = null; }
    if (!r.ok) {
      const msg = (data && data.detail) ? (typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail)) : ('Erreur ' + r.status);
      const err = new Error(msg); err.status = r.status; throw err;
    }
    return data;
  };
  SI.get = (url) => SI.api('GET', url);
  // Action d'un acteur : ajoute l'acteur courant, affiche un toast, prévient tous les composants
  SI.agir = async function (url, corps, succes) {
    try {
      const res = await SI.api('POST', url, Object.assign({ acteur: SI.acteur() }, corps || {}));
      SI.toast(succes || (res && res.message) || 'Action enregistrée dans le SI.', 'ok');
      window.dispatchEvent(new CustomEvent('si:maj'));
      return res;
    } catch (e) {
      SI.toast(e.message, e.status === 403 ? 'warn' : 'crit');
      throw e;
    }
  };

  // ------------------------------------------------------------------ toasts
  SI.toast = function (message, type = 'info', flux = []) {
    window.dispatchEvent(new CustomEvent('si:toast', { detail: { message, type, flux, id: Date.now() + Math.random() } }));
  };

  // ------------------------------------------------------------------ référentiel (mis en cache)
  let refPromise = null;
  SI.referentiel = function () {
    if (!refPromise) refPromise = SI.get('/api/referentiel');
    return refPromise;
  };

  // ------------------------------------------------------------------ changement d'acteur
  SI.changerActeur = function (code, ecranSlug) {
    document.cookie = 'acteur=' + code + '; path=/; max-age=2592000; samesite=lax';
    const insp = document.body.classList.contains('inspection') ? '?inspection=1' : '';
    if (location.pathname.startsWith('/a/') || ecranSlug) {
      location.href = '/a/' + code + (ecranSlug ? '/' + ecranSlug : '') + insp;
    } else {
      location.reload();
    }
  };
  SI.aller = function (url, acteur) {
    if (acteur) document.cookie = 'acteur=' + acteur + '; path=/; max-age=2592000; samesite=lax';
    location.href = url;
  };

  // ------------------------------------------------------------------ graphiques (Chart.js, specs de la charte data-viz)
  SI.graphiques = {};
  SI.graphique = function (id, type, labels, series, options = {}) {
    const el = typeof id === 'string' ? document.getElementById(id) : id;
    if (!el || !window.Chart) return null;
    const cle = el.id || Math.random().toString(36);
    if (SI.graphiques[cle]) SI.graphiques[cle].destroy();
    const plusieurs = series.length > 1;
    const datasets = series.map((s, i) => {
      const c = s.couleur || SI.palette[s.slot !== undefined ? s.slot : i];
      const base = { label: s.nom, data: s.valeurs, borderColor: c, backgroundColor: c };
      if (type === 'line') {
        Object.assign(base, { borderWidth: 2, pointRadius: 0, pointHoverRadius: 5, pointHoverBorderWidth: 2,
          pointHoverBorderColor: '#fff', tension: 0.25, fill: s.aire ? 'origin' : false,
          backgroundColor: s.aire ? c + '1a' : c, borderDash: s.pointille ? [6, 4] : undefined });
      }
      if (type === 'bar') {
        Object.assign(base, { borderRadius: 4, borderSkipped: 'start', maxBarThickness: 24, categoryPercentage: 0.7,
          barPercentage: 0.9, borderWidth: 0 });
      }
      return Object.assign(base, s.extra || {});
    });
    const empile = !!options.empile;
    const cfg = {
      type,
      data: { labels, datasets },
      options: {
        responsive: true, maintainAspectRatio: false, animation: SI.capture ? false : { duration: 350 },
        interaction: { mode: type === 'line' ? 'index' : 'nearest', intersect: false },
        indexAxis: options.horizontal ? 'y' : 'x',
        plugins: {
          legend: { display: plusieurs && options.legende !== false, position: 'top', align: 'start',
            labels: { usePointStyle: true, pointStyle: type === 'line' ? 'line' : 'rectRounded', boxWidth: 18, boxHeight: 8,
              color: SI.encre.secondaire, font: { size: 12 } } },
          tooltip: { backgroundColor: '#1d1d1f', titleColor: '#fff', bodyColor: '#fff', padding: 10, cornerRadius: 10,
            displayColors: true, boxWidth: 10, boxHeight: 3, usePointStyle: false,
            callbacks: { label: (ctx) => ' ' + (ctx.dataset.label ? ctx.dataset.label + ' : ' : '') + (options.formatVal || SI.fmt.n)(ctx.parsed[options.horizontal ? 'x' : 'y']) } },
        },
        scales: (() => {
          const fmtAxe = options.formatAxe || SI.fmt.compact;
          const valeur = { stacked: empile, beginAtZero: options.zero !== false, suggestedMax: options.max,
            grid: { color: SI.encre.grille, drawTicks: false }, border: { display: false },
            ticks: { color: SI.encre.douce, font: { size: 11 }, padding: 8, callback: (v) => fmtAxe(v) } };
          const categorie = { stacked: empile, grid: { display: false }, border: { color: SI.encre.axe },
            ticks: { color: SI.encre.douce, font: { size: 11 }, maxRotation: 0, autoSkipPadding: 14 } };
          return options.horizontal ? { x: valeur, y: categorie } : { x: categorie, y: valeur };
        })(),
      },
    };
    if (type === 'doughnut') { delete cfg.options.scales; cfg.options.cutout = '68%'; }
    if (options.cfg) options.cfg(cfg);
    SI.graphiques[cle] = new Chart(el, cfg);
    return SI.graphiques[cle];
  };

  // ------------------------------------------------------------------ rendu BPMN (couloirs en colonnes, comme dans le dossier)
  const TW = 236, TH = 92, GD = 64, ER = 44;
  function ancre(n, cote) {
    const demi = n.type === 'tache' ? [TW / 2, TH / 2] : n.type === 'passerelle' ? [GD, GD] : [ER, ER];
    return { t: [n.x, n.y - demi[1]], b: [n.x, n.y + demi[1]], l: [n.x - demi[0], n.y], r: [n.x + demi[0], n.y] }[cote];
  }
  const NORMALE = { t: [0, -1], b: [0, 1], l: [-1, 0], r: [1, 0] };
  function decouper(texte, max) {
    const lignes = [];
    texte.split('\n').forEach((bloc) => {
      let ligne = '';
      bloc.split(' ').forEach((mot) => {
        if ((ligne + ' ' + mot).trim().length > max && ligne) { lignes.push(ligne); ligne = mot; } else { ligne = (ligne + ' ' + mot).trim(); }
      });
      if (ligne) lignes.push(ligne);
    });
    return lignes;
  }
  const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  SI.esc = esc;

  SI.dessinerBPMN = function (svg, proc, etat, opts) {
    etat = etat || {}; opts = opts || {};
    const [W, H] = proc.viewbox;
    svg.setAttribute('viewBox', '0 0 ' + W + ' ' + H);
    const surligner = new Set(opts.surligner || []);
    const actifs = new Set(opts.actifs || []);
    const faits = new Set(opts.faits || []);
    const fluxTr = {};
    (proc.flux_transitions || []).forEach((s) => { const [ab, code] = s.split(':'); fluxTr[ab] = code; });
    let h = '<defs><marker id="fl-' + proc.code + '" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="9" markerHeight="9" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#1d1d1f"/></marker></defs>';
    proc.couloirs.forEach((c, i) => {
      h += '<rect x="' + c.x + '" y="0" width="' + c.w + '" height="' + H + '" fill="' + (i % 2 ? '#fbfbfd' : '#ffffff') + '" stroke="#d2d2d7" stroke-width="2"/>';
      h += '<rect x="' + c.x + '" y="0" width="' + c.w + '" height="70" fill="#f5f5f7" stroke="#d2d2d7" stroke-width="2"/>';
      decouper(c.libelle, 26).forEach((l, k, arr) => {
        h += '<text x="' + (c.x + c.w / 2) + '" y="' + (40 - (arr.length - 1) * 12 + k * 24) + '" text-anchor="middle" font-size="19" font-weight="600" fill="#424245" letter-spacing="0.5">' + esc(l) + '</text>';
      });
    });
    // transitions
    proc.transitions.forEach(([a, b, issue, sa, sb]) => {
      const na = proc.noeuds[a], nb = proc.noeuds[b];
      const p0 = ancre(na, sa), p3 = ancre(nb, sb);
      const dist = Math.hypot(p3[0] - p0[0], p3[1] - p0[1]);
      const k = Math.max(50, Math.min(240, dist * 0.38));
      const p1 = [p0[0] + NORMALE[sa][0] * k, p0[1] + NORMALE[sa][1] * k];
      const p2 = [p3[0] + NORMALE[sb][0] * k, p3[1] + NORMALE[sb][1] * k];
      const fait = faits.has(a + '>' + b);
      h += '<path d="M' + p0 + ' C' + p1 + ' ' + p2 + ' ' + p3 + '" fill="none" stroke="' + (fait ? '#0ca30c' : '#1d1d1f') + '" stroke-width="' + (fait ? 3.5 : 2) + '" marker-end="url(#fl-' + proc.code + ')"/>';
      if (issue) {
        const lib = (na.libelles_issues && na.libelles_issues[issue]) || issue;
        const lx = p0[0] + NORMALE[sa][0] * 34 + (sa === 't' || sa === 'b' ? 26 : 0);
        const ly = p0[1] + NORMALE[sa][1] * 34 + (sa === 'l' || sa === 'r' ? -12 : 6);
        h += '<text x="' + lx + '" y="' + ly + '" font-size="19" font-style="italic" fill="#424245" text-anchor="middle">' + esc(lib) + '</text>';
      }
      const code = fluxTr[a + '>' + b];
      if (code && opts.flux !== false) {
        const t = 0.5, u = 1 - t;
        const mx = u * u * u * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t * t * t * p3[0];
        const my = u * u * u * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t * t * t * p3[1];
        h += '<g class="flux-chip" data-flux="' + code + '"><rect x="' + (mx - 42) + '" y="' + (my - 15) + '" width="84" height="30" rx="8" fill="#e8f2fd" stroke="#0071e3" stroke-width="1"/><text x="' + mx + '" y="' + (my + 6) + '" text-anchor="middle" font-size="16" font-family="SF Mono, Menlo, monospace" fill="#0066cc">' + code + '</text></g>';
      }
    });
    // nœuds
    Object.entries(proc.noeuds).forEach(([id, n]) => {
      const info = etat[id] || {};
      const actif = actifs.has(id) || (info.jetons || 0) > 0;
      const passe = (info.passages || 0) > 0 || faits.has(id);
      const stroke = actif ? '#0071e3' : passe ? '#1d1d1f' : '#1d1d1f';
      const fill = actif ? '#e8f2fd' : '#ffffff';
      h += '<g class="noeud" data-noeud="' + id + '">';
      if (surligner.has(id)) {
        const m = n.type === 'tache' ? [TW / 2 + 12, TH / 2 + 12] : [GD + 16, GD + 16];
        h += '<rect x="' + (n.x - m[0]) + '" y="' + (n.y - m[1]) + '" width="' + 2 * m[0] + '" height="' + 2 * m[1] + '" rx="24" fill="#6250d6" fill-opacity="0.08" stroke="#6250d6" stroke-width="3" stroke-dasharray="10 7"/>';
      }
      if (n.type === 'tache') {
        h += '<rect class="forme" x="' + (n.x - TW / 2) + '" y="' + (n.y - TH / 2) + '" width="' + TW + '" height="' + TH + '" rx="20" fill="' + fill + '" stroke="' + stroke + '" stroke-width="' + (actif ? 4 : 2) + '"/>';
        const lignes = decouper(n.libelle, n.auto ? 17 : 19);
        lignes.forEach((l, k) => {
          h += '<text x="' + (n.x + (n.auto ? 8 : 0)) + '" y="' + (n.y + 7 - (lignes.length - 1) * 12 + k * 24) + '" text-anchor="middle" font-size="20" fill="#1d1d1f">' + esc(l) + '</text>';
        });
        if (n.auto) {
          h += '<g transform="translate(' + (n.x - TW / 2 + 9) + ',' + (n.y - TH / 2 + 9) + ')"><circle cx="8" cy="8" r="7" fill="none" stroke="#6e6e73" stroke-width="2.2"/><circle cx="8" cy="8" r="2.6" fill="#6e6e73"/></g>';
        }
      } else if (n.type === 'passerelle') {
        h += '<path class="forme" d="M' + n.x + ',' + (n.y - GD) + ' L' + (n.x + GD) + ',' + n.y + ' L' + n.x + ',' + (n.y + GD) + ' L' + (n.x - GD) + ',' + n.y + ' Z" fill="' + fill + '" stroke="' + stroke + '" stroke-width="' + (actif ? 4 : 2) + '"/>';
        const lignes = n.libelle.split('\n');
        lignes.forEach((l, k) => {
          h += '<text x="' + n.x + '" y="' + (n.y + 6 - (lignes.length - 1) * 10.5 + k * 21) + '" text-anchor="middle" font-size="17.5" fill="#1d1d1f">' + esc(l) + '</text>';
        });
      } else {
        const fin = n.type === 'fin';
        h += '<circle class="forme" cx="' + n.x + '" cy="' + n.y + '" r="' + ER + '" fill="#ffffff" stroke="#1d1d1f" stroke-width="' + (fin ? 6 : 2) + '"/>';
        if (fin) h += '<circle cx="' + n.x + '" cy="' + n.y + '" r="' + (ER - 9) + '" fill="none" stroke="#1d1d1f" stroke-width="2"/>';
        const lignes = n.libelle.split('\n');
        lignes.forEach((l, k) => {
          h += '<text x="' + n.x + '" y="' + (n.y + 6 - (lignes.length - 1) * 10 + k * 20) + '" text-anchor="middle" font-size="17" fill="#1d1d1f">' + esc(l) + '</text>';
        });
      }
      if ((info.jetons || 0) > 0) {
        const bx = n.x + (n.type === 'tache' ? TW / 2 - 6 : GD - 6), by = n.y - (n.type === 'tache' ? TH / 2 : GD) + 4;
        const txt = SI.fmt.compact(info.jetons);
        const bw = Math.max(40, 14 + txt.length * 12);
        h += '<g class="jeton-pulse"><rect x="' + (bx - bw / 2) + '" y="' + (by - 20) + '" width="' + bw + '" height="40" rx="20" fill="#0071e3" stroke="#fff" stroke-width="3"/><text x="' + bx + '" y="' + (by + 7) + '" text-anchor="middle" font-size="19" font-weight="700" fill="#fff">' + txt + '</text></g>';
      }
      if ((info.passages || 0) > 0 && opts.passages !== false && n.type !== 'debut') {
        const py = n.y + (n.type === 'tache' ? TH / 2 : n.type === 'passerelle' ? GD : ER) + 24;
        h += '<text x="' + n.x + '" y="' + py + '" text-anchor="middle" font-size="16" fill="#006300">✓ ' + SI.fmt.compact(info.passages) + '</text>';
      }
      h += '</g>';
    });
    svg.innerHTML = h;
    if (opts.onClic) {
      svg.querySelectorAll('.noeud').forEach((g) => g.addEventListener('click', () => opts.onClic(g.dataset.noeud)));
    }
    if (opts.onFlux) {
      svg.querySelectorAll('.flux-chip').forEach((g) => { g.style.cursor = 'pointer'; g.addEventListener('click', (e) => { e.stopPropagation(); opts.onFlux(g.dataset.flux); }); });
    }
  };

  // ------------------------------------------------------------------ composants Alpine globaux
  document.addEventListener('alpine:init', () => {
    Alpine.store('ui', {
      inspection: false,
      init() {
        let v = false;
        try { v = localStorage.getItem('si-inspection') === '1'; } catch (e) { /* stockage indisponible */ }
        if (params.get('inspection') === '1') v = true;
        if (params.get('inspection') === '0') v = false;
        this.inspection = v;
        document.body.classList.toggle('inspection', v);
      },
      basculer() {
        this.inspection = !this.inspection;
        try { localStorage.setItem('si-inspection', this.inspection ? '1' : '0'); } catch (e) { /* ignoré */ }
        document.body.classList.toggle('inspection', this.inspection);
        setTimeout(() => window.dispatchEvent(new CustomEvent('si:inspection')), 30);
      },
    });

    // Barre supérieure : acteur, horloge, notifications
    Alpine.data('barre', () => ({
      menuActeur: false, menuHorloge: false, menuNotif: false, recherche: '',
      horloge: null, base: 0, recu: 0, affichage: '', notifs: { non_lues: 0, items: [] },
      async init() {
        await this.chargerHorloge();
        setInterval(() => this.tic(), 1000);
        this.chargerNotifs();
        setInterval(() => this.chargerNotifs(), 6000);
        window.addEventListener('si:maj', () => { this.chargerNotifs(); this.chargerHorloge(); });
        window.addEventListener('keydown', (e) => {
          const tag = (e.target.tagName || '').toLowerCase();
          if (['input', 'textarea', 'select'].includes(tag) || e.metaKey || e.ctrlKey || e.altKey) return;
          if (e.key === 'i') Alpine.store('ui').basculer();
          if (e.key === 'a') { this.menuActeur = !this.menuActeur; this.$nextTick(() => this.$refs.rech && this.$refs.rech.focus()); }
          if (e.key === 'Escape') { this.menuActeur = false; this.menuHorloge = false; this.menuNotif = false; }
        });
      },
      async chargerHorloge() {
        try { this.horloge = await SI.get('/api/horloge'); this.base = new Date(this.horloge.iso).getTime(); this.recu = Date.now(); this.tic(); } catch (e) { /* hors-ligne */ }
      },
      tic() {
        if (!this.horloge) return;
        const ms = this.base + (Date.now() - this.recu) * (this.horloge.vitesse || 0);
        const d = new Date(ms);
        this.affichage = d.toLocaleDateString('fr-FR', { weekday: 'short', day: 'numeric', month: 'short' }) + ' · ' + d.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
      },
      async regler(corps) {
        try {
          this.horloge = await SI.api('POST', '/api/horloge', corps);
          this.base = new Date(this.horloge.iso).getTime(); this.recu = Date.now();
          SI.toast('Horloge du SI : ' + this.horloge.libelle, 'info');
          setTimeout(() => location.reload(), 350);
        } catch (e) { SI.toast(e.message, 'crit'); }
      },
      async reinitialiser() {
        if (!confirm('Réinitialiser la base ? Les données saisies pendant la démonstration seront effacées.')) return;
        SI.toast('Réinitialisation de la base en cours…', 'info');
        try { await SI.api('POST', '/api/demo/reinitialiser', {}); location.href = '/'; } catch (e) { SI.toast(e.message, 'crit'); }
      },
      async chargerNotifs() {
        try {
          const n = await SI.get('/api/notifications?acteur=' + SI.acteur());
          if (this.notifs.items.length && n.items.length && n.items[0].id !== this.notifs.items[0].id && n.non_lues > this.notifs.non_lues) {
            const it = n.items[0];
            SI.toast(it.titre, 'info', it.code ? [it.code] : []);
          }
          this.notifs = n;
        } catch (e) { /* ignoré */ }
      },
      async toutLu() { await SI.api('POST', '/api/notifications/lues', { acteur: SI.acteur() }); this.chargerNotifs(); },
    }));

    // File « À faire dans le SI » (démo guidée)
    Alpine.data('guide', () => ({
      ouvert: false, taches: [], acteurs: {},
      async init() {
        if (SI.capture) return;
        const ref = await SI.referentiel();
        this.acteurs = ref.acteurs; this.ecrans = ref.ecrans;
        this.charger();
        setInterval(() => this.charger(), 8000);
        window.addEventListener('si:maj', () => this.charger());
      },
      async charger() { try { this.taches = await SI.get('/api/files'); } catch (e) { /* ignoré */ } },
      urlEcran(t) {
        const e = (this.ecrans || []).find((x) => x.code === t.ecran);
        let u = e ? e.url : '/';
        if (t.type === 'campagne') u += '?c=' + t.objet_id;
        if (t.type === 'analyse') u += '?a=' + t.objet_id;
        return u;
      },
      mesTaches() { return this.taches.filter((t) => t.acteurs.includes(SI.acteur())); },
      autres() { return this.taches.filter((t) => !t.acteurs.includes(SI.acteur())).slice(0, 8); },
      nomActeur(c) { return this.acteurs[c] ? this.acteurs[c].court : c; },
    }));

    // Toasts
    Alpine.data('toasts', () => ({
      liste: [],
      init() {
        window.addEventListener('si:toast', (e) => {
          const t = e.detail; this.liste.push(t);
          setTimeout(() => { this.liste = this.liste.filter((x) => x.id !== t.id); }, t.type === 'crit' || t.type === 'warn' ? 7000 : 4200);
        });
      },
    }));

    // Inspection maquette : repères numérotés + tiroir
    Alpine.data('inspection', () => ({
      reperes: [], flux: {}, compteurs: {},
      async init() {
        const ref = await SI.referentiel();
        this.flux = ref.flux; this.acteurs = ref.acteurs;
        const maj = () => this.numeroter();
        window.addEventListener('si:inspection', maj);
        window.addEventListener('si:rendu', () => setTimeout(maj, 60));
        const zone = document.getElementById('contenu');
        if (zone && window.MutationObserver) {
          let tempo = null;
          new MutationObserver(() => { clearTimeout(tempo); tempo = setTimeout(maj, 250); }).observe(zone, { childList: true, subtree: true });
        }
        setTimeout(maj, 400);
        try { this.compteurs = await SI.get('/api/flux/stats'); } catch (e) { /* ignoré */ }
      },
      numeroter() {
        document.querySelectorAll('.insp-pastille').forEach((p) => p.remove());
        const liste = [];
        if (!Alpine.store('ui').inspection) { this.reperes = []; return; }
        document.querySelectorAll('#contenu [data-insp]').forEach((el) => {
          if (!el.offsetParent && el.tagName !== 'svg') return;
          const n = liste.length + 1;
          const p = document.createElement('span'); p.className = 'insp-pastille'; p.textContent = n;
          el.appendChild(p);
          liste.push({ n, titre: el.dataset.inspTitre || '', refs: (el.dataset.insp || '').split(/\s+/).filter(Boolean) });
        });
        this.reperes = liste;
      },
      libelleRef(r) {
        if (this.flux[r]) return r + ' · ' + this.flux[r].libelle;
        return r;
      },
      nomActeur(c) { return c === 'mkt' ? 'Apple (SI marketing)' : (this.acteurs && this.acteurs[c] ? this.acteurs[c].nom : c); },
    }));
  });

  // ------------------------------------------------------------------ capture de l'écran courant (PNG HD)
  SI.capturerEcran = async function () {
    if (!window.html2canvas) { SI.toast('Module de capture indisponible.', 'crit'); return; }
    SI.toast('Capture HD en cours…', 'info');
    const canvas = await html2canvas(document.body, { scale: 2, useCORS: true, backgroundColor: '#f5f5f7',
      windowWidth: document.documentElement.scrollWidth, ignoreElements: (el) => el.classList && (el.classList.contains('pas-capture')) });
    const a = document.createElement('a');
    a.download = (document.body.dataset.ecran || 'ecran') + '_' + (SI.acteur() || '') + '.png';
    a.href = canvas.toDataURL('image/png');
    a.click();
  };

  window.addEventListener('load', () => { window.SI_PRET_BASE = true; });
})();
