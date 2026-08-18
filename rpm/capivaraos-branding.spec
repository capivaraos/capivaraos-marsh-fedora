# capivaraos-branding — identidade visual do CapivaraOS Marsh (Fedora)
#
# Reimplementa em formato RPM o que os hooks do live-build faziam no
# CapivaraOS Marsh (Debian):
#   - 0010-wallpaper.hook.chroot  -> wallpapers, pacotes de wallpaper KDE,
#                                     script de aplicação no primeiro login
#   - 0020-desktop.hook.chroot    -> os-release, issue, plymouth, ícones
#                                     "Sobre o sistema", avatar, layout macOS
#
# O tema WhiteSur (GTK/KDE) e o ajuste fino do layout estilo macOS que
# dependem dele continuam em kickstart/capivaraos-post-theme.ks, pois
# exigem git clone de repositórios externos durante o build da imagem.

Name:           capivaraos-branding
Version:        1.2.4
# Sufixo ".marsh": as tres spins constroem um pacote com este MESMO Name e
# compartilham ~/rpmbuild, entao sem ele duas spins na mesma Version-Release
# geram nomes de arquivo identicos -- ja causou dois incidentes (ver BUG-30).
# Com o sufixo a colisao e impossivel por construcao.
Release:        1%{?dist}.marsh
Summary:        Identidade visual, wallpapers e tema padrão do CapivaraOS Marsh

License:        GPL-3.0-or-later AND LicenseRef-CapivaraOS-Trademark AND CC-BY-SA-3.0 AND CC-BY-SA-4.0
URL:            https://capivaraos.org
BuildArch:      noarch

Source0:        %{name}-%{version}.tar.gz

BuildRequires:  ImageMagick
# /usr/bin/convert
Requires:       plymouth
Requires:       sddm
Requires:       kde-settings

# Fornecemos nosso próprio /etc/os-release, ícones "Sobre o Sistema" e
# wallpapers padrão do Fedora KDE.
Conflicts:      fedora-release-kde-desktop
Conflicts:      fedora-logos

%description
Pacote de identidade visual do CapivaraOS Marsh: wallpapers (incluindo as
fotos de capivaras do Wikimedia Commons, CC BY-SA), conjunto de ícones
"capivaraos-logo", "capivaraos-full-logo" e "capivaraos-head", tema Plymouth
de boot, tela de login SDDM, /etc/os-release, /etc/issue, configuração padrão do Plasma
(Breeze Dark + wallpaper CapivaraOS) e o layout de painéis estilo macOS
(menu global no topo + dock inferior).

%prep
%setup -q

%build
set -e

# ── 1. Ícones hicolor "capivaraos-logo" (apenas a capivara, sem texto) ──────
# Fonte: icons/capivaraos-logo.png (1536x1024)
mkdir -p build/icons
for SIZE in 16 22 24 32 48 64 96 128 256 512; do
    mkdir -p "build/icons/hicolor/${SIZE}x${SIZE}/apps"
    convert icons/capivaraos-logo.png -resize "${SIZE}x${SIZE}" \
        "build/icons/hicolor/${SIZE}x${SIZE}/apps/capivaraos-logo.png"
done

# ── 2. Ícones hicolor "capivaraos-full-logo" (capivara + texto "CapivaraOS") ─
# Usado pelo KCM "Sobre este Sistema" (LOGO= em /etc/os-release).
# Fonte: backgrounds/CapivaraOS_Logo.png (1536x1024) ajustada para canvas
# quadrado transparente antes do resize, evitando distorção.
for SIZE in 16 22 24 32 48 64 96 128 256 512; do
    mkdir -p "build/icons/hicolor/${SIZE}x${SIZE}/apps"
    convert backgrounds/CapivaraOS_Logo.png -background none -gravity center \
        -extent 1536x1536 -resize "${SIZE}x${SIZE}" \
        "build/icons/hicolor/${SIZE}x${SIZE}/apps/capivaraos-full-logo.png"
done

# ── 2b. Ícones hicolor "capivaraos-head" (só a cabeça da capivara) ──────────
# Usado como ícone do lançador de aplicativos (kickoff) no dock, no lugar do
# logo do KDE. Fonte: icons/capivaraos-head.png (215x215, canvas quadrado) —
# silhueta BRANCA, para combinar com o painel/dock escuro do Breeze Dark.
for SIZE in 16 22 24 32 48 64 96 128 256 512; do
    mkdir -p "build/icons/hicolor/${SIZE}x${SIZE}/apps"
    convert icons/capivaraos-head.png -resize "${SIZE}x${SIZE}" \
        "build/icons/hicolor/${SIZE}x${SIZE}/apps/capivaraos-head.png"
done

# ── 3. Ícone branco para a área de trabalho ("Instalar CapivaraOS" etc) ─────
mkdir -p build/pixmaps
convert icons/capivaraos-logo.png -fill white -colorize 100% \
    -resize 256x256 build/pixmaps/capivaraos-white.png

# ── 4. Avatar padrão (.face): recorta só a capivara, fundo branco quadrado ──
convert backgrounds/CapivaraOS_Logo.png -crop 1536x600+0+0 +repage -trim +repage \
    -gravity center -background white -extent 1700x1700 \
    -resize 256x256 build/pixmaps/capivaraos-face.png

# ── 5. Logo BRANCA para o splash do Plymouth (boot/desligamento) ────────────
mkdir -p build/plymouth
convert backgrounds/CapivaraOS_Logo.png -fill white -colorize 100% \
    -resize 320x320 build/plymouth/logo.png

# Spinner branco (arco girando) exibido logo abaixo da logo no splash.
# Geramos 30 quadros, cada um girado 12°, e o script do Plymouth os cicla.
mkdir -p build/plymouth/spinner
convert -size 64x64 xc:none -stroke white -strokewidth 5 \
    -fill none -draw "stroke-linecap round arc 12,12 52,52 0,300" \
    build/plymouth/spinner-base.png
for i in $(seq 0 29); do
    ANG=$(( i * 12 ))
    convert build/plymouth/spinner-base.png -background none \
        -distort SRT ${ANG} +repage "build/plymouth/spinner/${i}.png"
done

# ── 6. Pacotes de wallpaper no formato KDE (aparecem no seletor do Plasma) ──
# Cada wallpaper "capivaraos-*" do live-build vira um pacote
# /usr/share/wallpapers/<id>/{metadata.json,contents/images/*.png}
mkdir -p build/wallpapers

create_kde_wallpaper_pkg() {
    local ID="$1" NAME="$2" FILE="$3" AUTHOR="${4:-CapivaraOS}"
    local DIR="build/wallpapers/${ID}/contents/images"
    mkdir -p "$DIR"
    cp "$FILE" "${DIR}/1920x1080.png"
    convert "$FILE" -resize 400x250 "${DIR}/400x250.png" 2>/dev/null || \
        cp "$FILE" "${DIR}/400x250.png"
    cat > "build/wallpapers/${ID}/metadata.json" << METAEOF
{
    "KPlugin": {
        "Authors": [{"Name": "${AUTHOR}"}],
        "Id": "${ID}",
        "License": "CC-BY-SA-4.0",
        "Name": "${NAME}",
        "Version": "%{version}",
        "Website": "https://capivaraos.org"
    },
    "X-KDE-PluginInfo-Name": "${ID}"
}
METAEOF
}

create_kde_wallpaper_pkg "capivaraos-azul" "CapivaraOS Azul" \
    backgrounds/capivaraos-desktop.png
create_kde_wallpaper_pkg "capivaraos-verde" "CapivaraOS Verde" \
    backgrounds/capivaraos-desktop-verde.png
create_kde_wallpaper_pkg "capivaraos-roxo" "CapivaraOS Roxo" \
    backgrounds/capivaraos-desktop-roxo.png
create_kde_wallpaper_pkg "capivaraos-preto" "CapivaraOS Preto" \
    backgrounds/capivaraos-desktop-preto.png
create_kde_wallpaper_pkg "capivaraos-azul-branco" "CapivaraOS Azul (logo branca)" \
    backgrounds/capivaraos-desktop-azul-branco.png
create_kde_wallpaper_pkg "capivaraos-verde-branco" "CapivaraOS Verde (logo branca)" \
    backgrounds/capivaraos-desktop-verde-branco.png
create_kde_wallpaper_pkg "capivaraos-roxo-branco" "CapivaraOS Roxo (logo branca)" \
    backgrounds/capivaraos-desktop-roxo-branco.png

# Wallpapers com fotos reais de capivaras (Wikimedia Commons, CC BY-SA)
create_kde_wallpaper_pkg "capivaraos-foto-ipe" "CapivaraOS Ipê Rosa" \
    backgrounds/capivaraos-desktop-foto-ipe.png \
    "Giles Laurent (Wikimedia Commons, CC BY-SA 4.0)"
create_kde_wallpaper_pkg "capivaraos-foto-capincho" "CapivaraOS Retrato" \
    backgrounds/capivaraos-desktop-foto-capincho.png \
    "Gabriel Sparrenberger (Wikimedia Commons, CC BY-SA 4.0)"
create_kde_wallpaper_pkg "capivaraos-foto-taim" "CapivaraOS Taim" \
    backgrounds/capivaraos-desktop-foto-taim.png \
    "Paulo Hopper (Wikimedia Commons, CC BY-SA 4.0)"
create_kde_wallpaper_pkg "capivaraos-foto-natacao" "CapivaraOS Natação" \
    backgrounds/capivaraos-desktop-foto-natacao.png \
    "Giles Laurent (Wikimedia Commons, CC BY-SA 4.0)"
create_kde_wallpaper_pkg "capivaraos-foto-salto" "CapivaraOS Rio" \
    backgrounds/capivaraos-desktop-foto-salto.png \
    "Giles Laurent (Wikimedia Commons, CC BY-SA 4.0)"
create_kde_wallpaper_pkg "capivaraos-foto-ibera" "CapivaraOS Iberá" \
    backgrounds/capivaraos-desktop-foto-ibera.png \
    "Taragui (Wikimedia Commons, CC BY-SA 3.0)"

%install
set -e
DEFAULT_WP=%{_datadir}/backgrounds/capivaraos/capivaraos-desktop-foto-natacao.png

# ── Wallpapers (arquivos originais + créditos) ──────────────────────────────
install -d %{buildroot}%{_datadir}/backgrounds/capivaraos
# NAO instalamos backgrounds/CapivaraOS_Logo.png: apesar de morar nesta pasta,
# ela nao e um wallpaper -- e a arte-mestre (1536x1024) da qual os wallpapers
# sao derivados. Instalada aqui, aparecia no seletor de papel de parede como
# uma opcao escolhivel e, ao ser aplicada, saia com a logo gigante e cortada
# pelo painel (visto na Pup 1.1.1 em 2026-07-21).
for WP in backgrounds/*.png; do
    [ "$(basename "$WP")" = "CapivaraOS_Logo.png" ] && continue
    install -m 0644 "$WP" %{buildroot}%{_datadir}/backgrounds/capivaraos/
done
install -m 0644 backgrounds/CREDITOS.txt %{buildroot}%{_datadir}/backgrounds/capivaraos/

# ── Pixmaps ──────────────────────────────────────────────────────────────────
install -d %{buildroot}%{_datadir}/pixmaps
install -m 0644 icons/capivaraos.png %{buildroot}%{_datadir}/pixmaps/capivaraos.png
install -m 0644 icons/capivaraos-logo.png %{buildroot}%{_datadir}/pixmaps/capivaraos-logo.png
install -m 0644 build/pixmaps/capivaraos-white.png %{buildroot}%{_datadir}/pixmaps/capivaraos-white.png

# ── Icones hicolor ───────────────────────────────────────────────────────────
for SIZE in 16 22 24 32 48 64 96 128 256 512; do
    install -d %{buildroot}%{_datadir}/icons/hicolor/${SIZE}x${SIZE}/apps
    install -m 0644 "build/icons/hicolor/${SIZE}x${SIZE}/apps/capivaraos-logo.png" \
        %{buildroot}%{_datadir}/icons/hicolor/${SIZE}x${SIZE}/apps/
    install -m 0644 "build/icons/hicolor/${SIZE}x${SIZE}/apps/capivaraos-full-logo.png" \
        %{buildroot}%{_datadir}/icons/hicolor/${SIZE}x${SIZE}/apps/
    install -m 0644 "build/icons/hicolor/${SIZE}x${SIZE}/apps/capivaraos-head.png" \
        %{buildroot}%{_datadir}/icons/hicolor/${SIZE}x${SIZE}/apps/
done

# ── Pacotes de wallpaper KDE ─────────────────────────────────────────────────
install -d %{buildroot}%{_datadir}/wallpapers
cp -r build/wallpapers/* %{buildroot}%{_datadir}/wallpapers/
find %{buildroot}%{_datadir}/wallpapers -type f -exec chmod 0644 {} \;
find %{buildroot}%{_datadir}/wallpapers -type d -exec chmod 0755 {} \;

# ── Tema Plymouth ────────────────────────────────────────────────────────────
install -d %{buildroot}%{_datadir}/plymouth/themes/capivaraos
install -m 0644 build/plymouth/logo.png \
    %{buildroot}%{_datadir}/plymouth/themes/capivaraos/logo.png

# Quadros do spinner (arco branco girando)
install -d %{buildroot}%{_datadir}/plymouth/themes/capivaraos/spinner
install -m 0644 build/plymouth/spinner/*.png \
    %{buildroot}%{_datadir}/plymouth/themes/capivaraos/spinner/

cat > %{buildroot}%{_datadir}/plymouth/themes/capivaraos/capivaraos.plymouth << 'EOF'
[Plymouth Theme]
Name=CapivaraOS
Description=CapivaraOS boot splash
ModuleName=script

[script]
ImageDir=/usr/share/plymouth/themes/capivaraos
ScriptFile=/usr/share/plymouth/themes/capivaraos/capivaraos.script
EOF

cat > %{buildroot}%{_datadir}/plymouth/themes/capivaraos/capivaraos.script << 'EOF'
Window.SetBackgroundTopColor(0.07, 0.09, 0.13);
Window.SetBackgroundBottomColor(0.07, 0.09, 0.13);

# ── Logo branca (acima do spinner) ──────────────────────────────────────────
logo.image = Image("logo.png");
logo.sprite = Sprite(logo.image);
logo.x = Window.GetWidth() / 2 - logo.image.GetWidth() / 2;
logo.y = Window.GetHeight() / 2 - logo.image.GetHeight() / 2 - 80;
logo.sprite.SetPosition(logo.x, logo.y, 1);

# ── Spinner (arco branco girando, logo abaixo da logo) ──────────────────────
spinner_frame_count = 30;
for (i = 0; i < spinner_frame_count; i++)
    spinner_image[i] = Image("spinner/" + i + ".png");

spinner.sprite = Sprite();
spinner.cx = Window.GetWidth() / 2;
spinner.cy = logo.y + logo.image.GetHeight() + 50;
spinner.frame = 0;

# ── Mensagem (abaixo do spinner) ────────────────────────────────────────────
# "updates"/"system-upgrade": modo usado pelo PackageKit/Discover ao reiniciar
# para aplicar atualizacoes offline (systemd system-update.target). Sem essa
# checagem, esse boot mostraria a mesma mensagem de inicializacao normal.
is_updates = (Plymouth.GetMode() == "updates" || Plymouth.GetMode() == "system-upgrade");

if (Plymouth.GetMode() == "shutdown" || Plymouth.GetMode() == "reboot") {
    message_text = "Encerrando o CapivaraOS";
} else if (is_updates) {
    message_text = "Instalando atualizações";
} else {
    message_text = "Inicializando o CapivaraOS";
}

message.image = Image.Text(message_text, 1, 1, 1, 1, "Sans 14");
message.sprite = Sprite(message.image);
message.sprite.SetPosition(Window.GetWidth() / 2 - message.image.GetWidth() / 2,
                            spinner.cy + 70, 1);

# ── Aviso + percentual, somente durante atualizacao offline ────────────────
if (is_updates) {
    warning.image = Image.Text("Não desligue o computador", 0.8, 0.8, 0.8, 1, "Sans 11");
    warning.sprite = Sprite(warning.image);
    warning.sprite.SetPosition(Window.GetWidth() / 2 - warning.image.GetWidth() / 2,
                                spinner.cy + 95, 1);

    # PackageKit/Discover reporta o progresso via "plymouth system-update
    # --progress=N" (N de 0 a 100) enquanto instala os pacotes baixados.
    fun system_update_callback(progress) {
        percent.image = Image.Text(Math.Int(progress) + "%", 1, 1, 1, 1, "Sans 11");
        if (percent.sprite)
            percent.sprite.SetImage(percent.image);
        else
            percent.sprite = Sprite(percent.image);
        percent.sprite.SetPosition(Window.GetWidth() / 2 - percent.image.GetWidth() / 2,
                                    spinner.cy + 118, 1);
    }
    Plymouth.SetSystemUpdateFunction(system_update_callback);
}

fun refresh_callback() {
    spinner.frame++;
    if (spinner.frame >= spinner_frame_count * 3)
        spinner.frame = 0;
    idx = Math.Int(spinner.frame / 3);
    img = spinner_image[idx];
    spinner.sprite.SetImage(img);
    spinner.sprite.SetX(spinner.cx - img.GetWidth() / 2);
    spinner.sprite.SetY(spinner.cy - img.GetHeight() / 2);
}
Plymouth.SetRefreshFunction(refresh_callback);
EOF

# NOTA CapivaraOS: /etc/os-release, /etc/issue, /etc/issue.net e
# /etc/xdg/kcm-about-distrorc NAO sao gerados aqui (em %{buildroot}). Esses
# caminhos tambem pertencem a fedora-release-common e kde-settings, e tê-los
# em %files causa "conflito de arquivo" no dnf durante a transacao de
# instalacao (PayloadInstallationError). Em vez disso, sao escritos
# diretamente no sistema instalado em %posttrans (ver abaixo), que roda
# depois de toda a transacao e garante que nosso conteudo prevaleca.

# ── /etc/skel: wallpaper, tela de bloqueio e tema padrão (Breeze Dark) ──────
install -d %{buildroot}%{_sysconfdir}/skel/.config

cat > %{buildroot}%{_sysconfdir}/skel/.config/plasma-org.kde.plasma.desktop-appletsrc << EOF
[Containments][1][Wallpaper][org.kde.image][General]
Image=${DEFAULT_WP}
FillMode=2
EOF

cat > %{buildroot}%{_sysconfdir}/skel/.config/kscreenlockerrc << EOF
[Greeter][Wallpaper][org.kde.image][General]
Image=${DEFAULT_WP}
FillMode=2
EOF

cat > %{buildroot}%{_sysconfdir}/skel/.config/kdeglobals << 'EOF'
[General]
ColorScheme=BreezeDark

[KDE]
LookAndFeelPackage=org.kde.breezedark.desktop
SingleClick=false

[KSplash]
Theme=None
EOF

cat > %{buildroot}%{_sysconfdir}/skel/.config/plasmarc << 'EOF'
[Theme]
name=breeze-dark
EOF

# Desativa o assistente de primeiro boot do Plasma (plasma-welcome / tela
# "Bem-vindo ao Plasma Desktop"). O fundo dessa tela é compilado no binário do
# plasma-welcome (não é personalizável para a identidade do CapivaraOS) e a
# tela é disparada pelo módulo KDED, não pelo autostart. Pré-gravar um
# LastSeenVersion alto faz o plasma-welcome considerar que o usuário já viu a
# apresentação, então o OOBE não aparece para novos usuários (sistema
# instalado). Na sessão live o livesys-kde escreve seu próprio plasma-welcomerc
# (LiveEnvironment=true), então este valor só afeta o sistema instalado.
# IMPORTANTE: a chave é "LastSeenVersion" (com L/S/V maiúsculos) -- é o nome
# exato lido pelo kded_plasma_welcome (confirmado via strings do binário). A
# variante "lastSeenVersion" (camelCase) é IGNORADA, e o módulo trata isso
# como "sem versão vista", disparando a tela de boas-vindas mesmo assim.
cat > %{buildroot}%{_sysconfdir}/skel/.config/plasma-welcomerc << 'EOF'
[General]
LastSeenVersion=99.0.0
EOF

# ── Avatar padrão (.face) para novos usuários ────────────────────────────────
install -m 0644 build/pixmaps/capivaraos-face.png %{buildroot}%{_sysconfdir}/skel/.face
ln -sf .face %{buildroot}%{_sysconfdir}/skel/.face.icon

# ── Layout estilo macOS: script JS do Plasma + autostarts de aplicação única ─
install -d %{buildroot}%{_datadir}/capivaraos
cat > %{buildroot}%{_datadir}/capivaraos/macos-layout.js << 'EOF'
// Remove quaisquer paineis existentes (layout padrao do Plasma / Look and Feel)
var ids = panelIds;
for (var i = 0; i < ids.length; i++) {
    panelById(ids[i]).remove();
}

// ── Painel superior (menu global estilo macOS) ──────────────────────────────
var topPanel = new Panel();
topPanel.location = "top";
topPanel.height = 28;
// Flutuante + translucido, para combinar com o dock inferior (visual
// "barra flutuante" do macOS, com a mesma transparencia nos dois paineis).
topPanel.floating = true;
topPanel.opacityMode = 2; // Panel.Global.Translucent

topPanel.addWidget("org.kde.plasma.appmenu");
topPanel.addWidget("org.kde.plasma.panelspacer");

// Previsao do tempo (widget proprio, do kdeplasma-addons)
var weather = topPanel.addWidget("org.kde.plasma.weather");
// Aparencia: temperatura ao lado do icone do widget; dica (tooltip) mostra
// temperatura, vento e umidade, mas nao a pressao.
weather.currentConfigGroup = ["Appearance"];
weather.writeConfig("showTemperatureInCompactMode", true);
weather.writeConfig("showTemperatureInBadge", false);
weather.writeConfig("showTemperatureInTooltip", true);
weather.writeConfig("showWindInTooltip", true);
weather.writeConfig("showPressureInTooltip", false);
weather.writeConfig("showHumidityInTooltip", true);

// Bandeja do sistema: mostra apenas volume, redes, layout de teclado e
// notificacoes; os demais itens ficam recolhidos (showAllItems=false) e os
// mais comuns sao explicitamente ocultados.
var systray = topPanel.addWidget("org.kde.plasma.systemtray");
systray.currentConfigGroup = ["General"];
systray.writeConfig("showAllItems", false);
// shownItems / hiddenItems sao StringList -> precisam ser ARRAYS JS (idem
// launchers do dock; string com virgulas nao funciona).
systray.writeConfig("shownItems", [
    "org.kde.plasma.volume",
    "org.kde.plasma.networkmanagement",
    "org.kde.plasma.keyboardlayout",
    "org.kde.plasma.notifications"
]);
systray.writeConfig("hiddenItems", [
    "org.kde.plasma.battery",
    "org.kde.plasma.brightness",
    "org.kde.plasma.clipboard",
    "org.kde.plasma.devicenotifier",
    "org.kde.plasma.bluetooth",
    "org.kde.plasma.mediacontroller",
    "org.kde.kscreen",
    "org.kde.plasma.printmanager"
]);

// Encerramento de sessao / bloquear tela
topPanel.addWidget("org.kde.plasma.lock_logout");
// Hora e data
topPanel.addWidget("org.kde.plasma.digitalclock");

// ── Dock inferior estilo macOS ──────────────────────────────────────────────
var dock = new Panel();
dock.location = "bottom";
dock.height = 64;
dock.alignment = "center";
dock.lengthMode = "fit";
// Flutuante + translucido, igual ao painel superior (visual "dock" do
// macOS, com a mesma transparencia em ambos os paineis).
dock.floating = true;
dock.opacityMode = 2; // Panel.Global.Translucent
dock.hiding = "none";

// Lancador de aplicativos (mantido). O icone padrao e o logo do KDE
// ("start-here-kde-symbolic"); trocamos pela cabeca da capivara da nossa
// logo (icone hicolor "capivaraos-head", instalado por este pacote).
var kickoff = dock.addWidget("org.kde.plasma.kickoff");
kickoff.currentConfigGroup = ["General"];
kickoff.writeConfig("icon", "capivaraos-head");

// Aplicativos fixados no dock, na ordem pedida (esquerda -> direita):
// Configuracoes do Sistema, Discover, Firefox, VLC, Dolphin, Spectacle,
// LibreOffice. IDs .desktop conferidos no proprio sistema instalado
// (Fedora 44): firefox = org.mozilla.firefox.desktop; configuracoes =
// systemsettings.desktop; Discover = org.kde.discover.desktop.
var tasks = dock.addWidget("org.kde.plasma.icontasks");
tasks.currentConfigGroup = ["General"];
// IMPORTANTE: "launchers" é um StringList — precisa ser um ARRAY JS. Passar
// uma string única com vírgulas faz o Plasma tratar tudo como UM lançador
// inválido (aparece como uma "folha em branco" no dock).
tasks.writeConfig("launchers", [
    "applications:systemsettings.desktop",
    "applications:org.kde.discover.desktop",
    "applications:org.mozilla.firefox.desktop",
    "applications:vlc.desktop",
    "applications:org.kde.dolphin.desktop",
    "applications:org.kde.spectacle.desktop",
    "applications:libreoffice-writer.desktop"
]);
EOF

install -d %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/capivaraos-set-layout << 'EOF'
#!/bin/bash
MARKER="$HOME/.config/.capivaraos-layout-applied"
[ -f "$MARKER" ] && exit 0

for i in $(seq 1 30); do
    pgrep -x plasmashell >/dev/null 2>&1 && break
    sleep 1
done
# Aguarda 12s para o Plasma + Look and Feel terminarem a criacao assincrona
# de todos os paineis padrao. Com 5s, o L&F criava um dock extra apos o
# primeiro evaluateScript, causando duplicidade visual por ~5s ate a segunda
# chamada limpar. Com 12s, aplicamos o layout uma unica vez, ja com todos os
# paineis do L&F presentes, e removemos tudo de uma vez.
sleep 12

QDBUS=""
for CAND in qdbus6 qdbus-qt6 qdbus; do
    command -v "$CAND" >/dev/null 2>&1 && QDBUS="$CAND" && break
done

if [ -n "$QDBUS" ]; then
    "$QDBUS" org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript \
        "$(cat /usr/share/capivaraos/macos-layout.js)" >/dev/null 2>&1 || true
fi

mkdir -p "$HOME/.config"
touch "$MARKER"
EOF
chmod 0755 %{buildroot}%{_bindir}/capivaraos-set-layout

cat > %{buildroot}%{_bindir}/capivaraos-set-wallpaper << EOF
#!/bin/bash
MARKER="\$HOME/.config/.capivaraos-wallpaper-applied"
[ -f "\$MARKER" ] && exit 0

for i in \$(seq 1 30); do
    pgrep -x plasmashell >/dev/null 2>&1 && break
    sleep 1
done
sleep 2

if command -v plasma-apply-wallpaperimage >/dev/null 2>&1; then
    plasma-apply-wallpaperimage "${DEFAULT_WP}" >/dev/null 2>&1
fi

mkdir -p "\$HOME/.config"
touch "\$MARKER"
EOF
chmod 0755 %{buildroot}%{_bindir}/capivaraos-set-wallpaper

install -d %{buildroot}%{_sysconfdir}/xdg/autostart
cat > %{buildroot}%{_sysconfdir}/xdg/autostart/capivaraos-wallpaper.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=CapivaraOS Wallpaper
Exec=/usr/bin/capivaraos-set-wallpaper
NoDisplay=true
X-KDE-autostart-phase=2
OnlyShowIn=KDE;
EOF

cat > %{buildroot}%{_sysconfdir}/xdg/autostart/capivaraos-layout.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=CapivaraOS Layout
Exec=/usr/bin/capivaraos-set-layout
NoDisplay=true
X-KDE-autostart-phase=2
OnlyShowIn=KDE;
EOF

# ── Perfil do Anaconda: faz o instalador reconhecer o CapivaraOS (BUG-38) ────
# O Anaconda casa o perfil de instalacao pelo os_id do /etc/os-release. Como o
# nosso ID e "capivaraos" (nao "fedora"), NENHUM perfil casava e o instalador
# caia no default de /etc/anaconda/anaconda.conf, que define efi_dir=default.
# Em UEFI isso faz o gen_grub_cfgstub tentar gravar o stub em
# /boot/efi/EFI/default (inexistente -- shim/grub2-efi instalam em /EFI/fedora)
# -> "gen_grub_cfgstub script failed" e a instalacao FALHA no passo do
# bootloader. So aparece em UEFI real; em VM no modo BIOS/legacy o caminho EFI
# nem roda (por isso nao pegamos antes). Herdando base_profile=fedora, o
# CapivaraOS reusa efi_dir=fedora, esquema BTRFS e demais ajustes do Fedora.
install -d %{buildroot}%{_sysconfdir}/anaconda/profile.d
cat > %{buildroot}%{_sysconfdir}/anaconda/profile.d/capivaraos.conf << 'EOF'
[Profile]
profile_id = capivaraos
base_profile = fedora

[Profile Detection]
os_id = capivaraos
EOF

%post
# Splash de boot CapivaraOS
plymouth-set-default-theme capivaraos >/dev/null 2>&1 || true

# Tela de login SDDM com wallpaper CapivaraOS (tema breeze, mecanismo
# padrao de customizacao via theme.conf.user — nao sobrescreve o tema)
install -d %{_datadir}/sddm/themes/breeze
cat > %{_datadir}/sddm/themes/breeze/theme.conf.user << 'EOF'
[General]
background=%{_datadir}/backgrounds/capivaraos/capivaraos-desktop-foto-natacao.png
EOF

# GRUB_DISTRIBUTOR -> "CapivaraOS" (efetivo apos grub2-mkconfig no sistema
# instalado; a ISO live em si usa o titulo passado ao livemedia-creator)
if [ -f %{_sysconfdir}/default/grub ]; then
    if grep -q '^GRUB_DISTRIBUTOR=' %{_sysconfdir}/default/grub; then
        sed -i 's/^GRUB_DISTRIBUTOR=.*/GRUB_DISTRIBUTOR="CapivaraOS"/' %{_sysconfdir}/default/grub
    else
        echo 'GRUB_DISTRIBUTOR="CapivaraOS"' >> %{_sysconfdir}/default/grub
    fi
fi

gtk-update-icon-cache -f %{_datadir}/icons/hicolor >/dev/null 2>&1 || true

%postun
if [ "$1" -eq 0 ]; then
    gtk-update-icon-cache -f %{_datadir}/icons/hicolor >/dev/null 2>&1 || true
fi

%posttrans
# Tema padrao do Plymouth (boot/desligamento): escrito direto aqui, em vez de
# depender so do "plymouth-set-default-theme capivaraos" do %post, porque o
# pacote plymouth grava /etc/plymouth/plymouthd.conf com "Theme=" comentado
# e plymouth-set-default-theme so EDITA uma linha "Theme=" existente -- nao
# descomenta/cria a linha se ela nao existir descomentada. Escrevendo aqui
# (%posttrans, depois de toda a transacao) garantimos que o tema CapivaraOS
# fique ativo quando o dracut gerar a initramfs da ISO live (etapa que roda
# depois, no %post do kickstart).
install -d %{_sysconfdir}/plymouth
cat > %{_sysconfdir}/plymouth/plymouthd.conf << 'EOF'
[Daemon]
Theme=capivaraos
EOF
plymouth-set-default-theme capivaraos >/dev/null 2>&1 || true

# /etc/os-release, /etc/issue, /etc/issue.net (fedora-release-common) e
# /etc/xdg/kcm-about-distrorc (kde-settings): escritos aqui (em vez de
# %files) para evitar conflito de arquivo no dnf durante a transacao.
# %posttrans roda depois de toda a transacao, entao nosso conteudo
# prevalece independente da ordem de instalacao dos pacotes.
cat > %{_sysconfdir}/os-release << 'EOF'
NAME="CapivaraOS"
VERSION="Marsh 1.2.4"
RELEASE_TYPE=stable
ID=capivaraos
ID_LIKE=fedora
VERSION_ID=44
VERSION_CODENAME=marsh
PLATFORM_ID="platform:f44"
PRETTY_NAME="CapivaraOS"
ANSI_COLOR="0;32"
LOGO=capivaraos-logo
CPE_NAME="cpe:/o:capivaraos:capivaraos:44"
DEFAULT_HOSTNAME=capivaraos
HOME_URL="https://capivaraos.org"
DOCUMENTATION_URL="https://capivaraos.org"
SUPPORT_URL="https://capivaraos.org"
BUG_REPORT_URL="https://capivaraos.org"
REDHAT_BUGZILLA_PRODUCT="Fedora"
REDHAT_BUGZILLA_PRODUCT_VERSION=44
REDHAT_SUPPORT_PRODUCT="Fedora"
REDHAT_SUPPORT_PRODUCT_VERSION=44
VARIANT="Marsh 1.2.4"
VARIANT_ID=marsh
EOF

cat > %{_sysconfdir}/issue << 'EOF'
CapivaraOS Marsh 1.2.4 \n \l

EOF

cat > %{_sysconfdir}/issue.net << 'EOF'
CapivaraOS Marsh 1.2.4
EOF

install -d %{_sysconfdir}/xdg
cat > %{_sysconfdir}/xdg/kcm-about-distrorc << 'EOF'
[General]
LogoPath=capivaraos-full-logo
Variant=Marsh 1.2.4
Website=https://capivaraos.org
UseOSReleaseVersion=true
EOF

# ── Reaplica os-release apos qualquer atualizacao futura do sistema ────────
# Nao declaramos /etc/os-release em %files (evita conflito na transacao da
# ISO), so sobrescrevemos o conteudo. Logo o arquivo continua pertencendo ao
# Fedora no rpmdb, e um "dnf update" que toque o pacote dono reescreve tudo de
# volta para o padrao do Fedora. Se isso acontecer na MESMA transacao em que
# um kernel novo e instalado, o titulo GRUB/BLS desse kernel (que o
# kernel-install gera a partir de NAME/VERSION do os-release) fica gravado
# como "Fedora Linux ... 44 (Forty Four)" -- e fica preso assim para sempre,
# mesmo depois do os-release ser corrigido.
#
# Geografia dos arquivos no Fedora 44 (os dois sao de pacotes DIFERENTES):
#
#   /etc/os-release      -> symlink para ../usr/lib/os-release,
#                           pertence a fedora-release-common
#   /usr/lib/os-release  -> arquivo com o conteudo REAL,
#                           pertence a fedora-release-identity-basic
#
# ATENCAO -- NAO troque o prefixo abaixo por um caminho de arquivo exato
# (ex.: /usr/lib/os-release). Verificado empiricamente em container fedora:44
# (2026-07-17): o %transfiletriggerin casa APENAS com prefixos de DIRETORIO e
# NUNCA com caminhos de arquivo exatos -- um trigger "-- /usr/lib/os-release"
# jamais dispara. (Ja o %filetriggerin casa com caminho exato, mas roda logo
# apos cada pacote, e nao no fim da transacao, o que reintroduz a corrida com
# o kernel-install.) Foi essa a armadilha da 1.1.2, cujo trigger
# "-- /etc/os-release" era codigo morto: nunca disparou uma unica vez.
#
# Por isso vigiamos o diretorio /usr/lib (dirname do arquivo que importa).
# Esse prefixo dispara em quase toda transacao, entao a guarda logo abaixo
# faz o caso comum sair de imediato; so pagamos o kernel-install quando o
# os-release realmente foi revertido.
%transfiletriggerin -- %{_prefix}/lib
# Caso comum: nosso os-release intacto, nada a fazer.
grep -q '^NAME="CapivaraOS"' %{_prefix}/lib/os-release 2>/dev/null && exit 0
cat > %{_sysconfdir}/os-release << 'EOF'
NAME="CapivaraOS"
VERSION="Marsh 1.2.4"
RELEASE_TYPE=stable
ID=capivaraos
ID_LIKE=fedora
VERSION_ID=44
VERSION_CODENAME=marsh
PLATFORM_ID="platform:f44"
PRETTY_NAME="CapivaraOS"
ANSI_COLOR="0;32"
LOGO=capivaraos-logo
CPE_NAME="cpe:/o:capivaraos:capivaraos:44"
DEFAULT_HOSTNAME=capivaraos
HOME_URL="https://capivaraos.org"
DOCUMENTATION_URL="https://capivaraos.org"
SUPPORT_URL="https://capivaraos.org"
BUG_REPORT_URL="https://capivaraos.org"
REDHAT_BUGZILLA_PRODUCT="Fedora"
REDHAT_BUGZILLA_PRODUCT_VERSION=44
REDHAT_SUPPORT_PRODUCT="Fedora"
REDHAT_SUPPORT_PRODUCT_VERSION=44
VARIANT="Marsh 1.2.4"
VARIANT_ID=marsh
EOF

cat > %{_sysconfdir}/issue << 'EOF'
CapivaraOS Marsh 1.2.4 \n \l

EOF

cat > %{_sysconfdir}/issue.net << 'EOF'
CapivaraOS Marsh 1.2.4
EOF

for kver in $(ls /lib/modules 2>/dev/null); do
    [ -f "/lib/modules/${kver}/vmlinuz" ] && \
        kernel-install add "${kver}" "/lib/modules/${kver}/vmlinuz" >/dev/null 2>&1 || true
done

%files
%license backgrounds/CREDITOS.txt
%{_datadir}/backgrounds/capivaraos/
%{_datadir}/pixmaps/capivaraos.png
%{_datadir}/pixmaps/capivaraos-logo.png
%{_datadir}/pixmaps/capivaraos-white.png
%{_datadir}/icons/hicolor/*/apps/capivaraos-logo.png
%{_datadir}/icons/hicolor/*/apps/capivaraos-full-logo.png
%{_datadir}/icons/hicolor/*/apps/capivaraos-head.png
%{_datadir}/wallpapers/capivaraos-*/
%{_datadir}/plymouth/themes/capivaraos/
%{_datadir}/capivaraos/
%{_bindir}/capivaraos-set-layout
%{_bindir}/capivaraos-set-wallpaper
%{_sysconfdir}/xdg/autostart/capivaraos-wallpaper.desktop
%{_sysconfdir}/xdg/autostart/capivaraos-layout.desktop
%{_sysconfdir}/skel/.config/plasma-org.kde.plasma.desktop-appletsrc
%{_sysconfdir}/skel/.config/kscreenlockerrc
%{_sysconfdir}/skel/.config/kdeglobals
%{_sysconfdir}/skel/.config/plasmarc
%{_sysconfdir}/skel/.config/plasma-welcomerc
%{_sysconfdir}/skel/.face
%{_sysconfdir}/skel/.face.icon
%{_sysconfdir}/anaconda/profile.d/capivaraos.conf

%changelog
* Tue Aug 18 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 1.2.4-1
- Instala em UEFI real: adiciona /etc/anaconda/profile.d/capivaraos.conf com
  base_profile=fedora. Sem ele o Anaconda nao casava perfil (ID=capivaraos),
  caia em efi_dir=default e o gen_grub_cfgstub falhava no fim da instalacao em
  UEFI ("gen_grub_cfgstub script failed") -- BUG-38. So aparecia em UEFI real;
  VM em modo BIOS/legacy nao pegava. Herdar fedora reusa efi_dir=fedora.
- (kickstart) initramfs de build agora --no-hostonly --no-hostonly-cmdline: o
  sistema instalado passa a achar o disco raiz em hardware com storage diferente
  do build (BUG-40), em vez de cair em emergency mode ("Not all disks have been
  found").

* Fri Aug 14 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 1.2.3-2
- Reconciliacao de licenca/marca (LEG-4): corrige o metadado License: do RPM.
  Antes "CC-BY-SA-4.0 AND MIT" -- (a) marcava MIT sem nada MIT no pacote (codigo
  e config do projeto sao GPLv3, como o LICENSE de topo), (b) varria a identidade
  visual sob CC-BY-SA (contradiz a marca) e (c) omitia CC-BY-SA-3.0 de uma das
  fotos embarcadas. Agora: GPL-3.0-or-later AND LicenseRef-CapivaraOS-Trademark
  AND CC-BY-SA-3.0 AND CC-BY-SA-4.0. Correcao de metadado apenas; a atribuicao
  exigida (CREDITOS.txt + creditos gravados nas imagens) ja estava correta (LEG-3).
- Adiciona TRADEMARK.md: nome/logo CapivaraOS sao marca do projeto (direitos
  reservados); codigo GPLv3; wallpapers fotograficos de terceiros CC BY-SA
  creditados em backgrounds/CREDITOS.txt.

* Wed Aug 12 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 1.2.3-1
- Corrige a atribuicao das fotos de Giles Laurent nos wallpapers: a
  licenca CC BY-SA 4.0 do autor exige o texto verbatim "(c) Giles
  Laurent, gileslaurent.com, License CC BY-SA 4.0"; o credito gravado
  antes ("Foto: Giles Laurent - CC BY-SA 4.0") omitia o dominio
  gileslaurent.com exigido. Ajustadas as 3 fotos (ipe, natacao, salto)
  e o CREDITOS.txt. Ver LEG-3.

* Tue Jul 21 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 1.2.2-1
- Zona segura nos wallpapers de foto: a logo e o credito de autoria sairam de
  40px/24px das laterais para 250px. Numa tela 4:3 exibindo um wallpaper 16:9
  com preenchimento por zoom ("Escalado e Cortado", padrao do Plasma), o corte
  e de 240px de CADA lado -- logo e credito caiam inteiros na faixa cortada.
  Diagnosticado na spin Pup em VM 4:3, onde o credito aparecia truncado como
  "...ann - CC BY-SA 4.0"; a Marsh tinha exatamente a mesma geometria, entao a
  1.2.1 publicada perde a atribuicao nesses monitores. As fotos sao CC BY-SA e
  a licenca EXIGE atribuicao -- e um problema de licenciamento, nao de layout.
  O deslocamento vertical (+120/+130) nao mudou: existe para manter logo e
  credito acima do dock.
- A arte-mestre backgrounds/CapivaraOS_Logo.png deixa de ser instalada como
  papel de parede: o %install usava glob "*.png" e a levava junto, entao ela
  aparecia no seletor de fundo do Plasma como opcao escolhivel. Diagnosticado
  na spin Pup; as tres tinham o mesmo defeito.
- Sufixo ".marsh" no Release, pelo mesmo motivo do build-rpm.sh (BUG-30):
  torna impossivel uma spin consumir o RPM de outra.

* Sun Jul 19 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 1.2.1-1
- Nova identidade visual: logo do CapivaraOS trocada (capivara "andando" no
  lugar da sentada) em todos os wallpapers (cor solida + foto), icones,
  logo do "Sobre o Sistema", splash do Plymouth e tela de login SDDM.
- Motivo: a logo anterior tinha semelhanca com um desenho de banco de
  imagens (Vecteezy); a nova e original.
- Wallpapers de cor solida agora sao reproduziveis via
  branding/regen-solid-wallpapers.sh (novo); os de foto continuam via
  branding/regen-photo-wallpapers.sh.
- icons/capivaraos-logo.png passa a ser apenas a capivara (sem o texto
  "CapivaraOS"), como o build sempre pressupos: evita o nome duplicado/
  sobreposto no lancador "Instalar CapivaraOS".
- Wallpapers de foto: marca d'agua e credito subiram (45->120 e 104->130 px
  a partir da base) para nao ficarem atras do dock inferior.
- LOGO= do /etc/os-release passa a apontar para "capivaraos-logo" (sem
  texto). O plasma-welcome desenha esse logo em marca d'agua atras do botao
  "Instalar CapivaraOS" (Live.qml, opacity 0.1), e com o logo completo o
  nome aparecia duplicado por tras do botao. O KCM "Sobre este Sistema"
  nao muda: ele usa LogoPath= do kcm-about-distrorc (capivaraos-full-logo).
- Novo conjunto de icones "capivaraos-head" (so a cabeca da capivara, em
  silhueta branca) e o lancador de aplicativos do dock passa a usa-lo no
  lugar do logo do KDE.

* Fri Jul 17 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 1.1.3-1
- Corrige titulo "Fedora Linux" no GRUB apos o primeiro update: o file
  trigger de 1.1.2 vigiava so /etc/os-release (symlink, do
  fedora-release-common) e nunca disparava quando o
  fedora-release-identity-basic -- dono do /usr/lib/os-release, que guarda o
  conteudo real -- era atualizado sozinho. Agora vigia os dois caminhos.
- Corrige ISO saindo com o Fedora 44 GA (~1068 pacotes / 7,4 GiB de update no
  primeiro boot): o anaconda nao expande $releasever nas linhas "repo" do
  kickstart, e o mirrorlist responde 200 + "invalid repo or arch" sem nenhum
  mirror, deixando o repo "updates" vazio silenciosamente. Ver
  kickstart/upstream/fedora-repo.ks.

* Thu Jun 18 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 1.1.2-1
- Corrige plasma-welcome aparecendo no primeiro login (chave LastSeenVersion)
- Corrige tema Plymouth sem logo/animacao (plymouth-plugin-script ausente)
- Corrige dock inferior duplicado por alguns segundos apos login
- Adiciona tela do Plymouth para atualizacoes offline com percentual
- Corrige titulo GRUB/BLS revertendo para "Fedora Linux" apos updates do
  sistema (file trigger em /etc/os-release)

* Sun Jun 14 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 1.1.0-1
- Versao inicial para Fedora 44 (portado do CapivaraOS Marsh / Debian trixie)
