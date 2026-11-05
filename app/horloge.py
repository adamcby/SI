"""Horloge de simulation du SI.

L'application « rejoue » le lancement : l'heure simulée part d'un point de départ
(ex. vendredi 16/10/2026 14:00, ouverture des précommandes) puis avance en temps
réel (ou accéléré). Toutes les données sont filtrées sur cette heure : les
précommandes historiques « arrivent » donc en direct quand on rejoue l'ouverture.
"""
import time
from datetime import datetime, timedelta
from typing import Optional

from .db import ecrire_parametre, lire_parametre

FORMAT = "%Y-%m-%dT%H:%M:%S"

PRESETS = [
    {"id": "keynote", "libelle": "Keynote — mer. 9 sept. 2026, 19:00", "date": "2026-09-09T19:00:00",
     "phase": "avant", "aide": "Démarrage du processus P2 (campagne TikTok)."},
    {"id": "tableau_12_10", "libelle": "Tableau de bord — lun. 12 oct. 2026, 09:00", "date": "2026-10-12T09:00:00",
     "phase": "avant", "aide": "Le tableau de bord CRM du dossier (§ 6.3), 4 jours avant les précommandes."},
    {"id": "ouverture", "libelle": "Ouverture des précommandes — ven. 16 oct. 2026, 14:00", "date": "2026-10-16T14:00:00",
     "phase": "precommandes", "aide": "Démarrage du processus P1 : les précommandes arrivent en direct."},
    {"id": "j3", "libelle": "Précommandes J+3 — lun. 19 oct. 2026, 10:00", "date": "2026-10-19T10:00:00",
     "phase": "precommandes", "aide": "Situation par défaut : files d'attente actives pour chaque acteur."},
    {"id": "apres", "libelle": "Après la sortie — lun. 2 nov. 2026, 10:00", "date": "2026-11-02T10:00:00",
     "phase": "apres", "aide": "Indicateurs de résultat : ventes, satisfaction, retours, AppleCare."},
]
PRESET_DEFAUT = "j3"


def parse(s: str) -> datetime:
    return datetime.strptime(s[:19], FORMAT)


def fmt(d: datetime) -> str:
    return d.strftime(FORMAT)


def regler(conn, date_iso: Optional[str] = None, vitesse: Optional[float] = None, preset: Optional[str] = None) -> None:
    if preset:
        p = next((x for x in PRESETS if x["id"] == preset), None)
        if p is None:
            raise ValueError("Préréglage inconnu : %s" % preset)
        date_iso = p["date"]
    if date_iso is None:
        date_iso = fmt(maintenant(conn))
    parse(date_iso)  # validation
    ecrire_parametre(conn, "horloge_base", date_iso[:19])
    ecrire_parametre(conn, "horloge_reel", repr(time.time()))
    if vitesse is not None:
        ecrire_parametre(conn, "horloge_vitesse", float(vitesse))
    ecrire_parametre(conn, "horloge_preset", preset or "")


def maintenant(conn) -> datetime:
    base = lire_parametre(conn, "horloge_base")
    if not base:
        p = next(x for x in PRESETS if x["id"] == PRESET_DEFAUT)
        return parse(p["date"])
    reel = float(lire_parametre(conn, "horloge_reel", "0") or 0)
    vitesse = float(lire_parametre(conn, "horloge_vitesse", "1") or 1)
    ecoule = max(0.0, time.time() - reel) * vitesse
    return parse(base) + timedelta(seconds=int(ecoule))


def maintenant_iso(conn) -> str:
    return fmt(maintenant(conn))


def phase(d: datetime) -> str:
    if d < parse("2026-10-16T14:00:00"):
        return "avant"
    if d < parse("2026-10-23T08:00:00"):
        return "precommandes"
    return "apres"


LIBELLES_PHASE = {
    "avant": "Avant la sortie (depuis la keynote)",
    "precommandes": "Précommandes ouvertes",
    "apres": "Après la sortie (23/10)",
}

JOURS = ["lun.", "mar.", "mer.", "jeu.", "ven.", "sam.", "dim."]
MOIS = ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."]
MOIS_LONG = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre",
             "novembre", "décembre"]


def libelle_date(d: datetime, heure: bool = True) -> str:
    s = "%s %d %s %d" % (JOURS[d.weekday()], d.day, MOIS[d.month - 1], d.year)
    return s + (" · %02d:%02d" % (d.hour, d.minute) if heure else "")


def etat(conn) -> dict:
    d = maintenant(conn)
    ph = phase(d)
    return {
        "iso": fmt(d), "libelle": libelle_date(d), "phase": ph, "phase_libelle": LIBELLES_PHASE[ph],
        "vitesse": float(lire_parametre(conn, "horloge_vitesse", "1") or 1),
        "preset": lire_parametre(conn, "horloge_preset", ""),
        "presets": PRESETS,
        "mode": lire_parametre(conn, "mode_execution", "pas_a_pas"),
    }
