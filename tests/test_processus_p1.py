"""Processus P1 — gestion des précommandes (Fig. 4) exécuté de bout en bout."""
from conftest import regler

CLIENT = {"prenom": "Léa", "nom": "Martin", "email": "lea.martin.test@icloud.com", "appareil": "iPhone 13 Pro"}


def precommander(client, **kw):
    body = {"acteur": "client", "capacite": "512", "coloris": "noir", "paiement_mode": "cb", "client": CLIENT,
            "applecare": True, "reprise_modele": "iPhone 13 Pro", "reprise_etat": "bon"}
    body.update(kw)
    r = client.post("/api/precommandes", json=body)
    assert r.status_code == 200, r.text
    return r.json()


def test_parcours_nominal_pas_a_pas(client):
    p = precommander(client)
    assert p["statut"] == "controle_paiement"
    assert p["etat_bpmn"]["jetons"] == ["G01"]
    assert [e["noeud"] for e in p["chronologie"]][:3] == ["T01", "T02", "T03"]
    assert p["reprise_valeur"] > 0 and p["delai_affiche"]
    codes = {f["code"] for f in p["flux"]}
    assert {"FE-01R", "FE-01A", "FE-10A", "FE-10R", "FE-09R"} <= codes

    # Finance : passerelle « Paiement accepté ? » -> T04 CA prévisionnel, T05 marge, T06 CRM (automatisés)
    r = client.post("/api/precommandes/%d/paiement" % p["id"], json={"acteur": "finance", "issue": "oui"})
    assert r.status_code == 200, r.text
    p = r.json()
    assert p["statut"] == "payee"
    assert set(p["etat_bpmn"]["jetons"]) == {"G02", "T10"}
    assert p["ca_previsionnel_ht"] > 2000 and p["marge"] > 0 and p["cout_par_precommande"] > 0

    # Production : « Stock disponible ? » -> (T07) -> T08 -> T09 confirmation client
    r = client.post("/api/precommandes/%d/stock" % p["id"], json={"acteur": "production"})
    assert r.status_code == 200, r.text
    p = r.json()
    if p["issue"] == "non":
        assert p["statut"] == "delai_a_allonger"
        p = client.post("/api/precommandes/%d/delai" % p["id"], json={"acteur": "production"}).json()
        assert p["statut"] == "a_reserver" and p["delai_allonge"] == 1
    p = client.post("/api/precommandes/%d/reserver" % p["id"], json={"acteur": "production"}).json()
    assert p["statut"] == "confirmee"
    assert p["etat_bpmn"]["jetons"] == ["T10"]          # en attente de l'analyse du tableau de bord
    assert "E1" in p["etat_bpmn"]["fins"]
    # le client est notifié de la confirmation (flux FE-01A)
    notif = client.get("/api/notifications", params={"acteur": "client"}).json()
    assert any("Confirmation" in n["titre"] or "Confirmation" in (n["message"] or "") for n in notif["items"])


def test_controle_des_roles(client):
    p = precommander(client)
    r = client.post("/api/precommandes/%d/paiement" % p["id"], json={"acteur": "production", "issue": "oui"})
    assert r.status_code == 403
    assert "Finance" in r.json()["detail"]
    r = client.post("/api/precommandes/%d/stock" % p["id"], json={"acteur": "production"})
    assert r.status_code == 409          # G02 pas encore active : le paiement n'est pas accepté


def test_paiement_refuse_retour_au_choix_de_configuration(client):
    p = precommander(client, simuler_refus=True)
    r = client.post("/api/precommandes/%d/paiement" % p["id"], json={"acteur": "finance", "issue": "non",
                                                                     "commentaire": "Autorisation refusée"})
    p = r.json()
    assert p["statut"] == "paiement_refuse" and p["etat_bpmn"]["jetons"] == ["T01"]
    r = client.post("/api/precommandes/%d/reprendre" % p["id"],
                    json={"acteur": "client", "capacite": "256", "coloris": "bleu", "paiement_mode": "apple_pay"})
    assert r.status_code == 200, r.text
    p = r.json()
    assert p["statut"] == "controle_paiement" and p["capacite"] == "256"
    assert p["etat_bpmn"]["jetons"] == ["G01"]
    assert [e["noeud"] for e in p["chronologie"]].count("T01") == 2


def test_credit_etudie_par_organisme_financier(client):
    p = precommander(client, capacite="2T", paiement_mode="cetelem_24m", reprise_modele=None)
    assert p["statut"] == "attente_credit"
    r = client.post("/api/precommandes/%d/paiement" % p["id"], json={"acteur": "finance", "issue": "oui"})
    assert r.status_code == 409                      # la réponse FE-09R n'est pas arrivée
    r = client.post("/api/credits/%d" % p["credit"]["id"], json={"acteur": "organisme_financier", "decision": "accorde"})
    assert r.status_code == 200, r.text
    assert r.json()["statut"] == "controle_paiement"
    r = client.post("/api/precommandes/%d/paiement" % p["id"], json={"acteur": "finance", "issue": "oui"})
    assert r.json()["statut"] == "payee"


def test_mode_automatique(client):
    client.post("/api/horloge", json={"mode": "automatique"})
    p = precommander(client, capacite="256", coloris="naturel")
    assert p["statut"] == "confirmee"
    noeuds = [e["noeud"] for e in p["chronologie"]]
    for n in ["T01", "T02", "T03", "G01", "T04", "T05", "T06", "G02", "T08", "T09"]:
        assert n in noeuds


def test_precommandes_fermees_avant_le_16_octobre(client):
    regler(client, "2026-10-12T09:00:00")
    r = client.post("/api/precommandes", json={"acteur": "client", "capacite": "256", "coloris": "noir",
                                               "paiement_mode": "cb", "client": CLIENT})
    assert r.status_code == 409


def test_analyse_tableau_de_bord_et_hausse_de_production(client):
    p = precommander(client)
    client.post("/api/precommandes/%d/paiement" % p["id"], json={"acteur": "finance", "issue": "oui"})
    pil = client.get("/api/pilotage").json()
    assert pil["en_attente"] > 0
    fr = next(l for l in pil["tableau"] if l["pays"] == "FR")
    assert fr["recommandation"] == "oui"             # demande projetée > offre en France
    r = client.post("/api/pilotage/analyses", json={"acteur": "dir_marketing", "pays": "FR"})
    assert r.status_code == 200, r.text
    a = r.json()
    assert a["etat"]["jetons"] == ["G03"]
    # la précommande en attente a été intégrée à l'analyse (jeton T10 consommé)
    p2 = client.get("/api/precommandes/%s" % p["reference"]).json()
    assert "T10" not in p2["etat_bpmn"]["jetons"]
    a = client.post("/api/pilotage/analyses/%d/decision" % a["id"], json={"acteur": "dir_marketing", "issue": "oui"}).json()
    assert a["etat"]["jetons"] == ["T11"]
    r = client.post("/api/pilotage/analyses/%d/production" % a["id"],
                    json={"acteur": "production", "transfert_de": "DE", "transfert_qte": 500, "hausse_hebdo": 1000,
                          "semaines": 2})
    assert r.status_code == 200, r.text
    assert r.json()["etat"]["fini"] is True
    # capacité Samsung Display : une hausse démesurée est refusée
    a2 = client.post("/api/pilotage/analyses", json={"acteur": "dir_marketing", "pays": "UK"}).json()
    client.post("/api/pilotage/analyses/%d/decision" % a2["id"], json={"acteur": "dir_marketing", "issue": "oui"})
    r = client.post("/api/pilotage/analyses/%d/production" % a2["id"],
                    json={"acteur": "production", "hausse_hebdo": 900000, "semaines": 1})
    assert r.status_code == 409


def test_relance_declenche_une_campagne_p2(client):
    a = client.post("/api/pilotage/analyses", json={"acteur": "dir_marketing", "pays": "DE"}).json()
    client.post("/api/pilotage/analyses/%d/decision" % a["id"], json={"acteur": "dir_marketing", "issue": "non"})
    r = client.post("/api/pilotage/analyses/%d/relance" % a["id"],
                    json={"acteur": "dir_marketing", "levier": "Reprise renforcée", "message": "Bonus de 100 €",
                          "declencher_campagne": True})
    assert r.status_code == 200, r.text
    cid = r.json()["campagne_creee"]
    c = client.get("/api/campagnes/%d" % cid).json()
    assert c["etat"]["jetons"] == ["T01"] and "P1-T12" in c["declencheur"]
