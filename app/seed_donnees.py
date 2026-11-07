"""Listes de référence pour le pré-remplissage (données fictives mais réalistes)."""

PRENOMS = (
    "Léa Emma Chloé Manon Camille Inès Jade Louise Alice Lina Zoé Sarah Juliette Clara Anna Rose Ambre Léna Mila Julia "
    "Lou Eva Agathe Margaux Pauline Marie Lucie Laura Mathilde Charlotte Océane Elise Héloïse Noémie Salomé Romane "
    "Justine Maëlle Capucine Victoire Yasmine Amira Nora Leïla Sofia Hanna Clémence Apolline Margot Anaïs "
    "Lucas Hugo Louis Gabriel Arthur Jules Adam Raphaël Léo Nathan Ethan Paul Tom Noah Théo Mathis Maël Sacha Enzo "
    "Timéo Antoine Maxime Thomas Alexandre Baptiste Clément Romain Julien Nicolas Pierre Quentin Victor Valentin "
    "Bastien Samuel Yanis Rayan Ilyes Mehdi Karim Sofiane Malik Benjamin Simon Martin Matthieu Florian Guillaume "
    "Kylian Axel Mathéo Noé Aaron Elias Nolan Léon Isaac Sami"
).split()

NOMS = (
    "Martin Bernard Thomas Petit Robert Richard Durand Dubois Moreau Laurent Simon Michel Lefebvre Leroy Roux David "
    "Bertrand Morel Fournier Girard Bonnet Dupont Lambert Fontaine Rousseau Vincent Muller Lefèvre Faure André Mercier "
    "Blanc Guérin Boyer Garnier Chevalier François Legrand Gauthier Garcia Perrin Robin Clément Morin Nicolas Henry "
    "Roussel Mathieu Gautier Masson Marchand Duval Denis Dumont Marie Lemaire Noël Meyer Dufour Meunier Brun Blanchard "
    "Giraud Joly Rivière Lucas Brunet Gaillard Barbier Arnaud Martinez Gérard Roche Renard Schmitt Roy Leroux Colin "
    "Vidal Caron Picard Roger Fabre Aubert Lemoine Renaud Dumas Lacroix Olivier Philippe Bourgeois Pierre Benoît Rey "
    "Leclerc Payet Rolland Leclercq Guillaume Lecomte Lopez Jean Dupuy Guillot Hubert Berger Carpentier Sanchez "
    "Dupuis Moulin Louis Deschamps Huet Vasseur Perez Boucher Fleury Royer Klein Jacquet Adam Paris Poirier Marty "
    "Aubry Guyot Carré Charles Renault Charpentier Ménard Maillard Baron Bertin Bailly Hervé Schneider Fernandez "
    "Le Gall Collet Léger Bouvier Julien Prévost Millet Perrot Daniel Le Roux Cousin Germain Breton Besson Langlois "
    "Rémy Le Goff Pelletier Lévêque Perrier Leblanc Barré Lebrun Marchal Weber Mallet Hamon Boulanger Jacob Monnier "
    "Michaud Rodriguez Guichard Gillet Étienne Grondin Poulain Tessier Chevallier Collin Chauvin Da Silva Bouchet "
    "Gay Lemaître Benard Marécha Humbert Reynaud Antoine Hoarau Perret Barthélemy Cordier Pichon Lejeune Gilbert "
    "Lamy Delaunay Pasquier Carlier Laporte Benali Haddad Nguyen Diallo Ferreira Martins Rossi Bensaïd"
).split()

# (ville, code postal, poids) — surpondération des grandes métropoles (clientèle premium)
VILLES = [
    ("Paris", "750", 160), ("Boulogne-Billancourt", "92100", 14), ("Neuilly-sur-Seine", "92200", 8),
    ("Levallois-Perret", "92300", 7), ("Issy-les-Moulineaux", "92130", 7), ("Versailles", "78000", 8),
    ("Saint-Denis", "93200", 6), ("Montreuil", "93100", 7), ("Vincennes", "94300", 5), ("Créteil", "94000", 5),
    ("Lyon", "6900", 55), ("Villeurbanne", "69100", 10), ("Marseille", "130", 40), ("Aix-en-Provence", "13100", 9),
    ("Toulouse", "31000", 32), ("Nice", "06000", 22), ("Nantes", "44000", 24), ("Montpellier", "34000", 22),
    ("Strasbourg", "67000", 18), ("Bordeaux", "33000", 26), ("Lille", "59000", 22), ("Rennes", "35000", 17),
    ("Reims", "51100", 8), ("Toulon", "83000", 8), ("Saint-Étienne", "42000", 7), ("Le Havre", "76600", 6),
    ("Grenoble", "38000", 12), ("Dijon", "21000", 8), ("Angers", "49000", 8), ("Nîmes", "30000", 6),
    ("Clermont-Ferrand", "63000", 8), ("Brest", "29200", 6), ("Tours", "37000", 8), ("Amiens", "80000", 5),
    ("Limoges", "87000", 5), ("Annecy", "74000", 8), ("Perpignan", "66000", 5), ("Metz", "57000", 6),
    ("Besançon", "25000", 5), ("Orléans", "45000", 6), ("Rouen", "76000", 7), ("Mulhouse", "68100", 4),
    ("Caen", "14000", 6), ("Nancy", "54000", 6), ("La Rochelle", "17000", 5), ("Pau", "64000", 4),
    ("Bayonne", "64100", 4), ("Avignon", "84000", 4), ("Poitiers", "86000", 4), ("Le Mans", "72000", 4),
]

DOMAINES = [("icloud.com", 46), ("gmail.com", 30), ("orange.fr", 7), ("outlook.fr", 5), ("free.fr", 4),
            ("hotmail.fr", 4), ("sfr.fr", 2), ("laposte.net", 1), ("me.com", 1)]

# (appareil, année, plateforme, poids parmi les inscrits « Me prévenir »)
APPAREILS = [
    ("iPhone 17 Pro Max", 2025, "iOS", 5), ("iPhone 17 Pro", 2025, "iOS", 5), ("iPhone 17", 2025, "iOS", 4),
    ("iPhone Air", 2025, "iOS", 3), ("iPhone 16 Pro Max", 2024, "iOS", 6), ("iPhone 16 Pro", 2024, "iOS", 6),
    ("iPhone 16", 2024, "iOS", 5), ("iPhone 15 Pro Max", 2023, "iOS", 7), ("iPhone 15 Pro", 2023, "iOS", 6),
    ("iPhone 15", 2023, "iOS", 5), ("iPhone 14 Pro", 2022, "iOS", 6), ("iPhone 14", 2022, "iOS", 4),
    ("iPhone 13 Pro", 2021, "iOS", 6), ("iPhone 13", 2021, "iOS", 5), ("iPhone 12", 2020, "iOS", 4),
    ("iPhone 11", 2019, "iOS", 3),
    ("Samsung Galaxy Z Fold7", 2025, "Android", 4), ("Samsung Galaxy Z Fold6", 2024, "Android", 3),
    ("Samsung Galaxy Z Flip7", 2025, "Android", 2), ("Samsung Galaxy S25 Ultra", 2025, "Android", 3),
    ("Samsung Galaxy S24", 2024, "Android", 2), ("Google Pixel 10 Pro", 2025, "Android", 2),
    ("Google Pixel 9 Pro Fold", 2024, "Android", 1), ("Xiaomi 15", 2025, "Android", 1),
    ("Huawei Mate X6", 2024, "Android", 1), ("OnePlus 13", 2025, "Android", 1),
]

# Grille Apple Trade In (valeurs fictives, « jusqu'à », parfait état)
REPRISE = [
    ("iPhone 17 Pro Max", "Apple", 830), ("iPhone 17 Pro", "Apple", 730), ("iPhone 17", "Apple", 480),
    ("iPhone Air", "Apple", 560), ("iPhone 16 Pro Max", "Apple", 650), ("iPhone 16 Pro", "Apple", 570),
    ("iPhone 16", "Apple", 400), ("iPhone 15 Pro Max", "Apple", 500), ("iPhone 15 Pro", "Apple", 430),
    ("iPhone 15", "Apple", 300), ("iPhone 14 Pro", "Apple", 330), ("iPhone 14", "Apple", 230),
    ("iPhone 13 Pro", "Apple", 260), ("iPhone 13", "Apple", 170), ("iPhone 12", "Apple", 110),
    ("iPhone 11", "Apple", 70),
    ("Samsung Galaxy Z Fold7", "Samsung", 650), ("Samsung Galaxy Z Fold6", "Samsung", 480),
    ("Samsung Galaxy Z Flip7", "Samsung", 320), ("Samsung Galaxy S25 Ultra", "Samsung", 520),
    ("Samsung Galaxy S24", "Samsung", 300), ("Google Pixel 10 Pro", "Google", 420),
    ("Google Pixel 9 Pro Fold", "Google", 430), ("Xiaomi 15", "Xiaomi", 260), ("Huawei Mate X6", "Huawei", 380),
    ("OnePlus 13", "OnePlus", 280), ("Autre smartphone", "Autre", 40),
]
ETATS_REPRISE = [("parfait", "Parfait état", 1.0), ("bon", "Bon état (rayures légères)", 0.85),
                 ("fissure", "Écran fissuré", 0.35)]

MODES_PAIEMENT = {
    "cb": "Carte bancaire",
    "apple_pay": "Apple Pay",
    "cetelem_10x": "Paiement en 10 fois sans frais (Cetelem)",
    "cetelem_24m": "Financement sur 24 mois (Cetelem)",
}

# Influenceurs fictifs (pseudonymes inventés)
INFLUENCEURS = [
    ("@lea.pixels", "Léa Morin", "TikTok", 1240000, 6.8, "Tech & lifestyle", "Paris", 18000),
    ("@hugo.unbox", "Hugo Lefèvre", "YouTube", 860000, 5.1, "Tests et déballages", "Lyon", 16000),
    ("@camille.cuisinevite", "Camille Petit", "TikTok", 2100000, 7.9, "Cuisine du quotidien", "Bordeaux", 24000),
    ("@yanis.fit", "Yanis Benamar", "Instagram", 640000, 4.6, "Sport et yoga", "Marseille", 9000),
    ("@mila.studio", "Mila Garnier", "TikTok", 930000, 8.4, "Montage et création vidéo", "Paris", 14000),
    ("@theo.technologie", "Théo Marchand", "YouTube", 1480000, 4.2, "High-tech", "Nantes", 22000),
    ("@sarah.ailleurs", "Sarah Klein", "Instagram", 770000, 3.9, "Voyage", "Nice", 11000),
    ("@nathan.manette", "Nathan Roche", "TikTok", 1050000, 6.1, "Jeu vidéo", "Lille", 15000),
    ("@ines.revise", "Inès Dubois", "TikTok", 410000, 9.2, "Études et productivité", "Toulouse", 6000),
    ("@lucas.objectif", "Lucas Fournier", "Instagram", 520000, 5.5, "Photographie", "Annecy", 8000),
    ("@manon.entreprend", "Manon Girard", "LinkedIn", 180000, 3.1, "Entrepreneuriat", "Paris", 5000),
    ("@jade.dressing", "Jade Lambert", "TikTok", 1620000, 7.2, "Mode", "Paris", 21000),
    ("@max.codes", "Maxime Chevalier", "YouTube", 290000, 6.6, "Développement d'apps", "Rennes", 5000),
    ("@emma.maison", "Emma Bonnet", "Instagram", 350000, 4.4, "Famille", "Strasbourg", 6000),
    ("@noah.seances", "Noah Mercier", "TikTok", 880000, 7.7, "Cinéma et séries", "Montpellier", 13000),
    ("@chloe.respire", "Chloé Faure", "Instagram", 470000, 5.8, "Bien-être", "Grenoble", 7000),
]

# Vidéos TikTok d'Apple (campagne de lancement) : (date, titre, concept, poids de vues)
VIDEOS_APPLE = [
    ("2026-09-11T18:00:00", "L'iPhone Duo fait son yoga", "Positions posé, relevé, ouvert", 1.35),
    ("2026-09-11T18:00:00", "Un mini-portable en terrasse", "Usage bureau nomade au café", 1.10),
    ("2026-09-11T18:00:00", "Ce soir, cinéma de poche", "Grand écran, série Silo sur Apple TV", 1.25),
    ("2026-09-11T18:00:00", "Plié en une seconde", "Démonstration de la charnière", 0.95),
    ("2026-09-11T18:00:00", "Le selfie sans les mains", "Mode posé + appareil photo", 0.85),
    ("2026-09-25T12:00:00", "La recette sur deux écrans", "Cuisine : recette + minuteur", 0.90),
    ("2026-09-25T12:00:00", "Le match en grand", "Matchs MLS sur grand écran", 0.70),
    ("2026-09-25T12:00:00", "Le bureau qui tient dans la poche", "Productivité, multitâche", 0.65),
    ("2026-10-06T18:00:00", "Passer d'Android en 5 minutes", "Conversion des utilisateurs Android", 0.75),
    ("2026-10-06T18:00:00", "La charnière, testée dans la poche", "Résistance du titane", 0.80),
    ("2026-10-13T12:00:00", "Votre ancien téléphone vaut de l'or", "Offre de reprise Apple Trade In", 0.60),
    ("2026-10-13T12:00:00", "Payez en 10 fois sans frais", "Paiement en plusieurs fois", 0.55),
]

# Applications adaptées au double écran (noms fictifs)
APPS = [
    ("Carnet+", "Studio Carnet", "Productivité"), ("Recettes Duo", "Miam Labs", "Cuisine"),
    ("Croquis Pro", "Atelier Nord", "Création"), ("Lumière RAW", "Pixel & Co", "Photo"),
    ("Tableur Nomade", "Calc SAS", "Productivité"), ("Ciné Club", "Écran Libre", "Divertissement"),
    ("Partition Live", "Mélodia", "Musique"), ("Atlas Rando", "Sentiers SAS", "Voyage"),
    ("Banque Clair", "Fintech Lyon", "Finance"), ("Montage Express", "Clipline", "Vidéo"),
    ("Révisions Duo", "EduNova", "Éducation"), ("Chess Duo", "Gambit Studio", "Jeux"),
    ("Magazine+", "Kiosque Numérique", "Actualités"), ("Plan Métro", "MobiCity", "Navigation"),
    ("Yoga Flow", "Zenapp", "Santé"), ("Mail Split", "Courrier Labs", "Productivité"),
    ("BD Infinie", "Bulles SAS", "Livres"), ("Stratège", "Polygone Games", "Jeux"),
    ("Code Mobile", "Devbox", "Développeurs"), ("Tableau Blanc", "Collab Studio", "Productivité"),
    ("Maison Connectée", "Domo FR", "Maison"), ("Course Live", "Runlab", "Sport"),
    ("Recettes du Monde", "Saveurs Apps", "Cuisine"), ("Étoiles", "Astro Lyon", "Éducation"),
    ("Agenda Famille", "Tribu Apps", "Productivité"), ("Mode Studio", "Dressing Lab", "Shopping"),
    ("Langues Duo", "Polyglot SAS", "Éducation"), ("Docs Scan", "Papier Zéro", "Productivité"),
    ("Pixel Art", "Carré Studio", "Création"), ("Podcast Plus", "Onde Courte", "Musique"),
]

# Retombées presse : titres issus des sources du dossier + articles génériques
PRESSE = [
    ("2026-09-09T21:30:00", "Mac4Ever", "Keynote « Surprise and Shine » : Apple dévoile l'iPhone Duo", "positive", 420000),
    ("2026-09-10T08:00:00", "Bbox Mag", "iPhone Duo : prix officiel et date de sortie", "neutre", 310000),
    ("2026-09-10T10:30:00", "Quotidien national (rubrique tech)", "Apple entre enfin sur le marché des pliables", "neutre", 1200000),
    ("2026-09-11T19:00:00", "MacGeneration", "L'iPhone Duo fait son numéro sur TikTok", "positive", 280000),
    ("2026-09-12T09:00:00", "Creative Bloq", "Apple's iPhone Duo TikToks nail foldable phone marketing", "positive", 190000),
    ("2026-09-14T07:30:00", "Magazine économique", "iPhone Duo : un pari à plus de 2 300 euros", "negative", 650000),
    ("2026-09-18T12:00:00", "iPhon.fr", "L'iPhone Duo plie déjà en deux la concurrence", "positive", 240000),
    ("2026-09-21T08:00:00", "Futura Sciences", "L'iPhone Duo ouvre de nouveaux usages", "positive", 520000),
    ("2026-09-24T18:00:00", "Site tech grand public", "Pliure visible : notre premier contact avec l'iPhone Duo", "neutre", 380000),
    ("2026-09-29T09:00:00", "Combak", "Date de sortie de l'iPhone Duo : tout savoir", "neutre", 90000),
    ("2026-10-02T11:00:00", "Magazine conso", "Smartphones pliables : faut-il craquer ?", "neutre", 450000),
    ("2026-10-08T08:30:00", "Quotidien économique", "Mémoire : la flambée des prix pèse sur les smartphones", "negative", 700000),
    ("2026-10-13T10:00:00", "iPhoneSoft", "iPhone Duo : Apple met en avant la reprise et le paiement en 10 fois", "positive", 210000),
    ("2026-10-16T15:10:00", "Mac4Ever", "Précommandes iPhone Duo : les délais s'allongent déjà", "neutre", 360000),
    ("2026-10-17T09:00:00", "Radio d'information", "Ruée sur l'iPhone pliable malgré son prix", "positive", 1500000),
    ("2026-10-23T08:30:00", "Quotidien régional (Lyon)", "Devant l'Apple Part-Dieu, la file des premiers acheteurs", "positive", 260000),
    ("2026-10-24T18:00:00", "Site tech grand public", "Test complet de l'iPhone Duo", "positive", 540000),
    ("2026-10-28T09:00:00", "Mac4Ever", "Aux Emmy Awards, John Ternus sort son iPhone Duo", "positive", 230000),
]

CONCURRENTS = [
    ("Samsung", "Galaxy Z Fold (génération 2026)", 2099.0), ("Samsung", "Galaxy Z Flip (génération 2026)", 1249.0),
    ("Google", "Pixel Pro Fold (génération 2026)", 1899.0), ("Huawei", "Mate X (génération 2026)", 2299.0),
    ("Honor", "Magic V (génération 2026)", 1999.0),
]

SUJETS_SAV = [
    ("Délai de livraison de ma précommande", "avant"), ("Modifier la couleur de ma précommande", "avant"),
    ("Paiement en plusieurs fois refusé", "avant"), ("Estimation de reprise de mon iPhone", "avant"),
    ("Pliure visible de l'écran intérieur", "apres"), ("Activation de l'eSIM", "apres"),
    ("Transfert de données depuis Android", "apres"), ("Compatibilité Apple Pencil", "apres"),
    ("Touch ID ne reconnaît pas mon doigt", "apres"), ("Souscrire AppleCare+ après l'achat", "apres"),
    ("Autonomie inférieure à l'annonce", "apres"), ("Retour sous 14 jours", "apres"),
]
