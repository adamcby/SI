"""Processus P1 — gestion des précommandes (Fig. 4), une instance BPMN par précommande.

Couloir Client      : T01 choisit sa configuration, T03 valide la précommande, T09 reçoit la confirmation
Couloir Marketing   : T02 affiche prix et délai (automatisé), T06 enregistre la précommande (CRM, automatisé)
Couloir Finance     : G01 paiement accepté ?, T04 CA prévisionnel, T05 marge et coût par précommande
Couloir Production  : G02 stock disponible ?, T07 allonge le délai affiché, T08 réserve un appareil
"""
from datetime import timedelta
from typing import Optional

from ..bus import emettre
from ..db import ecrire_parametre, lire_parametre
from ..horloge import fmt, parse
from ..metier import (CAPACITES, COLORIS, SORTIE, chiffrer, euros, ht, libelle_delai, prochain_lot)
from ..moteur import TransitionInvalide, charger_etat, creer_instance, enregistrer
from ..referentiel import PRODUIT
from ..seed_donnees import ETATS_REPRISE, MODES_PAIEMENT

SEUIL_ETUDE_CREDIT = 3000.0  # au-delà, l'organisme financier étudie manuellement la demande

STATUTS = {
    "attente_credit": ("En attente de l'organisme financier", "P1-G01"),
    "controle_paiement": ("Vérification du paiement (finance)", "P1-G01"),
    "paiement_refuse": ("Paiement refusé — à reconfigurer", "P1-T01"),
    "payee": ("Payée — vérification du stock (production)", "P1-G02"),
    "delai_a_allonger": ("Stock insuffisant — délai à allonger", "P1-T07"),
    "a_reserver": ("Appareil à réserver (production)", "P1-T08"),
    "confirmee": ("Confirmée", "P1-T09"),
    "abandonnee": ("Abandonnée", None),
}


def _p(conn, pid: int):
    row = conn.execute("SELECT * FROM precommandes WHERE id = ?", (pid,)).fetchone()
    if row is None:
        raise KeyError("Précommande %s introuvable" % pid)
    return row


def _maj(conn, pid: int, t: str, **champs):
    champs["maj_le"] = t
    cols = ", ".join("%s = ?" % k for k in champs)
    conn.execute("UPDATE precommandes SET %s WHERE id = ?" % cols, list(champs.values()) + [pid])


def _reference(conn) -> str:
    n = int(lire_parametre(conn, "seq_reference", "190000")) + 1
    ecrire_parametre(conn, "seq_reference", n)
    return "W%d" % n


def valeur_reprise(conn, modele: Optional[str], etat: Optional[str]) -> float:
    if not modele:
        return 0.0
    row = conn.execute("SELECT valeur FROM reprise_grille WHERE modele = ?", (modele,)).fetchone()
    base = row["valeur"] if row else 40.0
    facteur = next((f for (e, _l, f) in ETATS_REPRISE if e == etat), 0.85)
    return float(round(base * facteur / 5) * 5)


def _fx(conn, code, objet, t, pid, inst, noeud, **kw):
    lien = kw.pop("lien", None)
    return emettre(conn, code, objet, t, processus="P1", noeud=noeud, instance_id=inst, lien=lien,
                   demo=kw.pop("demo", 0), **kw)


# --------------------------------------------------------------------------- T01 + T02 + T03
def creer_precommande(conn, t: str, capacite: str, coloris: str, paiement_mode: str,
                      client_id: Optional[int] = None, client: Optional[dict] = None,
                      applecare: bool = False, reprise_modele: Optional[str] = None,
                      reprise_etat: Optional[str] = None, livraison_mode: str = "domicile",
                      magasin: Optional[str] = None, canal: str = "apple.com", mode: Optional[str] = None,
                      simuler_refus: bool = False, controle_renforce: bool = False, seed: bool = False,
                      montant_credit_force: Optional[float] = None, demo: int = 1) -> dict:
    if capacite not in CAPACITES or coloris not in COLORIS:
        raise ValueError("Configuration inconnue.")
    if paiement_mode not in MODES_PAIEMENT:
        raise ValueError("Mode de paiement inconnu.")
    if parse(t) < parse("2026-10-16T14:00:00"):
        raise TransitionInvalide("Les précommandes ouvrent le vendredi 16 octobre à 14 h (événement de début de P1).")
    if client_id is None:
        client_id = _creer_client(conn, client or {}, t, demo)
    cl = conn.execute("SELECT * FROM clients WHERE id = ?", (client_id,)).fetchone()
    if cl is None:
        raise KeyError("Client introuvable")
    mode = mode or lire_parametre(conn, "mode_execution", "pas_a_pas")
    demo = 0 if seed else demo
    ref = _reference(conn)
    inst = creer_instance(conn, "P1", "precommande", "Précommande %s" % ref, t, "client", demo=demo,
                          declencheur="Ouverture des précommandes (16/10, 14 h)")
    ch = chiffrer(capacite, applecare, conn)
    reprise_val = valeur_reprise(conn, reprise_modele, reprise_etat)
    lot = prochain_lot(conn, capacite, coloris, t)
    delai = libelle_delai(lot["date"], livraison_mode, parse(t))
    cur = conn.execute(
        "INSERT INTO precommandes(reference, client_id, instance_id, pays, canal, capacite, coloris, prix_ttc, prix_ht, "
        "applecare, applecare_ttc, reprise_modele, reprise_etat, reprise_valeur, paiement_mode, paiement_statut, "
        "livraison_mode, magasin, delai_affiche, statut, cree_le, maj_le, demo) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (ref, client_id, inst, "FR", canal, capacite, coloris, ch["prix_ttc"], ht(ch["prix_ttc"]), int(applecare),
         ch["applecare_ttc"], reprise_modele, reprise_etat if reprise_modele else None, reprise_val, paiement_mode,
         "en_attente", livraison_mode, magasin, delai, "controle_paiement", t, t, demo))
    pid = cur.lastrowid
    conn.execute("UPDATE instances SET objet_id = ? WHERE id = ?", (pid, inst))
    lib_conf = "iPhone Duo %s %s" % (CAPACITES[capacite]["libelle"], COLORIS[coloris]["libelle"])
    # T01 — le client choisit sa configuration (flux FE-01R ; FE-10 si reprise)
    enregistrer(conn, inst, "T01", t, "client", details=lib_conf)
    if reprise_modele:
        _fx(conn, "FE-10A", "Estimation de reprise demandée : %s" % reprise_modele, t, pid, inst, "T01", demo=demo,
            notifier=not seed)
        _fx(conn, "FE-10R", "Valeur de reprise : %s (%s)" % (euros(reprise_val), reprise_modele), t, pid, inst, "T01",
            demo=demo, notifier=False)
        conn.execute("INSERT INTO estimations_reprise(modele, etat, valeur, horodatage) VALUES (?,?,?,?)",
                     (reprise_modele, reprise_etat or "bon", reprise_val, t))
    # T02 — le site affiche prix et délai (tâche automatisée, couloir marketing / e-commerce)
    enregistrer(conn, inst, "T02", t, "mkt_ecommerce",
                details="%s TTC — %s" % (euros(ch["prix_ttc"] + ch["applecare_ttc"]), delai))
    _fx(conn, "FE-01A", "Prix et délai affichés : %s — %s" % (euros(ch["prix_ttc"]), delai), t, pid, inst, "T02",
        demo=demo, notifier=False)
    # T03 — le client valide la précommande
    enregistrer(conn, inst, "T03", t, "client", details="Précommande %s validée" % ref)
    _fx(conn, "FE-01R", "Précommande %s validée par %s %s (%s)" % (ref, cl["prenom"], cl["nom"], lib_conf), t, pid,
        inst, "T03", demo=demo, notifier=not seed, lien="/a/mkt_data/crm")
    # Autorisation de paiement (flux FE-09 avec l'organisme financier)
    montant = ch["prix_ttc"] + ch["applecare_ttc"] - reprise_val
    if paiement_mode.startswith("cetelem"):
        montant_dc = montant_credit_force or montant
        etude = montant_dc > SEUIL_ETUDE_CREDIT and not simuler_refus
        statut_dc = "etude" if etude else ("refuse" if simuler_refus else "accorde")
        conn.execute("INSERT INTO demandes_credit(precommande_id, organisme, produit, montant, duree_mois, statut, "
                     "cree_le, decide_le, motif) VALUES (?,?,?,?,?,?,?,?,?)",
                     (pid, "Cetelem", "10 fois sans frais" if paiement_mode == "cetelem_10x" else "Crédit 24 mois",
                      montant_dc, 10 if paiement_mode == "cetelem_10x" else 24, statut_dc, t,
                      None if etude else t, "Score insuffisant (simulation)" if simuler_refus else None))
        _fx(conn, "FE-09A", "Demande de crédit %s : %s sur %d mois" %
            (ref, euros(montant_dc), 10 if paiement_mode == "cetelem_10x" else 24), t, pid, inst, "T03",
            demo=demo, lien="/a/organisme_financier/portail")
        if etude:
            _maj(conn, pid, t, statut="attente_credit")
            return dict(_p(conn, pid))
        _fx(conn, "FE-09R", "Crédit %s pour %s" % ("refusé" if simuler_refus else "accordé", ref), t, pid, inst, "G01",
            demo=demo, notifier=False)
    else:
        _fx(conn, "FE-09R", "Autorisation bancaire %s (%s)" %
            ("refusée" if simuler_refus else "accordée", MODES_PAIEMENT[paiement_mode]), t, pid, inst, "G01",
            demo=demo, notifier=False)
    _maj(conn, pid, t, paiement_statut="autorise" if not simuler_refus else "refus_banque",
         motif="Contrôle renforcé : adresse de livraison différente de l'adresse de facturation"
         if controle_renforce else None)
    if mode == "automatique" and not controle_renforce:
        traiter_automatiquement(conn, pid, t)
    else:
        _fx(conn, "FI-12", "Paiement de %s à vérifier (%s)" % (ref, euros(montant)), t, pid, inst, "G01",
            demo=demo, emetteur="si", recepteur="finance", lien="/a/finance/paiements")
    return dict(_p(conn, pid))


def _creer_client(conn, c: dict, t: str, demo: int) -> int:
    prenom = (c.get("prenom") or "Léa").strip()[:40]
    nom = (c.get("nom") or "Martin").strip()[:40]
    email = (c.get("email") or "").strip()[:80]
    if not email or conn.execute("SELECT 1 FROM clients WHERE apple_id = ?", (email,)).fetchone():
        base = "%s.%s" % (prenom.lower(), nom.lower())
        email = "%s.demo%d@icloud.com" % ("".join(ch for ch in base if ch.isalnum() or ch == "."),
                                          int(lire_parametre(conn, "seq_reference", "1")))
    appareil = c.get("appareil") or "iPhone 13 Pro"
    plateforme = "Android" if any(m in appareil for m in ("Samsung", "Google", "Xiaomi", "Huawei", "OnePlus")) else "iOS"
    cur = conn.execute(
        "INSERT INTO clients(apple_id, prenom, nom, age, ville, code_postal, segment, appareil, appareil_annee, "
        "plateforme, me_prevenir_le, consentement_marketing, abonnements, source, cree_le, demo) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (email, prenom, nom, int(c.get("age") or 29), c.get("ville") or "Lyon", c.get("code_postal") or "69003",
         "Particulier", appareil, None, plateforme, None, 1 if c.get("consentement") else 0, "", "apple.com", t, demo))
    return cur.lastrowid


# --------------------------------------------------------------------------- organisme financier (FE-09)
def decision_credit(conn, demande_id: int, issue: str, t: str, acteur: str = "organisme_financier") -> dict:
    d = conn.execute("SELECT * FROM demandes_credit WHERE id = ?", (demande_id,)).fetchone()
    if d is None:
        raise KeyError("Demande de crédit introuvable")
    if d["statut"] != "etude":
        raise TransitionInvalide("Cette demande a déjà été traitée (%s)." % d["statut"])
    if issue not in ("accorde", "refuse"):
        raise ValueError("Décision invalide")
    conn.execute("UPDATE demandes_credit SET statut=?, decide_le=?, motif=? WHERE id=?",
                 (issue, t, "Taux d'endettement trop élevé" if issue == "refuse" else None, demande_id))
    p = _p(conn, d["precommande_id"])
    _fx(conn, "FE-09R", "Crédit %s pour la précommande %s (%s)" %
        ("accordé" if issue == "accorde" else "refusé", p["reference"], euros(d["montant"])), t, p["id"],
        p["instance_id"], "G01", emetteur=acteur, recepteur="finance", lien="/a/finance/paiements", demo=p["demo"])
    _maj(conn, p["id"], t, statut="controle_paiement",
         paiement_statut="autorise" if issue == "accorde" else "refus_banque")
    if lire_parametre(conn, "mode_execution", "pas_a_pas") == "automatique":
        traiter_automatiquement(conn, p["id"], t)
    return dict(_p(conn, p["id"]))


# --------------------------------------------------------------------------- G01 + T04 + T05 + T06
def decision_paiement(conn, pid: int, issue: str, t: str, acteur: str = "finance", commentaire: str = "") -> dict:
    p = _p(conn, pid)
    if p["statut"] == "attente_credit":
        raise TransitionInvalide("La réponse de l'organisme financier (flux FE-09R) n'est pas encore arrivée.")
    inst = p["instance_id"]
    enregistrer(conn, inst, "G01", t, acteur, issue=issue, details=commentaire)
    if issue == "non":
        _maj(conn, pid, t, statut="paiement_refuse", paiement_statut="refuse",
             motif=commentaire or "Paiement refusé par la finance")
        _fx(conn, "FE-01A", "Paiement refusé pour %s : modifiez votre configuration ou votre moyen de paiement"
            % p["reference"], t, pid, inst, "G01", emetteur="finance", recepteur="client",
            lien="/a/client/commandes?ref=%s" % p["reference"], demo=p["demo"])
        return dict(_p(conn, pid))
    _maj(conn, pid, t, paiement_statut="accepte", paye_le=t)
    # T04 — CA prévisionnel (ERP) ; T05 — marge et coût par précommande
    ch = chiffrer(p["capacite"], bool(p["applecare"]), conn)
    enregistrer(conn, inst, "T04", t, "finance", details="CA prévisionnel : %s HT" % euros(ch["ca_ht"], 2))
    _fx(conn, "FI-12", "CA prévisionnel enregistré : %s HT (%s)" % (euros(ch["ca_ht"], 2), p["reference"]), t, pid,
        inst, "T04", emetteur="finance", recepteur="si", notifier=False, demo=p["demo"])
    cpp = cout_par_precommande(conn, t)
    enregistrer(conn, inst, "T05", t, "finance",
                details="Marge : %s ; coût marketing par précommande : %s" % (euros(ch["marge"], 2), euros(cpp, 2)))
    _maj(conn, pid, t, ca_previsionnel_ht=ch["ca_ht"], cout_revient=ch["cout_revient"], marge=ch["marge"],
         cout_par_precommande=cpp)
    _fx(conn, "FM-18", "Coût par précommande actualisé : %s" % euros(cpp, 2), t, pid, inst, "T05",
        emetteur="mkt_data", recepteur="finance", notifier=False, demo=p["demo"])
    # T06 — enregistrement CRM (automatisé) puis transmission à la production (FM-19)
    enregistrer(conn, inst, "T06", t, "mkt_data", details="Fiche client et précommande à jour dans le CRM")
    _maj(conn, pid, t, crm_le=t, statut="payee")
    _fx(conn, "FI-10", "Précommande %s enregistrée dans le CRM" % p["reference"], t, pid, inst, "T06",
        emetteur="mkt_data", recepteur="si", notifier=False, demo=p["demo"])
    _fx(conn, "FM-19", "Nouvelle précommande à servir : %s (%s %s)" %
        (p["reference"], CAPACITES[p["capacite"]]["libelle"], COLORIS[p["coloris"]]["libelle"]), t, pid, inst, "T06",
        emetteur="mkt_data", recepteur="production", lien="/a/production/stocks", demo=p["demo"])
    return dict(_p(conn, pid))


def cout_par_precommande(conn, t: str) -> float:
    jour = t[:10]
    row = conn.execute("SELECT valeur FROM kpi_journalier WHERE pays='FR' AND indicateur='depense_marketing' "
                       "AND jour <= ? ORDER BY jour DESC LIMIT 1", (jour,)).fetchone()
    dep = row["valeur"] if row else 0.0
    echelle = float(lire_parametre(conn, "echelle", "1") or 1)
    n = conn.execute("SELECT COUNT(*) FROM precommandes WHERE pays='FR' AND paye_le IS NOT NULL AND paye_le <= ?",
                     (t,)).fetchone()[0]
    return round(dep * echelle / max(1, n), 2)


# --------------------------------------------------------------------------- G02 + T07 + T08 + T09
def verifier_stock(conn, pid: int, t: str, acteur: str = "production") -> dict:
    p = _p(conn, pid)
    lot = prochain_lot(conn, p["capacite"], p["coloris"], t)
    issue = "oui" if lot["en_stock"] else "non"
    enregistrer(conn, p["instance_id"], "G02", t, acteur, issue=issue,
                details="Stock pour le %s : %s" % ("23/10" if parse(t) < SORTIE else "jour même",
                                                   "disponible" if issue == "oui" else "insuffisant"))
    _fx(conn, "FI-11", "Contrôle de stock %s : %s" % (p["reference"], "disponible" if issue == "oui" else "insuffisant"),
        t, pid, p["instance_id"], "G02", emetteur="production", recepteur="si", notifier=False, demo=p["demo"])
    _maj(conn, pid, t, statut="a_reserver" if issue == "oui" else "delai_a_allonger")
    return dict(_p(conn, pid), issue=issue, lot=lot)


def allonger_delai(conn, pid: int, t: str, acteur: str = "production") -> dict:
    p = _p(conn, pid)
    lot = prochain_lot(conn, p["capacite"], p["coloris"], t)
    delai = libelle_delai(lot["date"], p["livraison_mode"], parse(t))
    enregistrer(conn, p["instance_id"], "T07", t, acteur, details="Nouveau délai : %s" % delai)
    _maj(conn, pid, t, delai_affiche=delai, delai_allonge=1, statut="a_reserver")
    _fx(conn, "FI-05", "Date de livraison décalée pour %s : %s" % (p["reference"], delai), t, pid, p["instance_id"],
        "T07", emetteur="production", recepteur="mkt_ecommerce", lien="/a/mkt_ecommerce/precommandes", demo=p["demo"])
    return dict(_p(conn, pid))


def reserver(conn, pid: int, t: str, acteur: str = "production") -> dict:
    p = _p(conn, pid)
    lot = prochain_lot(conn, p["capacite"], p["coloris"], t)
    enregistrer(conn, p["instance_id"], "T08", t, acteur,
                details="Lot %s (disponible le %s)" % (lot["lot_id"], (lot["date"] or "—")[:10]))
    _maj(conn, pid, t, lot_id=lot["lot_id"], livraison_prevue=(lot["date"] or "")[:10] or None, reserve_le=t,
         statut="reservee")
    _fx(conn, "FI-11", "Appareil réservé pour %s (lot %s)" % (p["reference"], lot["lot_id"]), t, pid, p["instance_id"],
        "T08", emetteur="production", recepteur="si", notifier=False, demo=p["demo"])
    # T09 — le client reçoit la confirmation (automatique) -> événement de fin « 23/10 »
    p2 = _p(conn, pid)
    enregistrer(conn, p["instance_id"], "T09", t, "client", details=p2["delai_affiche"] or "")
    _maj(conn, pid, t, statut="confirmee", confirme_le=t)
    _fx(conn, "FE-01A", "Confirmation de votre précommande %s — %s" % (p["reference"], p2["delai_affiche"]), t, pid,
        p["instance_id"], "T09", emetteur="mkt_ecommerce", recepteur="client",
        lien="/a/client/commandes?ref=%s" % p["reference"], demo=p["demo"])
    return dict(_p(conn, pid))


def reprendre(conn, pid: int, t: str, capacite: str, coloris: str, paiement_mode: str,
              simuler_refus: bool = False) -> dict:
    """Retour en T01 après un refus de paiement : nouvelle configuration / nouveau moyen de paiement."""
    p = _p(conn, pid)
    inst = p["instance_id"]
    if p["statut"] != "paiement_refuse":
        raise TransitionInvalide("Seule une précommande au paiement refusé peut être reconfigurée.")
    ch = chiffrer(capacite, bool(p["applecare"]), conn)
    lot = prochain_lot(conn, capacite, coloris, t)
    delai = libelle_delai(lot["date"], p["livraison_mode"], parse(t))
    enregistrer(conn, inst, "T01", t, "client", details="Nouvelle configuration après refus")
    enregistrer(conn, inst, "T02", t, "mkt_ecommerce", details="%s — %s" % (euros(ch["prix_ttc"]), delai))
    enregistrer(conn, inst, "T03", t, "client", details="Précommande revalidée")
    _maj(conn, pid, t, capacite=capacite, coloris=coloris, prix_ttc=ch["prix_ttc"], prix_ht=ht(ch["prix_ttc"]),
         paiement_mode=paiement_mode, delai_affiche=delai, statut="controle_paiement",
         paiement_statut="refus_banque" if simuler_refus else "autorise", motif=None)
    _fx(conn, "FE-01R", "Précommande %s revalidée après refus" % p["reference"], t, pid, inst, "T03",
        lien="/a/finance/paiements", recepteur="finance", demo=p["demo"])
    if lire_parametre(conn, "mode_execution", "pas_a_pas") == "automatique":
        traiter_automatiquement(conn, pid, t)
    return dict(_p(conn, pid))


def traiter_automatiquement(conn, pid: int, t: str) -> dict:
    """Mode « automatique » (traitement sans intervention) : le SI exécute G01, G02, T07, T08 selon les règles."""
    p = _p(conn, pid)
    if p["statut"] == "controle_paiement":
        issue = "non" if p["paiement_statut"] == "refus_banque" else "oui"
        decision_paiement(conn, pid, issue, t, acteur="si", commentaire="Décision automatique (règle de gestion)")
        p = _p(conn, pid)
    if p["statut"] == "payee":
        verifier_stock(conn, pid, t, acteur="si")
        p = _p(conn, pid)
    if p["statut"] == "delai_a_allonger":
        allonger_delai(conn, pid, t, acteur="si")
        p = _p(conn, pid)
    if p["statut"] == "a_reserver":
        reserver(conn, pid, t, acteur="si")
    return dict(_p(conn, pid))


# --------------------------------------------------------------------------- lecture
def etat_bpmn(conn, pid: int, t: str) -> dict:
    p = _p(conn, pid)
    if not p["instance_id"]:
        return {"jetons": [], "termines": [], "fini": True, "reconstitue": True}
    e = charger_etat(conn, p["instance_id"], t)
    return e.dict()


def chronologie(conn, pid: int, t: str) -> list:
    """Historique BPMN : événements réels (instance) ou reconstitués (précommandes historiques)."""
    p = _p(conn, pid)
    if p["instance_id"]:
        rows = conn.execute("SELECT noeud, issue, acteur, horodatage, details, partiel FROM evenements "
                            "WHERE instance_id=? AND horodatage <= ? ORDER BY horodatage, id",
                            (p["instance_id"], t)).fetchall()
        return [dict(r) for r in rows]
    out = []
    if p["cree_le"] <= t:
        conf = "%s %s" % (CAPACITES[p["capacite"]]["libelle"], COLORIS[p["coloris"]]["libelle"])
        out += [dict(noeud="T01", acteur="client", horodatage=p["cree_le"], details=conf),
                dict(noeud="T02", acteur="mkt_ecommerce", horodatage=p["cree_le"], details=p["delai_affiche"] or ""),
                dict(noeud="T03", acteur="client", horodatage=p["cree_le"], details="Précommande validée")]
    if p["paye_le"] and p["paye_le"] <= t:
        out += [dict(noeud="G01", issue="oui", acteur="si", horodatage=p["paye_le"], details="Paiement accepté"),
                dict(noeud="T04", acteur="finance", horodatage=p["paye_le"],
                     details="CA prévisionnel : %s HT" % euros(p["ca_previsionnel_ht"] or 0, 2)),
                dict(noeud="T05", acteur="finance", horodatage=p["paye_le"],
                     details="Marge : %s" % euros(p["marge"] or 0, 2))]
    if p["crm_le"] and p["crm_le"] <= t:
        out.append(dict(noeud="T06", acteur="mkt_data", horodatage=p["crm_le"], details="Enregistrée dans le CRM"))
    if p["reserve_le"] and p["reserve_le"] <= t:
        out.append(dict(noeud="G02", issue="non" if p["delai_allonge"] else "oui", acteur="si",
                        horodatage=p["reserve_le"], details="Contrôle du stock"))
        if p["delai_allonge"]:
            out.append(dict(noeud="T07", acteur="si", horodatage=p["reserve_le"], details=p["delai_affiche"]))
        out.append(dict(noeud="T08", acteur="si", horodatage=p["reserve_le"], details="Lot %s" % p["lot_id"]))
    if p["confirme_le"] and p["confirme_le"] <= t:
        out.append(dict(noeud="T09", acteur="client", horodatage=p["confirme_le"], details=p["delai_affiche"]))
    return out
