# CapivaraOS Marsh — Fedora 44 (KDE Plasma)

Recriação do **CapivaraOS Marsh** (originalmente um remix Debian 13/trixie +
live-build + Calamares) como uma live ISO **Fedora 44 KDE Plasma**, usando as
ferramentas oficiais do projeto Fedora: `kickstart` + `livemedia-creator`
(lorax) para a imagem, e **Anaconda** como instalador.

A versão Debian original fica intacta em `../capivaraos-marsh/` e serve de
referência de identidade visual (wallpapers, ícones, lista de pacotes, tema
"macOS"/WhiteSur).

## Estrutura do projeto

```
capivaraos-marsh-fedora/
├── PACKAGES.md                  # Mapeamento de pacotes Debian -> Fedora
├── README.md                    # Este arquivo
├── branding/                    # Assets de identidade visual (fonte para o RPM)
│   ├── backgrounds/              # Wallpapers + CREDITOS.txt (CC BY-SA)
│   ├── icons/                    # Logos do CapivaraOS
│   └── skel/.config/             # Configs do Plasma de referência (Debian)
├── kickstart/
│   ├── capivaraos-marsh.ks       # Kickstart principal (ponto de entrada)
│   ├── capivaraos-post-branding.ks  # %post: idioma/atalho de instalação
│   ├── capivaraos-post-theme.ks     # %post: tema WhiteSur ("macOS")
│   └── upstream/                 # Kickstarts vendorizados do Fedora KDE Live
│       ├── fedora-repo.ks
│       ├── fedora-live-base.ks
│       ├── fedora-kde-common.ks
│       └── fedora-live-kde-base.ks
└── rpm/
    ├── capivaraos-branding.spec  # Pacote RPM com toda a identidade visual
    └── build-rpm.sh               # Script auxiliar para gerar o RPM
```

## Visão geral da identidade visual

Quase todo o branding estático (wallpapers, ícones "Sobre o Sistema", tema de
boot Plymouth, fundo da tela de login SDDM, `/etc/os-release`, `/etc/issue`,
avatar padrão, configuração inicial do Plasma — cores, wallpaper, painéis) é
empacotado num único RPM, **`capivaraos-branding`**, que substitui o
`fedora-release-kde-desktop`/`fedora-logos` padrão do Fedora (ver
`rpm/capivaraos-branding.spec`).

O tema "macOS" (WhiteSur GTK/KDE + layout de painéis estilo macOS) é aplicado
em tempo de build pelo kickstart, em `kickstart/capivaraos-post-theme.ks`,
pois depende de clonar e instalar os temas WhiteSur do GitHub.

Ver `PACKAGES.md` para o mapeamento completo de pacotes Debian -> Fedora e as
decisões/limitações conhecidas (sem RPM Fusion, sem `appmenu-gtk3-module`,
Firefox em vez de Firefox ESR, etc.).

## Pré-requisitos (máquina de build, Fedora 44 x86_64)

```bash
sudo dnf install -y lorax rpm-build ImageMagick git createrepo_c
```

- `lorax` fornece o `livemedia-creator`.
- `rpm-build` + `ImageMagick` são necessários para gerar o RPM
  `capivaraos-branding` (a spec usa `convert` para gerar os ícones/wallpapers
  em vários tamanhos).
- `git` e `createrepo_c` são usados nos passos abaixo.
- O build precisa de acesso à rede: para baixar pacotes do Fedora e, durante
  o `%post` de `capivaraos-post-theme.ks`, para clonar os temas WhiteSur do
  GitHub.
- `livemedia-creator --no-virt` precisa rodar como root (usa
  `dnf --installroot` e monta `/dev`, `/proc` etc. no diretório de instalação).

## Passo 1 — Construir o RPM `capivaraos-branding`

```bash
cd rpm
./build-rpm.sh
```

Isso gera `~/rpmbuild/RPMS/noarch/capivaraos-branding-1.1.0-1.*.noarch.rpm`.

> O script já foi validado executando a lógica de `%build`/`%install` da spec
> diretamente (sem `rpmbuild`, que ainda não estava instalado nesta máquina) —
> a geração de ícones, wallpapers, pacotes de wallpaper do KDE, tema Plymouth
> etc. roda sem erros (apenas avisos cosméticos do ImageMagick IMv7 sobre o
> comando `convert` estar deprecado em favor de `magick`).

## Passo 2 — Disponibilizar o RPM como repositório local

O `livemedia-creator` instala pacotes via `dnf`/dnf a partir dos repositórios
listados no kickstart (`upstream/fedora-repo.ks`). Para que `dnf` encontre
`capivaraos-branding`, crie um repositório local apontando para o diretório
com o RPM gerado:

```bash
mkdir -p /var/tmp/capivaraos-repo
cp ~/rpmbuild/RPMS/noarch/capivaraos-branding-*.rpm /var/tmp/capivaraos-repo/
createrepo_c /var/tmp/capivaraos-repo
```

Em seguida, adicione esta linha ao topo de
`kickstart/capivaraos-marsh.ks` (após o `%include upstream/fedora-live-kde-base.ks`,
junto com as demais diretivas de configuração), ajustando o caminho se
necessário:

```
repo --name=capivaraos-local --baseurl=file:///var/tmp/capivaraos-repo
```

> Esta linha não está incluída no kickstart por padrão porque o caminho do
> repositório local é específico de cada máquina de build. Lembre-se de
> remover/ajustar essa linha se mover o repositório local.

## Passo 3 — Gerar a ISO com `livemedia-creator`

O anaconda (rodando via `--no-virt`) resolve `%include caminho.ks` em relação
ao seu próprio diretório de trabalho, não ao diretório deste projeto. Por
isso, primeiro "achatamos" o kickstart num único arquivo sem `%include` com
`ks-flatten.py` (usa o `pykickstart` já presente como dependência do
anaconda/lorax):

```bash
cd kickstart
python3 ks-flatten.py capivaraos-marsh.ks > /var/tmp/capivaraos-marsh-flat.ks

sudo livemedia-creator --ks=/var/tmp/capivaraos-marsh-flat.ks \
    --no-virt --resultdir=/var/tmp/capivaraos-marsh-result \
    --project="CapivaraOS Marsh" --make-iso --iso-only \
    --iso-name=CapivaraOS-Marsh-1.1.0-x86_64.iso \
    --volid="CapivaraOS Marsh 1.1.0" --variant="CapivaraOS Marsh" \
    --releasever=44
```

A ISO final fica em `/var/tmp/capivaraos-marsh-result/CapivaraOS-Marsh-1.1.0-x86_64.iso`.

Logs úteis em caso de problema:
- `/var/tmp/capivaraos-marsh-result/*.log` (logs do `livemedia-creator`/lorax)
- `/var/log/capivaraos-post-theme.log` **dentro da imagem** (log do `%post`
  de `capivaraos-post-theme.ks`, útil para depurar a instalação do WhiteSur)

## Testando a ISO

```bash
qemu-system-x86_64 -m 4096 -enable-kvm \
    -cdrom /var/tmp/capivaraos-marsh-result/CapivaraOS-Marsh-1.1.0-x86_64.iso
```

## Limitações conhecidas

- **RPM Fusion não está habilitado** (consistente com a postura do CapivaraOS
  Marsh original em relação a software não-livre): o VLC incluso roda com
  suporte de codecs reduzido em relação ao build Debian (que também não
  habilitava `contrib`/`non-free` por padrão, mas o pacote `vlc` do Debian já
  vem com mais codecs via `libavcodec` do `main`).
- **`appmenu-gtk3-module` não existe no Fedora**: o menu global de aplicações
  (painel superior estilo macOS) funciona para apps Qt/KDE, mas aplicativos
  GTK não mostrarão seus menus na barra superior.
- **Tema WhiteSur depende de rede durante o build** (`git clone` do GitHub em
  `capivaraos-post-theme.ks`). Se a rede não estiver disponível, o `%post`
  registra avisos no log e o sistema final usa o tema Breeze Dark padrão (já
  configurado pelo pacote `capivaraos-branding`), sem abortar o build.

## Próximos passos

Após revisão deste conjunto de arquivos (kickstart + RPM de branding), o
mesmo processo será aplicado à variante **CapivaraOS** (não-Marsh, em
`../capivaraos/`).
