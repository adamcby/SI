import os
import shutil
import sys
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE))


@pytest.fixture(scope="session")
def base_modele(tmp_path_factory):
    """Base pré-remplie une seule fois (échelle réduite pour la rapidité des tests)."""
    p = tmp_path_factory.mktemp("modele") / "si.db"
    from app import db
    db.initialiser(p, echelle=0.04, forcer=True)
    return p


@pytest.fixture
def client(base_modele, tmp_path, monkeypatch):
    """Client HTTP sur une copie isolée de la base, horloge figée au 19/10/2026 10:00."""
    p = tmp_path / "si.db"
    shutil.copy(str(base_modele), str(p))
    monkeypatch.setenv("SI_DB_PATH", str(p))
    from fastapi.testclient import TestClient
    from app.main import app
    with TestClient(app) as c:
        r = c.post("/api/horloge", json={"preset": "j3", "vitesse": 0, "mode": "pas_a_pas"})
        assert r.status_code == 200
        yield c


def regler(client, date, mode=None):
    body = {"date": date, "vitesse": 0}
    if mode:
        body["mode"] = mode
    r = client.post("/api/horloge", json=body)
    assert r.status_code == 200, r.text
