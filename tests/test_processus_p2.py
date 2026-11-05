"""Processus P2 — campagne TikTok et mesure de son efficacité (Fig. 5) exécuté de bout en bout."""


def act(client, cid, action, acteur, **body):
    body["acteur"] = acteur
    r = client.post("/api/campagnes/%d/%s" % (cid, action), json=body)
    assert r.status_code == 200, (action, r.text)
    return r.json()


def test_campagne_complete_avec_boucles(client):
    r = client.post("/api/campagnes", json={"acteur": "dir_marketing", "nom": "Campagne test", "pays": "FR"})
    assert r.status_code == 200, r.text
    c = r.json()
    cid = c["id"]
    assert c["etat"]["jetons"] == ["T01"]
    lignes = [{"canal": "TikTok Ads", "montant": 300000}, {"canal": "Influence", "montant": 200000}]
    c = act(client, cid, "proposition", "dir_marketing", lignes=lignes)
    assert c["etat"]["jetons"] == ["G01"] and c["budget_propose"] == 500000
    # Finance : « non : revoir » -> retour à T01
    c = act(client, cid, "validation", "finance", issue="non", commentaire="Trop élevé")
    assert c["etat"]["jetons"] == ["T01"]
    c = act(client, cid, "proposition", "dir_marketing", lignes=[{"canal": "TikTok Ads", "montant": 380000}])
    c = act(client, cid, "validation", "finance", issue="oui")
    assert c["etat"]["jetons"] == ["T02"]
    c = act(client, cid, "publication", "mkt_social", videos=[{"titre": "Yoga", "concept": "posé"}])
    assert set(c["etat"]["jetons"]) == {"T03"}           # T06 attend aussi les avis (jointure ET)
    ids = [i["id"] for i in c["catalogue_influenceurs"][:2]] if "catalogue_influenceurs" in c else None
    if ids is None:
        ids = [i["id"] for i in client.get("/api/campagnes/%d" % cid).json()["catalogue_influenceurs"][:2]]
    c = act(client, cid, "influenceurs", "mkt_social", ids=ids)
    assert c["etat"]["jetons"] == ["T04"]
    c = act(client, cid, "appareils", "production")
    assert c["etat"]["jetons"] == ["T05"]
    # T05 multi-instance : chaque influenceur publie ; la tâche se termine au dernier avis
    c = act(client, cid, "avis", "influenceur", influenceur_id=ids[0], titre="Mon avis", sentiment=75)
    assert c["etat"]["jetons"] == ["T05"]
    c = act(client, cid, "avis", "influenceur", influenceur_id=ids[1], titre="Mon avis", sentiment=70)
    assert c["etat"]["jetons"] == ["T06"]
    # Mesure -> objectifs non atteints -> ajustement -> nouvelle mesure -> atteints
    c = act(client, cid, "mesure", "mkt_data")
    assert c["etat"]["jetons"] == ["G02"]
    assert c["comparaison"] and any(not o["atteint"] for o in c["comparaison"])
    c = act(client, cid, "decision", "dir_marketing", issue="non")
    assert c["etat"]["jetons"] == ["T07"]
    c = act(client, cid, "ajustement", "mkt_social", ciblage="25-44 ans", message="Mettre en avant la reprise")
    assert c["etat"]["jetons"] == ["T06"]
    c = act(client, cid, "mesure", "mkt_data")
    assert all(o["atteint"] for o in c["comparaison"] if o["code"] == "sentiment")
    c = act(client, cid, "decision", "dir_marketing", issue="oui")
    assert c["etat"]["jetons"] == ["T08"]
    c = act(client, cid, "rapport", "dir_marketing", previsions={"total": 12000, "coloris_principal": "noir"})
    assert set(c["etat"]["jetons"]) == {"T09", "T10"}
    c = act(client, cid, "plan", "production", coloris="noir", quantite=800)
    assert c["etat"]["jetons"] == ["T10"]
    c = act(client, cid, "cac", "finance")
    assert c["etat"]["fini"] is True and "E1" in c["etat"]["fins"]
    assert c["cout_acquisition"] > 0 and c["statut"] == "terminee"
    # flux et notifications : la direction marketing a reçu le budget accordé et le CAC
    notifs = client.get("/api/notifications", params={"acteur": "dir_marketing"}).json()["items"]
    codes = {n["code"] for n in notifs}
    assert "FI-07" in codes and "FI-12" in codes


def test_roles_p2(client):
    c = client.post("/api/campagnes", json={"acteur": "dir_marketing", "nom": "Test rôles"}).json()
    r = client.post("/api/campagnes/%d/proposition" % c["id"], json={"acteur": "finance", "lignes": [
        {"canal": "TikTok Ads", "montant": 1000}]})
    assert r.status_code == 403
    r = client.post("/api/campagnes", json={"acteur": "client", "nom": "x"})
    assert r.status_code == 403


def test_campagne_relance_allemagne_en_attente_de_la_finance(client):
    camps = client.get("/api/campagnes").json()
    de = next(c for c in camps if "Allemagne" in c["nom"])
    assert de["jetons"] == ["G01"]
    files = client.get("/api/files", params={"acteur": "finance"}).json()
    assert any(f["code"] == "P2-G01" for f in files)


def test_campagne_de_lancement_rejouee_dans_le_temps(client):
    """Le moteur rejoue les événements jusqu'à l'heure simulée : au 12/10 à 09:00 la campagne
    de lancement attend la décision « Objectifs atteints ? »."""
    from conftest import regler
    regler(client, "2026-10-12T09:30:00")
    camps = client.get("/api/campagnes").json()
    lancement = next(c for c in camps if "Lancement" in c["nom"])
    assert lancement["jetons"] == ["G02"]
    detail = client.get("/api/campagnes/%d" % lancement["id"]).json()
    assert detail["fige"] is True and len(detail["mesures"]) == 3
    r = client.post("/api/campagnes/%d/decision" % lancement["id"], json={"acteur": "dir_marketing", "issue": "oui"})
    assert r.status_code == 409          # historique figé : on ne réécrit pas le passé
