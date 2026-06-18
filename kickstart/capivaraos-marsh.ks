#version=DEVEL
# =============================================================================
# CapivaraOS Marsh - Fedora 44 (KDE Plasma) - kickstart principal
# =============================================================================
#
# Baseado no kickstart oficial do Fedora KDE Live (vendorizado em
# upstream/), com a identidade visual, idioma e seleção de pacotes do
# CapivaraOS Marsh (originalmente construído sobre Debian 13/trixie com
# live-build). Ver PACKAGES.md para o mapeamento completo Debian -> Fedora.
#
# Uso (ver README.md para detalhes; ./build-all.sh automatiza tudo isto):
#   cd kickstart && python3 ks-flatten.py capivaraos-marsh.ks > /var/tmp/capivaraos-marsh-flat.ks
#   livemedia-creator --ks=/var/tmp/capivaraos-marsh-flat.ks \
#       --no-virt --resultdir=/var/tmp/capivaraos-marsh-result \
#       --project="CapivaraOS Marsh" --make-iso --iso-only \
#       --iso-name=CapivaraOS-Marsh-1.1.2-x86_64.iso \
#       --volid="CapivaraOS Marsh 1.1.2" --variant="CapivaraOS Marsh" \
#       --releasever=44
#
# NOTA: o anaconda resolve "%include caminho.ks" em relação ao seu próprio
# cwd (não ao diretório deste arquivo), por isso o ks-flatten.py acima é
# necessário — ver kickstart/ks-flatten.py.

%include upstream/fedora-live-kde-base.ks

# ── Repositório local com o RPM capivaraos-branding ─────────────────────────
# Gerado por ../build-all.sh (rpm/build-rpm.sh + createrepo_c) em
# /var/tmp/capivaraos-repo. Ajuste o caminho se mover o repositório local.
repo --name=capivaraos-local --baseurl=file:///var/tmp/capivaraos-repo

# ── IDIOMA / TECLADO / FUSO (sobrescreve os defaults en_US do fedora-live-base) ─
# Equivalente ao "locales=pt_BR.UTF-8 keyboard-layouts=br" do live-build
# Debian. glibc-all-langpacks (incluso via fedora-live-base) já traz todos os
# locales prontos, então pt_BR e en_US ficam disponíveis para troca em
# Configurações do Sistema > Idiomas sem precisar gerar locales.
lang pt_BR.UTF-8
keyboard --xlayouts='br-abnt2' --vckeymap=br-abnt2
timezone America/Sao_Paulo --utc
network --hostname=capivaraos

# =============================================================================
# PACOTES — ver PACKAGES.md para o mapeamento Debian -> Fedora
# =============================================================================
%packages

# ── Identidade visual: usamos nosso próprio pacote de branding em vez do
# branding padrão do Fedora KDE (wallpapers, plymouth, sddm, os-release,
# tema "Sobre o Sistema" do Fedora). Ver rpm/capivaraos-branding.spec.
-fedora-release-kde-desktop
capivaraos-branding

# Tema Plymouth do CapivaraOS (capivaraos.script) é um tema "script": precisa
# do plugin script.so do plymouth para ser renderizado. Sem este pacote,
# /usr/lib64/plymouth/script.so não existe e o plymouthd cai num
# renderizador genérico (spinner simples em fundo preto, sem logo/texto),
# mesmo com plymouthd.conf apontando Theme=capivaraos corretamente.
plymouth-plugin-script

# Plasma Welcome genérico (sem branding Fedora) no lugar da variante
# plasma-welcome-fedora trazida por fedora-kde-common.ks
-plasma-welcome-fedora
plasma-welcome

# Fedora Media Writer não é necessário e tem branding/conteúdo padrão do Fedora
-mediawriter

# ===== SISTEMA BASE (idioma) =====
langpacks-pt_BR
glibc-langpack-pt

# ===== OFFICE: tradução pt-BR do LibreOffice =====
libreoffice-langpack-pt-BR
libreoffice-help-pt-BR
libreoffice-kf6

# ===== INTERNET =====
thunderbird

# ===== MIDIA =====
vlc
gimp
# gwenview já incluso via @kde-media / @kde-apps

# ===== UTILITARIOS =====
gparted
htop
fastfetch
curl
wget
zip
unzip
rsync
# ark, kate, okular já inclusos via @kde-apps

# ===== DESENVOLVIMENTO =====
git
nano
vim-enhanced
@development-tools

# ===== FONTES =====
liberation-fonts
dejavu-fonts-all
google-noto-sans-fonts
google-noto-serif-fonts
google-noto-emoji-fonts

# ===== IMPRESSAO =====
cups
system-config-printer

# ===== TEMA MACOS (WHITESUR) — dependências para o post-script de tema =====
sassc
optipng
gtk-murrine-engine
gtk2-engines
ImageMagick

%end

# =============================================================================
# Post-scripts específicos do CapivaraOS
# =============================================================================
%include capivaraos-post-branding.ks
%include capivaraos-post-theme.ks
