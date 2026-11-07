"""Construit les livrables du dossier livrables_td/ à partir des sources Markdown.

1. Remplit les annexes du dossier complet (flux, écrans, traçabilité) depuis le référentiel de l'application
   -> une seule source de vérité : les tableaux sont toujours identiques au prototype.
2. Prépare des illustrations allégées (JPEG) à partir des captures HD          (nécessite Pillow)
3. Produit les versions HTML imprimables (A4) de chaque document
4. Produit les PDF                                                             (nécessite Playwright, optionnel)

Usage : python outils/construire_livrables.py [--sans-pdf] [--chromium /chemin/vers/chrome]
"""
import argparse
import html
import os
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
LIVRABLES = RACINE / "livrables_td"
sys.path.insert(0, str(RACINE))

from app import referentiel as R  # noqa: E402

DOCUMENTS = [
    ("DOSSIER_COMPLET_SI", "Dossier complet — SI marketing du lancement de l'iPhone Duo"),
    ("SEANCE_8_Developpement_Maintenance_Evolution_SI", "Séance 8 — Développement, maintenance et évolution du SI"),
    ("SOUTENANCE_Plan_oral_et_questions_jury", "Soutenance — plan de l'oral et questions du jury"),
    ("GUIDE_DEMO_Soutenance", "Guide de démonstration du prototype"),
]
PDF = ["DOSSIER_COMPLET_SI", "SEANCE_8_Developpement_Maintenance_Evolution_SI", "SOUTENANCE_Plan_oral_et_questions_jury"]

# (capture source, nom de l'illustration, haut, bas, gauche, droite) en pixels de la capture x2 ; None = pleine largeur
ILLUSTRATIONS = [
    ("E10_client_produit.png", "E10_page_produit.jpg", 0, 2100, None, None),
    ("E01_transversal_flux.png", "E01_cartographie.jpg", 0, 2060, None, None),
    ("E11_client_configurateur.png", "E11_configurateur.jpg", 0, 2000, None, None),
    ("E30_finance_paiements.png", "E30_finance.jpg", 0, 2150, None, None),
    ("E35_production_stocks.png", "E35_production.jpg", 0, 2250, None, None),
    ("E02_transversal_processus-P1.png", "E02_bpmn_p1.jpg", 800, 2920, 560, 2030),
    ("E20_dir_marketing_cockpit.png", "E20_cockpit.jpg", 0, 2000, None, None),
    ("E21_dir_marketing_pilotage-precommandes.png", "E21_pilotage.jpg", 0, 2580, None, None),
    ("E11_client_configurateur_annotee.png", "E11_inspection.jpg", 0, 1900, None, None),
]
FIGURES_HAUTES = ("Fig4", "Fig5", "E02_bpmn")


# ----------------------------------------------------------------------------- annexes générées
def _nom(code):
    return "Apple (SI marketing)" if code == "mkt" else R.ACTEURS[code]["nom"]


def table_flux() -> str:
    lignes = ["| Code | Figure | Émetteur | Destinataire | Information échangée |", "|---|---|---|---|---|"]
    for code, f in R.FLUX.items():
        lib = f["libelle"] + (" *(pointillés : indirect)*" if f["trait"] == "pointille" else "")
        lignes.append("| %s | %s | %s | %s | %s |" % (code, f["figure"], _nom(f["de"]), _nom(f["vers"]), lib))
    return "\n".join(lignes)


def table_ecrans() -> str:
    lignes = ["| Écran | Acteur | Tâches BPMN | Flux illustrés | Séances |", "|---|---|---|---|---|"]
    for e in R.ECRANS:
        acteur = R.ACTEURS[e["acteur"]]["nom"] if e["acteur"] else "Vue transversale"
        lignes.append("| %s — %s | %s | %s | %s | %s |" % (
            e["code"], e["nav"], acteur, ", ".join(e["taches"]) or "—", ", ".join(e["flux"]) or "—",
            ", ".join(e["seances"])))
    return "\n".join(lignes)


def table_tracabilite() -> str:
    lignes = ["| Tâche ou passerelle | Libellé (couloir) | Exécutée par | Écran(s) qui la réalisent |", "|---|---|---|---|"]
    for code in R.toutes_les_taches():
        t = R.tache(code)
        ecrans = ["%s %s" % (e["code"], e["nav"]) for e in R.ECRANS if code in e["taches"] and not e["transversal"]]
        auto = " — *automatisée*" if t.get("auto") else ""
        lignes.append("| %s | %s (%s)%s | %s | %s |" % (
            code, t["libelle"].replace("\n", " "), t["couloir"], auto,
            ", ".join(R.ACTEURS[a]["court"] for a in t.get("acteurs", [])), " · ".join(ecrans)))
    return "\n".join(lignes)


def remplir_annexes() -> None:
    p = LIVRABLES / "DOSSIER_COMPLET_SI.md"
    s = p.read_text(encoding="utf-8")
    for cle, contenu in (("FLUX", table_flux()), ("ECRANS", table_ecrans()), ("TRACABILITE", table_tracabilite())):
        s = re.sub(r"<!-- DEBUT:%s -->.*?<!-- FIN:%s -->" % (cle, cle),
                   "<!-- DEBUT:%s -->\n%s\n<!-- FIN:%s -->" % (cle, contenu, cle), s, flags=re.S)
    p.write_text(s, encoding="utf-8")
    print("  annexes régénérées depuis le référentiel (%d flux, %d écrans, %d tâches)"
          % (len(R.FLUX), len(R.ECRANS), len(R.toutes_les_taches())))


# ----------------------------------------------------------------------------- illustrations
def preparer_illustrations() -> None:
    try:
        from PIL import Image
    except ImportError:
        print("  (Pillow absent : illustrations non régénérées)")
        return
    dossier = LIVRABLES / "images_dossier"
    dossier.mkdir(exist_ok=True)
    for src, nom, haut, bas, gauche, droite in ILLUSTRATIONS:
        chemin = LIVRABLES / "captures" / src
        if not chemin.exists():
            print("  capture manquante :", src)
            continue
        im = Image.open(chemin).convert("RGB")
        w, h = im.size
        im = im.crop((gauche or 0, haut, droite or w, min(bas, h)))
        largeur = 1100 if nom.startswith("E02") else 1600
        im = im.resize((largeur, int(im.size[1] * largeur / im.size[0])), Image.LANCZOS)
        im.save(dossier / nom, "JPEG", quality=86, optimize=True, progressive=True)
    print("  %d illustrations préparées dans images_dossier/" % len(ILLUSTRATIONS))


# ----------------------------------------------------------------------------- HTML imprimable
CSS = """
@page { size: A4; margin: 17mm 15mm 19mm; }
:root { color-scheme: light; }
* { box-sizing: border-box; }
body { margin: 0; background: #f5f5f7; color: #1d1d1f;
  font: 10.5pt/1.55 -apple-system, BlinkMacSystemFont, "SF Pro Text", "Inter Variable", Inter, "Helvetica Neue", Arial, sans-serif; }
main { max-width: 210mm; margin: 0 auto; background: #fff; padding: 16mm 15mm; }
.bandeau { font-size: 8pt; color: #6e6e73; border-bottom: 1px solid #e8e8ed; padding-bottom: 3mm; margin-bottom: 6mm; display: flex; justify-content: space-between; }
h1 { font-size: 21pt; line-height: 1.2; letter-spacing: -0.01em; margin: 0 0 4mm; }
h2 { font-size: 15pt; letter-spacing: -0.01em; margin: 9mm 0 3mm; padding-bottom: 1.5mm; border-bottom: 1px solid #d2d2d7; }
h3 { font-size: 12pt; margin: 6mm 0 2mm; }
h4 { font-size: 10.5pt; margin: 4mm 0 1.5mm; }
p, li { orphans: 3; widows: 3; }
a { color: #0066cc; text-decoration: none; }
strong { font-weight: 600; }
table { border-collapse: collapse; width: 100%; margin: 3mm 0 5mm; font-size: 8.6pt; }
th, td { border: 1px solid #d2d2d7; padding: 1.6mm 2mm; vertical-align: top; text-align: left; }
th { background: #f5f5f7; font-weight: 600; }
tr { page-break-inside: avoid; }
blockquote { margin: 4mm 0; padding: 3mm 4mm; border-left: 3px solid #0071e3; background: #f2f7fd; border-radius: 0 6px 6px 0; }
blockquote p { margin: 1mm 0; }
code { font-family: "SF Mono", Menlo, Consolas, monospace; font-size: 8.8pt; background: #f5f5f7; padding: 0 1.2mm; border-radius: 3px; }
pre { background: #f5f5f7; padding: 3mm; font-size: 7.4pt; line-height: 1.35; border-radius: 6px; overflow: hidden; page-break-inside: avoid; }
pre code { background: none; padding: 0; }
hr { border: 0; border-top: 1px solid #e8e8ed; margin: 6mm 0; }
figure { margin: 5mm 0; text-align: center; page-break-inside: avoid; }
figure img { max-width: 100%; max-height: 118mm; border: 1px solid #d2d2d7; border-radius: 6px; }
figure.haute img { max-height: 205mm; }
figcaption { font-size: 8.4pt; color: #6e6e73; margin-top: 2mm; font-style: italic; }
.page-de-garde { text-align: center; padding: 34mm 8mm 0; min-height: 250mm; page-break-after: always; }
.page-de-garde h1 { font-size: 25pt; margin: 14mm 0 8mm; }
.page-de-garde table { width: 80%; margin: 18mm auto; font-size: 10pt; }
.page-de-garde table th, .page-de-garde table td { text-align: center; border: none; background: none; }
.page-de-garde p { margin: 2mm 0; }
@media print {
  body { background: #fff; }
  main { max-width: none; margin: 0; padding: 0; }
  h2 { page-break-after: avoid; }
  h3, h4 { page-break-after: avoid; }
  .bandeau { display: none; }
}
"""


def vers_html(nom: str, titre: str) -> Path:
    import markdown
    src = LIVRABLES / (nom + ".md")
    md = markdown.Markdown(extensions=["tables", "toc", "sane_lists", "md_in_html", "fenced_code"])
    corps = md.convert(src.read_text(encoding="utf-8"))

    def figure(m):
        attrs = m.group(1)
        alt = re.search(r'alt="([^"]*)"', attrs)
        srcv = re.search(r'src="([^"]*)"', attrs).group(1)
        haute = any(k in srcv for k in FIGURES_HAUTES)
        legende = html.unescape(alt.group(1)) if alt else ""
        return '<figure class="%s"><img%s><figcaption>%s</figcaption></figure>' % (
            "haute" if haute else "", attrs, html.escape(legende))

    corps = re.sub(r"<p>\s*<img([^>]*)/?>\s*</p>", figure, corps)
    page = """<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s</title><style>%s</style></head>
<body><main>
<div class="bandeau"><span>SI marketing · lancement de l'iPhone Duo — TD Fondamentaux des SI, IAE Lyon 3</span><span>Imprimer : Fichier → Imprimer → Enregistrer en PDF</span></div>
%s
</main></body></html>""" % (html.escape(titre), CSS, corps)
    sortie = LIVRABLES / (nom + ".html")
    sortie.write_text(page, encoding="utf-8")
    return sortie


def vers_pdf(fichiers, chromium=None) -> None:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("  (Playwright absent : PDF non régénérés — utilisez « Imprimer → Enregistrer en PDF » sur le HTML)")
        return
    with sync_playwright() as pw:
        nav = pw.chromium.launch(**({"executable_path": chromium} if chromium else {}))
        page = nav.new_page()
        for f in fichiers:
            page.goto(f.as_uri(), wait_until="networkidle")
            sortie = f.with_suffix(".pdf")
            page.pdf(path=str(sortie), format="A4", print_background=True, display_header_footer=True,
                     header_template="<span></span>",
                     footer_template='<div style="width:100%;font-size:7.5px;color:#86868b;text-align:center;'
                                     'font-family:Helvetica,Arial,sans-serif">SI marketing — lancement de l\'iPhone Duo'
                                     ' · page <span class="pageNumber"></span> / <span class="totalPages"></span></div>',
                     margin={"top": "15mm", "bottom": "17mm", "left": "14mm", "right": "14mm"})
            print("  PDF :", sortie.name, "(%d Ko)" % (sortie.stat().st_size // 1024))
        nav.close()


def main() -> int:
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument("--sans-pdf", action="store_true")
    a.add_argument("--chromium", default=os.environ.get("CHROMIUM_PATH"))
    args = a.parse_args()
    print("Construction des livrables :")
    remplir_annexes()
    preparer_illustrations()
    produits = []
    for nom, titre in DOCUMENTS:
        produits.append(vers_html(nom, titre))
        print("  HTML :", produits[-1].name)
    if not args.sans_pdf:
        vers_pdf([p for p in produits if p.stem in PDF], args.chromium)
    return 0


if __name__ == "__main__":
    sys.exit(main())
