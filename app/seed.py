"""Pré-remplissage déterministe de la base du SI (données fictives, cohérentes et datées).

Calage sur le dossier (§ 6.3) : au lundi 12/10/2026, le tableau de bord hebdomadaire
affiche exactement 2 350 000 visites, 96 000 inscriptions « Me prévenir »,
17 200 rendez-vous, 31 M de vues TikTok, 54 % de commentaires positifs,
6 % d'intention d'achat et 19 % de visiteurs Android.
"""
import json
import math
import random
import unicodedata
from datetime import datetime, timedelta
from typing import Dict, List

from . import horloge
from .bus import emettre
from .db import ecrire_parametre
from .horloge import fmt, parse
from .metier import (CAPACITES, COLORIS, OUVERTURE, SORTIE, _DIURNE, chiffrer, courbe_vues, euros, ht,
                     libelle_delai, profil_horaire)
from .moteur import creer_instance, enregistrer
from .referentiel import APPLE_STORES_FR, COUTS_REVIENT, PAYS, PRODUIT
from .seed_donnees import (APPAREILS, APPS, CONCURRENTS, DOMAINES, ETATS_REPRISE, INFLUENCEURS, NOMS, PRENOMS,
                           PRESSE, REPRISE, SUJETS_SAV, VIDEOS_APPLE, VILLES)

KEYNOTE = parse("2026-09-09T19:00:00")
FIN_DONNEES = parse("2026-11-04T23:59:00")
T_DEFAUT = parse("2026-10-19T10:00:00")
LUNDI_12 = parse("2026-10-12T00:00:00")

MIX_OFFRE_CAP = {"256": .38, "512": .34, "1T": .20, "2T": .08}
MIX_OFFRE_COL = {"naturel": .30, "noir": .32, "blanc": .18, "bleu": .20}
MIX_DEMANDE_CAP = {"256": .33, "512": .36, "1T": .22, "2T": .09}
MIX_DEMANDE_COL = {"naturel": .27, "noir": .35, "blanc": .16, "bleu": .22}

# pays : (stock de lancement au 23/10, production hebdomadaire, précommandes de la semaine)
PAYS_VOLUMES = {
    "FR": (30000, 5500, 38500), "DE": (42000, 6000, 29000), "UK": (45000, 7000, 51000),
    "IT": (18000, 2500, 16500), "ES": (16000, 2300, 14800), "US": (420000, 60000, 505000),
    "JP": (95000, 12000, 88000), "IN": (22000, 3500, 31000), "CN": (260000, 40000, 214000),
}
SEMAINES_PROD = ["2026-10-30", "2026-11-06", "2026-11-13", "2026-11-20", "2026-11-27", "2026-12-04"]


def _jours(d0: datetime, d1: datetime):
    d = datetime(d0.year, d0.month, d0.day)
    while d <= d1:
        yield d
        d += timedelta(days=1)


def _sans_accent(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return "".join(c for c in s.lower() if c.isalnum())


def _repartir(total: int, poids: List[float]) -> List[int]:
    """Répartit un entier selon des poids (méthode du plus fort reste) : somme exacte garantie."""
    s = float(sum(poids))
    bruts = [total * p / s for p in poids]
    ent = [int(math.floor(b)) for b in bruts]
    reste = total - sum(ent)
    for i in sorted(range(len(poids)), key=lambda i: bruts[i] - ent[i], reverse=True)[:reste]:
        ent[i] += 1
    return ent


class Ctx:
    def __init__(self, conn, echelle: float):
        self.conn = conn
        self.rng = random.Random(20261016)
        self.echelle = max(0.001, float(echelle))
        self.kpi: Dict[tuple, float] = {}

    def kpi_jour(self, jour: datetime, indicateur: str, valeur: float, pays: str = "FR"):
        self.kpi[(jour.strftime("%Y-%m-%d"), pays, indicateur)] = valeur

    def instant_dans_jour(self, jour: datetime, debut_h: int = 0) -> datetime:
        poids = [(_DIURNE[h] if h >= debut_h else 0.0) for h in range(24)]
        h = self.rng.choices(range(24), weights=poids)[0]
        return jour + timedelta(hours=h, seconds=self.rng.randint(0, 3599))


# =============================================================================
def pre_remplir(conn, echelle: float = 1.0) -> None:
    ctx = Ctx(conn, echelle)
    ecrire_parametre(conn, "horloge_base", fmt(T_DEFAUT))
    ecrire_parametre(conn, "horloge_reel", "0")  # sera recalé au démarrage du serveur
    ecrire_parametre(conn, "horloge_vitesse", "1")
    ecrire_parametre(conn, "horloge_preset", horloge.PRESET_DEFAUT)
    ecrire_parametre(conn, "mode_execution", "pas_a_pas")
    ecrire_parametre(conn, "echelle", echelle)
    ecrire_parametre(conn, "seq_reference", "104000")

    _referentiels_erp(ctx)
    _kpi_avant_lancement(ctx)
    _clients_inscrits(ctx)
    inf_ids = _influenceurs_et_appareils(ctx)
    camp1 = _campagne_lancement(ctx, inf_ids)
    _lots(ctx)
    _precommandes(ctx)
    _precommandes_autres_pays(ctx)
    _analyses(ctx)
    _campagne_relance(ctx)
    _depenses_et_cac(ctx, camp1)
    _precommandes_en_attente(ctx)
    _partenaires(ctx)
    _flux_historiques(ctx)
    _kpi_flush(ctx)
    _finaliser_notifications(ctx)


# =============================================================================
def _referentiels_erp(ctx: Ctx) -> None:
    c = ctx.conn
    for cap in PRODUIT["capacites"]:
        c.execute("INSERT INTO prix(capacite, prix_ttc, valide_le, valide_par) VALUES (?,?,?,?)",
                  (cap["id"], cap["prix"], "2026-09-03T17:00:00", "finance"))
    for comp, fourn, prevu, reel in COUTS_REVIENT:
        c.execute("INSERT INTO couts_revient(composant, fournisseur, cout_prevu, cout_reel, maj_le) VALUES (?,?,?,?,?)",
                  (comp, fourn, prevu, reel, "2026-10-08T10:00:00"))
    c.execute("INSERT INTO objectifs_marge(taux, defini_le, commentaire) VALUES (?,?,?)",
              (48.0, "2026-08-28T18:00:00",
               "Marge brute cible iPhone Duo (moyenne toutes capacités) malgré la hausse du coût de la mémoire."))
    plan1 = {
        "pays": ["FR", "DE", "UK", "IT", "ES", "US", "JP", "CN"],
        "dates": {"keynote": "9 septembre 2026, 19 h", "precommandes": "16 octobre 2026, 14 h",
                  "sortie": "23 octobre 2026"},
        "budget_marketing_france": 1950000,
        "objectifs": {"visites": 2000000, "me_prevenir": 120000, "rdv_demo": 15000, "vues_tiktok": 20000000,
                      "sentiment": 60, "intention": 8, "android": 15},
        "messages": ["Premier iPhone pliable", "Solidité de la charnière en titane", "Nouveaux usages",
                     "Confidentialité (IA sur l'appareil)"],
    }
    c.execute("INSERT INTO plans_lancement(titre, pays, contenu, soumis_le, statut, decide_le, commentaire) "
              "VALUES (?,?,?,?,?,?,?)",
              ("Plan de lancement iPhone Duo — vague 1 (Europe, Amériques, Asie)", "Monde", json.dumps(plan1),
               "2026-09-02T18:30:00", "valide", "2026-09-04T11:00:00",
               "Validé. Vigilance sur les volumes d'écrans (fournisseur unique)."))
    plan2 = {"pays": ["IN"], "dates": {"precommandes": "6 novembre 2026", "sortie": "13 novembre 2026"},
             "budget_marketing_inde": 2400000, "objectifs": {"precommandes": 45000},
             "messages": ["Paiement en plusieurs fois", "Fabrication locale"]}
    c.execute("INSERT INTO plans_lancement(titre, pays, contenu, soumis_le, statut) VALUES (?,?,?,?,?)",
              ("Plan de lancement iPhone Duo — vague 2 (Inde)", "IN", json.dumps(plan2),
               "2026-10-19T08:30:00", "soumis"))
    c.execute("INSERT INTO budgets_production(montant, motif, accorde_le) VALUES (?,?,?)",
              (1003000000.0, "Budget de production vague 1 (948 000 appareils, monde)", "2026-09-05T10:00:00"))
    for modele, marque, valeur in REPRISE:
        c.execute("INSERT INTO reprise_grille(modele, marque, valeur, maj_le) VALUES (?,?,?,?)",
                  (modele, marque, float(valeur), "2026-10-12T08:00:00"))
    # Capacités Samsung Display (écrans pliables) et commandes d'Apple (flux FE-04)
    lundi = parse("2026-09-28T00:00:00")
    for i in range(11):
        sem = (lundi + timedelta(days=7 * i)).strftime("%Y-%m-%d")
        c.execute("INSERT INTO capacites_fournisseurs(fournisseur, composant, semaine, capacite, engagee, declare_le) "
                  "VALUES (?,?,?,?,?,?)", ("Samsung Display", "Écran pliable OLED", sem, 280000, 252000,
                                           "2026-09-25T09:00:00"))
        c.execute("INSERT INTO capacites_fournisseurs(fournisseur, composant, semaine, capacite, engagee, declare_le) "
                  "VALUES (?,?,?,?,?,?)", ("Foxconn", "Assemblage iPhone Duo", sem, 300000, 262000,
                                           "2026-09-25T09:00:00"))
        statut = "livrée" if lundi + timedelta(days=7 * i + 6) < T_DEFAUT else "confirmée"
        c.execute("INSERT INTO commandes_fournisseurs(fournisseur, composant, quantite, semaine, statut, cree_le, livre_le) "
                  "VALUES (?,?,?,?,?,?,?)",
                  ("Samsung Display", "Écran pliable OLED", 250000, sem, statut, "2026-09-21T10:00:00",
                   fmt(lundi + timedelta(days=7 * i + 5)) if statut == "livrée" else None))


# =============================================================================
def _kpi_avant_lancement(ctx: Ctx) -> None:
    """Visites, rendez-vous, mentions (quotidien) et mesures hebdomadaires — calés sur le § 6.3."""
    visites_avant = [260, 215, 150, 95, 80, 72, 64, 58, 55, 62, 66, 60, 58, 54, 51, 49, 52, 55, 50, 47, 45, 44, 43,
                     45, 47, 44, 46, 44, 43, 45, 49, 52, 50]                       # 9/09 -> 11/10
    visites_apres = [58, 62, 66, 74, 190, 120, 96, 82, 74, 70, 76, 140, 98, 84, 70, 64, 60, 57, 55, 50, 47, 52, 50, 48]
    jours_avant = list(_jours(KEYNOTE, parse("2026-10-11T00:00:00")))
    jours_apres = list(_jours(parse("2026-10-12T00:00:00"), FIN_DONNEES))
    vals = _repartir(2350000, visites_avant)
    facteur = 2350000.0 / sum(visites_avant)
    for d, v in zip(jours_avant, vals):
        ctx.kpi_jour(d, "visites", v)
    for d, raw in zip(jours_apres, visites_apres):
        ctx.kpi_jour(d, "visites", int(raw * facteur))
    # Rendez-vous de démonstration en Apple Store (à partir du 18/09) : 17 200 au 11/10
    jours_rdv = list(_jours(parse("2026-09-18T00:00:00"), parse("2026-10-11T00:00:00")))
    brut = [1150, 980, 640, 760, 720, 700, 690, 740, 820, 560, 700, 680, 660, 650, 690, 760, 540, 690, 670, 660, 650,
            700, 780, 600]
    for d, v in zip(jours_rdv, _repartir(17200, brut)):
        ctx.kpi_jour(d, "rdv_demo", v)
    for d in _jours(parse("2026-10-12T00:00:00"), FIN_DONNEES):
        base = 780 if d < OUVERTURE else (860 if d < SORTIE else 380)
        ctx.kpi_jour(d, "rdv_demo", int(base * (0.9 + 0.2 * ctx.rng.random())))
    # Mentions sur les réseaux sociaux (social listening)
    for d in _jours(KEYNOTE, FIN_DONNEES):
        n = (d - KEYNOTE.replace(hour=0)).days
        v = 9000 + 40000 * math.exp(-n / 1.6)
        if parse("2026-09-18T00:00:00") <= d <= parse("2026-09-27T00:00:00"):
            v += 5200
        if d.strftime("%m-%d") in ("10-13", "10-14"):
            v += 5000
        if d.strftime("%m-%d") == "10-16":
            v += 38000
        if d.strftime("%m-%d") == "10-23":
            v += 33000
        ctx.kpi_jour(d, "mentions", int(v * (0.92 + 0.16 * ctx.rng.random())))
    # Paniers (configurations commencées) pendant les précommandes et après
    for d in _jours(parse("2026-10-16T00:00:00"), FIN_DONNEES):
        ctx.kpi_jour(d, "paniers", int(ctx.kpi[(d.strftime("%Y-%m-%d"), "FR", "visites")] * 0.062))
    hebdo = {
        "sentiment": [49, 51, 52, 53, 54, 62, 66, 68],
        "intention": [4.1, 4.6, 5.2, 5.6, 6.0, 7.4, 7.9, 8.3],
        "android": [22, 21, 20, 19.5, 19, 18, 17.5, 17],
    }
    semaines = [parse("2026-09-14T00:00:00") + timedelta(days=7 * i) for i in range(8)]
    for ind, valeurs in hebdo.items():
        for s, v in zip(semaines, valeurs):
            ctx.conn.execute("INSERT INTO kpi_hebdo(semaine, pays, indicateur, valeur) VALUES (?,?,?,?)",
                             (s.strftime("%Y-%m-%d"), "FR", ind, v))
    for s, sat, ret in (("2026-10-26", 91, 1.9), ("2026-11-02", 92, 2.2)):
        ctx.conn.execute("INSERT INTO kpi_hebdo VALUES (?,?,?,?)", (s, "FR", "satisfaction", sat))
        ctx.conn.execute("INSERT INTO kpi_hebdo VALUES (?,?,?,?)", (s, "FR", "retours", ret))
    ctx.conn.execute("INSERT INTO kpi_hebdo VALUES (?,?,?,?)", ("2026-11-02", "FR", "part_marche_pliables", 41))


# =============================================================================
def _nouveau_client(ctx: Ctx, cid: int, cree_le: datetime, me_prevenir: bool, emails: set) -> tuple:
    r = ctx.rng
    prenom = r.choice(PRENOMS)
    nom = r.choice(NOMS)
    ville, cp, _ = r.choices(VILLES, weights=[v[2] for v in VILLES])[0]
    if ville == "Paris":
        cp = "750%02d" % r.randint(1, 20)
    elif ville == "Lyon":
        cp = "6900%d" % r.randint(1, 9)
    elif ville == "Marseille":
        cp = "130%02d" % r.randint(1, 16)
    app, annee, plateforme, _ = r.choices(APPAREILS, weights=[a[3] for a in APPAREILS])[0]
    age = int(min(72, max(18, r.gauss(36, 11))))
    segment = r.choices(["Particulier", "Créatif / professionnel", "Entreprise", "Éducation"], [84, 7, 6, 3])[0]
    dom = r.choices([d[0] for d in DOMAINES], [d[1] for d in DOMAINES])[0]
    base = "%s.%s" % (_sans_accent(prenom), _sans_accent(nom))
    email = "%s%s@%s" % (base, r.choice(["", str(r.randint(1, 99)), str(r.randint(1975, 2006))]), dom)
    if email in emails:
        email = "%s.%d@%s" % (base, cid, dom)
    emails.add(email)
    abonnements = []
    if plateforme == "iOS":
        for nom_ab, p in (("iCloud+", .62), ("Apple Music", .38), ("Apple TV", .24), ("Apple One", .14),
                          ("AppleCare+", .21), ("Apple Arcade", .06)):
            if r.random() < p:
                abonnements.append(nom_ab)
    source = r.choices(["apple.com", "TikTok", "app Apple Store", "Apple Store (magasin)", "Presse / YouTube"],
                       [46, 18, 14, 12, 10])[0]
    return (cid, email, prenom, nom, age, ville, cp, segment, app, annee, plateforme,
            fmt(cree_le) if me_prevenir else None, 1 if r.random() < 0.64 else 0, ", ".join(abonnements),
            source, fmt(cree_le))


def _clients_inscrits(ctx: Ctx) -> None:
    """Inscriptions « Me prévenir » : 96 000 au 11/10, 120 000 à l'ouverture (16/10 14 h)."""
    brut = [9.6, 7.2, 6.4, 3.9, 3.3, 2.9, 2.6, 2.4, 2.3, 2.8, 3.0, 2.6, 2.5, 2.3, 2.2, 2.1, 2.4, 2.5, 2.2, 2.0, 1.9,
            1.9, 1.8, 1.9, 2.0, 1.9, 1.9, 2.1, 2.0, 1.9, 2.1, 2.2, 2.0]
    jours1 = list(_jours(KEYNOTE, parse("2026-10-11T00:00:00")))
    par_jour = list(zip(jours1, _repartir(96000, brut)))
    jours2 = list(_jours(parse("2026-10-12T00:00:00"), parse("2026-10-16T00:00:00")))
    par_jour += list(zip(jours2, _repartir(24000, [5.6, 6.2, 5.9, 4.4, 1.9])))
    lignes, emails = [], set()
    cid = 0
    for jour, n in par_jour:
        ctx.kpi_jour(jour, "me_prevenir", n)
        n_lignes = int(round(n * ctx.echelle))
        for _ in range(n_lignes):
            cid += 1
            if jour.date() == KEYNOTE.date():
                t = ctx.instant_dans_jour(jour, debut_h=19)
            elif jour.date() == OUVERTURE.date():
                t = jour + timedelta(seconds=ctx.rng.randint(0, 14 * 3600 - 1))
            else:
                t = ctx.instant_dans_jour(jour)
            lignes.append(_nouveau_client(ctx, cid, t, True, emails))
    ctx.conn.executemany(
        "INSERT INTO clients(id, apple_id, prenom, nom, age, ville, code_postal, segment, appareil, appareil_annee, "
        "plateforme, me_prevenir_le, consentement_marketing, abonnements, source, cree_le) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", lignes)
    ctx.emails = emails
    ctx.prochain_client = cid + 1
    # pool des inscrits (les plus anciens appareils précommandent plus volontiers)
    ids = [l[0] for l in lignes]
    ctx.rng.shuffle(ids)
    ctx.pool_inscrits = ids
    ctx.client_info = {l[0]: (l[8], l[10]) for l in lignes}


# =============================================================================
def _influenceurs_et_appareils(ctx: Ctx) -> List[int]:
    c = ctx.conn
    ids = []
    for pseudo, nom, plat, abonnes, eng, univ, ville, cout in INFLUENCEURS:
        cur = c.execute("INSERT INTO influenceurs(pseudo, nom, plateforme, abonnes, engagement, univers, ville, "
                        "cout_estime) VALUES (?,?,?,?,?,?,?,?)", (pseudo, nom, plat, abonnes, eng, univ, ville, cout))
        ids.append(cur.lastrowid)
    caps, cols = list(CAPACITES), list(COLORIS)
    for i in range(40):
        c.execute("INSERT INTO appareils_test(numero_serie, capacite, coloris, statut) VALUES (?,?,?,?)",
                  ("DUO-PS-%04d" % (i + 1), caps[i % 4], cols[(i // 4) % 4], "disponible"))
    return ids


def _vues_tiktok_a(ctx: Ctx, t: datetime) -> float:
    return sum(courbe_vues(v, d, t) for (d, v) in ctx.videos)


def _campagne_lancement(ctx: Ctx, inf_ids: List[int]) -> int:
    """P2 — campagne TikTok de lancement (France) : instance BPMN complète du 9/09 au 17/10."""
    c = ctx.conn
    objectifs = {"vues_tiktok": 20000000, "sentiment": 60, "mentions": 400000, "me_prevenir": 120000,
                 "intention": 8}
    inst = creer_instance(c, "P2", "campagne", "Campagne TikTok de lancement — France", fmt(KEYNOTE),
                          "dir_marketing", declencheur="Keynote du 9/09 (événement de début)")
    cur = c.execute("INSERT INTO campagnes(instance_id, nom, pays, declencheur, objectifs, statut, cree_le) "
                    "VALUES (?,?,?,?,?,?,?)",
                    (inst, "Lancement iPhone Duo — TikTok & influence", "FR", "Keynote du 9/09",
                     json.dumps(objectifs), "en_cours", fmt(KEYNOTE)))
    camp = cur.lastrowid
    c.execute("UPDATE instances SET objet_id = ? WHERE id = ?", (camp, inst))

    def ev(noeud, t, acteur, issue=None, details="", partiel=False):
        enregistrer(c, inst, noeud, t, acteur, issue=issue, details=details, partiel=partiel)

    def fx(code, objet, t, contenu="", noeud=None, **kw):
        emettre(c, code, objet, t, contenu=contenu, processus="P2", noeud=noeud, instance_id=inst, **kw)

    # Brief créatif et consignes (Fig. 3) avant la proposition
    fx("FM-05", "Calendrier keynote « Surprise and Shine » et tests presse", "2026-09-02T10:00:00")
    fx("FM-07", "Brief créatif : montrer les usages du pliable, ton humoristique", "2026-09-03T10:00:00")
    # T01 v1 -> G01 non -> T01 v2 -> G01 oui
    lignes_v1 = [("TikTok Ads", 1100000), ("Influence", 650000), ("Production de contenus", 380000),
                 ("Achat média social (Meta, YouTube)", 220000), ("Études et social listening", 100000)]
    lignes_v2 = [("TikTok Ads", 950000), ("Influence", 520000), ("Production de contenus", 330000),
                 ("Achat média social (Meta, YouTube)", 100000), ("Études et social listening", 50000)]
    for canal, m in lignes_v1:
        c.execute("INSERT INTO budget_lignes(campagne_id, version, canal, montant) VALUES (?,?,?,?)", (camp, 1, canal, m))
    ev("T01", "2026-09-10T09:30:00", "dir_marketing", details="Version 1 : 2 450 000 € — objectifs du plan de lancement")
    fx("FI-06", "Proposition de budget de campagne v1 : 2 450 000 €", "2026-09-10T09:30:00", noeud="T01")
    fx("FM-01", "Demande de budget — campagne TikTok de lancement", "2026-09-10T09:31:00", noeud="T01")
    ev("G01", "2026-09-10T16:45:00", "finance", issue="non",
       details="Budget supérieur de 26 % à l'enveloppe : réduire l'achat média et prioriser TikTok.")
    fx("FI-07", "Budget refusé (non : revoir) — réduire l'achat média", "2026-09-10T16:45:00", noeud="G01")
    for canal, m in lignes_v2:
        c.execute("INSERT INTO budget_lignes(campagne_id, version, canal, montant) VALUES (?,?,?,?)", (camp, 2, canal, m))
    ev("T01", "2026-09-11T09:15:00", "dir_marketing", details="Version 2 : 1 950 000 €")
    fx("FI-06", "Proposition de budget de campagne v2 : 1 950 000 €", "2026-09-11T09:15:00", noeud="T01")
    ev("G01", "2026-09-11T11:40:00", "finance", issue="oui", details="Budget accordé : 1 950 000 €")
    fx("FI-07", "Budget accordé : 1 950 000 €", "2026-09-11T11:40:00", noeud="G01")
    fx("FM-02", "Budget accordé — campagne TikTok de lancement", "2026-09-11T11:41:00", noeud="G01")
    fx("FM-08", "Objectifs et budget transmis à l'équipe réseaux sociaux", "2026-09-11T12:00:00", noeud="G01")
    c.execute("UPDATE campagnes SET budget_propose=?, budget_valide=?, version_budget=2, commentaire_finance=? "
              "WHERE id=?", (1950000, 1950000, "Validé après révision (v1 : 2 450 000 €)", camp))
    # Vidéos Apple (T02 + vidéos ultérieures issues des ajustements)
    K = 1.0
    ctx.videos = [(d, w) for (d, _t, _c, w) in VIDEOS_APPLE]
    brut = sum(courbe_vues(w, d, LUNDI_12) for d, w in ctx.videos)
    K = 31000000.0 / brut
    ctx.videos = [(d, w * K) for (d, w) in ctx.videos]
    for (d, titre, concept, w) in VIDEOS_APPLE:
        vf = int(w * K)
        c.execute("INSERT INTO publications(campagne_id, type, titre, concept, plateforme, auteur, publie_le, "
                  "vues_finales, likes, partages, commentaires, sentiment_positif) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                  (camp, "video_apple", titre, concept, "TikTok", "@apple", d, vf, int(vf * 0.061),
                   int(vf * 0.0043), int(vf * 0.0021), round(50 + ctx.rng.random() * 14, 1)))
        c.execute("INSERT INTO contenus_creation(campagne_id, type, titre, statut, destinataire, brief_le, livre_le) "
                  "VALUES (?,?,?,?,?,?,?)", (camp, "Vidéo TikTok", titre, "livré", "mkt_social",
                                            "2026-09-03T10:00:00", fmt(parse(d) - timedelta(hours=20))))
    fx("FM-10", "5 vidéos TikTok livrées (yoga, café, cinéma de poche, pliage, selfie)", "2026-09-10T22:00:00")
    ev("T02", "2026-09-11T18:00:00", "mkt_social", details="5 vidéos publiées sur @apple")
    fx("FE-06A", "Publication de 5 vidéos TikTok sur le compte officiel", "2026-09-11T18:00:00", noeud="T02",
       emetteur="mkt_social", recepteur="influenceur", notifier=False)
    fx("FE-07A", "Brief achat média TikTok Ads (950 000 €)", "2026-09-11T18:30:00", noeud="T02")
    # T03 sélection de 12 influenceurs
    choisis = [inf_ids[i] for i in (0, 1, 2, 3, 4, 5, 6, 7, 9, 11, 14, 15)]
    for iid in choisis:
        c.execute("INSERT INTO campagne_influenceurs(campagne_id, influenceur_id, selectionne_le) VALUES (?,?,?)",
                  (camp, iid, "2026-09-14T10:00:00"))
    ev("T03", "2026-09-14T10:00:00", "mkt_social", details="12 influenceurs sélectionnés")
    fx("FI-13", "Demande de 12 appareils de pré-série pour les influenceurs", "2026-09-14T10:05:00", noeud="T03")
    fx("FE-06A", "Invitations envoyées à 12 créateurs de contenu", "2026-09-14T10:10:00", noeud="T03")
    # T04 appareils de test
    app_ids = [r[0] for r in c.execute("SELECT id FROM appareils_test ORDER BY id LIMIT 12").fetchall()]
    for iid, aid in zip(choisis, app_ids):
        c.execute("UPDATE appareils_test SET statut='expédié', influenceur_id=?, campagne_id=?, expedie_le=? "
                  "WHERE id=?", (iid, camp, "2026-09-16T15:00:00", aid))
        c.execute("UPDATE campagne_influenceurs SET appareil_id=?, appareil_expedie_le=? "
                  "WHERE campagne_id=? AND influenceur_id=?", (aid, "2026-09-16T15:00:00", camp, iid))
    ev("T04", "2026-09-16T15:00:00", "production", details="12 appareils de pré-série expédiés")
    fx("FE-06A", "12 appareils de test expédiés aux influenceurs", "2026-09-16T15:00:00", noeud="T04",
       emetteur="production")
    # T05 avis des influenceurs (multi-instance)
    debut = parse("2026-09-18T12:00:00")
    for k, iid in enumerate(choisis):
        t = debut + timedelta(hours=int(k * 19.5 + ctx.rng.randint(0, 6)))
        inf = c.execute("SELECT * FROM influenceurs WHERE id=?", (iid,)).fetchone()
        vf = int(inf["abonnes"] * (0.35 + ctx.rng.random() * 0.9))
        senti = round(58 + ctx.rng.random() * 27, 1)
        cur = c.execute("INSERT INTO publications(campagne_id, type, titre, concept, plateforme, auteur, influenceur_id, "
                        "publie_le, vues_finales, likes, partages, commentaires, sentiment_positif) "
                        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                        (camp, "avis_influenceur", "J'ai testé l'iPhone Duo pendant une semaine", inf["univers"],
                         inf["plateforme"], inf["pseudo"], iid, fmt(t), vf, int(vf * inf["engagement"] / 100),
                         int(vf * 0.004), int(vf * 0.003), senti))
        c.execute("UPDATE campagne_influenceurs SET avis_publie_le=?, publication_id=? WHERE campagne_id=? AND "
                  "influenceur_id=?", (fmt(t), cur.lastrowid, camp, iid))
        ev("T05", fmt(t), "influenceur", details="Avis publié par %s" % inf["pseudo"], partiel=True)
        fx("FE-06R", "Avis publié par %s (%s abonnés)" % (inf["pseudo"], "{:,}".format(inf["abonnes"]).replace(",", " ")),
           fmt(t), noeud="T05", emetteur="influenceur")
        dernier = t
    ev("T05", fmt(dernier + timedelta(minutes=1)), "influenceur", details="Les 12 avis sont publiés")
    # Mesures / ajustements (boucle)
    mesures = [
        ("2026-09-28T09:00:00", 52.0, 5.2, "non", "2026-09-28T10:30:00",
         ("2026-09-28T15:00:00", "25-44 ans CSP+, utilisateurs d'Android équipés d'un pliable",
          "Insister sur la solidité de la charnière en titane")),
        ("2026-10-05T09:00:00", 53.0, 5.6, "non", "2026-10-05T11:00:00",
         ("2026-10-05T16:00:00", "Audiences « productivité » et « cinéma / séries »",
          "Montrer les usages : bureau nomade, cinéma de poche ; répondre aux commentaires sur le prix")),
        ("2026-10-12T09:00:00", 54.0, 6.0, "non", "2026-10-12T10:00:00",
         ("2026-10-12T14:00:00", "Possesseurs d'un iPhone de plus de 3 ans (CRM) et inscrits « Me prévenir »",
          "Mettre en avant l'offre de reprise et le paiement en 10 fois sans frais")),
        ("2026-10-15T18:00:00", 61.0, 6.9, "oui", "2026-10-15T19:00:00", None),
    ]
    depense = {"2026-09-28": 640000, "2026-10-05": 1050000, "2026-10-12": 1520000, "2026-10-15": 1780000}
    for num, (t, senti, inten, decision, t_dec, ajust) in enumerate(mesures, start=1):
        tt = parse(t)
        vues = int(_vues_tiktok_a(ctx, tt))
        if t.startswith("2026-10-12"):
            vues = 31000000
        mentions = int(sum(v for (j, p, i), v in ctx.kpi.items()
                           if i == "mentions" and p == "FR" and parse(j + "T00:00:00") < tt.replace(hour=0)))
        me = int(sum(v for (j, p, i), v in ctx.kpi.items()
                     if i == "me_prevenir" and parse(j + "T00:00:00") < tt.replace(hour=0)))
        if t.startswith("2026-10-15"):
            me = 116000
        engagement = round(5.2 + num * 0.3, 1)
        ev("T06", t, "mkt_data", details="Mesure n°%d" % num)
        fx("FM-14", "Vues, mentions, engagement de la semaine (mesure n°%d)" % num, t, noeud="T06",
           emetteur="mkt_social", recepteur="mkt_data", notifier=False)
        c.execute("INSERT INTO mesures(campagne_id, numero, horodatage, vues, mentions, sentiment, engagement, "
                  "me_prevenir, intention, objectifs_atteints, decide_par, decide_le, commentaire) "
                  "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                  (camp, num, t, vues, mentions, senti, engagement, me, inten, 1 if decision == "oui" else 0,
                   "dir_marketing", t_dec,
                   "Objectifs principaux atteints (vues, sentiment) ; « Me prévenir » à 97 %." if decision == "oui"
                   else "Sentiment et intention d'achat sous l'objectif."))
        c.execute("UPDATE campagnes SET budget_depense=? WHERE id=?", (depense[t[:10]], camp))
        ev("G02", t_dec, "dir_marketing", issue=decision)
        fx("FM-17", "Tableau de bord de campagne — mesure n°%d (objectifs atteints : %s)" % (num, decision), t_dec,
           noeud="G02", emetteur="mkt_data", recepteur="dir_marketing")
        if ajust:
            ta, ciblage, message = ajust
            ev("T07", ta, "mkt_social", details=message)
            c.execute("INSERT INTO ajustements(campagne_id, horodatage, ciblage, message, acteur) VALUES (?,?,?,?,?)",
                      (camp, ta, ciblage, message, "mkt_social"))
            fx("FM-15", "Nouveau ciblage des audiences : %s" % ciblage, fmt(parse(ta) - timedelta(minutes=30)),
               noeud="T07", emetteur="mkt_data", recepteur="mkt_social")
            fx("FE-07A", "Brief ajusté à l'agence média : %s" % message, ta, noeud="T07")
    # T08 rapport et prévisions
    previsions = {"FR": {"total": 38000, "coloris": {"noir": 35, "naturel": 27, "bleu": 22, "blanc": 16},
                         "capacites": {"512": 36, "256": 33, "1T": 22, "2T": 9}},
                  "DE": {"total": 30000}, "UK": {"total": 50000}, "IT": {"total": 16000}, "ES": {"total": 15000}}
    ev("T08", "2026-10-16T09:00:00", "dir_marketing", details="Rapport de campagne et prévisions de demande")
    c.execute("INSERT INTO rapports_campagne(campagne_id, horodatage, synthese, previsions) VALUES (?,?,?,?)",
              (camp, "2026-10-16T09:00:00",
               "36,4 M de vues TikTok, 61 % de commentaires positifs, 116 000 inscrits « Me prévenir ». "
               "Frein principal : le prix. Leviers activés : reprise et paiement en 10 fois.", json.dumps(previsions)))
    fx("FI-04", "Prévisions de demande France : 38 000 précommandes (noir 35 %, 512 Go 36 %)", "2026-10-16T09:00:00",
       noeud="T08")
    fx("FM-03", "Prévisions de demande par pays transmises à la production", "2026-10-16T09:01:00", noeud="T08")
    fx("FM-18", "Rapport de campagne : dépenses 1 780 000 € à date", "2026-10-16T09:02:00", noeud="T08")
    ctx.camp1_inst = inst
    return camp


# =============================================================================
def _lots(ctx: Ctx) -> None:
    """Allocation de lancement, production hebdomadaire et ajustements (P2-T09 le 16/10, P1-T11 le 17/10)."""
    c = ctx.conn
    e = ctx.echelle  # la France est détaillée précommande par précommande : ses stocks suivent la même échelle
    rows = []
    for pays, (stock, hebdo, _d) in PAYS_VOLUMES.items():
        if pays == "FR":
            stock, hebdo = stock * e, hebdo * e
            for cap, pc in MIX_OFFRE_CAP.items():
                for col, pk in MIX_OFFRE_COL.items():
                    rows.append((pays, cap, col, int(round(stock * pc * pk)), "2026-10-23T08:00:00",
                                 "Allocation de lancement (plan validé)", "2026-10-01T09:00:00"))
                    for s in SEMAINES_PROD:
                        rows.append((pays, cap, col, int(round(hebdo * pc * pk)), s + "T08:00:00",
                                     "Production hebdomadaire planifiée", "2026-10-01T09:00:00"))
        else:
            rows.append((pays, None, None, stock, "2026-10-23T08:00:00", "Allocation de lancement (plan validé)",
                         "2026-10-01T09:00:00"))
            for s in SEMAINES_PROD:
                rows.append((pays, None, None, hebdo, s + "T08:00:00", "Production hebdomadaire planifiée",
                             "2026-10-01T09:00:00"))
    # P2-T09 (16/10 11:30) : ajustement du mix coloris d'après les prévisions (noir +1 200 sur le lot du 30/10)
    for cap, pc in MIX_OFFRE_CAP.items():
        rows.append(("FR", cap, "noir", int(round(1200 * pc * e)), "2026-10-30T08:00:00",
                     "Ajustement du plan (P2-T09) : +1 200 Titane noir", "2026-10-16T11:30:00"))
    # P1-T11 (17/10 11:00) : transfert de 3 000 unités DE -> FR et +2 000 / semaine pendant 4 semaines
    for cap, pc in MIX_DEMANDE_CAP.items():
        for col, pk in MIX_DEMANDE_COL.items():
            rows.append(("FR", cap, col, int(round(3000 * pc * pk * e)), "2026-10-23T08:00:00",
                         "Transfert depuis l'Allemagne (P1-T11)", "2026-10-17T11:00:00"))
            for s in SEMAINES_PROD[:4]:
                rows.append(("FR", cap, col, int(round(2000 * pc * pk * e)), s + "T08:00:00",
                             "Hausse de production (P1-T11)", "2026-10-17T11:00:00"))
    rows.append(("DE", None, None, -3000, "2026-10-23T08:00:00", "Transfert vers la France (P1-T11)",
                 "2026-10-17T11:00:00"))
    c.executemany("INSERT INTO lots_production(pays, capacite, coloris, quantite, disponible_le, origine, cree_le) "
                  "VALUES (?,?,?,?,?,?,?)", rows)


# =============================================================================
def _heures_commandes(ctx: Ctx) -> List[datetime]:
    """Instants de création des commandes France (précommandes puis commandes après la sortie)."""
    instants: List[datetime] = []
    total = PAYS_VOLUMES["FR"][2] * ctx.echelle
    for (h, p) in profil_horaire():
        n = int(total * p + ctx.rng.random())
        for _ in range(n):
            instants.append(h + timedelta(seconds=ctx.rng.randint(0, 3599)))
    apres = [1500, 1200, 900, 1000, 900, 850, 800, 780, 760, 740, 720, 700, 680]
    for j, n_jour in enumerate(apres):
        jour = parse("2026-10-23T00:00:00") + timedelta(days=j)
        for _ in range(int(n_jour * ctx.echelle)):
            t = ctx.instant_dans_jour(jour, debut_h=8 if j == 0 else 0)
            if t <= FIN_DONNEES:
                instants.append(t)
    instants.sort()
    return instants


def _precommandes(ctx: Ctx) -> None:
    c, r = ctx.conn, ctx.rng
    # lots France en mémoire : config -> liste [id, dispo, cree_le, restant]
    lots: Dict[str, list] = {}
    for l in c.execute("SELECT id, capacite, coloris, quantite, disponible_le, cree_le FROM lots_production "
                       "WHERE pays='FR' ORDER BY disponible_le, id"):
        lots.setdefault("%s|%s" % (l["capacite"], l["coloris"]), []).append(
            [l["id"], l["disponible_le"], l["cree_le"], l["quantite"]])
    grille = {m: v for (m, _mq, v) in REPRISE}
    instants = _heures_commandes(ctx)
    caps = list(MIX_DEMANDE_CAP)
    cols = list(MIX_DEMANDE_COL)
    magasins_poids = [3 if ("Paris" in m or m in ("Apple Opéra", "Apple Champs-Élysées", "Apple Marché Saint-Germain"))
                      else 1 for m in APPLE_STORES_FR]
    nouveaux_clients, lignes = [], []
    pool = ctx.pool_inscrits
    seq = 104000
    for t in instants:
        seq += 1
        precommande = t < SORTIE
        # client
        if pool and r.random() < (0.72 if precommande else 0.35):
            cid = pool.pop()
            appareil, plateforme = ctx.client_info[cid]
        else:
            cid = ctx.prochain_client
            ctx.prochain_client += 1
            cl = _nouveau_client(ctx, cid, t - timedelta(minutes=r.randint(2, 30)), False, ctx.emails)
            nouveaux_clients.append(cl)
            appareil, plateforme = cl[8], cl[10]
        cap = r.choices(caps, weights=list(MIX_DEMANDE_CAP.values()))[0]
        col = r.choices(cols, weights=list(MIX_DEMANDE_COL.values()))[0]
        canal = r.choices(["apple.com", "app Apple Store", "Apple Store (magasin)"], [58, 32, 10])[0]
        mode_pay = r.choices(["cb", "apple_pay", "cetelem_10x", "cetelem_24m"], [50, 27, 15, 8])[0]
        applecare = r.random() < 0.33
        reprise_modele, reprise_etat, reprise_val = None, None, 0.0
        if appareil and r.random() < (0.55 if plateforme == "Android" else 0.41):
            etat_id, _lib, fact = r.choices(ETATS_REPRISE, [55, 38, 7])[0]
            reprise_modele, reprise_etat = appareil, etat_id
            reprise_val = round(grille.get(appareil, 40) * fact / 5) * 5
        if canal == "Apple Store (magasin)" or r.random() < 0.30:
            livraison, magasin = "retrait", r.choices(APPLE_STORES_FR, magasins_poids)[0]
        else:
            livraison, magasin = "domicile", None
        ch = chiffrer(cap, applecare)
        refuse = r.random() < 0.024
        abandon = refuse and r.random() < 0.2
        paye = t + timedelta(seconds=r.randint(6, 45) + (r.randint(180, 900) if refuse else 0))
        ref = "W%d" % seq
        if abandon:
            lignes.append((ref, cid, "FR", canal, cap, col, ch["prix_ttc"], ht(ch["prix_ttc"]), int(applecare),
                           ch["applecare_ttc"], reprise_modele, reprise_etat, reprise_val, mode_pay, "refuse",
                           livraison, magasin, None, None, None, 0, "abandonnee", None, None, None, None, None,
                           "Paiement refusé, précommande non finalisée", None, None, None, None, fmt(t), fmt(paye)))
            continue
        crm = paye + timedelta(seconds=r.randint(1, 4))
        reserve = crm + timedelta(seconds=r.randint(20, 240))
        confirme = reserve + timedelta(seconds=r.randint(3, 30))
        # allocation au premier lot disponible (créé avant la réservation)
        lot_id, lot_date = None, None
        for lot in lots["%s|%s" % (cap, col)]:
            if lot[3] > 0 and lot[2] <= fmt(reserve):
                lot[3] -= 1
                lot_id, lot_date = lot[0], lot[1]
                break
        limite = fmt(max(t, SORTIE))
        allonge = 1 if (lot_date is None or lot_date > limite) else 0
        delai = libelle_delai(lot_date, livraison, t)
        lignes.append((ref, cid, "FR", canal, cap, col, ch["prix_ttc"], ht(ch["prix_ttc"]), int(applecare),
                       ch["applecare_ttc"], reprise_modele, reprise_etat, reprise_val, mode_pay, "accepte",
                       livraison, magasin, delai, lot_date[:10] if lot_date else None, lot_id, allonge, "confirmee",
                       ch["ca_ht"], ch["cout_revient"], ch["marge"], None, None, None,
                       fmt(paye), fmt(crm), fmt(reserve), fmt(confirme), fmt(t), fmt(confirme)))
    ecrire_parametre(c, "seq_reference", seq + 1000)
    c.executemany(
        "INSERT INTO clients(id, apple_id, prenom, nom, age, ville, code_postal, segment, appareil, appareil_annee, "
        "plateforme, me_prevenir_le, consentement_marketing, abonnements, source, cree_le) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", nouveaux_clients)
    c.executemany(
        "INSERT INTO precommandes(reference, client_id, pays, canal, capacite, coloris, prix_ttc, prix_ht, applecare, "
        "applecare_ttc, reprise_modele, reprise_etat, reprise_valeur, paiement_mode, paiement_statut, livraison_mode, "
        "magasin, delai_affiche, livraison_prevue, lot_id, delai_allonge, statut, ca_previsionnel_ht, cout_revient, "
        "marge, cout_par_precommande, analyse_id, motif, paye_le, crm_le, reserve_le, confirme_le, cree_le, maj_le) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", lignes)
    # demandes de crédit (flux FE-09) pour les paiements Cetelem
    rows = c.execute("SELECT id, paiement_mode, prix_ttc, applecare_ttc, reprise_valeur, cree_le, paye_le, statut "
                     "FROM precommandes WHERE paiement_mode LIKE 'cetelem%'").fetchall()
    dc = []
    for p in rows:
        montant = p["prix_ttc"] + p["applecare_ttc"] - p["reprise_valeur"]
        dc.append((p["id"], "Cetelem", "10 fois sans frais" if p["paiement_mode"] == "cetelem_10x" else "Crédit 24 mois",
                   montant, 10 if p["paiement_mode"] == "cetelem_10x" else 24,
                   "refuse" if p["statut"] == "abandonnee" else "accorde", p["cree_le"], p["paye_le"],
                   "Score insuffisant" if p["statut"] == "abandonnee" else None))
    c.executemany("INSERT INTO demandes_credit(precommande_id, organisme, produit, montant, duree_mois, statut, cree_le, "
                  "decide_le, motif) VALUES (?,?,?,?,?,?,?,?,?)", dc)
    # estimations de reprise (flux FE-10)
    est = c.execute("SELECT reprise_modele, reprise_etat, reprise_valeur, cree_le FROM precommandes "
                    "WHERE reprise_modele IS NOT NULL").fetchall()
    c.executemany("INSERT INTO estimations_reprise(modele, etat, valeur, horodatage) VALUES (?,?,?,?)",
                  [(e[0], e[1], e[2], e[3]) for e in est])


def _precommandes_autres_pays(ctx: Ctx) -> None:
    rows = []
    for pays, (_s, _h, total) in PAYS_VOLUMES.items():
        if pays == "FR":
            continue
        for (h, p) in profil_horaire():
            n = int(round(total * p * (0.93 + 0.14 * ctx.rng.random())))
            rows.append((pays, fmt(h), n))
    ctx.conn.executemany("INSERT INTO precommandes_pays(pays, heure, nb) VALUES (?,?,?)", rows)


# =============================================================================
def _compter_fr(c, t: str) -> int:
    return c.execute("SELECT COUNT(*) FROM precommandes WHERE pays='FR' AND statut!='abandonnee' AND cree_le <= ?",
                     (t,)).fetchone()[0]


def _compter_pays(c, pays: str, t: str) -> int:
    return c.execute("SELECT COALESCE(SUM(nb),0) FROM precommandes_pays WHERE pays=? AND heure <= ?",
                     (pays, t)).fetchone()[0]


def _analyses(ctx: Ctx) -> None:
    """P1 — analyses du tableau de bord (T10 -> G03 -> T11/T12) seedées."""
    from .metier import projection_sortie
    c = ctx.conn

    def analyse(pays, t_analyse, t_dec, decision, t_action, action, details, demander_production=False):
        n = _compter_fr(c, t_analyse) if pays == "FR" else _compter_pays(c, pays, t_analyse)
        echelle = ctx.echelle if pays == "FR" else 1.0
        offre = int(PAYS_VOLUMES[pays][0] * echelle)
        proj = projection_sortie(n, parse(t_analyse))
        inst = creer_instance(c, "P1", "analyse", "Analyse du tableau de bord — %s" % pays, t_analyse,
                              "dir_marketing", declencheur="Précommandes en attente d'analyse")
        cur = c.execute("INSERT INTO analyses(instance_id, pays, horodatage, precommandes, projection, offre, ratio, "
                        "nb_precommandes_analysees, decision, action, details) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                        (inst, pays, t_analyse, n, proj, offre, round(proj / max(1, offre), 2), n, decision,
                         action, details))
        aid = cur.lastrowid
        c.execute("UPDATE instances SET objet_id=? WHERE id=?", (aid, inst))
        enregistrer(c, inst, "T10", t_analyse, "dir_marketing", details="%d précommandes analysées" % n)
        emettre(c, "FM-17", "Tableau de bord des précommandes — %s : %d précommandes, projection %d / offre %d"
                % (pays, n, proj, offre), fmt(parse(t_analyse) - timedelta(minutes=15)), processus="P1", noeud="T10",
                instance_id=inst)
        if t_dec:
            enregistrer(c, inst, "G03", t_dec, "dir_marketing", issue=decision)
        if pays == "FR":
            c.execute("UPDATE precommandes SET analyse_id=? WHERE pays='FR' AND analyse_id IS NULL AND cree_le <= ? "
                      "AND statut != 'abandonnee'", (aid, t_analyse))
        if decision == "oui" and t_dec:
            emettre(c, "FI-04", "Demande supérieure à l'offre (%s) : augmenter la production ou répartir les stocks"
                    % pays, t_dec, processus="P1", noeud="G03", instance_id=inst)
            if t_action:
                enregistrer(c, inst, "T11", t_action, "production", details=action)
                emettre(c, "FI-05", "Volumes disponibles mis à jour : %s" % action, t_action, processus="P1",
                        noeud="T11", instance_id=inst)
                emettre(c, "FE-04A", "Commande complémentaire d'écrans pliables à Samsung Display", t_action,
                        processus="P1", noeud="T11", instance_id=inst)
        elif decision == "non" and t_dec and t_action:
            enregistrer(c, inst, "T12", t_action, "dir_marketing", details=action)
            emettre(c, "FE-07A", "Brief de relance : %s" % action, t_action, processus="P1", noeud="T12",
                    instance_id=inst)
        return aid, inst

    analyse("FR", "2026-10-17T09:30:00", "2026-10-17T09:45:00", "oui", "2026-10-17T11:00:00",
            "Transfert de 3 000 unités depuis l'Allemagne + 2 000 unités / semaine pendant 4 semaines",
            "Demande projetée nettement supérieure au stock de lancement ; délais > 2 semaines sur Titane noir.")
    analyse("DE", "2026-10-17T10:00:00", "2026-10-17T10:10:00", "non", "2026-10-17T14:00:00",
            "Campagne de relance « Passez au pliable » + bonus de reprise de 100 €",
            "Demande inférieure à l'offre : relancer la communication (processus P2).")
    aid, inst = analyse("UK", "2026-10-19T09:15:00", "2026-10-19T09:25:00", "oui", None,
                        "En attente de la production", "Projection 1,13 x l'offre : la production doit arbitrer.")
    ctx.analyse_uk = (aid, inst)


def _campagne_relance(ctx: Ctx) -> None:
    """P2 — campagne de relance Allemagne déclenchée par P1-T12, en attente de validation budgétaire."""
    c = ctx.conn
    t0 = "2026-10-17T14:05:00"
    inst = creer_instance(c, "P2", "campagne", "Campagne de relance « Passez au pliable » — Allemagne", t0,
                          "dir_marketing", declencheur="P1-T12 : relance de la communication (analyse DE du 17/10)")
    objectifs = {"vues_tiktok": 6000000, "sentiment": 60, "mentions": 90000, "precommandes": 6000, "intention": 7}
    cur = c.execute("INSERT INTO campagnes(instance_id, nom, pays, declencheur, objectifs, budget_propose, statut, "
                    "version_budget, cree_le) VALUES (?,?,?,?,?,?,?,?,?)",
                    (inst, "Relance « Passez au pliable » — Allemagne", "DE", "P1-T12 (analyse du 17/10)",
                     json.dumps(objectifs), 420000, "en_cours", 1, t0))
    camp = cur.lastrowid
    c.execute("UPDATE instances SET objet_id=? WHERE id=?", (camp, inst))
    for canal, m in [("TikTok Ads", 180000), ("Influence (Allemagne)", 120000), ("Bonus de reprise (+100 €)", 90000),
                     ("Production de contenus", 30000)]:
        c.execute("INSERT INTO budget_lignes(campagne_id, version, canal, montant) VALUES (?,?,?,?)", (camp, 1, canal, m))
    enregistrer(c, inst, "T01", "2026-10-17T16:20:00", "dir_marketing", details="Budget proposé : 420 000 €")
    emettre(c, "FI-06", "Proposition de budget — relance Allemagne : 420 000 €", "2026-10-17T16:20:00",
            processus="P2", noeud="T01", instance_id=inst)
    emettre(c, "FM-01", "Demande de budget — relance « Passez au pliable » (DE)", "2026-10-17T16:21:00",
            processus="P2", noeud="T01", instance_id=inst)


def _depenses_et_cac(ctx: Ctx, camp1: int) -> None:
    """Dépenses marketing cumulées (France), coût par précommande et coût d'acquisition (P2-T10)."""
    c = ctx.conn
    jalons = [("2026-09-10", 0), ("2026-09-11", 180000), ("2026-09-28", 640000), ("2026-10-05", 1050000),
              ("2026-10-12", 1520000), ("2026-10-15", 1780000), ("2026-10-17", 1912400)]
    for d in _jours(KEYNOTE, FIN_DONNEES):
        ds = d.strftime("%Y-%m-%d")
        val = jalons[-1][1]
        for (j0, v0), (j1, v1) in zip(jalons, jalons[1:]):
            if j0 <= ds <= j1:
                a, b = parse(j0 + "T00:00:00"), parse(j1 + "T00:00:00")
                val = v0 + (v1 - v0) * ((d - a).days / max(1, (b - a).days))
                break
        if ds < jalons[0][0]:
            val = 0
        ctx.kpi_jour(d, "depense_marketing", round(val))
    # coût par précommande (T05) : dépenses à date / précommandes à date
    rows = c.execute("SELECT id, cree_le FROM precommandes WHERE statut='confirmee' ORDER BY cree_le").fetchall()
    maj, n = [], 0
    for row in rows:
        n += 1
        jour = row["cree_le"][:10]
        dep = ctx.kpi.get((jour, "FR", "depense_marketing"), 1912400) * ctx.echelle
        maj.append((round(dep / n, 2), row["id"]))
    c.executemany("UPDATE precommandes SET cout_par_precommande=? WHERE id=?", maj)
    # P2-T09 et P2-T10 de la campagne de lancement
    inst = ctx.camp1_inst
    enregistrer(c, inst, "T09", "2026-10-16T11:30:00", "production",
                details="Mix coloris ajusté : +1 200 Titane noir sur le lot du 30/10")
    emettre(c, "FI-05", "Plan ajusté : +1 200 Titane noir sur le lot du 30/10", "2026-10-16T11:30:00",
            processus="P2", noeud="T09", instance_id=inst)
    emettre(c, "FM-04", "Volumes disponibles par coloris mis à jour", "2026-10-16T11:31:00", processus="P2",
            noeud="T09", instance_id=inst)
    n17 = _compter_fr(c, "2026-10-17T10:00:00")
    cac = round(1912400 * ctx.echelle / max(1, n17), 2)
    enregistrer(c, inst, "T10", "2026-10-17T10:00:00", "finance",
                details="Coût d'acquisition : %s par précommande (%d précommandes)" % (euros(cac, 2), n17))
    c.execute("UPDATE campagnes SET budget_depense=?, cout_acquisition=?, precommandes_attribuees=?, statut='terminee' "
              "WHERE id=?", (1912400, cac, n17, camp1))
    emettre(c, "FI-12", "Coût d'acquisition par précommande : %s" % euros(cac, 2), "2026-10-17T10:00:00",
            processus="P2", noeud="T10", instance_id=inst, notifier=False)


# =============================================================================
def _precommandes_en_attente(ctx: Ctx) -> None:
    """Quelques précommandes en cours au 19/10 10:00 : files d'attente de la finance, de l'organisme
    financier et de la production (instances BPMN réelles)."""
    from .services import precommandes as svc
    c, r = ctx.conn, ctx.rng
    scenarios = [
        # (minutes avant 10:00, paiement, étape cible)
        (38, "cb", "controle"), (31, "apple_pay", "controle"), (24, "cetelem_24m", "credit"),
        (19, "cetelem_10x", "credit"), (15, "cb", "controle"), (12, "cb", "stock"), (9, "apple_pay", "stock"),
        (7, "cetelem_10x", "stock"), (5, "cb", "stock"), (3, "apple_pay", "stock"),
    ]
    ids = [row[0] for row in c.execute("SELECT id FROM clients WHERE me_prevenir_le IS NOT NULL ORDER BY id DESC LIMIT 400")]
    for k, (minutes, pay, etape) in enumerate(scenarios):
        t = fmt(T_DEFAUT - timedelta(minutes=minutes))
        cl = c.execute("SELECT * FROM clients WHERE id=?", (ids[k * 7],)).fetchone()
        cap = ["512", "256", "1T", "512", "2T", "512", "256", "1T", "512", "256"][k]
        col = ["noir", "naturel", "bleu", "noir", "blanc", "noir", "bleu", "naturel", "noir", "blanc"][k]
        svc.creer_precommande(c, t, client_id=cl["id"], capacite=cap, coloris=col, applecare=(k % 3 == 0),
                              reprise_modele=cl["appareil"] if k % 2 == 0 else None, reprise_etat="bon",
                              paiement_mode=pay, livraison_mode="domicile" if k % 4 else "retrait",
                              magasin=None if k % 4 else "Apple Part-Dieu", canal="apple.com", mode="pas_a_pas",
                              controle_renforce=(etape == "controle"), seed=True,
                              montant_credit_force=4100 if etape == "credit" else None)
        if etape == "stock":
            pid = c.execute("SELECT id FROM precommandes ORDER BY id DESC LIMIT 1").fetchone()[0]
            dc = c.execute("SELECT id FROM demandes_credit WHERE precommande_id=? AND statut='etude'", (pid,)).fetchone()
            if dc:
                svc.decision_credit(c, dc[0], "accorde", fmt(parse(t) + timedelta(seconds=40)))
            svc.decision_paiement(c, pid, "oui", fmt(parse(t) + timedelta(minutes=1)), acteur="finance",
                                  commentaire="Paiement autorisé")


# =============================================================================
def _partenaires(ctx: Ctx) -> None:
    c, r = ctx.conn, ctx.rng
    # Opérateurs : activations eSIM (à partir de la sortie)
    parts = {"Orange": .38, "SFR": .22, "Bouygues Telecom": .20, "Free": .20}
    for d in _jours(parse("2026-10-23T00:00:00"), FIN_DONNEES):
        total = 21000 if d.strftime("%m-%d") == "10-23" else (9000 if d.strftime("%m-%d") == "10-24" else
                                                               int(1500 + r.random() * 600))
        for op, p in parts.items():
            act = int(total * p * (0.9 + 0.2 * r.random()))
            ventes = int(act * (0.08 + 0.04 * r.random()))
            c.execute("INSERT INTO operateurs_activations VALUES (?,?,?,?,?)",
                      (d.strftime("%Y-%m-%d"), op, act, ventes, int(ventes * 0.62)))
    # Revendeurs : PLV, stocks puis ventes
    for ens, stock in (("Fnac", 1800), ("Darty", 1200), ("Boulanger", 900)):
        c.execute("INSERT INTO revendeurs_flux(enseigne, type, quantite, horodatage, commentaire) VALUES (?,?,?,?,?)",
                  (ens, "plv", 1, "2026-10-14T09:00:00", "Kit PLV iPhone Duo (présentoir, visuels)"))
        c.execute("INSERT INTO revendeurs_flux(enseigne, type, quantite, horodatage, commentaire) VALUES (?,?,?,?,?)",
                  (ens, "stock", stock, "2026-10-21T07:00:00", "Allocation de lancement revendeurs"))
        for d in _jours(parse("2026-10-23T00:00:00"), FIN_DONNEES):
            c.execute("INSERT INTO revendeurs_flux(enseigne, type, quantite, horodatage) VALUES (?,?,?,?)",
                      (ens, "ventes", int(stock * (0.12 if d.day == 23 else 0.03) * (0.8 + 0.4 * r.random())),
                       fmt(d + timedelta(hours=21))))
    # Développeurs : apps adaptées au double écran
    for k, (nom, ed, cat) in enumerate(APPS):
        t = KEYNOTE + timedelta(days=2 + k * 1.6, hours=r.randint(8, 20))
        c.execute("INSERT INTO apps_adaptees(nom, editeur, categorie, soumise_le, statut) VALUES (?,?,?,?,?)",
                  (nom, ed, cat, fmt(t), "publiée" if t < T_DEFAUT - timedelta(days=2) else "en revue"))
    # Instituts d'études (FE-08)
    etudes = [
        ("Counterpoint", "Intention d'achat iPhone Duo — vague 1", "intention", "2026-09-08T10:00:00",
         "2026-09-14T09:00:00", "livree", {"intention": 4.1}),
        ("Counterpoint", "Intention d'achat iPhone Duo — vague 3", "intention", "2026-09-22T10:00:00",
         "2026-09-28T09:00:00", "livree", {"intention": 5.2}),
        ("Counterpoint", "Intention d'achat iPhone Duo — vague 5", "intention", "2026-10-06T10:00:00",
         "2026-10-12T08:30:00", "livree", {"intention": 6.0, "frein_principal": "prix (62 %)"}),
        ("Institut de sondage", "Perception du prix et leviers (reprise, 10x)", "qualitative", "2026-10-07T10:00:00",
         "2026-10-11T18:00:00", "livree", {"reprise_levier": 48, "paiement_10x_levier": 37}),
        ("IDC", "Marché français des smartphones pliables — T3 2026", "parts_de_marche", "2026-09-15T10:00:00",
         "2026-10-20T10:00:00", "livree", {"Samsung": 61, "Google": 14, "Huawei": 11, "Honor": 9, "Autres": 5}),
        ("Counterpoint", "Intention d'achat iPhone Duo — vague 7", "intention", "2026-10-19T09:00:00",
         None, "commandee", None),
        ("IDC", "Parts de marché des pliables — octobre 2026", "parts_de_marche", "2026-10-26T10:00:00",
         "2026-11-02T10:00:00", "livree", {"Apple": 41, "Samsung": 38, "Google": 9, "Huawei": 5, "Honor": 4, "Autres": 3}),
    ]
    for inst, titre, typ, cmd, liv, st, res in etudes:
        c.execute("INSERT INTO etudes(institut, titre, type, commandee_le, livree_le, statut, resultat) VALUES (?,?,?,?,?,?,?)",
                  (inst, titre, typ, cmd, liv, st, json.dumps(res) if res else None))
    # Réglementation (FE-11)
    regl = [
        ("CNIL", "regle", "Recommandation « cookies et autres traceurs » (rappel)",
         "Consentement préalable obligatoire pour les traceurs publicitaires ; refus aussi simple que l'acceptation.",
         "2026-09-01T09:00:00", "applicable"),
        ("Commission européenne", "regle", "DMA — ouverture de l'App Store aux boutiques alternatives",
         "Obligations d'interopérabilité et de choix pour les utilisateurs européens.", "2026-07-15T09:00:00", "applicable"),
        ("CNIL", "declaration", "Registre des traitements : campagne iPhone Duo (ciblage publicitaire)",
         "Base légale : consentement. Durée de conservation : 13 mois. Données : Apple ID, appareil, inscriptions.",
         "2026-09-14T11:00:00", "transmise"),
        ("CNIL", "declaration", "Analyse d'impact (AIPD) : écoute des réseaux sociaux",
         "Données publiques agrégées, pseudonymisation, aucune donnée sensible.", "2026-09-10T15:00:00", "transmise"),
        ("Commission européenne", "declaration", "Rapport de conformité DMA — interopérabilité iOS 27",
         "Fonctions retardées dans l'UE (Siri IA) documentées.", "2026-10-01T10:00:00", "transmise"),
    ]
    for aut, sens, titre, contenu, t, st in regl:
        c.execute("INSERT INTO reglementation(autorite, sens, titre, contenu, horodatage, statut) VALUES (?,?,?,?,?,?)",
                  (aut, sens, titre, contenu, t, st))
    # Veille concurrentielle (FE-12, indirect)
    for conc, prod, prix in CONCURRENTS:
        for t, delta in (("2026-09-09T22:00:00", 0), ("2026-10-16T16:00:00", -200 if conc == "Samsung" else 0),
                         ("2026-10-26T10:00:00", -200 if conc in ("Samsung", "Google") else 0)):
            c.execute("INSERT INTO veille(concurrent, produit, prix, releve_le, source, commentaire) VALUES (?,?,?,?,?,?)",
                      (conc, prod, prix + delta, t, "Relevé site officiel",
                       "Remise de lancement en réponse à l'iPhone Duo" if delta else None))
    # Agences (FE-07)
    briefs = [
        ("Agence de création (fictive)", "Vidéos TikTok de lancement", 330000, "livre", "2026-09-03T10:00:00",
         "2026-09-10T22:00:00", "12 vidéos produites"),
        ("Agence d'achat média (fictive)", "Achat média TikTok Ads — lancement France", 950000, "livre",
         "2026-09-11T18:30:00", "2026-10-15T18:00:00", "36,4 M de vues, CPM moyen 6,10 €"),
        ("Agence de création (fictive)", "Relance : reprise et paiement en 10 fois", 60000, "livre",
         "2026-10-12T14:00:00", "2026-10-13T11:00:00", "2 vidéos livrées"),
        ("Agence d'achat média (fictive)", "Relance « Passez au pliable » — Allemagne", 180000, "en_attente_budget",
         "2026-10-17T14:00:00", None, None),
    ]
    for ag, titre, budget, st, env, liv, rap in briefs:
        c.execute("INSERT INTO briefs_agence(agence, titre, budget, statut, envoye_le, livre_le, rapport) "
                  "VALUES (?,?,?,?,?,?,?)", (ag, titre, budget, st, env, liv, rap))
    # Juridique
    vals = [
        ("Vidéos TikTok de lancement (5)", "message publicitaire", "mkt_social", "validee", "2026-09-10T11:00:00",
         "2026-09-10T17:00:00", "Mentions conformes ; pas d'allégation de solidité chiffrée."),
        ("Contrats influenceurs (12)", "contrat", "mkt_social", "validee", "2026-09-13T10:00:00",
         "2026-09-14T09:00:00", "Mention « collaboration commerciale » obligatoire."),
        ("Bandeau « paiement en 10 fois sans frais »", "mention légale", "mkt_ecommerce", "validee",
         "2026-10-12T15:00:00", "2026-10-12T18:00:00",
         "Ajout de la mention : « Un crédit vous engage et doit être remboursé »."),
        ("Messages de relance Allemagne (bonus reprise)", "message publicitaire", "dir_marketing", "en_attente",
         "2026-10-17T16:30:00", None, None),
    ]
    for obj, typ, dem, st, cree, dec, com in vals:
        c.execute("INSERT INTO validations_juridiques(objet, type, demandeur, statut, cree_le, decide_le, commentaire) "
                  "VALUES (?,?,?,?,?,?,?)", (obj, typ, dem, st, cree, dec, com))
    # Presse (FM-12)
    for t, media, titre, ton, aud in PRESSE:
        c.execute("INSERT INTO retombees_presse(media, titre, tonalite, audience, publie_le) VALUES (?,?,?,?,?)",
                  (media, titre, ton, aud, t))
    # Création : page produit et PLV
    for typ, titre, dest, brief, livre in (
            ("Page produit", "Page iPhone Duo (apple.com/fr)", "mkt_ecommerce", "2026-08-25T10:00:00", "2026-09-09T19:30:00"),
            ("Visuels", "Kit PLV Apple Store et revendeurs", "mkt_retail", "2026-09-20T10:00:00", "2026-10-10T17:00:00"),
            ("Page produit", "Bandeau reprise + paiement en 10 fois", "mkt_ecommerce", "2026-10-12T14:00:00",
             "2026-10-13T09:00:00"),
            ("Vidéo TikTok", "Relance Allemagne « Passez au pliable »", "mkt_social", "2026-10-17T14:00:00", None)):
        c.execute("INSERT INTO contenus_creation(type, titre, statut, destinataire, brief_le, livre_le) VALUES (?,?,?,?,?,?)",
                  (typ, titre, "livré" if livre else "en_production", dest, brief, livre))
    # Rendez-vous de démonstration (échantillon détaillé pour l'écran Apple Store)
    clients = [row[0] for row in c.execute("SELECT id FROM clients ORDER BY RANDOM() LIMIT 600")]
    for k in range(min(600, len(clients))):
        jour = parse("2026-10-14T00:00:00") + timedelta(days=k % 9)
        creneau = jour + timedelta(hours=10 + (k * 7) % 10, minutes=15 * (k % 4))
        statut = "réalisé" if creneau < T_DEFAUT else "planifié"
        note = r.choice([3, 4, 4, 5, 5, 5]) if statut == "réalisé" else None
        intention = r.choices(["achat probable", "hésitant (prix)", "achat certain", "non"], [35, 30, 25, 10])[0] \
            if statut == "réalisé" else None
        c.execute("INSERT INTO rdv_demo(magasin, creneau, client_id, statut, note_essai, intention, cree_le) "
                  "VALUES (?,?,?,?,?,?,?)", (APPLE_STORES_FR[k % len(APPLE_STORES_FR)], fmt(creneau), clients[k],
                                             statut, note, intention, fmt(creneau - timedelta(days=3))))
    # Service client (AppleCare)
    for k in range(260):
        sujet, periode = SUJETS_SAV[k % len(SUJETS_SAV)]
        base = parse("2026-10-16T15:00:00") if periode == "avant" else parse("2026-10-23T09:00:00")
        t = base + timedelta(minutes=r.randint(0, 60 * 24 * (6 if periode == "avant" else 12)))
        statut = "résolu" if t < T_DEFAUT - timedelta(hours=6) else "en cours"
        c.execute("INSERT INTO demandes_sav(sujet, canal, statut, satisfaction, escalade, cree_le) VALUES (?,?,?,?,?,?)",
                  (sujet, r.choice(["Chat", "Téléphone", "Apple Store", "App Assistance"]), statut,
                   r.choice([4, 5, 5, 5, 3]) if statut == "résolu" else None,
                   "Ingénierie produit" if "Pliure" in sujet and r.random() < 0.3 else None, fmt(t)))


# =============================================================================
def _flux_historiques(ctx: Ctx) -> None:
    """Journal des flux : lots horaires (volumes) pour les échanges répétitifs + messages individuels."""
    c = ctx.conn

    def lot(code, objet, t, volume, **kw):
        if volume > 0:
            emettre(c, code, objet, fmt(t), volume=volume, notifier=False, **kw)

    # Avant le lancement : inscriptions, trafic, essais, mentions (quotidien)
    for d in _jours(KEYNOTE, FIN_DONNEES):
        ds = d.strftime("%Y-%m-%d")
        fin = d + timedelta(hours=23, minutes=55)
        me = int(ctx.kpi.get((ds, "FR", "me_prevenir"), 0))
        lot("FE-01R", "Inscriptions « Me prévenir » du jour : %s" % me, fin, me)
        v = int(ctx.kpi.get((ds, "FR", "visites"), 0))
        lot("FM-13", "Trafic du jour sur la page iPhone Duo : %s visites" % v, fin, max(1, v // 1000),
            emetteur="mkt_ecommerce", recepteur="mkt_data")
        rdv = int(ctx.kpi.get((ds, "FR", "rdv_demo"), 0))
        lot("FM-16", "Rendez-vous et essais en magasin du jour : %s" % rdv, fin, rdv)
        men = int(ctx.kpi.get((ds, "FR", "mentions"), 0))
        lot("FM-14", "Mentions et engagement du jour : %s mentions" % men, fin, max(1, men // 100))
        lot("FE-12R", "Veille quotidienne des prix concurrents", d + timedelta(hours=7), 5)
        lot("FE-01A", "Publicités et offres diffusées (impressions, en milliers)", fin,
            max(1, int(ctx.kpi.get((ds, "FR", "visites"), 0) * 3 // 1000)))
    # Hebdomadaire : tableau de bord FM-17, commandes fournisseurs, capacités
    for k in range(9):
        lundi = parse("2026-09-14T09:00:00") + timedelta(days=7 * k)
        emettre(c, "FM-17", "Tableau de bord hebdomadaire du lundi %s" % lundi.strftime("%d/%m"), fmt(lundi),
                emetteur="mkt_data", recepteur="dir_marketing", notifier=lundi > T_DEFAUT - timedelta(days=8))
        emettre(c, "FE-04A", "Commande hebdomadaire de 250 000 écrans pliables", fmt(lundi - timedelta(days=7)),
                notifier=False)
        emettre(c, "FE-04R", "Capacité confirmée : 280 000 écrans / semaine, livraison en cours",
                fmt(lundi - timedelta(days=6)), notifier=lundi > T_DEFAUT - timedelta(days=8))
    # Précommandes France : lots horaires
    rows = c.execute(
        """SELECT substr(cree_le,1,13) AS h, COUNT(*) AS n,
                  SUM(CASE WHEN paiement_mode LIKE 'cetelem%' THEN 1 ELSE 0 END) AS cred,
                  SUM(CASE WHEN reprise_modele IS NOT NULL THEN 1 ELSE 0 END) AS rep,
                  SUM(CASE WHEN statut='confirmee' THEN 1 ELSE 0 END) AS ok,
                  SUM(COALESCE(ca_previsionnel_ht,0)) AS ca
           FROM precommandes WHERE demo=0 GROUP BY h ORDER BY h""").fetchall()
    for row in rows:
        t = parse(row["h"] + ":59:00")
        lot("FE-01R", "Précommandes reçues sur apple.com et l'app (%s h)" % row["h"][11:13], t, row["n"],
            processus="P1", noeud="T03")
        lot("FE-09A", "Demandes de crédit transmises à Cetelem", t, row["cred"], processus="P1", noeud="T03")
        lot("FE-09R", "Accords de crédit et autorisations de paiement", t, row["cred"], processus="P1", noeud="G01")
        lot("FE-10A", "Demandes d'estimation de reprise", t, row["rep"], processus="P1", noeud="T01")
        lot("FE-10R", "Valeurs de reprise retournées", t, row["rep"], processus="P1", noeud="T01")
        lot("FI-12", "CA prévisionnel enregistré : %s HT" % euros(row["ca"]), t, row["ok"], processus="P1", noeud="T04")
        lot("FI-10", "Précommandes enregistrées dans le CRM", t, row["ok"], processus="P1", noeud="T06")
        lot("FI-11", "Réservations d'appareils (stocks ERP)", t, row["ok"], processus="P1", noeud="T08")
        lot("FE-01A", "Confirmations de précommande envoyées", t, row["ok"], processus="P1", noeud="T09")
        lot("FI-05", "Délais de livraison recalculés et affichés", t, row["ok"], processus="P1", noeud="T02")
    for d in _jours(parse("2026-10-17T00:00:00"), FIN_DONNEES):
        t = d + timedelta(hours=8)
        n = c.execute("SELECT COUNT(*) FROM precommandes WHERE cree_le < ? AND statut='confirmee'", (fmt(d),)).fetchone()[0]
        emettre(c, "FM-19", "Précommandes par pays (cumul : %d en France)" % n, fmt(t), emetteur="mkt_data",
                recepteur="production", notifier=(d >= T_DEFAUT - timedelta(days=1)))
        emettre(c, "FM-18", "Coût par précommande mis à jour", fmt(t + timedelta(minutes=5)), emetteur="mkt_data",
                recepteur="finance", notifier=(d >= T_DEFAUT - timedelta(days=1)))
    # Après la sortie : opérateurs et revendeurs
    for row in c.execute("SELECT jour, SUM(activations_esim) a, SUM(ventes) v FROM operateurs_activations GROUP BY jour"):
        t = parse(row["jour"] + "T22:00:00")
        lot("FE-02R", "Ventes et forfaits remontés par les opérateurs", t, row["v"])
        lot("FE-02A", "Activations eSIM traitées", t, max(1, row["a"] // 10))
    for row in c.execute("SELECT * FROM revendeurs_flux"):
        t = parse(row["horodatage"])
        if row["type"] == "ventes":
            lot("FE-03R", "Ventes %s : %d iPhone Duo" % (row["enseigne"], row["quantite"]), t, row["quantite"])
        else:
            emettre(c, "FE-03A", "%s envoyé à %s (%s)" % ("Stock" if row["type"] == "stock" else "Kit PLV",
                                                          row["enseigne"], row["quantite"]), fmt(t), notifier=False)
    for row in c.execute("SELECT * FROM apps_adaptees"):
        emettre(c, "FE-05R", "App adaptée au pliable : %s (%s)" % (row["nom"], row["editeur"]), row["soumise_le"],
                notifier=False)
    emettre(c, "FE-05A", "Kit de développement iOS 27 : API double écran et simulateur pliable",
            "2026-09-09T20:30:00", notifier=False)
    for row in c.execute("SELECT * FROM etudes"):
        emettre(c, "FE-08A", "Commande d'étude : %s" % row["titre"], row["commandee_le"], notifier=False)
        if row["livree_le"]:
            emettre(c, "FE-08R", "Étude livrée : %s" % row["titre"], row["livree_le"],
                    notifier=parse(row["livree_le"]) > T_DEFAUT - timedelta(days=10))
    for row in c.execute("SELECT * FROM reglementation"):
        code = "FE-11A" if row["sens"] == "declaration" else "FE-11R"
        emettre(c, code, row["titre"], row["horodatage"], notifier=False)
    for row in c.execute("SELECT * FROM retombees_presse"):
        emettre(c, "FM-12", "Retombée presse : %s — %s" % (row["media"], row["titre"]), row["publie_le"],
                notifier=False)
    for row in c.execute("SELECT * FROM briefs_agence"):
        emettre(c, "FE-07A", "Brief : %s (%s)" % (row["titre"], euros(row["budget"])), row["envoye_le"], notifier=False)
        if row["livre_le"]:
            emettre(c, "FE-07R", "Livraison / rapport : %s" % row["titre"], row["livre_le"], notifier=False)
    emettre(c, "FI-01", "Plan de lancement vague 1 validé", "2026-09-04T11:00:00")
    emettre(c, "FI-02", "Plan de lancement vague 1 soumis à la direction générale", "2026-09-02T18:30:00")
    emettre(c, "FI-02", "Plan de lancement vague 2 (Inde) soumis pour validation", "2026-10-19T08:30:00")
    emettre(c, "FI-03", "Objectif de marge brute iPhone Duo : 48 %", "2026-08-28T18:00:00")
    emettre(c, "FI-07", "Prix validés : 2 339 € (256 Go) à 3 839 € (2 To)", "2026-09-03T17:00:00")
    emettre(c, "FI-08", "Coût de revient actualisé : mémoire DRAM +87 %, NAND +70 %", "2026-10-08T10:00:00")
    emettre(c, "FI-09", "Budget de production vague 1 : 1 003 M€", "2026-09-05T10:00:00")
    emettre(c, "FM-06", "Ouverture des précommandes : vendredi 16 octobre à 14 h", "2026-09-09T20:00:00")
    emettre(c, "FM-09", "Plan de démonstrations en Apple Store à partir du 18/09", "2026-09-12T10:00:00")
    emettre(c, "FM-11", "Page produit iPhone Duo livrée", "2026-09-09T19:30:00", emetteur="mkt_creation",
            recepteur="mkt_ecommerce", notifier=False)
    emettre(c, "FM-11", "Bandeau reprise + paiement en 10 fois livré", "2026-10-13T09:00:00",
            emetteur="mkt_creation", recepteur="mkt_ecommerce")
    emettre(c, "FE-06A", "Invitations presse à la keynote « Surprise and Shine »", "2026-09-01T10:00:00",
            emetteur="mkt_presse", notifier=False)


def _kpi_flush(ctx: Ctx) -> None:
    ctx.conn.executemany("INSERT OR REPLACE INTO kpi_journalier(jour, pays, indicateur, valeur) VALUES (?,?,?,?)",
                         [(j, p, i, v) for (j, p, i), v in ctx.kpi.items()])
    # vues TikTok quotidiennes (cohérentes avec la courbe de chaque vidéo)
    rows = []
    for d in _jours(KEYNOTE, FIN_DONNEES):
        v = round(_vues_tiktok_a(ctx, d + timedelta(days=1))) - round(_vues_tiktok_a(ctx, d))
        rows.append((d.strftime("%Y-%m-%d"), "FR", "vues_tiktok", v))
    ctx.conn.executemany("INSERT OR REPLACE INTO kpi_journalier VALUES (?,?,?,?)", rows)


def _finaliser_notifications(ctx: Ctx) -> None:
    """Notifications antérieures au 18/10 considérées comme lues ; les plus récentes restent à traiter."""
    ctx.conn.execute("UPDATE notifications SET lu = 1 WHERE horodatage < '2026-10-18T00:00:00'")
