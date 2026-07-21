#!/bin/bash
# =============================================================================
# Regera os wallpapers de fotos de capivaras (capivaraos-desktop-foto-*.png)
# =============================================================================
#
# As fotos originais NÃO ficam no repositório (apenas as versões finais com
# logo/crédito embutidos). Este script baixa de novo as fotos do Wikimedia
# Commons (CC BY-SA), recorta para 1920x1080, sobrepõe a logo branca do
# CapivaraOS no canto inferior direito e um crédito de autoria PEQUENO no
# canto inferior esquerdo, posicionado ACIMA da altura do dock inferior
# (para não ficar escondido por ele).
#
# A atribuição (CC BY-SA exige) é mantida; apenas ficou menor e mais discreta.
# Ver backgrounds/CREDITOS.txt para a lista de fontes e licenças.
#
# Requer: curl, ImageMagick (convert), python3. Precisa de acesso à rede.
# Uso:    ./regen-photo-wallpapers.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BG="${SCRIPT_DIR}/backgrounds"
UA="CapivaraOS-build/1.1 (https://capivaraos.org)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# ── Logo branca para o canto inferior direito ───────────────────────────────
convert "${BG}/CapivaraOS_Logo.png" -fill white -colorize 100% \
    -resize 220x "${TMP}/logo-branca.png"

# Faz o download de uma imagem do Wikimedia Commons pelo nome do arquivo.
baixar() {
    local nome="$1" destino="$2"
    local url
    url="$(python3 -c "import urllib.parse,sys; print('https://commons.wikimedia.org/wiki/Special:FilePath/'+urllib.parse.quote(sys.argv[1]))" "$nome")"
    echo "  baixando: $nome"
    curl -fsSL -A "$UA" -o "$destino" "$url"
}

# Gera um wallpaper final a partir da foto original.
#   $1 = arquivo original (.jpg)   $2 = saída (.png)   $3 = crédito (texto)
#
# ZONA SEGURA — por que a logo e o crédito ficam a 250px das laterais, e não
# nos 40/24px que seriam o natural para um canto.
#
# O wallpaper é 16:9 (1920x1080). Numa tela 4:3 com preenchimento por zoom
# (no Plasma, "Escalado e Cortado", que é o padrão), o corte é de
# 1920 - (1080*4/3) = 480px, ou 240px de CADA lado. Tudo a menos de 240px da
# borda lateral desaparece nessa tela.
#
# Com os 40/24px antigos, logo e crédito caíam inteiros na faixa cortada —
# diagnosticado na spin Pup em 2026-07-21, em VM 4:3, onde o crédito aparecia
# como "...ann — CC BY-SA 4.0". A spin Marsh tinha exatamente a mesma
# geometria. Isso é mais que estética: as fotos são CC BY-SA e a licença
# EXIGE atribuição, então um crédito cortado é um problema de licenciamento.
#
# 250px dá 10px de folga sobre os 240 necessários. O deslocamento vertical
# (+120/+130) é separado e existe por outro motivo: manter logo e crédito
# acima do dock inferior.
gerar() {
    local orig="$1" saida="$2" credito="$3"
    convert "$orig" \
        -resize 1920x1080^ -gravity center -extent 1920x1080 \
        "${TMP}/logo-branca.png" -gravity southeast -geometry +250+120 -composite \
        -gravity southwest -font Liberation-Sans -pointsize 22 \
        -undercolor '#00000066' -fill white \
        -annotate +250+130 "  ${credito}  " \
        "$saida"
    echo "  gerado: $(basename "$saida")"
}

# nome no Wikimedia | saída | crédito
declare -a FOTOS=(
"028 Capybara and Pink Ipê trees in Encontro das Águas State Park Photo by Giles Laurent.jpg|capivaraos-desktop-foto-ipe.png|Foto: Giles Laurent — CC BY-SA 4.0"
"Capincho.jpg|capivaraos-desktop-foto-capincho.png|Foto: Gabriel Sparrenberger — CC BY-SA 4.0"
"Capivara no Taim.jpg|capivaraos-desktop-foto-taim.png|Foto: Paulo Hopper — CC BY-SA 4.0"
"055 Capybara swimming in Encontro das Águas State Park Photo by Giles Laurent.jpg|capivaraos-desktop-foto-natacao.png|Foto: Giles Laurent — CC BY-SA 4.0"
"158 Capybara jumping in the river to escape a Jaguar in Encontro das Águas State Park Photo by Giles Laurent.jpg|capivaraos-desktop-foto-salto.png|Foto: Giles Laurent — CC BY-SA 4.0"
"Carpincho (Hydrochoerus hydrochaeris) Iberá.jpg|capivaraos-desktop-foto-ibera.png|Foto: Taragui — CC BY-SA 3.0"
)

for entrada in "${FOTOS[@]}"; do
    IFS='|' read -r nome saida credito <<< "$entrada"
    echo "== ${saida} =="
    baixar "$nome" "${TMP}/orig.jpg"
    gerar "${TMP}/orig.jpg" "${BG}/${saida}" "$credito"
done

echo
echo "Concluído. 6 wallpapers regenerados em ${BG}/"
