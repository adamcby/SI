"""Portails des acteurs « hors processus BPMN » : chaque portail montre les flux échangés avec Apple
(diagramme de contexte et § 3.4) et permet de déclencher ces flux (action -> flux codifié -> notification)."""
import json
from datetime import timedelta
from typing import Callable, Dict, List

from ..bus import emettre
from ..db import lire_parametre
from ..horloge import fmt, parse
from ..metier import PRODUIT, euros
from ..moteur import TransitionInvalide
from ..referentiel import APPLE_STORES_FR
from . import campagnes as svc_camp
from . import precommandes as svc_pc


def _n(conn, sql, args=()):
    row = conn.execute(sql, args).fetchone()
    return (row[0] or 0) if row else 0


def _rows(conn, sql, args=()):
    return [dict(r) for r in conn.execute(sql, args)]


def _sep(v):
    return "{:,}".format(int(round(v or 0))).replace(",", " ")


def _champ(nom, libelle, type_="text", options=None, defaut=None, requis=True):
    return {"nom": nom, "libelle": libelle, "type": type_, "options": options or [], "defaut": defaut, "requis": requis}


# =========================================================================== opérateurs (FE-02)
def _operateur(conn, t):
    jour = t[:10]
    kpis = [
        {"libelle": "Activations eSIM iPhone Duo", "valeur": _sep(_n(conn, "SELECT SUM(activations_esim) FROM "
                                                                     "operateurs_activations WHERE jour <= ?", (jour,)))},
        {"libelle": "Ventes en boutique opérateur", "valeur": _sep(_n(conn, "SELECT SUM(ventes) FROM operateurs_activations "
                                                                            "WHERE jour <= ?", (jour,)))},
        {"libelle": "Forfaits 5G associés", "valeur": _sep(_n(conn, "SELECT SUM(forfaits_5g) FROM operateurs_activations "
                                                                    "WHERE jour <= ?", (jour,)))},
        {"libelle": "Stocks reçus le 21/10", "valeur": "6 200" if t >= "2026-10-21T07" else "—",
         "aide": "Orange 2 400 · SFR 1 400 · Bouygues 1 300 · Free 1 100"},
    ]
    tables = [{"id": "activations", "titre": "Activations et ventes remontées (flux FE-02R)", "flux": "FE-02R",
               "colonnes": [("jour", "Jour"), ("operateur", "Opérateur"), ("activations_esim", "Activations eSIM"),
                            ("ventes", "Ventes"), ("forfaits_5g", "Forfaits 5G")],
               "lignes": _rows(conn, "SELECT * FROM operateurs_activations WHERE jour <= ? ORDER BY jour DESC, "
                                     "activations_esim DESC LIMIT 16", (jour,)),
               "vide": "Les activations démarrent à la sortie, le vendredi 23 octobre."}]
    actions = [{"code": "ventes", "libelle": "Remonter les ventes du jour", "flux": "FE-02R",
                "description": "Les ventes et forfaits remontés alimentent le tableau de bord d'Apple (après la sortie).",
                "champs": [_champ("operateur", "Opérateur", "select", ["Orange", "SFR", "Bouygues Telecom", "Free"]),
                           _champ("ventes", "iPhone Duo vendus", "number", defaut=120),
                           _champ("activations", "Activations eSIM", "number", defaut=640)]}]
    return kpis, tables, actions


def _operateur_action(conn, t, code, d):
    op, ventes, act = d["operateur"], int(d["ventes"]), int(d["activations"])
    conn.execute("INSERT INTO operateurs_activations(jour, operateur, activations_esim, ventes, forfaits_5g) VALUES "
                 "(?,?,?,?,?) ON CONFLICT(jour, operateur) DO UPDATE SET activations_esim = activations_esim + ?, "
                 "ventes = ventes + ?, forfaits_5g = forfaits_5g + ?",
                 (t[:10], op, act, ventes, int(ventes * .6), act, ventes, int(ventes * .6)))
    emettre(conn, "FE-02R", "%s : %d ventes et %d activations eSIM remontées" % (op, ventes, act), t,
            emetteur="operateur", demo=1)
    return "Ventes transmises à Apple (flux FE-02R)."


# =========================================================================== revendeurs (FE-03)
def _revendeur(conn, t):
    def s(type_):
        return _n(conn, "SELECT SUM(quantite) FROM revendeurs_flux WHERE type=? AND horodatage <= ?", (type_, t))
    kpis = [{"libelle": "Stock reçu (Fnac, Darty, Boulanger)", "valeur": _sep(s("stock"))},
            {"libelle": "Kits PLV reçus", "valeur": _sep(s("plv"))},
            {"libelle": "Ventes remontées", "valeur": _sep(s("ventes"))}]
    tables = [{"id": "flux", "titre": "Échanges avec Apple (stocks, PLV / ventes)", "flux": "FE-03A",
               "colonnes": [("horodatage", "Date"), ("enseigne", "Enseigne"), ("type", "Type"), ("quantite", "Quantité"),
                            ("commentaire", "Commentaire")],
               "lignes": _rows(conn, "SELECT * FROM revendeurs_flux WHERE horodatage <= ? ORDER BY horodatage DESC "
                                     "LIMIT 15", (t,))}]
    actions = [{"code": "ventes", "libelle": "Remonter les ventes", "flux": "FE-03R",
                "description": "Les ventes des revendeurs complètent la vision des ventes d'Apple.",
                "champs": [_champ("enseigne", "Enseigne", "select", ["Fnac", "Darty", "Boulanger"]),
                           _champ("quantite", "iPhone Duo vendus", "number", defaut=45)]}]
    return kpis, tables, actions


def _revendeur_action(conn, t, code, d):
    q = int(d["quantite"])
    conn.execute("INSERT INTO revendeurs_flux(enseigne, type, quantite, horodatage, demo) VALUES (?,?,?,?,1)",
                 (d["enseigne"], "ventes", q, t))
    emettre(conn, "FE-03R", "Ventes %s : %d iPhone Duo" % (d["enseigne"], q), t, emetteur="revendeur", demo=1)
    return "Ventes transmises (flux FE-03R)."


# =========================================================================== fournisseurs (FE-04)
def _fournisseur(conn, t):
    sem = (parse(t) - timedelta(days=6)).strftime("%Y-%m-%d")
    cap = conn.execute("SELECT * FROM capacites_fournisseurs WHERE fournisseur='Samsung Display' AND semaine >= ? "
                       "ORDER BY semaine LIMIT 1", (sem,)).fetchone()
    kpis = [{"libelle": "Capacité Samsung Display (écrans / semaine)", "valeur": _sep(cap["capacite"]) if cap else "—"},
            {"libelle": "Capacité engagée par Apple", "valeur": _sep(cap["engagee"]) if cap else "—"},
            {"libelle": "Capacité disponible", "valeur": _sep(cap["capacite"] - cap["engagee"]) if cap else "—",
             "aide": "Fournisseur exclusif de l'écran pliable pour trois ans (SWOT, faiblesses)."},
            {"libelle": "Commandes reçues d'Apple", "valeur": _sep(_n(conn, "SELECT COUNT(*) FROM commandes_fournisseurs "
                                                                              "WHERE cree_le <= ?", (t,)))}]
    commandes = _rows(conn, "SELECT * FROM commandes_fournisseurs WHERE cree_le <= ? ORDER BY semaine DESC LIMIT 12", (t,))
    tables = [
        {"id": "commandes", "titre": "Commandes d'Apple (flux FE-04A)", "flux": "FE-04A",
         "colonnes": [("semaine", "Semaine"), ("fournisseur", "Fournisseur"), ("composant", "Composant"),
                      ("quantite", "Quantité"), ("statut", "Statut")], "lignes": commandes,
         "action_ligne": {"code": "livrer", "libelle": "Confirmer la livraison", "condition": {"statut": ["confirmée", "envoyée"]},
                          "champs": []}},
        {"id": "capacites", "titre": "Capacités déclarées (flux FE-04R)", "flux": "FE-04R",
         "colonnes": [("semaine", "Semaine"), ("fournisseur", "Fournisseur"), ("composant", "Composant"),
                      ("capacite", "Capacité"), ("engagee", "Engagée")],
         "lignes": _rows(conn, "SELECT * FROM capacites_fournisseurs WHERE semaine >= ? ORDER BY semaine, fournisseur "
                               "LIMIT 10", (sem,))},
    ]
    actions = [{"code": "capacite", "libelle": "Déclarer une nouvelle capacité hebdomadaire", "flux": "FE-04R",
                "description": "La capacité déclarée limite les hausses de production possibles (tâche P1-T11).",
                "champs": [_champ("capacite", "Écrans pliables par semaine", "number", defaut=300000)]}]
    return kpis, tables, actions


def _fournisseur_action(conn, t, code, d):
    if code == "capacite":
        cap = int(d["capacite"])
        if cap < 200000 or cap > 400000:
            raise ValueError("Capacité attendue entre 200 000 et 400 000 écrans par semaine.")
        sem = (parse(t) - timedelta(days=6)).strftime("%Y-%m-%d")
        conn.execute("UPDATE capacites_fournisseurs SET capacite=?, declare_le=? WHERE fournisseur='Samsung Display' "
                     "AND semaine >= ?", (cap, t, sem))
        emettre(conn, "FE-04R", "Samsung Display déclare une capacité de %s écrans / semaine" % _sep(cap), t,
                emetteur="fournisseur", lien="/a/production/plan", demo=1)
        return "Capacité transmise à la production (flux FE-04R)."
    if code == "livrer":
        cid = int(d["id"])
        conn.execute("UPDATE commandes_fournisseurs SET statut='livrée', livre_le=? WHERE id=?", (t, cid))
        emettre(conn, "FE-04R", "Livraison confirmée (commande n°%d)" % cid, t, emetteur="fournisseur", demo=1)
        return "Livraison confirmée (flux FE-04R)."
    raise ValueError("Action inconnue")


# =========================================================================== développeurs (FE-05)
def _developpeur(conn, t):
    kpis = [{"libelle": "Apps adaptées au double écran (publiées)",
             "valeur": _sep(_n(conn, "SELECT COUNT(*) FROM apps_adaptees WHERE soumise_le <= ? AND statut='publiée'", (t,)))},
            {"libelle": "Apps en revue", "valeur": _sep(_n(conn, "SELECT COUNT(*) FROM apps_adaptees WHERE soumise_le <= ? "
                                                                 "AND statut='en revue'", (t,)))},
            {"libelle": "Outils fournis", "valeur": "iOS 27", "aide": "API double écran, simulateur pliable (flux FE-05A)."}]
    tables = [{"id": "apps", "titre": "Applications adaptées au pliable (flux FE-05R)", "flux": "FE-05R",
               "colonnes": [("soumise_le", "Soumise le"), ("nom", "Application"), ("editeur", "Éditeur"),
                            ("categorie", "Catégorie"), ("statut", "Statut")],
               "lignes": _rows(conn, "SELECT * FROM apps_adaptees WHERE soumise_le <= ? ORDER BY soumise_le DESC LIMIT 15",
                               (t,))}]
    actions = [{"code": "soumettre", "libelle": "Soumettre une app adaptée au double écran", "flux": "FE-05R",
                "description": "Chaque app adaptée renforce l'argumentaire de vente du marketing.",
                "champs": [_champ("nom", "Nom de l'application", defaut="Mon app Duo"),
                           _champ("editeur", "Éditeur", defaut="Studio indépendant"),
                           _champ("categorie", "Catégorie", "select", ["Productivité", "Création", "Jeux", "Éducation",
                                                                       "Photo", "Santé", "Divertissement"])]}]
    return kpis, tables, actions


def _developpeur_action(conn, t, code, d):
    conn.execute("INSERT INTO apps_adaptees(nom, editeur, categorie, soumise_le, statut, demo) VALUES (?,?,?,?,?,1)",
                 (d["nom"][:60], d["editeur"][:60], d["categorie"], t, "en revue"))
    emettre(conn, "FE-05R", "Nouvelle app adaptée au pliable : %s (%s)" % (d["nom"][:60], d["editeur"][:60]), t,
            emetteur="developpeur", demo=1)
    return "App soumise (flux FE-05R)."


# =========================================================================== agences (FE-07)
def _agence(conn, t):
    briefs = _rows(conn, "SELECT * FROM briefs_agence WHERE envoye_le <= ? ORDER BY envoye_le DESC", (t,))
    for b in briefs:
        if b["livre_le"] and b["livre_le"] > t:
            b["livre_le"], b["statut"], b["rapport"] = None, "en_cours", None
    kpis = [{"libelle": "Briefs reçus", "valeur": str(len(briefs))},
            {"libelle": "Budget confié", "valeur": euros(sum(b["budget"] for b in briefs))},
            {"libelle": "Livrés", "valeur": str(sum(1 for b in briefs if b["livre_le"]))}]
    tables = [{"id": "briefs", "titre": "Briefs reçus d'Apple (flux FE-07A)", "flux": "FE-07A",
               "colonnes": [("envoye_le", "Reçu le"), ("agence", "Agence"), ("titre", "Brief"), ("budget", "Budget"),
                            ("statut", "Statut"), ("rapport", "Rapport")], "lignes": briefs,
               "action_ligne": {"code": "livrer", "libelle": "Livrer campagne + rapport",
                                "condition": {"statut": ["en_cours"]},
                                "champs": [_champ("rapport", "Rapport de performance", "textarea",
                                                  defaut="Campagne diffusée : 4,2 M d'impressions, CPM 6,30 €.")]}}]
    return kpis, tables, []


def _agence_action(conn, t, code, d):
    bid = int(d["id"])
    conn.execute("UPDATE briefs_agence SET statut='livre', livre_le=?, rapport=? WHERE id=?",
                 (t, (d.get("rapport") or "")[:300], bid))
    titre = conn.execute("SELECT titre FROM briefs_agence WHERE id=?", (bid,)).fetchone()[0]
    emettre(conn, "FE-07R", "Campagne livrée et rapport transmis : %s" % titre, t, emetteur="agence", demo=1)
    return "Campagne et rapport livrés (flux FE-07R)."


# =========================================================================== instituts (FE-08)
def _institut(conn, t):
    etudes = _rows(conn, "SELECT * FROM etudes WHERE commandee_le <= ? ORDER BY commandee_le DESC", (t,))
    for e in etudes:
        if e["livree_le"] and e["livree_le"] > t:
            e["livree_le"], e["statut"], e["resultat"] = None, "commandee", None
        e["resultat_txt"] = ", ".join("%s : %s" % (k, v) for k, v in json.loads(e["resultat"]).items()) \
            if e["resultat"] else "—"
    derniere = next((e for e in etudes if e["type"] == "intention" and e["statut"] == "livree"), None)
    kpis = [{"libelle": "Études commandées", "valeur": str(len(etudes))},
            {"libelle": "Études livrées", "valeur": str(sum(1 for e in etudes if e["statut"] == "livree"))},
            {"libelle": "Dernière intention d'achat mesurée",
             "valeur": ("%s %%" % json.loads(derniere["resultat"])["intention"]).replace(".", ",") if derniere else "—"}]
    tables = [{"id": "etudes", "titre": "Commandes d'études (FE-08A) et livrables (FE-08R)", "flux": "FE-08A",
               "colonnes": [("commandee_le", "Commandée le"), ("institut", "Institut"), ("titre", "Étude"),
                            ("statut", "Statut"), ("resultat_txt", "Résultat")], "lignes": etudes,
               "action_ligne": {"code": "livrer", "libelle": "Livrer l'étude", "condition": {"statut": ["commandee"]},
                                "champs": [_champ("intention", "Intention d'achat mesurée (%)", "number", defaut=7.6)]}}]
    return kpis, tables, []


def _institut_action(conn, t, code, d):
    eid = int(d["id"])
    val = round(float(d["intention"]), 1)
    conn.execute("UPDATE etudes SET statut='livree', livree_le=?, resultat=? WHERE id=?",
                 (t, json.dumps({"intention": val}), eid))
    lundi = (parse(t) - timedelta(days=parse(t).weekday())).strftime("%Y-%m-%d")
    conn.execute("INSERT OR REPLACE INTO kpi_hebdo(semaine, pays, indicateur, valeur) VALUES (?,?,?,?)",
                 (lundi, "FR", "intention", val))
    emettre(conn, "FE-08R", "Étude livrée : intention d'achat %s %%" % str(val).replace(".", ","), t,
            emetteur="institut", lien="/a/dir_marketing/cockpit", demo=1)
    return "Étude livrée : le tableau de bord marketing est mis à jour (flux FE-08R)."


# =========================================================================== organisme financier (FE-09)
def _organisme(conn, t):
    dem = _rows(conn, "SELECT d.*, p.reference FROM demandes_credit d JOIN precommandes p ON p.id = d.precommande_id "
                      "WHERE d.cree_le <= ? ORDER BY CASE WHEN d.statut='etude' THEN 0 ELSE 1 END, d.cree_le DESC LIMIT 20",
                (t,))
    for x in dem:
        if x["decide_le"] and x["decide_le"] > t:
            x["statut"] = "etude"
        x["montant_txt"] = euros(x["montant"], 2)
    ech = float(lire_parametre(conn, "echelle", "1") or 1)
    tot = _n(conn, "SELECT COUNT(*) FROM demandes_credit WHERE cree_le <= ?", (t,))
    acc = _n(conn, "SELECT COUNT(*) FROM demandes_credit WHERE cree_le <= ? AND statut='accorde'", (t,))
    kpis = [{"libelle": "Demandes de crédit reçues", "valeur": _sep(tot / ech)},
            {"libelle": "Taux d'accord", "valeur": ("%.1f %%" % (100.0 * acc / tot)).replace(".", ",") if tot else "—"},
            {"libelle": "En étude manuelle", "valeur": str(_n(conn, "SELECT COUNT(*) FROM demandes_credit WHERE "
                                                                     "statut='etude' AND cree_le <= ?", (t,))),
             "aide": "Montant supérieur à 3 000 € : étude manuelle avant réponse (flux FE-09R)."},
            {"libelle": "Montant financé", "valeur": euros(_n(conn, "SELECT SUM(montant) FROM demandes_credit WHERE "
                                                                    "statut='accorde' AND cree_le <= ?", (t,)) / ech)}]
    tables = [{"id": "demandes", "titre": "Demandes de crédit reçues d'Apple (flux FE-09A)", "flux": "FE-09A",
               "colonnes": [("cree_le", "Reçue le"), ("reference", "Précommande"), ("produit", "Produit"),
                            ("montant_txt", "Montant"), ("duree_mois", "Durée (mois)"), ("statut", "Statut")],
               "lignes": dem,
               "action_ligne": {"code": "decider", "libelle": "Décider", "condition": {"statut": ["etude"]},
                                "champs": [_champ("decision", "Décision", "select", [["accorde", "Accorder"],
                                                                                       ["refuse", "Refuser"]])]}}]
    return kpis, tables, []


def _organisme_action(conn, t, code, d):
    svc_pc.decision_credit(conn, int(d["id"]), d["decision"], t)
    return "Réponse transmise à la finance d'Apple (flux FE-09R) : la passerelle P1-G01 peut être franchie."


# =========================================================================== reprise (FE-10)
def _reprise(conn, t):
    ech = float(lire_parametre(conn, "echelle", "1") or 1)
    n = _n(conn, "SELECT COUNT(*) FROM estimations_reprise WHERE horodatage <= ?", (t,))
    moy = conn.execute("SELECT AVG(valeur) FROM estimations_reprise WHERE horodatage <= ?", (t,)).fetchone()[0]
    kpis = [{"libelle": "Estimations demandées", "valeur": _sep(n / ech)},
            {"libelle": "Valeur moyenne de reprise", "valeur": euros(moy or 0)},
            {"libelle": "Modèle le plus repris", "valeur": (conn.execute(
                "SELECT modele FROM estimations_reprise WHERE horodatage <= ? GROUP BY modele ORDER BY COUNT(*) DESC "
                "LIMIT 1", (t,)).fetchone() or ["—"])[0]}]
    tables = [{"id": "grille", "titre": "Grille de reprise (valeurs en parfait état)", "flux": "FE-10R",
               "colonnes": [("modele", "Modèle"), ("marque", "Marque"), ("valeur", "Valeur (€)"), ("maj_le", "Mise à jour")],
               "lignes": _rows(conn, "SELECT * FROM reprise_grille ORDER BY valeur DESC")}]
    modeles = [r["modele"] for r in conn.execute("SELECT modele FROM reprise_grille ORDER BY valeur DESC")]
    actions = [{"code": "grille", "libelle": "Mettre à jour une valeur de reprise", "flux": "FE-10R",
                "description": "La nouvelle valeur s'affiche immédiatement dans le configurateur d'apple.com.",
                "champs": [_champ("modele", "Modèle", "select", modeles),
                           _champ("valeur", "Nouvelle valeur (€)", "number", defaut=300)]}]
    return kpis, tables, actions


def _reprise_action(conn, t, code, d):
    v = float(d["valeur"])
    if v < 0 or v > 1500:
        raise ValueError("Valeur hors limites.")
    conn.execute("UPDATE reprise_grille SET valeur=?, maj_le=? WHERE modele=?", (v, t, d["modele"]))
    emettre(conn, "FE-10R", "Nouvelle valeur de reprise : %s → %s" % (d["modele"], euros(v)), t,
            emetteur="partenaire_reprise", lien="/a/client/configurateur", demo=1)
    return "Grille mise à jour : le configurateur client utilise déjà la nouvelle valeur (flux FE-10R)."


# =========================================================================== régulateurs (FE-11)
def _regulateur(conn, t):
    regl = _rows(conn, "SELECT * FROM reglementation WHERE horodatage <= ? ORDER BY horodatage DESC", (t,))
    kpis = [{"libelle": "Déclarations reçues d'Apple", "valeur": str(sum(1 for r in regl if r["sens"] == "declaration"))},
            {"libelle": "Règles applicables publiées", "valeur": str(sum(1 for r in regl if r["sens"] == "regle"))},
            {"libelle": "Amende DMA (avril 2025)", "valeur": "500 M€", "aide": "Contestée par Apple (dossier, SWOT)."}]
    tables = [{"id": "registre", "titre": "Déclarations (FE-11A) et règles (FE-11R)", "flux": "FE-11A",
               "colonnes": [("horodatage", "Date"), ("autorite", "Autorité"), ("sens", "Type"), ("titre", "Objet"),
                            ("statut", "Statut")], "lignes": regl}]
    actions = [{"code": "regle", "libelle": "Publier une règle ou une recommandation", "flux": "FE-11R",
                "description": "Le juridique d'Apple est notifié et doit adapter les traitements.",
                "champs": [_champ("autorite", "Autorité", "select", ["CNIL", "Commission européenne"]),
                           _champ("titre", "Objet", defaut="Rappel : consentement au ciblage publicitaire"),
                           _champ("contenu", "Contenu", "textarea",
                                  defaut="Les campagnes ciblées doivent reposer sur un consentement explicite.")]}]
    return kpis, tables, actions


def _regulateur_action(conn, t, code, d):
    conn.execute("INSERT INTO reglementation(autorite, sens, titre, contenu, horodatage, statut, demo) VALUES "
                 "(?,?,?,?,?,?,1)", (d["autorite"], "regle", d["titre"][:120], d["contenu"][:500], t, "applicable"))
    emettre(conn, "FE-11R", "%s : %s" % (d["autorite"], d["titre"][:120]), t, emetteur="regulateur",
            lien="/a/juridique/conformite", demo=1)
    return "Règle publiée et transmise au juridique d'Apple (flux FE-11R)."


# =========================================================================== concurrents (FE-12, indirect)
def _concurrent(conn, t):
    veille = _rows(conn, "SELECT * FROM veille WHERE releve_le <= ? ORDER BY releve_le DESC, prix DESC", (t,))
    for v in veille:
        v["ecart"] = euros(2339 - v["prix"])
        v["prix_txt"] = euros(v["prix"])
    derniers = {}
    for v in veille:
        derniers.setdefault(v["produit"], v)
    kpis = [{"libelle": "Prix d'entrée iPhone Duo", "valeur": euros(2339)},
            {"libelle": "Pliable concurrent le moins cher", "valeur": euros(min((v["prix"] for v in derniers.values()),
                                                                              default=0))},
            {"libelle": "Relevés de veille", "valeur": str(len(veille)),
             "aide": "Flux indirect : Apple observe, sans échange avec ses concurrents."}]
    tables = [{"id": "veille", "titre": "Relevés de prix des pliables concurrents (flux FE-12R, pointillés)",
               "flux": "FE-12R", "colonnes": [("releve_le", "Relevé le"), ("concurrent", "Concurrent"),
                                              ("produit", "Produit"), ("prix_txt", "Prix"), ("ecart", "Écart avec l'iPhone Duo"),
                                              ("commentaire", "Commentaire")], "lignes": veille}]
    actions = [{"code": "releve", "libelle": "Enregistrer un relevé de veille (par l'équipe data d'Apple)",
                "flux": "FE-12R", "description": "Le concurrent n'agit pas : c'est Apple qui observe (flèche en pointillés).",
                "champs": [_champ("concurrent", "Concurrent", "select", ["Samsung", "Google", "Huawei", "Honor"]),
                           _champ("produit", "Produit", defaut="Galaxy Z Fold (génération 2026)"),
                           _champ("prix", "Prix relevé (€)", "number", defaut=1899)]}]
    return kpis, tables, actions


def _concurrent_action(conn, t, code, d):
    conn.execute("INSERT INTO veille(concurrent, produit, prix, releve_le, source, commentaire) VALUES (?,?,?,?,?,?)",
                 (d["concurrent"], d["produit"][:80], float(d["prix"]), t, "Relevé manuel (équipe data)", None))
    emettre(conn, "FE-12R", "Veille : %s %s à %s" % (d["concurrent"], d["produit"][:60], euros(float(d["prix"]))), t,
            emetteur="concurrent", recepteur="mkt_data", demo=1)
    return "Relevé enregistré (flux indirect FE-12R)."


# =========================================================================== création (FM-07 / FM-10 / FM-11)
def _creation(conn, t):
    contenus = _rows(conn, "SELECT * FROM contenus_creation WHERE COALESCE(brief_le, livre_le) <= ? "
                           "ORDER BY COALESCE(livre_le, brief_le) DESC LIMIT 20", (t,))
    for c in contenus:
        if c["livre_le"] and c["livre_le"] > t:
            c["livre_le"], c["statut"] = None, "en_production"
    kpis = [{"libelle": "Contenus livrés", "valeur": str(sum(1 for c in contenus if c["statut"] == "livré"))},
            {"libelle": "En production", "valeur": str(sum(1 for c in contenus if c["statut"] != "livré"))},
            {"libelle": "Dernier brief créatif (FM-07)", "valeur": "3 sept.", "aide": "Usages du pliable, ton humoristique."}]
    tables = [{"id": "contenus", "titre": "Contenus créatifs", "flux": "FM-10",
               "colonnes": [("brief_le", "Brief le"), ("type", "Type"), ("titre", "Contenu"), ("destinataire", "Destinataire"),
                            ("statut", "Statut"), ("livre_le", "Livré le")], "lignes": contenus,
               "action_ligne": {"code": "livrer", "libelle": "Livrer", "condition": {"statut": ["en_production"]},
                                "champs": []}}]
    actions = [{"code": "nouveau", "libelle": "Livrer un nouveau contenu", "flux": "FM-10",
                "description": "Vidéo -> équipe réseaux sociaux (FM-10) ; page produit -> équipe e-commerce (FM-11).",
                "champs": [_champ("type", "Type", "select", ["Vidéo TikTok", "Page produit", "Visuels"]),
                           _champ("titre", "Titre", defaut="L'iPhone Duo au bureau")]}]
    return kpis, tables, actions


def _creation_action(conn, t, code, d):
    if code == "livrer":
        c = conn.execute("SELECT * FROM contenus_creation WHERE id=?", (int(d["id"]),)).fetchone()
        typ, titre = c["type"], c["titre"]
        conn.execute("UPDATE contenus_creation SET statut='livré', livre_le=? WHERE id=?", (t, c["id"]))
    else:
        typ, titre = d["type"], d["titre"][:80]
        dest = {"Vidéo TikTok": "mkt_social", "Page produit": "mkt_ecommerce"}.get(typ, "mkt_retail")
        conn.execute("INSERT INTO contenus_creation(type, titre, statut, destinataire, brief_le, livre_le, demo) "
                     "VALUES (?,?,?,?,?,?,1)", (typ, titre, "livré", dest, t, t))
    code_flux = "FM-11" if typ == "Page produit" else "FM-10"
    emettre(conn, code_flux, "%s livré(e) : %s" % (typ, titre), t, emetteur="mkt_creation",
            recepteur="mkt_ecommerce" if code_flux == "FM-11" else "mkt_social", demo=1)
    return "Contenu livré (flux %s)." % code_flux


# =========================================================================== presse (FM-05 / FM-12)
def _presse(conn, t):
    ret = _rows(conn, "SELECT * FROM retombees_presse WHERE publie_le <= ? ORDER BY publie_le DESC", (t,))
    pos = sum(1 for r in ret if r["tonalite"] == "positive")
    kpis = [{"libelle": "Retombées presse", "valeur": str(len(ret))},
            {"libelle": "Audience cumulée", "valeur": _sep(sum(r["audience"] for r in ret))},
            {"libelle": "Tonalité positive", "valeur": ("%d %%" % round(100.0 * pos / len(ret))) if ret else "—"}]
    tables = [{"id": "retombees", "titre": "Retombées transmises à l'équipe data (flux FM-12)", "flux": "FM-12",
               "colonnes": [("publie_le", "Date"), ("media", "Média"), ("titre", "Titre"), ("tonalite", "Tonalité"),
                            ("audience", "Audience")], "lignes": ret}]
    actions = [{"code": "retombee", "libelle": "Enregistrer une retombée presse", "flux": "FM-12",
                "description": "La retombée alimente le tableau de bord hebdomadaire (FM-17).",
                "champs": [_champ("media", "Média", defaut="Magazine tech"),
                           _champ("titre", "Titre", defaut="L'iPhone Duo, un mois après"),
                           _champ("tonalite", "Tonalité", "select", ["positive", "neutre", "negative"]),
                           _champ("audience", "Audience estimée", "number", defaut=250000)]},
               {"code": "invitation", "libelle": "Envoyer une invitation / un test presse", "flux": "FE-06A",
                "description": "Contenus et invitations envoyés aux médias (diagramme de contexte).",
                "champs": [_champ("objet", "Objet", defaut="Prêt d'un iPhone Duo pour un test de 15 jours")]}]
    return kpis, tables, actions


def _presse_action(conn, t, code, d):
    if code == "retombee":
        conn.execute("INSERT INTO retombees_presse(media, titre, tonalite, audience, publie_le, demo) VALUES (?,?,?,?,?,1)",
                     (d["media"][:60], d["titre"][:120], d["tonalite"], int(d["audience"]), t))
        emettre(conn, "FM-12", "Retombée presse : %s — %s" % (d["media"][:60], d["titre"][:120]), t,
                emetteur="mkt_presse", recepteur="mkt_data", demo=1)
        return "Retombée transmise à l'équipe data (flux FM-12)."
    emettre(conn, "FE-06A", "Invitation presse : %s" % d["objet"][:120], t, emetteur="mkt_presse",
            recepteur="influenceur", demo=1)
    return "Invitation envoyée (flux FE-06A)."


# =========================================================================== Apple Store (FM-09 / FM-16)
def _retail(conn, t):
    jour = t[:10]
    rdv_jour = _rows(conn, "SELECT r.*, c.prenom || ' ' || substr(c.nom,1,1) || '.' AS client FROM rdv_demo r "
                           "LEFT JOIN clients c ON c.id = r.client_id WHERE substr(r.creneau,1,10) = ? "
                           "ORDER BY r.creneau LIMIT 30", (jour,))
    for r in rdv_jour:
        if r["creneau"] > t:
            r["statut"], r["note_essai"], r["intention"] = "planifié", None, None
    from .kpi import cumul
    notes = conn.execute("SELECT AVG(note_essai) FROM rdv_demo WHERE creneau <= ? AND note_essai IS NOT NULL",
                         (t,)).fetchone()[0]
    kpis = [{"libelle": "Rendez-vous cumulés (France)", "valeur": _sep(cumul(conn, "rdv_demo", t))},
            {"libelle": "Rendez-vous aujourd'hui (échantillon)", "valeur": str(len(rdv_jour))},
            {"libelle": "Note moyenne des essais", "valeur": ("%.1f / 5" % notes).replace(".", ",") if notes else "—"},
            {"libelle": "Plan de démonstrations (FM-09)", "valeur": "depuis le 18/09"}]
    tables = [{"id": "rdv", "titre": "Rendez-vous de démonstration du jour", "flux": "FM-16",
               "colonnes": [("creneau", "Créneau"), ("magasin", "Apple Store"), ("client", "Client"),
                            ("statut", "Statut"), ("note_essai", "Note"), ("intention", "Intention après essai")],
               "lignes": rdv_jour, "vide": "Aucun rendez-vous dans l'échantillon pour cette date."}]
    actions = [{"code": "essais", "libelle": "Remonter les essais du jour", "flux": "FM-16",
                "description": "Essais et rendez-vous sont un indicateur avancé du tableau de bord.",
                "champs": [_champ("magasin", "Apple Store", "select", APPLE_STORES_FR),
                           _champ("essais", "Nombre d'essais", "number", defaut=48)]}]
    return kpis, tables, actions


def _retail_action(conn, t, code, d):
    n = int(d["essais"])
    conn.execute("INSERT INTO kpi_journalier(jour, pays, indicateur, valeur) VALUES (?,?,?,?) ON CONFLICT(jour, pays, "
                 "indicateur) DO UPDATE SET valeur = valeur + ?", (t[:10], "FR", "rdv_demo", n, n))
    emettre(conn, "FM-16", "%s : %d essais en magasin remontés" % (d["magasin"], n), t, emetteur="mkt_retail",
            recepteur="mkt_data", demo=1)
    return "Essais transmis à l'équipe data (flux FM-16) : le cockpit est mis à jour."


# =========================================================================== ingénierie (§ 3.4)
def _ingenierie(conn, t):
    esc = _rows(conn, "SELECT * FROM demandes_sav WHERE escalade IS NOT NULL AND cree_le <= ? ORDER BY cree_le DESC", (t,))
    kpis = [{"libelle": "Puce", "valeur": PRODUIT["puce"]}, {"libelle": "Système", "valeur": PRODUIT["os"]},
            {"libelle": "Remontées clients escaladées", "valeur": str(len(esc))}]
    tables = [{"id": "arguments", "titre": "Caractéristiques transmises au marketing (arguments de vente)", "flux": "FI-14",
               "colonnes": [("argument", "Caractéristique"), ("usage", "Argument marketing")],
               "lignes": [{"argument": a, "usage": u} for a, u in PRODUIT["arguments"]]},
              {"id": "escalades", "titre": "Attentes et retours clients reçus", "flux": "FI-15",
               "colonnes": [("cree_le", "Date"), ("sujet", "Sujet"), ("canal", "Canal"), ("statut", "Statut")],
               "lignes": esc, "vide": "Aucune escalade à cette date."}]
    actions = [{"code": "argument", "libelle": "Transmettre une caractéristique au marketing", "flux": "FI-14",
                "description": "Les ingénieurs fournissent les caractéristiques qui deviennent des arguments de vente.",
                "champs": [_champ("titre", "Caractéristique", defaut="Charnière testée pour 200 000 pliages"),
                           _champ("usage", "Argument proposé", defaut="Rassurer sur la durabilité")]}]
    return kpis, tables, actions


def _ingenierie_action(conn, t, code, d):
    emettre(conn, "FI-14", "Caractéristique : %s — %s" % (d["titre"][:100], d["usage"][:100]), t,
            emetteur="ingenierie", recepteur="dir_marketing", demo=1)
    return "Caractéristique transmise à la direction marketing (flux FI-14)."


# =========================================================================== juridique (§ 3.4, FE-11)
def _juridique(conn, t):
    vals = _rows(conn, "SELECT * FROM validations_juridiques WHERE cree_le <= ? ORDER BY CASE WHEN statut='en_attente' "
                       "THEN 0 ELSE 1 END, cree_le DESC", (t,))
    for v in vals:
        if v["decide_le"] and v["decide_le"] > t:
            v["statut"], v["decide_le"], v["commentaire"] = "en_attente", None, None
    regl = _rows(conn, "SELECT * FROM reglementation WHERE horodatage <= ? ORDER BY horodatage DESC", (t,))
    kpis = [{"libelle": "Validations en attente", "valeur": str(sum(1 for v in vals if v["statut"] == "en_attente"))},
            {"libelle": "Validations rendues", "valeur": str(sum(1 for v in vals if v["statut"] != "en_attente"))},
            {"libelle": "Règles applicables (RGPD, DMA)", "valeur": str(sum(1 for r in regl if r["sens"] == "regle"))}]
    tables = [{"id": "validations", "titre": "Messages publicitaires et contrats à valider (flux FI-16)", "flux": "FI-16",
               "colonnes": [("cree_le", "Reçu le"), ("objet", "Objet"), ("type", "Type"), ("demandeur", "Demandeur"),
                            ("statut", "Statut"), ("commentaire", "Avis")], "lignes": vals,
               "action_ligne": {"code": "valider", "libelle": "Rendre l'avis", "condition": {"statut": ["en_attente"]},
                                "champs": [_champ("decision", "Décision", "select", [["validee", "Valider"],
                                                                                       ["refusee", "Refuser"]]),
                                           _champ("commentaire", "Commentaire", "textarea",
                                                  defaut="Ajouter la mention « collaboration commerciale ».")]}},
              {"id": "registre", "titre": "Échanges avec les régulateurs (FE-11A / FE-11R)", "flux": "FE-11A",
               "colonnes": [("horodatage", "Date"), ("autorite", "Autorité"), ("sens", "Type"), ("titre", "Objet")],
               "lignes": regl}]
    actions = [{"code": "declaration", "libelle": "Transmettre une déclaration au régulateur", "flux": "FE-11A",
                "description": "Registre des traitements, analyse d'impact, rapport DMA…",
                "champs": [_champ("autorite", "Autorité", "select", ["CNIL", "Commission européenne"]),
                           _champ("titre", "Objet", defaut="Mise à jour du registre : campagne de relance")]}]
    return kpis, tables, actions


def _juridique_action(conn, t, code, d):
    if code == "valider":
        vid = int(d["id"])
        conn.execute("UPDATE validations_juridiques SET statut=?, decide_le=?, commentaire=? WHERE id=?",
                     (d["decision"], t, (d.get("commentaire") or "")[:300], vid))
        objet = conn.execute("SELECT objet FROM validations_juridiques WHERE id=?", (vid,)).fetchone()[0]
        emettre(conn, "FI-17", "Avis juridique (%s) : %s" % ("validé" if d["decision"] == "validee" else "refusé", objet),
                t, emetteur="juridique", recepteur="dir_marketing", demo=1)
        return "Avis transmis au marketing (flux FI-17)."
    conn.execute("INSERT INTO reglementation(autorite, sens, titre, contenu, horodatage, statut, demo) VALUES "
                 "(?,?,?,?,?,?,1)", (d["autorite"], "declaration", d["titre"][:120], "", t, "transmise"))
    emettre(conn, "FE-11A", "Déclaration à %s : %s" % (d["autorite"], d["titre"][:120]), t, emetteur="juridique",
            recepteur="regulateur", demo=1)
    return "Déclaration transmise (flux FE-11A)."


# =========================================================================== AppleCare (§ 3.6)
def _applecare(conn, t):
    dem = _rows(conn, "SELECT * FROM demandes_sav WHERE cree_le <= ? ORDER BY cree_le DESC LIMIT 20", (t,))
    for x in dem:
        if x["statut"] == "résolu" and x["cree_le"] > fmt(parse(t) - timedelta(hours=6)):
            x["statut"] = "en cours"
    sat = conn.execute("SELECT AVG(satisfaction) FROM demandes_sav WHERE cree_le <= ? AND satisfaction IS NOT NULL",
                       (t,)).fetchone()[0]
    sujets = _rows(conn, "SELECT sujet, COUNT(*) n FROM demandes_sav WHERE cree_le <= ? GROUP BY sujet ORDER BY n DESC "
                         "LIMIT 5", (t,))
    kpis = [{"libelle": "Demandes clients", "valeur": str(_n(conn, "SELECT COUNT(*) FROM demandes_sav WHERE cree_le <= ?",
                                                               (t,)))},
            {"libelle": "Satisfaction moyenne", "valeur": ("%.1f / 5" % sat).replace(".", ",") if sat else "—"},
            {"libelle": "Sujet n°1", "valeur": sujets[0]["sujet"] if sujets else "—"}]
    tables = [{"id": "demandes", "titre": "Demandes des clients (flux FE-01R)", "flux": "FE-01R",
               "colonnes": [("cree_le", "Date"), ("sujet", "Sujet"), ("canal", "Canal"), ("statut", "Statut"),
                            ("satisfaction", "Satisfaction")], "lignes": dem,
               "action_ligne": {"code": "clore", "libelle": "Clôturer", "condition": {"statut": ["en cours"]},
                                "champs": [_champ("satisfaction", "Satisfaction (1-5)", "number", defaut=5)]}}]
    actions = [{"code": "synthese", "libelle": "Remonter une synthèse au marketing", "flux": "FI-18",
                "description": "Les retours clients aident le marketing à ajuster son message.",
                "champs": [_champ("message", "Synthèse", "textarea",
                                  defaut="Questions fréquentes sur la pliure visible : prévoir une FAQ vidéo.")]}]
    return kpis, tables, actions


def _applecare_action(conn, t, code, d):
    if code == "clore":
        conn.execute("UPDATE demandes_sav SET statut='résolu', satisfaction=? WHERE id=?",
                     (max(1, min(5, int(d["satisfaction"]))), int(d["id"])))
        return "Demande clôturée."
    emettre(conn, "FI-18", "Retours clients : %s" % d["message"][:160], t, emetteur="applecare",
            recepteur="dir_marketing", demo=1)
    return "Synthèse transmise à la direction marketing (flux FI-18)."


# =========================================================================== influenceurs (P2-T05)
def _influenceur(conn, t):
    collab = _rows(conn, "SELECT ci.*, i.pseudo, i.plateforme, i.abonnes, c.nom AS campagne, c.id AS campagne_id_ "
                         "FROM campagne_influenceurs ci JOIN influenceurs i ON i.id=ci.influenceur_id JOIN campagnes c "
                         "ON c.id=ci.campagne_id WHERE ci.selectionne_le <= ? ORDER BY ci.selectionne_le DESC, i.abonnes DESC",
                   (t,))
    for c in collab:
        if c["appareil_expedie_le"] and c["appareil_expedie_le"] > t:
            c["appareil_expedie_le"] = None
        if c["avis_publie_le"] and c["avis_publie_le"] > t:
            c["avis_publie_le"] = None
        c["id"] = "%d-%d" % (c["campagne_id"], c["influenceur_id"])
        c["etat"] = ("avis publié" if c["avis_publie_le"] else
                     ("appareil reçu — avis attendu" if c["appareil_expedie_le"] else "en attente de l'appareil"))
        c["abonnes_txt"] = _sep(c["abonnes"])
    publies = sum(1 for c in collab if c["avis_publie_le"])
    kpis = [{"libelle": "Collaborations", "valeur": str(len(collab))},
            {"libelle": "Avis publiés", "valeur": str(publies)},
            {"libelle": "Avis attendus (P2-T05)", "valeur": str(sum(1 for c in collab if c["etat"].startswith("appareil")))}]
    tables = [{"id": "collaborations", "titre": "Collaborations : invitations, appareils de test, avis", "flux": "FE-06R",
               "colonnes": [("campagne", "Campagne"), ("pseudo", "Créateur"), ("plateforme", "Plateforme"),
                            ("abonnes_txt", "Abonnés"), ("etat", "État"), ("avis_publie_le", "Avis publié le")],
               "lignes": collab,
               "action_ligne": {"code": "avis", "libelle": "Publier mon avis (P2-T05)",
                                "condition": {"etat": ["appareil reçu — avis attendu"]},
                                "champs": [_champ("titre", "Titre de la publication",
                                                  defaut="Une semaine avec l'iPhone Duo : mon verdict"),
                                           _champ("sentiment", "Tonalité positive des commentaires (%)", "number",
                                                  defaut=72)]}}]
    return kpis, tables, []


def _influenceur_action(conn, t, code, d):
    cid, iid = [int(x) for x in str(d["id"]).split("-")]
    svc_camp.publier_avis(conn, cid, iid, t, d.get("titre") or "", float(d.get("sentiment") or 70))
    return "Avis publié : la tâche P2-T05 avance et le marketing est notifié (flux FE-06R)."


PORTAILS: Dict[str, tuple] = {
    "operateur": (_operateur, _operateur_action),
    "revendeur": (_revendeur, _revendeur_action),
    "fournisseur": (_fournisseur, _fournisseur_action),
    "developpeur": (_developpeur, _developpeur_action),
    "agence": (_agence, _agence_action),
    "institut": (_institut, _institut_action),
    "organisme_financier": (_organisme, _organisme_action),
    "partenaire_reprise": (_reprise, _reprise_action),
    "regulateur": (_regulateur, _regulateur_action),
    "concurrent": (_concurrent, _concurrent_action),
    "mkt_creation": (_creation, _creation_action),
    "mkt_presse": (_presse, _presse_action),
    "mkt_retail": (_retail, _retail_action),
    "ingenierie": (_ingenierie, _ingenierie_action),
    "juridique": (_juridique, _juridique_action),
    "applecare": (_applecare, _applecare_action),
    "influenceur": (_influenceur, _influenceur_action),
}


def donnees(conn, acteur: str, t: str) -> dict:
    if acteur not in PORTAILS:
        raise KeyError("Pas de portail pour %s" % acteur)
    kpis, tables, actions = PORTAILS[acteur][0](conn, t)
    for tb in tables:
        tb["colonnes"] = [{"cle": c, "libelle": l} for (c, l) in tb["colonnes"]]
    return {"kpis": kpis, "tables": tables, "actions": actions}


def executer(conn, acteur: str, code: str, t: str, d: dict) -> str:
    if acteur not in PORTAILS:
        raise KeyError("Pas de portail pour %s" % acteur)
    try:
        return PORTAILS[acteur][1](conn, t, code, d)
    except (KeyError, IndexError, TypeError) as e:
        raise ValueError("Données incomplètes : %s" % e)
