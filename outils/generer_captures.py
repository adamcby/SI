"""Générateur de captures HD de toutes les maquettes (PNG Retina x2) pour le rapport et le PowerPoint.

Deux façons d'obtenir les captures :
  1. Sans rien installer : dans l'application, menu « Atelier captures HD » (http://localhost:8005/captures).
  2. En ligne de commande (ce script), avec Playwright :
        pip install playwright
        python -m playwright install chromium
        python outils/generer_captures.py                 # toutes les maquettes, propres + annotées
        python outils/generer_captures.py --version propre --ecrans E11 E30 E35

Le serveur doit tourner (double-clic sur lancer_app.command, ou : uvicorn app.main:app --port 8005).
Les fichiers sont écrits dans livrables_td/captures/ avec un index (README.md).
"""
import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--url", default="http://localhost:8005", help="adresse du serveur")
    p.add_argument("--sortie", default=str(RACINE / "livrables_td" / "captures"))
    p.add_argument("--largeur", type=int, default=1440)
    p.add_argument("--echelle", type=float, default=2.0, help="2 = qualité Retina (recommandé)")
    p.add_argument("--version", choices=["propre", "annotee", "toutes"], default="toutes")
    p.add_argument("--ecrans", nargs="*", help="codes d'écrans (ex. E11 E30) ; par défaut : tous")
    p.add_argument("--hauteur-max", type=int, default=3600, help="hauteur maximale capturée (px CSS)")
    p.add_argument("--chromium", default=os.environ.get("CHROMIUM_PATH"), help="chemin d'un Chromium déjà installé")
    a = p.parse_args()

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Playwright n'est pas installé : pip install playwright && python -m playwright install chromium\n"
              "Astuce : sans installation, utilisez l'« Atelier captures HD » de l'application.")
        return 1
    try:
        ref = json.load(urllib.request.urlopen(a.url + "/api/referentiel", timeout=10))
    except OSError:
        print("Serveur injoignable sur %s : lancez d'abord l'application." % a.url)
        return 1

    sortie = Path(a.sortie)
    sortie.mkdir(parents=True, exist_ok=True)
    ecrans = [e for e in ref["ecrans"] if e["code"] != "E07" and (not a.ecrans or e["code"] in a.ecrans)]
    versions = {"propre": [False], "annotee": [True], "toutes": [False, True]}[a.version]
    index = []
    with sync_playwright() as pw:
        lancement = {"executable_path": a.chromium} if a.chromium else {}
        navigateur = pw.chromium.launch(**lancement)
        contexte = navigateur.new_context(viewport={"width": a.largeur, "height": 900}, device_scale_factor=a.echelle)
        for e in ecrans:
            for annotee in versions:
                if e["acteur"]:
                    contexte.add_cookies([{"name": "acteur", "value": e["acteur"], "url": a.url}])
                page = contexte.new_page()
                sep = "&" if "?" in e["url"] else "?"
                page.goto(a.url + e["url"] + sep + "capture=1&inspection=%d" % (1 if annotee else 0), wait_until="networkidle")
                page.wait_for_timeout(1300)
                hauteur = min(a.hauteur_max, page.evaluate("document.documentElement.scrollHeight"))
                nom = "%s_%s_%s%s.png" % (e["code"], e["acteur"] or "transversal", e["slug"].replace("/", "-"),
                                          "_annotee" if annotee else "")
                page.screenshot(path=str(sortie / nom), clip={"x": 0, "y": 0, "width": a.largeur, "height": hauteur},
                                full_page=True)
                page.close()
                index.append((e, nom, annotee))
                print("  ✓", nom)
        navigateur.close()

    # index de TOUTES les captures présentes dans le dossier (exécutions successives comprises)
    par_code = {e["code"]: e for e in ref["ecrans"]}
    lignes = ["# Captures HD des maquettes (Séances 6-7)", "",
              "PNG haute définition (échelle x2, largeur 1440 px CSS) générées par `outils/generer_captures.py` ou par "
              "l'« Atelier captures HD » de l'application. Version *annotée* = mode Inspection maquette : repères "
              "numérotés et tiroir indiquant les séances, les tâches BPMN et les flux illustrés.", "",
              "| Écran | Acteur | Tâches BPMN | Flux illustrés | Propre | Annotée |", "|---|---|---|---|---|---|"]
    fichiers = sorted(f.name for f in sortie.glob("E*.png"))
    for code in sorted({f.split("_")[0] for f in fichiers}):
        e = par_code.get(code)
        if not e:
            continue
        propre = next((f for f in fichiers if f.startswith(code + "_") and not f.endswith("_annotee.png")), None)
        annot = next((f for f in fichiers if f.startswith(code + "_") and f.endswith("_annotee.png")), None)
        acteur = ref["acteurs"][e["acteur"]]["nom"] if e["acteur"] else "Vue transversale"
        lignes.append("| %s — %s | %s | %s | %s | %s | %s |" % (
            code, e["nav"], acteur, ", ".join(e["taches"][:6]) or "—", ", ".join(e["flux"][:6]) or "—",
            "[PNG](%s)" % propre if propre else "—", "[PNG](%s)" % annot if annot else "—"))
    (sortie / "README.md").write_text("\n".join(lignes) + "\n", encoding="utf-8")
    print("%d capture(s) dans %s" % (len(index), sortie))
    return 0


if __name__ == "__main__":
    sys.exit(main())
