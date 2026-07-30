#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
#  PUBLICAR — un solo comando lleva cualquier ajuste a las URLs, al hub,
#  a las apps del Mac y al iPhone.
#
#    bash _hub/publicar.sh              publica todo
#    bash _hub/publicar.sh --sin-apps   no toca las apps del Mac
#    bash _hub/publicar.sh --revisar    solo verifica que las URLs respondan
# ─────────────────────────────────────────────────────────────────────────────
set -e
export PATH=/opt/homebrew/bin:/usr/local/bin:$PATH
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

export GIT_AUTHOR_NAME="Roger Hernandez"
export GIT_AUTHOR_EMAIL="arhcarrasco@gmail.com"
export GIT_COMMITTER_NAME="$GIT_AUTHOR_NAME"
export GIT_COMMITTER_EMAIL="$GIT_AUTHOR_EMAIL"

verde () { printf '\033[32m%s\033[0m\n' "$1"; }
rojo  () { printf '\033[31m%s\033[0m\n' "$1"; }
paso  () { printf '\n\033[1m%s\033[0m\n' "$1"; }

revisar () {
  paso "Verificando URLs"
  local fallas=0
  while IFS='|' read -r nombre url; do
    code=$(curl -s -o /dev/null -w '%{http_code}' -L --max-time 25 "$url" || echo 000)
    if [ "$code" = "200" ]; then verde "  200  $nombre"
    else rojo "  $code  $nombre  →  $url"; fallas=$((fallas+1)); fi
  done < <(python3 -c "
import json
for a in json.load(open('_hub/catalogo.json'))['apps']:
    print(a['nombre'] + '|' + a['url'])
")
  code=$(curl -s -o /dev/null -w '%{http_code}' -L --max-time 25 "https://connectia.mx/hub/" || echo 000)
  [ "$code" = "200" ] && verde "  200  App Hub" || { rojo "  $code  App Hub"; fallas=$((fallas+1)); }
  echo
  [ "$fallas" -eq 0 ] && verde "Todo responde." || rojo "$fallas con problema."
  return 0
}

if [ "$1" = "--revisar" ]; then revisar; exit 0; fi

paso "1 · Íconos"
python3 _hub/iconos.py

paso "2 · Hub"
python3 _hub/hub.py

if [ "$1" != "--sin-apps" ]; then
  paso "3 · Apps del Mac"
  bash _hub/apps_mac.sh
else
  paso "3 · Apps del Mac — omitido"
fi

paso "4 · Publicando"
if [ -z "$(git status --porcelain)" ]; then
  echo "  sin cambios que publicar"
else
  git add -A
  git commit -q -m "${2:-Publica ajustes del App Hub y sus plataformas}"
  git fetch -q origin main
  git rebase -q origin/main >/dev/null 2>&1 || { rojo "  conflicto en rebase; resuélvelo y vuelve a correr"; exit 1; }
  git push -q origin main
  verde "  push OK · $(git log -1 --format='%h %s')"
fi

paso "5 · Esperando a GitHub Pages"
for i in $(seq 1 20); do
  printf '.'
  sleep 6
  estado=$(gh api repos/arhcarrasco-cloud/connectia/pages/builds/latest --jq .status 2>/dev/null || echo "")
  [ "$estado" = "built" ] && break
done
echo

revisar

paso "Listo"
echo "  Hub:     https://connectia.mx/hub/"
echo "  iPhone:  Safari → connectia.mx/hub → Compartir → Añadir a pantalla de inicio"
echo "  Mac:     Aplicaciones › Connectia"
