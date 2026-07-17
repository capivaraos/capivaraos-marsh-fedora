# Vendorizado de fedora-kickstarts (fedora-repo-not-rawhide.ks), branch de
# release (não-rawhide). Fonte original:
# https://forge.fedoraproject.org/releng/spin-kickstarts
# (histórico anterior à migração para kiwi, commit d93b2ac)
#
# NOTA CapivaraOS (2026-07-17): divergimos do upstream trocando $releasever e
# $basearch por valores literais nas linhas "repo".
#
# Por quê: o anaconda expande essas variáveis na linha "url" (repo base), mas
# NÃO nas linhas "repo". O mirrorlist do Fedora responde a um $releasever
# literal com HTTP 200 + "error: invalid repo or arch" e ZERO mirrors, ou
# seja, o repo fica vazio silenciosamente — sem erro no log. Efeito: a ISO
# 1.1.2 saiu com o Fedora 44 GA (kernel 6.19.10-300), e o usuário levava
# ~1068 pacotes / 7,4 GiB de atualização no primeiro boot. O repo local
# capivaraos-local funcionava justamente por não ter variáveis.
#
# Ao mexer aqui, confira que build-all.sh usa o mesmo releasever (--releasever).

repo --name=fedora --mirrorlist=https://mirrors.fedoraproject.org/mirrorlist?repo=fedora-44&arch=x86_64
repo --name=updates --mirrorlist=https://mirrors.fedoraproject.org/mirrorlist?repo=updates-released-f44&arch=x86_64
#repo --name=updates-testing --mirrorlist=https://mirrors.fedoraproject.org/mirrorlist?repo=updates-testing-f44&arch=x86_64
url --mirrorlist=https://mirrors.fedoraproject.org/mirrorlist?repo=fedora-$releasever&arch=$basearch
