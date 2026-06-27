#!/bin/bash
# Build completo do CapivaraOS Marsh (Fedora 44 KDE): instala dependências,
# gera o RPM capivaraos-branding, monta um repositório local com ele e
# constrói a ISO live com livemedia-creator.
#
# Requer privilégios de root (dnf install + livemedia-creator --no-virt) e
# acesso à rede (pacotes do Fedora + git clone dos temas WhiteSur durante o
# %post). Recomenda-se rodar num terminal interativo (a senha do sudo será
# solicitada e o build pode levar bastante tempo).
#
# Uso:
#   ./build-all.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR=/var/tmp/capivaraos-repo
RESULT_DIR=/var/tmp/capivaraos-marsh-result
ISO_NAME=CapivaraOS-Marsh-1.1.2-x86_64.iso

echo "==> 1/4: Instalando dependências (lorax, rpm-build, ImageMagick, git, createrepo_c)..."
sudo dnf install -y lorax rpm-build ImageMagick git createrepo_c

echo "==> 2/4: Construindo RPM capivaraos-branding..."
"$SCRIPT_DIR/rpm/build-rpm.sh"

echo "==> 3/4: Criando repositório local em ${REPO_DIR}..."
# BUG CORRIGIDO (2026-06-25): ~/rpmbuild/RPMS/noarch/ acumula RPMs
# "capivaraos-branding" de TODAS as spins buildadas na mesma máquina (Marsh,
# Pup, Snout). Copiar com glob "capivaraos-branding-*.rpm" SEM filtro de
# versão (como antes) pegaria TODOS eles, e um "dnf update"/instalação
# poderia escolher o de outra spin (Release mais alto "ganha" na
# comparação de NEVRA, mesmo entre pacotes de spins diferentes — já
# aconteceu de fato com Pup vs. Snout, que compartilham Version=1.0.0).
# Agora resolvemos a NEVRA EXATA deste spec (Version E Release) via
# "rpmspec -q", garantindo que copiamos só o RPM desta spin.
NEVRA=$(rpmspec -q --qf '%{name}-%{version}-%{release}.%{arch}\n' "$SCRIPT_DIR/rpm/capivaraos-branding.spec" | head -1)
RPM_FILE="$HOME/rpmbuild/RPMS/noarch/${NEVRA}.rpm"
[ -f "$RPM_FILE" ] || { echo "ERRO: RPM esperado não encontrado: ${RPM_FILE}" >&2; exit 1; }
mkdir -p "$REPO_DIR"
cp -v "$RPM_FILE" "$REPO_DIR/"
createrepo_c "$REPO_DIR"

echo "==> 4/4: Gerando ISO com livemedia-creator (pode levar bastante tempo)..."
sudo rm -rf "$RESULT_DIR"

# O anaconda (rodando via --no-virt/unshare) resolve "%include caminho.ks"
# em relação ao seu próprio cwd, que não é o diretório deste projeto — por
# isso "achatamos" o kickstart num único arquivo sem %include antes de
# chamar o livemedia-creator. Ver kickstart/ks-flatten.py.
FLAT_KS=/var/tmp/capivaraos-marsh-flat.ks
sudo rm -f "$FLAT_KS"
( cd "$SCRIPT_DIR/kickstart" && python3 ks-flatten.py capivaraos-marsh.ks > "$FLAT_KS" )

sudo livemedia-creator --ks="$FLAT_KS" \
    --no-virt --resultdir="$RESULT_DIR" \
    --project="CapivaraOS Marsh" --make-iso --iso-only \
    --iso-name="$ISO_NAME" \
    --volid="CapivaraOS Marsh 1.1.2" --variant="CapivaraOS Marsh" \
    --releasever=44

echo
echo "==> Concluído! ISO em: ${RESULT_DIR}/${ISO_NAME}"
