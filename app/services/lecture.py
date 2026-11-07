"""Lectures transverses : notifications, journal des flux, files de travail, jetons BPMN, SI partagé."""
from typing import Dict, List, Optional

from ..db import BRIQUES
from ..moteur import charger_etat
from ..referentiel import ACTEURS, FLUX, PROCESSUS, tache


# --------------------------------------------------------------------------- notifications
def notifications(conn, acteur: str, t: str, limite: int = 30) -> dict:
    rows = conn.execute("SELECT n.*, f.code FROM notifications n LEFT JOIN flux_log f ON f.id = n.flux_id "
                        "WHERE n.acteur=? AND n.horodatage <= ? ORDER BY n.horodatage DESC, n.id DESC LIMIT ?",
                        (acteur, t, limite)).fetchall()
    non_lues = conn.execute("SELECT COUNT(*) FROM notifications WHERE acteur=? AND horodatage <= ? AND lu=0",
                            (acteur, t)).fetchone()[0]
    return {"non_lues": non_lues, "items": [dict(r) for r in rows]}


def marquer_lues(conn, acteur: str, t: str) -> None:
    conn.execute("UPDATE notifications SET lu=1 WHERE acteur=? AND horodatage <= ?", (acteur, t))


# --------------------------------------------------------------------------- journal des flux
def journal(conn, t: str, code: Optional[str] = None, acteur: Optional[str] = None, processus: Optional[str] = None,
            limite: int = 100, depuis_id: int = 0) -> List[dict]:
    sql = "SELECT * FROM flux_log WHERE horodatage <= ? AND id > ?"
    args: list = [t, depuis_id]
    if code:
        sql += " AND code LIKE ?"
        args.append(code + "%")
    if acteur:
        sql += " AND (emetteur = ? OR recepteur = ?)"
        args += [acteur, acteur]
    if processus:
        sql += " AND processus = ?"
        args.append(processus)
    sql += " ORDER BY horodatage DESC, id DESC LIMIT ?"
    args.append(limite)
    return [dict(r) for r in conn.execute(sql, args)]


def stats_flux(conn, t: str) -> Dict[str, dict]:
    rows = conn.execute("SELECT code, SUM(volume) v, COUNT(*) n, MAX(horodatage) dernier FROM flux_log "
                        "WHERE horodatage <= ? GROUP BY code", (t,)).fetchall()
    out = {c: {"volume": 0, "messages": 0, "dernier": None} for c in FLUX}
    for r in rows:
        out[r["code"]] = {"volume": r["v"], "messages": r["n"], "dernier": r["dernier"]}
    return out


# --------------------------------------------------------------------------- instances actives
def _instances_visibles(conn, t: str, processus: Optional[str] = None):
    sql = "SELECT * FROM instances WHERE cree_le <= ?"
    args: list = [t]
    if processus:
        sql += " AND processus = ?"
        args.append(processus)
    return conn.execute(sql + " ORDER BY cree_le DESC", args).fetchall()


def files_de_travail(conn, t: str) -> List[dict]:
    """Toutes les tâches humaines en attente, avec l'acteur qui doit agir et l'écran où le faire."""
    out = []
    for inst in _instances_visibles(conn, t):
        etat = charger_etat(conn, inst["id"], t)
        for j in etat.jetons:
            d = PROCESSUS[inst["processus"]]["noeuds"][j]
            if inst["type"] == "precommande" and j == "T10":
                continue  # traité par lot (analyse)
            if d.get("auto"):
                continue
            out.append({"instance_id": inst["id"], "processus": inst["processus"], "type": inst["type"],
                        "objet_id": inst["objet_id"], "libelle": inst["libelle"], "noeud": j,
                        "code": "%s-%s" % (inst["processus"], j), "tache": d["libelle"].replace("\n", " "),
                        "acteurs": d.get("acteurs", []), "ecran": d.get("ecran"), "depuis": _depuis(conn, inst["id"], t),
                        "demo": inst["demo"]})
    # P1-T10 : précommandes en attente d'analyse (traitement par lot)
    n = conn.execute("SELECT COUNT(*) FROM precommandes WHERE pays='FR' AND analyse_id IS NULL AND paye_le IS NOT NULL "
                     "AND paye_le <= ? AND crm_le IS NOT NULL", (t,)).fetchone()[0]
    if n:
        out.append({"instance_id": None, "processus": "P1", "type": "lot", "objet_id": None,
                    "libelle": "%d précommandes en attente d'analyse" % n, "noeud": "T10", "code": "P1-T10",
                    "tache": "Analyse le tableau de bord", "acteurs": ["dir_marketing"], "ecran": "E21",
                    "depuis": None, "demo": 0})
    # Organisme financier : demandes en étude (flux FE-09 avant la passerelle G01)
    for r in conn.execute("SELECT d.id, d.cree_le, p.reference, p.instance_id FROM demandes_credit d JOIN precommandes p "
                          "ON p.id=d.precommande_id WHERE d.statut='etude' AND d.cree_le <= ?", (t,)):
        out.append({"instance_id": r["instance_id"], "processus": "P1", "type": "credit", "objet_id": r["id"],
                    "libelle": "Demande de crédit — précommande %s" % r["reference"], "noeud": "G01",
                    "code": "FE-09A", "tache": "Étudier la demande de crédit", "acteurs": ["organisme_financier"],
                    "ecran": "E48", "depuis": r["cree_le"], "demo": 0})
    return out


def _depuis(conn, inst_id: int, t: str) -> Optional[str]:
    row = conn.execute("SELECT MAX(horodatage) FROM evenements WHERE instance_id=? AND horodatage <= ?",
                       (inst_id, t)).fetchone()
    return row[0] if row else None


def file_acteur(conn, acteur: str, t: str) -> List[dict]:
    return [f for f in files_de_travail(conn, t) if acteur in f["acteurs"]]


# --------------------------------------------------------------------------- jetons BPMN (vue processus)
def jetons_processus(conn, processus: str, t: str) -> dict:
    noeuds = PROCESSUS[processus]["noeuds"]
    res = {n: {"jetons": 0, "passages": 0} for n in noeuds}
    for inst in _instances_visibles(conn, t, processus):
        etat = charger_etat(conn, inst["id"], t)
        for j in etat.jetons:
            if not (inst["type"] == "precommande" and j == "T10"):
                res[j]["jetons"] += 1
        for n in etat.termines:
            if n in res:
                res[n]["passages"] += 1
    if processus == "P1":
        # précommandes historiques (traitées automatiquement, sans instance détaillée)
        base = "FROM precommandes WHERE instance_id IS NULL AND cree_le <= ?"
        crees = conn.execute("SELECT COUNT(*) " + base, (t,)).fetchone()[0]
        payees = conn.execute("SELECT COUNT(*) " + base + " AND paye_le IS NOT NULL AND paye_le <= ?", (t, t)).fetchone()[0]
        reservees = conn.execute("SELECT COUNT(*) " + base + " AND reserve_le IS NOT NULL AND reserve_le <= ?",
                                 (t, t)).fetchone()[0]
        allongees = conn.execute("SELECT COUNT(*) " + base + " AND delai_allonge=1 AND reserve_le <= ?", (t, t)).fetchone()[0]
        confirmees = conn.execute("SELECT COUNT(*) " + base + " AND confirme_le IS NOT NULL AND confirme_le <= ?",
                                  (t, t)).fetchone()[0]
        for n, v in (("T01", crees), ("T02", crees), ("T03", crees), ("G01", payees), ("T04", payees), ("T05", payees),
                     ("T06", payees), ("G02", reservees), ("T07", allongees), ("T08", reservees), ("T09", confirmees),
                     ("E1", confirmees)):
            res[n]["passages"] += v
        attente = conn.execute("SELECT COUNT(*) FROM precommandes WHERE pays='FR' AND analyse_id IS NULL AND "
                               "paye_le IS NOT NULL AND paye_le <= ? AND crm_le IS NOT NULL", (t,)).fetchone()[0]
        res["T10"]["jetons"] += attente
        analysees = conn.execute("SELECT COUNT(*) FROM precommandes WHERE analyse_id IS NOT NULL AND paye_le <= ?",
                                 (t,)).fetchone()[0]
        res["T10"]["passages_precommandes"] = analysees
    return res


def instances_processus(conn, processus: str, t: str, limite: int = 40) -> List[dict]:
    out = []
    for inst in _instances_visibles(conn, t, processus)[:limite]:
        etat = charger_etat(conn, inst["id"], t)
        out.append(dict(inst, jetons=etat.jetons, termines=etat.termines, fini=etat.fini, fins=etat.fins))
    return out


# --------------------------------------------------------------------------- SI partagé
def tables_si(conn) -> List[dict]:
    out = []
    for brique, tables in BRIQUES.items():
        for tb in tables:
            n = conn.execute("SELECT COUNT(*) FROM %s" % tb).fetchone()[0]
            cols = [r[1] for r in conn.execute("PRAGMA table_info(%s)" % tb)]
            out.append({"brique": brique, "table": tb, "lignes": n, "colonnes": cols})
    return out


def apercu_table(conn, table: str, limite: int = 25) -> dict:
    autorisees = {tb for tables in BRIQUES.values() for tb in tables}
    if table not in autorisees:
        raise KeyError("Table inconnue")
    cols = [r[1] for r in conn.execute("PRAGMA table_info(%s)" % table)]
    ordre = "id DESC" if "id" in cols else "rowid DESC"
    rows = conn.execute("SELECT * FROM %s ORDER BY %s LIMIT ?" % (table, ordre), (limite,)).fetchall()
    lignes = []
    for r in rows:
        d = dict(r)
        if table == "clients" and d.get("apple_id"):
            d["apple_id"] = pseudonymiser(d["apple_id"])
            d["nom"] = (d.get("nom") or "")[:1] + "."
        lignes.append(d)
    return {"table": table, "colonnes": cols, "lignes": lignes}


def pseudonymiser(email: str) -> str:
    """Affichage minimisé de l'identifiant (RGPD) : l•••••.m•••••@icloud.com"""
    if "@" not in email:
        return email
    loc, dom = email.split("@", 1)
    parts = loc.split(".")
    return ".".join(p[:1] + "•" * max(2, min(5, len(p) - 1)) for p in parts) + "@" + dom


def libelle_tache(code: str) -> str:
    d = tache(code)
    return d["libelle"].replace("\n", " ") if d else code
