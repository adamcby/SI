"use strict";
/* SI marketing et ventes · iPhone Duo — prototype cliquable des maquettes M0 à M2.7 (données fictives, enregistrées dans le navigateur) */

const KEY = "si-iphone-duo-v2";
const JANV = "2027-01-25";
const OUT = "2026-10-16T14:28"; // stock de lancement épuisé
const T16 = "2026-10-16T14:35";
const T = (x) => (x.length === 5 ? "2026-10-16T" + x : x);
const esc = (s) => String(s == null ? "" : s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const nf = (n) => Math.round(n).toLocaleString("fr-FR");
const eur = (n) => nf(n) + " €";
const meur = (n) => (n / 1e6).toLocaleString("fr-FR", { maximumFractionDigits: 1, minimumFractionDigits: 1 }) + " M€";
const pct = (a, b) => (b ? Math.round((a / b) * 100) : 0) + " %";
const pct1 = (a, b) => (b ? ((a / b) * 100).toLocaleString("fr-FR", { maximumFractionDigits: 1, minimumFractionDigits: 1 }) : "0,0") + " %";
const dec1 = (x) => x.toLocaleString("fr-FR", { maximumFractionDigits: 1, minimumFractionDigits: 1 });
const D = (iso) => new Date(iso.slice(0, 10) + "T12:00:00");
const dLong = (iso) => D(iso).toLocaleDateString("fr-FR", { weekday: "long", day: "numeric", month: "long", year: "numeric" });
const dMed = (iso) => D(iso).toLocaleDateString("fr-FR", { day: "numeric", month: "long", year: "numeric" });
const dShort = (iso) => D(iso).toLocaleDateString("fr-FR", { day: "numeric", month: "short" });
const dShortY = (iso) => D(iso).toLocaleDateString("fr-FR", { day: "numeric", month: "short", year: "numeric" });
const cap1 = (s) => s.charAt(0).toUpperCase() + s.slice(1);
const hm = (iso) => iso.slice(11, 16);
const hmPhone = (iso) => hm(iso).replace(/^0/, "");
const ddmm = (iso) => iso.slice(8, 10) + "/" + iso.slice(5, 7);
const quand = (iso) => (iso.slice(0, 10) === now().slice(0, 10) ? hm(iso) : ddmm(iso) + " " + hm(iso));
const pill = (t, c) => `<span class='pill ${c}'>${t}</span>`;
const flow = (t) => `<span class='flow'>${t}</span>`;
function addMin(iso, m) { const d = new Date(iso + ":00Z"); d.setUTCMinutes(d.getUTCMinutes() + m); return d.toISOString().slice(0, 16); }
const clone = (x) => JSON.parse(JSON.stringify(x));

/* ---------- état ---------- */
let S;
function seed() {
  const s = { v: 2, last: {}, seq: 0, rseq: 413, bank: "ok", orders: {}, reviews: {}, signals: {}, costs: {}, notes: {}, offres: {}, reviewed: {}, deleted: {}, flog: [], distSent: 0 };
  SEED_ORDERS.forEach(([id, cli, cap, col, pay, bank, t0, hist, serial]) => {
    const h = hist.map(([t, st, x]) => ({ t: T(t), s: st, x: x || null }));
    s.orders[id] = { id, cli, cap, col, prix: prixDe(cap), pay, bank, created: T(t0), hist: h, h0: clone(h), serial: serial ? "••••••" + serial : null, u: false };
  });
  const rev = ([ref, cli, order, canal, t, note, motif, accord, txt, hist], b) => {
    const h = hist.map(([tt, st]) => ({ t: tt, s: st, x: null }));
    return { ref, cli, order, canal, t, note, motif, accord, txt, hist: h, h0: clone(h), b, script: !b };
  };
  const sig = ([id, r, defaut, lot, serial, cfg, diag, hist], b) => ({ id, rev: r, defaut, lot, serial, cfg, diag, t: hist[0][0], hist: hist.map(([tt, st, x]) => ({ t: tt, s: st, x: x || null })), b, script: !b });
  SEED_REVIEWS.forEach((r) => { s.reviews[r[0]] = rev(r, true); });
  SEED_SIGNALS.forEach((q) => { s.signals[q[0]] = sig(q, true); });
  const cost = (q, t, b) => { const c = q.hist.find((h) => h.s === "confirme"); return { id: q.id, t: c.t, action: c.x.action, cout: c.x.cout, hist: [{ t: c.t, s: "a_enregistrer", x: null }].concat(t ? [{ t, s: "enregistre", x: null }] : []), b, script: !b }; };
  SEED_COSTS.forEach(([q, t]) => { s.costs[q] = cost(s.signals[q], t, true); });
  // suite des maquettes M2.2 à M2.6 (réponse de Léa), remplacée dès qu'on agit soi-même
  s.reviews["R-0412"] = rev(SCRIPT_P2.review, false);
  s.signals["Q-0412"] = sig(SCRIPT_P2.signal, false);
  s.costs["Q-0412"] = cost(s.signals["Q-0412"], null, false);
  return s;
}
function load() { try { const x = JSON.parse(localStorage.getItem(KEY)); if (x && x.v === 2) return x; } catch (e) { /* stockage indisponible */ } return seed(); }
function save() { try { localStorage.setItem(KEY, JSON.stringify(S)); } catch (e) { /* stockage indisponible */ } }
S = load();

/* Heure : chaque écran s'ouvre au moment de sa maquette, puis suit les actions faites dans la démonstration */
let REF = T16;
const dayOf = (t) => t.slice(0, 10);
const effAt = (ref) => { const l = S.last[dayOf(ref)]; return l && l > ref ? l : ref; };
const now = () => effAt(REF);
function stamp(delay = 1) { const t = addMin(now(), delay); S.last[dayOf(t)] = t; return t; }
function withRef(ref, fn) { const old = REF; REF = ref; try { return fn(); } finally { REF = old; } }
function at(hist, t) { let r = null; hist.forEach((h) => { if (h.t <= t) r = h; }); return r; }
function step(obj, s, x, delay = 1) {
  const t0 = now();
  obj.hist = obj.hist.filter((h) => h.t <= t0);
  obj.script = false;
  const t = stamp(delay);
  obj.hist.push({ t, s, x: x || null });
  return t;
}
const offresDe = (cli) => (cli in S.offres ? S.offres[cli] : CLIENTS[cli] ? CLIENTS[cli].offres : false);

/* ---------- précommandes ---------- */
function oInfo(o, t = now(), hist = o.hist) {
  if (o.created > t) return null;
  const h = at(hist, t);
  let s = h ? h.s : "controle";
  const x = {};
  hist.forEach((e) => { if (e.t <= t && e.x) Object.assign(x, e.x); });
  if (s === "confirmee" && x.date === "2026-10-23" && t >= LIV) s = "livree";
  return Object.assign({ s }, x);
}
const tOf = (hist, s, t = now()) => { const h = hist.find((x) => x.s === s && x.t <= t); return h ? h.t : null; };
const visOrders = () => Object.values(S.orders).filter((o) => o.created <= now()).sort((a, b) => (a.created < b.created ? 1 : a.created > b.created ? -1 : a.id < b.id ? 1 : -1));
const aggKey = (t) => (t < "2026-10-17" ? (t < T16 ? "a" : "b") : "c");
function contrib(o, i) {
  const r = { controle: 0, conf: 0, janv: 0, annul: 0, ca: 0, res: 0, fab: 0, cfg: o.cap + "|" + o.col };
  if (!i) return r;
  if (i.s === "controle") r.controle = 1;
  if (["payee", "reservee", "confirmee", "livree"].includes(i.s)) r.ca = o.prix;
  if (["confirmee", "livree"].includes(i.s)) { r.conf = 1; if (i.date === JANV) r.janv = 1; }
  if (i.s === "annulee" || i.s === "refusee") r.annul = 1;
  if (["reservee", "confirmee", "livree"].includes(i.s)) { if (i.date === JANV) r.fab = 1; else r.res = 1; }
  return r;
}
function p1() {
  const t = now(); const a = Object.assign({}, AGG[aggKey(t)]); const resCfg = {};
  Object.values(S.orders).forEach((o) => {
    const cur = contrib(o, oInfo(o, t));
    const ref = o.u ? contrib(o, null) : contrib(o, oInfo(o, t, o.h0));
    if (o.u && o.created <= t) a.recues++;
    a.controle += cur.controle - ref.controle; a.confirmees += cur.conf - ref.conf; a.janvier += cur.janv - ref.janv;
    a.annulees += cur.annul - ref.annul; a.ca += cur.ca - ref.ca; a.stockRes += cur.res - ref.res; a.fab += cur.fab - ref.fab;
    resCfg[cur.cfg] = (resCfg[cur.cfg] || 0) + cur.res - ref.res;
  });
  a.resCfg = resCfg;
  return a;
}
const stockOut = () => now() >= OUT;
function stockTable() {
  const a = p1(); const out = stockOut();
  return Object.keys(STOCK).map((k) => {
    const res = out ? STOCK[k] : Math.min(STOCK[k], RES_T1[k] + (a.resCfg[k] || 0));
    return { k, total: STOCK[k], res, dispo: STOCK[k] - res };
  });
}
const dispoCfg = (cap, col) => !stockOut() && stockTable().find((r) => r.k === cap + "|" + col).dispo > 0;
function oPill(i) {
  switch (i.s) {
    case "controle": return pill("En contrôle", "wait");
    case "payee": return pill("Paiement accepté", "info");
    case "refusee": return pill("Paiement refusé", "ko");
    case "reservee": return pill("Réservé · à confirmer", "info");
    case "confirmee": return i.date === JANV ? pill("Confirmée · 25 janv.", "info") : pill("Confirmée · 23 oct.", "ok");
    case "annulee": return pill("Annulée · refus", "ko");
    case "livree": return pill("Livrée le 23 oct.", "ok");
  }
  return "";
}
const orderCfg = (id) => (S.orders[id] ? [S.orders[id].cap, S.orders[id].col] : ORDER_REF[id] || null);

/* ---------- avis, signalements, coûts ---------- */
const rInfo = (r, t = now()) => (r.t > t || S.deleted[r.ref] ? null : at(r.hist, t));
const visReviews = () => Object.values(S.reviews).filter((r) => rInfo(r)).sort((a, b) => (a.t < b.t ? 1 : -1));
const visSignals = () => Object.values(S.signals).filter((q) => q.t <= now()).sort((a, b) => (a.t < b.t ? 1 : -1));
const RLAB = {
  defaut: ["Défaut signalé", "ko"], a_recontacter: ["À recontacter", "wait"], remercie: ["Remercié", "ok"], statistique: ["Statistique", "grey"],
  en_analyse: ["En analyse (production)", "info"], a_informer: ["Suite à donner", "wait"], recontacte: ["Recontacté", "ok"], clos: ["Client informé", "ok"],
};
const rPill = (s) => pill(RLAB[s][0], RLAB[s][1]);
const qPill = (s) => ({ analyse: pill("À analyser", "wait"), confirme: pill("Défaut confirmé", "ko"), non_confirme: pill("Non confirmé", "grey") }[s]);
const cPill = (s) => ({ a_enregistrer: pill("À enregistrer", "wait"), enregistre: pill("Enregistré", "ok") }[s]);
const cliMail = (cli) => (cli && CLIENTS[cli] ? CLIENTS[cli].mail : "Réponse anonyme");
const cliNom = (cli) => (cli && CLIENTS[cli] ? CLIENTS[cli].nom : "Réponse anonyme");
const isCharn = (m) => /charni/i.test(m);
function proposition(q) {
  if (isCharn(q.defaut)) return ["Échange de l'appareil", 612, `Échange de l'appareil · contrôle renforcé du lot ${q.lot}`];
  return ["Remplacement de l'écran intérieur", 431, "Remplacement de l'écran intérieur"];
}

function sat(t = now()) {
  const s = clone(SAT);
  let sum = SAT.moy * SAT.rep, sumJ = SAT.jour.moy * SAT.jour.rep; s.extra = 0;
  Object.values(S.reviews).forEach((r) => {
    const i = rInfo(r, t);
    if (r.b) { // réponses de départ : seul le passage « à recontacter » peut changer
      const i0 = r.t <= t ? at(r.h0, t) : null;
      if (i0 && i0.s === "a_recontacter" && (!i || i.s !== "a_recontacter")) s.jour.recontacter--;
      return;
    }
    if (!i) return;
    s.extra++; s.rep++; sum += r.note; s.jour.rep++; sumJ += r.note;
    if (!r.accord) s.jour.anonymes++;
    if (r.note >= 7) s.satis++; else { s.motifs[r.motif]++; s.jour.insatisfaits++; }
    if (i.s === "a_recontacter") s.jour.recontacter++;
  });
  Object.values(S.signals).forEach((q) => { if (!q.b && q.t <= t) { s.defauts++; s.jour.transmis++; } });
  Object.values(S.costs).forEach((c) => { if (c.b) return; const i = at(c.hist, t); if (i && i.s === "enregistre") { s.couts += c.cout; s.confirmes++; } });
  s.moy = sum / s.rep; s.jour.moy = sumJ / s.jour.rep;
  return s;
}
function lotStats(t = now()) {
  return LOTS_BASE.map(([lot, sem, n, sig0, conf0]) => {
    let sg = sig0, cf = conf0;
    Object.values(S.signals).forEach((q) => {
      if (q.lot !== lot || q.t > t) return;
      const i = at(q.hist, t);
      if (!q.b) { sg++; if (i && i.s === "confirme") cf++; } else if (q.userConf && i && i.s === "confirme") cf++;
    });
    return { lot, sem, n, sg, cf };
  });
}

/* travail en attente pour chaque écran (badges du menu), calculé au moment de l'écran */
const BADGE = {
  "marketing/precommandes": [T16, () => visOrders().filter((o) => ["reservee", "refusee"].includes(oInfo(o).s)).length],
  "marketing/avis": ["2026-11-09T09:43", () => visReviews().filter((r) => ["defaut", "a_recontacter", "a_informer"].includes(rInfo(r).s)).length],
  "finance/paiements": [T16, () => visOrders().filter((o) => oInfo(o).s === "controle").length],
  "finance/garantie": ["2026-11-09T10:30", () => Object.values(S.costs).filter((c) => c.t <= now() && at(c.hist, now()).s === "a_enregistrer").length],
  "production/stock": [T16, () => visOrders().filter((o) => oInfo(o).s === "payee").length],
  "production/qualite": ["2026-11-09T09:58", () => visSignals().filter((q) => at(q.hist, now()).s === "analyse").length],
};
const badge = (k) => (BADGE[k] ? withRef(BADGE[k][0], BADGE[k][1]) : 0);

/* ---------- interface ---------- */
let ui = { cfg: { cap: "512 Go", col: "Ciel nocturne", pay: "Carte bancaire" }, sel: {}, q: null, dossier: false, crOpen: false, cr: "", note: "", erp: false, jf: "tous", actor: null };
const Q0 = () => ({ note: 4, motif: "Charnière", txt: "Un léger jeu dans la charnière depuis quelques jours.", accord: true });
ui.q = Q0();
const $app = () => document.getElementById("app");
let lastRoute = null;
function toast(t) {
  let el = document.querySelector(".toast"); if (!el) { el = document.createElement("div"); el.className = "toast"; document.body.appendChild(el); }
  el.textContent = t; el.classList.add("on"); clearTimeout(toast.h); toast.h = setTimeout(() => el.classList.remove("on"), 3200);
}
const head = (code, crumb, tags, title, sub) => `<div class='crumb'>${code ? code + " · " : ""}${crumb}${tags.length ? " " + tags.map((t) => `<span class='tag'>${t}</span>`).join("") : ""}</div><h1>${title}</h1><div class='sub'>${sub}</div>`;
const kpis = (arr, n) => `<div class='kpis' style='grid-template-columns:repeat(${n || arr.length},1fr)'>${arr.map(([a, b, c]) => `<div class='kpi'><span>${a}</span><b>${b}</b><i>${c}</i></div>`).join("")}</div>`;

const SCR = {
  client: {
    precommander: ["Configurer et précommander", "2026-10-16T14:02", () => vPrecommander()],
    precommandes: ["Messages reçus", T16, () => vMesPrecommandes()],
    avis: ["Donner mon avis", "2026-11-09T09:41", () => vAvisClient()],
    donnees: ["Mes données", "2026-11-09T09:41", () => vDonnees()],
  },
  marketing: {
    precommandes: ["Précommandes reçues", T16, () => sPrecommandes()],
    avis: ["Avis reçus (QR code)", "2026-11-09T09:43", () => sAvis()],
    suivi: ["Dossiers de suivi", "2026-11-09T09:43", () => sSuivi()],
    clients: ["Fiches clients", "2026-11-09T09:43", () => sClients()],
    lancement: ["Tableau de bord des précommandes", T16, () => sLancement()],
    satisfaction: ["Tableau de bord de satisfaction", "2026-11-09T09:41", () => sSatisfaction()],
    plan: ["Plan de lancement", "2026-11-09T09:41", () => sCampagnes()],
    distributeurs: ["Distributeurs", "2026-11-09T09:41", () => sDistributeurs()],
  },
  finance: {
    paiements: ["Contrôle des paiements", T16, () => sPaiements()],
    garantie: ["Coûts de garantie", "2026-11-09T10:30", () => sGarantie()],
    budgets: ["Budgets et prix", T16, () => sBudgets()],
    satisfaction: ["Tableau de bord de satisfaction", "2026-11-09T09:41", () => sSatisfaction()],
  },
  production: {
    stock: ["Stock et réservations", T16, () => sStock()],
    qualite: ["Signalements qualité", "2026-11-09T09:58", () => sQualite()],
    fabrication: ["Plan de production", T16, () => sFabrication()],
    satisfaction: ["Tableau de bord de satisfaction", "2026-11-09T09:41", () => sSatisfaction()],
  },
};
const VUE = { flux: ["Cartographie des flux", "2026-11-09T10:30"], p1: ["Processus P1 (BPMN)", T16], p2: ["Processus P2 (BPMN)", "2026-11-09T10:30"] };

function side(actor, cur, extra) {
  const A = actor && ACTEURS[actor] ? ACTEURS[actor] : actor && PARTENAIRES[actor] ? { nom: PARTENAIRES[actor].nom, role: PARTENAIRES[actor].role, ecrans: [] } : { nom: "Vue d'ensemble", role: "Tous les acteurs", ecrans: [] };
  const mine = actor && ACTEURS[actor] ? A.ecrans.map((k) => { const b = badge(actor + "/" + k); return `<li class='${cur === actor + "/" + k ? "on" : ""}'><a href='#/${actor}/${k}'><span>${SCR[actor][k][0]}</span>${b ? `<span class='badge'>${b}</span>` : ""}</a></li>`; }).join("")
    : actor && PARTENAIRES[actor] ? `<li class='on'><a href='#/partenaire/${actor}'><span>${PARTENAIRES[actor].ecran}</span></a></li>` : "";
  const vue = [["", "Accueil"], ["vue/flux", "Cartographie des flux"], ["vue/p1", "Processus P1 (BPMN)"], ["vue/p2", "Processus P2 (BPMN)"]]
    .map(([h, t]) => `<li class='${cur === (h || "home") ? "on" : ""}'><a href='#/${h}'><span>${t}</span></a></li>`).join("");
  return `<aside class='side'><div class='grow'><a class='brand' href='#/' style='display:block'>SI Marketing · iPhone Duo<small>Prototype · données fictives</small></a>
  <div class='actor'><span>Vue acteur</span><b>${A.nom}</b><span>${A.role}</span>${actor ? `<br><a href='#/'>Changer de vue</a>` : ""}</div>
  <ul class='menu'>${mine ? `<li class='sep'>Mes écrans</li>${mine}` : ""}<li class='sep'>Vue d'ensemble du SI</li>${vue}</ul></div>
  <div class='sidefoot'>${extra || ""}<a href='#/projet'>Le projet</a> · <a data-act='reset'>Recommencer la démonstration</a></div></aside>`;
}
function shell(actor, cur, inner, extra) { return `<div class='app'>${side(actor, cur, extra)}<main class='main'>${inner}</main></div>`; }

/* ---------- M0 · accueil ---------- */
function vHome() {
  const path = (title, sub, steps, screens, start, bpmn) => `<div class='card'><h2>${title}</h2><div class='sub' style='margin:0 0 10px'>${sub}</div><div class='steps'>${steps.map((x) => `<div class='done'>${x}</div>`).join("")}</div>${screens.map(([a, b, c, h]) => `<a class='scr' href='#/${h}'><b>${a}</b><span>${b}</span><i>${c}</i></a>`).join("")}<div style='margin-top:12px'><a class='btn pri' href='#/${start}'>Suivre ce parcours</a><a class='btn' href='#/${bpmn}'>Voir le processus (BPMN)</a></div></div>`;
  const p1 = path("Parcours 1 · De la précommande à sa confirmation", "Le client précommande ; le marketing enregistre, la finance contrôle le paiement, la production réserve un appareil ; le client reçoit sa date de livraison.",
    ["Client", "Marketing et ventes", "Finance", "Production", "Client"],
    [["M1.1", "Configurer et précommander", "Client", "client/precommander"], ["M1.2", "CRM : précommandes reçues", "Marketing et ventes", "marketing/precommandes"], ["M1.3", "Contrôle des paiements", "Finance", "finance/paiements"], ["M1.4", "Stock et réservations", "Production", "production/stock"], ["M1.5", "Confirmation ou refus", "Client", "client/precommandes"]], "client/precommander", "vue/p1");
  const p2 = path("Parcours 2 · Mesure de la satisfaction par QR code", "Le client répond au questionnaire ; la réponse arrive dans le CRM ; un défaut signalé part à la production, son coût à la finance ; le tableau de bord est mis à jour.",
    ["Client", "Marketing et ventes", "Production", "Finance", "Tableau de bord"],
    [["M2.1", "QR code, questionnaire, confirmation (M2.1 à M2.3)", "Client", "client/avis"], ["M2.4", "CRM : avis reçus", "Marketing et ventes", "marketing/avis"], ["M2.5", "Signalements qualité", "Production", "production/qualite"], ["M2.6", "Coûts de garantie", "Finance", "finance/garantie"], ["M2.7", "Tableau de bord de satisfaction", "Direction marketing", "marketing/satisfaction"]], "client/avis", "vue/p2");
  const views = [["client", "Client", "Acteur externe · précommande, questionnaire"], ["marketing", "Marketing et ventes", "Fonction principale · CRM, tableaux de bord"], ["finance", "Finance", "Fonction complémentaire · paiements, coûts"], ["production", "Production", "Fonction complémentaire · stocks, qualité"]]
    .map(([k, a, b]) => `<a class='view' href='#/${k}/${ACTEURS[k].ecrans[0]}'><b>${a}</b><div>${b}</div></a>`).join("");
  return shell(null, "home", `<div class='crumb'>M0 · Accueil du prototype</div>
  <h1>SI marketing et ventes : lancement de l'iPhone Duo</h1>
  <div class='sub'>Maquettes du SI. Elles montrent les principaux écrans du SI et le parcours de chaque utilisateur. Données fictives ; projet universitaire non affilié à Apple.</div>
  <div class='cols' style='grid-template-columns:1fr 1fr'>${p1}${p2}</div>
  <div class='card'><h2>Choisir une vue acteur <small>chaque acteur ne voit que ses écrans (profil d'autorisations)</small></h2><div class='views'>${views}</div></div>`);
}

/* ---------- client ---------- */
function bankBox() {
  return `<div class='lab'>Démonstration</div>Réponse de la banque :<br><select data-act='bank'><option value='ok' ${S.bank === "ok" ? "selected" : ""}>paiement accordé</option><option value='ko' ${S.bank === "ko" ? "selected" : ""}>paiement refusé</option></select><br><br>`;
}
function vPrecommander() {
  const c = ui.cfg; const dispo = dispoCfg(c.cap, c.col); const date = dispo ? "2026-10-23" : JANV; const off = offresDe("lea");
  const tile = (k, v, sub) => `<div class='tile ${c[k] === v ? "on" : ""}' data-act='cfg' data-k='${k}' data-v='${esc(v)}'><b>${v}</b><div>${sub}</div></div>`;
  const livr = (col) => (dispoCfg(c.cap, col) ? "Livraison le 23 octobre" : "Livraison le 25 janvier 2027");
  return shell("client", "client/precommander", head("M1.1", "Client (boutique en ligne)", ["P1 · Message « précommande validée »"], "Précommander l'iPhone Duo",
    `${cap1(dLong(now()))}, ${hm(now())}. Le client choisit sa configuration, s'identifie et paie. La validation envoie la précommande au SI marketing et ventes.`) +
  `<div class='cols'><div class='card'>
  <div class='lab2'>1. Capacité</div><div class='tiles'>${CAPS.map((x) => tile("cap", x.cap, eur(x.prix))).join("")}</div>
  <div class='lab2'>2. Couleur</div><div class='tiles'>${COLS.map((x) => tile("col", x.col, livr(x.col))).join("")}</div>
  <div class='lab2'>3. Paiement</div><div class='tiles'>${tile("pay", "Carte bancaire", "Débit à l'expédition")}${tile("pay", "Financement", "Sous réserve d'acceptation")}</div>
  <div class='lab2'>4. Compte client</div>
  <div class='kv' style='margin-top:8px'><span>Identifiant</span><b>l••.m•••••@icloud.com</b><span>Adresse de livraison</span><b>Lyon 3e (masquée)</b></div>
  <div class='chk' data-act='offres'><div class='box ${off ? "" : "off"}'>${off ? "✓" : ""}</div><div>J'accepte de recevoir des offres personnalisées (facultatif).</div></div>
  </div>
  <div class='card'><h2>Récapitulatif</h2>
  <div class='kv'><span>Produit</span><b>iPhone Duo ${c.cap}, ${c.col}</b><span>Prix TTC</span><b>${eur(prixDe(c.cap))}</b><span>Paiement</span><b>${c.pay}</b><span>Livraison estimée</span><b>${dLong(date)}</b></div>
  <div class='quote' style='margin:12px 0'>${dispo ? "La date affichée vient du stock disponible dans l'ERP. Elle est recalculée si le stock de lancement est épuisé." : "Le stock de lancement est épuisé : la date affichée a été recalculée à partir du plan de production lu dans l'ERP."}</div>
  <button class='btn pri' data-act='order'>Valider la précommande</button>
  <div class='note'>Données transmises : configuration, compte client, moyen de paiement.${flow("Précommande validée → Marketing et ventes")}</div></div></div>`, bankBox());
}
function phone(o) {
  const P = (hour, url, lab, icon, title, ref, ctx, kv, legal, min) => `<div class='pw'><div class='phone' style='min-height:${min || 640}px'>
  <div class='pbar'><span>${hour}</span><span>5G ▮▮▮</span></div><div class='url'>${url}</div>
  <div class='pbody'><div class='lab2'>${lab}</div><div class='big'>${icon}</div><h1 class='center'>${title}</h1>
  <p class='center' style='color:#6e6e73;margin-top:8px;font-size:13px'>${ref}</p>
  <div class='ctx' style='margin-top:22px'>${ctx}</div>
  <div class='card' style='border-radius:12px'><div class='kv' style='grid-template-columns:120px 1fr'>${kv}</div></div>
  <div class='legal'>${legal}</div></div></div></div>`;
  const i = oInfo(o); const ref = `Commande ${o.id} · ${dMed(o.created)}`;
  const kv = (paie) => `<span>Produit</span><b>iPhone Duo ${o.cap}, ${o.col}</b><span>Montant</span><b>${eur(o.prix)}</b><span>Paiement</span><b>${paie}</b>`;
  const url = "example.com/boutique/commande";
  if (i.s === "confirmee" || i.s === "livree") {
    const t = tOf(o.hist, "confirmee");
    return i.date === JANV
      ? P(hm(t), url, "Message au client", "✓", "Votre précommande est confirmée", ref, `<b>Livraison le ${dLong(JANV)}</b><br>Le stock de lancement est épuisé. Votre appareil est réservé sur la fabrication à venir.`, kv("Accepté"), "Vous serez prévenu(e) si la date de livraison change.")
      : P(hm(t), url, "Message au client", "✓", "Votre précommande est confirmée", ref, `<b>Livraison le ${dLong("2026-10-23")}</b><br>Un appareil du stock de lancement vous est réservé.`, kv("Accepté"), "Vous pouvez suivre ou annuler votre commande depuis votre compte.");
  }
  if (i.s === "annulee") return P(hm(tOf(o.hist, "annulee")), url, "Message au client", "✕", "Votre paiement n'a pas été accepté", ref, "<b>Votre précommande est annulée</b><br>Vous pouvez recommencer avec un autre moyen de paiement.", kv(o.pay === "Financement" ? "Refusé par l'organisme de crédit" : "Refusé par la banque"), "Aucun montant n'a été débité.");
  return P(hm(o.created), url, "Message au client", "…", "Votre précommande est enregistrée", ref, "<b>Paiement en cours de vérification</b><br>Vous recevrez la confirmation et la date de livraison dès que votre appareil sera réservé.", kv("En cours de vérification"), "Vous pouvez suivre ou annuler votre commande depuis votre compte.");
}
function vMesPrecommandes() {
  const vis = visOrders();
  const kind = (o) => { const i = oInfo(o); if (i.s === "annulee") return "ko"; if (["confirmee", "livree"].includes(i.s)) return i.date === JANV ? "j25" : "j23"; return "att"; };
  const msgT = (o) => tOf(o.hist, kind(o) === "ko" ? "annulee" : "confirmee") || o.created;
  const lea = vis.filter((o) => o.cli === "lea");
  const have = new Set(lea.map(kind));
  // les trois cas de message (confirmée, servie en janvier, refusée) restent visibles avec d'autres clients
  const others = ["j23", "j25", "ko"].filter((k) => !have.has(k)).map((k) => vis.filter((o) => o.cli !== "lea" && kind(o) === k).sort((x, y) => (msgT(x) < msgT(y) ? 1 : -1))[0]).filter(Boolean);
  const all = lea.concat(others);
  const by = []; all.forEach((o) => { const g = by.find((x) => x[0] === o.cli); if (g) g[1].push(o.id); else by.push([o.cli, [o.id]]); });
  const names = by.map(([c, ids]) => `${CLIENTS[c].nom} (${ids.join(", ")})`);
  const list = names.length > 1 ? names.slice(0, -1).join(", ") + " et " + names[names.length - 1] : names[0];
  return shell("client", "client/precommandes", `<div class='strip ${all.length >= 3 ? "three" : ""}'>${all.map(phone).join("")}</div><div class='note' style='margin-top:4px'>Messages reçus par ${list}.</div>`);
}
function suiviLab(s) { return { defaut: "Dossier ouvert", a_recontacter: "Dossier ouvert", en_analyse: "Analyse en cours", a_informer: "Solution en préparation", clos: "Solution proposée", recontacte: "Conseiller en contact", remercie: "Aucun", statistique: "Réponse anonyme" }[s]; }
function clientSuite(r) {
  if (!r.accord) return "Votre réponse anonyme est prise en compte dans nos statistiques.";
  if (r.note >= 7) return "Merci ! Votre note nous aide à améliorer l'iPhone Duo.";
  if (DEFAUTS.includes(r.motif)) return `Vous signalez un problème ${isCharn(r.motif) ? "de charnière" : "d'écran"}. Un conseiller vous recontacte sous 48 heures, par téléphone ou par courriel.`;
  return "Un conseiller vous recontacte sous 48 heures, par téléphone ou par courriel.";
}
function vAvisClient(oid) {
  const o = S.orders[oid] || S.orders.W150032;
  const qr = `<div class='pw qrw'><div class='qrcard'><div class='lab2'>iPhone Duo · votre avis compte</div><h1 style='margin-top:6px'>Dites-nous ce que vous en pensez</h1><img src='img/qr-avis.svg' alt='QR code du questionnaire'><div style='font-size:13px;color:#424245'>Scannez ce code avec l'appareil photo.<br>Deux minutes, trois questions.</div><div class='legal'>Carte posée sur les tables de démonstration, glissée dans le coffret et reprise dans le courriel envoyé 15 jours après la livraison.</div></div></div>`;
  const last = S.reviewed[o.id] && S.reviews[S.reviewed[o.id]];
  const r = last && !last.script && rInfo(last) ? last : Object.values(S.reviews).find((x) => x.order === o.id && !x.script && rInfo(x));
  const i = oInfo(o);
  let ph;
  if (r && ui.dossier) ph = questPhone(o, r) + dossierPhone(r, o);
  else if (r) ph = questPhone(o, r) + merciPhone(r);
  else if (!i || i.s !== "livree") ph = `<div class='pw'><div class='phone'><div class='pbar'><span>${hmPhone(now())}</span><span>5G ▮▮▮</span></div><div class='url'>example.com/avis-iphone-duo</div><div class='pbody'><h1>Votre avis sur l'iPhone Duo</h1><div class='ctx'>Le questionnaire s'ouvre après la livraison de votre commande.</div></div></div></div>`;
  else ph = questPhone(o);
  return shell("client", "client/avis", `<div class='strip ${r ? "three" : ""}'>${qr}${ph}</div>`);
}
function questPhone(o, sent) {
  const q = sent ? { note: sent.note, motif: sent.motif, txt: sent.txt, accord: sent.accord } : ui.q;
  const act = (x) => (sent ? "" : ` data-act='${x}'`);
  return `<div class='pw'><div class='phone'><div class='pbar'><span>${hmPhone(sent ? addMin(sent.t, -2) : now())}</span><span>5G ▮▮▮</span></div><div class='url'>example.com/avis-iphone-duo</div><div class='pbody'>
  <div class='lab2'>Étape 1 sur 2</div><h1>Votre avis sur l'iPhone Duo</h1>
  <div class='ctx'><b>Commande ${o.id}</b> · iPhone Duo ${o.cap}, ${o.col}<br>Livré le ${dMed(LIV)}</div>
  <div class='q'>1. Quelle note donnez-vous à votre iPhone Duo ?<small>0 = pas du tout satisfait · 10 = très satisfait</small></div>
  <div class='scale'>${Array.from({ length: 11 }, (_, k) => `<div class='${q.note === k ? "on" : ""}'${act("qnote")} data-v='${k}'>${k}</div>`).join("")}</div>
  <div class='q'>2. Qu'est-ce qui explique le plus cette note ?</div>
  <div class='chips'>${MOTIFS.map((m) => `<div class='${q.motif === m ? "on" : ""}'${act("qmotif")} data-v='${esc(m)}'>${m}</div>`).join("")}</div>
  <div class='q'>3. Souhaitez-vous préciser ?</div>
  <textarea class='ta' rows='2'${act("qtxt")} maxlength='500' ${sent ? "readonly" : ""}>${esc(q.txt)}</textarea>
  <div class='chk'${act("qaccord")}><div class='box ${q.accord ? "" : "off"}'>${q.accord ? "✓" : ""}</div><div>J'accepte d'être recontacté(e) par Apple au sujet de cet avis.</div></div>
  <button class='send'${act("sendavis")} data-id='${o.id}' ${!sent && (q.note === null || !q.motif) ? "disabled" : ""}${sent ? " tabindex='-1' style='cursor:default'" : ""}>Envoyer mon avis</button>
  <div class='legal'>Si vous acceptez d'être recontacté(e), votre réponse est rattachée à votre commande et vous pouvez la consulter ou la supprimer depuis votre compte ; sinon, elle est enregistrée de façon anonyme et sert seulement aux statistiques. <u>En savoir plus sur vos données</u></div>
  </div></div></div>`;
}
function merciPhone(r) {
  const i = rInfo(r);
  return `<div class='pw'><div class='phone'><div class='pbar'><span>${hmPhone(r.t)}</span><span>5G ▮▮▮</span></div><div class='url'>example.com/avis-iphone-duo/merci</div><div class='pbody'>
  <div class='lab2'>Étape 2 sur 2</div><div class='big'>✓</div><h1 class='center'>Merci, votre avis est enregistré</h1>
  <p class='center' style='color:#6e6e73;margin-top:8px;font-size:13px'>Référence ${r.ref} · ${dMed(r.t)}</p>
  <div class='ctx' style='margin-top:22px'><b>Et maintenant ?</b><br>${clientSuite(r)}</div>
  <div class='card' style='border-radius:12px'><div class='kv' style='grid-template-columns:120px 1fr'><span>Votre note</span><b>${r.note} / 10</b><span>Motif</span><b>${esc(r.motif)}</b><span>Suivi</span><b>${suiviLab(i.s)}</b></div></div>
  ${r.accord ? `<button class='send out' data-act='dossier'>Suivre mon dossier</button>` : ""}
  <div class='legal'>Vous pouvez retirer votre accord pour être recontacté(e), modifier ou supprimer votre réponse à tout moment depuis votre compte.</div>
  </div></div></div>`;
}
function dossierPhone(r, o) {
  const i = rInfo(r); const q = Object.values(S.signals).find((x) => x.rev === r.ref);
  const xq = {}; if (q) q.hist.forEach((h) => { if (h.t <= now() && h.x) Object.assign(xq, h.x); });
  const lab = { defaut: "Avis reçu : problème signalé", a_recontacter: "Avis reçu : un conseiller va vous recontacter", en_analyse: "Signalement transmis au service qualité", a_informer: "Analyse terminée", recontacte: "Un conseiller vous a recontacté(e)", remercie: "Merci pour votre avis", clos: xq.action ? `Solution proposée : ${xq.action.toLowerCase()}, prise en charge par la garantie` : "Aucun défaut constaté : contrôle gratuit proposé en magasin" };
  const hist = r.hist.filter((h) => h.t <= now()).map((h) => `<div style='display:flex;gap:10px;padding:7px 0;border-bottom:1px solid #f0f0f3;font-size:12px'><span style='color:#86868b;width:92px;flex-shrink:0'>${dShort(h.t)} · ${hm(h.t)}</span><span>${lab[h.s] || ""}</span></div>`).join("");
  return `<div class='pw'><div class='phone'><div class='pbar'><span>${hmPhone(now())}</span><span>5G ▮▮▮</span></div><div class='url'>example.com/avis-iphone-duo/dossier</div><div class='pbody'>
  <div class='lab2'>Votre dossier</div><h1>Dossier ${r.ref}</h1>
  <div class='ctx'><b>Commande ${o.id}</b> · iPhone Duo ${o.cap}, ${o.col}<br>Suivi : ${suiviLab(i.s).toLowerCase()}</div>
  ${hist}
  <button class='send out' data-act='retour'>Retour</button>
  <div class='legal'><a class='lnk' data-act='retirer' data-id='${r.ref}'>Retirer mon accord</a> · <a class='lnk' data-act='supprimer' data-id='${r.ref}'>Supprimer ma réponse</a></div>
  </div></div></div>`;
}
function vDonnees() {
  const rs = visReviews().filter((r) => r.cli === "lea" && !r.script);
  return shell("client", "client/donnees", head("", "Client (compte)", [], "Mes données", "Ce qu'Apple conserve sur vous pour l'iPhone Duo, et les accords que vous pouvez modifier à tout moment.") +
  `<div class='cols'><div class='card'><h2>Compte</h2><div class='kv'><span>Identifiant</span><b>l••.m•••••@icloud.com</b><span>Adresse de livraison</span><b>Lyon 3e (masquée)</b><span>Précommandes</span><b>${Object.values(S.orders).filter((o) => o.cli === "lea").map((o) => o.id).join(", ")}</b></div>
  <div class='chk' data-act='offres'><div class='box ${offresDe("lea") ? "" : "off"}'>${offresDe("lea") ? "✓" : ""}</div><div>J'accepte de recevoir des offres personnalisées (facultatif).</div></div></div>
  <div class='card'><h2>Mes avis <small>rattachés à mon compte</small></h2>${rs.length ? `<table><tr><th>Réponse</th><th>Note</th><th>Motif</th><th></th></tr>${rs.map((r) => `<tr><td><b>${r.ref}</b></td><td>${r.note}/10</td><td>${esc(r.motif)}</td><td><a class='lnk' data-act='retirer' data-id='${r.ref}'>Retirer l'accord</a> · <a class='lnk' data-act='supprimer' data-id='${r.ref}'>Supprimer</a></td></tr>`).join("")}</table>` : `<div class='empty'>Aucun avis rattaché à votre compte.</div>`}
  <div class='note'>Sans accord, une réponse devient anonyme et ne sert plus qu'aux statistiques.</div></div></div>`);
}

/* ---------- M1.2 · CRM, précommandes reçues ---------- */
function oSteps(o, i) {
  const st = (l, c) => `<div class='${c}'>${l}</div>`;
  if (["refusee", "annulee"].includes(i.s)) return `<div class='steps' style='margin-top:12px'>${st("Enregistrée", "done")}${st("Paiement refusé", "bad")}${st("Client informé", i.s === "annulee" ? "done" : "cur")}</div>`;
  const k = { controle: 1, payee: 2, reservee: 3, confirmee: 4, livree: 4 }[i.s];
  return `<div class='steps' style='margin-top:12px'>${["Enregistrée", "Paiement accepté", "Appareil réservé", "Confirmée"].map((l, j) => st(l, j < k ? "done" : j === k ? "cur" : "")).join("")}</div>`;
}
function sPrecommandes() {
  const a = p1(); const os = visOrders(); const out = stockOut();
  const pick = (id) => (id && S.orders[id] && oInfo(S.orders[id]) ? S.orders[id] : null);
  const o = pick(ui.sel.o) || pick("W150032") || os[0];
  const rows = os.map((x) => `<tr class='click ${x === o ? "sel" : ""}' data-act='selo' data-id='${x.id}'><td>${hm(x.created)}</td><td><b>${x.id}</b></td><td>${cliMail(x.cli)}</td><td>${x.cap}, ${x.col}</td><td>${eur(x.prix)}</td><td>${oPill(oInfo(x))}</td></tr>`).join("");
  let det = "";
  if (o) {
    const i = oInfo(o); const c = CLIENTS[o.cli];
    const tC = tOf(o.hist, "confirmee"), tA = tOf(o.hist, "annulee");
    const quote = {
      controle: "Précommande transmise à la finance pour le contrôle du paiement.",
      payee: "Paiement accepté par la finance. La production vérifie le stock et réserve un appareil.",
      reservee: `Appareil réservé (${i.lot || ""}). Livraison possible le ${dLong(i.date || "2026-10-23")}.`,
      refusee: "La finance a refusé le paiement : le client doit être informé.",
      confirmee: `Message envoyé au client à ${tC ? hm(tC) : ""} : précommande confirmée, livraison le ${dLong(i.date || "2026-10-23")}.`,
      livree: `Message envoyé au client à ${tC ? hm(tC) : ""} : précommande confirmée. Appareil livré le ${dLong("2026-10-23")}.`,
      annulee: `Message envoyé au client à ${tA ? hm(tA) : ""} : paiement refusé, précommande annulée.`,
    }[i.s];
    const btn = i.s === "reservee" ? `<div style='margin-bottom:4px'><button class='btn pri' data-act='confirmer' data-id='${o.id}'>Confirmer la commande au client</button></div>`
      : i.s === "refusee" ? `<div style='margin-bottom:4px'><button class='btn pri' data-act='informerrefus' data-id='${o.id}'>Informer le client du refus</button></div>` : "";
    det = `<div class='card'><h2>Précommande ${o.id} <small>fiche client créée le ${dShortY(o.created)}</small></h2>
    <div class='kv'><span>Client</span><b>${c.nom} · compte vérifié</b><span>Configuration</span><b>iPhone Duo ${o.cap}, ${o.col}</b><span>Montant TTC</span><b>${eur(o.prix)} · ${o.pay.toLowerCase()}</b><span>Canal</span><b>Boutique en ligne</b><span>Offres personnalisées</span><b>${offresDe(o.cli) ? "Acceptées (case cochée)" : "Refusées (case non cochée)"}</b></div>
    ${oSteps(o, i)}<div class='quote'>${quote}</div>${btn ? `<div style='margin-top:12px'>${btn}</div>` : ""}
    <div class='note'>Flux échangés avec les fonctions complémentaires.${flow("Commandes à encaisser → Finance")}${flow("Précommandes → Production")}</div></div>`;
  }
  return shell("marketing", "marketing/precommandes", head("M1.2", "Marketing et ventes (CRM)", ["P1 · Enregistrer la précommande", "P1 · Confirmer la commande", "P1 · Informer du refus"], "CRM : précommandes reçues",
    `France · ${dLong(now())}, ${hm(now())}. Chaque précommande validée crée ou complète une fiche client. Son statut suit l'avancement du processus.`) +
    kpis([["Précommandes reçues depuis 14 h", nf(a.recues), "France"], ["En contrôle", nf(a.controle), "transmises à la finance"], ["Confirmées", nf(a.confirmees), a.janvier ? `dont ${nf(a.janvier)} livrées en janvier` : "livraison le 23 octobre"],
      ["Annulées (paiement refusé)", nf(a.annulees), pct1(a.annulees, a.recues) + " des précommandes"], ["Date de livraison annoncée", out ? "25 janv." : "23 oct.", out ? "depuis 14:28" : "stock de lancement"]], 5) +
    `<div class='cols'><div class='card'><h2>Dernières précommandes <small>identifiants masqués à l'affichage</small></h2>
    <div class='tw'><table><tr><th>Heure</th><th>N°</th><th>Client</th><th>Configuration</th><th>Montant</th><th>Statut</th></tr>${rows}</table></div>
    <div class='note'>Le statut est mis à jour par la finance (paiement) puis par la production (réservation). Aucune ressaisie.</div></div>${det}</div>`);
}

/* ---------- M1.3 · Finance, contrôle des paiements ---------- */
function sPaiements() {
  const a = p1(); const os = visOrders();
  const rep = (o) => (o.pay === "Financement" ? (o.bank === "ok" ? "Crédit accepté" : "Crédit refusé") : o.bank === "ok" ? "Autorisation accordée" : "Autorisation refusée");
  const rows = os.map((o) => {
    const i = oInfo(o);
    const dec = i.s === "controle" ? `<button class='btn pri sm' data-act='accepter' data-id='${o.id}' ${o.bank === "ok" ? "" : "disabled"}>Accepter</button><button class='btn red sm' data-act='refuser' data-id='${o.id}'>Refuser</button>`
      : i.s === "refusee" ? pill("Refusé · client à informer", "ko") : i.s === "annulee" ? pill("Refusé · client informé", "ko") : pill("Accepté · CA enregistré", "ok");
    return `<tr class='${i.s === "controle" ? "sel" : ""}'><td><b>${o.id}</b></td><td>${eur(o.prix)}</td><td>${o.pay}</td><td>${rep(o)}</td><td>${dec}</td></tr>`;
  }).join("");
  return shell("finance", "finance/paiements", head("M1.3", "Finance", ["P1 · Contrôler le paiement", "P1 · Paiement accepté ?", "P1 · Enregistrer le CA prévisionnel"], "Finance : contrôle des paiements",
    "Les précommandes enregistrées dans le CRM arrivent ici avec la réponse de la banque ou de l'organisme de crédit.") +
    kpis([["Paiements à contrôler", nf(a.controle), "file d'attente"], ["Paiements acceptés", nf(a.recues - a.controle - a.annulees), "depuis 14 h"], ["Paiements refusés", nf(a.annulees), pct1(a.annulees, a.recues)], ["Chiffre d'affaires prévisionnel", meur(a.ca), "TTC, enregistré dans l'ERP"]], 4) +
    `<div class='card'><h2>Paiements <small>précommandes transmises par le marketing</small></h2>
    <div class='tw'><table><tr><th>Précommande</th><th>Montant</th><th>Moyen de paiement</th><th>Réponse de la banque</th><th>Décision</th></tr>${rows}</table></div>
    <div class='note'>Paiement accepté : le chiffre d'affaires prévisionnel est enregistré dans l'ERP et la précommande passe à la production. Paiement refusé : le marketing informe le client et la précommande est annulée.${flow("Paiements acceptés ou refusés → Marketing et ventes")}</div></div>`);
}

/* ---------- M1.4 · Production, stock et réservations ---------- */
function sStock() {
  const a = p1(); const st = stockTable(); const out = stockOut();
  const os = visOrders().filter((o) => ["payee", "reservee", "confirmee", "livree"].includes(oInfo(o).s));
  const anyPay = os.some((o) => oInfo(o).s === "payee");
  const rows = os.map((o, k) => {
    const i = oInfo(o); const d = dispoCfg(o.cap, o.col);
    let dispo, date, res;
    if (i.s === "payee") {
      dispo = d ? pill("Oui", "ok") : pill("Non", "ko");
      date = d ? dMed("2026-10-23") : "à recalculer";
      res = `<button class='btn pri sm' data-act='reserver' data-id='${o.id}'>${d ? "Réserver un appareil" : "Recalculer la date et réserver"}</button>`;
    } else {
      const j = i.date === JANV;
      dispo = j ? pill("Non", "ko") : pill("Oui", "ok");
      date = j ? `${dMed(JANV)} (recalculée)` : dMed("2026-10-23");
      res = j ? pill("Réservé sur fabrication à venir", "info") : pill(`Réservé · lot ${i.lot}`, "ok");
    }
    const sel = anyPay ? i.s === "payee" : k === 0;
    return `<tr class='${sel ? "sel" : ""}'><td>${hm(o.created)}</td><td><b>${o.id}</b></td><td>${o.cap}, ${o.col}</td><td>${dispo}</td><td>${date}</td><td>${res}</td></tr>`;
  }).join("");
  const srows = st.map((r) => `<tr><td>${r.k.replace("|", ", ")}</td><td>${nf(r.total)}</td><td>${nf(r.res)}</td><td><b>${nf(r.dispo)}</b></td></tr>`).join("");
  const resT = st.reduce((x, r) => x + r.res, 0);
  return shell("production", "production/stock", head("M1.4", "Production", ["P1 · Vérifier le stock", "P1 · Stock disponible ?", "P1 · Recalculer la date", "P1 · Réserver un appareil"], "Production : stock et réservations",
    `France · ${dLong(now())}, ${hm(now())}. Chaque précommande payée est servie sur le stock de lancement ou, à défaut, sur la fabrication à venir.`) +
    kpis([["Stock de lancement", "5 200", "appareils, France"], ["Appareils réservés", nf(resT), out ? "stock épuisé à 14:28" : `${nf(5200 - resT)} encore disponibles`], ["Réservés sur fabrication à venir", nf(a.fab), "précommandes payées"], ["Prochaine date de livraison", out ? "25 janv. 2027" : "23 oct. 2026", out ? "d'après le plan de production" : "stock de lancement"]], 4) +
    `<div class='cols'><div class='card'><h2>Précommandes payées à servir <small>reçues de la Finance</small></h2>
    <div class='tw'><table><tr><th>Heure</th><th>N°</th><th>Configuration</th><th>Stock disponible ?</th><th>Date de livraison</th><th>Réservation</th></tr>${rows}</table></div>
    <div class='note'>Si le stock est disponible, un appareil est réservé. Sinon, la date de livraison est recalculée, puis un appareil à fabriquer est réservé.${flow("Stock disponible, dates de livraison → Marketing et ventes")}</div></div>
    <div class='card'><h2>Stock par configuration <small>lu dans l'ERP</small></h2>
    <table><tr><th>Configuration</th><th>Stock de lancement</th><th>Réservés</th><th>Disponible</th></tr>${srows}</table></div></div>`);
}

/* ---------- M2.4 · CRM, avis reçus ---------- */
function rSteps(r, i) {
  const st = (l, c) => `<div class='${c}'>${l}</div>`;
  const path = !r.accord ? "stat" : r.note >= 7 ? "merci" : DEFAUTS.includes(r.motif) ? "defaut" : "recontact";
  const third = { stat: "Statistique", merci: "Remercié", defaut: "Défaut signalé", recontact: "À recontacter" }[path];
  const thirdCur = (path === "defaut" && i.s === "defaut") || (path === "recontact" && i.s === "a_recontacter");
  const done = ["clos", "recontacte", "remercie", "statistique"].includes(i.s);
  return `<div class='steps'>${st("Réponse enregistrée", "done")}${st("Score et motif", "done")}${st(third, thirdCur ? "cur" : "done")}${st("Suite donnée", done ? "done" : thirdCur ? "" : "cur")}</div>`;
}
function sAvis() {
  const s = sat(); const rs = visReviews();
  const pick = (ref) => (ref && S.reviews[ref] && rInfo(S.reviews[ref]) ? S.reviews[ref] : null);
  const r = pick(ui.sel.r) || rs[0];
  const rows = rs.slice(0, 6).map((x) => { const i = rInfo(x); return `<tr class='click ${x === r ? "sel" : ""}' data-act='selr' data-id='${x.ref}'><td>${ddmm(x.t)} · ${hm(x.t)}</td><td>${cliMail(x.cli)}</td><td>${x.canal}</td><td><b>${x.note}</b>/10</td><td>${esc(x.motif)}</td><td>${x.accord ? "oui" : "non"}</td><td>${rPill(i.s)}</td></tr>`; }).join("");
  let det = "";
  if (r) {
    const i = rInfo(r); const c = CLIENTS[r.cli]; const cfg = r.order ? orderCfg(r.order) : null;
    const tA = r.hist[0].t;
    const kv = r.accord && c ? `<span>Client</span><b>${c.nom} · compte Apple vérifié</b><span>Commande</span><b>${r.order}${cfg ? ` · iPhone Duo ${cfg[0]}, ${cfg[1]}` : " · iPhone Duo"}</b><span>Livraison</span><b>${dMed(LIV)}</b>
      <span>Note et motif</span><b>${r.note} / 10 · ${esc(r.motif)}</b><span>Accord de recontact</span><b>Oui (${dShortY(tA)}, ${hm(tA)})</b>`
      : `<span>Client</span><b>Réponse anonyme</b><span>Canal</span><b>${r.canal}</b><span>Note et motif</span><b>${r.note} / 10 · ${esc(r.motif)}</b><span>Accord de recontact</span><b>Non</b>`;
    let btns = "", note = `Les réponses alimentent le tableau de bord de satisfaction.${flow("Satisfaction → Direction marketing")}`;
    if (i.s === "defaut") { btns = `<button class='btn pri' data-act='transmettre' data-id='${r.ref}'>Transmettre à la production (qualité)</button><button class='btn' data-act='cropen'>Recontacter le client</button>`; note = `La transmission crée un signalement dans l'ERP avec le numéro de série et le lot de l'appareil.${flow("Défauts signalés → Production")}`; }
    if (i.s === "a_recontacter") btns = `<button class='btn pri' data-act='cropen'>Recontacter le client</button>`;
    if (i.s === "a_informer") { btns = `<button class='btn pri' data-act='informer' data-id='${r.ref}'>Informer le client de la suite donnée</button>`; note = `La production et la finance ont traité le signalement : le client peut être informé.${flow("Résultats d'analyse → Marketing")}`; }
    if (i.s === "en_analyse") note = `Le signalement est en cours d'analyse par la production.${flow("Défauts signalés → Production")}`;
    const cr = ui.crOpen && ["defaut", "a_recontacter"].includes(i.s) ? `<textarea class='ta' data-act='crtxt' placeholder='Compte rendu de l'appel ou du courriel' style='margin:12px 0 8px'>${esc(ui.cr)}</textarea><button class='btn' data-act='recontacte' data-id='${r.ref}'>Enregistrer le recontact</button>` : "";
    det = `<div class='card'><h2>Réponse ${r.ref} <small>${r.accord ? "rattachée à la fiche client" : "anonyme"}</small></h2>
    <div class='kv'>${kv}</div>
    ${r.txt ? `<div class='quote' style='margin:12px 0'>« ${esc(r.txt)} »</div>` : `<div style='height:12px'></div>`}
    ${rSteps(r, i)}${btns}${cr}
    <div class='note'>${note}</div></div>`;
  }
  return shell("marketing", "marketing/avis", head("M2.4", "Relation client et données (CRM)", ["P2 · Enregistrer la réponse", "P2 · Calculer le score", "P2 · Note et motif ?", "P2 · Remercier", "P2 · Recontacter", "P2 · Transmettre le défaut", "P2 · Informer de la suite"], "CRM : avis reçus par QR code",
    "Chaque réponse au questionnaire arrive ici, est rattachée à la fiche du client quand il l'a accepté, puis reçoit un score et un motif.") +
    kpis([["Réponses reçues aujourd'hui", nf(s.jour.rep), `dont ${s.jour.anonymes} anonymes`], ["Note moyenne", dec1(s.jour.moy), "sur 10"], ["Clients insatisfaits (note &lt; 7)", nf(s.jour.insatisfaits), pct(s.jour.insatisfaits, s.jour.rep) + " des réponses"], ["À recontacter sous 48 h", nf(s.jour.recontacter), "accord donné"], ["Défauts transmis à la production", nf(s.jour.transmis), "en analyse"]], 5) +
    `<div class='cols'><div class='card'><h2>Dernières réponses <small>identifiants masqués à l'affichage</small></h2>
    <div class='tw'><table><tr><th>Reçu le</th><th>Client</th><th>Canal</th><th>Note</th><th>Motif</th><th>Accord</th><th>Suite</th></tr>${rows}</table></div>
    <div class='note'>Règle de gestion : une note inférieure à 7 classe la réponse en « client insatisfait ». Sans accord, la réponse reste anonyme et sert seulement aux statistiques.</div></div>${det}</div>`);
}

/* ---------- M2.5 · Production, signalements qualité ---------- */
function sQualite() {
  const qs = visSignals(); const pick = (id) => (id && S.signals[id] && S.signals[id].t <= now() ? S.signals[id] : null);
  const q = pick(ui.sel.q) || qs[0]; const L = lotStats();
  let left = `<div class='card'><div class='empty'>Aucun signalement reçu.</div></div>`;
  if (q) {
    const i = at(q.hist, now()); const xq = {}; q.hist.forEach((h) => { if (h.t <= now() && h.x) Object.assign(xq, h.x); });
    const lot = L.find((l) => l.lot === q.lot); const prop = proposition(q);
    const act = xq.action ? (xq.action === "Échange de l'appareil" ? `Échange de l'appareil · contrôle renforcé du lot ${q.lot}` : xq.action) : prop[2];
    const cout = xq.cout != null ? xq.cout : prop[1];
    const dec = i.s === "analyse" ? `<button class='btn pri' data-act='confirmerq' data-id='${q.id}'>Oui : lancer l'action corrective</button><button class='btn red' data-act='nonq' data-id='${q.id}'>Non : informer le client</button>`
      : i.s === "confirme" ? pill("Défaut confirmé · action corrective lancée", "ko") : pill("Défaut non confirmé · client à informer", "grey");
    left = `<div class='card'><h2>Signalement ${q.id} <small>reçu du CRM le ${dShortY(q.t)} à ${hm(q.t)}</small></h2>
    <div class='kv'><span>Origine</span><b>Réponse ${q.rev} (questionnaire QR code)</b><span>Défaut signalé</span><b>${esc(q.defaut)}</b>
    <span>Appareil</span><b>${q.cfg}</b><span>Numéro de série</span><b>${q.serial || "••••••"} (lu dans l'ERP)</b>
    <span>Lot de fabrication</span><b>${q.lot} · assemblé en ${lot ? lot.sem : "semaine 41"}</b><span>Autres signalements du lot</span><b>${lot ? `${nf(lot.sg - 1)} sur ${nf(lot.n)} appareils` : "—"}</b></div>
    <div class='quote' style='margin:12px 0'>${q.diag}</div>
    <h2 style='margin-top:14px'>Défaut confirmé ?</h2>${dec}
    ${i.s === "non_confirme" ? "" : `<div style='margin-top:14px' class='kv'><span>Action corrective</span><b>${act}</b><span>Coût estimé</span><b>${eur(cout)} transmis à la finance</b></div>`}
    <div class='note'>La décision est renvoyée au CRM : le client est informé de la suite donnée.${flow("Résultats d'analyse → Marketing")}${flow("Coûts de garantie → Finance")}</div></div>`;
  }
  const ltr = L.map((l) => `<tr class='${q && l.lot === q.lot ? "sel" : ""}'><td><b>${l.lot}</b></td><td>${l.sem}</td><td>${nf(l.sg)}</td><td>${nf(l.cf)}</td></tr>`).join("");
  const others = qs.map((x) => `<tr class='click ${x === q ? "sel" : ""}' data-act='selq' data-id='${x.id}'><td><b>${x.id}</b></td><td>${ddmm(x.t)} · ${hm(x.t)}</td><td>${esc(x.defaut)}</td><td>${x.lot}</td><td>${qPill(at(x.hist, now()).s)}</td></tr>`).join("");
  return shell("production", "production/qualite", head("M2.5", "Production (qualité)", ["P2 · Analyser le signalement", "P2 · Défaut confirmé ?", "P2 · Action corrective"], "Production : signalements qualité",
    "Les défauts signalés par les clients arrivent du CRM. La production retrouve l'appareil dans l'ERP grâce à son numéro de série et décide de la suite.") +
    `<div class='cols'>${left}<div class='card'><h2>Signalements par lot <small>charnière, 30 derniers jours</small></h2>
    <table><tr><th>Lot</th><th>Assemblage</th><th>Signalés</th><th>Confirmés</th></tr>${ltr}</table>
    <div class='note'>Seuil d'alerte : plus de 0,3 % d'appareils signalés dans un lot déclenche un contrôle renforcé.</div></div></div>
    <div class='card'><h2>Tous les signalements <small>reçus du CRM</small></h2><div class='tw'><table><tr><th>N°</th><th>Reçu le</th><th>Défaut</th><th>Lot</th><th>Statut</th></tr>${others}</table></div></div>`);
}

/* ---------- M2.6 · Finance, coûts de garantie ---------- */
function sGarantie() {
  const s = sat(); const cs = Object.values(S.costs).filter((c) => c.t <= now()).sort((a, b) => (a.id < b.id ? 1 : -1));
  const pend = cs.filter((c) => at(c.hist, now()).s === "a_enregistrer");
  const first = pend[0];
  const rows = cs.map((c) => `<tr class='${pend.includes(c) ? "sel" : ""}'><td><b>${c.id}</b></td><td>${c.action}</td><td>${eur(c.cout)}</td><td>${cPill(at(c.hist, now()).s)}</td></tr>`).join("");
  const ce = first || cs[0];
  const erp = ui.erp && ce ? `<div class='erp'><b>Écriture ERP · coûts de garantie</b><br>${ce.id} · ${ce.action} · ${eur(ce.cout)} · centre de coût « Garantie iPhone Duo » · lot ${S.signals[ce.id] ? S.signals[ce.id].lot : ""}<br>Statut : ${at(ce.hist, now()).s === "enregistre" ? `enregistrée le ${dShortY(tOf(ce.hist, "enregistre"))} à ${hm(tOf(ce.hist, "enregistre"))}` : "à enregistrer"}</div>` : "";
  return shell("finance", "finance/garantie", head("M2.6", "Finance (contrôle de gestion)", ["P2 · Enregistrer le coût de garantie"], "Finance : coûts de garantie",
    "Chaque action corrective décidée par la production est chiffrée et enregistrée dans l'ERP. Le cumul est comparé à la provision.") +
    kpis([["Coûts enregistrés (semaine)", eur(s.couts), `${s.confirmes} défauts confirmés`], ["Coût moyen par défaut", eur(s.couts / s.confirmes), "échanges et réparations"], ["Provision pour garantie utilisée", pct(s.couts, 268550), "du budget du trimestre"], ["Écart par rapport à la prévision", "+1,2 pt", "à surveiller"]], 4) +
    `<div class='card'><h2>Actions correctives à chiffrer <small>reçues de la production</small></h2>
    <div class='tw'><table><tr><th>Signalement</th><th>Action corrective</th><th>Coût</th><th>Statut</th></tr>${rows}</table></div>
    <div style='margin-top:12px'>${first ? `<button class='btn pri' data-act='enregistrer' data-id='${first.id}'>Enregistrer le coût de ${first.id}</button>` : ""}<button class='btn' data-act='erp'>Voir l'écriture dans l'ERP</button></div>${erp}
    <div class='note'>Une fois le coût enregistré, le marketing informe le client de la solution et le tableau de bord de satisfaction est mis à jour.</div></div>`);
}

/* ---------- M2.7 · tableau de bord de satisfaction ---------- */
function sSatisfaction() {
  const s = sat(); const ins = Object.values(s.motifs).reduce((x, y) => x + y, 0);
  const bars = MOTIFS.map((m) => { const v = Math.round((s.motifs[m] / ins) * 100); return `<div class='barrow'><div>${m}</div><div class='barbg'><div class='bar' style='width:${Math.min(100, v * 3)}%'></div></div><div><b>${v} %</b></div></div>`; }).join("");
  const wk = s.semaines.map(([w, v]) => `<div style='flex:1;text-align:center'><div style='height:${Math.trunc(v * 12)}px;background:#0071e3;border-radius:8px 8px 0 0;margin:0 18px'></div><div style='font-size:12px;margin-top:6px'><b>${dec1(v)}</b><br><span style='color:#86868b'>${w.slice(0, 3)}</span></div></div>`).join("");
  const actor = ui.actor && ["finance", "production"].includes(ui.actor) ? ui.actor : "marketing";
  return shell(actor, actor + "/satisfaction", head("M2.7", "Direction marketing, Production, Finance", ["P2 · Mettre à jour le tableau de bord"], "Tableau de bord de satisfaction",
    `France · ${s.extra ? "du 2 au 9 novembre 2026" : "semaine du 2 au 8 novembre 2026"} · mis à jour à chaque réponse enregistrée dans le CRM.`) +
    kpis([["Réponses reçues", nf(s.rep), `taux de réponse ${s.taux} %`], ["Note moyenne", dec1(s.moy), "objectif 8,5"], ["Clients satisfaits (note ≥ 7)", pct(s.satis, s.rep), nf(s.satis) + " réponses"], ["Défauts signalés", nf(s.defauts), `dont ${s.confirmes} confirmés`], ["Délai moyen de recontact", s.recontact + " h", "objectif 48 h"], ["Coûts de garantie", eur(s.couts), "enregistrés par la Finance"]], 6) +
    `<div class='cols3'><div class='card'><h2>Motifs d'insatisfaction <small>${nf(ins)} réponses</small></h2>${bars}</div>
    <div class='card'><h2>Note moyenne par semaine</h2><div style='display:flex;align-items:flex-end;height:150px'>${wk}</div><div class='note'>La baisse vient surtout des délais de livraison et de la charnière.</div></div>
    <div class='card'><h2>Ce que chaque fonction en fait</h2><div class='kv' style='grid-template-columns:96px 1fr'><span>Marketing</span><div>Adapter les messages sur le prix et les délais ; suivre les dossiers ouverts.</div>
    <span>Production</span><div>Contrôler le lot L-2643-B ; corriger le serrage de la charnière.</div><span>Finance</span><div>Suivre la provision pour garantie ; actualiser le coût de revient.</div></div></div></div>`);
}

/* ---------- autres écrans du marketing ---------- */
function sSuivi() {
  const rs = visReviews().filter((r) => r.accord && rInfo(r).s !== "remercie");
  const etape = { defaut: "Défaut à transmettre", a_recontacter: "Client à recontacter", en_analyse: "Analyse par la production", a_informer: "Client à informer", recontacte: "Terminé", clos: "Terminé" };
  const rows = rs.map((r) => { const i = rInfo(r); return `<tr class='click' data-act='openr' data-id='${r.ref}'><td><b>${r.ref}</b></td><td>${cliNom(r.cli)}</td><td>${r.note}/10 · ${esc(r.motif)}</td><td>${etape[i.s]}</td><td>${quand(i.t)}</td><td>${rPill(i.s)}</td></tr>`; }).join("");
  const open = rs.filter((r) => !["clos", "recontacte"].includes(rInfo(r).s)).length;
  return shell("marketing", "marketing/suivi", head("", "Relation client et données (CRM)", [], "Dossiers de suivi", "Les avis qui demandent une action : recontact, défaut signalé, solution à annoncer au client.") +
    kpis([["Dossiers ouverts", nf(open), "avis avec accord de recontact"], ["Délai moyen de recontact", "19 h", "objectif 48 h"], ["Dossiers clos", nf(rs.length - open), "depuis le 3 novembre"]], 3) +
    `<div class='card'><h2>Dossiers <small>cliquer pour ouvrir la réponse</small></h2><div class='tw'><table><tr><th>Dossier</th><th>Client</th><th>Avis</th><th>Étape</th><th>Depuis</th><th>Statut</th></tr>${rows}</table></div></div>`);
}
function sClients() {
  const ids = Object.keys(CLIENTS); const selId = CLIENTS[ui.sel.c] ? ui.sel.c : "lea";
  const ordersOf = (cli) => { const os = Object.values(S.orders).filter((o) => o.cli === cli && o.created <= now()).map((o) => [o.id, `iPhone Duo ${o.cap}, ${o.col}`, oPill(oInfo(o)), o.created]);
    Object.values(S.reviews).forEach((r) => { if (r.cli === cli && r.order && !S.orders[r.order] && rInfo(r)) { const c = orderCfg(r.order); os.push([r.order, c ? `iPhone Duo ${c[0]}, ${c[1]}` : "iPhone Duo", pill("Livrée le 23 oct.", "ok"), "2026-10-16"]); } });
    return os; };
  const rows = ids.map((k) => { const c = CLIENTS[k]; return `<tr class='click ${k === selId ? "sel" : ""}' data-act='selc' data-id='${k}'><td><b>${c.nom}</b></td><td>${c.mail}</td><td>${c.ville}</td><td>${ordersOf(k).length}</td><td>${offresDe(k) ? pill("Oui", "ok") : pill("Non", "grey")}</td></tr>`; }).join("");
  const c = CLIENTS[selId]; const os = ordersOf(selId); const rs = visReviews().filter((r) => r.cli === selId);
  const notes = (S.notes[selId] || []).filter((n) => n.t <= now());
  const line = (h) => `<div style='padding:6px 0;border-bottom:1px solid #f0f0f3;font-size:12.5px'>${h}</div>`;
  const det = `<div class='card'><h2>${c.nom} <small>${os.length ? `fiche créée le ${dShortY(os.map((o) => o[3]).sort()[0])}` : "aucune commande iPhone Duo"}</small></h2>
  <div class='kv'><span>Courriel</span><b>${c.mail}</b><span>Téléphone</span><b>${c.tel}</b><span>Ville</span><b>${c.ville}</b><span>Offres personnalisées</span><b>${offresDe(selId) ? "Acceptées" : "Refusées"}</b></div>
  <h2 style='margin-top:16px'>Commandes</h2>${os.map(([id, cfg, p]) => line(`<b>${id}</b> · ${cfg} · ${p}`)).join("") || `<div class='empty'>Aucune commande.</div>`}
  <h2 style='margin-top:16px'>Avis</h2>${rs.map((r) => line(`<b>${r.ref}</b> · ${r.note}/10 · ${esc(r.motif)} · ${rPill(rInfo(r).s)}`)).join("") || `<div class='empty'>Aucun avis rattaché.</div>`}
  <h2 style='margin-top:16px'>Notes</h2>${notes.map((n) => line(`<span style='color:#86868b'>${quand(n.t)}</span><br>${esc(n.txt)}`)).join("") || `<div class='empty'>Aucune note.</div>`}
  <textarea class='ta' data-act='notetxt' placeholder='Ajouter une note sur ce client' style='margin-top:10px'>${esc(ui.note)}</textarea><div style='margin-top:8px'><button class='btn' data-act='addnote' data-id='${selId}'>Ajouter la note</button></div></div>`;
  return shell("marketing", "marketing/clients", head("", "Marketing et ventes (CRM)", [], "Fiches clients", "Une fiche par client, créée ou complétée à chaque précommande. Les accords donnés par le client ne se modifient que depuis son compte.") +
    `<div class='cols'><div class='card'><h2>Clients <small>${ids.length} fiches</small></h2><div class='tw'><table><tr><th>Client</th><th>Courriel</th><th>Ville</th><th>Commandes</th><th>Offres</th></tr>${rows}</table></div></div>${det}</div>`);
}
function chart() {
  const lim = hm(now()) > "15:00" || now() > "2026-10-17" ? "15:00" : hm(now());
  const pts = COURBE.filter(([h]) => h <= lim); const W = 560, H = 200, X = (h) => { const [a, b] = h.split(":").map(Number); return 40 + (((a - 14) * 60 + b) / 60) * (W - 60); }, Y = (v) => H - 24 - (v / 8000) * (H - 40);
  const path = pts.map(([h, v], k) => (k ? "L" : "M") + X(h).toFixed(1) + " " + Y(v).toFixed(1)).join(" ");
  const ticks = ["14:00", "14:15", "14:30", "14:45", "15:00"].map((h) => `<text x="${X(h)}" y="${H - 6}" font-size="10" text-anchor="middle" fill="#86868b">${h}</text>`).join("");
  const ep = lim >= "14:28" ? `<line x1="${X("14:28")}" y1="14" x2="${X("14:28")}" y2="${H - 24}" stroke="#ff3b30" stroke-dasharray="3 3"/><text x="${X("14:28") + 4}" y="22" font-size="10" fill="#b3261e">stock épuisé, 14:28</text>` : "";
  return `<svg viewBox="0 0 ${W} ${H}" width="100%"><line x1="40" y1="${Y(5200)}" x2="${W - 20}" y2="${Y(5200)}" stroke="#d2d2d7" stroke-dasharray="4 4"/><text x="${W - 20}" y="${Y(5200) - 4}" font-size="10" text-anchor="end" fill="#86868b">stock de lancement : 5 200</text>
  ${[0, 2000, 4000, 6000, 8000].map((v) => `<text x="34" y="${Y(v) + 3}" font-size="10" text-anchor="end" fill="#86868b">${nf(v)}</text>`).join("")}${ticks}${ep}
  <path d="${path}" fill="none" stroke="#0071e3" stroke-width="2.5"/>${pts.length ? `<circle cx="${X(pts[pts.length - 1][0])}" cy="${Y(pts[pts.length - 1][1])}" r="4" fill="#0071e3"/>` : ""}</svg>`;
}
const hbars = (arr, max) => arr.map(([l, v]) => `<div class='barrow'><div>${l}</div><div class='barbg'><div class='bar' style='width:${Math.min(100, (v / max) * 100)}%'></div></div><div><b>${v} %</b></div></div>`).join("");
function sLancement() {
  const a = p1(); const out = stockOut();
  return shell("marketing", "marketing/lancement", head("", "Direction marketing", [], "Tableau de bord des précommandes", `France · ${dLong(now())}, ${hm(now())} · données agrégées, sans information personnelle.`) +
    kpis([["Précommandes reçues", nf(a.recues), "depuis 14 h"], ["Confirmées", nf(a.confirmees), pct(a.confirmees, a.recues)], ["Chiffre d'affaires prévisionnel", meur(a.ca), "TTC"], ["Stock de lancement réservé", pct(Math.min(5200, a.stockRes), 5200), nf(Math.min(5200, a.stockRes)) + " sur 5 200"], ["Confirmées pour janvier", nf(a.janvier), "fabrication à venir"], ["Date annoncée", out ? "25 janv." : "23 oct.", out ? "depuis 14:28" : "stock disponible"]], 6) +
    `<div class='cols'><div class='card'><h2>Précommandes cumulées le 16 octobre</h2>${chart()}</div>
    <div class='card'><h2>Mix des précommandes</h2>${hbars(MIX, 40)}<h2 style='margin-top:14px'>Couleurs</h2>${hbars([["Ciel nocturne", 54], ["Blanc stellaire", 46]], 60)}</div></div>`);
}
function sCampagnes() {
  const rows = CAMPAGNES.map((r) => `<tr>${r.map((c, k) => `<td>${k === 0 ? "<b>" + c + "</b>" : c}</td>`).join("")}</tr>`).join("");
  return shell("marketing", "marketing/plan", head("", "Direction marketing", [], "Plan de lancement", "Actions de lancement et audience, rapprochées des précommandes dans le CRM (attribution au dernier contact).") +
    kpis([["Visites de la page iPhone Duo", "940 000", "France, depuis le 9 septembre"], ["Vues des vidéos sociales", "4,3 M", "TikTok et Instagram"], ["Précommandes après un clic social", "17 %", "des précommandes en ligne"], ["Clients ayant accepté les offres", "38 %", "des clients Apple en France"]], 4) +
    `<div class='card'><h2>Actions de lancement</h2><div class='tw'><table><tr><th>Action</th><th>Période</th><th>Objectif</th><th>Audience</th><th>Interaction</th><th>Part des précommandes</th></tr>${rows}</table></div>
    <div class='note'>Les courriels ne sont envoyés qu'aux clients qui ont accepté les offres personnalisées.</div></div>`);
}
const ventesDist = (part) => (now() >= "2026-10-23T09:00" ? part : 0);
function sDistributeurs() {
  const after = now() >= "2026-10-23T09:00"; const extra = S.distSent || 0;
  const rows = DISTRIBS.map(([n, ty, al, part], k) => { const v = Math.round(al * ventesDist(part)) + (k === 0 ? extra : 0); return `<tr><td><b>${n}</b></td><td>${ty}</td><td>${nf(al)}</td><td>${nf(v)}</td><td>${pct(v, al)}</td><td>${after ? dShort(now()) + " 08:00" : "—"}</td></tr>`; }).join("");
  const tot = DISTRIBS.reduce((a, d) => a + d[2], 0); const vend = DISTRIBS.reduce((a, d) => a + Math.round(d[2] * ventesDist(d[3])), 0) + extra;
  return shell("marketing", "marketing/distributeurs", head("", "Marketing et ventes (EDI)", [], "Distributeurs", "Opérateurs télécom et revendeurs agréés : Apple leur alloue un stock pour la mise en vente, ils renvoient chaque matin leurs ventes de la veille par échange de données informatisé (EDI).") +
    kpis([["Stock alloué aux distributeurs", nf(tot), "hors boutique en ligne"], ["Ventes déclarées", nf(vend), after ? "depuis le 23 octobre" : "mise en vente le 23 octobre"], ["Taux d'écoulement", pct(vend, tot), ""], ["Distributeurs reliés", DISTRIBS.length, "relevé quotidien"]], 4) +
    `<div class='card'><h2>Distributeurs <small>noms fictifs</small></h2><div class='tw'><table><tr><th>Distributeur</th><th>Type</th><th>Stock alloué</th><th>Ventes déclarées</th><th>Écoulement</th><th>Dernier relevé</th></tr>${rows}</table></div>
    <div class='note'>Les ventes des distributeurs complètent les précommandes de la boutique en ligne. Voir aussi l'<a class='lnk' href='#/partenaire/distributeur'>espace partenaire de Néo Télécom</a>.</div></div>`);
}

/* ---------- autres écrans finance et production ---------- */
function sBudgets() {
  const a = p1(); const w = CAPS.map((c) => MIX.find((m) => m[0] === c.cap)[1] * c.prix); const W = w.reduce((x, y) => x + y, 0);
  const rows = CAPS.map((c, k) => { const ca = (a.ca * w[k]) / W; return `<tr><td>${c.cap}</td><td>${eur(c.prix)}</td><td>${nf(ca / c.prix)}</td><td><b>${meur(ca)}</b></td></tr>`; }).join("");
  return shell("finance", "finance/budgets", head("", "Finance (contrôle de gestion)", [], "Budgets et prix", "Prix de vente fixés avec la direction marketing, chiffre d'affaires prévisionnel enregistré à chaque paiement accepté, et budget de garantie du trimestre.") +
    kpis([["Chiffre d'affaires prévisionnel", meur(a.ca), "TTC, France"], ["Paiements acceptés", nf(a.recues - a.controle - a.annulees), "depuis 14 h"], ["Panier moyen", eur(a.ca / Math.max(1, a.recues - a.controle - a.annulees)), "par précommande"], ["Budget de garantie", "268 550 €", "trimestre en cours"]], 4) +
    `<div class='card'><h2>Prix et chiffre d'affaires par capacité <small>estimation à partir du mix des précommandes</small></h2><div class='tw'><table><tr><th>Capacité</th><th>Prix TTC</th><th>Précommandes payées</th><th>Chiffre d'affaires</th></tr>${rows}</table></div>
    <div class='note'>Le chiffre d'affaires prévisionnel devient du chiffre d'affaires réalisé à l'expédition de l'appareil.</div></div>`);
}
function sFabrication() {
  const a = p1(); let cum = 0; const out = stockOut();
  const rows = PLAN.map(([w, q]) => { const avant = cum; cum += q; const servies = Math.max(0, Math.min(q, a.fab - avant)); return `<tr><td>${w}</td><td>${nf(q)}</td><td>${nf(servies)}</td><td>${nf(Math.max(0, a.fab - cum))}</td></tr>`; }).join("");
  return shell("production", "production/fabrication", head("", "Production (ERP)", [], "Plan de production", "Appareils attendus à l'entrepôt français, d'après le plan de fabrication transmis par l'assembleur.") +
    kpis([["Précommandes en attente de fabrication", nf(a.fab), a.fab ? "livraison à partir du 25 janvier" : "le stock de lancement suffit"], ["Prochaine arrivée", "11 janv. 2027", "1 800 appareils"], ["Date annoncée aux nouveaux clients", out ? "25 janv. 2027" : "23 oct. 2026", "affichée sur la boutique"]], 3) +
    `<div class='card'><h2>Arrivées prévues <small>France</small></h2><div class='tw'><table><tr><th>Semaine</th><th>Appareils prévus</th><th>Précommandes servies</th><th>Encore en attente</th></tr>${rows}</table></div>
    <div class='note'>La date de livraison affichée sur la boutique est recalculée à partir de ce plan quand le stock de lancement est épuisé.</div></div>`);
}

/* ---------- vue d'ensemble : flux, processus ---------- */
const F = (t, de, vers, info, outil, ref, proc) => ({ t, de, vers, info, outil, ref, proc });
function fluxAll() {
  const t = now(); const L = [];
  FLUX_SEED.forEach((f) => { if (f[0] <= t) L.push(F(...f)); });
  (S.flog || []).forEach((f) => { if (f.t <= t) L.push(f); });
  Object.values(S.orders).forEach((o) => {
    if (o.created > t) return; const c = o.created;
    L.push(F(c, "Client", "Marketing et ventes", `Précommande ${o.id} (${o.cap}, ${o.col}) et données de paiement`, "Site de vente → CRM", "A3-9 · A1-1", "P1"));
    L.push(F(c, "Marketing et ventes", "Finance", `Commande à encaisser ${o.id} (${eur(o.prix)})`, "CRM → ERP", "A3-11 · A2-5", "P1"));
    L.push(F(c, "Finance", "Banque", `Demande ${o.pay === "Financement" ? "de crédit" : "d'autorisation"} pour ${o.id}`, "Données de paiement", "A1-7", "P1"));
    L.push(F(c, "Banque", "Finance", `${o.bank === "ok" ? "Paiement accordé" : "Paiement refusé"} pour ${o.id}`, "Données de paiement", "A1-7", "P1"));
    o.hist.forEach((h) => {
      if (h.t > t) return;
      if (h.s === "payee") { L.push(F(h.t, "Finance", "Marketing et ventes", `Paiement accepté pour ${o.id}`, "ERP → CRM", "A3-11 · A2-6", "P1")); L.push(F(h.t, "Finance", "Production", `Précommande payée ${o.id} à servir`, "ERP", "A2-3", "P1")); }
      if (h.s === "refusee") L.push(F(h.t, "Finance", "Marketing et ventes", `Paiement refusé pour ${o.id}`, "ERP → CRM", "A3-11 · A2-6", "P1"));
      if (h.s === "reservee") L.push(F(h.t, "Production", "Marketing et ventes", h.x && h.x.date === JANV ? `Stock épuisé : livraison de ${o.id} recalculée au 25 janvier 2027` : `Appareil réservé pour ${o.id} (${h.x ? h.x.lot : ""}) : livraison le 23 octobre`, "ERP → CRM", "A3-12 · A2-4", "P1"));
      if (h.s === "confirmee") L.push(F(h.t, "Marketing et ventes", "Client", `Confirmation de ${o.id} et date de livraison`, "Courriel", "A3-10 · A1-2", "P1"));
      if (h.s === "annulee") L.push(F(h.t, "Marketing et ventes", "Client", `Paiement refusé : précommande ${o.id} annulée`, "Courriel", "A3-10 · A1-2", "P1"));
    });
  });
  Object.values(S.reviews).forEach((r) => {
    if (!rInfo(r, t)) return; const qui = r.accord ? "Client" : "Client (anonyme)";
    L.push(F(r.t, qui, "Marketing et ventes", `Réponse au questionnaire ${r.ref} (${r.note}/10, ${r.motif})`, "Questionnaire → CRM", "A3-15 · A1-1", "P2"));
    L.push(F(r.t, "Marketing et ventes", "Direction marketing", `Tableau de bord de satisfaction mis à jour (${r.ref})`, "Tableau de bord", "A3-18", "P2"));
    r.hist.forEach((h) => {
      if (h.t > t) return;
      if (h.s === "remercie") L.push(F(h.t, "Marketing et ventes", "Client", `Remerciement pour l'avis ${r.ref}`, "Courriel", "A3-16 · A1-2", "P2"));
      if (h.s === "en_analyse") L.push(F(h.t, "Marketing et ventes", "Production", `Défaut signalé ${r.ref} (${r.motif})`, "CRM → ERP", "A3-17 · A2-3", "P2"));
      if (h.s === "recontacte") L.push(F(h.t, "Marketing et ventes", "Client", `Réponse à l'avis ${r.ref}`, "Téléphone", "A3-16 · A1-2", "P2"));
      if (h.s === "clos") L.push(F(h.t, "Marketing et ventes", "Client", `Suite donnée à l'avis ${r.ref}`, "Courriel", "A3-16 · A1-2", "P2"));
    });
  });
  Object.values(S.signals).forEach((q) => {
    q.hist.forEach((h) => {
      if (h.t > t) return;
      if (h.s === "confirme") { L.push(F(h.t, "Production", "Marketing et ventes", `Résultat d'analyse ${q.id} : défaut confirmé`, "ERP → CRM", "A3-17 · A2-4", "P2")); L.push(F(h.t, "Production", "Finance", `Coût de garantie ${q.id} : ${eur(h.x.cout)}`, "ERP", "A2-7", "P2")); }
      if (h.s === "non_confirme") L.push(F(h.t, "Production", "Marketing et ventes", `Résultat d'analyse ${q.id} : défaut non confirmé`, "ERP → CRM", "A3-17 · A2-4", "P2"));
    });
  });
  return L.sort((a, b) => (a.t < b.t ? 1 : a.t > b.t ? -1 : 0));
}
const EXT = ["Client", "Client (anonyme)", "Banque", "Distributeurs"];
function vFlux() {
  const all = fluxAll(); const f = ui.jf || "tous";
  const L = all.filter((x) => f === "tous" || (f === "ext" ? EXT.includes(x.de) || EXT.includes(x.vers) : x.proc === f));
  const chip = (k, t) => `<button class='${f === k ? "on" : ""}' data-act='jf' data-id='${k}'>${t}</button>`;
  const rows = L.slice(0, 60).map((x) => `<tr><td>${ddmm(x.t)} · ${hm(x.t)}</td><td>${x.de}</td><td>${x.vers}</td><td>${esc(x.info)}</td><td>${x.outil}</td><td><b>${x.ref}</b></td></tr>`).join("");
  const figs = [["contexte-apple", "Modèle de contexte d'Apple pour le lancement"], ["flux-apple", "Flux entre les acteurs internes d'Apple"], ["contexte-fonction", "Modèle de contexte de la fonction marketing et ventes"], ["flux-fonction", "Flux internes de la fonction marketing et ventes"]];
  return shell(ui.actor, "vue/flux", head("", "Vue d'ensemble du SI", [], "Cartographie des flux", "Les modèles de notre dossier, puis chaque information réellement échangée dans la démonstration, d'un service à l'autre ou avec un acteur externe.") +
    `<div class='grid2'>${figs.map(([fn, t]) => `<div class='fig'><a href='img/fig/${fn}.png' target='_blank'><img src='img/fig/${fn}.png' alt='${t}' loading='lazy'></a><p>${t}</p></div>`).join("")}</div>
    <div class='card'><h2>Journal des échanges <small>références des tableaux de flux A1 à A3 du dossier</small></h2><div class='chipsf'>${chip("tous", "Tous")}${chip("P1", "Processus 1")}${chip("P2", "Processus 2")}${chip("ext", "Avec l'extérieur")}</div>
    <div class='tw'><table><tr><th>Date</th><th>Émetteur</th><th>Récepteur</th><th>Information</th><th>Outil</th><th>Flux</th></tr>${rows || `<tr><td colspan='6' class='empty'>Aucun échange.</td></tr>`}</table></div>
    <div class='note'>A1 : flux entre Apple et ses acteurs externes · A2 : flux entre les acteurs internes d'Apple · A3 : flux de la fonction marketing et ventes.</div></div>
    <div class='card'><h2>Acteurs externes <small>espaces partenaires</small></h2><div class='views'><a class='view' href='#/partenaire/banque'><b>Banque du client</b><div>Demandes d'autorisation envoyées par la finance</div></a><a class='view' href='#/partenaire/distributeur'><b>Néo Télécom</b><div>Distributeur : stock alloué et relevé des ventes (EDI)</div></a></div></div>`);
}
function timeline(steps) {
  let cur = false;
  return `<div style='margin-top:10px'>${steps.map(([lane, task, tt, skip]) => {
    let st, col;
    if (skip) { st = "Non concerné"; col = "#c7c7cc"; } else if (tt && tt <= now()) { st = ddmm(tt) + " · " + hm(tt); col = "#34c759"; } else if (!cur) { cur = true; st = "En cours"; col = "#0071e3"; } else { st = "À venir"; col = "#d2d2d7"; }
    return `<div style='display:grid;grid-template-columns:14px 130px 1fr 90px;gap:10px;align-items:center;padding:7px 0;border-bottom:1px solid #f0f0f3;font-size:12.5px;${skip ? "color:#aeaeb2" : ""}'><span style='width:10px;height:10px;border-radius:50%;background:${col}'></span><span style='color:#86868b'>${lane}</span><span>${task}</span><span style='text-align:right;color:#6e6e73'>${st}</span></div>`;
  }).join("")}</div>`;
}
function tlOrder(o) {
  const c = o.created; const tP = tOf(o.hist, "payee"), tR = tOf(o.hist, "refusee"), tRes = tOf(o.hist, "reservee"), tC = tOf(o.hist, "confirmee"), tA = tOf(o.hist, "annulee");
  const i = oInfo(o); const ko = !!tR || o.bank === "ko"; const fab = i.date === JANV || (!tRes && !dispoCfg(o.cap, o.col));
  return timeline([
    ["Client", "Précommander (message « précommande validée »)", c], ["Marketing et ventes", "Enregistrer la précommande", c], ["Finance", "Contrôler le paiement", c],
    ["Finance", `Paiement accepté ? ${tP ? "· oui" : tR ? "· non" : ""}`, tP || tR], ["Finance", "Enregistrer le CA prévisionnel", tP, ko],
    ["Production", `Vérifier le stock · stock disponible ? ${tRes ? (fab ? "· non" : "· oui") : ""}`, tRes, ko], ["Production", "Recalculer la date", tRes, ko || !fab], ["Production", "Réserver un appareil", tRes, ko],
    ["Marketing et ventes", "Confirmer la commande", tC, ko], ["Marketing et ventes", "Informer du refus", tA, !ko], ["Client", ko ? "Recevoir le message de refus" : "Recevoir la confirmation", ko ? tA : tC],
  ]);
}
function tlReview(r) {
  const h = r.hist; const q = Object.values(S.signals).find((x) => x.rev === r.ref);
  const tQ = q ? tOf(q.hist, "confirme") || tOf(q.hist, "non_confirme") : null; const conf = q && tOf(q.hist, "confirme");
  const cost = q && S.costs[q.id] ? tOf(S.costs[q.id].hist, "enregistre") : null;
  const def = r.accord && r.note < 7 && DEFAUTS.includes(r.motif); const rec = r.accord && r.note < 7 && !def;
  return timeline([
    [r.accord ? "Client" : "Client (anonyme)", "Répondre au questionnaire", r.t], ["Marketing et ventes", "Enregistrer la réponse, calculer le score", r.t],
    ["Marketing et ventes", `Note et motif ? · ${!r.accord ? "sans accord" : r.note >= 7 ? "7 ou plus" : def ? "défaut" : "moins de 7"}`, r.t],
    ["Marketing et ventes", "Remercier le client", r.t, !(r.accord && r.note >= 7)], ["Marketing et ventes", "Recontacter le client", tOf(h, "recontacte"), !rec],
    ["Marketing et ventes", "Transmettre le défaut à la production", tOf(h, "en_analyse"), !def], ["Production", `Analyser le signalement · défaut confirmé ? ${tQ ? (conf ? "· oui" : "· non") : ""}`, tQ, !def],
    ["Production", "Lancer l'action corrective", conf, !def || (tQ && !conf)], ["Finance", "Enregistrer le coût de garantie", cost, !def || (tQ && !conf)],
    ["Marketing et ventes", "Informer le client de la suite", tOf(h, "clos"), !def], ["Direction marketing", "Mettre à jour le tableau de bord", r.t],
  ]);
}
function vProc(n) {
  const prm = new URLSearchParams(location.hash.split("?")[1] || "");
  const line = (l, v, href) => `<div style='display:flex;justify-content:space-between;padding:7px 0;border-bottom:1px solid #f0f0f3;font-size:12.5px'><a class='lnk' href='#/${href}'>${l}</a><b>${v}</b></div>`;
  if (n === "p1") {
    const os = visOrders(); const o = S.orders[prm.get("o")] && oInfo(S.orders[prm.get("o")]) ? S.orders[prm.get("o")] : os.find((x) => x.u) || S.orders.W150032;
    const sel = `<select class='inp' data-act='trk' data-k='o'>${os.map((x) => `<option value='${x.id}' ${x === o ? "selected" : ""}>${x.id} · ${x.cap}, ${x.col} · ${hm(x.created)}</option>`).join("")}</select>`;
    return shell(ui.actor, "vue/p1", head("", "Vue d'ensemble du SI", [], "Processus P1 : de la précommande à la confirmation", "Le diagramme BPMN de notre dossier, le travail en attente à chaque étape et le suivi d'une précommande dans le processus.") +
      `<div class='cols'><div class='card'><h2>Diagramme BPMN</h2><a href='img/fig/bpmn-precommande.png' target='_blank'><img src='img/fig/bpmn-precommande.png' alt='Diagramme BPMN du processus de précommande' style='width:100%;border:1px solid #f0f0f3;border-radius:8px'></a></div>
      <div class='card'><h2>Travail en attente</h2>${line("Paiements à contrôler (Finance, M1.3)", badge("finance/paiements"), "finance/paiements")}${line("Précommandes payées à servir (Production, M1.4)", badge("production/stock"), "production/stock")}${line("Confirmations et refus à envoyer (Marketing, M1.2)", badge("marketing/precommandes"), "marketing/precommandes")}
      <h2 style='margin-top:18px'>Suivre une précommande</h2>${sel}${o ? tlOrder(o) : ""}</div></div>`);
  }
  const rs = visReviews(); const r = S.reviews[prm.get("r")] && rInfo(S.reviews[prm.get("r")]) ? S.reviews[prm.get("r")] : rs[0];
  const sel = `<select class='inp' data-act='trk' data-k='r'>${rs.map((x) => `<option value='${x.ref}' ${x === r ? "selected" : ""}>${x.ref} · ${x.note}/10 · ${x.motif} · ${ddmm(x.t)}</option>`).join("")}</select>`;
  return shell(ui.actor, "vue/p2", head("", "Vue d'ensemble du SI", [], "Processus P2 : satisfaction par QR code", "Le diagramme BPMN de notre dossier, le travail en attente à chaque étape et le suivi d'un avis dans le processus.") +
    `<div class='cols'><div class='card'><h2>Diagramme BPMN</h2><a href='img/fig/bpmn-satisfaction.png' target='_blank'><img src='img/fig/bpmn-satisfaction.png' alt='Diagramme BPMN du processus de satisfaction' style='width:100%;border:1px solid #f0f0f3;border-radius:8px'></a></div>
    <div class='card'><h2>Travail en attente</h2>${line("Avis à traiter (Marketing, M2.4)", badge("marketing/avis"), "marketing/avis")}${line("Signalements à analyser (Production, M2.5)", badge("production/qualite"), "production/qualite")}${line("Coûts de garantie à enregistrer (Finance, M2.6)", badge("finance/garantie"), "finance/garantie")}
    <h2 style='margin-top:18px'>Suivre un avis</h2>${sel}${r ? tlReview(r) : ""}</div></div>`);
}

/* ---------- acteurs externes ---------- */
function vBanque() {
  const a = p1(); const os = visOrders();
  const rows = os.map((o) => `<tr><td>${hm(o.created)}</td><td>Apple Distribution International</td><td><b>${o.id}</b></td><td>${eur(o.prix)}</td><td>${o.pay === "Financement" ? "Crédit" : "Carte bancaire"}</td><td>${o.bank === "ok" ? pill("Accordée", "ok") : pill("Refusée", "ko")}</td></tr>`).join("");
  return shell("banque", "", head("", "Acteur externe", [], "Banque : demandes d'autorisation", "Demandes envoyées par la finance d'Apple pour chaque précommande. La réponse est automatique : solde, plafond de la carte ou étude du crédit.") +
    kpis([["Demandes reçues d'Apple", nf(a.recues), "depuis 14 h"], ["Accordées", pct(a.recues - a.annulees, a.recues), ""], ["Refusées", nf(a.annulees), "le client est prévenu par Apple"], ["Délai moyen de réponse", "1,2 s", ""]], 4) +
    `<div class='card'><h2>Dernières demandes</h2><div class='tw'><table><tr><th>Heure</th><th>Commerçant</th><th>Référence</th><th>Montant</th><th>Type</th><th>Réponse</th></tr>${rows}</table></div>
    <div class='note'>La banque ne voit que les données de paiement : ni le détail du client, ni ses autres commandes.</div></div>`);
}
function vDistributeur() {
  const after = now() >= "2026-10-23T09:00"; const extra = S.distSent || 0; const part = DISTRIBS[0][3]; let left = extra;
  const rows = Object.entries(ALLOC_NEO).map(([k, al]) => { let v = Math.round(al * (after ? part : 0)); if (left > 0) { const add = Math.min(left, al - v); v += add; left -= add; } return `<tr><td>${k.replace("|", ", ")}</td><td>${nf(al)}</td><td>${nf(v)}</td><td><b>${nf(al - v)}</b></td></tr>`; }).join("");
  const vend = Math.round(600 * (after ? part : 0)) + extra;
  return shell("distributeur", "", head("", "Acteur externe", [], "Néo Télécom : stock alloué et ventes", "Stock d'iPhone Duo alloué par Apple pour la mise en vente, et ventes déclarées chaque matin à Apple par EDI.") +
    kpis([["Stock alloué par Apple", "600", "reçu le 22 octobre"], ["Vendus", nf(vend), "depuis le 23 octobre"], ["Restant en boutique", nf(600 - vend), ""], ["Relevés envoyés", nf(17 + (S.distSent ? 1 : 0)), "un par jour"]], 4) +
    `<div class='card'><h2>Par configuration</h2><div class='tw'><table><tr><th>Configuration</th><th>Alloué</th><th>Vendus</th><th>Restant</th></tr>${rows}</table></div><div style='margin-top:12px'><button class='btn pri' data-act='releve'>Envoyer le relevé des ventes à Apple (EDI)</button></div></div>`);
}

/* ---------- le projet ---------- */
function vProjet() {
  const L = [["M0", "Accueil du prototype", ""], ["M1.1", "Précommander l'iPhone Duo", "client/precommander"], ["M1.2", "CRM : précommandes reçues", "marketing/precommandes"], ["M1.3", "Finance : contrôle des paiements", "finance/paiements"], ["M1.4", "Production : stock et réservations", "production/stock"], ["M1.5", "Message au client", "client/precommandes"],
    ["M2.1 à M2.3", "Carte QR code, questionnaire, confirmation", "client/avis"], ["M2.4", "CRM : avis reçus par QR code", "marketing/avis"], ["M2.5", "Production : signalements qualité", "production/qualite"], ["M2.6", "Finance : coûts de garantie", "finance/garantie"], ["M2.7", "Tableau de bord de satisfaction", "marketing/satisfaction"]];
  return shell(ui.actor, "projet", head("", "Le projet", [], "Prototype du SI marketing et ventes d'Apple", "Projet de TD de Fondamentaux des systèmes d'information · L2 Gestion et Management, IAE Lyon · groupe 12 : Adam, Romy, Anna et Clara.") +
    `<div class='cols'><div class='card'><h2>Les maquettes du dossier <small>chaque écran s'ouvre comme dans le dossier, puis reste cliquable</small></h2>${L.map(([c, t, h]) => `<a class='scr' href='#/${h}'><b>${c.length > 4 ? c.slice(0, 4) : c}</b><span>${t}</span><i>${c}</i></a>`).join("")}
    <div class='note'>Toutes les données sont fictives. Les actions faites dans la démonstration sont gardées dans ce navigateur ; « Recommencer la démonstration » remet les écrans dans l'état des maquettes.</div></div>
    <div class='card' style='text-align:center'><h2>Accès direct</h2><img src='img/qr-site.svg' alt='QR code du site' style='width:170px;height:170px;margin:8px auto;display:block'><div style='font-size:12.5px;color:#6e6e73'>${SITE_URL}</div></div></div>`);
}

/* ---------- routeur ---------- */
const LEGACY = { boutique: "client/precommander", compte: "client/precommandes", carte: "client/avis", "avis-merci": "client/avis", "si/vendeur/precommandes": "marketing/precommandes", "si/vendeur/clients": "marketing/clients", "si/vendeur/distributeurs": "marketing/distributeurs", "si/conseiller/avis": "marketing/avis", "si/conseiller/suivi": "marketing/suivi", "si/marketing/satisfaction": "marketing/satisfaction", "si/marketing/lancement": "marketing/lancement", "si/marketing/campagnes": "marketing/plan", "si/stock/stock": "production/stock", "si/stock/plan": "production/fabrication", "si/qualite/qualite": "production/qualite", "si/controleur/paiements": "finance/paiements", "si/controleur/garantie": "finance/garantie", "si/controleur/ca": "finance/budgets" };
function route() {
  const raw = location.hash.replace(/^#/, "") || "/"; const path = raw.split("?")[0]; const seg = path.split("/").filter(Boolean);
  document.body.classList.toggle("solo", seg[0] === "avis");
  const lg = LEGACY[seg.slice(0, 3).join("/")] || LEGACY[seg[0]] || (seg[0] === "si" ? "" : null);
  if (lg !== null && lg !== undefined) { location.replace("#/" + lg); return null; }
  if (!seg.length) { REF = T16; return [vHome(), "Accueil"]; }
  if (seg[0] === "avis") { REF = SCR.client.avis[1]; ui.actor = "client"; return [vAvisClient(seg[1]), "Votre avis"]; }
  if (ACTEURS[seg[0]]) {
    const a = seg[0]; const k = SCR[a][seg[1]] ? seg[1] : ACTEURS[a].ecrans[0]; const d = SCR[a][k];
    REF = d[1]; ui.actor = a; return [d[2](), d[0] + " · " + ACTEURS[a].nom];
  }
  if (seg[0] === "vue" && VUE[seg[1]]) { REF = VUE[seg[1]][1]; return [seg[1] === "flux" ? vFlux() : vProc(seg[1]), VUE[seg[1]][0]]; }
  if (seg[0] === "partenaire") { if (seg[1] === "distributeur") { REF = "2026-11-09T09:41"; return [vDistributeur(), "Néo Télécom · espace partenaire"]; } REF = T16; return [vBanque(), "Banque · autorisations"]; }
  if (seg[0] === "projet") { REF = T16; return [vProjet(), "Le projet"]; }
  REF = T16; return [vHome(), "Accueil"];
}
function render(keepScroll) {
  const r = route(); if (!r) return;
  const [html, title] = r;
  $app().innerHTML = html; document.title = title + " · iPhone Duo";
  const h = location.hash.split("?")[0];
  if (!keepScroll && h !== lastRoute) window.scrollTo(0, 0);
  lastRoute = h;
}
function rerender() { save(); render(true); }

/* ---------- actions ---------- */
function dropScript(ref) {
  const q = "Q-" + ref.slice(2);
  if (S.reviews[ref] && S.reviews[ref].script) delete S.reviews[ref];
  if (S.signals[q] && S.signals[q].script) delete S.signals[q];
  if (S.costs[q] && S.costs[q].script) delete S.costs[q];
}
function touchReview(ref) { const r = S.reviews[ref]; if (r && r.script) { r.script = false; if (r.order) S.reviewed[r.order] = ref; } }
function newOrderId(t) { S.seq++; return "W" + (t < T16 ? 150040 + S.seq : 153010 + S.seq * 7); }
document.addEventListener("click", (e) => {
  const el = e.target.closest("[data-act]");
  if (!el) return;
  const a = el.dataset.act; const id = el.dataset.id;
  if (["bank", "trk", "qtxt", "crtxt", "notetxt"].includes(a)) return; // gérés par « change » ou « input »
  if (el.disabled) return;
  const o = S.orders[id], r = S.reviews[id], q = S.signals[id];
  switch (a) {
    case "reset": if (confirm("Remettre tous les écrans dans l'état des maquettes ?")) { S = seed(); ui.sel = {}; ui.q = Q0(); ui.dossier = false; ui.crOpen = false; ui.erp = false; save(); toast("Démonstration remise à zéro"); render(true); } return;
    case "cfg": ui.cfg[el.dataset.k] = el.dataset.v; return render(true);
    case "offres": S.offres.lea = !offresDe("lea"); toast(S.offres.lea ? "Accord enregistré pour les offres personnalisées" : "Accord retiré pour les offres personnalisées"); return rerender();
    case "order": {
      const c = ui.cfg; const t = stamp(1); const nid = newOrderId(t);
      S.orders[nid] = { id: nid, cli: "lea", cap: c.cap, col: c.col, prix: prixDe(c.cap), pay: c.pay, bank: S.bank, created: t, hist: [{ t, s: "controle", x: null }], h0: [], serial: null, u: true };
      ui.sel.o = nid; save(); toast(`Précommande ${nid} envoyée au CRM · la finance contrôle le paiement`); location.hash = "#/client/precommandes"; return;
    }
    case "selo": ui.sel.o = id; return render(true);
    case "selc": ui.sel.c = id; ui.note = ""; return render(true);
    case "selr": ui.sel.r = id; ui.cr = ""; ui.crOpen = false; return render(true);
    case "selq": ui.sel.q = id; return render(true);
    case "openr": ui.sel.r = id; location.hash = "#/marketing/avis"; return;
    case "accepter": step(o, "payee"); ui.sel.o = id; toast(`Paiement de ${id} accepté · la précommande passe à la production`); return rerender();
    case "refuser": step(o, "refusee"); ui.sel.o = id; toast(`Paiement de ${id} refusé · le marketing doit informer le client`); return rerender();
    case "reserver": {
      if (dispoCfg(o.cap, o.col)) { step(o, "reservee", { date: "2026-10-23", lot: LOTS[Math.floor(Math.random() * LOTS.length)] }); o.serial = o.serial || "••••••" + Math.random().toString(36).slice(2, 6).toUpperCase(); toast(`Appareil réservé pour ${id} · livraison le 23 octobre`); }
      else { step(o, "reservee", { date: JANV, lot: "Fabrication à venir" }); toast(`Date recalculée pour ${id} · livraison le 25 janvier 2027`); }
      ui.sel.o = id; return rerender();
    }
    case "confirmer": step(o, "confirmee"); ui.sel.o = id; toast(`Confirmation envoyée au client pour ${id}`); return rerender();
    case "informerrefus": step(o, "annulee"); ui.sel.o = id; toast(`Message de refus envoyé au client pour ${id}`); return rerender();
    case "qnote": ui.q.note = Number(el.dataset.v); return render(true);
    case "qmotif": ui.q.motif = el.dataset.v; return render(true);
    case "qaccord": ui.q.accord = !ui.q.accord; return render(true);
    case "sendavis": {
      const qq = ui.q; if (qq.note === null || !qq.motif) return;
      const oid = id; const ord = S.orders[oid];
      if (oid === "W150032") dropScript("R-0412");
      const t = stamp(2);
      const ref = oid === "W150032" && !S.reviews["R-0412"] ? "R-0412" : "R-" + String(S.rseq++).padStart(4, "0");
      const accord = !!qq.accord;
      const st = !accord ? "statistique" : qq.note >= 7 ? "remercie" : DEFAUTS.includes(qq.motif) ? "defaut" : "a_recontacter";
      S.reviews[ref] = { ref, cli: accord ? ord.cli : null, order: accord ? oid : null, canal: "Coffret (après achat)", t, note: qq.note, motif: qq.motif, accord, txt: qq.txt.trim(), hist: [{ t, s: st, x: null }], h0: [], b: false, script: false };
      S.reviewed[oid] = ref;
      ui.q = Q0(); ui.dossier = false; ui.sel.r = ref; toast(`Réponse ${ref} enregistrée dans le CRM`); return rerender();
    }
    case "dossier": ui.dossier = true; return render(true);
    case "retour": ui.dossier = false; return render(true);
    case "transmettre": {
      const qid = "Q-" + r.ref.slice(2);
      if (S.signals[qid] && S.signals[qid].script) { delete S.signals[qid]; if (S.costs[qid] && S.costs[qid].script) delete S.costs[qid]; }
      touchReview(r.ref);
      const t = step(r, "en_analyse", null, 15);
      const ord = r.order && S.orders[r.order]; const i = ord ? oInfo(ord) : {}; const cfg = r.order ? orderCfg(r.order) : null;
      const lot = i && i.lot && i.lot.startsWith("L-") ? i.lot : "L-2643-B";
      const charn = isCharn(r.motif);
      S.signals[qid] = { id: qid, rev: r.ref, defaut: r.txt && r.txt.length < 40 ? r.txt : charn ? "Jeu dans la charnière" : "Problème d'écran ou de pliure", lot, serial: (ord && ord.serial) || "••••••" + Math.random().toString(36).slice(2, 6).toUpperCase(), cfg: cfg ? `iPhone Duo ${cfg[0]}, ${cfg[1]}` : "iPhone Duo", diag: charn ? "Diagnostic à distance : couple de serrage de la charnière hors tolérance. Contrôle en magasin proposé au client." : "Diagnostic à distance : marque visible sur le pli de l'écran intérieur. Contrôle en magasin proposé au client.", t, hist: [{ t, s: "analyse", x: null }], b: false, script: false };
      ui.sel.q = qid; toast(`Signalement ${qid} créé dans l'ERP · transmis à la production`); return rerender();
    }
    case "cropen": ui.crOpen = !ui.crOpen; return render(true);
    case "recontacte": {
      const i = rInfo(r); const txt = ui.cr.trim();
      touchReview(r.ref);
      if (i.s === "a_recontacter") step(r, "recontacte", { cr: txt });
      if (r.cli) (S.notes[r.cli] = S.notes[r.cli] || []).push({ t: i.s === "a_recontacter" ? now() : stamp(1), txt: `Recontact au sujet de ${r.ref}${txt ? " : " + txt : ""}` });
      ui.cr = ""; ui.crOpen = false; toast("Recontact enregistré dans la fiche client"); return rerender();
    }
    case "informer": touchReview(r.ref); step(r, "clos"); toast("Client informé · dossier clos"); return rerender();
    case "confirmerq": {
      const [act, cout] = proposition(q);
      if (S.costs[q.id] && S.costs[q.id].script) delete S.costs[q.id];
      touchReview(q.rev); if (q.b) q.userConf = true;
      const t = step(q, "confirme", { action: act, cout }, 7);
      S.costs[q.id] = { id: q.id, t, action: act, cout, hist: [{ t, s: "a_enregistrer", x: null }], b: false, script: false };
      toast(`Défaut confirmé · coût de ${eur(cout)} transmis à la finance`); return rerender();
    }
    case "nonq": {
      if (S.costs[q.id] && S.costs[q.id].script) delete S.costs[q.id];
      touchReview(q.rev); step(q, "non_confirme");
      const rv = S.reviews[q.rev]; if (rv) step(rv, "a_informer", null, 0);
      toast("Défaut non confirmé · le marketing informe le client"); return rerender();
    }
    case "enregistrer": {
      const c = S.costs[id]; const sg = S.signals[id]; if (sg) touchReview(sg.rev);
      step(c, "enregistre"); const rv = sg && S.reviews[sg.rev]; if (rv && rInfo(rv) && rInfo(rv).s === "en_analyse") step(rv, "a_informer", null, 0);
      toast(`Coût de ${eur(c.cout)} enregistré dans l'ERP`); return rerender();
    }
    case "erp": ui.erp = !ui.erp; return render(true);
    case "addnote": { const txt = ui.note.trim(); if (!txt) return; (S.notes[id] = S.notes[id] || []).push({ t: now(), txt }); ui.note = ""; toast("Note ajoutée à la fiche"); return rerender(); }
    case "jf": ui.jf = id; return render(true);
    case "releve": S.distSent = (S.distSent || 0) + 23; S.flog.push({ t: stamp(1), de: "Distributeurs", vers: "Marketing et ventes", info: "Relevé des ventes de Néo Télécom (23 appareils)", outil: "EDI", ref: "A3-13 · A1-3", proc: "" }); toast("Relevé envoyé à Apple par EDI"); return rerender();
    case "retirer": touchReview(id); r.accord = false; r.cli = null; toast("Accord retiré · la réponse devient anonyme"); return rerender();
    case "supprimer": if (confirm("Supprimer définitivement cette réponse ?")) { touchReview(id); S.deleted[id] = true; ui.dossier = false; toast("Réponse supprimée"); rerender(); } return;
  }
});
document.addEventListener("change", (e) => {
  const el = e.target.closest("[data-act]"); if (!el) return;
  const a = el.dataset.act;
  if (a === "bank") { S.bank = el.value; save(); toast(el.value === "ok" ? "La banque accordera le paiement" : "La banque refusera le paiement"); }
  if (a === "trk") { location.hash = `#/${location.hash.split("?")[0].replace(/^#\//, "")}?${el.dataset.k}=${el.value}`; }
});
document.addEventListener("input", (e) => {
  const el = e.target.closest("[data-act]"); if (!el) return;
  if (el.dataset.act === "qtxt") ui.q.txt = el.value;
  if (el.dataset.act === "crtxt") ui.cr = el.value;
  if (el.dataset.act === "notetxt") ui.note = el.value;
});
window.addEventListener("hashchange", () => render(false));
render(false);
