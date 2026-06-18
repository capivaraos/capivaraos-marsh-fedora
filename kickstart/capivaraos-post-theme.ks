# =============================================================================
# CapivaraOS Marsh — pós-instalação: tema WhiteSur (visual "macOS")
# =============================================================================
#
# Adaptado do hook 0030-macos-theme.hook.chroot do CapivaraOS Marsh (Debian).
# O layout de painéis estilo macOS (0035) e os wallpapers/avatar/plymouth/
# os-release/configuração padrão do Plasma (0010/0020) já vêm pelo pacote
# `capivaraos-branding` (ver ../rpm/capivaraos-branding.spec), que também
# instala /usr/share/capivaraos/macos-layout.js e o autostart
# capivaraos-set-layout/capivaraos-set-wallpaper.
#
# Este post-script cobre só o que depende de baixar e instalar os temas
# WhiteSur de terceiros (GitHub) e detectar, em tempo de build, os nomes que
# eles registram no sistema — exatamente como o hook 0030 fazia no chroot do
# live-build.
#
# Requisitos: acesso à rede durante o build (git clone do GitHub), igual ao
# hook original. kwriteconfig6 vem do kde-cli-tools, incluso via
# @kde-desktop-environment. sassc/optipng/gtk-murrine-engine/gtk2-engines/
# imagemagick/git já estão no %packages de capivaraos-marsh.ks.
#
# Diferenças deliberadas em relação ao hook 0030 (Debian):
#   - Não recriamos [Autologin] no sddm.conf.d: no Fedora Live isso é
#     responsabilidade genérica do livesys-scripts (usuário "liveuser").
#   - Não forçamos DisplayServer=x11: o Breeze/SDDM padrão do Fedora 44
#     funciona em Wayland; se o tema SDDM do WhiteSur não renderizar bem em
#     Wayland, isso é uma limitação conhecida do tema de terceiros, não algo
#     que devemos "corrigir" globalmente fixando X11 para todo o sistema.
#   - Não definimos gtk-modules=appmenu-gtk-module: não existe módulo
#     GTK3/4 equivalente no Fedora (ver PACKAGES.md, limitação conhecida).

%post --log=/var/log/capivaraos-post-theme.log
# Sem "set -e": a instalação dos temas WhiteSur depende de repositórios
# externos (GitHub) e seus scripts de instalação. Uma falha pontual aqui não
# deve abortar o build inteiro — o sistema continua funcional com o tema
# Breeze Dark padrão (já configurado pelo pacote capivaraos-branding) caso
# algum componente não seja instalado.

WORKDIR=$(mktemp -d)

# ── 1. WHITESUR GTK THEME ─────────────────────────────────────────────────
echo "==> Instalando WhiteSur GTK theme..."
if git clone --depth 1 https://github.com/vinceliuice/WhiteSur-gtk-theme.git "$WORKDIR/gtk-theme"; then
    ( cd "$WORKDIR/gtk-theme" && ( ./install.sh -c Dark || ./install.sh ) ) \
        || echo "AVISO: falha ao instalar WhiteSur-gtk-theme"
else
    echo "AVISO: falha ao clonar WhiteSur-gtk-theme"
fi

# ── 2. WHITESUR PARA KDE PLASMA (Aurorae, cores, tema Plasma) ───────────────
# Não usamos o pacote "Look and Feel" nem o tema de ícones do WhiteSur (ver
# seções 4 e 7) — apenas a decoração de janelas (Aurorae), o esquema de cores
# e o tema visual do Plasma, que são apenas paletas/formas, sem nenhum
# logotipo ou ícone da Apple.
echo "==> Instalando WhiteSur para KDE Plasma..."
if git clone --depth 1 https://github.com/vinceliuice/WhiteSur-kde.git "$WORKDIR/kde-theme"; then
    ( cd "$WORKDIR/kde-theme" && ( ./install.sh -c dark --sddm || ./install.sh -c dark || ./install.sh ) ) \
        || echo "AVISO: falha ao instalar WhiteSur-kde"
else
    echo "AVISO: falha ao clonar WhiteSur-kde"
fi

rm -rf "$WORKDIR"

# ── 3. DETECÇÃO DOS NOMES INSTALADOS ────────────────────────────────────────
GTK_THEME=$(ls /usr/share/themes/ 2>/dev/null | grep -i '^WhiteSur.*[Dd]ark' | head -1)
[ -z "$GTK_THEME" ] && GTK_THEME=$(ls /usr/share/themes/ 2>/dev/null | grep -i '^WhiteSur' | head -1)

# Ícones: usamos sempre o tema oficial Breeze Dark do KDE (sem ícones estilo
# Apple, ex.: o ícone de "Preferências do Sistema" do WhiteSur imita o ícone
# de Preferências do Sistema do macOS).
ICON_THEME="breeze-dark"

COLOR_SCHEME_FILE=$(ls /usr/share/color-schemes/ 2>/dev/null | grep -i 'whitesur' | grep -i 'dark' | head -1)
[ -z "$COLOR_SCHEME_FILE" ] && COLOR_SCHEME_FILE=$(ls /usr/share/color-schemes/ 2>/dev/null | grep -i 'whitesur' | head -1)
COLOR_SCHEME="${COLOR_SCHEME_FILE%.colors}"

AURORAE_THEME=$(ls /usr/share/aurorae/themes/ 2>/dev/null | grep -i 'whitesur' | grep -i 'dark' | head -1)
[ -z "$AURORAE_THEME" ] && AURORAE_THEME=$(ls /usr/share/aurorae/themes/ 2>/dev/null | grep -i 'whitesur' | head -1)

SDDM_THEME=$(ls /usr/share/sddm/themes/ 2>/dev/null | grep -i 'whitesur' | head -1)

PLASMA_THEME=$(ls /usr/share/plasma/desktoptheme/ 2>/dev/null | grep -i 'whitesur' | grep -i 'dark' | head -1)
[ -z "$PLASMA_THEME" ] && PLASMA_THEME=$(ls /usr/share/plasma/desktoptheme/ 2>/dev/null | grep -i 'whitesur' | head -1)

echo "==> Tema GTK detectado: ${GTK_THEME:-<nenhum>}"
echo "==> Tema de ícones: ${ICON_THEME} (oficial KDE)"
echo "==> Esquema de cores detectado: ${COLOR_SCHEME:-<nenhum>}"
echo "==> Decoração Aurorae detectada: ${AURORAE_THEME:-<nenhum>}"
echo "==> Tema SDDM detectado: ${SDDM_THEME:-<nenhum>}"
echo "==> Tema Plasma detectado: ${PLASMA_THEME:-<nenhum>}"

# ── 4. APLICA OS TEMAS DETECTADOS (KDE) ─────────────────────────────────────
# Importante: NÃO definimos KDE/LookAndFeelPackage para um pacote WhiteSur.
# Esse pacote "Look and Feel" traz seu próprio splash do Plasma (com um
# logotipo estilo Apple) e seu próprio script de layout de painéis, que
# entraria em conflito com o layout próprio do CapivaraOS (já aplicado via
# capivaraos-set-layout) e causaria painéis duplicados/ícones quebrados.
# Aplicamos apenas cores, ícones (Breeze), decoração de janela e tema do
# Plasma, individualmente — sobrescrevendo o que o pacote capivaraos-branding
# já gravou em /etc/skel/.config/kdeglobals.
for HOMEDIR in /root /etc/skel; do
    mkdir -p "$HOMEDIR/.config"

    KDEGLOBALS="$HOMEDIR/.config/kdeglobals"
    [ -n "$COLOR_SCHEME" ] && \
        kwriteconfig6 --file "$KDEGLOBALS" --group General --key ColorScheme "$COLOR_SCHEME" 2>/dev/null || \
        kwriteconfig5 --file "$KDEGLOBALS" --group General --key ColorScheme "$COLOR_SCHEME" 2>/dev/null || true
    kwriteconfig6 --file "$KDEGLOBALS" --group Icons --key Theme "$ICON_THEME" 2>/dev/null || \
        kwriteconfig5 --file "$KDEGLOBALS" --group Icons --key Theme "$ICON_THEME" 2>/dev/null || true

    # Desativa a tela de splash do Plasma (KSplash) para evitar qualquer
    # logotipo de terceiros entre o login e a área de trabalho.
    kwriteconfig6 --file "$KDEGLOBALS" --group KSplash --key Theme "None" 2>/dev/null || \
        kwriteconfig5 --file "$KDEGLOBALS" --group KSplash --key Theme "None" 2>/dev/null || true

    # Força o "Look and Feel" padrão do KDE (Breeze Dark), sobrescrevendo
    # qualquer KDE/LookAndFeelPackage=com.github.vinceliuice.WhiteSur-* que o
    # instalador do WhiteSur-kde (seção 2) tenha definido.
    kwriteconfig6 --file "$KDEGLOBALS" --group KDE --key LookAndFeelPackage "org.kde.breezedark.desktop" 2>/dev/null || \
        kwriteconfig5 --file "$KDEGLOBALS" --group KDE --key LookAndFeelPackage "org.kde.breezedark.desktop" 2>/dev/null || true

    if [ -n "$AURORAE_THEME" ]; then
        KWINRC="$HOMEDIR/.config/kwinrc"
        kwriteconfig6 --file "$KWINRC" --group "org.kde.kdecoration2" --key library "org.kde.kwin.aurorae" 2>/dev/null || \
        kwriteconfig5 --file "$KWINRC" --group "org.kde.kdecoration2" --key library "org.kde.kwin.aurorae" 2>/dev/null || true
        kwriteconfig6 --file "$KWINRC" --group "org.kde.kdecoration2" --key theme "__aurorae__svg__${AURORAE_THEME}" 2>/dev/null || \
        kwriteconfig5 --file "$KWINRC" --group "org.kde.kdecoration2" --key theme "__aurorae__svg__${AURORAE_THEME}" 2>/dev/null || true
    fi

    if [ -n "$PLASMA_THEME" ]; then
        cat > "$HOMEDIR/.config/plasmarc" << EOF
[Theme]
name=${PLASMA_THEME}
EOF
    fi
done

# ── 5. APLICA OS TEMAS GTK (apps GTK seguem o visual WhiteSur, ícones Breeze) ─
if [ -n "$GTK_THEME" ]; then
    for HOMEDIR in /root /etc/skel; do
        mkdir -p "$HOMEDIR/.config/gtk-3.0" "$HOMEDIR/.config/gtk-4.0"

        cat > "$HOMEDIR/.config/gtk-3.0/settings.ini" << EOF
[Settings]
gtk-theme-name=${GTK_THEME:-Adwaita-dark}
gtk-icon-theme-name=${ICON_THEME}
gtk-application-prefer-dark-theme=1
EOF
        cp "$HOMEDIR/.config/gtk-3.0/settings.ini" "$HOMEDIR/.config/gtk-4.0/settings.ini"

        cat > "$HOMEDIR/.gtkrc-2.0" << EOF
gtk-theme-name="${GTK_THEME:-Adwaita-dark}"
gtk-icon-theme-name="${ICON_THEME}"
EOF
    done
fi

# ── 6. TEMA DO SDDM (tela de login) ─────────────────────────────────────────
# O pacote capivaraos-branding já gravou o wallpaper do CapivaraOS em
# /usr/share/sddm/themes/breeze/theme.conf.user. Se o WhiteSur-kde instalou
# um tema próprio para o SDDM, copiamos o mesmo wallpaper para ele e o
# selecionamos como tema padrão (mantendo a identidade visual do CapivaraOS,
# agora com a decoração WhiteSur).
if [ -n "$SDDM_THEME" ]; then
    EXISTING_BG=""
    [ -f /usr/share/sddm/themes/breeze/theme.conf.user ] && \
        EXISTING_BG=$(grep -m1 '^background=' /usr/share/sddm/themes/breeze/theme.conf.user | cut -d= -f2-)

    if [ -n "$EXISTING_BG" ]; then
        mkdir -p "/usr/share/sddm/themes/${SDDM_THEME}"
        cat > "/usr/share/sddm/themes/${SDDM_THEME}/theme.conf.user" << EOF
[General]
background=${EXISTING_BG}
EOF
    fi

    mkdir -p /etc/sddm.conf.d
    cat > /etc/sddm.conf.d/capivaraos.conf << EOF
[Theme]
Current=${SDDM_THEME}
EOF
fi

# ── 7. REMOVE ITENS DO WHITESUR NÃO UTILIZADOS QUE IMITAM A APPLE ───────────
# O tema de ícones WhiteSur (preferences-system*, etc.) imita literalmente
# ícones do macOS e não é usado (ICON_THEME=breeze-dark). O pacote "Look and
# Feel" com.github.vinceliuice.WhiteSur-dark traz seu próprio KSplash com
# logotipo estilo Apple e também não é usado (LookAndFeelPackage=
# org.kde.breezedark.desktop, seção 4). Os wallpapers próprios do WhiteSur
# (WhiteSur, WhiteSur-dark, WhiteSur-light, Next) também não fazem parte da
# identidade visual do CapivaraOS. Removemos tudo isso do sistema final por
# segurança jurídica, mantendo apenas o que é estilo/paleta (tema GTK,
# esquemas de cores, Aurorae, tema Plasma do WhiteSur), sem nenhum ícone ou
# logotipo da Apple.
rm -rf /usr/share/icons/WhiteSur /usr/share/icons/WhiteSur-dark /usr/share/icons/WhiteSur-light
rm -rf /usr/share/plasma/look-and-feel/com.github.vinceliuice.WhiteSur-dark
for WP in WhiteSur WhiteSur-dark WhiteSur-light Next; do
    rm -rf "/usr/share/wallpapers/${WP}"
done

# ── 8. ATUALIZA CACHES DE TEMA/ÍCONES ───────────────────────────────────────
gtk-update-icon-cache -f /usr/share/icons/hicolor 2>/dev/null || true
gtk-update-icon-cache -f "/usr/share/icons/${ICON_THEME}" 2>/dev/null || true

%end
