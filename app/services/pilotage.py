"""Processus P1 (suite) — pilotage par le tableau de bord : T10 Analyse, G03 Demande > offre ?,
T11 Augmente la production / répartit les stocks (production), T12 Relance la communication (marketing)."""
import json
from datetime import timedelta
from typing import List, Optional

from ..bus import emettre
from ..db import lire_parametre
from ..horloge import fmt, parse
from ..metier import projection_sortie
from ..moteur import TransitionInvalide, charger_etat, creer_instance, enregistrer
from ..referentiel import PAYS_LIBELLE
from . import campagnes as svc_campagnes

MIX_CAP = {"256": .33, "512": .36, "1T": .22, "2T": .09}
MIX_COL = {"naturel": .27, "noir": .35, "blanc": .16, "bleu": .22}
CAPACITE_HEBDO_PAYS = {"FR": 5500, "DE": 6000, "UK": 7000, "IT": 2500, "ES": 2300, "US": 60000, "JP": 12000,
                       "IN": 3500, "CN": 40000}


def _echelle(conn) -> float:
    return float(lire_parametre(conn, "echelle", "1") or 1)


def precommandes_pays(conn, pays: str, t: str) -> int:
    if pays == "FR":
        n = conn.execute("SELECT COUNT(*) FROM precommandes WHERE pays='FR' AND statut != 'abandonnee' "
                         "AND cree_le <= ? AND cree_le < '2026-10-23T08:00:00'", (t,)).fetchone()[0]
        return n
    return conn.execute("SELECT COALESCE(SUM(nb),0) FROM precommandes_pays WHERE pays=? AND heure <= ?",
                        (pays, t)).fetchone()[0]


def offre_sortie(conn, pays: str, t: str) -> int:
    """Stock livrable à la sortie (23/10) connu à l'instant t (allocations, transferts, hausses)."""
    return conn.execute("SELECT COALESCE(SUM(quantite),0) FROM lots_production WHERE pays=? AND cree_le <= ? "
                        "AND disponible_le <= '2026-10-23T08:00:00'", (pays, t)).fetchone()[0]


def tableau(conn, t: str) -> List[dict]:
    """Tableau de bord des précommandes par pays (données de la tâche T10)."""
    tt = parse(t)
    out = []
    for pays in ["FR", "DE", "UK", "IT", "ES", "US", "JP", "IN", "CN"]:
        n = precommandes_pays(conn, pays, t)
        offre = offre_sortie(conn, pays, t)
        proj = projection_sortie(n, tt)
        hebdo = conn.execute("SELECT COALESCE(SUM(quantite),0) FROM lots_production WHERE pays=? AND cree_le <= ? "
                             "AND disponible_le > '2026-10-23T08:00:00' AND disponible_le <= '2026-11-06T08:00:00'",
                             (pays, t)).fetchone()[0]
        derniere = conn.execute("SELECT * FROM analyses WHERE pays=? AND horodatage <= ? ORDER BY horodatage DESC "
                                "LIMIT 1", (pays, t)).fetchone()
        out.append({
            "pays": pays, "libelle": PAYS_LIBELLE[pays], "precommandes": n, "projection": proj, "offre": offre,
            "ratio": round(proj / offre, 2) if offre else None, "production_2_semaines": hebdo,
            "derniere_analyse": dict(derniere) if derniere else None,
            "recommandation": "oui" if offre and proj > offre else "non",
        })
    return out


def en_attente_analyse(conn, t: str) -> int:
    return conn.execute("SELECT COUNT(*) FROM precommandes WHERE pays='FR' AND analyse_id IS NULL AND paye_le IS NOT NULL "
                        "AND paye_le <= ? AND crm_le IS NOT NULL", (t,)).fetchone()[0]


# --------------------------------------------------------------------------- T10
def lancer_analyse(conn, pays: str, t: str, acteur: str = "dir_marketing") -> dict:
    if pays not in PAYS_LIBELLE:
        raise ValueError("Pays inconnu")
    if parse(t) < parse("2026-10-16T14:00:00"):
        raise TransitionInvalide("Aucune précommande avant l'ouverture du 16/10 à 14 h.")
    ligne = next(l for l in tableau(conn, t) if l["pays"] == pays)
    inst = creer_instance(conn, "P1", "analyse", "Analyse du tableau de bord — %s" % PAYS_LIBELLE[pays], t, acteur,
                          declencheur="Précommandes en attente d'analyse", demo=1)
    nb = en_attente_analyse(conn, t) if pays == "FR" else ligne["precommandes"]
    cur = conn.execute("INSERT INTO analyses(instance_id, pays, horodatage, precommandes, projection, offre, ratio, "
                       "nb_precommandes_analysees, details, demo) VALUES (?,?,?,?,?,?,?,?,?,1)",
                       (inst, pays, t, ligne["precommandes"], ligne["projection"], ligne["offre"], ligne["ratio"], nb,
                        "Recommandation du SI : %s" % ("demande > offre" if ligne["recommandation"] == "oui"
                                                       else "demande <= offre")))
    aid = cur.lastrowid
    conn.execute("UPDATE instances SET objet_id=? WHERE id=?", (aid, inst))
    enregistrer(conn, inst, "T10", t, acteur, details="%d précommandes intégrées à l'analyse" % nb)
    if pays == "FR":
        # les précommandes en attente au jeton T10 sont « consommées » par cette analyse
        rows = conn.execute("SELECT id, instance_id FROM precommandes WHERE pays='FR' AND analyse_id IS NULL AND "
                            "paye_le IS NOT NULL AND paye_le <= ? AND crm_le IS NOT NULL", (t,)).fetchall()
        conn.execute("UPDATE precommandes SET analyse_id=? WHERE pays='FR' AND analyse_id IS NULL AND paye_le IS NOT NULL "
                     "AND paye_le <= ? AND crm_le IS NOT NULL", (aid, t))
        for r in rows:
            if r["instance_id"]:
                try:
                    if charger_etat(conn, r["instance_id"], t).actif("T10"):
                        enregistrer(conn, r["instance_id"], "T10", t, acteur, details="Intégrée à l'analyse #%d" % aid)
                except TransitionInvalide:
                    pass
    emettre(conn, "FM-17", "Tableau de bord des précommandes — %s : %s précommandes, projection %s, offre %s"
            % (PAYS_LIBELLE[pays], ligne["precommandes"], ligne["projection"], ligne["offre"]), t,
            processus="P1", noeud="T10", instance_id=inst, notifier=False, demo=1)
    return detail(conn, aid, t)


# --------------------------------------------------------------------------- G03
def decider(conn, aid: int, issue: str, t: str, commentaire: str = "", acteur: str = "dir_marketing") -> dict:
    a = _a(conn, aid)
    enregistrer(conn, a["instance_id"], "G03", t, acteur, issue=issue, details=commentaire)
    conn.execute("UPDATE analyses SET decision=?, details=COALESCE(details,'') || ? WHERE id=?",
                 (issue, (" — " + commentaire) if commentaire else "", aid))
    if issue == "oui":
        emettre(conn, "FI-04", "Demande supérieure à l'offre (%s) : augmenter la production ou répartir les stocks"
                % PAYS_LIBELLE[a["pays"]], t, processus="P1", noeud="G03", instance_id=a["instance_id"],
                lien="/a/production/plan?a=%d" % aid, demo=a["demo"])
    return detail(conn, aid, t)


# --------------------------------------------------------------------------- T11 (production)
def capacite_disponible(conn, t: str) -> dict:
    row = conn.execute("SELECT * FROM capacites_fournisseurs WHERE fournisseur='Samsung Display' AND semaine >= ? "
                       "ORDER BY semaine LIMIT 1", ((parse(t) - timedelta(days=6)).strftime("%Y-%m-%d"),)).fetchone()
    if row is None:
        return {"capacite": 0, "engagee": 0, "disponible": 0, "semaine": None}
    return {"capacite": row["capacite"], "engagee": row["engagee"], "disponible": row["capacite"] - row["engagee"],
            "semaine": row["semaine"]}


def executer_production(conn, aid: int, t: str, transfert_de: Optional[str], transfert_qte: int,
                        hausse_hebdo: int, semaines: int, acteur: str = "production") -> dict:
    a = _a(conn, aid)
    pays = a["pays"]
    transfert_qte, hausse_hebdo, semaines = int(transfert_qte or 0), int(hausse_hebdo or 0), int(semaines or 0)
    if transfert_qte <= 0 and hausse_hebdo <= 0:
        raise ValueError("Indiquez un transfert de stock et/ou une hausse de production.")
    cap = capacite_disponible(conn, t)
    if hausse_hebdo > cap["disponible"]:
        raise TransitionInvalide("Capacité Samsung Display insuffisante : %d écrans/semaine disponibles (fournisseur "
                                 "unique de l'écran pliable)." % cap["disponible"])
    actions = []
    if transfert_qte > 0:
        if not transfert_de or transfert_de == pays:
            raise ValueError("Choisissez un pays d'origine différent.")
        dispo_origine = offre_sortie(conn, transfert_de, t) - precommandes_pays(conn, transfert_de, t)
        if transfert_qte > max(0, dispo_origine):
            raise TransitionInvalide("Le pays d'origine ne dispose que de %d unités non réservées." % max(0, dispo_origine))
        _lots(conn, pays, transfert_qte, "2026-10-23T08:00:00", "Transfert depuis %s (P1-T11)" %
              PAYS_LIBELLE[transfert_de], t)
        conn.execute("INSERT INTO lots_production(pays, capacite, coloris, quantite, disponible_le, origine, cree_le, demo) "
                     "VALUES (?,?,?,?,?,?,?,1)", (transfert_de, None, None, -transfert_qte, "2026-10-23T08:00:00",
                                                  "Transfert vers %s (P1-T11)" % PAYS_LIBELLE[pays], t))
        actions.append("transfert de %d unités depuis %s" % (transfert_qte, PAYS_LIBELLE[transfert_de]))
    if hausse_hebdo > 0 and semaines > 0:
        debut = parse("2026-10-30T08:00:00")
        while debut <= parse(t):
            debut += timedelta(days=7)
        for k in range(semaines):
            _lots(conn, pays, hausse_hebdo, fmt(debut + timedelta(days=7 * k)), "Hausse de production (P1-T11)", t)
        conn.execute("UPDATE capacites_fournisseurs SET engagee = engagee + ? WHERE fournisseur='Samsung Display' "
                     "AND semaine >= ? ", (hausse_hebdo, (parse(t) - timedelta(days=6)).strftime("%Y-%m-%d")))
        conn.execute("INSERT INTO commandes_fournisseurs(fournisseur, composant, quantite, semaine, statut, cree_le, demo) "
                     "VALUES (?,?,?,?,?,?,1)", ("Samsung Display", "Écran pliable OLED", hausse_hebdo * semaines,
                                                (debut - timedelta(days=11)).strftime("%Y-%m-%d"), "envoyée", t))
        actions.append("+%d unités / semaine pendant %d semaines" % (hausse_hebdo, semaines))
        emettre(conn, "FE-04A", "Commande complémentaire : %d écrans pliables (%d / semaine)" %
                (hausse_hebdo * semaines, hausse_hebdo), t, processus="P1", noeud="T11",
                instance_id=a["instance_id"], lien="/a/fournisseur/portail", demo=1)
    texte = " ; ".join(actions)
    enregistrer(conn, a["instance_id"], "T11", t, acteur, details=texte)
    conn.execute("UPDATE analyses SET action=? WHERE id=?", (texte, aid))
    emettre(conn, "FI-05", "Volumes disponibles mis à jour pour %s : %s" % (PAYS_LIBELLE[pays], texte), t,
            processus="P1", noeud="T11", instance_id=a["instance_id"], lien="/a/dir_marketing/pilotage-precommandes",
            demo=1)
    return detail(conn, aid, t)


def _lots(conn, pays: str, quantite: int, date: str, origine: str, t: str) -> None:
    if pays == "FR":
        for cap, pc in MIX_CAP.items():
            for col, pk in MIX_COL.items():
                q = int(round(quantite * pc * pk))
                if q:
                    conn.execute("INSERT INTO lots_production(pays, capacite, coloris, quantite, disponible_le, origine, "
                                 "cree_le, demo) VALUES (?,?,?,?,?,?,?,1)", (pays, cap, col, q, date, origine, t))
    else:
        conn.execute("INSERT INTO lots_production(pays, capacite, coloris, quantite, disponible_le, origine, cree_le, demo) "
                     "VALUES (?,?,?,?,?,?,?,1)", (pays, None, None, quantite, date, origine, t))


# --------------------------------------------------------------------------- T12 (marketing)
def relancer(conn, aid: int, t: str, levier: str, message: str, declencher_campagne: bool = True,
             acteur: str = "dir_marketing") -> dict:
    a = _a(conn, aid)
    if not message.strip():
        raise ValueError("Décrivez le message de relance.")
    enregistrer(conn, a["instance_id"], "T12", t, acteur, details="%s : %s" % (levier, message[:150]))
    conn.execute("UPDATE analyses SET action=? WHERE id=?", ("%s : %s" % (levier, message[:200]), aid))
    emettre(conn, "FE-07A", "Brief de relance (%s) : %s" % (PAYS_LIBELLE[a["pays"]], message[:150]), t, processus="P1",
            noeud="T12", instance_id=a["instance_id"], lien="/a/agence/portail", demo=1)
    emettre(conn, "FE-01A", "Nouvelle offre diffusée aux prospects : %s" % levier, t, processus="P1", noeud="T12",
            instance_id=a["instance_id"], notifier=False, demo=1)
    resultat = detail(conn, aid, t)
    if declencher_campagne:
        camp = svc_campagnes.creer_campagne(conn, t, "Relance — %s (%s)" % (levier, PAYS_LIBELLE[a["pays"]]),
                                            a["pays"], declencheur="P1-T12 : relance de la communication "
                                                                   "(analyse #%d)" % aid, acteur=acteur)
        emettre(conn, "FM-08", "Nouvelle campagne de relance à préparer : %s" % camp["nom"], t, processus="P2",
                noeud="T01", instance_id=camp["instance_id"], lien="/a/dir_marketing/campagne?c=%d" % camp["id"],
                recepteur="dir_marketing", demo=1)
        resultat["campagne_creee"] = camp["id"]
    return resultat


# --------------------------------------------------------------------------- lecture
def _a(conn, aid: int):
    row = conn.execute("SELECT * FROM analyses WHERE id=?", (aid,)).fetchone()
    if row is None:
        raise KeyError("Analyse introuvable")
    return row


def detail(conn, aid: int, t: str) -> dict:
    a = _a(conn, aid)
    etat = charger_etat(conn, a["instance_id"], t)
    evts = [dict(r) for r in conn.execute("SELECT noeud, issue, acteur, horodatage, details FROM evenements "
                                          "WHERE instance_id=? AND horodatage <= ? ORDER BY horodatage, id",
                                          (a["instance_id"], t))]
    d = dict(a)
    d.update(etat=etat.dict(), evenements=evts, libelle_pays=PAYS_LIBELLE[a["pays"]])
    if not any(e["noeud"] == "G03" for e in evts):
        d["decision"] = None
    if not any(e["noeud"] in ("T11", "T12") for e in evts):
        d["action"] = None
    return d


def liste(conn, t: str, limite: int = 20) -> List[dict]:
    rows = conn.execute("SELECT id FROM analyses WHERE horodatage <= ? ORDER BY horodatage DESC LIMIT ?",
                        (t, limite)).fetchall()
    return [detail(conn, r["id"], t) for r in rows]
