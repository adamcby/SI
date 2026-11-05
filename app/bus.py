"""Bus d'information : chaque action d'un acteur émet un flux codifié (Fig. 1-3)
et notifie l'acteur destinataire. C'est la traduction exécutable des flèches
des diagrammes de flux.
"""
from typing import Optional

from .referentiel import ACTEURS, FLUX, PORTEUR_APPLE, ECRANS, ecran_url


def _destinataire_reel(code_acteur: str, flux: dict, cote: str) -> str:
    """« mkt » (SI marketing d'Apple) -> acteur interne qui porte la relation."""
    if code_acteur != "mkt":
        return code_acteur
    autre = flux["vers"] if cote == "de" else flux["de"]
    return PORTEUR_APPLE.get(autre, "dir_marketing")


def lien_defaut(acteur: str) -> str:
    a = ACTEURS.get(acteur)
    if not a or not a.get("ecran_defaut"):
        return "/journal"
    for e in ECRANS:
        if e["acteur"] == acteur and e["slug"] == a["ecran_defaut"]:
            return ecran_url(e)
    return "/journal"


def emettre(conn, code: str, objet: str, horodatage: str, contenu: str = "", emetteur: Optional[str] = None,
            recepteur: Optional[str] = None, processus: Optional[str] = None, noeud: Optional[str] = None,
            instance_id: Optional[int] = None, volume: int = 1, notifier: bool = True, lien: Optional[str] = None,
            demo: int = 0, titre: Optional[str] = None) -> int:
    """Enregistre un flux dans le journal et crée la notification du destinataire."""
    f = FLUX[code]
    em = emetteur or _destinataire_reel(f["de"], f, "de")
    rc = recepteur or _destinataire_reel(f["vers"], f, "vers")
    cur = conn.execute(
        "INSERT INTO flux_log(code, emetteur, recepteur, objet, contenu, processus, noeud, instance_id, volume, "
        "horodatage, demo) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        (code, em, rc, objet, contenu, processus, noeud, instance_id, volume, horodatage, demo))
    fid = cur.lastrowid
    if notifier and rc in ACTEURS and ACTEURS[rc]["type"] != "systeme":
        conn.execute(
            "INSERT INTO notifications(acteur, flux_id, titre, message, lien, lu, horodatage) VALUES (?,?,?,?,?,0,?)",
            (rc, fid, titre or "%s · %s" % (code, f["libelle"]), objet, lien or lien_defaut(rc), horodatage))
    return fid
