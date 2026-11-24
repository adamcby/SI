/* Données de démonstration (fictives) */
"use strict";

const SITE_URL = "https://adamcby.github.io/SI/";

const CAPS = [
  { cap: "256 Go", prix: 2339 },
  { cap: "512 Go", prix: 2589 },
  { cap: "1 To", prix: 3089 },
  { cap: "2 To", prix: 3839 },
];
const COLS = [
  { col: "Ciel nocturne", hex: "#2c3440" },
  { col: "Blanc stellaire", hex: "#eceae4" },
];
const prixDe = (cap) => CAPS.find((c) => c.cap === cap).prix;

const STOCK = {
  "256 Go|Ciel nocturne": 900, "256 Go|Blanc stellaire": 800,
  "512 Go|Ciel nocturne": 1100, "512 Go|Blanc stellaire": 900,
  "1 To|Ciel nocturne": 600, "1 To|Blanc stellaire": 500,
  "2 To|Ciel nocturne": 220, "2 To|Blanc stellaire": 180,
};
// appareils déjà réservés sur le stock de lancement à 14:10
const RES_T1 = {
  "256 Go|Ciel nocturne": 227, "256 Go|Blanc stellaire": 201,
  "512 Go|Ciel nocturne": 277, "512 Go|Blanc stellaire": 227,
  "1 To|Ciel nocturne": 151, "1 To|Blanc stellaire": 126,
  "2 To|Ciel nocturne": 55, "2 To|Blanc stellaire": 45,
};
const LOTS = ["L-2643-B", "L-2644-A", "L-2651-C"];

// chiffres agrégés (France) : a = 16 octobre avant 14:35, b = 16 octobre à 14:35, c = 9 novembre (lignes détaillées comprises)
const AGG = {
  a: { recues: 330, controle: 64, confirmees: 262, janvier: 0, annulees: 4, ca: 820000, stockRes: 262, fab: 0 },
  b: { recues: 6240, controle: 318, confirmees: 5826, janvier: 626, annulees: 96, ca: 15805000, stockRes: 5200, fab: 626 },
  c: { recues: 11420, controle: 0, confirmees: 11196, janvier: 5996, annulees: 224, ca: 31208000, stockRes: 5200, fab: 5996 },
};
// précommandes cumulées le 16 octobre
const COURBE = [["14:00", 0], ["14:05", 820], ["14:10", 1486], ["14:15", 2950], ["14:20", 4120], ["14:25", 5040], ["14:30", 5890], ["14:35", 6240], ["14:45", 6810], ["15:00", 7390]];
const MIX = [["256 Go", 31], ["512 Go", 38], ["1 To", 21], ["2 To", 10]];

const CLIENTS = {
  lea: { nom: "Léa M.", mail: "l••.m•••••@icloud.com", ville: "Lyon 3e", depuis: 2019, offres: false, tel: "06 •• •• •• 41" },
  helene: { nom: "Hélène B.", mail: "h•••.b••••@icloud.com", ville: "Villeurbanne", depuis: 2016, offres: true, tel: "06 •• •• •• 07" },
  ines: { nom: "Inès K.", mail: "i•••.k•••••@gmail.com", ville: "Grenoble", depuis: 2021, offres: false, tel: "07 •• •• •• 58" },
  marc: { nom: "Marc D.", mail: "m•••.d•••••@free.fr", ville: "Annecy", depuis: 2014, offres: true, tel: "06 •• •• •• 90" },
  nora: { nom: "Nora A.", mail: "n•••.a••••@icloud.com", ville: "Lyon 7e", depuis: 2022, offres: false, tel: "06 •• •• •• 13" },
  theo: { nom: "Théo B.", mail: "t••••.b•••@gmail.com", ville: "Saint-Étienne", depuis: 2018, offres: true, tel: "07 •• •• •• 26" },
  julien: { nom: "Julien T.", mail: "j••••.t•••••@orange.fr", ville: "Dijon", depuis: 2020, offres: false, tel: "06 •• •• •• 64" },
  camille: { nom: "Camille R.", mail: "c••••.r••••@icloud.com", ville: "Lyon 6e", depuis: 2017, offres: true, tel: "06 •• •• •• 35" },
  mathis: { nom: "Mathis D.", mail: "m•••.d••••@orange.fr", ville: "Chambéry", depuis: 2023, offres: false, tel: "07 •• •• •• 82" },
  anais: { nom: "Anaïs P.", mail: "a•••••.p••••@gmail.com", ville: "Valence", depuis: 2015, offres: true, tel: "06 •• •• •• 19" },
  sarah: { nom: "Sarah N.", mail: "s••••.n•••@icloud.com", ville: "Paris 11e", depuis: 2012, offres: true, tel: "06 •• •• •• 50" },
  paul: { nom: "Paul G.", mail: "p•••.g•••••@gmail.com", ville: "Marseille", depuis: 2019, offres: false, tel: "06 •• •• •• 77" },
  clement: { nom: "Clément F.", mail: "c••••••.f•••@icloud.com", ville: "Nantes", depuis: 2021, offres: false, tel: "07 •• •• •• 03" },
  lucie: { nom: "Lucie V.", mail: "l••••.v••••@gmail.com", ville: "Lille", depuis: 2016, offres: true, tel: "06 •• •• •• 61" },
  yanis: { nom: "Yanis L.", mail: "y••••.l•••@gmail.com", ville: "Toulouse", depuis: 2020, offres: false, tel: "06 •• •• •• 48" },
  karim: { nom: "Karim S.", mail: "k••••.s••••@icloud.com", ville: "Bordeaux", depuis: 2013, offres: true, tel: "06 •• •• •• 22" },
  lina: { nom: "Lina G.", mail: "l•••.g••••@orange.fr", ville: "Rennes", depuis: 2022, offres: false, tel: "07 •• •• •• 95" },
  romain: { nom: "Romain C.", mail: "r•••••.c••••@orange.fr", ville: "Nice", depuis: 2011, offres: true, tel: "06 •• •• •• 30" },
  elsa: { nom: "Elsa M.", mail: "e•••.m•••••@icloud.com", ville: "Strasbourg", depuis: 2018, offres: false, tel: "06 •• •• •• 86" },
};

/* précommandes détaillées : [heure, statut, infos] ; « controle » = enregistrée dans le CRM et transmise à la finance */
const J23 = { date: "2026-10-23" }, J25 = { date: "2027-01-25", lot: "Fabrication à venir" };
const LIV = "2026-10-23T10:00";
const SEED_ORDERS = [
  ["W150032", "lea", "512 Go", "Ciel nocturne", "Carte bancaire", "ok", "14:02", [["14:02", "controle"], ["14:02", "payee"], ["14:03", "reservee", { ...J23, lot: "L-2643-B" }], ["14:03", "confirmee"]], "7XQ2"],
  ["W150118", "helene", "256 Go", "Blanc stellaire", "Carte bancaire", "ok", "14:07", [["14:07", "controle"], ["14:07", "payee"], ["14:08", "reservee", { ...J23, lot: "L-2644-A" }], ["14:08", "confirmee"]], "2KD8"],
  ["W151467", "julien", "1 To", "Ciel nocturne", "Carte bancaire", "ko", "14:19", [["14:19", "controle"], ["14:20", "refusee"], ["14:20", "annulee"]], null],
  ["W152903", "sarah", "2 To", "Blanc stellaire", "Financement", "ok", "14:31", [["14:31", "controle"], ["14:31", "payee"], ["14:32", "reservee", J25], ["14:32", "confirmee"]], "0GA2"],
  ["W152950", "paul", "512 Go", "Blanc stellaire", "Carte bancaire", "ok", "14:32", [["14:32", "controle"], ["14:48", "payee"], ["14:49", "reservee", J25], ["14:50", "confirmee"]], "7FE1"],
];
// commandes plus anciennes citées par les avis (lues dans l'ERP, hors démonstration)
const ORDER_REF = { W150480: ["512 Go", "Ciel nocturne"], W152388: ["512 Go", "Ciel nocturne"], W152011: ["256 Go", "Ciel nocturne"], W150702: ["2 To", "Ciel nocturne"] };

/* avis reçus par QR code (9 novembre, 09:40) */
const SEED_REVIEWS = [
  ["R-0398", "yanis", "W1497••", "Coffret (après achat)", "2026-11-03T10:14", 3, "Écran et pliure", true, "Une petite ligne apparaît sur le pli de l'écran.", [["2026-11-03T10:14", "defaut"], ["2026-11-03T10:40", "en_analyse"], ["2026-11-04T17:00", "a_informer"], ["2026-11-04T17:40", "clos"]]],
  ["R-0399", "karim", "W1503••", "Courriel J+15", "2026-11-04T08:51", 4, "Charnière", true, "La charnière accroche quand je referme le téléphone.", [["2026-11-04T08:51", "defaut"], ["2026-11-04T09:30", "en_analyse"], ["2026-11-05T11:58", "a_informer"], ["2026-11-05T12:30", "clos"]]],
  ["R-0403", "lina", "W1511••", "Coffret (après achat)", "2026-11-06T09:05", 8, "Autonomie", true, "", [["2026-11-06T09:05", "remercie"]]],
  ["R-0404", null, null, "Table de démonstration", "2026-11-06T12:30", 7, "Prix", false, "", [["2026-11-06T12:30", "statistique"]]],
  ["R-0405", "elsa", "W1508••", "Coffret (après achat)", "2026-11-06T17:48", 4, "Charnière", true, "Jeu dans la charnière depuis une semaine.", [["2026-11-06T17:48", "defaut"], ["2026-11-06T18:30", "en_analyse"], ["2026-11-07T10:58", "a_informer"], ["2026-11-07T11:30", "clos"]]],
  ["R-0406", "anais", "W150480", "Courriel J+15", "2026-11-08T18:22", 3, "Écran et pliure", true, "Le pli de l'écran se voit beaucoup en plein soleil.", [["2026-11-08T18:22", "defaut"], ["2026-11-09T08:30", "en_analyse"]]],
  ["R-0407", "mathis", "W152388", "Coffret (après achat)", "2026-11-09T08:40", 10, "Écran et pliure", true, "Le grand écran ouvert change tout.", [["2026-11-09T08:40", "remercie"]]],
  ["R-0408", "camille", "W152011", "Courriel J+15", "2026-11-09T08:57", 5, "Délai de livraison", true, "Livrée à temps, mais j'ai eu peur de ne l'avoir qu'en janvier.", [["2026-11-09T08:57", "a_recontacter"]]],
  ["R-0409", null, null, "Table de démonstration", "2026-11-09T09:12", 6, "Prix", false, "", [["2026-11-09T09:12", "statistique"]]],
  ["R-0411", "theo", "W150702", "Courriel J+15", "2026-11-09T09:31", 9, "Autonomie", true, "", [["2026-11-09T09:31", "remercie"]]],
];
/* signalements : [n°, réponse, défaut, lot, n° de série, configuration, diagnostic, historique] */
const SEED_SIGNALS = [
  ["Q-0398", "R-0398", "Ligne sur le pli de l'écran intérieur", "L-2644-A", "••••••4LM8", "iPhone Duo 256 Go, Blanc stellaire", "Diagnostic à distance : marque sur le pli de l'écran intérieur.", [["2026-11-03T10:40", "analyse"], ["2026-11-04T16:02", "confirme", { action: "Remplacement de l'écran intérieur", cout: 431 }]]],
  ["Q-0405", "R-0405", "Jeu dans la charnière", "L-2643-B", "••••••5RE2", "iPhone Duo 512 Go, Ciel nocturne", "Diagnostic à distance : couple de serrage de la charnière hors tolérance.", [["2026-11-06T18:30", "analyse"], ["2026-11-07T10:20", "confirme", { action: "Échange de l'appareil", cout: 612 }]]],
  ["Q-0406", "R-0406", "Pli de l'écran très visible", "L-2651-C", "••••••9PL4", "iPhone Duo 512 Go, Ciel nocturne", "Diagnostic à distance : pli de l'écran intérieur plus marqué que la normale. Contrôle en magasin proposé au client.", [["2026-11-09T08:30", "analyse"]]],
  ["Q-0409", "R-0399", "Charnière qui accroche", "L-2643-B", "••••••1QA6", "iPhone Duo 1 To, Ciel nocturne", "Diagnostic à distance : axe de la charnière à remplacer.", [["2026-11-04T09:30", "analyse"], ["2026-11-05T11:15", "confirme", { action: "Remplacement de la charnière", cout: 184 }]]],
];
// coûts de garantie : [signalement, heure à laquelle la finance l'enregistre]
const SEED_COSTS = [["Q-0398", "2026-11-04T17:00"], ["Q-0409", "2026-11-05T11:58"], ["Q-0405", "2026-11-07T10:58"]];
/* suite des maquettes M2.2 à M2.6 (Léa, commande W150032) : remplacée dès qu'on agit soi-même */
const SCRIPT_P2 = {
  review: ["R-0412", "lea", "W150032", "Coffret (après achat)", "2026-11-09T09:43", 4, "Charnière", true, "Un léger jeu dans la charnière depuis quelques jours.", [["2026-11-09T09:43", "defaut"], ["2026-11-09T09:58", "en_analyse"]]],
  signal: ["Q-0412", "R-0412", "Jeu dans la charnière", "L-2643-B", "••••••7XQ2", "iPhone Duo 512 Go, Ciel nocturne", "Diagnostic à distance : couple de serrage de la charnière hors tolérance. Contrôle en magasin proposé au client.", [["2026-11-09T09:58", "analyse"], ["2026-11-09T10:05", "confirme", { action: "Échange de l'appareil", cout: 612 }]]],
};

const LOTS_BASE = [["L-2643-B", "semaine 41", 4200, 13, 9], ["L-2644-A", "semaine 41", 3900, 6, 2], ["L-2651-C", "semaine 42", 4100, 3, 1], ["L-2660-A", "semaine 43", 4300, 1, 0]];
const MOTIFS = ["Prix", "Délai de livraison", "Charnière", "Écran et pliure", "Autonomie", "Autre"];
const DEFAUTS = ["Charnière", "Écran et pliure"];
const ACTIONS = [["Échange de l'appareil", 612], ["Remplacement de la charnière", 184], ["Remplacement de l'écran intérieur", 431]];

// tableau de bord de satisfaction (semaine du 2 au 8 novembre) et réponses du 9 novembre avant 09:43
const SAT = { rep: 1842, taux: 31, moy: 8.4, satis: 1584, defauts: 77, confirmes: 41, recontact: 19, couts: 21484,
  motifs: { "Prix": 80, "Délai de livraison": 70, "Charnière": 46, "Écran et pliure": 31, "Autonomie": 18, "Autre": 13 },
  semaines: [["S43", 8.9], ["S44", 8.7], ["S45", 8.4]],
  jour: { rep: 262, anonymes: 41, moy: 8.4168, insatisfaits: 36, recontacter: 12, transmis: 5 } };

const CAMPAGNES = [
  ["Keynote et page iPhone Duo (apple.com/fr)", "depuis le 9 sept.", "Faire connaître", "940 000 visites", "—", "48 %"],
  ["Série de sketchs TikTok (@apple)", "9 sept. → 23 oct.", "Montrer les usages", "3,1 M de vues", "82 000 clics", "11 %"],
  ["Instagram et Reels", "9 sept. → 23 oct.", "Montrer les usages", "1,2 M de vues", "36 000 clics", "6 %"],
  ["Courriel aux clients ayant accepté les offres", "14 oct.", "Annoncer l'ouverture", "410 000 envois", "38 % d'ouverture", "21 %"],
  ["Magasins : tables de démonstration", "depuis le 23 oct.", "Faire essayer", "20 magasins", "QR code d'avis", "14 %"],
];
const PLAN = [["S02 (11 → 17 janv.)", 1800], ["S03 (18 → 24 janv.)", 2400], ["S04 (25 → 31 janv.)", 2200], ["S05 (1er → 7 févr.)", 2600]];

/* vues acteur (M0) : chaque acteur ne voit que ses écrans */
const ACTEURS = {
  client: { nom: "Client", role: "Léa M. · cliente (fictive)", ecrans: ["precommander", "precommandes", "avis", "donnees"] },
  marketing: { nom: "Marketing et ventes", role: "Ventes en ligne, CRM, direction marketing", ecrans: ["precommandes", "avis", "suivi", "clients", "lancement", "satisfaction", "plan", "distributeurs"] },
  finance: { nom: "Finance", role: "Contrôle de gestion", ecrans: ["paiements", "garantie", "budgets", "satisfaction"] },
  production: { nom: "Production", role: "Chaîne d'approvisionnement et qualité", ecrans: ["stock", "qualite", "fabrication", "satisfaction"] },
};

/* Distributeurs (noms fictifs) : [nom, type, stock alloué pour le 23 octobre, part écoulée au 9 novembre] */
const DISTRIBS = [["Néo Télécom", "Opérateur télécom", 600, 0.83], ["Opéra Mobile", "Opérateur télécom", 450, 0.79], ["Hexa Télécom", "Opérateur télécom", 380, 0.71], ["Pomme & Co", "Revendeur agréé", 220, 0.88]];
const ALLOC_NEO = { "256 Go|Ciel nocturne": 110, "256 Go|Blanc stellaire": 90, "512 Go|Ciel nocturne": 130, "512 Go|Blanc stellaire": 110, "1 To|Ciel nocturne": 60, "1 To|Blanc stellaire": 50, "2 To|Ciel nocturne": 30, "2 To|Blanc stellaire": 20 };

/* Échanges hors des deux processus : [heure, émetteur, récepteur, information, outil, flux du dossier, processus] */
const FLUX_SEED = [
  ["2026-09-09T19:00", "Direction marketing produit", "Communication et réseaux sociaux", "Messages et budget des campagnes de lancement", "Courriel interne", "A3-5", ""],
  ["2026-10-12T09:00", "Direction marketing produit", "Ventes", "Prix, date d'ouverture des précommandes et offres", "CRM", "A3-4", "P1"],
  ["2026-10-14T10:00", "Ventes", "Distributeurs", "Stocks alloués pour la mise en vente du 23 octobre", "EDI", "A3-13 · A1-3", ""],
  ["2026-10-15T18:00", "Communication et réseaux sociaux", "Relation client et données", "Audience des campagnes TikTok et Instagram", "CRM", "A3-7", ""],
  ["2026-10-16T13:30", "Production", "Ventes", "Stock de lancement disponible : 5 200 appareils", "ERP → CRM", "A3-12 · A2-4", "P1"],
  ["2026-10-16T14:28", "Production", "Ventes", "Stock de lancement épuisé : nouvelle date de livraison le 25 janvier 2027", "ERP → CRM", "A3-12 · A2-4", "P1"],
  ["2026-11-02T08:00", "Relation client et données", "Direction marketing produit", "Tableau de bord de satisfaction de la semaine 44", "Tableau de bord", "A3-18", "P2"],
  ["2026-11-05T08:00", "Distributeurs", "Ventes", "Relevé des ventes de la veille", "EDI", "A3-13 · A1-3", ""],
  ["2026-11-06T08:00", "Distributeurs", "Ventes", "Relevé des ventes de la veille", "EDI", "A3-13 · A1-3", ""],
  ["2026-11-06T09:00", "Relation client et données", "Communication et réseaux sociaux", "Segments de clients à cibler (clients satisfaits ayant accepté les offres)", "CRM", "A3-8", ""],
  ["2026-11-07T08:00", "Distributeurs", "Ventes", "Relevé des ventes de la veille", "EDI", "A3-13 · A1-3", ""],
  ["2026-11-08T08:00", "Distributeurs", "Ventes", "Relevé des ventes de la veille", "EDI", "A3-13 · A1-3", ""],
  ["2026-11-09T08:00", "Distributeurs", "Ventes", "Relevé des ventes de la veille", "EDI", "A3-13 · A1-3", ""],
  ["2026-11-09T08:00", "Relation client et données", "Direction marketing produit", "Tableau de bord de satisfaction de la semaine 45", "Tableau de bord", "A3-18", "P2"],
];
const PARTENAIRES = {
  banque: { nom: "Banque du client", role: "Service d'autorisation des paiements", couleur: "#1d1d1f", ecran: "Demandes d'autorisation" },
  distributeur: { nom: "Néo Télécom", role: "Distributeur agréé · espace partenaire", couleur: "#0a7f5a", ecran: "Stock alloué et ventes" },
};
