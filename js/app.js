"use strict";
/* SI marketing et ventes · iPhone Duo — prototype (données fictives, enregistrées dans le navigateur) */

const KEY = "si-iphone-duo-v1";
const JANV = "2027-01-25";
const T = (x) => (x.length === 5 ? "2026-10-16T" + x : x);
const esc = (s) => String(s == null ? "" : s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const nf = (n) => Math.round(n).toLocaleString("fr-FR");
const eur = (n) => nf(n) + " €";
const meur = (n) => (n / 1e6).toLocaleString("fr-FR", { maximumFractionDigits: 1, minimumFractionDigits: 1 }) + " M€";
const pct = (a, b) => (b ? Math.round((a / b) * 100) : 0) + " %";
const dec1 = (x) => x.toLocaleString("fr-FR", { maximumFractionDigits: 1, minimumFractionDigits: 1 });
const D = (iso) => new Date(iso.slice(0, 10) + "T12:00:00");
const dLong = (iso) => D(iso).toLocaleDateString("fr-FR", { weekday: "long", day: "numeric", month: "long", year: "numeric" });
const dMed = (iso) => D(iso).toLocaleDateString("fr-FR", { day: "numeric", month: "long", year: "numeric" });
const dShort = (iso) => D(iso).toLocaleDateString("fr-FR", { day: "numeric", month: "short" });
const hm = (iso) => iso.slice(11, 16);
const quand = (iso) => (iso.slice(0, 10) === now().slice(0, 10) ? hm(iso) : iso.slice(8, 10) + "/" + iso.slice(5, 7) + " " + hm(iso));
const pill = (t, c) => `<span class="pill ${c}">${t}</span>`;
function addMin(iso, m) { const d = new Date(iso + ":00Z"); d.setUTCMinutes(d.getUTCMinutes() + m); return d.toISOString().slice(0, 16); }

/* ---------- état ---------- */
let S;
function seed() {
  const s = { v: 1, clock: "t1", tick: { t1: 0, t2: 0, t3: 0 }, seq: { t1: 0, t2: 0, t3: 0 }, rseq: 412, orders: {}, reviews: {}, signals: {}, costs: {}, msgs: [], notes: {}, offres: {}, reviewed: {}, deleted: {} };
  SEED_ORDERS.forEach(([id, cli, cap, col, pay, bank, t0, hist, serial]) => {
    const h = hist.map(([t, st, x]) => ({ t: T(t), s: st, x: x || null }));
    s.orders[id] = { id, cli, cap, col, prix: prixDe(cap), pay, bank, created: T(t0), hist: h, h0: JSON.parse(JSON.stringify(h)), serial: serial ? "••••••" + serial : null, u: false };
  });
  SEED_REVIEWS.forEach(([ref, cli, order, canal, t, note, motif, accord, txt, hist]) => {
    s.reviews[ref] = { ref, cli, order, canal, t, note, motif, accord, txt, hist: hist.map(([tt, st]) => ({ t: tt, s: st, x: null })), u: false };
  });
  SEED_SIGNALS.forEach(([id, rev, defaut, lot, serial, hist]) => {
    s.signals[id] = { id, rev, defaut, lot, serial, t: hist[0][0], hist: hist.map(([tt, st, x]) => ({ t: tt, s: st, x: x || null })), u: false };
  });
  SEED_COSTS.forEach(([q, t]) => {
    const c = s.signals[q].hist.find((h) => h.s === "confirme");
    s.costs[q] = { id: q, t: c.t, action: c.x.action, cout: c.x.cout, hist: [{ t: c.t, s: "a_enregistrer", x: null }].concat(t ? [{ t, s: "enregistre", x: null }] : []), u: false };
  });
  s.msgs = [
    { t: "2026-10-16T14:03", titre: "Votre précommande est confirmée", corps: "Commande W150032 · iPhone Duo 512 Go, Ciel nocturne. Un appareil du stock de lancement vous est réservé : livraison le vendredi 23 octobre 2026.", lien: "#/compte/commandes" },
    { t: "2026-10-23T10:00", titre: "Votre iPhone Duo est livré", corps: "Commande W150032. Une carte avec un QR code se trouve dans le coffret si vous souhaitez nous donner votre avis.", lien: "#/compte/commandes" },
    { t: "2026-11-07T09:00", titre: "Votre avis sur l'iPhone Duo", corps: "Vous utilisez votre iPhone Duo depuis deux semaines. Trois questions, deux minutes.", lien: "#/avis/W150032" },
  ];
  return s;
}
function load() { try { const x = JSON.parse(localStorage.getItem(KEY)); if (x && x.v === 1) return x; } catch (e) { /* stockage indisponible */ } return seed(); }
function save() { try { localStorage.setItem(KEY, JSON.stringify(S)); } catch (e) { /* stockage indisponible */ } }
S = load();

const C = () => CLOCKS[S.clock];
const now = () => addMin(C().base, S.tick[S.clock]);
function stamp() { S.tick[S.clock]++; return now(); }
function at(hist, t) { let r = null; hist.forEach((h) => { if (h.t <= t) r = h; }); return r; }
function step(obj, s, x) {
  const t0 = now();
  obj.hist = obj.hist.filter((h) => h.t <= t0);
  const t = stamp();
  obj.hist.push({ t, s, x: x || null });
  return t;
}
function msg(titre, corps, lien) { S.msgs.push({ t: now(), titre, corps, lien: lien || "" }); }
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
const visOrders = () => Object.values(S.orders).filter((o) => o.created <= now()).sort((a, b) => (a.created < b.created ? 1 : -1));
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
  const a = Object.assign({}, AGG[S.clock]); const t = now(); const resCfg = {};
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
function stockTable() {
  const a = p1();
  return Object.keys(STOCK).map((k) => {
    const res = S.clock === "t1" ? Math.min(STOCK[k], RES_T1[k] + (a.resCfg[k] || 0)) : STOCK[k];
    return { k, total: STOCK[k], res, dispo: STOCK[k] - res };
  });
}
const dispoCfg = (cap, col) => C().stock && stockTable().find((r) => r.k === cap + "|" + col).dispo > 0;
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

/* ---------- avis, signalements, coûts ---------- */
const rInfo = (r, t = now()) => (r.t > t || S.deleted[r.ref] ? null : at(r.hist, t));
const visReviews = () => Object.values(S.reviews).filter((r) => rInfo(r)).sort((a, b) => (a.t < b.t ? 1 : -1));
const visSignals = () => Object.values(S.signals).filter((q) => q.t <= now()).sort((a, b) => (a.t < b.t ? 1 : -1));
const visCosts = () => Object.values(S.costs).filter((c) => c.t <= now()).sort((a, b) => (a.t < b.t ? 1 : -1));
const RLAB = {
  defaut: ["Défaut signalé", "ko"], a_recontacter: ["À recontacter", "wait"], remercie: ["Remercié", "ok"], statistique: ["Statistique", "grey"],
  en_analyse: ["En cours de traitement", "info"], a_informer: ["Suite à donner", "wait"], recontacte: ["Recontacté", "ok"], clos: ["Clos · client informé", "ok"],
};
const rPill = (s) => pill(RLAB[s][0], RLAB[s][1]);
const qPill = (s) => ({ analyse: pill("À analyser", "wait"), confirme: pill("Défaut confirmé", "ko"), non_confirme: pill("Non confirmé", "grey") }[s]);
const cPill = (s) => ({ a_enregistrer: pill("À enregistrer", "wait"), enregistre: pill("Enregistré", "ok") }[s]);
const cliMail = (cli) => (cli && CLIENTS[cli] ? CLIENTS[cli].mail : "Réponse anonyme");
const cliNom = (cli) => (cli && CLIENTS[cli] ? CLIENTS[cli].nom : "Réponse anonyme");

function sat() {
  const t = now(); const us = Object.values(S.reviews).filter((r) => r.u && rInfo(r, t));
  const s = JSON.parse(JSON.stringify(SAT));
  let sum = SAT.moy * SAT.rep, sumJ = SAT.jour.moy * SAT.jour.rep;
  us.forEach((r) => {
    s.rep++; sum += r.note; s.jour.rep++; sumJ += r.note;
    if (!r.accord) s.jour.anonymes++;
    if (r.note >= 7) s.satis++; else { s.motifs[r.motif]++; s.jour.insatisfaits++; }
  });
  s.moy = sum / s.rep; s.jour.moy = sumJ / s.jour.rep;
  // tâches et défauts créés pendant la démonstration
  Object.values(S.reviews).forEach((r) => {
    const i = rInfo(r, t); if (!i || !r.u) return;
    if (i.s === "a_recontacter") s.jour.recontacter++;
  });
  Object.values(S.signals).forEach((q) => {
    if (q.t > t) return;
    if (q.u) { s.defauts++; s.jour.transmis++; }
    const i = at(q.hist, t); const orig = q.u ? null : at(SEED_SIGNALS.find((x) => x[0] === q.id)[5].map(([tt, st]) => ({ t: tt, s: st })), t);
    if (i && i.s === "confirme" && (!orig || orig.s !== "confirme")) s.confirmes++;
  });
  Object.values(S.costs).forEach((c) => {
    if (c.t > t) return;
    const i = at(c.hist, t); const seedC = SEED_COSTS.find((x) => x[0] === c.id);
    const wasRec = seedC && seedC[1] && seedC[1] <= t;
    if (i.s === "enregistre" && !wasRec) s.couts += c.cout;
  });
  return s;
}

/* ---------- tâches en attente ---------- */
function tasks() {
  const t = now(); const n = { paiements: 0, stock: 0, precommandes: 0, avis: 0, qualite: 0, garantie: 0 };
  visOrders().forEach((o) => { const i = oInfo(o, t); if (i.s === "controle") n.paiements++; if (i.s === "payee") n.stock++; if (i.s === "reservee" || i.s === "refusee") n.precommandes++; });
  visReviews().forEach((r) => { const i = rInfo(r, t); if (["defaut", "a_recontacter", "a_informer"].includes(i.s)) n.avis++; });
  visSignals().forEach((q) => { if (at(q.hist, t).s === "analyse") n.qualite++; });
  visCosts().forEach((c) => { if (at(c.hist, t).s === "a_enregistrer") n.garantie++; });
  return n;
}

/* ---------- interface commune ---------- */
let ui = { sel: {}, cfg: { cap: "512 Go", col: "Ciel nocturne", pay: "Carte bancaire", bank: "ok" }, q: { note: null, motif: null, txt: "", accord: false }, clockOpen: false, cr: "", act: 0, note: "" };
let lastRoute = "";
const $app = () => document.getElementById("app");
function toast(t) {
  let el = document.querySelector(".toast"); if (!el) { el = document.createElement("div"); el.className = "toast"; document.body.appendChild(el); }
  el.textContent = t; el.classList.add("on"); clearTimeout(el._h); el._h = setTimeout(() => el.classList.remove("on"), 2600);
}
function clockBox() {
  const items = Object.values(CLOCKS).map((c) => `<button data-act="setclock" data-id="${c.id}" class="${c.id === S.clock ? "on" : ""}">${c.titre}<small>${c.legende}</small></button>`).join("");
  return `<div class="clock ${ui.clockOpen ? "open" : ""}"><button data-act="clock" title="Moment de la démonstration"><span>Démonstration : </span><b>${C().court}</b> ▾</button>
  <div class="menu"><div class="lab">Moment de la démonstration</div>${items}<hr><button class="reset" data-act="reset">Réinitialiser les données de démonstration</button></div></div>`;
}
function topbar(on) {
  const L = [["#/", "Accueil", "home"], ["#/boutique", "Boutique", "shop"], ["#/compte", "Mon compte", "acc"], ["#/si", "Outils internes", "si"], ["#/projet", "Le projet", "proj"]];
  return `<header class="top"><a class="logo" href="#/">iPhone Duo<small>SI marketing et ventes</small></a>
  <nav>${L.map(([h, t, k]) => `<a href="${h}" class="${on === k ? "on" : ""}">${t}</a>`).join("")}</nav>${clockBox()}</header>`;
}
const foot = () => `<footer class="foot">Projet de TD · Fondamentaux des systèmes d'information · L2 Gestion et Management, IAE Lyon, 2026-2027. Prototype universitaire, sans lien avec Apple Inc. Les clients, commandes et chiffres internes sont fictifs ; ils sont enregistrés seulement dans votre navigateur. <a href="#/projet">Le projet</a></footer>`;
const page = (on, body) => topbar(on) + body + foot();

/* ---------- accueil ---------- */
function vHome() {
  const P1 = [["Précommander l'iPhone Duo", "Client", "#/boutique"], ["Accepter le paiement", "Finance", "#/si/controleur/paiements"], ["Réserver un appareil", "Production", "#/si/stock/stock"], ["Confirmer au client", "Ventes", "#/si/vendeur/precommandes"], ["Lire la confirmation", "Client", "#/compte/messages"]];
  const P2 = [["Donner son avis (QR code du coffret)", "Client", "#/carte"], ["Transmettre le défaut", "Relation client", "#/si/conseiller/avis"], ["Analyser le signalement", "Production", "#/si/qualite/qualite"], ["Enregistrer le coût de garantie", "Finance", "#/si/controleur/garantie"], ["Informer le client, suivre la satisfaction", "Relation client · Marketing", "#/si/marketing/satisfaction"]];
  const li = (a) => a.map(([t, w, h]) => `<li><a href="${h}">${t}</a><span>${w}</span></li>`).join("");
  return page("home", `<main class="wrap">
  <h1>Le SI marketing et ventes du lancement de l'iPhone Duo</h1>
  <p class="lead">La boutique en ligne côté client et les outils internes de la vente, de la relation client, du marketing, de la production et de la finance. Les informations passent d'un service à l'autre au fil des deux processus étudiés dans notre dossier.</p>
  <div class="grid2">
   <a class="tile" href="#/boutique"><div class="k">Côté client</div><h2>Boutique en ligne</h2><p>Configurer et précommander l'iPhone Duo, suivre sa commande, répondre au questionnaire de satisfaction.</p><span class="go">Ouvrir la boutique ›</span></a>
   <a class="tile" href="#/si"><div class="k">Côté entreprise</div><h2>Outils internes</h2><p>Six profils de salariés et deux partenaires externes (banque, distributeur). Chacun ne voit que les écrans et les données dont il a besoin.</p><span class="go">Se connecter ›</span></a>
  </div>
  <div class="grid2" style="margin-top:16px">
   <div class="tile"><div class="k">Processus 1</div><h2>De la précommande à la confirmation</h2><ol class="steps-list">${li(P1)}</ol></div>
   <div class="tile"><div class="k">Processus 2</div><h2>La satisfaction mesurée par QR code</h2><ol class="steps-list">${li(P2)}</ol></div>
  </div>
  <p class="small muted" style="margin-top:18px">Le bouton « Démonstration » en haut à droite place le système à un moment du lancement : l'ouverture des précommandes (16 octobre, 14:10), le stock épuisé (14:35) ou après les livraisons (9 novembre).</p>
  </main>`);
}

/* ---------- boutique ---------- */
function vShop() {
  const c = ui.cfg; const dispo = dispoCfg(c.cap, c.col); const date = dispo ? "2026-10-23" : JANV;
  const after = now() >= "2026-10-23";
  const opt = (k, v, title, sub, extra = "") => `<button class="opt ${c[k] === v ? "on" : ""}" data-act="cfg" data-k="${k}" data-v="${esc(v)}">${extra}<b>${title}</b><span>${sub}</span></button>`;
  return page("shop", `<main class="wrap">
  <section class="hero"><div class="new">${after ? "Disponible" : "Précommandes ouvertes"}</div><h1>iPhone Duo</h1><p>Fermé, un iPhone. Ouvert, presque une tablette.</p>
   <img src="img/duo.jpg" alt="iPhone Duo fermé et ouvert"><div class="price">À partir de 2 339 € · ${after ? "en vente depuis le 23 octobre" : "mise en vente le 23 octobre 2026"}</div></section>
  <div class="facts"><div class="fact"><b>5,4 pouces</b><span>écran extérieur</span></div><div class="fact"><b>7,6 pouces</b><span>écran intérieur, ouvert</span></div><div class="fact"><b>Titane</b><span>cadre et couvre-charnière</span></div><div class="fact"><b>256 Go à 2 To</b><span>quatre capacités</span></div></div>
  <div class="buy">
   <div class="panel"><h2>Configurez votre iPhone Duo</h2><p class="muted small">Connecté en tant que Léa M. · <a href="#/compte">mon compte</a></p>
    <div class="lab">Capacité</div><div class="opts four">${CAPS.map((x) => opt("cap", x.cap, x.cap, eur(x.prix))).join("")}</div>
    <div class="lab">Couleur</div><div class="opts">${COLS.map((x) => opt("col", x.col, x.col, dispoCfg(c.cap, x.col) ? "Livraison le 23 octobre" : "Livraison le 25 janvier 2027", `<span class="sw" style="background:${x.hex}"></span>`)).join("")}</div>
    <div class="lab">Paiement</div><div class="opts">${opt("pay", "Carte bancaire", "Carte bancaire", "Débit à l'expédition")}${opt("pay", "Financement", "Financement", "Sous réserve d'acceptation")}</div>
    <label class="chk"><input type="checkbox" data-act="offres" ${offresDe("lea") ? "checked" : ""}><span>J'accepte de recevoir des offres personnalisées (facultatif).</span></label>
    <div class="demo">Environnement de démonstration · réponse de ${c.pay === "Financement" ? "l'organisme de crédit" : "la banque"} :
     <select data-act="bank"><option value="ok" ${c.bank === "ok" ? "selected" : ""}>accordée</option><option value="ko" ${c.bank === "ko" ? "selected" : ""}>refusée</option></select></div>
   </div>
   <div class="panel sum"><h2>Récapitulatif</h2>
    <div class="kv" style="margin-top:12px"><span>Produit</span><b>iPhone Duo ${c.cap}, ${c.col}</b><span>Prix TTC</span><b>${eur(prixDe(c.cap))}</b><span>Paiement</span><b>${c.pay}</b><span>Livraison estimée</span><b>${dLong(date)}</b></div>
    ${dispo ? "" : `<div class="box">Le stock de lancement de cette configuration est épuisé. Votre appareil sera réservé sur la fabrication à venir.</div>`}
    <button class="btn pri big" data-act="order">${after ? "Commander" : "Valider la précommande"}</button>
    <p class="legal">Vous pouvez suivre ou annuler votre commande depuis votre compte. Vos données servent à traiter la commande ; les offres personnalisées ne sont envoyées qu'avec votre accord.</p>
   </div></div></main>`);
}
function vMerci(id) {
  const o = S.orders[id]; if (!o) return vShop();
  return page("shop", `<main class="wrap narrow center"><div class="okmark wait">…</div><h1>Précommande enregistrée</h1>
  <p class="muted" style="margin-top:6px">Commande ${o.id} · ${dLong(o.created)}, ${hm(o.created)}</p>
  <div class="panel" style="text-align:left;margin-top:22px"><div class="kv"><span>Produit</span><b>iPhone Duo ${o.cap}, ${o.col}</b><span>Montant</span><b>${eur(o.prix)}</b><span>Paiement</span><b>${o.pay} · en cours de vérification</b></div>
  <p class="small muted" style="margin-top:12px">Vous recevrez dans vos messages la confirmation et la date de livraison dès que le paiement et la réservation de votre appareil seront validés.</p></div>
  <p style="margin-top:18px"><a class="btn pri" href="#/compte/commandes">Suivre ma commande</a><a class="btn" href="#/boutique">Retour à la boutique</a></p>
  <div class="demo" style="text-align:left">Démonstration : la précommande est maintenant dans le CRM et attend la décision de la finance. <a href="#/si/controleur/paiements">Ouvrir le contrôle des paiements ›</a></div></main>`);
}

/* ---------- compte client ---------- */
const CLIENT_LAB = { controle: "Paiement en cours de vérification", payee: "Paiement accepté · réservation de votre appareil", reservee: "Appareil réservé · confirmation en cours", refusee: "Paiement refusé", annulee: "Annulée · paiement refusé" };
function vCompte(tab) {
  tab = tab || "commandes";
  const tabs = [["commandes", "Mes commandes"], ["messages", "Messages"], ["avis", "Mes avis"], ["donnees", "Mes données"]];
  let body = "";
  if (tab === "commandes") {
    const os = visOrders().filter((o) => o.cli === "lea");
    body = os.map((o) => {
      const i = oInfo(o); const ann = i.s === "annulee" || i.s === "refusee";
      const lab = i.s === "confirmee" ? `Confirmée · livraison le ${dLong(i.date)}` : i.s === "livree" ? `Livrée le ${dMed(i.date)}` : CLIENT_LAB[i.s];
      const stp = ["Commande passée", "Paiement accepté", "Confirmée", "Livrée"]; const idx = { controle: 0, payee: 1, reservee: 1, confirmee: 2, livree: 3 }[i.s];
      const track = ann ? "" : `<div class="track">${stp.map((x, k) => `<div class="${k < idx ? "done" : k === idx ? "cur" : ""}">${x}</div>`).join("")}</div>`;
      const avis = i.s === "livree" ? (S.reviewed[o.id] ? `<span class="small muted">Avis envoyé · merci</span>` : `<a class="btn pri sm" href="#/avis/${o.id}">Donner mon avis</a>`) : "";
      return `<div class="order"><div class="hd"><div><b>iPhone Duo ${o.cap}, ${o.col}</b><div class="small muted">Commande ${o.id} · ${dMed(o.created)} · ${eur(o.prix)}</div></div>${ann ? pill("Annulée", "ko") : ""}</div>
      <div>${esc(lab)}</div>${track}${avis}</div>`;
    }).join("") || `<div class="empty">Aucune commande.</div>`;
  } else if (tab === "messages") {
    body = S.msgs.filter((m) => m.t <= now()).sort((a, b) => (a.t < b.t ? 1 : -1)).map((m) => `<div class="msg"><div class="when">${dMed(m.t)} · ${hm(m.t)}</div><b>${esc(m.titre)}</b><div class="small">${esc(m.corps)}</div>${m.lien ? `<div style="margin-top:8px"><a href="${m.lien}">Voir ›</a></div>` : ""}</div>`).join("") || `<div class="empty">Aucun message.</div>`;
  } else if (tab === "avis") {
    const rs = visReviews().filter((r) => r.cli === "lea");
    body = rs.map((r) => {
      const i = rInfo(r);
      const suite = { remercie: "Merci pour votre avis.", a_recontacter: "Un conseiller va vous recontacter.", defaut: "Un conseiller étudie votre signalement.", en_analyse: "Votre signalement est en cours d'analyse.", a_informer: "Une solution vous sera proposée très bientôt.", recontacte: "Un conseiller vous a recontactée.", clos: "Une solution vous a été proposée (voir vos messages)." }[i.s] || "";
      return `<div class="order"><div class="hd"><div><b>Avis ${r.ref} · ${r.note}/10 · ${esc(r.motif)}</b><div class="small muted">Commande ${r.order} · ${dMed(r.t)}</div></div></div>
      ${r.txt ? `<div class="quote">« ${esc(r.txt)} »</div>` : ""}<div class="small">${suite}</div>
      <div style="margin-top:10px"><button class="btn sm" data-act="retirer" data-id="${r.ref}">Retirer mon accord pour être recontactée</button><button class="btn sm red" data-act="supprimer" data-id="${r.ref}">Supprimer ma réponse</button></div></div>`;
    }).join("") || `<div class="empty">Vous n'avez pas encore donné d'avis rattaché à votre compte. Les réponses envoyées sans accord sont anonymes et n'apparaissent pas ici.</div>`;
  } else {
    body = `<div class="order"><b>Léa M.</b><div class="small muted">l••.m•••••@icloud.com · Lyon 3e · cliente depuis 2019</div>
    <label class="chk"><input type="checkbox" data-act="offres" ${offresDe("lea") ? "checked" : ""}><span>Recevoir des offres personnalisées</span></label></div>
    <div class="order"><b>Ce que nous conservons</b><div class="small" style="margin-top:6px">Votre compte et vos coordonnées, vos commandes et leur paiement, vos réponses au questionnaire si vous avez accepté d'être recontactée. Vous pouvez retirer un accord ou supprimer une réponse depuis « Mes avis ».</div></div>`;
  }
  return page("acc", `<main class="wrap"><h1>Mon compte</h1><p class="lead" style="margin-bottom:18px">Léa M. · compte de démonstration</p>
  <div class="acc"><div class="tabs">${tabs.map(([k, t]) => `<a href="#/compte/${k}" class="${k === tab ? "on" : ""}">${t}</a>`).join("")}</div><div>${body}</div></div></main>`);
}

/* ---------- questionnaire ---------- */
function vCarte() {
  return page("shop", `<main class="wrap"><div class="qrcard"><div class="crumb">iPhone Duo · votre avis compte</div><h1 style="font-size:24px">Dites-nous ce que vous en pensez</h1>
  <img src="img/qr-avis.svg" alt="QR code du questionnaire"><div class="small">Scannez ce code avec l'appareil photo.<br>Deux minutes, trois questions.</div>
  <p style="margin-top:14px"><a class="btn pri" href="#/avis/W150032?t=t3">Ouvrir le questionnaire</a></p>
  <p class="legal">Carte glissée dans le coffret de l'iPhone Duo de Léa M. (commande W150032). Le même questionnaire est proposé sur les tables de démonstration et dans le courriel envoyé 15 jours après la livraison.</p></div></main>`);
}
function vAvis(id) {
  const o = id ? S.orders[id] : null;
  if (id && !o) return page("shop", `<main class="wrap narrow center"><h1>Commande introuvable</h1></main>`);
  if (o) {
    const i = oInfo(o);
    if (!i || i.s !== "livree") return page("shop", `<main class="wrap narrow center"><div class="okmark wait">⏳</div><h1>Le questionnaire n'est pas encore ouvert</h1>
      <p class="muted" style="margin-top:8px">Il s'ouvre après la livraison de la commande ${o.id}.</p>
      <p style="margin-top:16px"><button class="btn pri" data-act="setclock" data-id="t3">Passer au 9 novembre (démonstration)</button></p></main>`);
    if (S.reviewed[o.id]) return page("shop", `<main class="wrap narrow center"><div class="okmark">✓</div><h1>Vous avez déjà répondu</h1><p class="muted" style="margin-top:8px">Merci. Votre réponse est enregistrée.</p><p style="margin-top:16px"><a class="btn" href="#/compte/avis">Mes avis</a></p></main>`);
  }
  const q = ui.q; const ok = q.note !== null && q.motif;
  return page("shop", `<main class="wrap narrow"><div class="panel">
  <div class="crumb">Étape 1 sur 2</div><h1 style="font-size:24px">Votre avis sur l'iPhone Duo</h1>
  ${o ? `<div class="box"><b>Commande ${o.id}</b> · iPhone Duo ${o.cap}, ${o.col}<br>Livrée le 23 octobre 2026</div>` : `<div class="box">Vous avez essayé l'iPhone Duo en magasin.</div>`}
  <div class="q">1. Quelle note donnez-vous ${o ? "à votre " : "à l'"}iPhone Duo ?</div>
  <div class="scale">${[...Array(11).keys()].map((n) => `<button data-act="qnote" data-v="${n}" class="${q.note === n ? "on" : ""}">${n}</button>`).join("")}</div>
  <div class="scale-leg"><span>pas du tout satisfait</span><span>très satisfait</span></div>
  <div class="q">2. Qu'est-ce qui explique le plus cette note ?</div>
  <div class="chips">${MOTIFS.map((m) => `<button data-act="qmotif" data-v="${esc(m)}" class="${q.motif === m ? "on" : ""}">${m}</button>`).join("")}</div>
  <div class="q">3. Souhaitez-vous préciser ? <span class="muted" style="font-weight:400">(facultatif)</span></div>
  <textarea data-act="qtxt" placeholder="Votre commentaire">${esc(q.txt)}</textarea>
  ${o ? `<label class="chk"><input type="checkbox" data-act="qaccord" ${q.accord ? "checked" : ""}><span>J'accepte d'être recontacté(e) par Apple au sujet de cet avis.</span></label>` : ""}
  <button class="btn pri big" data-act="sendavis" data-id="${o ? o.id : ""}" ${ok ? "" : "disabled"}>Envoyer mon avis</button>
  <p class="legal">${o ? "Si vous acceptez d'être recontacté(e), votre réponse est rattachée à votre commande et vous pouvez la consulter ou la supprimer depuis votre compte. Sinon, elle est enregistrée de façon anonyme et sert seulement aux statistiques." : "Votre réponse est anonyme et sert seulement aux statistiques."}</p>
  </div></main>`);
}
function vAvisMerci(ref) {
  const r = S.reviews[ref]; if (!r) return vHome();
  const i = at(r.hist, "9999");
  const suite = {
    remercie: "Merci ! Votre note nous aide à améliorer nos produits.",
    statistique: "Votre réponse anonyme est prise en compte dans nos statistiques.",
    a_recontacter: "Un conseiller vous recontacte sous 48 heures, par téléphone ou par courriel.",
    defaut: `Vous signalez un problème (${r.motif.toLowerCase()}). Un conseiller vous recontacte sous 48 heures, par téléphone ou par courriel.`,
  }[i.s];
  return page("shop", `<main class="wrap narrow"><div class="panel center"><div class="crumb">Étape 2 sur 2</div><div class="okmark" style="margin-top:12px">✓</div><h1 style="font-size:24px">Merci, votre avis est enregistré</h1>
  <p class="muted small" style="margin-top:6px">Référence ${r.ref} · ${dMed(r.t)}</p>
  <div class="box" style="text-align:left"><b>Et maintenant ?</b><br>${suite}</div>
  <div class="kv" style="text-align:left;margin:12px 0"><span>Votre note</span><b>${r.note} / 10</b><span>Motif</span><b>${esc(r.motif)}</b></div>
  ${r.accord ? `<a class="btn" href="#/compte/avis">Suivre mon avis</a>` : ""}
  <p class="legal">Vous pouvez retirer votre accord, modifier ou supprimer votre réponse à tout moment depuis votre compte.</p></div>
  <div class="demo">Démonstration : la réponse vient d'arriver dans le CRM. <a href="#/si/conseiller/avis">Ouvrir les avis reçus ›</a></div></main>`);
}

/* ---------- outils internes : connexion ---------- */
function vLogin() {
  return page("si", `<main class="wrap login"><h1>Outils internes</h1><p class="lead">Connexion avec un compte salarié et une validation en deux étapes. Choisissez un profil : les menus et les données affichées dépendent de ses autorisations.</p>
  <div class="prof">${Object.entries(PROFILS).map(([k, p]) => `<a href="#/si/connexion/${k}"><div class="av" style="background:${p.couleur}">${p.nom.split(" ").map((x) => x[0]).join("")}</div><b>${p.nom}</b><span>${p.role}</span><div class="small" style="margin-top:8px;color:#424245">${p.ecrans.map((e) => ECRANS[e].t).join(" · ")}</div></a>`).join("")}</div>
  <h2 style="margin:28px 0 4px;font-size:18px">Partenaires externes</h2><p class="muted small" style="margin-bottom:12px">Deux acteurs externes du modèle de contexte, avec leur propre accès.</p>
  <div class="prof">${Object.entries(PARTENAIRES).map(([k, p]) => `<a href="#/partenaire/${k}"><div class="av" style="background:${p.couleur}">${p.nom.split(" ").map((x) => x[0]).join("").slice(0, 2).toUpperCase()}</div><b>${p.nom}</b><span>${p.role}</span><div class="small" style="margin-top:8px;color:#424245">${p.ecran}</div></a>`).join("")}</div></main>`);
}
function vTwoFA(p) {
  const P = PROFILS[p]; if (!P) return vLogin();
  return page("si", `<main class="wrap narrow"><div class="panel center"><div class="av" style="background:${P.couleur};width:48px;height:48px;border-radius:50%;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;margin:0 auto 10px">${P.nom.split(" ").map((x) => x[0]).join("")}</div>
  <h1 style="font-size:22px">Validation en deux étapes</h1><p class="muted small" style="margin-top:6px">${P.nom} · ${P.role}<br>Un code a été envoyé sur votre appareil de confiance.</p>
  <div class="code">${"482913".split("").map((d) => `<div>${d}</div>`).join("")}</div>
  <button class="btn pri big" data-act="login" data-id="${p}">Se connecter</button><p class="legal">Code prérempli pour la démonstration.</p></div></main>`);
}

/* ---------- outils internes : cadre ---------- */
function shell(p, scr, inner) {
  const P = PROFILS[p]; const n = tasks();
  const item = (e) => `<li><a href="#/si/${p}/${e}" class="${e === scr ? "on" : ""}">${ECRANS[e].t}${n[e] ? `<span class="badge">${n[e]}</span>` : ""}</a></li>`;
  return topbar("si") + `<div class="app"><aside class="side"><div class="who"><span>Connecté</span><b>${P.nom}</b><span>${P.role}</span><div style="margin-top:6px"><a href="#/si">Changer de profil</a></div></div>
  <ul class="nav"><li class="sep">Mes écrans</li>${P.ecrans.map(item).join("")}<li class="sep">Entreprise</li>${item("processus")}${item("echanges")}</ul></aside>
  <main class="main">${inner}<p class="hint" style="margin-top:22px">${ECRANS[scr].code ? "Écran " + ECRANS[scr].code + " · " : ""}${C().titre} · données fictives</p></main></div>`;
}
const head = (crumb, title, sub) => `<div class="crumb">${crumb}</div><h1>${title}</h1><div class="sub">${sub}</div>`;
const kpi = (l, v, i) => `<div class="kpi"><span>${l}</span><b>${v}</b><i>${i || ""}</i></div>`;
const kpis = (a) => `<div class="kpis">${a.map((x) => kpi(...x)).join("")}</div>`;
const prog = (labels, idx, bad) => `<div class="prog">${labels.map((l, k) => `<div class="${k < idx ? "done" : k === idx ? (bad ? "bad" : "cur") : ""}">${l}</div>`).join("")}</div>`;

/* Ventes : précommandes (M1.2) */
function sPrecommandes(p) {
  const a = p1(); const os = visOrders(); const sel = S.orders[ui.sel.o] && oInfo(S.orders[ui.sel.o]) ? S.orders[ui.sel.o] : os[0];
  const rows = os.slice(0, 18).map((o) => { const i = oInfo(o); return `<tr class="click ${o === sel ? "sel" : ""}" data-act="selo" data-id="${o.id}"><td>${quand(o.created)}</td><td><b>${o.id}</b></td><td>${cliMail(o.cli)}</td><td>${o.cap}, ${o.col}</td><td>${oPill(i)}</td></tr>`; }).join("");
  let det = "";
  if (sel) {
    const i = oInfo(sel); const cl = CLIENTS[sel.cli];
    const idx = { controle: 1, payee: 2, refusee: 1, reservee: 3, confirmee: 4, livree: 5, annulee: 1 }[i.s];
    const act = i.s === "reservee" ? `<button class="btn pri" data-act="confirmer" data-id="${sel.id}">Confirmer la commande au client</button>` : i.s === "refusee" ? `<button class="btn red" data-act="informerrefus" data-id="${sel.id}">Informer le client du refus</button>` : "";
    const etat = { controle: () => "Paiement transmis à la finance.", payee: () => "Paiement accepté. La production réserve un appareil.", refusee: () => "La finance a refusé le paiement : le client doit être informé.", reservee: () => `Appareil réservé (${i.lot}). Livraison possible le ${dLong(i.date)}.`, confirmee: () => `Client informé : livraison le ${dLong(i.date)}.`, livree: () => "Commande livrée le 23 octobre 2026.", annulee: () => "Précommande annulée, client informé du refus." }[i.s]();
    det = `<div class="card"><h2>Précommande ${sel.id} <small>créée le ${dMed(sel.created)} à ${hm(sel.created)}</small></h2>
    <div class="kv"><span>Client</span><b>${cl.nom} · ${cl.mail}</b><span>Configuration</span><b>iPhone Duo ${sel.cap}, ${sel.col}</b><span>Montant TTC</span><b>${eur(sel.prix)} · ${sel.pay}</b><span>Canal</span><b>Boutique en ligne</b><span>Offres personnalisées</span><b>${offresDe(sel.cli) ? "Acceptées" : "Refusées (case non cochée)"}</b></div>
    ${i.s === "annulee" || i.s === "refusee" ? prog(["Enregistrée", "Paiement refusé", "Client informé"], i.s === "annulee" ? 3 : 1, true) : prog(["Enregistrée", "Paiement", "Réservation", "Confirmée", "Livrée"], idx)}
    <div class="quote" style="font-style:normal">${etat}</div>${act}<div class="small" style="margin-top:6px"><a href="#/si/${p}/processus?o=${sel.id}">Voir l'avancement dans le processus ›</a></div></div>`;
  }
  return shell(p, "precommandes", head("Ventes · CRM", "Précommandes", `France · ${C().titre}. Chaque précommande crée ou complète une fiche client ; son statut suit le paiement puis la réservation.`) +
    kpis([[S.clock === "t3" ? "Précommandes reçues depuis le 16 octobre" : "Précommandes reçues depuis 14 h", nf(a.recues), "France"], ["En contrôle", nf(a.controle), "à la finance"], ["Confirmées", nf(a.confirmees), a.janvier ? `dont ${nf(a.janvier)} livrées en janvier` : "livrées le 23 octobre"], ["Annulées (paiement refusé)", nf(a.annulees), pct(a.annulees, a.recues)], ["Date de livraison annoncée", dShort(C().stock ? "2026-10-23" : JANV), C().stock ? "stock de lancement" : "depuis 14:28"]]) +
    `<div class="cols"><div class="card"><h2>Dernières précommandes <small>adresses masquées à l'affichage</small></h2><div class="tw"><table><tr><th>Heure</th><th>N°</th><th>Client</th><th>Configuration</th><th>Statut</th></tr>${rows}</table></div></div>${det}</div>`);
}

/* Fiches clients */
function sClients(p) {
  const t = now(); const ids = Object.keys(CLIENTS); const selId = CLIENTS[ui.sel.c] ? ui.sel.c : "lea";
  const nb = (cli) => visOrders().filter((o) => o.cli === cli).length;
  const rows = ids.map((k) => { const c = CLIENTS[k]; return `<tr class="click ${k === selId ? "sel" : ""}" data-act="selc" data-id="${k}"><td><b>${c.nom}</b></td><td>${c.mail}</td><td>${c.ville}</td><td>${nb(k)}</td><td>${offresDe(k) ? pill("Oui", "ok") : pill("Non", "grey")}</td></tr>`; }).join("");
  const c = CLIENTS[selId]; const os = visOrders().filter((o) => o.cli === selId);
  const rs = p === "conseiller" ? visReviews().filter((r) => r.cli === selId) : [];
  const notes = (S.notes[selId] || []).filter((n) => n.t <= t);
  const det = `<div class="card"><h2>${c.nom} <small>client depuis ${c.depuis}</small></h2>
  <div class="kv"><span>Courriel</span><b>${c.mail}</b><span>Téléphone</span><b>${c.tel}</b><span>Ville</span><b>${c.ville}</b><span>Offres personnalisées</span><b>${offresDe(selId) ? "Accord donné" : "Pas d'accord"}</b></div>
  <h2 style="margin-top:16px">Commandes</h2>${os.map((o) => `<div class="small" style="padding:5px 0;border-bottom:1px solid #f0f0f3">${o.id} · iPhone Duo ${o.cap}, ${o.col} · ${oPill(oInfo(o))}</div>`).join("") || `<div class="small muted">Aucune commande iPhone Duo.</div>`}
  ${p === "conseiller" ? `<h2 style="margin-top:16px">Avis</h2>${rs.map((r) => `<div class="small" style="padding:5px 0;border-bottom:1px solid #f0f0f3">${r.ref} · ${r.note}/10 · ${esc(r.motif)} · ${rPill(rInfo(r).s)}</div>`).join("") || `<div class="small muted">Aucun avis rattaché.</div>`}` : ""}
  <h2 style="margin-top:16px">Notes</h2>${notes.map((n) => `<div class="small" style="padding:5px 0;border-bottom:1px solid #f0f0f3"><span class="muted">${quand(n.t)} · ${n.par}</span><br>${esc(n.txt)}</div>`).join("") || `<div class="small muted">Aucune note.</div>`}
  <textarea data-act="notetxt" placeholder="Ajouter une note sur ce client" style="margin-top:10px;min-height:60px">${esc(ui.note)}</textarea><button class="btn" style="margin-top:8px" data-act="addnote" data-id="${selId}">Ajouter la note</button></div>`;
  return shell(p, "clients", head(p === "vendeur" ? "Ventes · CRM" : "Relation client · CRM", "Fiches clients", "Une fiche par client, créée à la première commande. Les accords donnés par le client ne se modifient que depuis son compte.") +
    `<div class="cols"><div class="card"><h2>Clients <small>${ids.length} fiches</small></h2><div class="tw"><table><tr><th>Client</th><th>Courriel</th><th>Ville</th><th>Commandes</th><th>Offres</th></tr>${rows}</table></div></div>${det}</div>`);
}

/* Finance : paiements (M1.3) */
function sPaiements(p) {
  const a = p1(); const os = visOrders();
  const rows = os.slice(0, 18).map((o) => {
    const i = oInfo(o); const rep = o.bank === "ok" ? (o.pay === "Financement" ? "Crédit accordé" : "Autorisation accordée") : (o.pay === "Financement" ? "Crédit refusé" : "Autorisation refusée");
    let dec;
    if (i.s === "controle") dec = `<button class="btn pri sm" data-act="accepter" data-id="${o.id}" ${o.bank === "ok" ? "" : "disabled"}>Accepter</button><button class="btn red sm" data-act="refuser" data-id="${o.id}">Refuser</button>`;
    else if (i.s === "refusee") dec = pill("Refusé · ventes à prévenir", "ko");
    else if (i.s === "annulee") dec = pill("Refusé · client informé", "ko");
    else dec = pill("Accepté · CA enregistré", "ok");
    return `<tr class="${i.s === "controle" ? "sel" : ""}"><td>${quand(o.created)}</td><td><b>${o.id}</b></td><td>${eur(o.prix)}</td><td>${o.pay}</td><td>${rep}</td><td>${dec}</td></tr>`;
  }).join("");
  return shell(p, "paiements", head("Finance", "Contrôle des paiements", "Les précommandes enregistrées dans le CRM arrivent ici avec la réponse de la banque ou de l'organisme de crédit.") +
    kpis([["Paiements à contrôler", nf(a.controle), "file d'attente"], ["Paiements acceptés", nf(a.recues - a.controle - a.annulees), "depuis 14 h"], ["Paiements refusés", nf(a.annulees), pct(a.annulees, a.recues)], ["Chiffre d'affaires prévisionnel", meur(a.ca), "TTC, enregistré dans l'ERP"]]) +
    `<div class="card"><h2>Paiements <small>précommandes transmises par les ventes</small></h2><div class="tw"><table><tr><th>Heure</th><th>Précommande</th><th>Montant</th><th>Moyen de paiement</th><th>Réponse</th><th>Décision</th></tr>${rows}</table></div>
    <p class="hint">Un paiement accepté enregistre le chiffre d'affaires prévisionnel et envoie la précommande à la production. Un paiement refusé annule la précommande.</p></div>`);
}

/* Production : stock (M1.4) */
function sStock(p) {
  const a = p1(); const os = visOrders(); const st = stockTable();
  const serve = os.filter((o) => ["payee", "reservee", "confirmee", "livree"].includes(oInfo(o).s)).slice(0, 12);
  const rows = serve.map((o) => {
    const i = oInfo(o); const disp = dispoCfg(o.cap, o.col);
    let res, dispo, date;
    if (i.s === "payee") {
      dispo = disp ? pill("Oui", "ok") : pill("Non", "ko"); date = disp ? "23 octobre 2026" : "25 janvier 2027 (recalculée)";
      res = disp ? `<button class="btn pri sm" data-act="reserver" data-id="${o.id}">Réserver un appareil</button>` : `<button class="btn pri sm" data-act="reserver" data-id="${o.id}">Recalculer la date et réserver</button>`;
    } else {
      const fab = i.date === JANV; dispo = fab ? pill("Non", "ko") : pill("Oui", "ok"); date = fab ? "25 janvier 2027" : "23 octobre 2026";
      res = fab ? pill("Réservé sur fabrication à venir", "info") : pill("Réservé · lot " + i.lot, "ok");
    }
    return `<tr class="${i.s === "payee" ? "sel" : ""}"><td>${quand(o.created)}</td><td><b>${o.id}</b></td><td>${o.cap}, ${o.col}</td><td>${dispo}</td><td>${date}</td><td>${res}</td></tr>`;
  }).join("");
  const tab = st.map((r) => `<tr><td>${r.k.replace("|", ", ")}</td><td>${nf(r.total)}</td><td>${nf(r.res)}</td><td><b>${nf(r.dispo)}</b></td></tr>`).join("");
  const resTot = Math.min(5200, a.stockRes);
  return shell(p, "stock", head("Production · ERP", "Stock et réservations", `France · ${C().titre}. Chaque précommande payée est servie sur le stock de lancement ou, à défaut, sur la fabrication à venir.`) +
    kpis([["Stock de lancement", "5 200", "appareils, France"], ["Appareils réservés", nf(resTot), resTot >= 5200 ? "stock épuisé à 14:28" : nf(5200 - resTot) + " encore disponibles"], ["Réservés sur fabrication à venir", nf(a.fab), "précommandes payées"], ["Prochaine date de livraison", C().stock ? "23 oct. 2026" : "25 janv. 2027", C().stock ? "stock de lancement" : "d'après le plan de production"]]) +
    `<div><div class="card"><h2>Précommandes payées à servir <small>reçues de la finance</small></h2><div class="tw"><table><tr><th>Heure</th><th>N°</th><th>Configuration</th><th>Stock disponible ?</th><th>Date de livraison</th><th>Réservation</th></tr>${rows || `<tr><td colspan="6" class="empty">Aucune précommande à servir.</td></tr>`}</table></div>
    <p class="hint">Si le stock est disponible, un appareil est réservé. Sinon, la date de livraison est recalculée et un appareil à fabriquer est réservé.</p></div>
    <div class="card"><h2>Stock par configuration <small>ERP</small></h2><div class="tw"><table><tr><th>Configuration</th><th>Stock</th><th>Réservés</th><th>Disponible</th></tr>${tab}</table></div></div></div>`);
}
function sPlan(p) {
  const a = p1(); let cum = 0;
  const rows = PLAN.map(([w, q]) => { const avant = cum; cum += q; const servies = Math.max(0, Math.min(q, a.fab - avant)); return `<tr><td>${w}</td><td>${nf(q)}</td><td>${nf(servies)}</td><td>${nf(Math.max(0, a.fab - cum))}</td></tr>`; }).join("");
  return shell(p, "plan", head("Production · ERP", "Plan de production", "Appareils attendus à l'entrepôt français, d'après le plan de fabrication transmis par l'assembleur.") +
    kpis([["Précommandes en attente de fabrication", nf(a.fab), a.fab ? "livraison à partir du 25 janvier" : "le stock de lancement suffit"], ["Prochaine arrivée", "11 janv. 2027", "1 800 appareils"], ["Date annoncée aux nouveaux clients", C().stock ? "23 oct. 2026" : "25 janv. 2027", "affichée sur la boutique"]]) +
    `<div class="card"><h2>Arrivées prévues <small>France</small></h2><div class="tw"><table><tr><th>Semaine</th><th>Appareils prévus</th><th>Précommandes servies</th><th>Encore en attente</th></tr>${rows}</table></div>
    <p class="hint">La date de livraison affichée sur la boutique est recalculée à partir de ce plan quand le stock de lancement est épuisé.</p></div>`);
}

/* Relation client : avis (M2.4) */
function noP2(p, scr, crumb, title) {
  return shell(p, scr, head(crumb, title, "") + `<div class="card empty">Les premières livraisons ont lieu le 23 octobre 2026 : aucune réponse au questionnaire pour l'instant.<br><br><button class="btn pri" data-act="setclock" data-id="t3">Passer au 9 novembre (démonstration)</button></div>`);
}
function sAvis(p) {
  if (now() < "2026-10-23") return noP2(p, "avis", "Relation client · CRM", "Avis reçus");
  const s = sat(); const rs = visReviews(); const sel = S.reviews[ui.sel.r] && rInfo(S.reviews[ui.sel.r]) ? S.reviews[ui.sel.r] : rs[0];
  const rows = rs.slice(0, 16).map((r) => `<tr class="click ${r === sel ? "sel" : ""}" data-act="selr" data-id="${r.ref}"><td>${quand(r.t)}</td><td>${cliMail(r.cli)}</td><td><b>${r.note}</b>/10</td><td>${esc(r.motif)}</td><td>${rPill(rInfo(r).s)}</td></tr>`).join("");
  let det = "";
  if (sel) {
    const i = rInfo(sel); const q = Object.values(S.signals).find((x) => x.rev === sel.ref);
    const idx = { statistique: 2, remercie: 3, a_recontacter: 2, defaut: 2, en_analyse: 3, a_informer: 3, recontacte: 4, clos: 4 }[i.s];
    let acts = "";
    if (i.s === "defaut") acts = `<button class="btn pri" data-act="transmettre" data-id="${sel.ref}">Transmettre à la production (qualité)</button>`;
    if (i.s === "a_recontacter") acts = `<textarea data-act="crtxt" placeholder="Compte rendu de l'appel ou du courriel" style="min-height:60px">${esc(ui.cr)}</textarea><button class="btn pri" style="margin-top:8px" data-act="recontacte" data-id="${sel.ref}">Client recontacté</button>`;
    if (i.s === "a_informer") acts = `<button class="btn pri" data-act="informer" data-id="${sel.ref}">Informer le client de la suite donnée</button>`;
    const suiteQ = q ? (() => { const qi = at(q.hist, now()); const x = {}; q.hist.forEach((h) => { if (h.t <= now() && h.x) Object.assign(x, h.x); }); return `<div class="small" style="margin-top:8px">Signalement ${q.id} · ${qPill(qi.s)}${x.action ? " · " + x.action : ""}</div>`; })() : "";
    const ord = sel.order && S.orders[sel.order] ? S.orders[sel.order] : null;
    det = `<div class="card"><h2>Réponse ${sel.ref} <small>${sel.accord ? "rattachée à la fiche client" : "anonyme"}</small></h2>
    <div class="kv"><span>Client</span><b>${sel.accord ? cliNom(sel.cli) + " · compte vérifié" : "Réponse anonyme"}</b>${sel.accord ? `<span>Commande</span><b>${sel.order}${ord ? " · iPhone Duo " + ord.cap + ", " + ord.col : ""}</b>` : ""}<span>Canal</span><b>${sel.canal}</b><span>Note et motif</span><b>${sel.note} / 10 · ${esc(sel.motif)}</b><span>Accord de recontact</span><b>${sel.accord ? "Oui" : "Non"}</b></div>
    ${sel.txt ? `<div class="quote">« ${esc(sel.txt)} »</div>` : ""}
    ${prog(["Réponse enregistrée", "Score et motif", i.s === "defaut" || i.s === "en_analyse" || i.s === "a_informer" ? "Défaut signalé" : i.s === "statistique" ? "Statistique" : sel.note < 7 ? "À recontacter" : "Remercié", "Suite donnée"], idx)}
    ${suiteQ}<div style="margin-top:10px">${acts}</div><div class="small" style="margin-top:6px"><a href="#/si/${p}/processus?r=${sel.ref}">Voir l'avancement dans le processus ›</a></div></div>`;
  }
  return shell(p, "avis", head("Relation client · CRM", "Avis reçus par QR code", "Chaque réponse au questionnaire arrive ici, est rattachée à la fiche du client quand il l'a accepté, puis reçoit un score et un motif.") +
    kpis([["Réponses reçues aujourd'hui", nf(s.jour.rep), `dont ${s.jour.anonymes} anonymes`], ["Note moyenne", dec1(s.jour.moy), "sur 10"], ["Clients insatisfaits (note < 7)", nf(s.jour.insatisfaits), pct(s.jour.insatisfaits, s.jour.rep) + " des réponses"], ["À recontacter sous 48 h", nf(s.jour.recontacter), "accord donné"], ["Défauts transmis à la production", nf(s.jour.transmis), "en analyse"]]) +
    `<div class="cols"><div class="card"><h2>Dernières réponses <small>adresses masquées à l'affichage</small></h2><div class="tw"><table><tr><th>Reçu</th><th>Client</th><th>Note</th><th>Motif</th><th>Suite</th></tr>${rows}</table></div>
    <p class="hint">Note de 7 ou plus : le client est remercié. Note inférieure à 7 : il est recontacté, et un défaut de charnière ou d'écran part à la production. Sans accord, la réponse reste anonyme.</p></div>${det}</div>`);
}
function sSuivi(p) {
  if (now() < "2026-10-23") return noP2(p, "suivi", "Relation client · CRM", "Dossiers de suivi");
  const rs = visReviews().filter((r) => r.accord && rInfo(r).s !== "remercie");
  const etape = { defaut: "Défaut à transmettre", a_recontacter: "Client à recontacter", en_analyse: "Production ou finance", a_informer: "Client à informer", recontacte: "Terminé", clos: "Terminé" };
  const rows = rs.map((r) => { const i = rInfo(r); return `<tr class="click" data-act="openr" data-id="${r.ref}"><td><b>${r.ref}</b></td><td>${cliNom(r.cli)}</td><td>${r.note}/10 · ${esc(r.motif)}</td><td>${etape[i.s]}</td><td>${quand(i.t)}</td><td>${rPill(i.s)}</td></tr>`; }).join("");
  const open = rs.filter((r) => !["clos", "recontacte"].includes(rInfo(r).s)).length;
  return shell(p, "suivi", head("Relation client · CRM", "Dossiers de suivi", "Les avis qui demandent une action : recontact, défaut signalé, solution à annoncer au client.") +
    kpis([["Dossiers ouverts", nf(open), ""], ["Délai moyen de recontact", "19 h", "objectif 48 h"], ["Dossiers clos cette semaine", nf(rs.length - open), ""]]) +
    `<div class="card"><h2>Dossiers <small>avis avec accord de recontact</small></h2><div class="tw"><table><tr><th>Dossier</th><th>Client</th><th>Avis</th><th>Étape</th><th>Depuis</th><th>Statut</th></tr>${rows}</table></div></div>`);
}

/* Production : qualité (M2.5) */
function sQualite(p) {
  if (now() < "2026-10-23") return noP2(p, "qualite", "Production · qualité", "Signalements qualité");
  const qs = visSignals(); const sel = S.signals[ui.sel.q] && S.signals[ui.sel.q].t <= now() ? S.signals[ui.sel.q] : qs[0];
  const rows = qs.map((q) => `<tr class="click ${q === sel ? "sel" : ""}" data-act="selq" data-id="${q.id}"><td><b>${q.id}</b></td><td>${quand(q.t)}</td><td>${esc(q.defaut)}</td><td>${q.lot}</td><td>${qPill(at(q.hist, now()).s)}</td></tr>`).join("");
  let det = "";
  if (sel) {
    const i = at(sel.hist, now()); const x = {}; sel.hist.forEach((h) => { if (h.t <= now() && h.x) Object.assign(x, h.x); });
    const r = S.reviews[sel.rev]; const lb = LOTS_BASE.find((l) => l[0] === sel.lot);
    const acts = i.s === "analyse" ? `<h2 style="margin-top:14px">Défaut confirmé ?</h2><select class="inp" data-act="qact" style="margin-bottom:10px">${ACTIONS.map(([a, c], k) => `<option value="${k}" ${k === ui.act ? "selected" : ""}>${a} · ${eur(c)}</option>`).join("")}</select>
      <button class="btn pri" data-act="confirmerq" data-id="${sel.id}">Oui : lancer l'action corrective</button><button class="btn red" data-act="nonq" data-id="${sel.id}">Non : informer le client</button>` :
      i.s === "confirme" ? `<div class="kv" style="margin-top:12px"><span>Action corrective</span><b>${x.action}</b><span>Coût estimé</span><b>${eur(x.cout)} · transmis à la finance</b></div>` : `<div class="quote" style="font-style:normal">Défaut non confirmé : la relation client informe le client et lui propose un contrôle en magasin.</div>`;
    det = `<div class="card"><h2>Signalement ${sel.id} <small>reçu du CRM le ${dMed(sel.t)} à ${hm(sel.t)}</small></h2>
    <div class="kv"><span>Origine</span><b>Réponse ${sel.rev} (questionnaire)</b><span>Défaut signalé</span><b>${esc(sel.defaut)}</b>${r && r.order ? `<span>Commande</span><b>${r.order}</b>` : ""}<span>Numéro de série</span><b>${sel.serial || "lu dans l'ERP"}</b><span>Lot de fabrication</span><b>${sel.lot}${lb ? " · assemblé en " + lb[1] : ""}</b></div>
    ${r && r.txt ? `<div class="quote">« ${esc(r.txt)} »</div>` : ""}${acts}</div>`;
  }
  const lots = LOTS_BASE.map(([l, w, n, sg, cf]) => {
    let s2 = sg, c2 = cf;
    Object.values(S.signals).forEach((q) => { if (q.lot !== l || q.t > now()) return; const i = at(q.hist, now()); if (q.u) s2++; const seedQ = SEED_SIGNALS.find((z) => z[0] === q.id); const was = seedQ ? at(seedQ[5].map(([tt, st]) => ({ t: tt, s: st })), now()) : null; if (i.s === "confirme" && (!was || was.s !== "confirme")) c2++; });
    return `<tr><td><b>${l}</b></td><td>${w}</td><td>${s2}</td><td>${c2}</td><td>${(s2 / n * 100).toLocaleString("fr-FR", { maximumFractionDigits: 2 })} %</td></tr>`;
  }).join("");
  return shell(p, "qualite", head("Production · qualité", "Signalements qualité", "Les défauts signalés par les clients arrivent du CRM. Le technicien retrouve l'appareil dans l'ERP grâce à son numéro de série et décide de la suite.") +
    `<div class="cols"><div><div class="card"><h2>Signalements <small>reçus du CRM</small></h2><div class="tw"><table><tr><th>N°</th><th>Reçu</th><th>Défaut</th><th>Lot</th><th>Statut</th></tr>${rows}</table></div></div>
    <div class="card"><h2>Signalements par lot <small>30 derniers jours</small></h2><div class="tw"><table><tr><th>Lot</th><th>Assemblage</th><th>Signalés</th><th>Confirmés</th><th>Taux</th></tr>${lots}</table></div><p class="hint">Au-delà de 0,3 % d'appareils signalés dans un lot, un contrôle renforcé est déclenché.</p></div></div>${det}</div>`);
}

/* Finance : garantie (M2.6), chiffre d'affaires */
function sGarantie(p) {
  if (now() < "2026-10-23") return noP2(p, "garantie", "Finance · contrôle de gestion", "Coûts de garantie");
  const s = sat(); const cs = visCosts();
  const rows = cs.map((c) => { const i = at(c.hist, now()); return `<tr class="${i.s === "a_enregistrer" ? "sel" : ""}"><td><b>${c.id}</b></td><td>${quand(c.t)}</td><td>${c.action}</td><td>${eur(c.cout)}</td><td>${i.s === "a_enregistrer" ? `<button class="btn pri sm" data-act="enregistrer" data-id="${c.id}">Enregistrer le coût</button>` : cPill(i.s)}</td></tr>`; }).join("");
  const budget = 268550;
  return shell(p, "garantie", head("Finance · contrôle de gestion", "Coûts de garantie", "Chaque action corrective décidée par la production est chiffrée puis enregistrée dans l'ERP. Le cumul est comparé à la provision du trimestre.") +
    kpis([["Coûts enregistrés (semaine)", eur(s.couts), `${s.confirmes} défauts confirmés`], ["Coût moyen par défaut", eur(s.couts / s.confirmes), "échanges et réparations"], ["Provision pour garantie utilisée", Math.round(s.couts / budget * 100) + " %", "du budget du trimestre"], ["Écart par rapport à la prévision", "+1,2 pt", "à surveiller"]]) +
    `<div class="card"><h2>Actions correctives à chiffrer <small>reçues de la production</small></h2><div class="tw"><table><tr><th>Signalement</th><th>Reçu</th><th>Action corrective</th><th>Coût</th><th>Statut</th></tr>${rows}</table></div>
    <p class="hint">Une fois le coût enregistré, la relation client informe le client de la solution et le tableau de bord de satisfaction est mis à jour.</p></div>`);
}
function sCA(p) {
  const a = p1(); const w = CAPS.map((c) => (MIX.find((m) => m[0] === c.cap)[1]) * c.prix); const W = w.reduce((x, y) => x + y, 0);
  const rows = CAPS.map((c, k) => { const ca = a.ca * w[k] / W; return `<tr><td>${c.cap}</td><td>${eur(c.prix)}</td><td>${nf(ca / c.prix)}</td><td><b>${meur(ca)}</b></td></tr>`; }).join("");
  return shell(p, "ca", head("Finance · ERP", "Chiffre d'affaires prévisionnel", "Enregistré à chaque paiement accepté ; il devient du chiffre d'affaires réalisé à l'expédition de l'appareil.") +
    kpis([["Chiffre d'affaires prévisionnel", meur(a.ca), "TTC, France"], ["Paiements acceptés", nf(a.recues - a.controle - a.annulees), ""], ["Paiements refusés", nf(a.annulees), pct(a.annulees, a.recues)], ["Panier moyen", eur(a.ca / Math.max(1, a.recues - a.controle - a.annulees)), "par précommande"]]) +
    `<div class="card"><h2>Répartition par capacité <small>estimation à partir du mix des précommandes</small></h2><div class="tw"><table><tr><th>Capacité</th><th>Prix TTC</th><th>Précommandes payées</th><th>Chiffre d'affaires</th></tr>${rows}</table></div></div>`);
}

/* Marketing : tableaux de bord et campagnes */
function chart() {
  const lim = S.clock === "t1" ? "14:10" : S.clock === "t2" ? "14:35" : "15:00";
  const pts = COURBE.filter(([h]) => h <= lim); const W = 560, H = 200, X = (h) => { const [a, b] = h.split(":").map(Number); return 40 + ((a - 14) * 60 + b) / 60 * (W - 60); }, Y = (v) => H - 24 - v / 8000 * (H - 40);
  const path = pts.map(([h, v], k) => (k ? "L" : "M") + X(h).toFixed(1) + " " + Y(v).toFixed(1)).join(" ");
  const ticks = ["14:00", "14:15", "14:30", "14:45", "15:00"].map((h) => `<text x="${X(h)}" y="${H - 6}" font-size="10" text-anchor="middle" fill="#86868b">${h}</text>`).join("");
  const ep = lim >= "14:28" ? `<line x1="${X("14:28")}" y1="14" x2="${X("14:28")}" y2="${H - 24}" stroke="#ff3b30" stroke-dasharray="3 3"/><text x="${X("14:28") + 4}" y="22" font-size="10" fill="#b3261e">stock épuisé, 14:28</text>` : "";
  return `<svg viewBox="0 0 ${W} ${H}" width="100%"><line x1="40" y1="${Y(5200)}" x2="${W - 20}" y2="${Y(5200)}" stroke="#d2d2d7" stroke-dasharray="4 4"/><text x="${W - 20}" y="${Y(5200) - 4}" font-size="10" text-anchor="end" fill="#86868b">stock de lancement : 5 200</text>
  ${[0, 2000, 4000, 6000, 8000].map((v) => `<text x="34" y="${Y(v) + 3}" font-size="10" text-anchor="end" fill="#86868b">${nf(v)}</text>`).join("")}${ticks}${ep}
  <path d="${path}" fill="none" stroke="#0071e3" stroke-width="2.5"/>${pts.length ? `<circle cx="${X(pts[pts.length - 1][0])}" cy="${Y(pts[pts.length - 1][1])}" r="4" fill="#0071e3"/>` : ""}</svg>`;
}
const bars = (arr, max, alt) => arr.map(([l, v, lab]) => `<div class="barrow"><div>${l}</div><div class="barbg"><div class="bar ${alt ? "alt" : ""}" style="width:${Math.min(100, v / max * 100)}%"></div></div><div><b>${lab || v + " %"}</b></div></div>`).join("");
function sLancement(p) {
  const a = p1();
  return shell(p, "lancement", head("Direction marketing", "Tableau de bord du lancement", `France · ${C().titre} · données agrégées, sans information personnelle.`) +
    kpis([["Précommandes reçues", nf(a.recues), S.clock === "t3" ? "depuis le 16 octobre" : "depuis 14 h"], ["Confirmées", nf(a.confirmees), pct(a.confirmees, a.recues)], ["Chiffre d'affaires prévisionnel", meur(a.ca), "TTC"], ["Stock de lancement réservé", pct(Math.min(5200, a.stockRes), 5200), nf(Math.min(5200, a.stockRes)) + " sur 5 200"], ["Confirmées pour janvier", nf(a.janvier), "fabrication à venir"], ["Date annoncée", dShort(C().stock ? "2026-10-23" : JANV), C().stock ? "stock disponible" : "depuis 14:28"]]) +
    `<div class="cols"><div class="card"><h2>Précommandes cumulées le 16 octobre</h2>${chart()}</div>
    <div class="card"><h2>Mix des précommandes</h2>${bars(MIX.map(([c, v]) => [c, v]), 40)}<h2 style="margin-top:14px">Couleurs</h2>${bars([["Ciel nocturne", 54], ["Blanc stellaire", 46]], 60)}</div></div>`);
}
function sSatisfaction(p) {
  if (now() < "2026-10-23") return noP2(p, "satisfaction", "Direction marketing", "Tableau de bord de satisfaction");
  const s = sat(); const ins = Object.values(s.motifs).reduce((x, y) => x + y, 0);
  const mot = MOTIFS.map((m) => [m, Math.round(s.motifs[m] / ins * 100)]);
  const wk = s.semaines.concat([["S46 (en cours)", s.jour.moy]]).map(([w, v]) => `<div style="flex:1;text-align:center"><div style="height:${Math.round((v - 6) * 40)}px;background:#0071e3;border-radius:8px 8px 0 0;margin:0 14px"></div><div class="small" style="margin-top:6px"><b>${dec1(v)}</b><br><span class="muted">${w}</span></div></div>`).join("");
  return shell(p, "satisfaction", head("Direction marketing · production · finance", "Tableau de bord de satisfaction", "France · du 2 au 9 novembre 2026 · mis à jour à chaque réponse enregistrée dans le CRM.") +
    kpis([["Réponses reçues", nf(s.rep), `taux de réponse ${s.taux} %`], ["Note moyenne", dec1(s.moy), "objectif 8,5"], ["Clients satisfaits (note ≥ 7)", pct(s.satis, s.rep), nf(s.satis) + " réponses"], ["Défauts signalés", nf(s.defauts), `dont ${s.confirmes} confirmés`], ["Délai moyen de recontact", s.recontact + " h", "objectif 48 h"], ["Coûts de garantie", eur(s.couts), "enregistrés par la finance"]]) +
    `<div class="cols3"><div class="card"><h2>Motifs d'insatisfaction <small>${ins} réponses</small></h2>${bars(mot, 35)}</div>
    <div class="card"><h2>Note moyenne par semaine</h2><div style="display:flex;align-items:flex-end;height:170px">${wk}</div><p class="hint">La baisse vient surtout des délais de livraison et de la charnière.</p></div>
    <div class="card"><h2>Ce que chaque fonction en fait</h2><div class="kv" style="grid-template-columns:90px 1fr"><span>Marketing</span><div>Adapter les messages sur le prix et les délais ; suivre les dossiers ouverts.</div><span>Production</span><div>Contrôler le lot L-2643-B ; corriger le serrage de la charnière.</div><span>Finance</span><div>Suivre la provision pour garantie ; actualiser le coût de revient.</div></div></div></div>`);
}
function sCampagnes(p) {
  const rows = CAMPAGNES.map((r) => `<tr>${r.map((c, k) => `<td>${k === 0 ? "<b>" + c + "</b>" : c}</td>`).join("")}</tr>`).join("");
  return shell(p, "campagnes", head("Direction marketing · communication", "Campagnes et audience", "Audience remontée par la communication et rapprochée des précommandes dans le CRM (attribution au dernier contact).") +
    kpis([["Visites de la page iPhone Duo", "940 000", "France, depuis le 9 septembre"], ["Vues des vidéos sociales", "4,3 M", "TikTok et Instagram"], ["Précommandes après un clic social", "17 %", "des précommandes en ligne"], ["Clients ayant accepté les offres", "38 %", "des clients Apple en France"]]) +
    `<div class="card"><h2>Actions de lancement</h2><div class="tw"><table><tr><th>Action</th><th>Période</th><th>Objectif</th><th>Audience</th><th>Interaction</th><th>Part des précommandes</th></tr>${rows}</table></div>
    <p class="hint">Les courriels ne sont envoyés qu'aux clients qui ont accepté les offres personnalisées.</p></div>`);
}

/* Processus (pour tous les profils) */
function sProcessus(p) {
  const n = tasks(); const P = PROFILS[p].ecrans; const prm = new URLSearchParams(location.hash.split("?")[1] || "");
  const link = (e, t) => (P.includes(e) ? `<a href="#/si/${p}/${e}">${t}</a>` : t);
  const line = (l, v, e) => `<div style="display:flex;justify-content:space-between;padding:7px 0;border-bottom:1px solid #f0f0f3;font-size:13px"><span>${link(e, l)}</span><b>${v}</b></div>`;
  const os = visOrders(); const o = S.orders[prm.get("o")] && oInfo(S.orders[prm.get("o")]) ? S.orders[prm.get("o")] : (os.find((x) => x.u) || os[0]);
  const rs = visReviews(); const r = S.reviews[prm.get("r")] && rInfo(S.reviews[prm.get("r")]) ? S.reviews[prm.get("r")] : rs[0];
  const selO = `<select class="inp" data-act="trk" data-k="o" style="max-width:360px">${os.slice(0, 30).map((x) => `<option value="${x.id}" ${x === o ? "selected" : ""}>${x.id} · ${x.cap}, ${x.col} · ${quand(x.created)}</option>`).join("")}</select>`;
  const selR = rs.length ? `<select class="inp" data-act="trk" data-k="r" style="max-width:360px">${rs.slice(0, 30).map((x) => `<option value="${x.ref}" ${x === r ? "selected" : ""}>${x.ref} · ${x.note}/10 · ${x.motif} · ${quand(x.t)}</option>`).join("")}</select>` : "";
  return shell(p, "processus", head("Entreprise", "Processus", "Les deux processus outillés par le SI, le travail en attente à chaque étape et le suivi d'une commande ou d'un avis.") +
    `<div class="grid2"><div class="card"><h2>De la précommande à la confirmation</h2><a href="img/fig/bpmn-precommande.png" target="_blank"><img src="img/fig/bpmn-precommande.png" alt="Diagramme BPMN du processus de précommande" style="width:100%;border:1px solid #f0f0f3;border-radius:8px"></a>
    ${line("Paiements à contrôler (finance)", n.paiements, "paiements")}${line("Précommandes à servir (production)", n.stock, "stock")}${line("Confirmations et refus à envoyer (ventes)", n.precommandes, "precommandes")}
    <h2 style="margin-top:18px">Suivre une précommande</h2>${selO}${o ? tlOrder(o) : ""}</div>
    <div class="card"><h2>Satisfaction par QR code</h2><a href="img/fig/bpmn-satisfaction.png" target="_blank"><img src="img/fig/bpmn-satisfaction.png" alt="Diagramme BPMN du processus de satisfaction" style="width:100%;border:1px solid #f0f0f3;border-radius:8px"></a>
    ${line("Avis à traiter (relation client)", n.avis, "avis")}${line("Signalements à analyser (production)", n.qualite, "qualite")}${line("Coûts de garantie à enregistrer (finance)", n.garantie, "garantie")}
    <h2 style="margin-top:18px">Suivre un avis</h2>${r ? selR + tlReview(r) : `<div class="small muted">Aucun avis : les premières livraisons ont lieu le 23 octobre 2026.</div>`}</div></div>`);
}

/* ---------- échanges entre services (flux d'information) ---------- */
const F = (t, de, vers, info, outil, ref, proc) => ({ t, de, vers, info, outil, ref, proc });
function fluxAll() {
  const t = now(); const L = [];
  FLUX_SEED.forEach((f) => { if (f[0] <= t) L.push(F(...f)); });
  (S.flog || []).forEach((f) => { if (f.t <= t) L.push(f); });
  Object.values(S.orders).forEach((o) => {
    if (o.created > t) return; const c = o.created;
    L.push(F(c, "Client", "Ventes", `Précommande ${o.id} (${o.cap}, ${o.col}) et données de paiement`, "Site de vente", "A3-9 · A1-1", "P1"));
    L.push(F(c, "Ventes", "Relation client et données", `Précommande ${o.id} ajoutée à la fiche client`, "CRM", "A3-14", "P1"));
    L.push(F(c, "Ventes", "Finance", `Commande à encaisser ${o.id} (${eur(o.prix)})`, "CRM → ERP", "A3-11 · A2-5", "P1"));
    L.push(F(c, "Finance", "Banque", `Demande ${o.pay === "Financement" ? "de crédit" : "d'autorisation"} pour ${o.id}`, "Données de paiement", "A1-7", "P1"));
    L.push(F(c, "Banque", "Finance", `${o.bank === "ok" ? (o.pay === "Financement" ? "Crédit accordé" : "Autorisation accordée") : (o.pay === "Financement" ? "Crédit refusé" : "Autorisation refusée")} pour ${o.id}`, "Données de paiement", "A1-7", "P1"));
    o.hist.forEach((h) => {
      if (h.t > t) return;
      if (h.s === "payee") { L.push(F(h.t, "Finance", "Ventes", `Paiement accepté pour ${o.id}`, "ERP → CRM", "A3-11 · A2-6", "P1")); L.push(F(h.t, "Ventes", "Production", `Précommande payée ${o.id} à servir`, "CRM → ERP", "A3-12 · A2-3", "P1")); }
      if (h.s === "refusee") L.push(F(h.t, "Finance", "Ventes", `Paiement refusé pour ${o.id}`, "ERP → CRM", "A3-11 · A2-6", "P1"));
      if (h.s === "reservee") L.push(F(h.t, "Production", "Ventes", h.x && h.x.date === JANV ? `Stock épuisé : livraison de ${o.id} recalculée au 25 janvier 2027` : `Appareil réservé pour ${o.id} (${h.x ? h.x.lot : ""}) : livraison le 23 octobre`, "ERP → CRM", "A3-12 · A2-4", "P1"));
      if (h.s === "confirmee") L.push(F(h.t, "Ventes", "Client", `Confirmation de ${o.id} et date de livraison`, "Courriel", "A3-10 · A1-2", "P1"));
      if (h.s === "annulee") L.push(F(h.t, "Ventes", "Client", `Paiement refusé : précommande ${o.id} annulée`, "Courriel", "A3-10 · A1-2", "P1"));
    });
  });
  Object.values(S.reviews).forEach((r) => {
    if (!rInfo(r, t)) return; const qui = r.accord ? "Client" : "Client (anonyme)";
    L.push(F(r.t, qui, "Relation client et données", `Réponse au questionnaire ${r.ref} (${r.note}/10, ${r.motif})`, "Questionnaire → CRM", "A3-15 · A1-1", "P2"));
    L.push(F(r.t, "Relation client et données", "Direction marketing produit", `Tableau de bord de satisfaction mis à jour (${r.ref})`, "Tableau de bord", "A3-18", "P2"));
    r.hist.forEach((h) => {
      if (h.t > t) return;
      if (h.s === "remercie") L.push(F(h.t, "Relation client et données", "Client", `Remerciement pour l'avis ${r.ref}`, "Courriel", "A3-16 · A1-2", "P2"));
      if (h.s === "en_analyse") L.push(F(h.t, "Relation client et données", "Production", `Défaut signalé ${r.ref} (${r.motif})`, "CRM → ERP", "A3-17 · A2-3", "P2"));
      if (h.s === "recontacte") L.push(F(h.t, "Relation client et données", "Client", `Réponse à l'avis ${r.ref}`, "Téléphone", "A3-16 · A1-2", "P2"));
      if (h.s === "clos") L.push(F(h.t, "Relation client et données", "Client", `Solution proposée pour l'avis ${r.ref}`, "Courriel", "A3-16 · A1-2", "P2"));
    });
  });
  Object.values(S.signals).forEach((q) => {
    q.hist.forEach((h) => {
      if (h.t > t) return;
      if (h.s === "confirme") { L.push(F(h.t, "Production", "Relation client et données", `Résultat d'analyse ${q.id} : défaut confirmé, ${h.x.action.toLowerCase()}`, "ERP → CRM", "A3-17 · A2-4", "P2")); L.push(F(h.t, "Production", "Finance", `Coût de garantie ${q.id} : ${eur(h.x.cout)}`, "ERP", "A2-7", "P2")); }
      if (h.s === "non_confirme") L.push(F(h.t, "Production", "Relation client et données", `Résultat d'analyse ${q.id} : défaut non confirmé`, "ERP → CRM", "A3-17 · A2-4", "P2"));
    });
  });
  return L.sort((a, b) => (a.t < b.t ? 1 : a.t > b.t ? -1 : 0));
}
const EXT = ["Client", "Client (anonyme)", "Banque", "Distributeurs"];
function sEchanges(p) {
  const all = fluxAll(); const f = ui.jf || "tous";
  const keep = (x) => f === "tous" || (f === "ext" ? EXT.includes(x.de) || EXT.includes(x.vers) : x.proc === f);
  const L = all.filter(keep);
  const chip = (k, t) => `<button class="${f === k ? "on" : ""}" data-act="jf" data-id="${k}">${t}</button>`;
  const rows = L.slice(0, 80).map((x) => `<tr><td>${quand(x.t)}</td><td>${x.de}</td><td>${x.vers}</td><td>${esc(x.info)}</td><td>${x.outil}</td><td><b>${x.ref}</b></td></tr>`).join("");
  const jour = all.filter((x) => x.t.slice(0, 10) === now().slice(0, 10));
  return shell(p, "echanges", head("Entreprise", "Échanges entre services", "Chaque information qui passe d'un service à un autre, ou entre Apple et un acteur externe. La référence renvoie aux tableaux de flux de notre dossier (annexe, tableaux A1 à A3).") +
    kpis([["Échanges aujourd'hui", nf(jour.length), dMed(now())], ["Avec un acteur externe", nf(jour.filter((x) => EXT.includes(x.de) || EXT.includes(x.vers)).length), "clients, banque, distributeurs"], ["Processus 1 (précommande)", nf(jour.filter((x) => x.proc === "P1").length), "aujourd'hui"], ["Processus 2 (satisfaction)", nf(jour.filter((x) => x.proc === "P2").length), "aujourd'hui"]]) +
    `<div class="card"><div class="chips" style="margin:0 0 12px">${chip("tous", "Tous")}${chip("P1", "Processus 1")}${chip("P2", "Processus 2")}${chip("ext", "Avec l'extérieur")}</div>
    <div class="tw"><table><tr><th>Heure</th><th>Émetteur</th><th>Récepteur</th><th>Information</th><th>Outil</th><th>Flux</th></tr>${rows || `<tr><td colspan="6" class="empty">Aucun échange.</td></tr>`}</table></div>
    <p class="hint">A1 : flux entre Apple et ses acteurs externes · A2 : flux entre les acteurs internes d'Apple · A3 : flux de la fonction marketing et ventes. ${L.length > 80 ? "80 derniers échanges affichés." : ""}</p></div>`);
}

/* ---------- distributeurs (ventes) ---------- */
function ventesDist(part) { return now() >= "2026-10-23T09:00" ? part : 0; }
function sDistributeurs(p) {
  const after = now() >= "2026-10-23T09:00"; const extra = S.distSent || 0;
  const rows = DISTRIBS.map(([n, ty, al, part], k) => { const v = Math.round(al * ventesDist(part)) + (k === 0 ? extra : 0); return `<tr><td><b>${n}</b></td><td>${ty}</td><td>${nf(al)}</td><td>${nf(v)}</td><td>${pct(v, al)}</td><td>${after ? (now() >= "2026-11-09T08:00" ? "09/11 08:00" : dShort(now()) + " 08:00") : "—"}</td></tr>`; }).join("");
  const tot = DISTRIBS.reduce((a, d) => a + d[2], 0); const vend = DISTRIBS.reduce((a, d) => a + Math.round(d[2] * ventesDist(d[3])), 0) + extra;
  return shell(p, "distributeurs", head("Ventes · EDI", "Distributeurs", "Opérateurs télécom et revendeurs agréés : Apple leur alloue un stock pour la mise en vente, ils renvoient chaque matin leurs ventes de la veille par échange de données informatisé (EDI).") +
    kpis([["Stock alloué aux distributeurs", nf(tot), "hors boutique en ligne"], ["Ventes déclarées", nf(vend), after ? "depuis le 23 octobre" : "mise en vente le 23 octobre"], ["Taux d'écoulement", pct(vend, tot), ""], ["Distributeurs reliés", DISTRIBS.length, "relevé quotidien"]]) +
    `<div class="card"><h2>Distributeurs <small>noms fictifs</small></h2><div class="tw"><table><tr><th>Distributeur</th><th>Type</th><th>Stock alloué</th><th>Ventes déclarées</th><th>Écoulement</th><th>Dernier relevé</th></tr>${rows}</table></div>
    <p class="hint">Les ventes des distributeurs complètent les précommandes de la boutique en ligne dans le tableau de bord du lancement.</p></div>`);
}

/* ---------- partenaires externes ---------- */
function pshell(k, inner) {
  const P = PARTENAIRES[k];
  return topbar("si") + `<div class="app"><aside class="side"><div class="who"><span>Espace partenaire</span><b>${P.nom}</b><span>${P.role}</span><div style="margin-top:6px"><a href="#/si">Changer de profil</a></div></div>
  <ul class="nav"><li class="sep">Mes écrans</li><li><a class="on" href="#/partenaire/${k}">${P.ecran}</a></li></ul></aside><main class="main">${inner}<p class="hint" style="margin-top:22px">${C().titre} · données fictives</p></main></div>`;
}
function vBanque() {
  const a = p1(); const os = visOrders();
  const rows = os.slice(0, 18).map((o) => `<tr><td>${quand(o.created)}</td><td>Apple Distribution International</td><td><b>${o.id}</b></td><td>${eur(o.prix)}</td><td>${o.pay === "Financement" ? "Crédit" : "Carte bancaire"}</td><td>${o.bank === "ok" ? pill("Accordée", "ok") : pill("Refusée", "ko")}</td><td>${(0.8 + (parseInt(o.id.slice(-2), 10) % 9) / 10).toLocaleString("fr-FR")} s</td></tr>`).join("");
  return pshell("banque", head("Banque · acteur externe", "Demandes d'autorisation", "Demandes envoyées par la finance d'Apple pour chaque précommande. La réponse est automatique : solde, plafond de la carte ou étude du crédit.") +
    kpis([["Demandes reçues d'Apple", nf(a.recues), S.clock === "t3" ? "depuis le 16 octobre" : "depuis 14 h"], ["Accordées", pct(a.recues - a.annulees, a.recues), ""], ["Refusées", nf(a.annulees), "le client est prévenu par Apple"], ["Délai moyen de réponse", "1,2 s", ""]]) +
    `<div class="card"><h2>Dernières demandes</h2><div class="tw"><table><tr><th>Heure</th><th>Commerçant</th><th>Référence</th><th>Montant</th><th>Type</th><th>Réponse</th><th>Délai</th></tr>${rows}</table></div>
    <p class="hint">La banque ne voit que les données de paiement : ni le détail du client, ni ses autres commandes.</p></div>`);
}
function vDistributeur() {
  const after = now() >= "2026-10-23T09:00"; const extra = S.distSent || 0; const part = DISTRIBS[0][3];
  let left = extra;
  const rows = Object.entries(ALLOC_NEO).map(([k, al]) => { let v = Math.round(al * (after ? part : 0)); if (left > 0) { const add = Math.min(left, al - v); v += add; left -= add; } return `<tr><td>${k.replace("|", ", ")}</td><td>${nf(al)}</td><td>${nf(v)}</td><td><b>${nf(al - v)}</b></td></tr>`; }).join("");
  const vend = Math.round(600 * (after ? part : 0)) + extra;
  const btn = after ? `<button class="btn pri" data-act="releve">Envoyer le relevé des ventes à Apple (EDI)</button>` : `<div class="box">Livraison du stock alloué dans nos boutiques le 22 octobre. Mise en vente le 23 octobre.</div>`;
  return pshell("distributeur", head("Distributeur · acteur externe", "Stock alloué et ventes", "Stock d'iPhone Duo alloué par Apple à Néo Télécom pour la mise en vente, et ventes déclarées chaque matin à Apple.") +
    kpis([["Stock alloué par Apple", "600", "reçu le 22 octobre"], ["Vendus", nf(vend), after ? "depuis le 23 octobre" : "mise en vente le 23 octobre"], ["Restant en boutique", nf(600 - vend), ""], ["Relevés envoyés", after ? nf(17 + (S.distSent ? 1 : 0)) : "0", "un par jour"]]) +
    `<div class="card"><h2>Par configuration</h2><div class="tw"><table><tr><th>Configuration</th><th>Alloué</th><th>Vendus</th><th>Restant</th></tr>${rows}</table></div><div style="margin-top:12px">${btn}</div></div>`);
}

/* ---------- suivi d'une commande ou d'un avis dans son processus ---------- */
function timeline(steps) {
  let cur = false;
  return `<div style="margin-top:10px">${steps.map(([lane, task, tt, skip]) => {
    let st, col;
    if (skip) { st = "Non concerné"; col = "#c7c7cc"; }
    else if (tt && tt <= now()) { st = quand(tt); col = "#34c759"; }
    else if (!cur) { cur = true; st = "En cours"; col = "#0071e3"; }
    else { st = "À venir"; col = "#d2d2d7"; }
    return `<div style="display:grid;grid-template-columns:14px 150px 1fr 90px;gap:10px;align-items:center;padding:7px 0;border-bottom:1px solid #f0f0f3;font-size:13px;${skip ? "color:#aeaeb2" : ""}"><span style="width:10px;height:10px;border-radius:50%;background:${col}"></span><span class="muted">${lane}</span><span>${task}</span><span class="small" style="text-align:right;${st === "En cours" ? "color:#0058b9;font-weight:600" : ""}">${st}</span></div>`;
  }).join("")}</div>`;
}
const tOf = (hist, s) => { const h = hist.find((x) => x.s === s && x.t <= now()); return h ? h.t : null; };
function tlOrder(o) {
  const c = o.created; const tP = tOf(o.hist, "payee"), tR = tOf(o.hist, "refusee"), tRes = tOf(o.hist, "reservee"), tC = tOf(o.hist, "confirmee"), tA = tOf(o.hist, "annulee");
  const i = oInfo(o); const ko = !!tR || o.bank === "ko"; const fab = i.date === JANV || (!tRes && !dispoCfg(o.cap, o.col));
  return timeline([
    ["Client", "Précommander (message « précommande validée »)", c], ["Ventes", "Enregistrer la précommande", c], ["Finance", "Contrôler le paiement", c],
    ["Banque", "Répondre à la demande d'autorisation", c], ["Finance", `Paiement accepté ? ${tP ? "· oui" : tR ? "· non" : ""}`, tP || tR],
    ["Finance", "Enregistrer le CA prévisionnel", tP, ko], ["Production", `Vérifier le stock · stock disponible ? ${tRes ? (fab ? "· non" : "· oui") : ""}`, tRes, ko],
    ["Production", "Recalculer la date de livraison", tRes, ko || !fab], ["Production", "Réserver un appareil", tRes, ko],
    ["Ventes", "Confirmer la commande", tC, ko], ["Ventes", "Informer du refus", tA, !ko], ["Client", ko ? "Recevoir le message de refus" : "Recevoir la confirmation", ko ? tA : tC],
  ]);
}
function tlReview(r) {
  const h = r.hist; const st = at(h, now()).s; const q = Object.values(S.signals).find((x) => x.rev === r.ref);
  const tQ = q ? (tOf(q.hist, "confirme") || tOf(q.hist, "non_confirme")) : null; const conf = q && tOf(q.hist, "confirme");
  const cost = q && S.costs[q.id] ? tOf(S.costs[q.id].hist, "enregistre") : null;
  const def = r.accord && r.note < 7 && DEFAUTS.includes(r.motif); const rec = r.accord && r.note < 7 && !def;
  return timeline([
    [r.accord ? "Client" : "Client (anonyme)", "Répondre au questionnaire", r.t], ["Relation client", "Enregistrer la réponse, calculer le score", r.t],
    ["Relation client", `Note et motif ? · ${!r.accord ? "sans accord" : r.note >= 7 ? "7 ou plus" : def ? "défaut" : "moins de 7"}`, r.t],
    ["Relation client", "Remercier le client", r.t, !(r.accord && r.note >= 7)], ["Relation client", "Recontacter le client", tOf(h, "recontacte"), !rec],
    ["Relation client", "Transmettre le défaut à la production", tOf(h, "en_analyse"), !def], ["Production", `Analyser le signalement · défaut confirmé ? ${tQ ? (conf ? "· oui" : "· non") : ""}`, tQ, !def],
    ["Production", "Lancer l'action corrective", conf, !def || (tQ && !conf)], ["Finance", "Enregistrer le coût de garantie", cost, !def || (tQ && !conf)],
    ["Relation client", "Informer le client de la suite", tOf(h, "clos"), !def], ["Direction marketing", "Mettre à jour le tableau de bord", r.t],
  ]) + (st === "statistique" ? `<p class="hint">Réponse sans accord : elle reste anonyme et sert seulement aux statistiques.</p>` : "");
}

/* ---------- le projet ---------- */
function vProjet() {
  const figs = [["contexte-apple", "Modèle de contexte d'Apple pour le lancement"], ["flux-apple", "Flux entre les acteurs internes d'Apple"], ["contexte-fonction", "Modèle de contexte de la fonction marketing et ventes"], ["flux-fonction", "Flux internes de la fonction marketing et ventes"], ["bpmn-precommande", "Processus 1 : de la précommande à la confirmation (BPMN)"], ["bpmn-satisfaction", "Processus 2 : la satisfaction mesurée par QR code (BPMN)"]];
  const rows = Object.values(PROFILS).map((p) => `<tr><td><b>${p.role}</b></td><td>${p.ecrans.map((e) => ECRANS[e].t).join(", ")}</td></tr>`).join("");
  return page("proj", `<main class="wrap"><h1>Le projet</h1>
  <p class="lead">Ce site accompagne notre dossier de TD de Fondamentaux des systèmes d'information (L2 Gestion et Management, IAE Lyon, groupe 12 : Adam, Romy, Anna et Clara). Nous y avons construit les écrans du SI marketing et ventes d'Apple pour le lancement de l'iPhone Duo, avec la production et la finance comme fonctions complémentaires. Les entreprises citées sont réelles ; les clients, les commandes et les chiffres internes sont inventés.</p>
  <div class="card"><h2>Profils et écrans</h2><div class="tw"><table><tr><th>Profil</th><th>Écrans</th></tr><tr><td><b>Client (Léa M.)</b></td><td>Boutique, compte, questionnaire de satisfaction</td></tr>${rows}<tr><td><b>Banque (partenaire)</b></td><td>Demandes d'autorisation</td></tr><tr><td><b>Distributeur (partenaire)</b></td><td>Stock alloué et ventes</td></tr><tr><td><b>Tous les profils internes</b></td><td>Processus (suivi d'une commande ou d'un avis), Échanges entre services</td></tr></table></div></div>
  <div class="grid2" style="margin-top:6px">${figs.map(([f, t]) => `<div class="fig"><a href="img/fig/${f}.png" target="_blank"><img src="img/fig/${f}.png" alt="${t}" loading="lazy"></a><p>${t}</p></div>`).join("")}</div>
  <div class="card center"><h2>Accès direct</h2><img src="img/qr-site.svg" alt="QR code du site" style="width:160px;height:160px;margin:6px auto;display:block"><div class="small muted">${SITE_URL}</div></div></main>`);
}

/* ---------- routeur ---------- */
function route() {
  const raw = location.hash.replace(/^#/, "") || "/"; const [path, qs] = raw.split("?"); const prm = new URLSearchParams(qs || "");
  if (prm.get("t") && CLOCKS[prm.get("t")] && S.clock !== prm.get("t")) { S.clock = prm.get("t"); save(); }
  const seg = path.split("/").filter(Boolean);
  if (!seg.length) return [vHome(), "Accueil"];
  if (seg[0] === "boutique") return seg[1] === "merci" ? [vMerci(seg[2]), "Précommande enregistrée"] : [vShop(), "Boutique"];
  if (seg[0] === "compte") return [vCompte(seg[1]), "Mon compte"];
  if (seg[0] === "carte") return [vCarte(), "Votre avis compte"];
  if (seg[0] === "avis") return [vAvis(seg[1]), "Votre avis"];
  if (seg[0] === "avis-merci") return [vAvisMerci(seg[1]), "Merci"];
  if (seg[0] === "projet") return [vProjet(), "Le projet"];
  if (seg[0] === "partenaire") return seg[1] === "distributeur" ? [vDistributeur(), "Espace partenaire · Néo Télécom"] : [vBanque(), "Banque · autorisations"];
  if (seg[0] === "si") {
    if (!seg[1]) return [vLogin(), "Outils internes"];
    if (seg[1] === "connexion") return [vTwoFA(seg[2]), "Connexion"];
    const p = seg[1]; if (!PROFILS[p]) return [vLogin(), "Outils internes"];
    const scr = seg[2] && (PROFILS[p].ecrans.includes(seg[2]) || seg[2] === "processus" || seg[2] === "echanges") ? seg[2] : PROFILS[p].ecrans[0];
    const f = { precommandes: sPrecommandes, clients: sClients, paiements: sPaiements, stock: sStock, plan: sPlan, avis: sAvis, suivi: sSuivi, qualite: sQualite, garantie: sGarantie, ca: sCA, lancement: sLancement, satisfaction: sSatisfaction, campagnes: sCampagnes, processus: sProcessus, echanges: sEchanges, distributeurs: sDistributeurs }[scr];
    return [f(p), ECRANS[scr].t + " · " + PROFILS[p].nom];
  }
  return [vHome(), "Accueil"];
}
function render(keepScroll) {
  const [html, title] = route();
  $app().innerHTML = html; document.title = title + " · iPhone Duo";
  const r = location.hash.split("?")[0];
  if (!keepScroll && r !== lastRoute) window.scrollTo(0, 0);
  lastRoute = r;
}
function rerender() { save(); render(true); }

/* ---------- actions ---------- */
document.addEventListener("click", (e) => {
  const el = e.target.closest("[data-act]");
  if (!el) { if (ui.clockOpen && !e.target.closest(".clock")) { ui.clockOpen = false; render(true); } return; }
  const a = el.dataset.act; const id = el.dataset.id;
  if (["offres", "qaccord", "bank", "qact", "trk"].includes(a)) return; // gérés par « change »
  const o = S.orders[id]; const r = S.reviews[id]; const q = S.signals[id];
  switch (a) {
    case "clock": ui.clockOpen = !ui.clockOpen; return render(true);
    case "setclock": S.clock = id; ui.clockOpen = false; save(); toast("Démonstration : " + C().titre + " · " + C().legende.toLowerCase()); return render(true);
    case "reset": if (confirm("Effacer toutes les actions faites pendant la démonstration ?")) { S = seed(); ui.sel = {}; ui.clockOpen = false; save(); toast("Données de démonstration réinitialisées"); render(true); } return;
    case "cfg": ui.cfg[el.dataset.k] = el.dataset.v; return render(true);
    case "order": {
      const c = ui.cfg; const t = stamp(); const nid = "W" + (C().idBase + (++S.seq[S.clock]));
      S.orders[nid] = { id: nid, cli: "lea", cap: c.cap, col: c.col, prix: prixDe(c.cap), pay: c.pay, bank: c.bank, created: t, hist: [{ t, s: "controle", x: null }], h0: [], serial: null, u: true };
      ui.sel.o = nid; save(); location.hash = "#/boutique/merci/" + nid; return;
    }
    case "selo": ui.sel.o = id; return render(true);
    case "selc": ui.sel.c = id; ui.note = ""; return render(true);
    case "selr": ui.sel.r = id; ui.cr = ""; return render(true);
    case "selq": ui.sel.q = id; return render(true);
    case "openr": ui.sel.r = id; location.hash = location.hash.replace(/\/suivi$/, "/avis"); return;
    case "accepter": step(o, "payee"); ui.sel.o = id; toast(`Paiement de ${id} accepté · la précommande part à la production`); return rerender();
    case "refuser": step(o, "refusee"); ui.sel.o = id; toast(`Paiement de ${id} refusé · les ventes doivent informer le client`); return rerender();
    case "reserver": {
      const disp = dispoCfg(o.cap, o.col);
      if (disp) { step(o, "reservee", { date: "2026-10-23", lot: LOTS[Math.floor(Math.random() * LOTS.length)] }); o.serial = o.serial || "••••••" + Math.random().toString(36).slice(2, 6).toUpperCase(); toast(`Appareil réservé pour ${id} · livraison le 23 octobre`); }
      else { step(o, "reservee", { date: JANV, lot: "Fabrication à venir" }); toast(`Date recalculée pour ${id} · livraison le 25 janvier 2027`); }
      ui.sel.o = id; return rerender();
    }
    case "confirmer": {
      step(o, "confirmee"); const i = oInfo(o);
      if (o.cli === "lea") msg("Votre précommande est confirmée", `Commande ${o.id} · iPhone Duo ${o.cap}, ${o.col}. ${i.date === JANV ? "Le stock de lancement est épuisé : votre appareil est réservé sur la fabrication à venir. Livraison le lundi 25 janvier 2027." : "Un appareil du stock de lancement vous est réservé. Livraison le vendredi 23 octobre 2026."}`, "#/compte/commandes");
      toast(`Confirmation envoyée au client pour ${id}`); return rerender();
    }
    case "informerrefus": step(o, "annulee"); if (o.cli === "lea") msg("Votre paiement n'a pas été accepté", `Commande ${o.id} · iPhone Duo ${o.cap}, ${o.col}. Votre précommande est annulée et aucun montant n'a été débité. Vous pouvez recommencer avec un autre moyen de paiement.`, "#/boutique"); toast(`Client informé du refus pour ${id}`); return rerender();
    case "qnote": ui.q.note = Number(el.dataset.v); return render(true);
    case "qmotif": ui.q.motif = el.dataset.v; return render(true);
    case "sendavis": {
      const qq = ui.q; if (qq.note === null || !qq.motif) return;
      const t = stamp(); const ref = "R-" + String(S.rseq++).padStart(4, "0"); const oid = id || null;
      const accord = !!(oid && qq.accord);
      const st = !accord ? "statistique" : qq.note >= 7 ? "remercie" : DEFAUTS.includes(qq.motif) ? "defaut" : "a_recontacter";
      S.reviews[ref] = { ref, cli: accord ? "lea" : null, order: accord ? oid : null, canal: oid ? (location.hash.includes("c=courriel") ? "Courriel J+15" : "Coffret (QR code)") : "Table de démonstration", t, note: qq.note, motif: qq.motif, accord, txt: qq.txt.trim(), hist: [{ t, s: st, x: null }], u: true };
      if (oid) S.reviewed[oid] = ref;
      if (st === "remercie") msg("Merci pour votre avis", `Vous avez donné la note de ${qq.note}/10 à votre iPhone Duo. Merci d'avoir pris le temps de répondre.`, "#/compte/avis");
      ui.q = { note: null, motif: null, txt: "", accord: false }; ui.sel.r = ref; save(); location.hash = "#/avis-merci/" + ref; return;
    }
    case "transmettre": {
      step(r, "en_analyse"); const num = r.ref.slice(2); const qid = "Q-" + num; const ord = r.order && S.orders[r.order];
      const info = ord ? oInfo(ord) : {}; const lot = info && info.lot && info.lot.startsWith("L-") ? info.lot : "L-2643-B";
      S.signals[qid] = { id: qid, rev: r.ref, defaut: r.txt || ({ "Charnière": "Problème de charnière", "Écran et pliure": "Problème d'écran ou de pliure" }[r.motif]), lot, serial: (ord && ord.serial) || null, t: now(), hist: [{ t: now(), s: "analyse", x: null }], u: true };
      toast(`Signalement ${qid} créé dans l'ERP · transmis à la production`); return rerender();
    }
    case "recontacte": step(r, "recontacte", { cr: ui.cr }); if (r.cli === "lea") msg("Suite à votre avis", "Merci d'avoir échangé avec notre conseillère au sujet de votre avis sur l'iPhone Duo.", "#/compte/avis"); ui.cr = ""; toast("Recontact enregistré dans la fiche client"); return rerender();
    case "informer": {
      const qs = Object.values(S.signals).find((x) => x.rev === r.ref); let txt = "Notre analyse n'a pas confirmé de défaut. Un contrôle gratuit vous est proposé dans le magasin de votre choix.";
      if (qs) { const x = {}; qs.hist.forEach((h) => { if (h.t <= now() && h.x) Object.assign(x, h.x); }); if (x.action) txt = `Notre analyse a confirmé le défaut. Solution proposée : ${x.action.toLowerCase()}, prise en charge au titre de la garantie.`; }
      step(r, "clos"); if (r.cli === "lea") msg("La suite donnée à votre avis", txt, "#/compte/avis"); toast("Client informé · dossier clos"); return rerender();
    }
    case "confirmerq": {
      const [act, cout] = ACTIONS[ui.act]; step(q, "confirme", { action: act, cout });
      S.costs[q.id] = { id: q.id, t: now(), action: act, cout, hist: [{ t: now(), s: "a_enregistrer", x: null }], u: true };
      toast(`Défaut confirmé · coût de ${eur(cout)} transmis à la finance`); return rerender();
    }
    case "nonq": { step(q, "non_confirme"); const rv = S.reviews[q.rev]; if (rv) step(rv, "a_informer"); toast("Défaut non confirmé · la relation client informe le client"); return rerender(); }
    case "enregistrer": { const c = S.costs[id]; step(c, "enregistre"); const sg = S.signals[id]; const rv = sg && S.reviews[sg.rev]; if (rv) step(rv, "a_informer"); toast(`Coût de ${eur(c.cout)} enregistré dans l'ERP`); return rerender(); }
    case "addnote": { const txt = ui.note.trim(); if (!txt) return; const P = PROFILS[location.hash.split("/")[2]]; (S.notes[id] = S.notes[id] || []).push({ t: stamp(), par: P ? P.nom : "", txt }); ui.note = ""; toast("Note ajoutée"); return rerender(); }
    case "jf": ui.jf = id; return render(true);
    case "releve": S.distSent = (S.distSent || 0) + 23; (S.flog = S.flog || []).push({ t: stamp(), de: "Distributeurs", vers: "Ventes", info: "Relevé des ventes de Néo Télécom (23 appareils)", outil: "EDI", ref: "A3-13 · A1-3", proc: "" }); toast("Relevé envoyé à Apple par EDI"); return rerender();
    case "login": try { sessionStorage.setItem("si-profil", id); } catch (err) { /* sans effet */ } location.hash = "#/si/" + id + "/" + PROFILS[id].ecrans[0]; return;
    case "retirer": r.accord = false; r.cli = null; toast("Accord retiré · votre réponse devient anonyme"); location.hash = "#/compte/avis"; return rerender();
    case "supprimer": if (confirm("Supprimer définitivement cette réponse ?")) { S.deleted[id] = true; toast("Réponse supprimée"); rerender(); } return;
  }
});
document.addEventListener("change", (e) => {
  const el = e.target.closest("[data-act]"); if (!el) return;
  const a = el.dataset.act;
  if (a === "offres") { S.offres.lea = el.checked; save(); toast(el.checked ? "Accord enregistré pour les offres personnalisées" : "Accord retiré pour les offres personnalisées"); }
  if (a === "qaccord") { ui.q.accord = el.checked; }
  if (a === "bank") { ui.cfg.bank = el.value; }
  if (a === "qact") { ui.act = Number(el.value); }
  if (a === "trk") { const pp = location.hash.split("/")[2]; location.hash = `#/si/${pp}/processus?${el.dataset.k}=${el.value}`; }
});
document.addEventListener("input", (e) => {
  const el = e.target.closest("[data-act]"); if (!el) return;
  if (el.dataset.act === "qtxt") ui.q.txt = el.value;
  if (el.dataset.act === "crtxt") ui.cr = el.value;
  if (el.dataset.act === "notetxt") ui.note = el.value;
});
window.addEventListener("hashchange", () => render(false));
render(false);
