#!/usr/bin/env bash
# Prepara as fotos do celular para upload no Roboflow.
#
#   1. move imagens de ~/Downloads (ou da pasta indicada) para dataset/raw/
#   2. converte HEIC/HEIF -> JPG  (o Roboflow não lê HEIC)
#   3. renomeia em sequência: calcada_0001.jpg, calcada_0002.jpg, ...
#   4. conta o resultado e avisa se faltar para o mínimo da rubrica
#
# uso:  ./scripts/preparar_fotos.sh [pasta_de_origem]
#       (padrão: ~/Downloads)

set -euo pipefail

ORIGEM="${1:-$HOME/Downloads}"
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DESTINO="$REPO/dataset/raw"
MINIMO=60

mkdir -p "$DESTINO"

echo "origem  : $ORIGEM"
echo "destino : $DESTINO"
echo

# ── 1. mover ──────────────────────────────────────────────
movidas=0
shopt -s nullglob nocaseglob
for f in "$ORIGEM"/IMG_*.jpg "$ORIGEM"/IMG_*.jpeg "$ORIGEM"/IMG_*.png \
         "$ORIGEM"/IMG_*.heic "$ORIGEM"/IMG_*.heif \
         "$ORIGEM"/PXL_*.jpg "$ORIGEM"/*.HEIC; do
  [ -e "$f" ] || continue
  mv -n "$f" "$DESTINO/" && movidas=$((movidas + 1))
done
shopt -u nocaseglob
echo "→ $movidas arquivo(s) movido(s) de $ORIGEM"

# ── 2. converter HEIC ─────────────────────────────────────
convertidas=0
for f in "$DESTINO"/*.HEIC "$DESTINO"/*.heic "$DESTINO"/*.HEIF "$DESTINO"/*.heif; do
  [ -e "$f" ] || continue
  if sips -s format jpeg "$f" --out "${f%.*}.jpg" >/dev/null 2>&1; then
    rm "$f"
    convertidas=$((convertidas + 1))
  else
    echo "  ⚠️  falhou ao converter: $(basename "$f")"
  fi
done
echo "→ $convertidas HEIC convertido(s) para JPG"

# ── 3. renomear em sequência ──────────────────────────────
n=0
tmp="$DESTINO/.renomeando"
mkdir -p "$tmp"
for f in "$DESTINO"/*.jpg "$DESTINO"/*.jpeg "$DESTINO"/*.png; do
  [ -e "$f" ] || continue
  n=$((n + 1))
  mv "$f" "$(printf '%s/calcada_%04d.%s' "$tmp" "$n" "${f##*.}")"
done
mv "$tmp"/* "$DESTINO/" 2>/dev/null || true
rmdir "$tmp"
echo "→ $n arquivo(s) renomeado(s) como calcada_NNNN"

# ── 4. relatório ──────────────────────────────────────────
total=$(find "$DESTINO" -maxdepth 1 -type f \
          \( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' \) | wc -l | tr -d ' ')

echo
echo "═══════════════════════════════════════════"
echo "  $total imagem(ns) em dataset/raw/"
echo "═══════════════════════════════════════════"

if [ "$total" -ge 80 ]; then
  echo "  ✅ ótimo volume (mínimo da rubrica: $MINIMO)"
elif [ "$total" -ge "$MINIMO" ]; then
  echo "  🟡 acima do mínimo, mas sem margem para descartes."
  echo "     Capture mais algumas — fotos tremidas vão ser descartadas."
else
  echo "  ❌ faltam $((MINIMO - total)) para o mínimo de $MINIMO"
fi

echo
echo "próximo passo: suba dataset/raw/ no Roboflow e anote as 3 classes"
echo "               (regras em CAPTURA.md, seção 2.3)"
