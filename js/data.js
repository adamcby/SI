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

const CLOCKS = {
  t1: { id: "t1", base: "2026-10-16T14:10", court: "16 oct. · 14:10", titre: "Vendredi 16 octobre 2026, 14:10", legende: "Ouverture des précommandes, stock disponible", stock: true, idBase: 150720 },
  t2: { id: "t2", base: "2026-10-16T14:35", court: "16 oct. · 14:35", titre: "Vendredi 16 octobre 2026, 14:35", legende: "Stock de lancement épuisé à 14:28", stock: false, idBase: 153010 },
  t3: { id: "t3", base: "2026-11-09T09:40", court: "9 nov. · 09:40", titre: "Lundi 9 novembre 2026, 09:40", legende: "Après les premières livraisons", stock: false, idBase: 219400 },
};

// chiffres agrégés (France) à chaque moment, lignes détaillées comprises
const AGG = {
  t1: { recues: 1486, controle: 154, confirmees: 1309, janvier: 0, annulees: 23, ca: 3650801, stockRes: 1309, fab: 0, date: "2026-10-23" },
  t2: { recues: 6240, controle: 318, confirmees: 5826, janvier: 626, annulees: 96, ca: 15805000, stockRes: 5200, fab: 626, date: "2027-01-25" },
  t3: { recues: 11420, controle: 0, confirmees: 11196, janvier: 5996, annulees: 224, ca: 31208000, stockRes: 5200, fab: 5996, date: "2027-01-25" },
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
  ["W150118", "helene", "256 Go", "Blanc stellaire", "Carte bancaire", "ok", "14:04", [["14:04", "controle"], ["14:05", "payee"], ["14:06", "reservee", { ...J23, lot: "L-2644-A" }], ["14:06", "confirmee"]], "2KD8"],
  ["W150480", "anais", "512 Go", "Ciel nocturne", "Carte bancaire", "ok", "14:05", [["14:05", "controle"], ["14:05", "payee"], ["14:06", "reservee", { ...J23, lot: "L-2651-C" }], ["14:07", "confirmee"]], "9PL4"],
  ["W150555", "ines", "1 To", "Ciel nocturne", "Carte bancaire", "ok", "14:06", [["14:06", "controle"], ["14:07", "payee"], ["14:09", "reservee", { ...J23, lot: "L-2643-B" }], ["14:22", "confirmee"]], "4HQ1"],
  ["W150590", "marc", "256 Go", "Ciel nocturne", "Carte bancaire", "ok", "14:08", [["14:08", "controle"], ["14:09", "payee"], ["14:22", "reservee", { ...J23, lot: "L-2644-A" }], ["14:23", "confirmee"]], "6TM3"],
  ["W150611", "nora", "512 Go", "Blanc stellaire", "Financement", "ok", "14:09", [["14:09", "controle"], ["14:22", "payee"], ["14:23", "reservee", { ...J23, lot: "L-2643-B" }], ["14:24", "confirmee"]], "1RW7"],
  ["W150702", "theo", "2 To", "Ciel nocturne", "Carte bancaire", "ok", "14:10", [["14:10", "controle"], ["14:23", "payee"], ["14:24", "reservee", { ...J23, lot: "L-2651-C" }], ["14:24", "confirmee"]], "8CV5"],
  ["W151467", "julien", "1 To", "Ciel nocturne", "Carte bancaire", "ko", "14:19", [["14:19", "controle"], ["14:20", "refusee"], ["14:20", "annulee"]], null],
  ["W152011", "camille", "256 Go", "Ciel nocturne", "Carte bancaire", "ok", "14:24", [["14:24", "controle"], ["14:25", "payee"], ["14:26", "reservee", { ...J23, lot: "L-2651-C" }], ["14:26", "confirmee"]], "3JN6"],
  ["W152388", "mathis", "512 Go", "Ciel nocturne", "Carte bancaire", "ok", "14:27", [["14:27", "controle"], ["14:27", "payee"], ["14:28", "reservee", { ...J23, lot: "L-2643-B" }], ["14:28", "confirmee"]], "5BX9"],
  ["W152903", "sarah", "2 To", "Blanc stellaire", "Financement", "ok", "14:31", [["14:31", "controle"], ["14:31", "payee"], ["14:32", "reservee", J25], ["14:32", "confirmee"]], "0GA2"],
  ["W152950", "paul", "512 Go", "Blanc stellaire", "Carte bancaire", "ok", "14:32", [["14:32", "controle"], ["14:48", "payee"], ["14:49", "reservee", J25], ["14:50", "confirmee"]], "7FE1"],
  ["W152977", "clement", "1 To", "Blanc stellaire", "Carte bancaire", "ok", "14:33", [["14:33", "controle"], ["14:34", "payee"], ["14:48", "reservee", J25], ["14:49", "confirmee"]], "2UY8"],
  ["W152990", "lucie", "256 Go", "Ciel nocturne", "Carte bancaire", "ok", "14:34", [["14:34", "controle"], ["14:34", "payee"], ["14:35", "reservee", J25], ["14:50", "confirmee"]], "4SZ0"],
];

/* avis reçus par QR code (9 novembre, 09:40) */
const SEED_REVIEWS = [
  ["R-0398", "yanis", "W1497••", "Coffret (QR code)", "2026-11-03T10:14", 3, "Écran et pliure", true, "Une petite ligne apparaît sur le pli de l'écran.", [["2026-11-03T10:14", "defaut"], ["2026-11-03T10:40", "en_analyse"], ["2026-11-04T17:00", "a_informer"], ["2026-11-04T17:40", "clos"]]],
  ["R-0399", "karim", "W1503••", "Courriel J+15", "2026-11-04T08:51", 4, "Charnière", true, "La charnière accroche quand je referme le téléphone.", [["2026-11-04T08:51", "defaut"], ["2026-11-04T09:30", "en_analyse"], ["2026-11-05T11:58", "a_informer"], ["2026-11-05T12:30", "clos"]]],
  ["R-0402", "romain", "W1505••", "Courriel J+15", "2026-11-05T19:40", 2, "Charnière", true, "La charnière craque à l'ouverture.", [["2026-11-05T19:40", "defaut"], ["2026-11-06T09:05", "en_analyse"]]],
  ["R-0403", "lina", "W1511••", "Coffret (QR code)", "2026-11-06T09:05", 8, "Autonomie", true, "", [["2026-11-06T09:05", "remercie"]]],
  ["R-0404", null, null, "Table de démonstration", "2026-11-06T12:30", 7, "Prix", false, "", [["2026-11-06T12:30", "statistique"]]],
  ["R-0405", "elsa", "W1508••", "Coffret (QR code)", "2026-11-06T17:48", 4, "Charnière", true, "Jeu dans la charnière depuis une semaine.", [["2026-11-06T17:48", "defaut"], ["2026-11-06T18:30", "en_analyse"], ["2026-11-07T10:58", "a_informer"], ["2026-11-07T11:30", "clos"]]],
  ["R-0406", "anais", "W150480", "Courriel J+15", "2026-11-08T18:22", 3, "Écran et pliure", true, "Le pli de l'écran se voit beaucoup en plein soleil.", [["2026-11-08T18:22", "defaut"], ["2026-11-09T08:30", "en_analyse"]]],
  ["R-0407", "mathis", "W152388", "Coffret (QR code)", "2026-11-09T08:40", 10, "Écran et pliure", true, "Le grand écran ouvert change tout.", [["2026-11-09T08:40", "remercie"]]],
  ["R-0408", "camille", "W152011", "Courriel J+15", "2026-11-09T08:57", 5, "Délai de livraison", true, "Livrée à temps, mais j'ai eu peur de ne l'avoir qu'en janvier.", [["2026-11-09T08:57", "a_recontacter"]]],
  ["R-0409", null, null, "Table de démonstration", "2026-11-09T09:12", 6, "Prix", false, "", [["2026-11-09T09:12", "statistique"]]],
  ["R-0410", "helene", "W150118", "Coffret (QR code)", "2026-11-09T09:20", 5, "Charnière", true, "La charnière est un peu dure à ouvrir.", [["2026-11-09T09:20", "defaut"]]],
  ["R-0411", "theo", "W150702", "Courriel J+15", "2026-11-09T09:31", 9, "Autonomie", true, "", [["2026-11-09T09:31", "remercie"]]],
];
const SEED_SIGNALS = [
  ["Q-0398", "R-0398", "Ligne sur le pli de l'écran intérieur", "L-2644-A", "••••••4LM8", [["2026-11-03T10:40", "analyse"], ["2026-11-04T16:02", "confirme", { action: "Remplacement de l'écran intérieur", cout: 431 }]]],
  ["Q-0399", "R-0399", "Charnière qui accroche", "L-2643-B", "••••••1QA6", [["2026-11-04T09:30", "analyse"], ["2026-11-05T11:15", "confirme", { action: "Remplacement de la charnière", cout: 184 }]]],
  ["Q-0402", "R-0402", "Charnière qui craque", "L-2643-B", "••••••8WD3", [["2026-11-06T09:05", "analyse"], ["2026-11-08T15:30", "confirme", { action: "Échange de l'appareil", cout: 612 }]]],
  ["Q-0405", "R-0405", "Jeu dans la charnière", "L-2643-B", "••••••5RE2", [["2026-11-06T18:30", "analyse"], ["2026-11-07T10:20", "confirme", { action: "Échange de l'appareil", cout: 612 }]]],
  ["Q-0406", "R-0406", "Pli de l'écran très visible", "L-2651-C", "••••••9PL4", [["2026-11-09T08:30", "analyse"]]],
];
// coûts de garantie : [signalement, heure à laquelle la finance l'enregistre (null = à enregistrer)]
const SEED_COSTS = [["Q-0398", "2026-11-04T17:00"], ["Q-0399", "2026-11-05T11:58"], ["Q-0405", "2026-11-07T10:58"], ["Q-0402", null]];

const LOTS_BASE = [["L-2643-B", "semaine 41", 4200, 14, 9], ["L-2644-A", "semaine 41", 3900, 6, 2], ["L-2651-C", "semaine 42", 4100, 3, 1], ["L-2660-A", "semaine 43", 4300, 1, 0]];
const MOTIFS = ["Prix", "Délai de livraison", "Charnière", "Écran et pliure", "Autonomie", "Autre"];
const DEFAUTS = ["Charnière", "Écran et pliure"];
const ACTIONS = [["Échange de l'appareil", 612], ["Remplacement de la charnière", 184], ["Remplacement de l'écran intérieur", 431]];

// tableau de bord de satisfaction (du 2 au 9 novembre), avant les réponses saisies dans la démonstration
const SAT = { rep: 1842, taux: 31, moy: 8.4, satis: 1584, defauts: 77, confirmes: 41, recontact: 19, couts: 21484,
  motifs: { "Prix": 80, "Délai de livraison": 70, "Charnière": 46, "Écran et pliure": 31, "Autonomie": 18, "Autre": 13 },
  semaines: [["S43", 8.9], ["S44", 8.7], ["S45", 8.4]],
  jour: { rep: 263, anonymes: 41, moy: 8.4, insatisfaits: 37, recontacter: 12, transmis: 5 } };

const CAMPAGNES = [
  ["Keynote et page iPhone Duo (apple.com/fr)", "depuis le 9 sept.", "Faire connaître", "940 000 visites", "—", "48 %"],
  ["Série de sketchs TikTok (@apple)", "9 sept. → 23 oct.", "Montrer les usages", "3,1 M de vues", "82 000 clics", "11 %"],
  ["Instagram et Reels", "9 sept. → 23 oct.", "Montrer les usages", "1,2 M de vues", "36 000 clics", "6 %"],
  ["Courriel aux clients ayant accepté les offres", "14 oct.", "Annoncer l'ouverture", "410 000 envois", "38 % d'ouverture", "21 %"],
  ["Magasins : tables de démonstration", "depuis le 23 oct.", "Faire essayer", "20 magasins", "QR code d'avis", "14 %"],
];
const PLAN = [["S02 (11 → 17 janv.)", 1800], ["S03 (18 → 24 janv.)", 2400], ["S04 (25 → 31 janv.)", 2200], ["S05 (1er → 7 févr.)", 2600]];

const PROFILS = {
  vendeur: { nom: "Hugo R.", role: "Vendeur · boutique en ligne", couleur: "#0071e3", ecrans: ["precommandes", "clients"] },
  conseiller: { nom: "Mélanie D.", role: "Conseillère relation client", couleur: "#34a853", ecrans: ["avis", "suivi", "clients"] },
  marketing: { nom: "Claire V.", role: "Responsable marketing produit", couleur: "#bf4800", ecrans: ["lancement", "satisfaction", "campagnes"] },
  stock: { nom: "Karim B.", role: "Gestionnaire de stock · production", couleur: "#5e5ce6", ecrans: ["stock", "plan"] },
  qualite: { nom: "Lucas F.", role: "Technicien qualité · production", couleur: "#af52de", ecrans: ["qualite"] },
  controleur: { nom: "Sophie L.", role: "Contrôleuse de gestion · finance", couleur: "#d97706", ecrans: ["paiements", "garantie", "ca"] },
};
const ECRANS = {
  precommandes: { t: "Précommandes", code: "M1.2" },
  clients: { t: "Fiches clients" },
  avis: { t: "Avis reçus", code: "M2.4" },
  suivi: { t: "Dossiers de suivi" },
  lancement: { t: "Tableau de bord du lancement" },
  satisfaction: { t: "Tableau de bord de satisfaction", code: "M2.7" },
  campagnes: { t: "Campagnes et audience" },
  stock: { t: "Stock et réservations", code: "M1.4" },
  plan: { t: "Plan de production" },
  qualite: { t: "Signalements qualité", code: "M2.5" },
  paiements: { t: "Contrôle des paiements", code: "M1.3" },
  garantie: { t: "Coûts de garantie", code: "M2.6" },
  ca: { t: "Chiffre d'affaires prévisionnel" },
  processus: { t: "Processus" },
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
PROFILS.vendeur.ecrans.push("distributeurs");
Object.assign(ECRANS, { distributeurs: { t: "Distributeurs" }, echanges: { t: "Échanges entre services" } });
const PARTENAIRES = {
  banque: { nom: "Banque du client", role: "Service d'autorisation des paiements", couleur: "#1d1d1f", ecran: "Demandes d'autorisation" },
  distributeur: { nom: "Néo Télécom", role: "Distributeur agréé · espace partenaire", couleur: "#0a7f5a", ecran: "Stock alloué et ventes" },
};
