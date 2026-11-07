"""Règles de gestion partagées (prix, coûts, marges, délais, allocation des stocks, projection)."""
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from .horloge import MOIS, MOIS_LONG, JOURS, fmt, parse
from .referentiel import COUTS_REVIENT, PRODUIT, SURCOUT_NAND

OUVERTURE = parse("2026-10-16T14:00:00")
SORTIE = parse("2026-10-23T08:00:00")
FIN_PRECOMMANDES = parse("2026-10-23T00:00:00")
TVA = PRODUIT["tva"]

CAPACITES = {c["id"]: c for c in PRODUIT["capacites"]}
COLORIS = {c["id"]: c for c in PRODUIT["coloris"]}


# ----------------------------------------------------------------- prix et coûts
def prix_catalogue(conn=None) -> Dict[str, float]:
    if conn is not None:
        rows = conn.execute("SELECT capacite, prix_ttc FROM prix").fetchall()
        if rows:
            return {r["capacite"]: r["prix_ttc"] for r in rows}
    return {c["id"]: c["prix"] for c in PRODUIT["capacites"]}


def ht(ttc: float) -> float:
    return round(ttc / (1 + TVA), 2)


def cout_revient(capacite: str, conn=None) -> float:
    if conn is not None:
        row = conn.execute("SELECT SUM(cout_reel) FROM couts_revient").fetchone()
        base = row[0] if row and row[0] else None
    else:
        base = None
    if base is None:
        base = sum(c[3] for c in COUTS_REVIENT)
    return round(base + SURCOUT_NAND[capacite], 2)


def cout_revient_prevu(capacite: str) -> float:
    return round(sum(c[2] for c in COUTS_REVIENT) + SURCOUT_NAND[capacite] * 0.62, 2)


def chiffrer(capacite: str, applecare: bool, conn=None) -> dict:
    """CA prévisionnel HT, coût de revient et marge d'une précommande (tâches P1-T04 / T05)."""
    prix = prix_catalogue(conn)[capacite]
    ac = PRODUIT["applecare"]["prix"] if applecare else 0.0
    ca = ht(prix + ac)
    cout = cout_revient(capacite, conn)
    marge_produit = ht(prix) - cout
    return {"prix_ttc": prix, "applecare_ttc": ac, "ca_ht": ca, "cout_revient": cout,
            "marge": round(marge_produit + ht(ac) * 0.7, 2),
            "taux_marge_produit": round(100 * marge_produit / ht(prix), 1)}


# ----------------------------------------------------------------- dates et libellés
def libelle_court(d: datetime) -> str:
    return "%d %s" % (d.day, MOIS[d.month - 1])


def libelle_delai(date_lot: Optional[str], mode: str = "domicile", maintenant: Optional[datetime] = None) -> str:
    verbe = "Retrait en magasin" if mode == "retrait" else "Livraison"
    if not date_lot:
        return "%s : décembre (sous réserve de production)" % verbe
    d = parse(date_lot)
    if maintenant is not None and maintenant >= SORTIE and d <= maintenant:
        return "%s : 2 à 4 jours ouvrés" % verbe if mode == "domicile" else "Retrait en magasin : sous 2 h"
    if d <= SORTIE:
        return "%s à partir du vendredi 23 octobre" % verbe
    fin = d + timedelta(days=7)
    return "%s : %s – %s" % (verbe, libelle_court(d), libelle_court(fin))


# ----------------------------------------------------------------- allocation des stocks (ERP)
def lots_config(conn, pays: str, capacite: str, coloris: str, maintenant: str) -> List[dict]:
    rows = conn.execute(
        """SELECT l.id, l.disponible_le, l.quantite, l.origine,
                  (SELECT COUNT(*) FROM precommandes p WHERE p.lot_id = l.id AND p.reserve_le <= ?) AS reserve
           FROM lots_production l
           WHERE l.pays = ? AND l.capacite = ? AND l.coloris = ? AND l.cree_le <= ?
           ORDER BY l.disponible_le, l.id""",
        (maintenant, pays, capacite, coloris, maintenant)).fetchall()
    return [dict(r, restant=r["quantite"] - r["reserve"]) for r in rows]


def date_limite_stock(maintenant: datetime) -> datetime:
    """Un appareil est « en stock » s'il est livrable à la sortie (avant le 23/10) ou tout de suite (après)."""
    return max(maintenant, SORTIE)


def prochain_lot(conn, capacite: str, coloris: str, maintenant: str, pays: str = "FR") -> dict:
    """Premier lot ayant encore de la capacité -> date de livraison promise (tâche P1-T02)."""
    now = parse(maintenant)
    limite = fmt(date_limite_stock(now))
    for lot in lots_config(conn, pays, capacite, coloris, maintenant):
        if lot["restant"] > 0:
            return {"lot_id": lot["id"], "date": lot["disponible_le"], "restant": lot["restant"],
                    "en_stock": lot["disponible_le"] <= limite}
    return {"lot_id": None, "date": None, "restant": 0, "en_stock": False}


def delais_catalogue(conn, maintenant: str, mode: str = "domicile") -> Dict[str, dict]:
    """Délai affiché pour chaque configuration (16 combinaisons) — ce que voit le client."""
    out = {}
    now = parse(maintenant)
    for cap in CAPACITES:
        for col in COLORIS:
            lot = prochain_lot(conn, cap, col, maintenant)
            out["%s|%s" % (cap, col)] = dict(lot, libelle=libelle_delai(lot["date"], mode, now))
    return out


# ----------------------------------------------------------------- profil des précommandes et projection
_POIDS_JOURS = [5200, 3900, 3600, 3100, 2800, 3300]          # 17/10 -> 22/10
_PREMIERES_HEURES = [6400, 3100, 1800, 1250, 980, 820, 760, 690, 520, 310]   # 16/10 14 h -> 23 h
_DIURNE = [0.6, 0.3, 0.2, 0.15, 0.15, 0.2, 0.6, 1.6, 2.8, 3.6, 4.2, 4.6, 5.2, 5.0, 4.8, 4.6, 4.7, 5.0, 5.6,
           6.4, 7.0, 6.6, 4.8, 2.4]


def profil_horaire() -> List[Tuple[datetime, float]]:
    """Poids horaires des précommandes du 16/10 14:00 au 22/10 23:00 (somme = 1)."""
    pts: List[Tuple[datetime, float]] = []
    for i, v in enumerate(_PREMIERES_HEURES):
        pts.append((OUVERTURE + timedelta(hours=i), float(v)))
    s_diurne = sum(_DIURNE)
    for j, total in enumerate(_POIDS_JOURS):
        jour = parse("2026-10-17T00:00:00") + timedelta(days=j)
        for h in range(24):
            pts.append((jour + timedelta(hours=h), total * _DIURNE[h] / s_diurne))
    tot = sum(p for _, p in pts)
    return [(d, p / tot) for d, p in pts]


_PROFIL = None


def fraction_attendue(t: datetime) -> float:
    """Part des précommandes de la semaine normalement atteinte à l'instant t."""
    global _PROFIL
    if _PROFIL is None:
        _PROFIL = profil_horaire()
    f = 0.0
    for d, p in _PROFIL:
        if t >= d + timedelta(hours=1):
            f += p
        elif t > d:
            f += p * (t - d).total_seconds() / 3600.0
            break
        else:
            break
    return f


def projection_sortie(precommandes: int, t: datetime) -> int:
    """Projection de la demande à la date de sortie à partir du rythme observé (prévision simple)."""
    if t >= FIN_PRECOMMANDES:
        return precommandes
    f = fraction_attendue(t)
    if f < 0.02:
        return precommandes
    return int(round(precommandes / f))


def courbe_vues(vues_finales: float, publie_le: str, t: datetime, tau_jours: float = 4.0) -> float:
    """Vues cumulées d'une vidéo à l'instant t (croissance saturante)."""
    d0 = parse(publie_le)
    if t <= d0:
        return 0.0
    jours = (t - d0).total_seconds() / 86400.0
    return vues_finales * (1 - math.exp(-jours / tau_jours))


def euros(v: float, decimales: int = 0) -> str:
    s = ("{:,.%df}" % decimales).format(v).replace(",", " ").replace(".", ",")
    return s + " €"


def libelle_jour(d: datetime) -> str:
    return "%s %d %s" % (JOURS[d.weekday()], d.day, MOIS_LONG[d.month - 1])
