"""Application web du SI marketing — lancement de l'iPhone Duo (prototype des Séances 6-7).

Lancement :  uvicorn app.main:app --port 8005   (ou double-clic sur lancer_app.command)
"""
import json
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from . import horloge
from .api import installer_gestion_erreurs, router
from .db import connecter, ecrire_parametre, initialiser, lire_parametre
from .metier import euros
from .referentiel import (ACTEURS, ECRANS, ECRANS_PAR_CODE, FLUX, GROUPES_ACTEURS, PROCESSUS, PROJET, SEANCES,
                          ecran_url, ecrans_acteur, export_referentiel, tache)

ICI = Path(__file__).resolve().parent
RACINE = ICI.parent
ACTEUR_DEFAUT = "dir_marketing"

@asynccontextmanager
async def cycle_de_vie(_app):
    demarrage()
    yield


app = FastAPI(title="SI marketing — lancement de l'iPhone Duo", version="1.0", lifespan=cycle_de_vie,
              description="Prototype pédagogique (TD Fondamentaux des SI, L2 Gestion et Management, IAE Lyon 3).")
app.include_router(router)
installer_gestion_erreurs(app)
app.mount("/static", StaticFiles(directory=str(ICI / "static")), name="static")
app.mount("/livrables", StaticFiles(directory=str(RACINE / "livrables_td"), check_dir=False), name="livrables")

templates = Jinja2Templates(directory=str(ICI / "templates"))


def _sep(v, dec=0):
    if v is None:
        return "—"
    s = ("{:,.%df}" % dec).format(v).replace(",", " ").replace(".", ",")
    return s


templates.env.filters["sep"] = _sep
templates.env.filters["euros"] = lambda v, d=0: euros(v or 0, d)
templates.env.filters["tojson_safe"] = lambda v: json.dumps(v, ensure_ascii=False)
templates.env.globals.update(ACTEURS=ACTEURS, FLUX=FLUX, PROCESSUS=PROCESSUS, PROJET=PROJET, SEANCES=SEANCES,
                             GROUPES=GROUPES_ACTEURS, ecran_url=ecran_url, tache=tache, ECRANS=ECRANS)


def demarrage():
    initialiser()
    conn = connecter()
    try:
        # L'horloge reprend au préréglage choisi, sans « cacher » les données de démonstration déjà saisies.
        preset = lire_parametre(conn, "horloge_preset") or horloge.PRESET_DEFAUT
        dernier = conn.execute("SELECT MAX(horodatage) FROM flux_log WHERE demo = 1").fetchone()[0]
        base = next((p["date"] for p in horloge.PRESETS if p["id"] == preset), None) or lire_parametre(conn, "horloge_base")
        if dernier and dernier > base:
            from datetime import timedelta
            base = horloge.fmt(horloge.parse(dernier) + timedelta(minutes=1))
        ecrire_parametre(conn, "horloge_base", base)
        ecrire_parametre(conn, "horloge_reel", repr(time.time()))
        conn.commit()
    finally:
        conn.close()


def _contexte(request: Request, ecran: dict, acteur: str, **extra) -> dict:
    conn = connecter()
    try:
        etat_horloge = horloge.etat(conn)
    finally:
        conn.close()
    a = ACTEURS.get(acteur) or ACTEURS[ACTEUR_DEFAUT]
    ctx = {
        "request": request, "ecran": ecran, "acteur": acteur, "acteur_def": a,
        "ecrans_acteur": [dict(e, url=ecran_url(e)) for e in ecrans_acteur(acteur)],
        "transversaux": [dict(e, url=ecran_url(e)) for e in ECRANS if e["transversal"]],
        "horloge": etat_horloge,
        "inspection": {
            "code": ecran["code"], "titre": ecran["titre"], "seances": ecran["seances"],
            "taches": [dict(tache(t) or {}, code=t) for t in ecran["taches"]],
            "flux": [FLUX[f] for f in ecran["flux"]], "donnees": ecran["donnees"], "jury": ecran["jury"],
        },
    }
    ctx.update(extra)
    return ctx


def _acteur_cookie(request: Request) -> str:
    a = request.cookies.get("acteur")
    return a if a in ACTEURS and ACTEURS[a]["type"] != "systeme" else ACTEUR_DEFAUT


def _page(request: Request, code: str, template: str, acteur: str, **extra) -> HTMLResponse:
    ecran = ECRANS_PAR_CODE[code]
    resp = templates.TemplateResponse(template, _contexte(request, ecran, acteur, **extra))
    resp.set_cookie("acteur", acteur, max_age=3600 * 24 * 30, samesite="lax")
    return resp


@app.get("/", response_class=HTMLResponse)
def accueil(request: Request):
    return _page(request, "E00", "accueil.html", _acteur_cookie(request))


@app.get("/flux", response_class=HTMLResponse)
def page_flux(request: Request):
    return _page(request, "E01", "flux.html", _acteur_cookie(request))


@app.get("/processus/{code}", response_class=HTMLResponse)
def page_processus(request: Request, code: str):
    if code not in PROCESSUS:
        return RedirectResponse("/processus/P1")
    return _page(request, "E02" if code == "P1" else "E03", "processus.html", _acteur_cookie(request), proc=code)


@app.get("/journal", response_class=HTMLResponse)
def page_journal(request: Request):
    return _page(request, "E04", "journal.html", _acteur_cookie(request))


@app.get("/si-partage", response_class=HTMLResponse)
def page_si(request: Request):
    return _page(request, "E05", "si_partage.html", _acteur_cookie(request))


@app.get("/dossier", response_class=HTMLResponse)
def page_dossier(request: Request, doc: str = "seance8"):
    from .dossier import DOCUMENTS, rendre
    if doc not in DOCUMENTS:
        doc = "seance8"
    html, toc = rendre(doc)
    return _page(request, "E06", "dossier.html", _acteur_cookie(request), doc=doc, documents=DOCUMENTS,
                 contenu=html, toc=toc)


@app.get("/captures", response_class=HTMLResponse)
def page_captures(request: Request):
    return _page(request, "E07", "captures.html", _acteur_cookie(request))


@app.get("/a/{acteur}", response_class=HTMLResponse)
def page_acteur_defaut(acteur: str):
    a = ACTEURS.get(acteur)
    if not a or not a.get("ecran_defaut"):
        return RedirectResponse("/")
    return RedirectResponse("/a/%s/%s" % (acteur, a["ecran_defaut"]))


@app.get("/a/{acteur}/{slug:path}", response_class=HTMLResponse)
def page_ecran(request: Request, acteur: str, slug: str):
    ecran = next((e for e in ECRANS if e["acteur"] == acteur and e["slug"] == slug), None)
    if ecran is None:
        return RedirectResponse("/a/%s" % acteur if acteur in ACTEURS else "/")
    nom_template = "ecrans/%s_%s.html" % (acteur, slug.replace("-", "_"))
    if not (ICI / "templates" / nom_template).exists():
        nom_template = "ecrans/portail.html"
    return _page(request, ecran["code"], nom_template, acteur)


@app.get("/favicon.ico")
def favicon():
    return Response(status_code=204)
