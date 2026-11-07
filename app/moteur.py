"""Moteur d'exécution BPMN (jetons) pour les processus P1 et P2.

L'état d'une instance est TOUJOURS recalculé en rejouant ses événements
jusqu'à l'heure simulée : on peut donc remonter le temps (préréglages de
l'horloge) et voir chaque processus dans l'état exact où il était.

Règles :
* une tâche à plusieurs sorties = parallélisme implicite (toutes les sorties) ;
* une passerelle exclusive choisit UNE sortie selon son « issue » (oui / non) ;
* les jointures implicites (référentiel « jointures ») attendent toutes leurs branches ;
* une tâche sans sortie (ex. P1-T11, P1-T12) termine sa branche.
"""
from typing import Dict, Iterable, List, Optional

from .referentiel import PROCESSUS

DEPARTS = {
    # type d'instance -> nœuds actifs au démarrage
    ("P1", "precommande"): ["T01"],
    ("P1", "analyse"): ["T10"],
    ("P2", "campagne"): ["T01"],
}
ARRETS = {
    # une précommande « passe la main » au tableau de bord : T10 est traité par lot (instance « analyse »)
    ("P1", "precommande"): {"T10"},
}


class TransitionInvalide(Exception):
    """Action refusée : la tâche n'est pas active dans le processus."""


def _sorties(proc: dict, noeud: str) -> List[tuple]:
    return [t for t in proc["transitions"] if t[0] == noeud]


class Etat:
    def __init__(self, processus: str, type_instance: str):
        self.processus = processus
        self.type = type_instance
        self.proc = PROCESSUS[processus]
        self.jetons: List[str] = list(DEPARTS[(processus, type_instance)])
        self.arrivees: Dict[str, set] = {}
        self.termines: List[str] = []          # nœuds exécutés (ordre)
        self.fins: List[str] = []              # événements de fin atteints
        self.historique: List[dict] = []
        self.arrets = ARRETS.get((processus, type_instance), set())

    # -- lecture
    @property
    def fini(self) -> bool:
        return not self.jetons

    def actif(self, noeud: str) -> bool:
        return noeud in self.jetons

    def dict(self) -> dict:
        return {"processus": self.processus, "type": self.type, "jetons": list(self.jetons),
                "termines": list(self.termines), "fins": list(self.fins), "fini": self.fini,
                "attente_jointure": {k: sorted(v) for k, v in self.arrivees.items() if v}}

    # -- écriture
    def appliquer(self, noeud: str, issue: Optional[str] = None, evt: Optional[dict] = None) -> "Etat":
        if noeud not in self.jetons:
            raise TransitionInvalide(
                "La tâche %s-%s n'est pas active (tâches actives : %s)."
                % (self.processus, noeud, ", ".join(self.jetons) or "aucune — processus terminé"))
        definition = self.proc["noeuds"][noeud]
        sorties = _sorties(self.proc, noeud)
        if definition["type"] == "passerelle":
            if issue not in definition.get("issues", []):
                raise TransitionInvalide("Issue « %s » invalide pour la passerelle %s." % (issue, noeud))
            sorties = [t for t in sorties if t[2] == issue]
        self.jetons.remove(noeud)
        self.termines.append(noeud)
        self.historique.append(dict(evt or {}, noeud=noeud, issue=issue))
        if noeud in self.arrets:
            return self
        jointures = self.proc.get("jointures", {})
        for (_src, cible, _issue, _a, _b) in sorties:
            cdef = self.proc["noeuds"][cible]
            if cible in jointures and noeud in jointures[cible]:
                arr = self.arrivees.setdefault(cible, set())
                arr.add(noeud)
                if arr >= set(jointures[cible]):
                    self.arrivees[cible] = set()
                    self._activer(cible, cdef)
            else:
                self._activer(cible, cdef)
        return self

    def _activer(self, cible: str, cdef: dict) -> None:
        if cdef["type"] == "fin":
            self.fins.append(cible)
            self.termines.append(cible)
        elif cible not in self.jetons:
            self.jetons.append(cible)


def rejouer(processus: str, type_instance: str, evenements: Iterable[dict]) -> Etat:
    """Reconstruit l'état à partir d'événements triés (les événements « partiels » sont ignorés)."""
    etat = Etat(processus, type_instance)
    for e in evenements:
        if e.get("partiel"):
            continue
        etat.appliquer(e["noeud"], e.get("issue"), e)
    return etat


def charger_etat(conn, instance_id: int, jusqua: str) -> Etat:
    inst = conn.execute("SELECT * FROM instances WHERE id = ?", (instance_id,)).fetchone()
    if inst is None:
        raise KeyError("Instance %s introuvable" % instance_id)
    evts = conn.execute(
        "SELECT * FROM evenements WHERE instance_id = ? AND horodatage <= ? ORDER BY horodatage, id",
        (instance_id, jusqua)).fetchall()
    return rejouer(inst["processus"], inst["type"], [dict(e) for e in evts])


def evenements_futurs(conn, instance_id: int, apres: str) -> int:
    return conn.execute("SELECT COUNT(*) FROM evenements WHERE instance_id = ? AND horodatage > ?",
                        (instance_id, apres)).fetchone()[0]


def enregistrer(conn, instance_id: int, noeud: str, horodatage: str, acteur: str,
                issue: Optional[str] = None, details: str = "", partiel: bool = False, controler: bool = True) -> Etat:
    """Valide puis enregistre l'exécution d'une tâche (contrôle des transitions)."""
    if controler and not partiel:
        if evenements_futurs(conn, instance_id, horodatage):
            raise TransitionInvalide(
                "Cette instance contient des événements postérieurs à l'heure simulée : elle est figée "
                "(historique). Avancez l'horloge ou lancez une nouvelle démonstration.")
        etat = charger_etat(conn, instance_id, horodatage)
        etat.appliquer(noeud, issue)
    conn.execute(
        "INSERT INTO evenements(instance_id, noeud, issue, acteur, horodatage, partiel, details) VALUES (?,?,?,?,?,?,?)",
        (instance_id, noeud, issue, acteur, horodatage, 1 if partiel else 0, details))
    return charger_etat(conn, instance_id, horodatage)


def creer_instance(conn, processus: str, type_instance: str, libelle: str, horodatage: str,
                   cree_par: str, objet_id: Optional[int] = None, declencheur: Optional[str] = None,
                   demo: int = 0) -> int:
    cur = conn.execute(
        "INSERT INTO instances(processus, type, libelle, objet_id, declencheur, cree_le, cree_par, demo) "
        "VALUES (?,?,?,?,?,?,?,?)",
        (processus, type_instance, libelle, objet_id, declencheur, horodatage, cree_par, demo))
    return cur.lastrowid
