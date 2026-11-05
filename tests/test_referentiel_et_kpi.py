"""Cohérence modèles (Séances 1-5) <-> prototype, et calage des indicateurs sur le dossier."""
from app import referentiel as r
from conftest import regler


def test_chaque_tache_bpmn_a_un_ecran():
    couvertes = {t for e in r.ECRANS if not e["transversal"] for t in e["taches"]}
    assert set(r.toutes_les_taches()) <= couvertes


def test_chaque_flux_est_illustre_par_un_ecran():
    illustres = {f for e in r.ECRANS for f in e["flux"]}
    assert set(r.FLUX) <= illustres


def test_references_valides():
    for e in r.ECRANS:
        for t in e["taches"]:
            assert r.tache(t), t
        for f in e["flux"]:
            assert f in r.FLUX, f
    for p in r.PROCESSUS.values():
        for (a, b, _i, _sa, _sb) in p["transitions"]:
            assert a in p["noeuds"] and b in p["noeuds"]
        for n, d in p["noeuds"].items():
            for a in d.get("acteurs", []):
                assert a in r.ACTEURS


def test_douze_acteurs_externes_du_diagramme_de_contexte():
    externes = {f["vers"] for f in r.FLUX.values() if f["figure"] == "Fig. 1" and f["de"] == "mkt"} | \
               {f["de"] for f in r.FLUX.values() if f["figure"] == "Fig. 1" and f["vers"] == "mkt"}
    assert len(externes) == 12


def test_tableau_de_bord_du_12_octobre_identique_au_dossier(client):
    regler(client, "2026-10-12T09:00:00")
    t = client.get("/api/kpi/hebdo").json()
    v = {l["code"]: l for l in t["lignes"]}
    assert t["lundi"] == "2026-10-12"
    assert round(v["visites"]["resultat"]) == 2350000 and v["visites"]["evaluation"] == "Atteint"
    assert round(v["me_prevenir"]["resultat"]) == 96000 and v["me_prevenir"]["evaluation"] == "En retard"
    assert round(v["rdv_demo"]["resultat"]) == 17200 and v["rdv_demo"]["evaluation"] == "Atteint"
    assert round(v["vues_tiktok"]["resultat"]) == 31000000
    assert v["sentiment"]["resultat"] == 54 and v["intention"]["resultat"] == 6 and v["android"]["resultat"] == 19
    assert t["atteints"] == 4


def test_kpi_par_fonction(client):
    m = client.get("/api/kpi/marketing").json()
    assert m["phase"] == "precommandes" and m["precommandes"]["total"] > 0
    f = client.get("/api/kpi/finance").json()
    assert f["objectif_marge"] == 48 and any(l["sous_objectif"] for l in f["par_capacite"])
    p = client.get("/api/kpi/production").json()
    assert len(p["grille"]) == 16
    d = client.get("/api/kpi/dg").json()
    assert any(pl["statut"] == "soumis" for pl in d["plans"])


def test_files_de_travail_au_19_octobre(client):
    files = client.get("/api/files").json()
    codes = {f["code"] for f in files}
    assert {"P1-G01", "P1-G02", "P1-T10", "P1-T11", "P2-G01", "FE-09A"} <= codes


def test_portails_et_actions(client):
    for acteur in ["operateur", "revendeur", "fournisseur", "developpeur", "agence", "institut", "organisme_financier",
                   "partenaire_reprise", "regulateur", "concurrent", "mkt_creation", "mkt_presse", "mkt_retail",
                   "ingenierie", "juridique", "applecare", "influenceur"]:
        r = client.get("/api/portails/%s" % acteur)
        assert r.status_code == 200, (acteur, r.text)
    r = client.post("/api/portails/partenaire_reprise/grille",
                    json={"acteur": "partenaire_reprise", "donnees": {"modele": "iPhone 13 Pro", "valeur": 310}})
    assert r.status_code == 200, r.text
    est = client.post("/api/reprise/estimation", json={"modele": "iPhone 13 Pro", "etat": "parfait"}).json()
    assert est["valeur"] == 310
    r = client.post("/api/portails/partenaire_reprise/grille",
                    json={"acteur": "client", "donnees": {"modele": "iPhone 13 Pro", "valeur": 310}})
    assert r.status_code == 403
    journal = client.get("/api/journal", params={"code": "FE-10R", "limite": 5}).json()
    assert journal and journal[0]["code"] == "FE-10R"


def test_me_prevenir_avant_ouverture(client):
    regler(client, "2026-10-12T09:00:00")
    r = client.post("/api/me-prevenir", json={"email": "prospect@example.com", "consentement": True})
    assert r.status_code == 200
    regler(client, "2026-10-19T10:00:00")
    r = client.post("/api/me-prevenir", json={"email": "prospect2@example.com"})
    assert r.status_code == 409
