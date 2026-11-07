#!/bin/bash
# =============================================================================
#  SI Marketing · iPhone Duo — lancement en un double-clic (macOS)
#  Prototype du TD « Fondamentaux des systèmes d'information » (L2, IAE Lyon 3)
#
#  1. vérifie Python 3.9 ou plus (celui de macOS convient)
#  2. crée un environnement isolé (.venv) et installe les dépendances (1re fois)
#  3. démarre le serveur sur http://localhost:8005 et ouvre le navigateur
#  Pour arrêter : Ctrl+C ou fermer cette fenêtre.
# =============================================================================
set -u
cd "$(dirname "$0")" || exit 1
DOSSIER="$(pwd)"
PORT=8005
URL="http://localhost:$PORT"

pause_et_quitter() {
  echo ""
  read -r -p "Appuyez sur Entrée pour fermer cette fenêtre…" _
  exit "${1:-1}"
}

echo ""
echo "  ============================================================"
echo "    SI Marketing · iPhone Duo — prototype du TD (Séances 6-7)"
echo "  ============================================================"
echo ""

# --- 1. Python 3.9+ -----------------------------------------------------------
PY=""
for candidat in python3.13 python3.12 python3.11 python3.10 python3.9 python3; do
  if command -v "$candidat" >/dev/null 2>&1; then
    if "$candidat" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)' >/dev/null 2>&1; then
      PY="$(command -v "$candidat")"
      break
    fi
  fi
done
if [ -z "$PY" ]; then
  echo "❌ Python 3.9 ou plus est introuvable."
  echo "   Installez-le depuis https://www.python.org/downloads/macos/"
  echo "   (ou tapez dans le Terminal : xcode-select --install), puis relancez."
  osascript -e 'display dialog "Python 3.9 ou plus est nécessaire. Installez-le depuis python.org puis relancez lancer_app.command." buttons {"OK"} default button 1 with icon caution' >/dev/null 2>&1
  pause_et_quitter 1
fi
echo "✓ Python : $("$PY" --version 2>&1)"

# --- 2. Déjà lancée ? ---------------------------------------------------------
if curl -s -o /dev/null --max-time 2 "$URL/api/sante"; then
  echo "✓ L'application tourne déjà : ouverture de $URL"
  open "$URL"
  exit 0
fi
if command -v lsof >/dev/null 2>&1 && lsof -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
  echo "❌ Le port $PORT est déjà utilisé par un autre programme :"
  lsof -iTCP:"$PORT" -sTCP:LISTEN
  pause_et_quitter 1
fi

# --- 3. Environnement virtuel et dépendances ----------------------------------
if [ ! -x ".venv/bin/python" ]; then
  echo "… Création de l'environnement Python (.venv)"
  "$PY" -m venv .venv || { echo "❌ Impossible de créer l'environnement .venv"; pause_et_quitter 1; }
fi
VPY="$DOSSIER/.venv/bin/python"
if [ ! -f ".venv/.installe" ] || [ "requirements.txt" -nt ".venv/.installe" ]; then
  echo "… Installation des dépendances (première fois seulement, environ 1 minute)"
  "$VPY" -m pip install --upgrade pip >/dev/null 2>&1
  if "$VPY" -m pip install -r requirements.txt; then
    touch ".venv/.installe"
  else
    echo "❌ L'installation a échoué (une connexion Internet est nécessaire la première fois)."
    pause_et_quitter 1
  fi
fi
echo "✓ Dépendances installées"

# --- 4. Démarrage du serveur --------------------------------------------------
if [ ! -f "data/si_iphone_duo.db" ]; then
  echo "… Première utilisation : création de la base de démonstration (10 à 20 secondes)"
fi
"$VPY" -m uvicorn app.main:app --host 127.0.0.1 --port "$PORT" > serveur.log 2>&1 &
PID=$!
trap 'echo ""; echo "Arrêt du serveur…"; kill "$PID" 2>/dev/null; exit 0' INT TERM HUP

PRET=0
for _ in $(seq 1 120); do
  if curl -s -o /dev/null --max-time 2 "$URL/api/sante"; then PRET=1; break; fi
  if ! kill -0 "$PID" 2>/dev/null; then break; fi
  sleep 1
done
if [ "$PRET" -ne 1 ]; then
  echo "❌ Le serveur n'a pas démarré. Dernières lignes du journal (serveur.log) :"
  tail -25 serveur.log
  kill "$PID" 2>/dev/null
  pause_et_quitter 1
fi

open "$URL"
echo ""
echo "✅ Application prête : $URL"
echo ""
echo "   • Changer de « Vue acteur » : touche A   • Mode inspection (soutenance) : touche I"
echo "   • Dossier TD (Séance 8, dossier complet, soutenance) : icône livre en haut à droite"
echo "   • Laissez cette fenêtre ouverte pendant l'utilisation ; Ctrl+C ou fermer la fenêtre pour arrêter."
echo ""
wait "$PID"
