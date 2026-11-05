"""Rendu des livrables Markdown (livrables_td/) dans l'onglet « Dossier TD » de l'application."""
import re
from pathlib import Path
from typing import List, Tuple

import markdown

RACINE = Path(__file__).resolve().parent.parent / "livrables_td"

DOCUMENTS = {
    "seance8": {"fichier": "SEANCE_8_Developpement_Maintenance_Evolution_SI.md", "titre": "Séance 8 — Acteurs et évolutions"},
    "dossier": {"fichier": "DOSSIER_COMPLET_SI.md", "titre": "Dossier complet (Séances 1 à 8)"},
    "soutenance": {"fichier": "SOUTENANCE_Plan_oral_et_questions_jury.md", "titre": "Soutenance : plan et questions"},
    "guide": {"fichier": "GUIDE_DEMO_Soutenance.md", "titre": "Guide de démonstration"},
}


def rendre(code: str) -> Tuple[str, List[dict]]:
    doc = DOCUMENTS[code]
    chemin = RACINE / doc["fichier"]
    if not chemin.exists():
        return "<p>Document en cours de rédaction.</p>", []
    texte = chemin.read_text(encoding="utf-8")
    # les images des livrables sont servies sous /livrables/
    texte = re.sub(r"\]\((captures|figures)/", r"](/livrables/\1/", texte)
    md = markdown.Markdown(extensions=["tables", "toc", "sane_lists", "attr_list"],
                           extension_configs={"toc": {"toc_depth": "2-3"}})
    html = md.convert(texte)
    toc = []

    def parcourir(items):
        for it in items:
            toc.append({"id": it["id"], "titre": it["name"], "niveau": it["level"]})
            parcourir(it.get("children", []))

    parcourir(getattr(md, "toc_tokens", []))
    return html, toc
