#!/bin/bash
# Empacota os assets de branding/ num tarball e constroi o RPM
# capivaraos-branding com rpmbuild.
#
# Uso:
#   dnf install -y rpm-build ImageMagick
#   ./build-rpm.sh
#
# O RPM resultante fica em ~/rpmbuild/RPMS/noarch/capivaraos-branding-*.rpm

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
VERSION="1.1.3"
NAME="capivaraos-branding"
WORKDIR="$(mktemp -d)"
SRCDIR="${WORKDIR}/${NAME}-${VERSION}"

mkdir -p "$SRCDIR"
cp -r "${PROJECT_DIR}/branding/backgrounds" "$SRCDIR/"
cp -r "${PROJECT_DIR}/branding/icons" "$SRCDIR/"

mkdir -p "$HOME/rpmbuild/SOURCES" "$HOME/rpmbuild/SPECS"
tar -C "$WORKDIR" -czf "$HOME/rpmbuild/SOURCES/${NAME}-${VERSION}.tar.gz" "${NAME}-${VERSION}"
cp "${SCRIPT_DIR}/capivaraos-branding.spec" "$HOME/rpmbuild/SPECS/"

rm -rf "$WORKDIR"

rpmbuild -bb "$HOME/rpmbuild/SPECS/capivaraos-branding.spec"

echo
echo "RPM gerado em: $HOME/rpmbuild/RPMS/noarch/"
ls -1 "$HOME/rpmbuild/RPMS/noarch/" | grep "^${NAME}"
