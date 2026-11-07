"""Base SQLite du SI partagé (CRM + ERP + pilotage + échanges partenaires).

Une connexion par requête ; mode WAL pour lire pendant les écritures.
Le fichier est créé et pré-rempli automatiquement au premier lancement.
"""
import os
import sqlite3
import threading
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
VERSION_SCHEMA = "2026.11.3"

_verrou_init = threading.Lock()


def chemin_base() -> Path:
    return Path(os.environ.get("SI_DB_PATH", str(RACINE / "data" / "si_iphone_duo.db")))


def connecter(chemin=None) -> sqlite3.Connection:
    conn = sqlite3.connect(str(chemin or chemin_base()), timeout=15, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = NORMAL")
    return conn


# Regroupement des tables par « brique » du SI (affiché dans l'écran SI partagé)
BRIQUES = {
    "CRM (clients, relation)": ["clients", "rdv_demo", "demandes_sav"],
    "ERP (ventes, stocks, coûts)": ["precommandes", "precommandes_pays", "lots_production", "capacites_fournisseurs",
                                    "commandes_fournisseurs", "couts_revient", "prix", "budgets_production"],
    "Pilotage et décisions": ["plans_lancement", "objectifs_marge", "analyses", "kpi_journalier", "kpi_hebdo"],
    "Moteur de processus (BPMN)": ["instances", "evenements"],
    "Bus d'information": ["flux_log", "notifications"],
    "Marketing (campagnes)": ["campagnes", "budget_lignes", "publications", "influenceurs", "campagne_influenceurs",
                              "appareils_test", "mesures", "ajustements", "rapports_campagne", "contenus_creation",
                              "retombees_presse"],
    "Partenaires externes": ["demandes_credit", "reprise_grille", "estimations_reprise", "operateurs_activations",
                             "revendeurs_flux", "apps_adaptees", "etudes", "reglementation", "veille",
                             "briefs_agence", "validations_juridiques"],
    "Paramètres": ["parametres"],
}

SCHEMA = """
CREATE TABLE parametres (cle TEXT PRIMARY KEY, valeur TEXT NOT NULL);

-- ===================== CRM =====================
CREATE TABLE clients (
  id INTEGER PRIMARY KEY,
  apple_id TEXT NOT NULL UNIQUE,
  prenom TEXT NOT NULL, nom TEXT NOT NULL, age INTEGER, ville TEXT, code_postal TEXT,
  segment TEXT NOT NULL,
  appareil TEXT, appareil_annee INTEGER, plateforme TEXT,
  me_prevenir_le TEXT,
  consentement_marketing INTEGER NOT NULL DEFAULT 0,
  abonnements TEXT,
  source TEXT,
  cree_le TEXT NOT NULL,
  demo INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX ix_clients_me ON clients(me_prevenir_le);

CREATE TABLE rdv_demo (
  id INTEGER PRIMARY KEY, magasin TEXT NOT NULL, creneau TEXT NOT NULL, client_id INTEGER,
  statut TEXT NOT NULL, note_essai INTEGER, intention TEXT, cree_le TEXT NOT NULL, demo INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX ix_rdv_creneau ON rdv_demo(creneau);

CREATE TABLE demandes_sav (
  id INTEGER PRIMARY KEY, sujet TEXT NOT NULL, canal TEXT NOT NULL, statut TEXT NOT NULL,
  satisfaction INTEGER, escalade TEXT, cree_le TEXT NOT NULL, demo INTEGER NOT NULL DEFAULT 0
);

-- ===================== ERP =====================
CREATE TABLE precommandes (
  id INTEGER PRIMARY KEY,
  reference TEXT NOT NULL UNIQUE,
  client_id INTEGER REFERENCES clients(id),
  instance_id INTEGER,
  pays TEXT NOT NULL DEFAULT 'FR',
  canal TEXT NOT NULL,
  capacite TEXT NOT NULL, coloris TEXT NOT NULL,
  prix_ttc REAL NOT NULL, prix_ht REAL NOT NULL,
  applecare INTEGER NOT NULL DEFAULT 0, applecare_ttc REAL NOT NULL DEFAULT 0,
  reprise_modele TEXT, reprise_etat TEXT, reprise_valeur REAL NOT NULL DEFAULT 0,
  paiement_mode TEXT NOT NULL,
  paiement_statut TEXT NOT NULL,
  livraison_mode TEXT NOT NULL,
  magasin TEXT,
  delai_affiche TEXT,
  livraison_prevue TEXT,
  lot_id INTEGER,
  delai_allonge INTEGER NOT NULL DEFAULT 0,
  statut TEXT NOT NULL,
  ca_previsionnel_ht REAL, cout_revient REAL, marge REAL, cout_par_precommande REAL,
  analyse_id INTEGER,
  motif TEXT,
  paye_le TEXT, crm_le TEXT, reserve_le TEXT, confirme_le TEXT,
  cree_le TEXT NOT NULL, maj_le TEXT NOT NULL,
  demo INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX ix_pc_cree ON precommandes(cree_le);
CREATE INDEX ix_pc_statut ON precommandes(statut);
CREATE INDEX ix_pc_config ON precommandes(capacite, coloris, reserve_le);
CREATE INDEX ix_pc_client ON precommandes(client_id);
CREATE INDEX ix_pc_analyse ON precommandes(analyse_id);
CREATE INDEX ix_pc_lot ON precommandes(lot_id, reserve_le);
CREATE INDEX ix_pc_instance ON precommandes(instance_id);

CREATE TABLE precommandes_pays (
  pays TEXT NOT NULL, heure TEXT NOT NULL, nb INTEGER NOT NULL, PRIMARY KEY (pays, heure)
);

CREATE TABLE lots_production (
  id INTEGER PRIMARY KEY, pays TEXT NOT NULL, capacite TEXT, coloris TEXT,
  quantite INTEGER NOT NULL, disponible_le TEXT NOT NULL, origine TEXT NOT NULL,
  cree_le TEXT NOT NULL, demo INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX ix_lots ON lots_production(pays, capacite, coloris, disponible_le);

CREATE TABLE capacites_fournisseurs (
  id INTEGER PRIMARY KEY, fournisseur TEXT NOT NULL, composant TEXT NOT NULL, semaine TEXT NOT NULL,
  capacite INTEGER NOT NULL, engagee INTEGER NOT NULL DEFAULT 0, declare_le TEXT NOT NULL, demo INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE commandes_fournisseurs (
  id INTEGER PRIMARY KEY, fournisseur TEXT NOT NULL, composant TEXT NOT NULL, quantite INTEGER NOT NULL,
  semaine TEXT NOT NULL, statut TEXT NOT NULL, cree_le TEXT NOT NULL, livre_le TEXT, demo INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE couts_revient (
  id INTEGER PRIMARY KEY, composant TEXT NOT NULL, fournisseur TEXT, cout_prevu REAL NOT NULL, cout_reel REAL NOT NULL,
  maj_le TEXT NOT NULL
);
CREATE TABLE prix (capacite TEXT PRIMARY KEY, prix_ttc REAL NOT NULL, valide_le TEXT NOT NULL, valide_par TEXT);
CREATE TABLE budgets_production (
  id INTEGER PRIMARY KEY, montant REAL NOT NULL, motif TEXT NOT NULL, accorde_le TEXT NOT NULL, demo INTEGER NOT NULL DEFAULT 0
);

-- ===================== Pilotage =====================
CREATE TABLE plans_lancement (
  id INTEGER PRIMARY KEY, titre TEXT NOT NULL, pays TEXT, contenu TEXT NOT NULL, soumis_le TEXT NOT NULL,
  statut TEXT NOT NULL, decide_le TEXT, commentaire TEXT, demo INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE objectifs_marge (
  id INTEGER PRIMARY KEY, taux REAL NOT NULL, defini_le TEXT NOT NULL, commentaire TEXT, demo INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE analyses (
  id INTEGER PRIMARY KEY, instance_id INTEGER, pays TEXT NOT NULL, horodatage TEXT NOT NULL,
  precommandes INTEGER, projection INTEGER, offre INTEGER, ratio REAL, nb_precommandes_analysees INTEGER,
  decision TEXT, action TEXT, details TEXT, demo INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE kpi_journalier (
  jour TEXT NOT NULL, pays TEXT NOT NULL, indicateur TEXT NOT NULL, valeur REAL NOT NULL,
  PRIMARY KEY (jour, pays, indicateur)
);
CREATE TABLE kpi_hebdo (
  semaine TEXT NOT NULL, pays TEXT NOT NULL, indicateur TEXT NOT NULL, valeur REAL NOT NULL,
  PRIMARY KEY (semaine, pays, indicateur)
);

-- ===================== Moteur BPMN =====================
CREATE TABLE instances (
  id INTEGER PRIMARY KEY, processus TEXT NOT NULL, type TEXT NOT NULL, libelle TEXT NOT NULL,
  objet_id INTEGER, declencheur TEXT, cree_le TEXT NOT NULL, cree_par TEXT, demo INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE evenements (
  id INTEGER PRIMARY KEY, instance_id INTEGER NOT NULL REFERENCES instances(id), noeud TEXT NOT NULL,
  issue TEXT, acteur TEXT, horodatage TEXT NOT NULL, partiel INTEGER NOT NULL DEFAULT 0, details TEXT
);
CREATE INDEX ix_ev_inst ON evenements(instance_id, horodatage, id);

-- ===================== Bus d'information =====================
CREATE TABLE flux_log (
  id INTEGER PRIMARY KEY, code TEXT NOT NULL, emetteur TEXT NOT NULL, recepteur TEXT NOT NULL,
  objet TEXT NOT NULL, contenu TEXT, processus TEXT, noeud TEXT, instance_id INTEGER,
  volume INTEGER NOT NULL DEFAULT 1, horodatage TEXT NOT NULL, demo INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX ix_flux_h ON flux_log(horodatage);
CREATE INDEX ix_flux_code ON flux_log(code, horodatage);
CREATE TABLE notifications (
  id INTEGER PRIMARY KEY, acteur TEXT NOT NULL, flux_id INTEGER, titre TEXT NOT NULL, message TEXT,
  lien TEXT, lu INTEGER NOT NULL DEFAULT 0, horodatage TEXT NOT NULL
);
CREATE INDEX ix_notif ON notifications(acteur, horodatage);

-- ===================== Marketing : campagnes (P2) =====================
CREATE TABLE campagnes (
  id INTEGER PRIMARY KEY, instance_id INTEGER, nom TEXT NOT NULL, pays TEXT NOT NULL, declencheur TEXT,
  objectifs TEXT NOT NULL, budget_propose REAL, budget_valide REAL, budget_depense REAL NOT NULL DEFAULT 0,
  version_budget INTEGER NOT NULL DEFAULT 0, commentaire_finance TEXT, statut TEXT NOT NULL,
  cout_acquisition REAL, precommandes_attribuees INTEGER, cree_le TEXT NOT NULL, demo INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE budget_lignes (
  id INTEGER PRIMARY KEY, campagne_id INTEGER NOT NULL, version INTEGER NOT NULL, canal TEXT NOT NULL, montant REAL NOT NULL
);
CREATE TABLE influenceurs (
  id INTEGER PRIMARY KEY, pseudo TEXT NOT NULL, nom TEXT NOT NULL, plateforme TEXT NOT NULL, abonnes INTEGER NOT NULL,
  engagement REAL NOT NULL, univers TEXT NOT NULL, ville TEXT, cout_estime REAL NOT NULL
);
CREATE TABLE publications (
  id INTEGER PRIMARY KEY, campagne_id INTEGER, type TEXT NOT NULL, titre TEXT NOT NULL, concept TEXT,
  plateforme TEXT NOT NULL, auteur TEXT NOT NULL, influenceur_id INTEGER, publie_le TEXT NOT NULL,
  vues_finales INTEGER NOT NULL, likes INTEGER, partages INTEGER, commentaires INTEGER, sentiment_positif REAL,
  demo INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE campagne_influenceurs (
  campagne_id INTEGER NOT NULL, influenceur_id INTEGER NOT NULL, selectionne_le TEXT NOT NULL,
  appareil_id INTEGER, appareil_expedie_le TEXT, avis_publie_le TEXT, publication_id INTEGER,
  PRIMARY KEY (campagne_id, influenceur_id)
);
CREATE TABLE appareils_test (
  id INTEGER PRIMARY KEY, numero_serie TEXT NOT NULL UNIQUE, capacite TEXT NOT NULL, coloris TEXT NOT NULL,
  statut TEXT NOT NULL, influenceur_id INTEGER, campagne_id INTEGER, expedie_le TEXT
);
CREATE TABLE mesures (
  id INTEGER PRIMARY KEY, campagne_id INTEGER NOT NULL, numero INTEGER NOT NULL, horodatage TEXT NOT NULL,
  vues INTEGER, mentions INTEGER, sentiment REAL, engagement REAL, me_prevenir INTEGER, intention REAL,
  objectifs_atteints INTEGER, decide_par TEXT, decide_le TEXT, commentaire TEXT
);
CREATE TABLE ajustements (
  id INTEGER PRIMARY KEY, campagne_id INTEGER NOT NULL, horodatage TEXT NOT NULL, ciblage TEXT NOT NULL,
  message TEXT NOT NULL, acteur TEXT NOT NULL
);
CREATE TABLE rapports_campagne (
  id INTEGER PRIMARY KEY, campagne_id INTEGER NOT NULL, horodatage TEXT NOT NULL, synthese TEXT NOT NULL,
  previsions TEXT NOT NULL
);
CREATE TABLE contenus_creation (
  id INTEGER PRIMARY KEY, campagne_id INTEGER, type TEXT NOT NULL, titre TEXT NOT NULL, statut TEXT NOT NULL,
  destinataire TEXT NOT NULL, brief_le TEXT, livre_le TEXT, demo INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE retombees_presse (
  id INTEGER PRIMARY KEY, media TEXT NOT NULL, titre TEXT NOT NULL, tonalite TEXT NOT NULL,
  audience INTEGER NOT NULL, publie_le TEXT NOT NULL, demo INTEGER NOT NULL DEFAULT 0
);

-- ===================== Partenaires externes =====================
CREATE TABLE demandes_credit (
  id INTEGER PRIMARY KEY, precommande_id INTEGER NOT NULL, organisme TEXT NOT NULL, produit TEXT NOT NULL,
  montant REAL NOT NULL, duree_mois INTEGER NOT NULL, statut TEXT NOT NULL, cree_le TEXT NOT NULL,
  decide_le TEXT, motif TEXT
);
CREATE TABLE reprise_grille (modele TEXT PRIMARY KEY, marque TEXT NOT NULL, valeur REAL NOT NULL, maj_le TEXT NOT NULL);
CREATE TABLE estimations_reprise (
  id INTEGER PRIMARY KEY, modele TEXT NOT NULL, etat TEXT NOT NULL, valeur REAL NOT NULL, horodatage TEXT NOT NULL
);
CREATE TABLE operateurs_activations (
  jour TEXT NOT NULL, operateur TEXT NOT NULL, activations_esim INTEGER NOT NULL, ventes INTEGER NOT NULL,
  forfaits_5g INTEGER NOT NULL, PRIMARY KEY (jour, operateur)
);
CREATE TABLE revendeurs_flux (
  id INTEGER PRIMARY KEY, enseigne TEXT NOT NULL, type TEXT NOT NULL, quantite INTEGER NOT NULL,
  horodatage TEXT NOT NULL, commentaire TEXT, demo INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE apps_adaptees (
  id INTEGER PRIMARY KEY, nom TEXT NOT NULL, editeur TEXT NOT NULL, categorie TEXT NOT NULL,
  soumise_le TEXT NOT NULL, statut TEXT NOT NULL, demo INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE etudes (
  id INTEGER PRIMARY KEY, institut TEXT NOT NULL, titre TEXT NOT NULL, type TEXT NOT NULL, commandee_le TEXT NOT NULL,
  livree_le TEXT, statut TEXT NOT NULL, resultat TEXT, demo INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE reglementation (
  id INTEGER PRIMARY KEY, autorite TEXT NOT NULL, sens TEXT NOT NULL, titre TEXT NOT NULL, contenu TEXT,
  horodatage TEXT NOT NULL, statut TEXT NOT NULL, demo INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE veille (
  id INTEGER PRIMARY KEY, concurrent TEXT NOT NULL, produit TEXT NOT NULL, prix REAL NOT NULL, releve_le TEXT NOT NULL,
  source TEXT NOT NULL, commentaire TEXT
);
CREATE TABLE briefs_agence (
  id INTEGER PRIMARY KEY, agence TEXT NOT NULL, titre TEXT NOT NULL, budget REAL NOT NULL, statut TEXT NOT NULL,
  envoye_le TEXT NOT NULL, livre_le TEXT, rapport TEXT, demo INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE validations_juridiques (
  id INTEGER PRIMARY KEY, objet TEXT NOT NULL, type TEXT NOT NULL, demandeur TEXT NOT NULL, statut TEXT NOT NULL,
  cree_le TEXT NOT NULL, decide_le TEXT, commentaire TEXT, demo INTEGER NOT NULL DEFAULT 0
);
"""


def creer_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)


def lire_parametre(conn, cle, defaut=None):
    row = conn.execute("SELECT valeur FROM parametres WHERE cle = ?", (cle,)).fetchone()
    return row["valeur"] if row else defaut


def ecrire_parametre(conn, cle, valeur) -> None:
    conn.execute("INSERT INTO parametres(cle, valeur) VALUES (?, ?) "
                 "ON CONFLICT(cle) DO UPDATE SET valeur = excluded.valeur", (cle, str(valeur)))


def base_prete(chemin=None) -> bool:
    p = Path(chemin or chemin_base())
    if not p.exists():
        return False
    try:
        conn = connecter(p)
        try:
            return lire_parametre(conn, "version_schema") == VERSION_SCHEMA and \
                lire_parametre(conn, "seed_termine") == "1"
        finally:
            conn.close()
    except sqlite3.DatabaseError:
        return False


def initialiser(chemin=None, echelle=None, forcer=False) -> Path:
    """Crée et pré-remplit la base si nécessaire (idempotent)."""
    from . import seed  # import local : évite un cycle

    p = Path(chemin or chemin_base())
    with _verrou_init:
        if not forcer and base_prete(p):
            return p
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_suffix(".tmp.db")
        for f in (tmp, Path(str(tmp) + "-wal"), Path(str(tmp) + "-shm")):
            if f.exists():
                f.unlink()
        conn = sqlite3.connect(str(tmp))
        conn.row_factory = sqlite3.Row
        try:
            creer_schema(conn)
            if echelle is None:
                echelle = float(os.environ.get("SI_SEED_ECHELLE", "1.0"))
            seed.pre_remplir(conn, echelle=echelle)
            ecrire_parametre(conn, "version_schema", VERSION_SCHEMA)
            ecrire_parametre(conn, "seed_termine", "1")
            conn.commit()
        finally:
            conn.close()
        for f in (p, Path(str(p) + "-wal"), Path(str(p) + "-shm")):
            if f.exists():
                f.unlink()
        os.replace(str(tmp), str(p))
        return p
