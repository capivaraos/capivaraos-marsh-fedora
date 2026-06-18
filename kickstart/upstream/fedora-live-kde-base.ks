# Vendorizado de fedora-kickstarts: fedora-live-kde-base.ks
# Fonte original: https://forge.fedoraproject.org/releng/spin-kickstarts
# (histórico anterior à migração para kiwi, commit d93b2ac)
#
# Maintained by the Fedora KDE SIG:
# http://fedoraproject.org/wiki/SIGs/KDE
# mailto:kde@lists.fedoraproject.org

# NOTA CapivaraOS: caminhos de %include são resolvidos pelo pykickstart
# relativos ao diretório de trabalho do processo anaconda (não ao diretório
# deste arquivo), por isso usamos "upstream/..." aqui — veja a observação em
# capivaraos-marsh.ks e o cd para kickstart/ em build-all.sh.
%include upstream/fedora-live-base.ks
%include upstream/fedora-kde-common.ks

%post

# set default GTK+ theme for root (see #683855, #689070, #808062)
cat > /root/.gtkrc-2.0 << EOF
include "/usr/share/themes/Adwaita/gtk-2.0/gtkrc"
include "/etc/gtk-2.0/gtkrc"
gtk-theme-name="Adwaita"
EOF
mkdir -p /root/.config/gtk-3.0
cat > /root/.config/gtk-3.0/settings.ini << EOF
[Settings]
gtk-theme-name = Adwaita
EOF

# set livesys session type
sed -i 's/^livesys_session=.*/livesys_session="kde"/' /etc/sysconfig/livesys

%end
