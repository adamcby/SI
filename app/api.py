"""API JSON du SI. Chaque action vérifie que l'acteur courant a le droit d'exécuter la tâche
(contrôle d'accès par rôle, déduit des couloirs BPMN) puis émet les flux d'information."""
import json
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Request
from fastapi.responses import JSONResponse

from . import horloge
from .db import connecter, ecrire_parametre, lire_parametre
from .metier import CAPACITES, COLORIS, delais_catalogue, euros, chiffrer, libelle_delai, prochain_lot
from .moteur import TransitionInvalide, charger_etat
from .referentiel import ACTEURS, APPLE_STORES_FR, FLUX, PRODUIT, PROCESSUS, export_referentiel
from .seed_donnees import ETATS_REPRISE, MODES_PAIEMENT
from .services import campagnes as svc_camp
from .services import kpi as svc_kpi
from .services import lecture
from .services import pilotage as svc_pilot
from .services import portails as svc_portails
from .services import precommandes as svc_pc
from .bus import emettre

router = APIRouter(prefix="/api")


def get_conn():
    conn = connecter()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def maintenant(conn) -> str:
    return horloge.maintenant_iso(conn)


def autoriser(acteur: Optional[str], processus: str, noeud: str) -> str:
    d = PROCESSUS[processus]["noeuds"][noeud]
    autorises = d.get("acteurs", [])
    if acteur not in autorises:
        noms = ", ".join(ACTEURS[a]["nom"] for a in autorises)
        raise PermissionError("La tâche %s-%s « %s » relève de : %s. Changez de « Vue acteur »."
                              % (processus, noeud, d["libelle"].replace("\n", " "), noms))
    return acteur


def autoriser_acteurs(acteur: Optional[str], autorises: List[str]) -> str:
    if acteur not in autorises:
        raise PermissionError("Action réservée à : %s." % ", ".join(ACTEURS[a]["nom"] for a in autorises))
    return acteur


# =========================================================================== système
@router.get("/sante")
def sante(conn=Depends(get_conn)):
    return {"ok": True, "heure_simulee": maintenant(conn), "version": lire_parametre(conn, "version_schema")}


@router.get("/referentiel")
def referentiel():
    return export_referentiel()


@router.get("/horloge")
def get_horloge(conn=Depends(get_conn)):
    return horloge.etat(conn)


@router.post("/horloge")
def set_horloge(body: Dict[str, Any] = Body(...), conn=Depends(get_conn)):
    if body.get("mode") in ("pas_a_pas", "automatique"):
        ecrire_parametre(conn, "mode_execution", body["mode"])
    if body.get("preset") or body.get("date") or body.get("vitesse") is not None:
        horloge.regler(conn, date_iso=body.get("date"), vitesse=body.get("vitesse"), preset=body.get("preset"))
    return horloge.etat(conn)


@router.post("/demo/reinitialiser")
def reinitialiser():
    from .db import initialiser
    initialiser(forcer=True)
    conn = connecter()
    try:
        horloge.regler(conn, preset=horloge.PRESET_DEFAUT, vitesse=1)
        conn.commit()
    finally:
        conn.close()
    return {"ok": True, "message": "Base réinitialisée (données de démonstration effacées)."}


@router.get("/notifications")
def get_notifications(acteur: str, conn=Depends(get_conn)):
    return lecture.notifications(conn, acteur, maintenant(conn))


@router.post("/notifications/lues")
def post_lues(body: Dict[str, Any] = Body(...), conn=Depends(get_conn)):
    lecture.marquer_lues(conn, body.get("acteur", ""), maintenant(conn))
    return {"ok": True}


@router.get("/journal")
def get_journal(code: Optional[str] = None, acteur: Optional[str] = None, processus: Optional[str] = None,
                limite: int = Query(100, le=500), depuis_id: int = 0, conn=Depends(get_conn)):
    return lecture.journal(conn, maintenant(conn), code, acteur, processus, limite, depuis_id)


@router.get("/flux/stats")
def get_stats_flux(conn=Depends(get_conn)):
    return lecture.stats_flux(conn, maintenant(conn))


@router.get("/files")
def get_files(acteur: Optional[str] = None, conn=Depends(get_conn)):
    t = maintenant(conn)
    return lecture.file_acteur(conn, acteur, t) if acteur else lecture.files_de_travail(conn, t)


@router.get("/processus/{code}/jetons")
def get_jetons(code: str, conn=Depends(get_conn)):
    if code not in PROCESSUS:
        raise KeyError("Processus inconnu")
    return lecture.jetons_processus(conn, code, maintenant(conn))


@router.get("/processus/{code}/instances")
def get_instances(code: str, conn=Depends(get_conn)):
    return lecture.instances_processus(conn, code, maintenant(conn))


@router.get("/instances/{iid}")
def get_instance(iid: int, conn=Depends(get_conn)):
    t = maintenant(conn)
    inst = conn.execute("SELECT * FROM instances WHERE id=?", (iid,)).fetchone()
    if inst is None:
        raise KeyError("Instance introuvable")
    etat = charger_etat(conn, iid, t)
    evts = [dict(r) for r in conn.execute("SELECT * FROM evenements WHERE instance_id=? AND horodatage <= ? "
                                          "ORDER BY horodatage, id", (iid, t))]
    flux = [dict(r) for r in conn.execute("SELECT * FROM flux_log WHERE instance_id=? AND horodatage <= ? "
                                          "ORDER BY horodatage, id", (iid, t))]
    return {"instance": dict(inst), "etat": etat.dict(), "evenements": evts, "flux": flux}


# =========================================================================== client (P1 couloir client)
@router.get("/catalogue")
def catalogue(mode: str = "domicile", conn=Depends(get_conn)):
    t = maintenant(conn)
    prix = {c: chiffrer(c, False, conn)["prix_ttc"] for c in CAPACITES}
    return {
        "heure": t, "ouvert": t >= "2026-10-16T14:00:00", "produit": PRODUIT, "prix": prix,
        "delais": delais_catalogue(conn, t, mode),
        "reprise": [dict(r) for r in conn.execute("SELECT modele, marque, valeur FROM reprise_grille ORDER BY valeur DESC")],
        "etats_reprise": [{"id": e, "libelle": l, "facteur": f} for (e, l, f) in ETATS_REPRISE],
        "paiements": [{"id": k, "libelle": v} for k, v in MODES_PAIEMENT.items()],
        "magasins": APPLE_STORES_FR,
    }


@router.post("/me-prevenir")
def me_prevenir(body: Dict[str, Any] = Body(...), conn=Depends(get_conn)):
    t = maintenant(conn)
    email = (body.get("email") or "").strip()
    if "@" not in email:
        raise ValueError("Adresse e-mail invalide.")
    if t >= "2026-10-16T14:00:00":
        raise TransitionInvalide("Les précommandes sont ouvertes : rendez-vous dans le configurateur.")
    row = conn.execute("SELECT id FROM clients WHERE apple_id=?", (email,)).fetchone()
    if row:
        conn.execute("UPDATE clients SET me_prevenir_le=COALESCE(me_prevenir_le, ?), consentement_marketing=? WHERE id=?",
                     (t, 1 if body.get("consentement") else 0, row["id"]))
    else:
        conn.execute("INSERT INTO clients(apple_id, prenom, nom, segment, appareil, plateforme, me_prevenir_le, "
                     "consentement_marketing, source, cree_le, demo) VALUES (?,?,?,?,?,?,?,?,?,?,1)",
                     (email, (body.get("prenom") or "Prospect")[:40], (body.get("nom") or "")[:40], "Particulier",
                      body.get("appareil") or None, "Android" if "Samsung" in (body.get("appareil") or "") else "iOS",
                      t, 1 if body.get("consentement") else 0, "apple.com", t))
    conn.execute("INSERT INTO kpi_journalier(jour, pays, indicateur, valeur) VALUES (?,?,?,1) ON CONFLICT(jour, pays, "
                 "indicateur) DO UPDATE SET valeur = valeur + 1", (t[:10], "FR", "me_prevenir"))
    emettre(conn, "FE-01R", "Inscription « Me prévenir » : %s" % lecture.pseudonymiser(email), t,
            emetteur="client", recepteur="mkt_data", lien="/a/mkt_data/crm", demo=1)
    return {"ok": True, "message": "Merci ! Vous serez prévenu(e) de l'ouverture des précommandes."}


@router.post("/reprise/estimation")
def estimation(body: Dict[str, Any] = Body(...), conn=Depends(get_conn)):
    v = svc_pc.valeur_reprise(conn, body.get("modele"), body.get("etat"))
    return {"valeur": v, "libelle": euros(v), "flux": ["FE-10A", "FE-10R"]}


@router.post("/precommandes")
def post_precommande(body: Dict[str, Any] = Body(...), conn=Depends(get_conn)):
    autoriser(body.get("acteur"), "P1", "T01")
    t = maintenant(conn)
    p = svc_pc.creer_precommande(
        conn, t, capacite=body["capacite"], coloris=body["coloris"], paiement_mode=body["paiement_mode"],
        client=body.get("client") or {}, applecare=bool(body.get("applecare")),
        reprise_modele=body.get("reprise_modele") or None, reprise_etat=body.get("reprise_etat") or None,
        livraison_mode=body.get("livraison_mode") or "domicile", magasin=body.get("magasin") or None,
        canal="apple.com", simuler_refus=bool(body.get("simuler_refus")), demo=1)
    return detail_precommande(conn, p["id"], t)


def detail_precommande(conn, pid: int, t: str) -> dict:
    p = conn.execute("SELECT p.*, c.prenom, c.nom, c.apple_id, c.appareil, c.plateforme, c.ville FROM precommandes p "
                     "LEFT JOIN clients c ON c.id = p.client_id WHERE p.id=?", (pid,)).fetchone()
    if p is None:
        raise KeyError("Précommande introuvable")
    d = dict(p)
    d["apple_id"] = lecture.pseudonymiser(d.get("apple_id") or "")
    d["libelle_config"] = "iPhone Duo %s %s" % (CAPACITES[p["capacite"]]["libelle"], COLORIS[p["coloris"]]["libelle"])
    d["statut_libelle"] = svc_pc.STATUTS.get(p["statut"], (p["statut"], None))[0]
    d["etat_bpmn"] = svc_pc.etat_bpmn(conn, pid, t)
    d["chronologie"] = svc_pc.chronologie(conn, pid, t)
    d["credit"] = dict(conn.execute("SELECT * FROM demandes_credit WHERE precommande_id=?", (pid,)).fetchone() or {}) or None
    d["paiement_libelle"] = MODES_PAIEMENT.get(p["paiement_mode"], p["paiement_mode"])
    if p["statut"] == "confirmee" and p["livraison_prevue"] and p["livraison_prevue"] <= t[:10]:
        d["statut_libelle"] = "Livrée" if p["livraison_mode"] == "domicile" else "Retirée en magasin"
    d["flux"] = [dict(r) for r in conn.execute("SELECT code, objet, horodatage, emetteur, recepteur FROM flux_log WHERE "
                                               "instance_id=? AND horodatage <= ? ORDER BY id",
                                               (p["instance_id"], t))] if p["instance_id"] else []
    return d


@router.get("/precommandes")
def list_precommandes(statut: Optional[str] = None, q: Optional[str] = None, limite: int = Query(50, le=200),
                      demo: Optional[int] = None, conn=Depends(get_conn)):
    t = maintenant(conn)
    sql = ("SELECT p.id, p.reference, p.capacite, p.coloris, p.prix_ttc, p.statut, p.paiement_mode, p.paiement_statut, "
           "p.delai_affiche, p.livraison_prevue, p.cree_le, p.maj_le, p.motif, p.demo, p.instance_id, p.reprise_valeur, "
           "p.applecare, p.ca_previsionnel_ht, p.marge, p.delai_allonge, p.canal, c.prenom, c.nom, c.ville, c.plateforme, "
           "c.appareil, c.apple_id FROM precommandes p LEFT JOIN clients c ON c.id=p.client_id WHERE p.cree_le <= ?")
    args: list = [t]
    if statut:
        statuts = statut.split(",")
        sql += " AND p.statut IN (%s)" % ",".join("?" * len(statuts))
        args += statuts
    if q:
        sql += " AND (p.reference LIKE ? OR c.nom LIKE ? OR c.ville LIKE ?)"
        args += ["%" + q + "%"] * 3
    if demo is not None:
        sql += " AND p.demo = ?"
        args.append(demo)
    sql += " ORDER BY p.cree_le DESC, p.id DESC LIMIT ?"
    args.append(limite)
    out = []
    for r in conn.execute(sql, args):
        d = dict(r)
        d["apple_id"] = lecture.pseudonymiser(d.get("apple_id") or "")
        d["nom"] = (d.get("nom") or "")[:1] + "."
        d["libelle_config"] = "%s %s" % (CAPACITES[r["capacite"]]["libelle"], COLORIS[r["coloris"]]["libelle"])
        d["statut_libelle"] = svc_pc.STATUTS.get(r["statut"], (r["statut"], None))[0]
        d["tache"] = svc_pc.STATUTS.get(r["statut"], (None, None))[1]
        if r["statut"] in ("payee", "a_reserver", "delai_a_allonger"):
            d["stock"] = prochain_lot(conn, r["capacite"], r["coloris"], t)
        out.append(d)
    return out


@router.get("/clients/{cid}/export")
def export_client(cid: int, conn=Depends(get_conn)):
    """Droit d'accès (RGPD, art. 15) : toutes les données du client, au format JSON."""
    t = maintenant(conn)
    c = conn.execute("SELECT * FROM clients WHERE id=?", (cid,)).fetchone()
    if c is None:
        raise KeyError("Client introuvable")
    pcs = [dict(r) for r in conn.execute("SELECT reference, capacite, coloris, prix_ttc, statut, delai_affiche, cree_le "
                                         "FROM precommandes WHERE client_id=? AND cree_le <= ?", (cid, t))]
    return {"responsable_du_traitement": "Apple (maquette pédagogique)", "finalites": [
        "Gestion des précommandes", "Information sur l'ouverture des précommandes (« Me prévenir »)",
        "Communications marketing (si consentement)"], "donnees": dict(c), "precommandes": pcs,
        "droits": "Accès, rectification, effacement, opposition, portabilité — délai de réponse : 1 mois."}


@router.post("/clients/{cid}/consentement")
def consentement_client(cid: int, body: Dict[str, Any] = Body(...), conn=Depends(get_conn)):
    autoriser_acteurs(body.get("acteur"), ["client"])
    t = maintenant(conn)
    v = 1 if body.get("consentement") else 0
    if not conn.execute("UPDATE clients SET consentement_marketing=? WHERE id=?", (v, cid)).rowcount:
        raise KeyError("Client introuvable")
    emettre(conn, "FE-01R", "Préférence de consentement marketing mise à jour (%s)" % ("accepté" if v else "retiré"), t,
            emetteur="client", recepteur="mkt_data", demo=1)
    return {"ok": True, "message": "Préférence enregistrée dans le CRM (consentement %s)." % ("accordé" if v else "retiré")}


@router.get("/precommandes/{ref}")
def get_precommande(ref: str, conn=Depends(get_conn)):
    t = maintenant(conn)
    row = conn.execute("SELECT id FROM precommandes WHERE reference=? OR CAST(id AS TEXT)=?", (ref, ref)).fetchone()
    if row is None:
        raise KeyError("Précommande introuvable")
    return detail_precommande(conn, row["id"], t)


@router.post("/precommandes/{pid}/reprendre")
def post_reprendre(pid: int, body: Dict[str, Any] = Body(...), conn=Depends(get_conn)):
    autoriser(body.get("acteur"), "P1", "T01")
    t = maintenant(conn)
    svc_pc.reprendre(conn, pid, t, body["capacite"], body["coloris"], body["paiement_mode"],
                     simuler_refus=bool(body.get("simuler_refus")))
    return detail_precommande(conn, pid, t)


@router.post("/precommandes/{pid}/paiement")
def post_paiement(pid: int, body: Dict[str, Any] = Body(...), conn=Depends(get_conn)):
    autoriser(body.get("acteur"), "P1", "G01")
    t = maintenant(conn)
    if body.get("issue") not in ("oui", "non"):
        raise ValueError("Issue attendue : oui ou non.")
    svc_pc.decision_paiement(conn, pid, body["issue"], t, acteur=body["acteur"], commentaire=body.get("commentaire", ""))
    return detail_precommande(conn, pid, t)


@router.post("/precommandes/{pid}/stock")
def post_stock(pid: int, body: Dict[str, Any] = Body(...), conn=Depends(get_conn)):
    autoriser(body.get("acteur"), "P1", "G02")
    t = maintenant(conn)
    r = svc_pc.verifier_stock(conn, pid, t, acteur=body["acteur"])
    d = detail_precommande(conn, pid, t)
    d["issue"] = r["issue"]
    return d


@router.post("/precommandes/{pid}/delai")
def post_delai(pid: int, body: Dict[str, Any] = Body(...), conn=Depends(get_conn)):
    autoriser(body.get("acteur"), "P1", "T07")
    t = maintenant(conn)
    svc_pc.allonger_delai(conn, pid, t, acteur=body["acteur"])
    return detail_precommande(conn, pid, t)


@router.post("/precommandes/{pid}/reserver")
def post_reserver(pid: int, body: Dict[str, Any] = Body(...), conn=Depends(get_conn)):
    autoriser(body.get("acteur"), "P1", "T08")
    t = maintenant(conn)
    svc_pc.reserver(conn, pid, t, acteur=body["acteur"])
    return detail_precommande(conn, pid, t)


@router.post("/credits/{did}")
def post_credit(did: int, body: Dict[str, Any] = Body(...), conn=Depends(get_conn)):
    autoriser_acteurs(body.get("acteur"), ["organisme_financier"])
    t = maintenant(conn)
    p = svc_pc.decision_credit(conn, did, body.get("decision"), t)
    return detail_precommande(conn, p["id"], t)


# =========================================================================== CRM (équipe data)
SEGMENTS = {
    "iphone_3ans": ("Possesseurs d'un iPhone de plus de 3 ans", "plateforme='iOS' AND appareil_annee <= 2023"),
    "android": ("Utilisateurs Android (dont pliables)", "plateforme='Android'"),
    "android_pliable": ("Android équipés d'un pliable", "plateforme='Android' AND (appareil LIKE '%Fold%' OR appareil LIKE '%Flip%' OR appareil LIKE '%Mate X%')"),
    "inscrits_sans_pc": ("Inscrits « Me prévenir » sans précommande", "me_prevenir_le IS NOT NULL AND id NOT IN (SELECT client_id FROM precommandes WHERE client_id IS NOT NULL)"),
    "consentants": ("Clients ayant consenti au marketing", "consentement_marketing = 1"),
    "createurs": ("Créatifs et professionnels", "segment = 'Créatif / professionnel'"),
}


@router.get("/crm/segments")
def crm_segments(conn=Depends(get_conn)):
    t = maintenant(conn)
    total = conn.execute("SELECT COUNT(*) FROM clients WHERE cree_le <= ?", (t,)).fetchone()[0]
    out = []
    for code, (lib, cond) in SEGMENTS.items():
        n = conn.execute("SELECT COUNT(*) FROM clients WHERE cree_le <= ? AND " + cond, (t,)).fetchone()[0]
        nc = conn.execute("SELECT COUNT(*) FROM clients WHERE cree_le <= ? AND consentement_marketing=1 AND " + cond,
                          (t,)).fetchone()[0]
        out.append({"code": code, "libelle": lib, "clients": n, "ciblables": nc})
    me = conn.execute("SELECT COUNT(*) FROM clients WHERE me_prevenir_le IS NOT NULL AND me_prevenir_le <= ?", (t,)).fetchone()[0]
    cons = conn.execute("SELECT AVG(consentement_marketing) FROM clients WHERE cree_le <= ?", (t,)).fetchone()[0] or 0
    pcs = conn.execute("SELECT COUNT(*) FROM precommandes WHERE crm_le IS NOT NULL AND crm_le <= ?", (t,)).fetchone()[0]
    return {"total": total, "me_prevenir": me, "taux_consentement": round(100 * cons, 1), "precommandes_crm": pcs,
            "segments": out}


@router.get("/crm/clients")
def crm_clients(q: Optional[str] = None, segment: Optional[str] = None, limite: int = Query(25, le=100),
                conn=Depends(get_conn)):
    t = maintenant(conn)
    sql = ("SELECT c.*, (SELECT COUNT(*) FROM precommandes p WHERE p.client_id=c.id AND p.cree_le <= ?) AS nb_pc "
           "FROM clients c WHERE c.cree_le <= ?")
    args: list = [t, t]
    if segment in SEGMENTS:
        sql += " AND " + SEGMENTS[segment][1].replace("id NOT IN", "c.id NOT IN")
    if q:
        sql += " AND (c.nom LIKE ? OR c.ville LIKE ? OR c.appareil LIKE ?)"
        args += ["%" + q + "%"] * 3
    sql += " ORDER BY c.cree_le DESC LIMIT ?"
    args.append(limite)
    out = []
    for r in conn.execute(sql, args):
        d = dict(r)
        d["apple_id"] = lecture.pseudonymiser(d["apple_id"])
        d["nom"] = d["nom"][:1] + "."
        out.append(d)
    return out


@router.post("/crm/diffusion")
def crm_diffusion(body: Dict[str, Any] = Body(...), conn=Depends(get_conn)):
    """Flux sortants de l'équipe data : ciblage (FM-15), précommandes par pays (FM-19), coût par précommande (FM-18)."""
    autoriser_acteurs(body.get("acteur"), ["mkt_data"])
    t = maintenant(conn)
    code = body.get("code")
    if code == "FM-15":
        seg = SEGMENTS.get(body.get("segment"), ("Segment", ""))[0]
        emettre(conn, "FM-15", "Ciblage des audiences : %s" % seg, t, emetteur="mkt_data", recepteur="mkt_social",
                lien="/a/mkt_social/campagne", demo=1)
    elif code == "FM-19":
        tab = svc_pilot.tableau(conn, t)
        txt = ", ".join("%s %s" % (l["pays"], "{:,}".format(l["precommandes"]).replace(",", " ")) for l in tab[:5])
        emettre(conn, "FM-19", "Précommandes par pays : %s…" % txt, t, emetteur="mkt_data", recepteur="production",
                lien="/a/production/plan", demo=1)
    elif code == "FM-18":
        k = svc_kpi.kpi_finance(conn, t)
        emettre(conn, "FM-18", "Coût par précommande : %s" % euros(k["cout_par_precommande"] or 0, 2), t,
                emetteur="mkt_data", recepteur="finance", lien="/a/finance/budgets", demo=1)
    elif code == "FM-17":
        h = svc_kpi.tableau_hebdomadaire(conn, t)
        emettre(conn, "FM-17", "Tableau de bord hebdomadaire : %s objectif(s) atteint(s) sur %s" %
                (h.get("atteints", 0), h.get("total", 7)), t, emetteur="mkt_data", recepteur="dir_marketing",
                lien="/a/dir_marketing/cockpit", demo=1)
    else:
        raise ValueError("Flux non géré")
    return {"ok": True, "message": "Flux %s émis." % code}


# =========================================================================== pilotage P1 (T10 -> T12)
@router.get("/pilotage")
def get_pilotage(conn=Depends(get_conn)):
    t = maintenant(conn)
    return {"tableau": svc_pilot.tableau(conn, t), "en_attente": svc_pilot.en_attente_analyse(conn, t),
            "analyses": svc_pilot.liste(conn, t), "capacite": svc_pilot.capacite_disponible(conn, t)}


@router.post("/pilotage/analyses")
def post_analyse(body: Dict[str, Any] = Body(...), conn=Depends(get_conn)):
    autoriser(body.get("acteur"), "P1", "T10")
    return svc_pilot.lancer_analyse(conn, body.get("pays", "FR"), maintenant(conn), acteur=body["acteur"])


@router.post("/pilotage/analyses/{aid}/decision")
def post_decision_analyse(aid: int, body: Dict[str, Any] = Body(...), conn=Depends(get_conn)):
    autoriser(body.get("acteur"), "P1", "G03")
    return svc_pilot.decider(conn, aid, body.get("issue"), maintenant(conn), body.get("commentaire", ""),
                             acteur=body["acteur"])


@router.post("/pilotage/analyses/{aid}/production")
def post_production(aid: int, body: Dict[str, Any] = Body(...), conn=Depends(get_conn)):
    autoriser(body.get("acteur"), "P1", "T11")
    return svc_pilot.executer_production(conn, aid, maintenant(conn), body.get("transfert_de"),
                                         body.get("transfert_qte", 0), body.get("hausse_hebdo", 0),
                                         body.get("semaines", 0), acteur=body["acteur"])


@router.post("/pilotage/analyses/{aid}/relance")
def post_relance(aid: int, body: Dict[str, Any] = Body(...), conn=Depends(get_conn)):
    autoriser(body.get("acteur"), "P1", "T12")
    return svc_pilot.relancer(conn, aid, maintenant(conn), body.get("levier", "Offre"), body.get("message", ""),
                              bool(body.get("declencher_campagne", True)), acteur=body["acteur"])


# =========================================================================== campagnes P2
@router.get("/campagnes")
def get_campagnes(conn=Depends(get_conn)):
    return svc_camp.liste(conn, maintenant(conn))


@router.get("/campagnes/{cid}")
def get_campagne(cid: int, conn=Depends(get_conn)):
    t = maintenant(conn)
    d = svc_camp.detail(conn, cid, t)
    d["catalogue_influenceurs"] = [dict(r) for r in conn.execute("SELECT * FROM influenceurs ORDER BY abonnes DESC")]
    d["appareils_disponibles"] = conn.execute("SELECT COUNT(*) FROM appareils_test WHERE statut='disponible'").fetchone()[0]
    d["videos_suggerees"] = [{"titre": a, "concept": b} for a, b in svc_camp.VIDEOS_SUGGEREES]
    d["canaux_defaut"] = [{"canal": a, "montant": b} for a, b in svc_camp.CANAUX_DEFAUT]
    return d


@router.post("/campagnes")
def post_campagne(body: Dict[str, Any] = Body(...), conn=Depends(get_conn)):
    autoriser(body.get("acteur"), "P2", "T01")
    t = maintenant(conn)
    nom = (body.get("nom") or "Campagne TikTok — démonstration").strip()[:90]
    c = svc_camp.creer_campagne(conn, t, nom, body.get("pays", "FR"),
                                declencheur=body.get("declencheur") or "Keynote du 9/09 (rejouée)")
    return svc_camp.detail(conn, c["id"], t)


ACTIONS_P2 = {
    "proposition": ("T01", lambda c, cid, t, b: svc_camp.proposer(c, cid, t, b.get("lignes", []), b.get("objectifs"), b["acteur"])),
    "validation": ("G01", lambda c, cid, t, b: svc_camp.valider_budget(c, cid, t, b.get("issue"), b.get("commentaire", ""), b["acteur"])),
    "publication": ("T02", lambda c, cid, t, b: svc_camp.publier_videos(c, cid, t, b.get("videos", []), b["acteur"])),
    "influenceurs": ("T03", lambda c, cid, t, b: svc_camp.selectionner_influenceurs(c, cid, t, b.get("ids", []), b["acteur"])),
    "appareils": ("T04", lambda c, cid, t, b: svc_camp.fournir_appareils(c, cid, t, b["acteur"])),
    "mesure": ("T06", lambda c, cid, t, b: svc_camp.mesurer(c, cid, t, b["acteur"])),
    "decision": ("G02", lambda c, cid, t, b: svc_camp.decider_objectifs(c, cid, t, b.get("issue"), b.get("commentaire", ""), b["acteur"])),
    "ajustement": ("T07", lambda c, cid, t, b: svc_camp.ajuster(c, cid, t, b.get("ciblage", ""), b.get("message", ""), b["acteur"])),
    "rapport": ("T08", lambda c, cid, t, b: svc_camp.envoyer_rapport(c, cid, t, b.get("previsions", {}), b.get("synthese", ""), b["acteur"])),
    "plan": ("T09", lambda c, cid, t, b: svc_camp.ajuster_plan(c, cid, t, b.get("coloris", "noir"), b.get("quantite", 0), b["acteur"])),
    "cac": ("T10", lambda c, cid, t, b: svc_camp.calculer_cac(c, cid, t, b["acteur"])),
}


@router.post("/campagnes/{cid}/{action}")
def post_action_campagne(cid: int, action: str, body: Dict[str, Any] = Body(...), conn=Depends(get_conn)):
    if action == "avis":
        autoriser(body.get("acteur"), "P2", "T05")
        t = maintenant(conn)
        svc_camp.publier_avis(conn, cid, int(body["influenceur_id"]), t, body.get("titre", ""),
                              float(body.get("sentiment") or 70))
        return svc_camp.detail(conn, cid, t)
    if action not in ACTIONS_P2:
        raise KeyError("Action inconnue")
    noeud, fn = ACTIONS_P2[action]
    autoriser(body.get("acteur"), "P2", noeud)
    t = maintenant(conn)
    fn(conn, cid, t, body)
    return svc_camp.detail(conn, cid, t)


# =========================================================================== KPI
@router.get("/kpi/marketing")
def kpi_marketing(conn=Depends(get_conn)):
    return svc_kpi.cockpit_marketing(conn, maintenant(conn))


@router.get("/kpi/hebdo")
def kpi_hebdo(conn=Depends(get_conn)):
    return svc_kpi.tableau_hebdomadaire(conn, maintenant(conn))


@router.get("/kpi/finance")
def kpi_finance(conn=Depends(get_conn)):
    return svc_kpi.kpi_finance(conn, maintenant(conn))


@router.get("/kpi/production")
def kpi_production(conn=Depends(get_conn)):
    return svc_kpi.kpi_production(conn, maintenant(conn))


@router.get("/kpi/dg")
def kpi_dg(conn=Depends(get_conn)):
    return svc_kpi.kpi_dg(conn, maintenant(conn))


# =========================================================================== direction générale / consignes
@router.post("/plans/{pid}/decision")
def post_plan_decision(pid: int, body: Dict[str, Any] = Body(...), conn=Depends(get_conn)):
    autoriser_acteurs(body.get("acteur"), ["dg"])
    t = maintenant(conn)
    issue = body.get("issue")
    if issue not in ("valide", "refuse"):
        raise ValueError("Décision invalide")
    plan = conn.execute("SELECT * FROM plans_lancement WHERE id=?", (pid,)).fetchone()
    if plan is None:
        raise KeyError("Plan introuvable")
    if plan["statut"] != "soumis":
        raise TransitionInvalide("Ce plan a déjà été traité.")
    conn.execute("UPDATE plans_lancement SET statut=?, decide_le=?, commentaire=? WHERE id=?",
                 (issue, t, body.get("commentaire", "")[:300], pid))
    emettre(conn, "FI-01", "%s : %s" % ("Lancement validé" if issue == "valide" else "Plan à revoir", plan["titre"]), t,
            emetteur="dg", recepteur="dir_marketing", lien="/a/dir_marketing/campagne", demo=1)
    return {"ok": True}


@router.post("/plans")
def post_plan(body: Dict[str, Any] = Body(...), conn=Depends(get_conn)):
    autoriser_acteurs(body.get("acteur"), ["dir_marketing"])
    t = maintenant(conn)
    titre = (body.get("titre") or "").strip()
    if not titre:
        raise ValueError("Titre obligatoire")
    contenu = {"pays": body.get("pays", ["FR"]), "budget": body.get("budget"), "messages": body.get("messages", [])}
    conn.execute("INSERT INTO plans_lancement(titre, pays, contenu, soumis_le, statut, demo) VALUES (?,?,?,?,?,1)",
                 (titre[:120], ",".join(contenu["pays"]) if isinstance(contenu["pays"], list) else contenu["pays"],
                  json.dumps(contenu), t, "soumis"))
    emettre(conn, "FI-02", "Plan de lancement soumis : %s" % titre[:120], t, emetteur="dir_marketing", recepteur="dg",
            lien="/a/dg/pilotage", demo=1)
    return {"ok": True}


@router.post("/objectifs-marge")
def post_objectif(body: Dict[str, Any] = Body(...), conn=Depends(get_conn)):
    autoriser_acteurs(body.get("acteur"), ["dg"])
    t = maintenant(conn)
    taux = float(body.get("taux"))
    if not 30 <= taux <= 70:
        raise ValueError("Taux de marge attendu entre 30 et 70 %.")
    conn.execute("INSERT INTO objectifs_marge(taux, defini_le, commentaire, demo) VALUES (?,?,?,1)",
                 (taux, t, body.get("commentaire", "")[:300]))
    emettre(conn, "FI-03", "Nouvel objectif de marge brute : %s %%" % str(taux).replace(".", ","), t, emetteur="dg",
            recepteur="finance", lien="/a/finance/budgets", demo=1)
    return {"ok": True}


CONSIGNES = {"FM-05": "mkt_presse", "FM-06": "mkt_ecommerce", "FM-07": "mkt_creation", "FM-08": "mkt_social",
             "FM-09": "mkt_retail", "FI-15": "ingenierie", "FI-16": "juridique"}


@router.post("/consignes")
def post_consigne(body: Dict[str, Any] = Body(...), conn=Depends(get_conn)):
    autoriser_acteurs(body.get("acteur"), ["dir_marketing"])
    code = body.get("code")
    if code not in CONSIGNES:
        raise ValueError("Consigne inconnue")
    t = maintenant(conn)
    msg = (body.get("message") or FLUX[code]["libelle"]).strip()[:200]
    if code == "FI-16":
        conn.execute("INSERT INTO validations_juridiques(objet, type, demandeur, statut, cree_le, demo) VALUES "
                     "(?,?,?,?,?,1)", (msg, "message publicitaire", "dir_marketing", "en_attente", t))
    if code == "FM-07":
        conn.execute("INSERT INTO contenus_creation(type, titre, statut, destinataire, brief_le, demo) VALUES "
                     "(?,?,?,?,?,1)", ("Vidéo TikTok", msg[:80], "en_production", "mkt_social", t))
    emettre(conn, code, msg, t, emetteur="dir_marketing", recepteur=CONSIGNES[code], demo=1)
    return {"ok": True, "message": "Consigne envoyée (flux %s)." % code}


@router.post("/finance/budget-production")
def post_budget_production(body: Dict[str, Any] = Body(...), conn=Depends(get_conn)):
    autoriser_acteurs(body.get("acteur"), ["finance"])
    t = maintenant(conn)
    m = float(body.get("montant") or 0)
    if m <= 0:
        raise ValueError("Montant invalide")
    conn.execute("INSERT INTO budgets_production(montant, motif, accorde_le, demo) VALUES (?,?,?,1)",
                 (m, (body.get("motif") or "Budget complémentaire")[:200], t))
    emettre(conn, "FI-09", "Budget de production accordé : %s" % euros(m), t, emetteur="finance",
            recepteur="production", lien="/a/production/plan", demo=1)
    return {"ok": True}


@router.post("/production/cout-revient")
def post_cout_revient(body: Dict[str, Any] = Body(...), conn=Depends(get_conn)):
    autoriser_acteurs(body.get("acteur"), ["production"])
    t = maintenant(conn)
    comp = body.get("composant")
    cout = float(body.get("cout") or 0)
    if cout <= 0:
        raise ValueError("Coût invalide")
    n = conn.execute("UPDATE couts_revient SET cout_reel=?, maj_le=? WHERE composant=?", (cout, t, comp)).rowcount
    if not n:
        raise KeyError("Composant inconnu")
    emettre(conn, "FI-08", "Coût de revient actualisé — %s : %s" % (comp, euros(cout)), t, emetteur="production",
            recepteur="finance", lien="/a/finance/budgets", demo=1)
    return {"ok": True}


# =========================================================================== portails
@router.get("/portails/{acteur}")
def get_portail(acteur: str, conn=Depends(get_conn)):
    return svc_portails.donnees(conn, acteur, maintenant(conn))


@router.post("/portails/{acteur}/{code}")
def post_portail(acteur: str, code: str, body: Dict[str, Any] = Body(...), conn=Depends(get_conn)):
    if body.get("acteur") != acteur:
        raise PermissionError("Action réservée à : %s. Changez de « Vue acteur »." % ACTEURS[acteur]["nom"])
    msg = svc_portails.executer(conn, acteur, code, maintenant(conn), body.get("donnees") or {})
    return {"ok": True, "message": msg}


# =========================================================================== SI partagé
@router.get("/si/tables")
def get_tables(conn=Depends(get_conn)):
    return lecture.tables_si(conn)


@router.get("/si/tables/{table}")
def get_table(table: str, conn=Depends(get_conn)):
    return lecture.apercu_table(conn, table)


# =========================================================================== gestion d'erreurs
def installer_gestion_erreurs(app):
    @app.exception_handler(TransitionInvalide)
    async def _ti(request: Request, exc: TransitionInvalide):
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @app.exception_handler(PermissionError)
    async def _pe(request: Request, exc: PermissionError):
        return JSONResponse(status_code=403, content={"detail": str(exc)})

    @app.exception_handler(ValueError)
    async def _ve(request: Request, exc: ValueError):
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    @app.exception_handler(KeyError)
    async def _ke(request: Request, exc: KeyError):
        return JSONResponse(status_code=404, content={"detail": str(exc).strip("'\"")})
