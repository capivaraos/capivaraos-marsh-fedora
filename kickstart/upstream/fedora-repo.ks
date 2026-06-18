# Vendorizado de fedora-kickstarts (fedora-repo-not-rawhide.ks), branch de
# release (não-rawhide). Fonte original:
# https://forge.fedoraproject.org/releng/spin-kickstarts
# (histórico anterior à migração para kiwi, commit d93b2ac)

repo --name=fedora --mirrorlist=https://mirrors.fedoraproject.org/mirrorlist?repo=fedora-$releasever&arch=$basearch
repo --name=updates --mirrorlist=https://mirrors.fedoraproject.org/mirrorlist?repo=updates-released-f$releasever&arch=$basearch
#repo --name=updates-testing --mirrorlist=https://mirrors.fedoraproject.org/mirrorlist?repo=updates-testing-f$releasever&arch=$basearch
url --mirrorlist=https://mirrors.fedoraproject.org/mirrorlist?repo=fedora-$releasever&arch=$basearch
