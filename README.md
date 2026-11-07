# SI Marketing · iPhone Duo — prototype interactif du système d'information

**TD « Fondamentaux des systèmes d'information » — Licence 2 Gestion et Management, IAE Lyon 3 (2026-2027)**

Le système d'information marketing d'**Apple** pour le **lancement de l'iPhone Duo**, construit à partir de notre travail des Séances 1 à 5 (entreprise, SWOT, fonction marketing, stratégie digitale, acteurs et flux, processus BPMN) : une application web **réelle et exécutable** plutôt que des maquettes statiques (Séances 6-7), accompagnée du dossier de la Séance 8 et de tout le nécessaire pour la soutenance (Séances 9-10).

> Problématique : *en quoi le système d'information marketing d'Apple lui permet-il de piloter et d'évaluer le lancement de l'iPhone Duo avant même sa commercialisation ?*

---

## Lancer l'application (macOS) — un double-clic

1. Télécharger le projet (bouton **Code → Download ZIP** sur GitHub, puis décompresser) ou le cloner.
2. Double-cliquer sur **`lancer_app.command`**.
   * La première fois : création d'un environnement Python isolé, installation des dépendances (environ 1 minute, connexion Internet nécessaire) et création de la base de démonstration (10 à 20 secondes).
   * Le navigateur s'ouvre sur **http://localhost:8005**. Laisser la fenêtre du Terminal ouverte ; **Ctrl+C** ou fermer la fenêtre pour arrêter.
3. Ensuite, l'application fonctionne **hors-ligne** (toutes les librairies sont embarquées).

**Si macOS bloque le fichier** (« provenant d'un développeur non identifié ») : clic droit sur `lancer_app.command` → **Ouvrir** → **Ouvrir**. Si le fichier n'est pas exécutable (rare après un téléchargement ZIP) : ouvrir le Terminal dans le dossier et taper `chmod +x lancer_app.command`.

**Python 3.9 ou plus** est requis : celui fourni par macOS convient (sinon `xcode-select --install`, ou https://www.python.org/downloads/macos/).

### Lancement manuel (macOS, Linux, Windows)

```bash
python3 -m venv .venv
```

```bash
.venv/bin/pip install -r requirements.txt
```

```bash
.venv/bin/python -m uvicorn app.main:app --port 8005
```

Puis ouvrir http://localhost:8005 (sous Windows : `.venv\Scripts\python -m uvicorn app.main:app --port 8005`).

---

## Visite rapide

| Élément | Où | Ce qu'il montre |
|---|---|---|
| **Vue acteur** | Bouton en haut à gauche (raccourci **A**) | 25 acteurs internes et externes des Fig. 1 à 5, chacun avec ses écrans |
| **Horloge du SI** | En haut à droite | Rejouer la keynote (9/09), le tableau de bord du 12/10, l'ouverture des précommandes (16/10, 14 h), J+3, l'après-sortie ; exécution *pas à pas* ou *automatique* |
| **Processus P1 et P2** | Menu « Vue d'ensemble » | Les BPMN du dossier, vivants : jetons en attente, passages, parcours de chaque instance |
| **Cartographie des flux** | Menu « Vue d'ensemble » | Les Fig. 1, 2 et 3 interactives : 60 flux codifiés (FE, FI, FM) avec compteurs |
| **Mode Inspection** | Bouton « Inspection » (raccourci **I**) | Pour chaque écran : séances mobilisées, tâches BPMN et flux illustrés, repères numérotés, argument pour le jury |
| **Atelier captures HD** | Icône appareil photo / menu | PNG Retina (×2) de chaque maquette, avec ou sans annotations, en ZIP |
| **Dossier TD** | Icône livre | Séance 8, dossier complet, plan de soutenance, guide de démonstration |
| **Tâches en attente** | Pastille noire en bas | Quel acteur doit agir maintenant (démonstration guidée) |

Démonstration conseillée pour la soutenance : [`livrables_td/GUIDE_DEMO_Soutenance.md`](livrables_td/GUIDE_DEMO_Soutenance.md).

---

## Correspondance avec les séances du TD

| Séance | Dans ce dépôt |
|---|---|
| **S1** Entreprise, SWOT | Dossier complet § 2-3 ; contraintes du SWOT reprises dans le prototype (fournisseur unique d'écrans, flambée de la mémoire, frein du prix) |
| **S2** Fonction marketing, outils, KPI | Cockpit KPI en trois phases (E20), CRM (E24), finance et production (E30-E37) |
| **S3** Stratégie digitale | Page produit apple.com (E10), configurateur (E11), campagne TikTok (E23) |
| **S4** Acteurs et flux | Référentiel des 25 acteurs et 60 flux (`app/referentiel.py`), cartographie (E01), journal (E04), portails partenaires (E41-E51) |
| **S5** BPMN P1 et P2, tableau de bord | Moteur BPMN (`app/moteur.py`), BPMN vivants (E02, E03), tableau du 12/10 reproduit à l'identique (E25) |
| **S6-S7** Maquettes du SI | L'application elle-même : 41 écrans, mode inspection, captures HD (`livrables_td/captures/`) |
| **S8** Développement, maintenance, évolution | [`livrables_td/SEANCE_8_Developpement_Maintenance_Evolution_SI.md`](livrables_td/SEANCE_8_Developpement_Maintenance_Evolution_SI.md) |
| **S9-S10** Soutenance et rendu | [`livrables_td/SOUTENANCE_Plan_oral_et_questions_jury.md`](livrables_td/SOUTENANCE_Plan_oral_et_questions_jury.md), [`livrables_td/DOSSIER_COMPLET_SI.md`](livrables_td/DOSSIER_COMPLET_SI.md) (+ HTML et PDF) |

---

## Architecture

* **Serveur** : Python, FastAPI ; **base** : SQLite (fichier `data/si_iphone_duo.db`, créé et pré-rempli au premier lancement).
* **Interface** : HTML (Jinja2), Tailwind CSS compilé, Alpine.js, Chart.js, html2canvas, JSZip — **tout est embarqué** dans `app/static/vendor` (aucun CDN).
* **Référentiel unique** (`app/referentiel.py`) : acteurs, flux, processus BPMN et registre des écrans (métadonnées du mode inspection).
* **Moteur BPMN à jetons** (`app/moteur.py`) : l'état de chaque instance est recalculé en rejouant ses événements jusqu'à l'heure simulée.
* **Bus d'information** (`app/bus.py`) : chaque action émet un flux codifié et notifie l'acteur destinataire.
* **Contrôle d'accès par rôle** (`app/api.py`) : une tâche BPMN n'est exécutable que par l'acteur de son couloir.

```
app/
  main.py, api.py          routes des pages et API JSON
  referentiel.py           modèles des Séances 1-5 (source unique)
  moteur.py, bus.py        moteur BPMN, bus de flux et notifications
  services/                précommandes (P1), pilotage, campagnes (P2), KPI, portails, lectures
  seed.py, seed_donnees.py base de démonstration réaliste et déterministe
  templates/, static/      interface (41 écrans) et ressources embarquées
livrables_td/              dossier complet, Séance 8, soutenance, guide, captures, figures
outils/                    captures HD (Playwright), construction HTML/PDF, parcours navigateur
tests/                     66 tests pytest
frontend/                  sources Tailwind (pour recompiler le CSS ; inutile pour lancer l'application)
lancer_app.command         lanceur macOS
```

---

## Tests

```bash
.venv/bin/pip install -r requirements-dev.txt
```

```bash
.venv/bin/python -m pytest -q
```

66 tests : processus P1 et P2 de bout en bout (avec leurs branches et boucles), contrôle des rôles, rejeu dans le temps, calage sur le tableau de bord du 12/10, couverture complète des modèles (chaque tâche BPMN et chaque flux ont un écran), affichage des 41 écrans, livrables. Testés sous Python 3.9 et 3.13. Un parcours optionnel par vrais clics dans le navigateur est fourni : `outils/verifier_parcours_navigateur.js`.

## Outils de production

* Captures HD de toutes les maquettes : `python outils/generer_captures.py` (Playwright) — ou l'« Atelier captures HD » de l'application, sans installation.
* Livrables HTML/PDF et annexes générées : `python outils/construire_livrables.py`.
* CSS et librairies front : `cd frontend && npm install && npm run build`.

## Dépannage

* **Le port 8005 est occupé** : fermer l'autre fenêtre de l'application, ou arrêter le programme qui utilise ce port.
* **Revenir à la base d'origine** : menu de l'horloge → « Réinitialiser la base de démonstration » (ou supprimer `data/si_iphone_duo.db`).
* **Erreur au démarrage** : le détail est dans `serveur.log`.

---

*Prototype pédagogique réalisé dans le cadre d'un TD universitaire. Les données du SI (clients, précommandes, campagnes) sont fictives ; les informations sur l'entreprise proviennent des sources citées dans le dossier. Projet non affilié à Apple Inc. ; les illustrations du produit sont des dessins originaux.*
