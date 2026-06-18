# Vendorizado de fedora-kickstarts: fedora-kde-common.ks
# Fonte original: https://forge.fedoraproject.org/releng/spin-kickstarts
# (histórico anterior à migração para kiwi, commit d93b2ac)
#
# NOTA CapivaraOS: fedora-release-kde traz a identidade visual padrão do
# Fedora KDE (wallpapers, plymouth, sddm theme, os-release). Removemos esse
# pacote em capivaraos-marsh.ks e fornecemos nosso próprio pacote de branding
# (capivaraos-branding), análogo ao que o hook 0020-desktop.hook.chroot fazia
# no Debian.
#
# NOTA CapivaraOS: removidas em relação ao original (causavam
# NonCriticalInstallationError no anaconda 44.30/dnf5 do Fedora 44):
#   - "@kde-spin-initial-setup": grupo não existe mais nos comps do F44.
#   - "-@admin-tools": "admin-tools" não é mais um grupo opcional do
#     ambiente kde-desktop-environment, então excluí-lo dá erro de
#     "grupo do ambiente" inexistente.
#   - bloco "### space issues" (-ktorrent -digikam -kipi-plugins -krusader
#     -k3b): no F44, nenhum desses é membro padrão/obrigatório de @kde-apps
#     (no máx. opcional, ou nem existe — caso de kipi-plugins), então dnf5
#     trata a exclusão como "argumento corresponde apenas a pacotes
#     excluídos" e reporta erro. Como não seriam instalados por padrão
#     mesmo sem a exclusão, removê-la não muda o conjunto final de pacotes.

%packages
# install env-group to resolve RhBug:1891500
@^kde-desktop-environment

@firefox
@kde-apps
@kde-media
@kde-pim
@libreoffice
# add libreoffice-draw and libreoffice-math (pagureio:fedora-kde/SIG#103)
libreoffice-draw
libreoffice-math

fedora-release-kde-desktop

# drop tracker stuff pulled in by gtk3 (pagureio:fedora-kde/SIG#124)
-tracker-miners
-tracker

# Not needed on desktops. See: https://pagure.io/fedora-kde/SIG/issue/566
-mariadb-server-utils

### The KDE-Desktop

# fedora-specific packages
plasma-welcome-fedora

### fixes

# minimal localization support - allows installing the kde-l10n-* packages
kde-l10n

# Additional packages that are not default in kde-* groups, but useful
fuse
mediawriter

%end
