"""Référentiel du SI — source unique de vérité du prototype.

Tout ce qui est affiché ou exécuté dans l'application provient des modèles
produits en Séances 1 à 5 (dossier « Projet_SI_Apple_iPhone_Duo ») :

* Fig. 1 — diagramme de contexte (12 acteurs externes)           -> FLUX « FE-xx »
* Fig. 2 — flux internes marketing / production / finance / DG    -> FLUX « FI-xx »
* Fig. 3 — circulation de l'information dans la direction marketing -> FLUX « FM-xx »
* Fig. 4 — BPMN P1 : gestion des précommandes du 16 octobre       -> PROCESSUS["P1"]
* Fig. 5 — BPMN P2 : campagne TikTok et mesure de son efficacité  -> PROCESSUS["P2"]

Le registre ECRANS relie chaque maquette (Séances 6-7) aux tâches BPMN et aux
flux qu'elle illustre : c'est lui qui alimente le mode « Inspection maquette ».
"""
from typing import Dict, List, Optional

# ---------------------------------------------------------------------------
# Projet
# ---------------------------------------------------------------------------
PROJET = {
    "entreprise": "Apple",
    "produit": "iPhone Duo",
    "fonction": "Marketing",
    "fonctions_liees": ["Production", "Finance"],
    "universite": "Université Jean Moulin Lyon 3 — IAE Lyon",
    "formation": "Licence 2 Gestion et Management",
    "td": "Fondamentaux des systèmes d'information",
    "annee": "2026-2027",
    "problematique": (
        "En quoi le système d'information marketing d'Apple lui permet-il de piloter "
        "et d'évaluer le lancement de l'iPhone Duo avant même sa commercialisation ?"
    ),
    "dates": {
        "keynote": "2026-09-09T19:00:00",
        "precommandes": "2026-10-16T14:00:00",
        "sortie": "2026-10-23T08:00:00",
    },
    "avertissement": (
        "Prototype pédagogique réalisé dans le cadre d'un TD universitaire. "
        "Données fictives ou reconstituées. Projet non affilié à Apple Inc."
    ),
}

# Séances du TD (contenu reconstitué d'après le document « TD SI » et le dossier)
SEANCES = {
    "S1": {"titre": "Présentation de l'entreprise et SWOT",
           "apport": "Fiche d'identité, historique, chiffres clés, clients, matrice SWOT (Xerfi)."},
    "S2": {"titre": "Le SI de la fonction marketing",
           "apport": "Choix et justification de la fonction, rôles, interactions (production, finance), outils CRM/ERP, KPI."},
    "S3": {"titre": "Stratégie digitale",
           "apport": "Analyse de la page iPhone Duo sur apple.com et de la campagne TikTok, tableau de synthèse."},
    "S4": {"titre": "Acteurs et flux d'information",
           "apport": "Acteurs internes/externes, diagramme de contexte (Fig. 1), flux internes (Fig. 2), flux marketing (Fig. 3)."},
    "S5": {"titre": "Modélisation des processus (BPMN)",
           "apport": "P1 précommandes du 16/10 (Fig. 4), P2 campagne TikTok (Fig. 5), tableau de bord CRM."},
    "S6": {"titre": "Maquettage du SI (1/2)",
           "apport": "Prototype interactif : écrans des acteurs et exécution des processus."},
    "S7": {"titre": "Maquettage du SI (2/2)",
           "apport": "Tableaux de bord, mode inspection, captures pour le rapport."},
    "S8": {"titre": "Développement, maintenance et évolution du SI",
           "apport": "MOA/MOE, DSI, éditeurs, gouvernance, SLA, TMA ; perspectives (IA, API, cloud, IoT, RPA, cybersécurité)."},
    "S9": {"titre": "Soutenance (1/2)", "apport": "Présentation orale de 10 minutes."},
    "S10": {"titre": "Soutenance (2/2)", "apport": "Questions du jury (5 minutes) et rendu Moodle."},
}

# ---------------------------------------------------------------------------
# Acteurs (Vue Acteur)
# ---------------------------------------------------------------------------
GROUPES_ACTEURS = [
    ("direction", "Direction & pilotage"),
    ("marketing", "Direction marketing et ses équipes (Fig. 3)"),
    ("fonctions", "Fonctions liées (Fig. 2)"),
    ("support", "Autres acteurs internes (§ 5.1)"),
    ("externes", "Acteurs externes (Fig. 1)"),
]

ACTEURS: Dict[str, dict] = {
    # --- Interne : direction
    "dg": dict(nom="Direction générale", court="Direction générale", type="interne", groupe="direction",
               persona="Comité exécutif (PDG et directeurs)", icone="couronne", couleur="#1d1d1f",
               role="Valide le plan de lancement présenté par le marketing et fixe à la finance les objectifs de marge.",
               figures=["Fig. 2"], ecran_defaut="pilotage"),
    # --- Interne : marketing (Fig. 3)
    "dir_marketing": dict(nom="Direction marketing iPhone", court="Dir. marketing", type="interne", groupe="marketing",
               persona="Claire Morel — Directrice marketing iPhone France", icone="megaphone", couleur="#0071e3",
               role="Fixe objectifs, budget et calendrier ; reçoit le tableau de bord hebdomadaire ; arbitre les décisions.",
               figures=["Fig. 2", "Fig. 3", "Fig. 4", "Fig. 5"], ecran_defaut="cockpit"),
    "mkt_creation": dict(nom="Équipe création (films, visuels)", court="Création", type="interne", groupe="marketing",
               persona="Hugo Benali — Directeur de création", icone="pinceau", couleur="#6250d6",
               role="Produit les films, visuels et vidéos TikTok, ainsi que le contenu de la page produit.",
               figures=["Fig. 3"], ecran_defaut="studio"),
    "mkt_social": dict(nom="Équipe réseaux sociaux et influence", court="Réseaux sociaux", type="interne", groupe="marketing",
               persona="Inès Caradec — Responsable réseaux sociaux & influence", icone="bulle", couleur="#e87ba4",
               role="Publie les contenus, sélectionne et gère les influenceurs, ajuste ciblage et message.",
               figures=["Fig. 3", "Fig. 5"], ecran_defaut="campagne"),
    "mkt_presse": dict(nom="Relations presse et événementiel", court="Relations presse", type="interne", groupe="marketing",
               persona="Mathieu Roux — Relations presse & événementiel", icone="journal", couleur="#424245",
               role="Organise la keynote et les tests presse ; suit les retombées médiatiques.",
               figures=["Fig. 3"], ecran_defaut="presse"),
    "mkt_ecommerce": dict(nom="Équipe e-commerce (apple.com, app Apple Store)", court="E-commerce", type="interne", groupe="marketing",
               persona="Sarah Lemaire — Responsable e-commerce apple.com/fr", icone="panier", couleur="#1baf7a",
               role="Gère la page iPhone Duo, l'affichage du prix et du délai, l'ouverture des précommandes.",
               figures=["Fig. 3", "Fig. 4"], ecran_defaut="precommandes"),
    "mkt_retail": dict(nom="Marketing retail et ventes (Apple Store)", court="Apple Store", type="interne", groupe="marketing",
               persona="Karim Haddad — Marketing retail Apple Store France", icone="boutique", couleur="#eb6834",
               role="Organise les démonstrations en Apple Store et remonte essais et rendez-vous.",
               figures=["Fig. 3"], ecran_defaut="apple-store"),
    "mkt_data": dict(nom="Équipe data et CRM", court="Data & CRM", type="interne", groupe="marketing",
               persona="Julie Fontaine — Responsable data & CRM", icone="base", couleur="#008300",
               role="Centre du système : regroupe trafic, mentions, retombées, essais, précommandes ; produit le tableau de bord.",
               figures=["Fig. 3", "Fig. 4"], ecran_defaut="crm"),
    # --- Interne : fonctions liées (Fig. 2)
    "finance": dict(nom="Finance", court="Finance", type="interne", groupe="fonctions",
               persona="Antoine Garnier — Contrôleur financier iPhone", icone="euro", couleur="#eda100",
               role="Valide prix et budgets, vérifie les paiements, enregistre le CA prévisionnel, calcule marges et coûts.",
               figures=["Fig. 2", "Fig. 3", "Fig. 4", "Fig. 5"], ecran_defaut="paiements"),
    "production": dict(nom="Production / Opérations (supply chain)", court="Production", type="interne", groupe="fonctions",
               persona="Nadia Perrin — Responsable supply chain Europe", icone="usine", couleur="#e34948",
               role="Vérifie le stock, réserve les appareils, ajuste le plan de production, fournit les appareils de test.",
               figures=["Fig. 2", "Fig. 3", "Fig. 4", "Fig. 5"], ecran_defaut="stocks"),
    # --- Interne : autres acteurs (§ 5.1)
    "ingenierie": dict(nom="Ingénierie / Produit", court="Ingénierie", type="interne", groupe="support",
               persona="Équipe ingénierie produit iPhone", icone="puce", couleur="#6e6e73",
               role="Fournit les caractéristiques (charnière titane, double écran, A20 Pro) qui deviennent des arguments de vente.",
               figures=["§ 3.4", "§ 5.1"], ecran_defaut="produit"),
    "juridique": dict(nom="Juridique et conformité", court="Juridique", type="interne", groupe="support",
               persona="Élise Vasseur — Juriste conformité & DPO adjointe", icone="balance", couleur="#6e6e73",
               role="Valide messages publicitaires et contrats d'influenceurs ; veille au RGPD et au DMA.",
               figures=["§ 3.4", "§ 5.1"], ecran_defaut="conformite"),
    "applecare": dict(nom="Service client (AppleCare)", court="AppleCare", type="interne", groupe="support",
               persona="Équipe AppleCare France", icone="bouee", couleur="#6e6e73",
               role="Répond aux clients, suit satisfaction, retours et souscriptions AppleCare.",
               figures=["§ 3.6", "§ 5.1"], ecran_defaut="service"),
    # --- Externes (Fig. 1)
    "client": dict(nom="Clients et prospects", court="Client", type="externe", groupe="externes",
               persona="Léa Martin, 29 ans, Lyon — possède un iPhone 13 Pro", icone="personne", couleur="#0071e3",
               role="Consulte la page produit, s'inscrit, configure et précommande l'iPhone Duo.",
               figures=["Fig. 1", "Fig. 4"], ecran_defaut="produit"),
    "influenceur": dict(nom="Médias, réseaux sociaux et influenceurs", court="Influenceurs & médias", type="externe", groupe="externes",
               persona="Créateurs de contenu sélectionnés pour le lancement", icone="etoile", couleur="#e87ba4",
               role="Reçoivent contenus, invitations et appareils de test ; publient leurs avis (visibilité, retours).",
               figures=["Fig. 1", "Fig. 5"], ecran_defaut="portail"),
    "operateur": dict(nom="Opérateurs télécom", court="Opérateurs", type="externe", groupe="externes",
               persona="Orange, SFR, Bouygues Telecom, Free", icone="antenne", couleur="#1baf7a",
               role="Activent l'eSIM, reçoivent des stocks et remontent ventes et forfaits.",
               figures=["Fig. 1"], ecran_defaut="portail"),
    "revendeur": dict(nom="Revendeurs agréés", court="Revendeurs", type="externe", groupe="externes",
               persona="Fnac, Darty, Boulanger…", icone="boutique", couleur="#eb6834",
               role="Reçoivent stocks et PLV, transmettent leurs ventes.",
               figures=["Fig. 1"], ecran_defaut="portail"),
    "fournisseur": dict(nom="Fournisseurs", court="Fournisseurs", type="externe", groupe="externes",
               persona="Samsung Display, TSMC, assembleurs", icone="camion", couleur="#e34948",
               role="Reçoivent les commandes ; communiquent capacités et livraisons (écran pliable : fournisseur unique).",
               figures=["Fig. 1"], ecran_defaut="portail"),
    "developpeur": dict(nom="Développeurs App Store", court="Développeurs", type="externe", groupe="externes",
               persona="Éditeurs d'applications de l'App Store", icone="code", couleur="#6250d6",
               role="Reçoivent les outils d'iOS 27 et adaptent leurs apps au double écran.",
               figures=["Fig. 1"], ecran_defaut="portail"),
    "agence": dict(nom="Agences de publicité et d'achat média", court="Agences", type="externe", groupe="externes",
               persona="Agence de création et agence d'achat média (fictives)", icone="etincelle", couleur="#eda100",
               role="Reçoivent briefs et budget, livrent campagnes et rapports de performance.",
               figures=["Fig. 1"], ecran_defaut="portail"),
    "institut": dict(nom="Instituts d'études", court="Instituts d'études", type="externe", groupe="externes",
               persona="IDC, Counterpoint, instituts de sondage", icone="graphique", couleur="#008300",
               role="Réalisent les études commandées : parts de marché, intention d'achat.",
               figures=["Fig. 1"], ecran_defaut="portail"),
    "organisme_financier": dict(nom="Organismes financiers", court="Organismes financiers", type="externe", groupe="externes",
               persona="Cetelem, Apple Pay, banques", icone="carte", couleur="#0071e3",
               role="Traitent paiements et demandes de crédit (paiement en plusieurs fois).",
               figures=["Fig. 1"], ecran_defaut="portail"),
    "partenaire_reprise": dict(nom="Partenaire reprise", court="Reprise", type="externe", groupe="externes",
               persona="Apple Trade In / Likewize", icone="recycle", couleur="#1baf7a",
               role="Fournit les estimations de valeur de reprise des anciens téléphones.",
               figures=["Fig. 1"], ecran_defaut="portail"),
    "regulateur": dict(nom="Régulateurs", court="Régulateurs", type="externe", groupe="externes",
               persona="Commission européenne, CNIL", icone="bouclier", couleur="#424245",
               role="Fixent les règles (RGPD, DMA) ; Apple leur transmet les informations obligatoires.",
               figures=["Fig. 1"], ecran_defaut="portail"),
    "concurrent": dict(nom="Concurrents", court="Concurrents", type="externe", groupe="externes",
               persona="Samsung, Google, Huawei", icone="jumelles", couleur="#86868b",
               role="Flux indirect (pointillés) : Apple ne communique pas avec eux mais surveille prix et produits.",
               figures=["Fig. 1"], ecran_defaut="veille", indirect=True),
    # --- Système (non sélectionnable comme humain : SI partagé de la Fig. 2)
    "si": dict(nom="SI partagé (CRM + ERP)", court="SI partagé", type="systeme", groupe=None,
               persona="CRM (clients) + ERP (stocks, coûts, ventes)", icone="base", couleur="#1d1d1f",
               role="Base commune : une précommande enregistrée est immédiatement visible par marketing, production et finance.",
               figures=["Fig. 2"], ecran_defaut=None),
}

ACTEURS_MARKETING = ["dir_marketing", "mkt_creation", "mkt_social", "mkt_presse", "mkt_ecommerce", "mkt_retail", "mkt_data"]

# ---------------------------------------------------------------------------
# Flux d'information (codifiés à partir des Fig. 1, 2 et 3)
#   A = aller (Apple -> acteur externe), R = retour (acteur externe -> Apple)
#   « de » / « vers » : acteurs du référentiel ; « mkt » = SI marketing d'Apple
# ---------------------------------------------------------------------------
FLUX: Dict[str, dict] = {}


def _flux(code, figure, de, vers, libelle, trait="plein", note=None):
    FLUX[code] = dict(code=code, figure=figure, de=de, vers=vers, libelle=libelle, trait=trait, note=note)


# Fig. 1 — diagramme de contexte (Apple / SI marketing au centre)
_flux("FE-01A", "Fig. 1", "mkt", "client", "Offres, publicités")
_flux("FE-01R", "Fig. 1", "client", "mkt", "Précommandes, avis, données")
_flux("FE-02A", "Fig. 1", "mkt", "operateur", "eSIM, stocks")
_flux("FE-02R", "Fig. 1", "operateur", "mkt", "Ventes, forfaits")
_flux("FE-03A", "Fig. 1", "mkt", "revendeur", "Stocks, PLV")
_flux("FE-03R", "Fig. 1", "revendeur", "mkt", "Ventes")
_flux("FE-04A", "Fig. 1", "mkt", "fournisseur", "Commandes")
_flux("FE-04R", "Fig. 1", "fournisseur", "mkt", "Livraisons, capacités")
_flux("FE-05A", "Fig. 1", "mkt", "developpeur", "Outils iOS 27")
_flux("FE-05R", "Fig. 1", "developpeur", "mkt", "Apps adaptées au pliable")
_flux("FE-06A", "Fig. 1", "mkt", "influenceur", "Contenus, invitations")
_flux("FE-06R", "Fig. 1", "influenceur", "mkt", "Visibilité, retours")
_flux("FE-07A", "Fig. 1", "mkt", "agence", "Briefs, budget")
_flux("FE-07R", "Fig. 1", "agence", "mkt", "Campagnes, rapports")
_flux("FE-08A", "Fig. 1", "mkt", "institut", "Commandes d'études")
_flux("FE-08R", "Fig. 1", "institut", "mkt", "Parts de marché")
_flux("FE-09A", "Fig. 1", "mkt", "organisme_financier", "Demandes de crédit")
_flux("FE-09R", "Fig. 1", "organisme_financier", "mkt", "Accords, paiements")
_flux("FE-10A", "Fig. 1", "mkt", "partenaire_reprise", "Estimations")
_flux("FE-10R", "Fig. 1", "partenaire_reprise", "mkt", "Valeurs de reprise")
_flux("FE-11A", "Fig. 1", "mkt", "regulateur", "Déclarations")
_flux("FE-11R", "Fig. 1", "regulateur", "mkt", "Règles RGPD, DMA")
_flux("FE-12R", "Fig. 1", "concurrent", "mkt", "Veille prix et produits", trait="pointille",
      note="Flux indirect : Apple ne communique pas avec ses concurrents, elle les observe.")

# Fig. 2 — flux internes (triangle marketing / production / finance + DG + SI partagé)
_flux("FI-01", "Fig. 2", "dg", "dir_marketing", "Validation du lancement")
_flux("FI-02", "Fig. 2", "dir_marketing", "dg", "Plan de lancement")
_flux("FI-03", "Fig. 2", "dg", "finance", "Objectifs de marge")
_flux("FI-04", "Fig. 2", "dir_marketing", "production", "Prévisions de demande par pays et couleur")
_flux("FI-05", "Fig. 2", "production", "dir_marketing", "Volumes disponibles, dates de livraison")
_flux("FI-06", "Fig. 2", "dir_marketing", "finance", "Proposition de prix, budget de campagne")
_flux("FI-07", "Fig. 2", "finance", "dir_marketing", "Prix validé, budget accordé")
_flux("FI-08", "Fig. 2", "production", "finance", "Coût de revient (écran, mémoire, titane)")
_flux("FI-09", "Fig. 2", "finance", "production", "Budget de production")
_flux("FI-10", "Fig. 2", "dir_marketing", "si", "Précommandes, données clients", note="Échange bidirectionnel avec le SI partagé (CRM).")
_flux("FI-11", "Fig. 2", "production", "si", "Stocks", note="Échange bidirectionnel avec le SI partagé (ERP).")
_flux("FI-12", "Fig. 2", "finance", "si", "CA, marges", note="Échange bidirectionnel avec le SI partagé (ERP).")
_flux("FI-13", "Prototype", "dir_marketing", "production", "Demande d'appareils de test",
      note="Flux révélé par le BPMN P2 (tâche « Fournit les appareils de test ») et absent de la Fig. 2 : "
           "complément identifié pendant le prototypage.")

# Fig. 3 — circulation de l'information au sein de la direction marketing
_flux("FM-01", "Fig. 3", "dir_marketing", "finance", "Demande de budget")
_flux("FM-02", "Fig. 3", "finance", "dir_marketing", "Budget accordé")
_flux("FM-03", "Fig. 3", "dir_marketing", "production", "Prévisions de demande")
_flux("FM-04", "Fig. 3", "production", "dir_marketing", "Volumes disponibles")
_flux("FM-05", "Fig. 3", "dir_marketing", "mkt_presse", "Calendrier keynote")
_flux("FM-06", "Fig. 3", "dir_marketing", "mkt_ecommerce", "Date des précommandes")
_flux("FM-07", "Fig. 3", "dir_marketing", "mkt_creation", "Brief créatif")
_flux("FM-08", "Fig. 3", "dir_marketing", "mkt_social", "Objectifs, budget")
_flux("FM-09", "Fig. 3", "dir_marketing", "mkt_retail", "Plan de démonstrations")
_flux("FM-10", "Fig. 3", "mkt_creation", "mkt_social", "Vidéos TikTok, visuels")
_flux("FM-11", "Fig. 3", "mkt_creation", "mkt_ecommerce", "Page produit")
_flux("FM-12", "Fig. 3", "mkt_presse", "mkt_data", "Retombées presse")
_flux("FM-13", "Fig. 3", "mkt_ecommerce", "mkt_data", "Trafic, paniers, précommandes")
_flux("FM-14", "Fig. 3", "mkt_social", "mkt_data", "Vues, mentions, engagement")
_flux("FM-15", "Fig. 3", "mkt_data", "mkt_social", "Ciblage des audiences")
_flux("FM-16", "Fig. 3", "mkt_retail", "mkt_data", "Essais en magasin, rendez-vous")
_flux("FM-17", "Fig. 3", "mkt_data", "dir_marketing", "Tableau de bord hebdomadaire")
_flux("FM-18", "Fig. 3", "mkt_data", "finance", "Coût par précommande", trait="pointille")
_flux("FM-19", "Fig. 3", "mkt_data", "production", "Précommandes par pays", trait="pointille")

# Acteur « Apple » réel qui porte un flux externe (pour l'affichage des notifications)
PORTEUR_APPLE = {
    "client": "mkt_ecommerce", "operateur": "production", "revendeur": "mkt_retail",
    "fournisseur": "production", "developpeur": "dir_marketing", "influenceur": "mkt_social",
    "agence": "dir_marketing", "institut": "mkt_data", "organisme_financier": "finance",
    "partenaire_reprise": "mkt_ecommerce", "regulateur": "juridique", "concurrent": "mkt_data",
}

# ---------------------------------------------------------------------------
# Processus BPMN (Fig. 4 et Fig. 5) — couloirs en colonnes, comme dans le dossier
# Coordonnées en unités SVG (viewBox 1440 x 2000)
# ---------------------------------------------------------------------------
PROCESSUS: Dict[str, dict] = {
    "P1": {
        "code": "P1",
        "nom": "Gestion des précommandes du 16 octobre",
        "figure": "Fig. 4",
        "seance": "S5",
        "resume": ("Ouverture des précommandes le 16/10 à 14 h : le client configure et valide, la finance vérifie "
                   "le paiement et enregistre le CA prévisionnel, le CRM enregistre la précommande, la production "
                   "réserve un appareil ; le marketing analyse le tableau de bord et déclenche soit une hausse de "
                   "production, soit une relance de la communication."),
        "viewbox": [1440, 2000],
        "couloirs": [
            {"id": "production", "libelle": "PRODUCTION (supply chain)", "x": 0, "w": 470, "acteurs": ["production"]},
            {"id": "marketing", "libelle": "MARKETING (e-commerce, data et CRM)", "x": 470, "w": 400,
             "acteurs": ["mkt_ecommerce", "mkt_data", "dir_marketing"]},
            {"id": "finance", "libelle": "FINANCE", "x": 870, "w": 280, "acteurs": ["finance"]},
            {"id": "client", "libelle": "CLIENT", "x": 1150, "w": 290, "acteurs": ["client"]},
        ],
        "noeuds": {
            "E0": dict(type="debut", couloir="client", libelle="16/10\n14 h", x=1295, y=150),
            "T01": dict(type="tache", couloir="client", libelle="Choisit sa configuration", x=1295, y=290,
                        acteurs=["client"], auto=False, ecran="E11", flux=["FE-01R", "FE-10A", "FE-10R"]),
            "T02": dict(type="tache", couloir="marketing", libelle="Affiche prix et délai sur le site", x=640, y=430,
                        acteurs=["mkt_ecommerce"], auto=True, ecran="E11", flux=["FE-01A", "FI-05"],
                        note="Tâche automatisée par le site apple.com (calcul du délai à partir du stock ERP)."),
            "T03": dict(type="tache", couloir="client", libelle="Valide la précommande", x=1295, y=570,
                        acteurs=["client"], auto=False, ecran="E11", flux=["FE-01R", "FE-09A"]),
            "G01": dict(type="passerelle", couloir="finance", libelle="Paiement\naccepté ?", x=1010, y=730,
                        acteurs=["finance"], auto=False, ecran="E30", issues=["oui", "non"], flux=["FE-09R"],
                        note="La décision s'appuie sur la réponse de l'organisme financier (flux FE-09R)."),
            "T04": dict(type="tache", couloir="finance", libelle="Enregistre le CA prévisionnel", x=1010, y=900,
                        acteurs=["finance"], auto=True, ecran="E30", flux=["FI-12"],
                        note="Écriture automatique dans l'ERP dès l'acceptation du paiement."),
            "T05": dict(type="tache", couloir="finance", libelle="Calcule la marge et le coût par précommande", x=1010, y=1060,
                        acteurs=["finance"], auto=True, ecran="E30", flux=["FI-12", "FI-08", "FM-18"]),
            "T06": dict(type="tache", couloir="marketing", libelle="Enregistre la précommande (CRM)", x=700, y=1060,
                        acteurs=["mkt_data"], auto=True, ecran="E24", flux=["FI-10", "FM-13", "FM-19"]),
            "T10": dict(type="tache", couloir="marketing", libelle="Analyse le tableau de bord", x=700, y=1240,
                        acteurs=["dir_marketing"], auto=False, ecran="E21", flux=["FM-17", "FI-12"], lot=True,
                        note="Tâche « par lot » : une analyse regroupe toutes les précommandes en attente."),
            "G03": dict(type="passerelle", couloir="marketing", libelle="Demande\nsupérieure\nà l'offre ?", x=610, y=1430,
                        acteurs=["dir_marketing"], auto=False, ecran="E21", issues=["oui", "non"], flux=["FI-05"]),
            "T12": dict(type="tache", couloir="marketing", libelle="Relance la communication", x=610, y=1620,
                        acteurs=["dir_marketing"], auto=False, ecran="E21", flux=["FE-01A", "FE-07A", "FM-08"]),
            "G02": dict(type="passerelle", couloir="production", libelle="Stock\ndisponible ?", x=300, y=1240,
                        acteurs=["production"], auto=False, ecran="E35", issues=["oui", "non"], flux=["FI-11", "FM-19"]),
            "T07": dict(type="tache", couloir="production", libelle="Allonge le délai affiché", x=300, y=1430,
                        acteurs=["production"], auto=False, ecran="E35", flux=["FI-05"]),
            "T08": dict(type="tache", couloir="production", libelle="Réserve un appareil au client", x=125, y=1620,
                        acteurs=["production"], auto=False, ecran="E35", flux=["FI-11"]),
            "T11": dict(type="tache", couloir="production", libelle="Augmente la production / répartit les stocks par pays",
                        x=355, y=1620, acteurs=["production"], auto=False, ecran="E36", flux=["FI-04", "FI-05", "FE-04A"]),
            "T09": dict(type="tache", couloir="client", libelle="Reçoit la confirmation", x=1295, y=1780,
                        acteurs=["client"], auto=True, ecran="E12", flux=["FE-01A"]),
            "E1": dict(type="fin", couloir="client", libelle="23/10", x=1295, y=1920),
        },
        # (source, cible, issue, ancre source, ancre cible)
        "transitions": [
            ("E0", "T01", None, "b", "t"),
            ("T01", "T02", None, "l", "t"),
            ("T02", "T03", None, "r", "l"),
            ("T03", "G01", None, "b", "t"),
            ("G01", "T01", "non", "r", "b"),
            ("G01", "T04", "oui", "b", "t"),
            ("T04", "T05", None, "b", "t"),
            ("T04", "T06", None, "l", "t"),
            ("T05", "T10", None, "b", "r"),
            ("T06", "T10", None, "b", "t"),
            ("T06", "G02", None, "l", "t"),
            ("T10", "G03", None, "b", "t"),
            ("G03", "T11", "oui", "l", "t"),
            ("G03", "T12", "non", "b", "t"),
            ("G02", "T07", "non", "b", "t"),
            ("G02", "T08", "oui", "l", "t"),
            ("T07", "T08", None, "b", "r"),
            ("T08", "T09", None, "b", "l"),
            ("T09", "E1", None, "b", "t"),
        ],
        # Jointures implicites (ET) : la tâche démarre quand toutes les branches sont arrivées
        "jointures": {"T10": ["T05", "T06"]},
        # Flux d'information portés par les transitions qui changent de couloir
        "flux_transitions": {
            ("T01", "T02"): "FE-01R", ("T02", "T03"): "FE-01A", ("T03", "G01"): "FE-09A",
            ("G01", "T01"): "FE-01A", ("T04", "T06"): "FI-10", ("T05", "T10"): "FM-18",
            ("T06", "G02"): "FM-19", ("G03", "T11"): "FI-04", ("T08", "T09"): "FE-01A",
            ("T07", "T08"): "FI-05", ("T06", "T10"): "FM-17",
        },
    },
    "P2": {
        "code": "P2",
        "nom": "Campagne TikTok et mesure de son efficacité",
        "figure": "Fig. 5",
        "seance": "S5",
        "resume": ("Après la keynote du 9/09 : le marketing propose objectifs et budget, la finance valide, le marketing "
                   "publie les vidéos TikTok et sélectionne des influenceurs, la production fournit les appareils de test, "
                   "les influenceurs publient leur avis ; le marketing mesure, ajuste si besoin, puis envoie rapport et "
                   "prévisions : la finance calcule le coût d'acquisition et la production ajuste son plan."),
        "viewbox": [1440, 2000],
        "couloirs": [
            {"id": "production", "libelle": "PRODUCTION", "x": 0, "w": 300, "acteurs": ["production"]},
            {"id": "influenceurs", "libelle": "INFLUENCEURS (externe)", "x": 300, "w": 300, "acteurs": ["influenceur"]},
            {"id": "marketing", "libelle": "MARKETING", "x": 600, "w": 540,
             "acteurs": ["dir_marketing", "mkt_social", "mkt_data"]},
            {"id": "finance", "libelle": "FINANCE", "x": 1140, "w": 300, "acteurs": ["finance"]},
        ],
        "noeuds": {
            "E0": dict(type="debut", couloir="marketing", libelle="Keynote\n9/09", x=1010, y=150),
            "T01": dict(type="tache", couloir="marketing", libelle="Propose objectifs et budget de campagne", x=1010, y=310,
                        acteurs=["dir_marketing"], auto=False, ecran="E22", flux=["FI-06", "FM-01", "FM-08"]),
            "G01": dict(type="passerelle", couloir="finance", libelle="Budget\nvalidé ?", x=1290, y=490,
                        acteurs=["finance"], auto=False, ecran="E31", issues=["oui", "non"], flux=["FI-07", "FM-02"],
                        libelles_issues={"non": "non : revoir"}),
            "T02": dict(type="tache", couloir="marketing", libelle="Conçoit et publie les vidéos TikTok", x=900, y=660,
                        acteurs=["mkt_social"], auto=False, ecran="E23", flux=["FM-07", "FM-10", "FE-06A", "FE-07A"]),
            "T03": dict(type="tache", couloir="marketing", libelle="Sélectionne les influenceurs", x=740, y=820,
                        acteurs=["mkt_social"], auto=False, ecran="E23", flux=["FE-06A", "FI-13"]),
            "T04": dict(type="tache", couloir="production", libelle="Fournit les appareils de test", x=150, y=980,
                        acteurs=["production"], auto=False, ecran="E37", flux=["FI-13", "FE-06A"]),
            "T05": dict(type="tache", couloir="influenceurs", libelle="Testent et publient leur avis", x=450, y=1150,
                        acteurs=["influenceur"], auto=False, ecran="E41", flux=["FE-06R"], multi=True,
                        note="Tâche multi-instance : chaque influenceur sélectionné publie son avis."),
            "T06": dict(type="tache", couloir="marketing", libelle="Mesure vues, mentions, sentiment", x=880, y=1310,
                        acteurs=["mkt_data", "mkt_social"], auto=False, ecran="E25", flux=["FM-14", "FM-17"]),
            "G02": dict(type="passerelle", couloir="marketing", libelle="Objectifs\natteints ?", x=840, y=1470,
                        acteurs=["dir_marketing"], auto=False, ecran="E25", issues=["oui", "non"], flux=["FM-17"]),
            "T07": dict(type="tache", couloir="marketing", libelle="Ajuste le ciblage et le message", x=1015, y=1630,
                        acteurs=["mkt_social"], auto=False, ecran="E23", flux=["FM-15", "FE-07A"]),
            "T08": dict(type="tache", couloir="marketing", libelle="Envoie le rapport et les prévisions", x=720, y=1630,
                        acteurs=["dir_marketing"], auto=False, ecran="E22", flux=["FI-04", "FM-03", "FM-18"]),
            "T09": dict(type="tache", couloir="production", libelle="Ajuste le plan de production", x=150, y=1790,
                        acteurs=["production"], auto=False, ecran="E36", flux=["FI-05", "FM-04", "FE-04A"]),
            "T10": dict(type="tache", couloir="finance", libelle="Calcule le coût d'acquisition par précommande", x=1290, y=1790,
                        acteurs=["finance"], auto=False, ecran="E31", flux=["FM-18", "FI-12"]),
            "E1": dict(type="fin", couloir="marketing", libelle="Fin", x=870, y=1925),
        },
        "transitions": [
            ("E0", "T01", None, "b", "t"),
            ("T01", "G01", None, "r", "t"),
            ("G01", "T01", "non", "t", "r"),
            ("G01", "T02", "oui", "b", "r"),
            ("T02", "T03", None, "b", "t"),
            ("T02", "T06", None, "b", "t"),
            ("T03", "T04", None, "l", "t"),
            ("T04", "T05", None, "b", "t"),
            ("T05", "T06", None, "r", "l"),
            ("T06", "G02", None, "b", "t"),
            ("G02", "T08", "oui", "b", "t"),
            ("G02", "T07", "non", "b", "t"),
            ("T07", "T06", None, "t", "r"),
            ("T08", "T09", None, "l", "t"),
            ("T08", "T10", None, "r", "l"),
            ("T09", "E1", None, "r", "l"),
            ("T10", "E1", None, "b", "r"),
        ],
        "jointures": {"T06": ["T02", "T05"], "E1": ["T09", "T10"]},
        "flux_transitions": {
            ("T01", "G01"): "FI-06", ("G01", "T01"): "FI-07", ("G01", "T02"): "FI-07",
            ("T03", "T04"): "FI-13", ("T04", "T05"): "FE-06A", ("T05", "T06"): "FE-06R",
            ("T08", "T09"): "FI-04", ("T08", "T10"): "FM-18", ("T07", "T06"): "FM-15",
        },
    },
}


def tache(code: str) -> Optional[dict]:
    """« P1-T03 » -> définition du nœud (avec code et processus)."""
    try:
        proc, noeud = code.split("-", 1)
        d = dict(PROCESSUS[proc]["noeuds"][noeud])
    except (ValueError, KeyError):
        return None
    d.update(code=code, processus=proc, noeud=noeud)
    return d


def toutes_les_taches() -> List[str]:
    out = []
    for p, proc in PROCESSUS.items():
        for n, d in proc["noeuds"].items():
            if d["type"] in ("tache", "passerelle"):
                out.append("%s-%s" % (p, n))
    return out


# ---------------------------------------------------------------------------
# Produit iPhone Duo (prix min/max issus du dossier ; paliers intermédiaires = hypothèse)
# ---------------------------------------------------------------------------
PRODUIT = {
    "nom": "iPhone Duo",
    "accroche": "Le premier iPhone pliable.",
    "puce": "A20 Pro",
    "os": "iOS 27",
    "capacites": [
        {"id": "256", "libelle": "256 Go", "prix": 2339.0},
        {"id": "512", "libelle": "512 Go", "prix": 2839.0},
        {"id": "1T", "libelle": "1 To", "prix": 3339.0},
        {"id": "2T", "libelle": "2 To", "prix": 3839.0},
    ],
    "coloris": [
        {"id": "naturel", "libelle": "Titane naturel", "hex": "#bdb5a6"},
        {"id": "noir", "libelle": "Titane noir", "hex": "#3a3a3c"},
        {"id": "blanc", "libelle": "Titane blanc", "hex": "#e9e8e3"},
        {"id": "bleu", "libelle": "Titane bleu", "hex": "#3e566f"},
    ],
    "applecare": {"libelle": "AppleCare+ pour iPhone Duo (2 ans)", "prix": 329.0},
    "tva": 0.20,
    "arguments": [
        ("Charnière et cadre en titane", "Répond à la principale crainte des acheteurs de pliables : la solidité."),
        ("Double écran", "Le plus grand écran jamais vu sur un iPhone, ouvert comme une mini-tablette."),
        ("Puce A20 Pro", "Performances et traitement de l'IA sur l'appareil (confidentialité)."),
        ("iOS 27 et apps adaptées", "Applications de l'App Store adaptées au double écran."),
        ("Environnement", "35 % de matériaux recyclés, titane recyclé à 85 %, emballage 100 % fibres."),
        ("eSIM uniquement", "Activation directe avec Orange, SFR, Bouygues Telecom et Free."),
    ],
}

# Coût de revient unitaire (fictif) — reflète la flambée du prix de la mémoire (SWOT, menaces)
COUTS_REVIENT = [
    # composant, fournisseur, coût prévu (budget), coût réel (€)
    ("Écran pliable OLED (intérieur + extérieur)", "Samsung Display", 398.0, 412.0),
    ("Puce A20 Pro", "TSMC", 148.0, 148.0),
    ("Mémoire vive DRAM 12 Go", "Micron / SK hynix", 31.0, 58.0),
    ("Stockage NAND 256 Go", "Kioxia / Samsung", 27.0, 46.0),
    ("Charnière et cadre en titane", "Assembleurs", 92.0, 96.0),
    ("Modules photo (3 capteurs)", "Sony", 84.0, 84.0),
    ("Batterie, modem 5G, capteurs", "Divers", 102.0, 102.0),
    ("Assemblage et tests", "Foxconn", 46.0, 46.0),
    ("Logistique et droits de douane", "—", 30.0, 38.0),
]
SURCOUT_NAND = {"256": 0.0, "512": 46.0, "1T": 132.0, "2T": 294.0}  # supplément vs 256 Go

PAYS = [
    {"id": "FR", "libelle": "France"}, {"id": "DE", "libelle": "Allemagne"},
    {"id": "UK", "libelle": "Royaume-Uni"}, {"id": "IT", "libelle": "Italie"},
    {"id": "ES", "libelle": "Espagne"}, {"id": "US", "libelle": "États-Unis"},
    {"id": "JP", "libelle": "Japon"}, {"id": "IN", "libelle": "Inde"},
    {"id": "CN", "libelle": "Grande Chine"},
]
PAYS_LIBELLE = {p["id"]: p["libelle"] for p in PAYS}

APPLE_STORES_FR = [
    "Apple Champs-Élysées", "Apple Opéra", "Apple Marché Saint-Germain", "Apple Les Quatre Temps",
    "Apple Vélizy 2", "Apple Parly 2", "Apple Rosny 2", "Apple Val d'Europe", "Apple Part-Dieu",
    "Apple Confluence", "Apple Sainte-Catherine", "Apple Odysseum", "Apple Lille", "Apple Cap 3000",
]

OBJECTIFS_HEBDO = [
    # code, libellé (France), objectif, unité, sens (+ = plus haut est mieux)
    ("visites", "Visites de la page iPhone Duo (cumul)", 2000000, "nb", 1),
    ("me_prevenir", "Inscriptions « Me prévenir »", 120000, "nb", 1),
    ("rdv_demo", "Rendez-vous de démonstration en Apple Store", 15000, "nb", 1),
    ("vues_tiktok", "Vues des vidéos TikTok Apple", 20000000, "nb", 1),
    ("sentiment", "Part de commentaires positifs", 60.0, "%", 1),
    ("intention", "Intention d'achat déclarée (sondage)", 8.0, "%", 1),
    ("android", "Part des visiteurs utilisant Android", 15.0, "%", 1),
]

# ---------------------------------------------------------------------------
# Registre des écrans (maquettes Séances 6-7) -> alimente le mode Inspection
# ---------------------------------------------------------------------------
ECRANS: List[dict] = []


def _ecran(code, acteur, slug, titre, sous_titre, seances, taches, flux, donnees, jury, transversal=False):
    ECRANS.append(dict(code=code, acteur=acteur, slug=slug, titre=titre, sous_titre=sous_titre,
                       seances=seances, taches=taches, flux=flux, donnees=donnees, jury=jury,
                       transversal=transversal))


# Transversaux
_ecran("E00", None, "accueil", "Accueil — le SI du lancement de l'iPhone Duo",
       "Vue d'ensemble : problématique, acteurs, processus et indicateurs", ["S1", "S2", "S4", "S5"],
       [], [], ["Synthèse de toutes les bases"],
       ["Rappeler la problématique : piloter le lancement AVANT la commercialisation.",
        "Montrer que chaque acteur des Fig. 1 à 3 dispose de son interface dédiée."], transversal=True)
_ecran("E01", None, "flux", "Cartographie vivante des flux d'information",
       "Fig. 1, 2 et 3 du dossier rendues interactives, avec compteurs temps réel", ["S4"],
       [], ["FE-01A", "FE-01R", "FI-01", "FI-02", "FM-17"], ["Journal des flux (bus d'information)"],
       ["Chaque flèche du diagramme de contexte est cliquable et compte les messages réellement échangés.",
        "Le flux FI-13 a été découvert grâce au BPMN P2 : la maquette complète les modèles."], transversal=True)
_ecran("E02", None, "processus/P1", "Processus P1 — précommandes (BPMN exécutable)",
       "Fig. 4 : jetons en temps réel sur chaque tâche, démo guidée pas à pas", ["S5"],
       ["P1-" + n for n in ["T01", "T02", "T03", "G01", "T04", "T05", "T06", "G02", "T07", "T08", "T09", "T10", "G03", "T11", "T12"]],
       ["FE-01R", "FE-09A", "FE-09R", "FI-10", "FI-11", "FI-12", "FM-17", "FM-19"], ["Instances de processus, événements"],
       ["Le BPMN n'est plus un dessin : chaque précommande est une instance qui avance de couloir en couloir.",
        "Les passerelles (paiement, stock, demande/offre) sont de vraies règles de gestion."], transversal=True)
_ecran("E03", None, "processus/P2", "Processus P2 — campagne TikTok (BPMN exécutable)",
       "Fig. 5 : budget, publication, influenceurs, mesure, ajustement, rapport", ["S5"],
       ["P2-" + n for n in ["T01", "G01", "T02", "T03", "T04", "T05", "T06", "G02", "T07", "T08", "T09", "T10"]],
       ["FI-06", "FI-07", "FE-06A", "FE-06R", "FM-14", "FM-15", "FI-04", "FM-18"], ["Campagnes, mesures, ajustements"],
       ["La boucle « Objectifs atteints ? non -> ajuste -> mesure » est exécutable.",
        "Même une campagne de communication mobilise la finance et la production."], transversal=True)
_ecran("E04", None, "journal", "Journal des flux d'information",
       "Bus d'information : qui envoie quoi à qui, quand, dans quel processus", ["S4", "S5"],
       [], ["FE-01R", "FI-10", "FM-13"], ["Table flux_log, notifications"],
       ["Traçabilité complète : chaque action d'un acteur génère un flux codifié et une notification."], transversal=True)
_ecran("E05", None, "si-partage", "SI partagé — base CRM + ERP",
       "Les tables du SI commun de la Fig. 2, en lecture seule", ["S2", "S4"],
       [], ["FI-10", "FI-11", "FI-12"], ["Toutes les tables SQLite"],
       ["Le SI partagé est la clé : une précommande enregistrée est visible à la fois par le marketing, la production et la finance."],
       transversal=True)
_ecran("E06", None, "dossier", "Dossier TD — Séance 8 et soutenance",
       "Acteurs du développement/maintenance, évolutions, dossier complet, plan d'oral, questions du jury", ["S8", "S9", "S10"],
       [], [], ["Livrables Markdown (livrables_td/)"], ["Tout le rendu Moodle est consultable dans l'application."],
       transversal=True)
_ecran("E07", None, "captures", "Atelier de captures HD",
       "Génère des PNG haute définition de chaque maquette pour le rapport et le PowerPoint", ["S6", "S7"],
       [], [], [], ["Captures 2x (Retina), avec ou sans annotations d'inspection."], transversal=True)

# Client
_ecran("E10", "client", "produit", "iPhone Duo — page produit (apple.com/fr)",
       "Stratégie digitale : informer, rassurer, convertir — collecte des signaux avancés", ["S3", "S2"],
       [], ["FE-01A", "FE-01R", "FE-10A", "FE-10R", "FM-11", "FM-13"], ["CRM : inscriptions « Me prévenir », consentements", "Analytics : visites"],
       ["Chaque visite et chaque inscription « Me prévenir » alimente le tableau de bord avant la sortie.",
        "Conformité visible : confidentialité, cookies, mentions légales du crédit, environnement."])
_ecran("E11", "client", "configurateur", "Configurer et précommander l'iPhone Duo",
       "Couloir Client du BPMN P1 : choix, affichage prix/délai, validation, paiement", ["S5", "S3"],
       ["P1-T01", "P1-T02", "P1-T03"], ["FE-01R", "FE-01A", "FE-09A", "FE-10A", "FE-10R", "FI-05"],
       ["ERP : stocks et lots de production (délai)", "CRM : client, précommande", "Reprise : grille de valeurs"],
       ["Le délai affiché est calculé en direct à partir du stock ERP : c'est la tâche T02 automatisée.",
        "Le paiement en plusieurs fois déclenche le flux FE-09A vers l'organisme financier."])
_ecran("E12", "client", "commandes", "Mon compte — suivi de précommande",
       "Réception de la confirmation (T09) et événement de fin 23/10 ; droits RGPD", ["S5"],
       ["P1-T09", "P1-T01"], ["FE-01A", "FE-01R"], ["CRM : précommandes, consentements"],
       ["Le client voit l'avancement de SA précommande dans le processus (transparence).",
        "Exercice des droits RGPD : consentement marketing modifiable."])
# Direction générale
_ecran("E15", "dg", "pilotage", "Direction générale — plan de lancement et objectifs de marge",
       "Validation du lancement (FI-01) et objectifs de marge (FI-03)", ["S4", "S2"],
       [], ["FI-01", "FI-02", "FI-03"], ["Plans de lancement, objectifs de marge, synthèse KPI"],
       ["La direction générale pilote par exception : elle valide le plan et fixe la marge cible."])
# Direction marketing
_ecran("E20", "dir_marketing", "cockpit", "Cockpit marketing — tableau de bord du lancement",
       "Indicateurs avancés (avant la sortie), précommandes, puis résultats (§ 3.6 et § 6.3)", ["S2", "S5"],
       ["P1-T10"], ["FM-17", "FM-13", "FM-14", "FM-16", "FE-08R"], ["Entrepôt KPI (kpi_journalier, kpi_hebdo)"],
       ["Répond à la problématique : mesurer l'efficacité de la communication sans chiffre de ventes.",
        "Le tableau de bord du lundi 12/10 reproduit exactement celui du dossier (§ 6.3)."])
_ecran("E21", "dir_marketing", "pilotage-precommandes", "Analyse du tableau de bord des précommandes",
       "BPMN P1 : T10 Analyse, G03 Demande > offre ?, T12 Relance la communication", ["S5"],
       ["P1-T10", "P1-G03", "P1-T12"], ["FM-17", "FI-04", "FI-05", "FM-04", "FE-07A", "FE-01A"],
       ["Analyses, précommandes par pays, lots de production"],
       ["La décision est assistée par le SI (ratio demande/offre) mais reste humaine.",
        "Si la demande dépasse l'offre, la production est notifiée (T11) ; sinon, relance de la communication (T12)."])
_ecran("E22", "dir_marketing", "campagne", "Pilotage de la campagne et des équipes",
       "BPMN P2 : T01 objectifs et budget, T08 rapport et prévisions ; consignes Fig. 3", ["S5", "S4"],
       ["P2-T01", "P2-T08"], ["FI-06", "FM-01", "FM-05", "FM-06", "FM-07", "FM-08", "FM-09", "FI-02", "FI-04", "FM-03"],
       ["Campagnes, budgets, plans de lancement"],
       ["La direction marketing est l'émetteur de la majorité des flux de la Fig. 3."])
# Équipes marketing
_ecran("E23", "mkt_social", "campagne", "Campagne TikTok et influence",
       "BPMN P2 : T02 publier, T03 sélectionner les influenceurs, T07 ajuster ciblage et message", ["S3", "S5"],
       ["P2-T02", "P2-T03", "P2-T07"], ["FM-10", "FE-06A", "FI-13", "FM-15", "FE-07A"],
       ["Publications, influenceurs, ajustements"],
       ["Ton humoristique et usages du quotidien (yoga, café, mini-cinéma) : analyse de la Séance 3.",
        "La sélection des influenceurs déclenche une demande d'appareils de test à la production (FI-13)."])
_ecran("E24", "mkt_data", "crm", "CRM — clients et précommandes",
       "BPMN P1 : T06 enregistrement CRM ; diffusion vers finance (FM-18) et production (FM-19)", ["S2", "S5"],
       ["P1-T06"], ["FI-10", "FM-13", "FM-15", "FM-18", "FM-19"], ["CRM : clients (Apple ID), précommandes, segments"],
       ["Le compte Apple joue le rôle d'identifiant unique du client (focus CRM du dossier).",
        "Affichage pseudonymisé des identifiants : minimisation des données (RGPD)."])
_ecran("E25", "mkt_data", "mesure", "Mesure de la campagne et tableau de bord hebdomadaire",
       "BPMN P2 : T06 mesure, G02 objectifs atteints ? ; FM-17 tableau de bord", ["S5"],
       ["P2-T06", "P2-G02"], ["FM-14", "FM-12", "FM-16", "FM-17"], ["Mesures, KPI"],
       ["C'est ce circuit qui permet de savoir si la communication fonctionne avant la sortie."])
_ecran("E26", "mkt_ecommerce", "precommandes", "E-commerce — ouverture et suivi des précommandes",
       "BPMN P1 : T02 prix et délai affichés ; FM-06 date, FM-11 page produit, FM-13 trafic", ["S3", "S5"],
       ["P1-T02"], ["FM-06", "FM-11", "FM-13", "FE-01A", "FI-05"], ["ERP : stocks, délais ; Analytics"],
       ["Le délai affiché est la traduction commerciale d'une contrainte de production."])
_ecran("E27", "mkt_creation", "studio", "Studio création", "Brief créatif reçu, livraison des vidéos et de la page produit",
       ["S3", "S4"], [], ["FM-07", "FM-10", "FM-11"], ["Contenus créatifs"],
       ["Illustration des flux internes à la direction marketing (Fig. 3)."])
_ecran("E28", "mkt_presse", "presse", "Relations presse et événementiel", "Calendrier keynote, invitations, retombées presse",
       ["S4"], [], ["FM-05", "FE-06A", "FM-12"], ["Retombées presse"],
       ["Les retombées presse remontent à l'équipe data (FM-12) pour le tableau de bord."])
_ecran("E29", "mkt_retail", "apple-store", "Apple Store — démonstrations et essais",
       "Plan de démonstrations (FM-09), rendez-vous et essais remontés à la data (FM-16)", ["S4", "S2"],
       [], ["FM-09", "FM-16"], ["Rendez-vous de démonstration"],
       ["Les essais en magasin sont un indicateur avancé : 17 200 rendez-vous au 12/10."])
# Finance
_ecran("E30", "finance", "paiements", "Finance — contrôle des paiements et CA prévisionnel",
       "BPMN P1 : G01 Paiement accepté ?, T04 CA prévisionnel, T05 marge et coût par précommande", ["S5", "S2"],
       ["P1-G01", "P1-T04", "P1-T05"], ["FE-09R", "FI-12", "FI-08", "FM-18"], ["ERP : écritures de CA, marges ; demandes de crédit"],
       ["La finance voit en temps réel le CA prévisionnel généré par les précommandes.",
        "La marge par configuration révèle l'effet de la flambée du prix de la mémoire (SWOT)."])
_ecran("E31", "finance", "budgets", "Finance — budgets, prix et coût d'acquisition",
       "BPMN P2 : G01 Budget validé ?, T10 coût d'acquisition ; FI-03, FI-07, FI-08, FI-09", ["S5", "S4"],
       ["P2-G01", "P2-T10"], ["FI-06", "FI-07", "FM-02", "FI-03", "FI-08", "FI-09", "FM-18"],
       ["Budgets, prix, coûts de revient, objectifs de marge"],
       ["Le prix de 2 339 € est un arbitrage entre positionnement marketing et marge (§ 3.4)."])
# Production
_ecran("E35", "production", "stocks", "Production — stocks et réservations",
       "BPMN P1 : G02 Stock disponible ?, T07 allonge le délai, T08 réserve un appareil", ["S5", "S4"],
       ["P1-G02", "P1-T07", "P1-T08"], ["FI-11", "FI-05", "FM-19"], ["ERP : lots de production, réservations"],
       ["Le marketing ne peut pas promettre plus que ce que la production peut livrer (§ 5.3)."])
_ecran("E36", "production", "plan", "Production — plan de production et capacités",
       "BPMN : P1-T11 augmente / répartit, P2-T09 ajuste le plan ; capacité Samsung Display (FE-04)", ["S5", "S4", "S1"],
       ["P1-T11", "P2-T09"], ["FI-04", "FI-05", "FI-08", "FI-09", "FE-04A", "FE-04R", "FM-19"],
       ["ERP : lots, capacités fournisseurs, coûts de revient"],
       ["La dépendance à Samsung Display (SWOT, faiblesses) devient une contrainte visible dans le SI."])
_ecran("E37", "production", "appareils-test", "Production — appareils de test",
       "BPMN P2 : T04 fournit les appareils de test aux influenceurs", ["S5"],
       ["P2-T04"], ["FI-13", "FE-06A"], ["Parc d'appareils de pré-série"],
       ["Le produit n'étant pas en vente, la production fournit des appareils de pré-série."])
# Autres internes
_ecran("E38", "ingenierie", "produit", "Ingénierie — fiche produit et arguments", "Caractéristiques -> arguments de vente ; attentes clients",
       ["S2"], [], ["FM-11"], ["Fiche produit"], ["Interaction ingénierie / marketing (§ 3.4)."])
_ecran("E39", "juridique", "conformite", "Juridique — conformité RGPD, DMA et publicité",
       "Validation des messages et contrats, registre des traitements, échanges avec la CNIL", ["S1", "S2", "S3"],
       [], ["FE-11A", "FE-11R"], ["Registre RGPD, validations"], ["Pression réglementaire européenne (SWOT, menaces)."])
_ecran("E40", "applecare", "service", "AppleCare — service client", "Questions, satisfaction, retours, souscriptions AppleCare",
       ["S2"], [], ["FE-01R"], ["Demandes SAV"], ["Indicateurs après la sortie : satisfaction, retours, AppleCare."])
# Externes
_ecran("E41", "influenceur", "portail", "Portail influenceurs et médias",
       "BPMN P2 : T05 testent et publient leur avis (multi-instance)", ["S3", "S5"],
       ["P2-T05"], ["FE-06A", "FE-06R"], ["Influenceurs, publications"],
       ["Acteur externe intégré au processus : son avis alimente la mesure (T06)."])
_ecran("E42", "operateur", "portail", "Portail opérateurs télécom", "eSIM, stocks / ventes, forfaits", ["S4"],
       [], ["FE-02A", "FE-02R"], ["Activations eSIM, ventes opérateurs"], ["L'iPhone Duo est 100 % eSIM : flux indispensable."])
_ecran("E43", "revendeur", "portail", "Portail revendeurs agréés", "Stocks, PLV / ventes", ["S4"],
       [], ["FE-03A", "FE-03R"], ["Ventes revendeurs"], ["Canal de distribution indirect (§ 1.6)."])
_ecran("E44", "fournisseur", "portail", "Portail fournisseurs", "Commandes / livraisons, capacités", ["S4", "S1"],
       [], ["FE-04A", "FE-04R"], ["Capacités fournisseurs, commandes"], ["Ce flux conditionne les quantités que le marketing peut promettre."])
_ecran("E45", "developpeur", "portail", "Portail développeurs", "Outils iOS 27 / apps adaptées au pliable", ["S4"],
       [], ["FE-05A", "FE-05R"], ["Apps adaptées"], ["Les apps adaptées renforcent l'argumentaire de vente."])
_ecran("E46", "agence", "portail", "Portail agences", "Briefs, budget / campagnes, rapports", ["S4"],
       [], ["FE-07A", "FE-07R"], ["Briefs, rapports"], ["Externalisation de la création et de l'achat média."])
_ecran("E47", "institut", "portail", "Portail instituts d'études", "Commandes d'études / parts de marché", ["S4", "S1"],
       [], ["FE-08A", "FE-08R"], ["Études"], ["Mesure de l'intention d'achat : indicateur avancé clé."])
_ecran("E48", "organisme_financier", "portail", "Portail organisme financier", "Demandes de crédit / accords, paiements", ["S4", "S5"],
       ["P1-G01"], ["FE-09A", "FE-09R"], ["Demandes de crédit"], ["Le paiement en plusieurs fois lève le frein du prix."])
_ecran("E49", "partenaire_reprise", "portail", "Portail partenaire reprise", "Estimations / valeurs de reprise", ["S4", "S3"],
       [], ["FE-10A", "FE-10R"], ["Grille de reprise, estimations"], ["La reprise est un levier contre le frein du prix (§ 6.3)."])
_ecran("E50", "regulateur", "portail", "Portail régulateurs", "Déclarations / règles RGPD, DMA", ["S4", "S1"],
       [], ["FE-11A", "FE-11R"], ["Registre, règles"], ["Conformité légale et éthique (Séance 3)."])
_ecran("E51", "concurrent", "veille", "Veille concurrentielle (flux indirect)", "Prix et produits concurrents observés",
       ["S1", "S4"], [], ["FE-12R"], ["Relevés de veille"],
       ["Pas d'interface « concurrent » : la flèche en pointillés signifie qu'Apple observe sans échanger."])

ECRANS_PAR_CODE = {e["code"]: e for e in ECRANS}


def ecrans_acteur(acteur: str) -> List[dict]:
    return [e for e in ECRANS if e["acteur"] == acteur]


def ecran_url(e: dict) -> str:
    if e["transversal"]:
        return "/" if e["slug"] == "accueil" else "/" + e["slug"]
    return "/a/%s/%s" % (e["acteur"], e["slug"])


def libelle_acteur(code: str) -> str:
    if code == "mkt":
        return "Apple — SI marketing"
    a = ACTEURS.get(code)
    return a["nom"] if a else code


def export_referentiel() -> dict:
    """Version JSON du référentiel pour le front (inspection, BPMN, cartographie)."""
    procs = {}
    for code, p in PROCESSUS.items():
        q = {k: v for k, v in p.items() if k != "flux_transitions"}
        q["flux_transitions"] = ["%s>%s:%s" % (a, b, f) for (a, b), f in p["flux_transitions"].items()]
        procs[code] = q
    return {
        "projet": PROJET, "seances": SEANCES, "acteurs": ACTEURS, "groupes": GROUPES_ACTEURS,
        "flux": FLUX, "processus": procs,
        "ecrans": [dict(e, url=ecran_url(e)) for e in ECRANS],
        "produit": PRODUIT, "pays": PAYS,
    }
