// Vérification optionnelle (Node.js + Playwright) : rejoue par de vrais clics les processus P1 et P2 de bout en bout.
// Usage : npm i playwright && npx playwright install chromium && node outils/verifier_parcours_navigateur.js
// Attention : ajoute des données de démonstration (réinitialisables depuis le menu Horloge de l application).
const { chromium } = require('playwright');
const B = 'http://localhost:8005';
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 950 } });
  const errs = [];
  page.on('pageerror', e => errs.push(e.message));
  page.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  const toasts = [];
  const go = async (u) => { await page.goto(B + u, { waitUntil: 'networkidle' }); await page.waitForTimeout(700); };
  const clic = async (sel, opts = {}) => { await page.locator(sel).first().click(opts); await page.waitForTimeout(900); };
  const toast = async () => { const t = await page.locator('[x-data="toasts()"] div.flex.items-start').allInnerTexts(); if (t.length) toasts.push(t[t.length - 1].replace(/\s+/g, ' ')); return t; };
  const etape = (n) => console.log('▶', n);

  // ---------------- P1
  etape('P1-T01..T03 client : précommande 512 Go Titane noir');
  await go('/a/client/configurateur');
  await clic('button:has-text("Valider la précommande")');
  await page.waitForSelector('text=Précommande enregistrée', { timeout: 8000 });
  const ref = (await page.locator('p:has-text("Référence") b').first().innerText()).trim();
  console.log('   référence', ref);
  etape('P1-G01 finance : accepter le paiement');
  await go('/a/finance/paiements');
  await page.locator('tr', { hasText: ref }).locator('button:has-text("Accepter")').click(); await page.waitForTimeout(1200); await toast();
  etape('P1-G02/T07/T08 production');
  await go('/a/production/stocks');
  const ligne = page.locator('tr', { hasText: ref });
  await ligne.locator('button:has-text("Vérifier le stock")').click(); await page.waitForTimeout(1200); await toast();
  if (await page.locator('tr', { hasText: ref }).locator('button:has-text("Allonger")').isVisible()) {
    await page.locator('tr', { hasText: ref }).locator('button:has-text("Allonger")').click(); await page.waitForTimeout(1200); await toast();
    console.log('   branche « non » : délai allongé');
  }
  await page.locator('tr', { hasText: ref }).locator('button:has-text("Réserver")').click(); await page.waitForTimeout(1200); await toast();
  etape('P1-T09 client : confirmation');
  await go('/a/client/commandes?ref=' + ref);
  console.log('   statut affiché :', (await page.locator('span.badge.\\!px-3').first().innerText()).trim());
  etape('P1-T10/G03 direction marketing : analyse France');
  await go('/a/dir_marketing/pilotage-precommandes');
  await page.locator('tr', { hasText: 'France' }).locator('button:has-text("Analyser")').click(); await page.waitForTimeout(1500); await toast();
  await clic('button:has-text("Oui → demander à la production")'); await toast();
  etape('P1-T11 production : transfert + hausse');
  await go('/a/production/plan');
  await clic('button:has-text("Exécuter (T11)")'); await toast();

  // ---------------- P2
  etape('P2 : nouvelle campagne + T01');
  await go('/a/dir_marketing/campagne');
  await clic('button:has-text("Nouvelle campagne")'); await page.waitForTimeout(800);
  await clic('button:has-text("Proposer à la finance")'); await toast();
  etape('P2-G01 finance : accorder');
  await go('/a/finance/budgets');
  await clic('button:has-text("Accorder le budget")'); await toast();
  etape('P2-T02/T03 réseaux sociaux');
  await go('/a/mkt_social/campagne');
  await clic('button:has-text("Publier sur TikTok")'); await toast();
  const cases = page.locator('table input[type=checkbox]');
  await cases.nth(0).check(); await cases.nth(1).check();
  await clic('button:has-text("Sélectionner 2 influenceur")'); await toast();
  etape('P2-T04 production : appareils');
  await go('/a/production/appareils-test');
  await clic('button:has-text("Expédier")'); await toast();
  etape('P2-T05 influenceurs : 2 avis');
  for (let i = 0; i < 2; i++) { await go('/a/influenceur/portail'); await clic('button:has-text("Publier mon avis")'); await toast(); }
  for (const tour of ['non', 'oui']) {
    etape('P2-T06 data : mesure');
    await go('/a/mkt_data/mesure'); await clic('button:has-text("Mesurer maintenant")'); await toast();
    etape('P2-G02 dir marketing : ' + tour);
    await go('/a/dir_marketing/campagne');
    await clic(tour === 'non' ? 'button:has-text("Non : ajuster")' : 'button:has-text("Oui : atteints")'); await toast();
    if (tour === 'non') { etape('P2-T07 réseaux sociaux : ajuster'); await go('/a/mkt_social/campagne'); await clic('button:has-text("Ajuster et relancer")'); await toast(); }
  }
  etape('P2-T08 rapport'); await clic('button:has-text("Envoyer rapport et prévisions")'); await toast();
  etape('P2-T09 production'); await go('/a/production/plan'); await clic('button:has-text("Ajuster le plan")'); await toast();
  etape('P2-T10 finance : CAC'); await go('/a/finance/budgets'); await clic('button:has-text("Calculer le coût d")'); await toast();
  const camps = await (await page.request.get(B + '/api/campagnes')).json();
  console.log('   campagne démo :', camps[0].nom, '— terminée :', camps[0].fini);
  console.log('\nTOASTS :\n - ' + toasts.join('\n - '));
  console.log(errs.length ? '\nERREURS :\n' + [...new Set(errs)].join('\n') : '\nAucune erreur JavaScript.');
  await browser.close();
})().catch(e => { console.error('ÉCHEC :', e.message); process.exit(1); });
