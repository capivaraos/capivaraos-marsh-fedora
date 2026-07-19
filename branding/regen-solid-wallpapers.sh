#!/bin/bash
# =============================================================================
# Regera os wallpapers de cor sólida (capivaraos-desktop*.png, capivaraos-
# wallpaper.png) e o ícone quadrado (icons/capivaraos.png) a partir da
# logo-mestre (backgrounds/CapivaraOS_Logo.png).
# =============================================================================
#
# Cada wallpaper sólido é um gradiente vertical linear + a logo do CapivaraOS
# centralizada. Este script reconstrói o gradiente (mesmas cores de topo/base
# de cada tema) e sobrepõe a logo — em tom bege (variantes escuras) ou branca
# (variantes "-branco"), no mesmo tamanho/posição de sempre.
#
# Para trocar a logo, basta substituir backgrounds/CapivaraOS_Logo.png e rodar
# este script (não precisa de rede).
#
# Requer: ImageMagick (magick).
# Uso:    ./regen-solid-wallpapers.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BG="${SCRIPT_DIR}/backgrounds"
IC="${SCRIPT_DIR}/icons"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

TAN="#605140"    # tom bege da logo nas variantes escuras
WHITE="#ffffff"  # logo branca nas variantes "-branco"

# Forma limpa da logo (aparada), usada como base para recolorir.
magick "${BG}/CapivaraOS_Logo.png" -trim +repage "${TMP}/shape.png"

# gerar_solido <saida> <hex_topo> <hex_base> <tint> <altura_logo> <offset_y>
gerar_solido() {
    local saida="$1" topo="$2" base="$3" tint="$4" h="$5" off="$6"
    magick -size 1920x1080 gradient:"${topo}"-"${base}" \
        \( "${TMP}/shape.png" -fill "${tint}" -colorize 100% -resize x"${h}" \) \
        -gravity center -geometry +0"${off}" -composite \
        "${BG}/${saida}"
    echo "  gerado: ${saida}"
}

echo "== wallpapers de cor sólida =="
#            saída                                    topo       base       tint    alt  offY
gerar_solido "capivaraos-desktop.png"                "#0D1117" "#1A2B4A" "$TAN"   300  -48
gerar_solido "capivaraos-desktop-azul-branco.png"    "#0D1117" "#1A2B4A" "$WHITE" 300  -48
gerar_solido "capivaraos-desktop-preto.png"          "#0A0A0D" "#1C1C24" "$WHITE" 300  -48
gerar_solido "capivaraos-desktop-roxo.png"           "#12091A" "#2A1040" "$TAN"   300  -48
gerar_solido "capivaraos-desktop-roxo-branco.png"    "#12091A" "#2A1040" "$WHITE" 300  -48
gerar_solido "capivaraos-desktop-verde.png"          "#0A1A0D" "#1A3A1E" "$TAN"   300  -48
gerar_solido "capivaraos-desktop-verde-branco.png"   "#0A1A0D" "#1A3A1E" "$WHITE" 300  -48
gerar_solido "capivaraos-wallpaper.png"              "#080808" "#080808" "$TAN"   220  -20

echo "== ícone quadrado 256x256 =="
magick -size 256x256 xc:"#1A2B4A" \
    \( "${TMP}/shape.png" -fill "$TAN" -colorize 100% -resize x120 \) \
    -gravity center -geometry +0-6 -composite \
    "${IC}/capivaraos.png"
echo "  gerado: icons/capivaraos.png"

echo
echo "Concluído."
