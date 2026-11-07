"""Indicateurs de performance (§ 3.6 et § 6.3 du dossier) calculés à l'heure simulée."""
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from ..db import lire_parametre
from ..horloge import fmt, parse, phase
from ..metier import (CAPACITES, COLORIS, OUVERTURE, SORTIE, chiffrer, cout_revient, euros, ht,
                      prix_catalogue)
from ..referentiel import OBJECTIFS_HEBDO, PAYS_LIBELLE
from . import pilotage

KEYNOTE = parse("2026-09-09T00:00:00")


def _echelle(conn) -> float:
    return float(lire_parametre(conn, "echelle", "1") or 1)


def _fraction_jour(t: datetime) -> float:
    return (t.hour * 3600 + t.minute * 60 + t.second) / 86400.0


def cumul(conn, indicateur: str, t: str, pays: str = "FR", depuis: Optional[str] = None) -> float:
    """Somme des valeurs quotidiennes jusqu'à t (journée en cours au prorata)."""
    tt = parse(t)
    jour = t[:10]
    args = [pays, indicateur, jour]
    sql = "SELECT COALESCE(SUM(valeur),0) FROM kpi_journalier WHERE pays=? AND indicateur=? AND jour < ?"
    if depuis:
        sql += " AND jour >= ?"
        args.append(depuis)
    total = conn.execute(sql, args).fetchone()[0]
    row = conn.execute("SELECT valeur FROM kpi_journalier WHERE pays=? AND indicateur=? AND jour=?",
                       (pays, indicateur, jour)).fetchone()
    if row:
        total += row[0] * _fraction_jour(tt)
    return total


def serie(conn, indicateur: str, t: str, debut: str = "2026-09-09", pays: str = "FR") -> List[dict]:
    tt = parse(t)
    rows = conn.execute("SELECT jour, valeur FROM kpi_journalier WHERE pays=? AND indicateur=? AND jour >= ? "
                        "AND jour <= ? ORDER BY jour", (pays, indicateur, debut, t[:10])).fetchall()
    out = []
    for r in rows:
        v = r["valeur"]
        if r["jour"] == t[:10]:
            v = v * _fraction_jour(tt)
        out.append({"x": r["jour"], "y": round(v)})
    return out


def hebdo(conn, indicateur: str, t: str, pays: str = "FR") -> Optional[float]:
    row = conn.execute("SELECT valeur FROM kpi_hebdo WHERE pays=? AND indicateur=? AND semaine <= ? "
                       "ORDER BY semaine DESC LIMIT 1", (pays, indicateur, t[:10])).fetchone()
    return row[0] if row else None


def serie_hebdo(conn, indicateur: str, t: str, pays: str = "FR") -> List[dict]:
    return [{"x": r["semaine"], "y": r["valeur"]} for r in conn.execute(
        "SELECT semaine, valeur FROM kpi_hebdo WHERE pays=? AND indicateur=? AND semaine <= ? ORDER BY semaine",
        (pays, indicateur, t[:10]))]


def vues_tiktok(conn, t: str) -> float:
    return cumul(conn, "vues_tiktok", t)


# --------------------------------------------------------------------------- § 6.3
def tableau_hebdomadaire(conn, t: str) -> dict:
    """Tableau de bord CRM du lundi (données arrêtées au dimanche 23:59)."""
    tt = parse(t)
    lundi = (tt - timedelta(days=tt.weekday())).replace(hour=0, minute=0, second=0)
    if lundi < parse("2026-09-14T00:00:00"):
        return {"disponible": False, "lundi": "2026-09-14", "lignes": []}
    lun = fmt(lundi)
    valeurs = {
        "visites": cumul(conn, "visites", lun),
        "me_prevenir": cumul(conn, "me_prevenir", lun),
        "rdv_demo": cumul(conn, "rdv_demo", lun),
        "vues_tiktok": cumul(conn, "vues_tiktok", lun),
        "sentiment": hebdo(conn, "sentiment", lun),
        "intention": hebdo(conn, "intention", lun),
        "android": hebdo(conn, "android", lun),
    }
    lignes = []
    for code, libelle, objectif, unite, _sens in OBJECTIFS_HEBDO:
        v = valeurs.get(code)
        atteint = v is not None and v >= objectif
        lignes.append({"code": code, "libelle": libelle, "objectif": objectif, "resultat": v, "unite": unite,
                       "evaluation": "Atteint" if atteint else "En retard", "atteint": atteint})
    return {"disponible": True, "lundi": lundi.strftime("%Y-%m-%d"), "lignes": lignes,
            "atteints": sum(1 for l in lignes if l["atteint"]), "total": len(lignes)}


# --------------------------------------------------------------------------- cockpit marketing
def _precommandes_stats(conn, t: str) -> dict:
    ech = _echelle(conn)
    base = "FROM precommandes WHERE pays='FR' AND statut != 'abandonnee' AND cree_le <= ? AND cree_le < ?"
    args = (t, fmt(SORTIE))
    n = conn.execute("SELECT COUNT(*) " + base, args).fetchone()[0]
    def group(col):
        return {r[0]: r[1] for r in conn.execute("SELECT %s, COUNT(*) %s GROUP BY 1" % (col, base), args)}
    par_cap = group("capacite")
    par_col = group("coloris")
    par_canal = group("canal")
    par_pay = group("paiement_mode")
    android = conn.execute("SELECT COUNT(*) FROM precommandes p JOIN clients c ON c.id=p.client_id WHERE p.pays='FR' "
                           "AND p.statut!='abandonnee' AND p.cree_le <= ? AND p.cree_le < ? AND c.plateforme='Android'",
                           args).fetchone()[0]
    agg = conn.execute("SELECT COALESCE(SUM(ca_previsionnel_ht),0), COALESCE(SUM(marge),0), "
                       "SUM(CASE WHEN reprise_modele IS NOT NULL THEN 1 ELSE 0 END), SUM(applecare), "
                       "SUM(delai_allonge) " + base, args).fetchone()
    par_heure = [{"x": r[0] + ":00", "y": r[1]} for r in conn.execute(
        "SELECT substr(cree_le,1,13), COUNT(*) %s GROUP BY 1 ORDER BY 1" % base, args)]
    par_jour = [{"x": r[0], "y": r[1]} for r in conn.execute(
        "SELECT substr(cree_le,1,10), COUNT(*) %s GROUP BY 1 ORDER BY 1" % base, args)]
    visites = cumul(conn, "visites", t, depuis="2026-10-16") - (
        conn.execute("SELECT valeur FROM kpi_journalier WHERE pays='FR' AND indicateur='visites' AND jour='2026-10-16'"
                     ).fetchone()[0] * 14 / 24.0 if t >= "2026-10-16T14" else 0)
    n_reel = n / ech if ech else n
    return {
        "total": int(round(n_reel)), "total_brut": n, "par_capacite": par_cap, "par_coloris": par_col,
        "par_canal": par_canal, "par_paiement": par_pay, "par_heure": par_heure[-72:], "par_jour": par_jour,
        "part_android": round(100.0 * android / n, 1) if n else 0.0,
        "ca_ht": agg[0] / ech, "marge": agg[1] / ech,
        "part_reprise": round(100.0 * (agg[2] or 0) / n, 1) if n else 0.0,
        "part_applecare": round(100.0 * (agg[3] or 0) / n, 1) if n else 0.0,
        "part_delai_allonge": round(100.0 * (agg[4] or 0) / n, 1) if n else 0.0,
        "conversion": round(100.0 * n_reel / visites, 2) if visites > 0 else None,
    }


def cockpit_marketing(conn, t: str) -> dict:
    tt = parse(t)
    ph = phase(tt)
    obj = {o[0]: o[2] for o in OBJECTIFS_HEBDO}
    avant = {
        "visites": round(cumul(conn, "visites", t)), "me_prevenir": round(cumul(conn, "me_prevenir", t)),
        "rdv_demo": round(cumul(conn, "rdv_demo", t)), "vues_tiktok": round(vues_tiktok(conn, t)),
        "mentions": round(cumul(conn, "mentions", t)),
        "sentiment": hebdo(conn, "sentiment", t), "intention": hebdo(conn, "intention", t),
        "android": hebdo(conn, "android", t), "objectifs": obj,
        "series": {
            "visites": serie(conn, "visites", t), "me_prevenir": serie(conn, "me_prevenir", t),
            "vues_tiktok": serie(conn, "vues_tiktok", t), "mentions": serie(conn, "mentions", t),
            "rdv_demo": serie(conn, "rdv_demo", t),
            "sentiment": serie_hebdo(conn, "sentiment", t), "intention": serie_hebdo(conn, "intention", t),
            "android": serie_hebdo(conn, "android", t),
        },
    }
    pre = _precommandes_stats(conn, t) if tt >= OUVERTURE else None
    apres = None
    if tt >= SORTIE:
        ech = _echelle(conn)
        livrees = conn.execute("SELECT COUNT(*) FROM precommandes WHERE pays='FR' AND statut='confirmee' AND "
                               "livraison_prevue IS NOT NULL AND livraison_prevue <= ? AND cree_le <= ?",
                               (t[:10], t)).fetchone()[0]
        ventes_jour = [{"x": r[0], "y": round(r[1] / ech)} for r in conn.execute(
            "SELECT substr(cree_le,1,10), COUNT(*) FROM precommandes WHERE pays='FR' AND statut='confirmee' AND "
            "cree_le >= ? AND cree_le <= ? GROUP BY 1 ORDER BY 1", (fmt(SORTIE), t))]
        esim = conn.execute("SELECT COALESCE(SUM(activations_esim),0) FROM operateurs_activations WHERE jour <= ?",
                            (t[:10],)).fetchone()[0]
        etude = conn.execute("SELECT resultat FROM etudes WHERE type='parts_de_marche' AND livree_le <= ? "
                             "ORDER BY livree_le DESC LIMIT 1", (t,)).fetchone()
        apres = {"livrees": round(livrees / ech), "ventes_jour": ventes_jour,
                 "satisfaction": hebdo(conn, "satisfaction", t), "retours": hebdo(conn, "retours", t),
                 "applecare": pre["part_applecare"] if pre else None, "activations_esim": esim,
                 "parts_de_marche": json.loads(etude["resultat"]) if etude else None,
                 "part_marche_apple": hebdo(conn, "part_marche_pliables", t)}
    return {"phase": ph, "avant": avant, "precommandes": pre, "apres": apres,
            "hebdo": tableau_hebdomadaire(conn, t)}


# --------------------------------------------------------------------------- finance
def kpi_finance(conn, t: str) -> dict:
    ech = _echelle(conn)
    prix = prix_catalogue(conn)
    lignes_cap = []
    objectif = conn.execute("SELECT taux FROM objectifs_marge WHERE defini_le <= ? ORDER BY defini_le DESC LIMIT 1",
                            (t,)).fetchone()
    objectif = objectif[0] if objectif else None
    for cap, d in CAPACITES.items():
        cr = cout_revient(cap, conn)
        h = ht(prix[cap])
        n = conn.execute("SELECT COUNT(*), COALESCE(SUM(ca_previsionnel_ht),0) FROM precommandes WHERE capacite=? AND "
                         "paye_le IS NOT NULL AND paye_le <= ?", (cap, t)).fetchone()
        lignes_cap.append({"capacite": cap, "libelle": d["libelle"], "prix_ttc": prix[cap], "prix_ht": h,
                           "cout_revient": cr, "marge_unitaire": round(h - cr, 2),
                           "taux_marge": round(100 * (h - cr) / h, 1), "precommandes": round(n[0] / ech),
                           "ca_ht": n[1] / ech, "sous_objectif": objectif is not None and 100 * (h - cr) / h < objectif})
    tot_n = sum(l["precommandes"] for l in lignes_cap)
    tot_ca = sum(l["ca_ht"] for l in lignes_cap)
    marge_tot = sum(l["marge_unitaire"] * l["precommandes"] for l in lignes_cap)
    ca_produits = sum(l["prix_ht"] * l["precommandes"] for l in lignes_cap)
    serie_ca = [{"x": r[0], "y": round(r[1] / ech)} for r in conn.execute(
        "SELECT substr(paye_le,1,10), SUM(ca_previsionnel_ht) FROM precommandes WHERE paye_le IS NOT NULL AND "
        "paye_le <= ? GROUP BY 1 ORDER BY 1", (t,))]
    cumul_ca, acc = [], 0
    for p in serie_ca:
        acc += p["y"]
        cumul_ca.append({"x": p["x"], "y": acc})
    couts = [dict(r) for r in conn.execute("SELECT composant, fournisseur, cout_prevu, cout_reel FROM couts_revient")]
    camps = [dict(r) for r in conn.execute(
        "SELECT id, nom, pays, budget_propose, budget_valide, budget_depense, cout_acquisition, statut "
        "FROM campagnes WHERE cree_le <= ? ORDER BY cree_le", (t,))]
    dep = conn.execute("SELECT valeur FROM kpi_journalier WHERE pays='FR' AND indicateur='depense_marketing' AND "
                       "jour <= ? ORDER BY jour DESC LIMIT 1", (t[:10],)).fetchone()
    cpp = round(dep[0] / tot_n, 2) if dep and tot_n else None
    attente = conn.execute("SELECT COUNT(*) FROM precommandes WHERE statut IN ('controle_paiement','attente_credit') "
                           "AND cree_le <= ?", (t,)).fetchone()[0]
    return {"par_capacite": lignes_cap, "precommandes_payees": tot_n, "ca_ht": tot_ca,
            "marge_produits": marge_tot, "taux_marge_moyen": round(100 * marge_tot / ca_produits, 1) if ca_produits else None,
            "objectif_marge": objectif, "serie_ca": cumul_ca, "couts_revient": couts, "campagnes": camps,
            "depense_marketing": dep[0] if dep else 0, "cout_par_precommande": cpp, "paiements_en_attente": attente}


# --------------------------------------------------------------------------- production
def kpi_production(conn, t: str) -> dict:
    ech = _echelle(conn)
    grille = []
    for cap, dcap in CAPACITES.items():
        for col, dcol in COLORIS.items():
            offre = conn.execute("SELECT COALESCE(SUM(quantite),0) FROM lots_production WHERE pays='FR' AND capacite=? "
                                 "AND coloris=? AND cree_le <= ? AND disponible_le <= '2026-10-23T08:00:00'",
                                 (cap, col, t)).fetchone()[0]
            reserve = conn.execute("SELECT COUNT(*) FROM precommandes p JOIN lots_production l ON l.id=p.lot_id WHERE "
                                   "p.capacite=? AND p.coloris=? AND p.reserve_le <= ? AND "
                                   "l.disponible_le <= '2026-10-23T08:00:00'", (cap, col, t)).fetchone()[0]
            demande = conn.execute("SELECT COUNT(*) FROM precommandes WHERE capacite=? AND coloris=? AND cree_le <= ? "
                                   "AND statut != 'abandonnee'", (cap, col, t)).fetchone()[0]
            from ..metier import prochain_lot, libelle_delai
            lot = prochain_lot(conn, cap, col, t)
            grille.append({"capacite": cap, "coloris": col, "libelle": "%s %s" % (dcap["libelle"], dcol["libelle"]),
                           "offre_lancement": offre, "reserve_lancement": reserve, "demande": demande,
                           "taux_couverture": round(100 * min(offre, reserve) / demande, 1) if demande else 100.0,
                           "prochaine_date": lot["date"], "en_stock": lot["en_stock"],
                           "delai": libelle_delai(lot["date"], "domicile", parse(t))})
    plan = [{"x": r[0][:10], "y": r[1]} for r in conn.execute(
        "SELECT disponible_le, SUM(quantite) FROM lots_production WHERE pays='FR' AND cree_le <= ? GROUP BY 1 ORDER BY 1",
        (t,))]
    origines = [dict(r) for r in conn.execute(
        "SELECT origine, SUM(quantite) quantite, MIN(disponible_le) disponible_le, MAX(cree_le) cree_le "
        "FROM lots_production WHERE pays='FR' AND cree_le <= ? GROUP BY origine ORDER BY MIN(cree_le)", (t,))]
    capa = [dict(r) for r in conn.execute("SELECT * FROM capacites_fournisseurs WHERE semaine >= ? ORDER BY semaine, "
                                          "fournisseur LIMIT 8", ((parse(t) - timedelta(days=6)).strftime("%Y-%m-%d"),))]
    files = {s: conn.execute("SELECT COUNT(*) FROM precommandes WHERE statut=? AND cree_le <= ?", (s, t)).fetchone()[0]
             for s in ("payee", "delai_a_allonger", "a_reserver")}
    tests = {r[0]: r[1] for r in conn.execute("SELECT statut, COUNT(*) FROM appareils_test GROUP BY 1")}
    return {"grille": grille, "plan": plan, "origines": origines, "capacites": capa, "files": files,
            "appareils_test": tests, "echelle": ech, "pays": pilotage.tableau(conn, t)}


# --------------------------------------------------------------------------- direction générale
def kpi_dg(conn, t: str) -> dict:
    fin = kpi_finance(conn, t)
    tab = pilotage.tableau(conn, t)
    total_monde = sum(l["precommandes"] for l in tab if l["pays"] != "FR") + _precommandes_stats(conn, t)["total"] \
        if parse(t) >= OUVERTURE else 0
    plans = [dict(r, contenu=json.loads(r["contenu"])) for r in conn.execute(
        "SELECT * FROM plans_lancement WHERE soumis_le <= ? ORDER BY soumis_le DESC", (t,))]
    for p in plans:
        if p["decide_le"] and p["decide_le"] > t:
            p["statut"], p["decide_le"] = "soumis", None
    objectifs = [dict(r) for r in conn.execute("SELECT * FROM objectifs_marge WHERE defini_le <= ? ORDER BY defini_le "
                                               "DESC", (t,))]
    return {"finance": fin, "pays": tab, "precommandes_monde": total_monde, "plans": plans, "objectifs": objectifs,
            "hebdo": tableau_hebdomadaire(conn, t)}
