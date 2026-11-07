"""Processus P2 — campagne TikTok et mesure de son efficacité (Fig. 5)."""
import json
from datetime import timedelta
from typing import Dict, List, Optional

from ..bus import emettre
from ..db import lire_parametre
from ..horloge import fmt, parse
from ..metier import CAPACITES, COLORIS, courbe_vues, euros
from ..moteur import TransitionInvalide, charger_etat, creer_instance, enregistrer

OBJECTIFS_DEFAUT = {"vues_tiktok": 8000000, "sentiment": 60, "mentions": 120000, "me_prevenir": 20000, "intention": 7}
CANAUX_DEFAUT = [("TikTok Ads", 220000), ("Influence", 140000), ("Production de contenus", 60000),
                 ("Études et social listening", 20000)]
VIDEOS_SUGGEREES = [
    ("L'iPhone Duo fait son yoga", "Positions posé, relevé, ouvert"),
    ("Un mini-portable en terrasse", "Usage bureau nomade au café"),
    ("Ce soir, cinéma de poche", "Grand écran pour les séries"),
    ("Votre ancien téléphone vaut de l'or", "Offre de reprise Apple Trade In"),
    ("Passer d'Android en 5 minutes", "Conversion des utilisateurs Android"),
]


def _camp(conn, cid: int):
    row = conn.execute("SELECT * FROM campagnes WHERE id = ?", (cid,)).fetchone()
    if row is None:
        raise KeyError("Campagne %s introuvable" % cid)
    return row


def _fx(conn, code, objet, t, camp, noeud, **kw):
    return emettre(conn, code, objet, t, processus="P2", noeud=noeud, instance_id=camp["instance_id"],
                   demo=camp["demo"], **kw)


def _lien(cid):
    return "/a/mkt_social/campagne?c=%d" % cid


# --------------------------------------------------------------------------- démarrage
def creer_campagne(conn, t: str, nom: str, pays: str = "FR", declencheur: str = "Keynote du 9/09",
                   acteur: str = "dir_marketing", demo: int = 1) -> dict:
    inst = creer_instance(conn, "P2", "campagne", nom, t, acteur, declencheur=declencheur, demo=demo)
    cur = conn.execute("INSERT INTO campagnes(instance_id, nom, pays, declencheur, objectifs, statut, cree_le, demo) "
                       "VALUES (?,?,?,?,?,?,?,?)",
                       (inst, nom, pays, declencheur, json.dumps(OBJECTIFS_DEFAUT), "en_cours", t, demo))
    cid = cur.lastrowid
    conn.execute("UPDATE instances SET objet_id = ? WHERE id = ?", (cid, inst))
    return dict(_camp(conn, cid))


# --------------------------------------------------------------------------- T01 / G01
def proposer(conn, cid: int, t: str, lignes: List[dict], objectifs: Optional[Dict] = None,
             acteur: str = "dir_marketing") -> dict:
    camp = _camp(conn, cid)
    lignes = [l for l in lignes if float(l.get("montant") or 0) > 0]
    if not lignes:
        raise ValueError("Le budget doit comporter au moins une ligne.")
    total = sum(float(l["montant"]) for l in lignes)
    version = camp["version_budget"] + 1
    enregistrer(conn, camp["instance_id"], "T01", t, acteur, details="Version %d : %s" % (version, euros(total)))
    for l in lignes:
        conn.execute("INSERT INTO budget_lignes(campagne_id, version, canal, montant) VALUES (?,?,?,?)",
                     (cid, version, str(l["canal"])[:60], float(l["montant"])))
    obj = dict(json.loads(camp["objectifs"]))
    if objectifs:
        obj.update({k: float(v) for k, v in objectifs.items() if v not in (None, "")})
    conn.execute("UPDATE campagnes SET budget_propose=?, version_budget=?, objectifs=? WHERE id=?",
                 (total, version, json.dumps(obj), cid))
    _fx(conn, "FI-06", "Proposition de budget « %s » v%d : %s" % (camp["nom"], version, euros(total)), t, camp, "T01",
        lien="/a/finance/budgets")
    _fx(conn, "FM-01", "Demande de budget — %s" % camp["nom"], t, camp, "T01", notifier=False)
    return dict(_camp(conn, cid))


def valider_budget(conn, cid: int, t: str, issue: str, commentaire: str = "", acteur: str = "finance") -> dict:
    camp = _camp(conn, cid)
    enregistrer(conn, camp["instance_id"], "G01", t, acteur, issue=issue, details=commentaire)
    if issue == "oui":
        conn.execute("UPDATE campagnes SET budget_valide=budget_propose, commentaire_finance=? WHERE id=?",
                     (commentaire or "Budget accordé", cid))
        _fx(conn, "FI-07", "Budget accordé : %s — %s" % (euros(camp["budget_propose"] or 0), camp["nom"]), t, camp,
            "G01", lien="/a/dir_marketing/campagne?c=%d" % cid)
        _fx(conn, "FM-02", "Budget accordé — %s" % camp["nom"], t, camp, "G01", notifier=False)
        _fx(conn, "FM-08", "Objectifs et budget transmis : %s" % camp["nom"], t, camp, "G01", lien=_lien(cid))
        conn.execute("UPDATE briefs_agence SET statut='en_cours' WHERE statut='en_attente_budget' AND titre LIKE ?",
                     ("%" + camp["nom"].split("—")[-1].strip() + "%",))
    else:
        conn.execute("UPDATE campagnes SET commentaire_finance=? WHERE id=?", (commentaire or "À revoir", cid))
        _fx(conn, "FI-07", "Budget à revoir (non : revoir) — %s : %s" % (camp["nom"], commentaire or "montant trop élevé"),
            t, camp, "G01", lien="/a/dir_marketing/campagne?c=%d" % cid)
    return dict(_camp(conn, cid))


# --------------------------------------------------------------------------- T02 / T03 / T04 / T05
def publier_videos(conn, cid: int, t: str, videos: List[dict], acteur: str = "mkt_social") -> dict:
    camp = _camp(conn, cid)
    videos = [v for v in videos if (v.get("titre") or "").strip()]
    if not videos:
        raise ValueError("Sélectionnez au moins une vidéo à publier.")
    enregistrer(conn, camp["instance_id"], "T02", t, acteur, details="%d vidéo(s) publiée(s)" % len(videos))
    budget = camp["budget_valide"] or 400000
    for v in videos:
        vf = int(budget * 14 * (0.8 + 0.1 * len(v["titre"]) % 5 / 10))
        conn.execute("INSERT INTO publications(campagne_id, type, titre, concept, plateforme, auteur, publie_le, "
                     "vues_finales, likes, partages, commentaires, sentiment_positif, demo) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                     (cid, "video_apple", v["titre"][:80], (v.get("concept") or "")[:120], "TikTok", "@apple", t, vf,
                      int(vf * 0.06), int(vf * 0.004), int(vf * 0.002), 55.0, camp["demo"]))
        conn.execute("INSERT INTO contenus_creation(campagne_id, type, titre, statut, destinataire, brief_le, livre_le, demo) "
                     "VALUES (?,?,?,?,?,?,?,?)", (cid, "Vidéo TikTok", v["titre"][:80], "livré", "mkt_social", t, t,
                                                  camp["demo"]))
    _fx(conn, "FM-10", "%d vidéo(s) TikTok livrée(s) par la création" % len(videos), t, camp, "T02",
        emetteur="mkt_creation", recepteur="mkt_social", notifier=False)
    _fx(conn, "FE-06A", "Publication de %d vidéo(s) sur le compte TikTok officiel" % len(videos), t, camp, "T02",
        emetteur="mkt_social", recepteur="influenceur", lien="/a/influenceur/portail")
    _fx(conn, "FE-07A", "Brief d'achat média TikTok Ads — %s" % camp["nom"], t, camp, "T02", lien="/a/agence/portail")
    return dict(_camp(conn, cid))


def selectionner_influenceurs(conn, cid: int, t: str, ids: List[int], acteur: str = "mkt_social") -> dict:
    camp = _camp(conn, cid)
    ids = [int(i) for i in ids]
    if not ids:
        raise ValueError("Sélectionnez au moins un influenceur.")
    dispo = conn.execute("SELECT COUNT(*) FROM appareils_test WHERE statut='disponible'").fetchone()[0]
    if len(ids) > dispo:
        raise ValueError("Seulement %d appareils de pré-série disponibles." % dispo)
    enregistrer(conn, camp["instance_id"], "T03", t, acteur, details="%d influenceur(s) sélectionné(s)" % len(ids))
    for i in ids:
        conn.execute("INSERT OR IGNORE INTO campagne_influenceurs(campagne_id, influenceur_id, selectionne_le) "
                     "VALUES (?,?,?)", (cid, i, t))
    noms = ", ".join(r["pseudo"] for r in conn.execute(
        "SELECT pseudo FROM influenceurs WHERE id IN (%s)" % ",".join("?" * len(ids)), ids))
    _fx(conn, "FI-13", "Demande de %d appareil(s) de test pour %s" % (len(ids), noms), t, camp, "T03",
        lien="/a/production/appareils-test?c=%d" % cid)
    _fx(conn, "FE-06A", "Invitation à tester l'iPhone Duo : %s" % noms, t, camp, "T03", emetteur="mkt_social",
        recepteur="influenceur", lien="/a/influenceur/portail?c=%d" % cid)
    return dict(_camp(conn, cid))


def fournir_appareils(conn, cid: int, t: str, acteur: str = "production") -> dict:
    camp = _camp(conn, cid)
    selection = conn.execute("SELECT influenceur_id FROM campagne_influenceurs WHERE campagne_id=? "
                             "AND appareil_id IS NULL", (cid,)).fetchall()
    apps = conn.execute("SELECT id FROM appareils_test WHERE statut='disponible' ORDER BY id LIMIT ?",
                        (len(selection),)).fetchall()
    if len(apps) < len(selection):
        raise TransitionInvalide("Stock d'appareils de pré-série insuffisant.")
    enregistrer(conn, camp["instance_id"], "T04", t, acteur, details="%d appareil(s) expédié(s)" % len(selection))
    for s, a in zip(selection, apps):
        conn.execute("UPDATE appareils_test SET statut='expédié', influenceur_id=?, campagne_id=?, expedie_le=? WHERE id=?",
                     (s["influenceur_id"], cid, t, a["id"]))
        conn.execute("UPDATE campagne_influenceurs SET appareil_id=?, appareil_expedie_le=? WHERE campagne_id=? AND "
                     "influenceur_id=?", (a["id"], t, cid, s["influenceur_id"]))
    _fx(conn, "FE-06A", "%d appareil(s) de test expédié(s) aux influenceurs" % len(selection), t, camp, "T04",
        emetteur="production", recepteur="influenceur", lien="/a/influenceur/portail?c=%d" % cid)
    return dict(_camp(conn, cid))


def publier_avis(conn, cid: int, influenceur_id: int, t: str, titre: str, note_sentiment: float,
                 acteur: str = "influenceur") -> dict:
    camp = _camp(conn, cid)
    lien_ci = conn.execute("SELECT * FROM campagne_influenceurs WHERE campagne_id=? AND influenceur_id=?",
                           (cid, influenceur_id)).fetchone()
    if lien_ci is None:
        raise TransitionInvalide("Cet influenceur n'a pas été sélectionné pour la campagne.")
    if not lien_ci["appareil_expedie_le"]:
        raise TransitionInvalide("L'appareil de test n'a pas encore été fourni par la production (P2-T04).")
    if lien_ci["avis_publie_le"]:
        raise TransitionInvalide("Avis déjà publié.")
    etat = charger_etat(conn, camp["instance_id"], t)
    if not etat.actif("T05"):
        raise TransitionInvalide("La tâche P2-T05 n'est pas active.")
    inf = conn.execute("SELECT * FROM influenceurs WHERE id=?", (influenceur_id,)).fetchone()
    vf = int(inf["abonnes"] * 0.8)
    cur = conn.execute("INSERT INTO publications(campagne_id, type, titre, concept, plateforme, auteur, influenceur_id, "
                       "publie_le, vues_finales, likes, partages, commentaires, sentiment_positif, demo) "
                       "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                       (cid, "avis_influenceur", (titre or "Mon avis sur l'iPhone Duo")[:100], inf["univers"],
                        inf["plateforme"], inf["pseudo"], influenceur_id, t, vf, int(vf * inf["engagement"] / 100),
                        int(vf * 0.004), int(vf * 0.003), float(note_sentiment), camp["demo"]))
    conn.execute("UPDATE campagne_influenceurs SET avis_publie_le=?, publication_id=? WHERE campagne_id=? AND "
                 "influenceur_id=?", (t, cur.lastrowid, cid, influenceur_id))
    enregistrer(conn, camp["instance_id"], "T05", t, acteur, details="Avis publié par %s" % inf["pseudo"], partiel=True)
    _fx(conn, "FE-06R", "Avis publié par %s : « %s »" % (inf["pseudo"], titre), t, camp, "T05",
        emetteur="influenceur", recepteur="mkt_social", lien=_lien(cid))
    restants = conn.execute("SELECT COUNT(*) FROM campagne_influenceurs WHERE campagne_id=? AND avis_publie_le IS NULL",
                            (cid,)).fetchone()[0]
    if restants == 0:
        enregistrer(conn, camp["instance_id"], "T05", t, acteur, details="Tous les avis sont publiés")
        _fx(conn, "FM-14", "Tous les avis influenceurs sont publiés : mesure possible", t, camp, "T05",
            emetteur="mkt_social", recepteur="mkt_data", lien="/a/mkt_data/mesure?c=%d" % cid)
    return dict(_camp(conn, cid))


# --------------------------------------------------------------------------- T06 / G02 / T07
def calculer_mesure(conn, camp, t: str) -> dict:
    """Indicateurs de la campagne à l'instant t (vues, mentions, sentiment…)."""
    tt = parse(t)
    pubs = conn.execute("SELECT * FROM publications WHERE campagne_id=? AND publie_le <= ?", (camp["id"], t)).fetchall()
    vues_apple = sum(courbe_vues(p["vues_finales"], p["publie_le"], tt) for p in pubs if p["type"] == "video_apple")
    vues_inf = sum(courbe_vues(p["vues_finales"], p["publie_le"], tt) for p in pubs if p["type"] != "video_apple")
    n_mes = conn.execute("SELECT COUNT(*) FROM mesures WHERE campagne_id=?", (camp["id"],)).fetchone()[0]
    n_aj = conn.execute("SELECT COUNT(*) FROM ajustements WHERE campagne_id=?", (camp["id"],)).fetchone()[0]
    obj = json.loads(camp["objectifs"])
    # modèle simple et explicable : chaque ajustement améliore le sentiment de 5 points
    sentiment = round(obj.get("sentiment", 60) - 5 + 5 * n_aj, 1)
    vues = int(max(vues_apple, obj.get("vues_tiktok", 1) * (0.6 + 0.45 * (n_mes + 1))))
    mentions = int(obj.get("mentions", 1) * (0.5 + 0.4 * (n_mes + 1)) + vues_inf * 0.01)
    me = int(obj.get("me_prevenir", 1) * (0.7 + 0.2 * (n_mes + 1)))
    intention = round(obj.get("intention", 7) - 1.5 + 0.9 * n_aj, 1)
    return {"vues": vues, "mentions": mentions, "sentiment": sentiment, "engagement": round(5.4 + 0.3 * n_aj, 1),
            "me_prevenir": me, "intention": intention, "numero": n_mes + 1}


def comparer_objectifs(camp, mesure: dict) -> List[dict]:
    obj = json.loads(camp["objectifs"])
    lib = {"vues_tiktok": ("Vues TikTok", "vues"), "sentiment": ("Commentaires positifs (%)", "sentiment"),
           "mentions": ("Mentions", "mentions"), "me_prevenir": ("Inscriptions « Me prévenir »", "me_prevenir"),
           "intention": ("Intention d'achat (%)", "intention")}
    out = []
    for k, (libelle, champ) in lib.items():
        if k in obj and mesure.get(champ) is not None:
            out.append({"code": k, "libelle": libelle, "objectif": obj[k], "resultat": mesure[champ],
                        "atteint": mesure[champ] >= obj[k]})
    return out


def mesurer(conn, cid: int, t: str, acteur: str = "mkt_data") -> dict:
    camp = _camp(conn, cid)
    m = calculer_mesure(conn, camp, t)
    enregistrer(conn, camp["instance_id"], "T06", t, acteur, details="Mesure n°%d" % m["numero"])
    conn.execute("INSERT INTO mesures(campagne_id, numero, horodatage, vues, mentions, sentiment, engagement, "
                 "me_prevenir, intention) VALUES (?,?,?,?,?,?,?,?,?)",
                 (cid, m["numero"], t, m["vues"], m["mentions"], m["sentiment"], m["engagement"], m["me_prevenir"],
                  m["intention"]))
    conn.execute("UPDATE campagnes SET budget_depense = MIN(COALESCE(budget_valide,0), budget_depense + ?) WHERE id=?",
                 (0.28 * (camp["budget_valide"] or 0), cid))
    _fx(conn, "FM-14", "Vues, mentions, engagement collectés (mesure n°%d)" % m["numero"], t, camp, "T06",
        emetteur="mkt_social", recepteur="mkt_data", notifier=False)
    atteints = sum(1 for o in comparer_objectifs(camp, m) if o["atteint"])
    _fx(conn, "FM-17", "Tableau de bord de campagne — mesure n°%d : %d objectif(s) atteint(s) sur %d"
        % (m["numero"], atteints, len(comparer_objectifs(camp, m))), t, camp, "T06", emetteur="mkt_data",
        recepteur="dir_marketing", lien="/a/mkt_data/mesure?c=%d" % cid)
    return m


def decider_objectifs(conn, cid: int, t: str, issue: str, commentaire: str = "", acteur: str = "dir_marketing") -> dict:
    camp = _camp(conn, cid)
    enregistrer(conn, camp["instance_id"], "G02", t, acteur, issue=issue, details=commentaire)
    conn.execute("UPDATE mesures SET objectifs_atteints=?, decide_par=?, decide_le=?, commentaire=? WHERE id = "
                 "(SELECT MAX(id) FROM mesures WHERE campagne_id=?)",
                 (1 if issue == "oui" else 0, acteur, t, commentaire, cid))
    if issue == "non":
        _fx(conn, "FM-08", "Objectifs non atteints : ajuster le ciblage et le message (%s)" % camp["nom"], t, camp,
            "G02", emetteur="dir_marketing", recepteur="mkt_social", lien=_lien(cid))
    return dict(_camp(conn, cid))


def ajuster(conn, cid: int, t: str, ciblage: str, message: str, acteur: str = "mkt_social") -> dict:
    camp = _camp(conn, cid)
    if not ciblage.strip() or not message.strip():
        raise ValueError("Ciblage et message sont obligatoires.")
    enregistrer(conn, camp["instance_id"], "T07", t, acteur, details=message[:200])
    conn.execute("INSERT INTO ajustements(campagne_id, horodatage, ciblage, message, acteur) VALUES (?,?,?,?,?)",
                 (cid, t, ciblage[:200], message[:300], acteur))
    _fx(conn, "FM-15", "Ciblage des audiences mis à jour : %s" % ciblage[:120], t, camp, "T07", emetteur="mkt_data",
        recepteur="mkt_social", notifier=False)
    _fx(conn, "FE-07A", "Brief ajusté à l'agence : %s" % message[:120], t, camp, "T07", lien="/a/agence/portail")
    return dict(_camp(conn, cid))


# --------------------------------------------------------------------------- T08 / T09 / T10
def envoyer_rapport(conn, cid: int, t: str, previsions: Dict, synthese: str = "", acteur: str = "dir_marketing") -> dict:
    camp = _camp(conn, cid)
    total = int(previsions.get("total") or 0)
    if total <= 0:
        raise ValueError("Indiquez une prévision de demande (nombre de précommandes).")
    enregistrer(conn, camp["instance_id"], "T08", t, acteur, details="Prévision : %d précommandes" % total)
    m = conn.execute("SELECT * FROM mesures WHERE campagne_id=? ORDER BY id DESC LIMIT 1", (cid,)).fetchone()
    syn = synthese or ("%s vues, %s %% de commentaires positifs." % ("{:,}".format(m["vues"]).replace(",", " "),
                                                                     m["sentiment"]) if m else "Rapport de campagne.")
    conn.execute("INSERT INTO rapports_campagne(campagne_id, horodatage, synthese, previsions) VALUES (?,?,?,?)",
                 (cid, t, syn, json.dumps({camp["pays"]: previsions})))
    _fx(conn, "FI-04", "Prévisions de demande %s : %d précommandes (couleur dominante : %s)" %
        (camp["pays"], total, previsions.get("coloris_principal", "noir")), t, camp, "T08",
        lien="/a/production/plan?c=%d" % cid)
    _fx(conn, "FM-03", "Prévisions de demande transmises — %s" % camp["nom"], t, camp, "T08", notifier=False)
    _fx(conn, "FM-18", "Rapport de campagne et dépenses : %s" % euros(camp["budget_depense"] or 0), t, camp, "T08",
        emetteur="mkt_data", recepteur="finance", lien="/a/finance/budgets?c=%d" % cid)
    return dict(_camp(conn, cid))


def ajuster_plan(conn, cid: int, t: str, coloris: str, quantite: int, acteur: str = "production") -> dict:
    camp = _camp(conn, cid)
    quantite = int(quantite)
    if coloris not in COLORIS or quantite <= 0:
        raise ValueError("Ajustement invalide.")
    pays = camp["pays"]
    lot_date = "2026-11-06T08:00:00" if t < "2026-10-30" else fmt(parse(t[:10] + "T08:00:00") + timedelta(days=10))
    if pays == "FR":
        parts = {"256": .33, "512": .36, "1T": .22, "2T": .09}
        for cap, pc in parts.items():
            conn.execute("INSERT INTO lots_production(pays, capacite, coloris, quantite, disponible_le, origine, cree_le, "
                         "demo) VALUES (?,?,?,?,?,?,?,?)",
                         (pays, cap, coloris, int(round(quantite * pc)), lot_date,
                          "Ajustement du plan (P2-T09) : +%d %s" % (quantite, COLORIS[coloris]["libelle"]), t,
                          camp["demo"]))
    else:
        conn.execute("INSERT INTO lots_production(pays, capacite, coloris, quantite, disponible_le, origine, cree_le, demo) "
                     "VALUES (?,?,?,?,?,?,?,?)", (pays, None, None, quantite, lot_date,
                                                  "Ajustement du plan (P2-T09)", t, camp["demo"]))
    enregistrer(conn, camp["instance_id"], "T09", t, acteur,
                details="+%d %s sur le lot du %s" % (quantite, COLORIS[coloris]["libelle"], lot_date[:10]))
    _fx(conn, "FI-05", "Plan de production ajusté : +%d %s (%s)" % (quantite, COLORIS[coloris]["libelle"], pays), t,
        camp, "T09", lien="/a/dir_marketing/campagne?c=%d" % cid)
    _fx(conn, "FM-04", "Volumes disponibles mis à jour (%s)" % pays, t, camp, "T09", notifier=False)
    return dict(_camp(conn, cid))


def calculer_cac(conn, cid: int, t: str, acteur: str = "finance") -> dict:
    camp = _camp(conn, cid)
    depense = camp["budget_depense"] or (camp["budget_valide"] or 0) * 0.9
    if camp["pays"] == "FR":
        n = conn.execute("SELECT COUNT(*) FROM precommandes WHERE pays='FR' AND paye_le IS NOT NULL AND paye_le <= ? "
                         "AND paye_le >= ?", (t, camp["cree_le"])).fetchone()[0]
        n = int(n / float(lire_parametre(conn, "echelle", "1") or 1)) if n else 0
    else:
        n = conn.execute("SELECT COALESCE(SUM(nb),0) FROM precommandes_pays WHERE pays=? AND heure <= ? AND heure >= ?",
                         (camp["pays"], t, camp["cree_le"])).fetchone()[0]
    if n == 0:
        rap = conn.execute("SELECT previsions FROM rapports_campagne WHERE campagne_id=? ORDER BY id DESC LIMIT 1",
                           (cid,)).fetchone()
        prev = json.loads(rap["previsions"]).get(camp["pays"], {}) if rap else {}
        n = int(prev.get("total") or 1)
        base = "prévisionnel (sur %d précommandes prévues)" % n
    else:
        base = "sur %d précommandes" % n
    cac = round(depense / max(1, n), 2)
    enregistrer(conn, camp["instance_id"], "T10", t, acteur, details="CAC : %s %s" % (euros(cac, 2), base))
    conn.execute("UPDATE campagnes SET cout_acquisition=?, precommandes_attribuees=?, budget_depense=?, statut=? "
                 "WHERE id=?", (cac, n, depense, "terminee", cid))
    _fx(conn, "FI-12", "Coût d'acquisition par précommande — %s : %s (%s)" % (camp["nom"], euros(cac, 2), base), t,
        camp, "T10", emetteur="finance", recepteur="dir_marketing", lien="/a/dir_marketing/campagne?c=%d" % cid)
    return dict(_camp(conn, cid))


# --------------------------------------------------------------------------- lecture
def detail(conn, cid: int, t: str) -> dict:
    camp = _camp(conn, cid)
    visible = camp["cree_le"] <= t
    etat = charger_etat(conn, camp["instance_id"], t).dict() if visible else None
    fige = conn.execute("SELECT COUNT(*) FROM evenements WHERE instance_id=? AND horodatage > ?",
                        (camp["instance_id"], t)).fetchone()[0] > 0
    version = conn.execute("SELECT MAX(version) FROM budget_lignes WHERE campagne_id=? AND version <= ?",
                           (cid, camp["version_budget"])).fetchone()[0]
    lignes = [dict(r) for r in conn.execute("SELECT canal, montant, version FROM budget_lignes WHERE campagne_id=? "
                                            "ORDER BY version, id", (cid,))]
    infl = [dict(r) for r in conn.execute(
        "SELECT i.*, ci.selectionne_le, ci.appareil_id, ci.appareil_expedie_le, ci.avis_publie_le, ci.publication_id "
        "FROM campagne_influenceurs ci JOIN influenceurs i ON i.id = ci.influenceur_id WHERE ci.campagne_id=? "
        "AND ci.selectionne_le <= ? ORDER BY i.abonnes DESC", (cid, t))]
    for i in infl:
        if i["appareil_expedie_le"] and i["appareil_expedie_le"] > t:
            i["appareil_expedie_le"] = None
        if i["avis_publie_le"] and i["avis_publie_le"] > t:
            i["avis_publie_le"] = None
    pubs = [dict(r) for r in conn.execute("SELECT * FROM publications WHERE campagne_id=? AND publie_le <= ? "
                                          "ORDER BY publie_le", (cid, t))]
    tt = parse(t)
    for p in pubs:
        p["vues_a_date"] = int(courbe_vues(p["vues_finales"], p["publie_le"], tt))
    mesures = [dict(r) for r in conn.execute("SELECT * FROM mesures WHERE campagne_id=? AND horodatage <= ? "
                                             "ORDER BY numero", (cid, t))]
    for m in mesures:
        if m["decide_le"] and m["decide_le"] > t:
            m["objectifs_atteints"], m["decide_le"] = None, None
    ajust = [dict(r) for r in conn.execute("SELECT * FROM ajustements WHERE campagne_id=? AND horodatage <= ? "
                                           "ORDER BY horodatage", (cid, t))]
    rapports = [dict(r, previsions=json.loads(r["previsions"])) for r in conn.execute(
        "SELECT * FROM rapports_campagne WHERE campagne_id=? AND horodatage <= ?", (cid, t))]
    evts = [dict(r) for r in conn.execute("SELECT noeud, issue, acteur, horodatage, details, partiel FROM evenements "
                                          "WHERE instance_id=? AND horodatage <= ? ORDER BY horodatage, id",
                                          (camp["instance_id"], t))]
    d = dict(camp)
    d["objectifs"] = json.loads(camp["objectifs"])
    budget_a_date = [l for l in lignes if any(e["noeud"] == "T01" for e in evts)]
    derniere = max([l["version"] for l in budget_a_date] or [0])
    d.update(visible=visible, etat=etat, fige=fige, lignes=[l for l in lignes if l["version"] == derniere],
             historique_budget=lignes, influenceurs=infl, publications=pubs, mesures=mesures,
             ajustements=ajust, rapports=rapports, evenements=evts,
             comparaison=comparer_objectifs(camp, mesures[-1]) if mesures else [],
             mesure_previsionnelle=calculer_mesure(conn, camp, t) if visible else None)
    if any(e["noeud"] == "G01" and e["issue"] == "oui" for e in evts):
        d["budget_valide_a_date"] = camp["budget_valide"] or camp["budget_propose"]
    else:
        d["budget_valide_a_date"] = None
    return d


def liste(conn, t: str) -> List[dict]:
    rows = conn.execute("SELECT id, nom, pays, statut, cree_le, demo, instance_id FROM campagnes WHERE cree_le <= ? "
                        "ORDER BY cree_le DESC", (t,)).fetchall()
    out = []
    for r in rows:
        e = charger_etat(conn, r["instance_id"], t)
        out.append(dict(r, jetons=e.jetons, fini=e.fini))
    return out
