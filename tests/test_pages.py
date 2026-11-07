"""Chaque écran (maquette) s'affiche, pour chaque vue acteur, et les livrables sont consultables."""
from pathlib import Path

import pytest

from app import referentiel as r

RACINE = Path(__file__).resolve().parent.parent


@pytest.mark.parametrize("ecran", r.ECRANS, ids=[e["code"] for e in r.ECRANS])
def test_chaque_ecran_s_affiche(client, ecran):
    url = r.ecran_url(ecran)
    if ecran["acteur"]:
        client.cookies.set("acteur", ecran["acteur"])
    rep = client.get(url)
    assert rep.status_code == 200, (ecran["code"], url, rep.text[:300])
    html = rep.text
    assert ecran["code"] in html                       # repère de l'écran (inspection)
    assert "Vue acteur" in html                        # sélecteur d'acteur présent partout
    for t in ecran["taches"][:3]:
        assert t in html                               # tâches BPMN annoncées dans le tiroir d'inspection


def test_dossier_td_et_livrables(client):
    for doc in ("seance8", "dossier", "soutenance", "guide"):
        rep = client.get("/dossier?doc=%s" % doc)
        assert rep.status_code == 200
        assert "prose-dossier" in rep.text
    assert "page-de-garde" in client.get("/dossier?doc=dossier").text
    for f in ("DOSSIER_COMPLET_SI.md", "SEANCE_8_Developpement_Maintenance_Evolution_SI.md",
              "SOUTENANCE_Plan_oral_et_questions_jury.md", "GUIDE_DEMO_Soutenance.md"):
        assert (RACINE / "livrables_td" / f).exists(), f


def test_soutenance_contient_15_questions():
    texte = (RACINE / "livrables_td" / "SOUTENANCE_Plan_oral_et_questions_jury.md").read_text(encoding="utf-8")
    for n in range(1, 16):
        assert "**%d. " % n in texte, n


def test_seance8_couvre_les_attendus():
    texte = (RACINE / "livrables_td" / "SEANCE_8_Developpement_Maintenance_Evolution_SI.md").read_text(encoding="utf-8")
    for mot in ("MOA", "MOE", "DSI", "Éditeurs", "intégrateurs", "gouvernance", "SLA", "TMA", "RACI",
                "IA prédictive", "IA générative", "API", "Cloud", "IoT", "RPA", "Cybersécurité", "RGPD"):
        assert mot.lower() in texte.lower(), mot


def test_ressources_hors_ligne_embarquees():
    vendor = RACINE / "app" / "static" / "vendor"
    for f in ("alpine.min.js", "chart.umd.min.js", "html2canvas.min.js", "jszip.min.js", "inter-latin-wght-normal.woff2"):
        assert (vendor / f).stat().st_size > 10000, f
    assert (RACINE / "app" / "static" / "css" / "app.css").stat().st_size > 20000
    base = (RACINE / "app" / "templates" / "base.html").read_text(encoding="utf-8")
    assert "cdn." not in base and "googleapis" not in base   # aucune ressource en ligne
