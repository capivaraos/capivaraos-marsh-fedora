# Política de Segurança

## Reportando uma vulnerabilidade

Se você encontrar uma vulnerabilidade de segurança no
**CapivaraOS Marsh** (kickstart, scripts de build, pacote RPM de branding,
ou qualquer artefato gerado a partir deste repositório), por favor **não
abra uma issue pública**.

Em vez disso, reporte de forma privada através do
[formulário de contato](https://capivaraos.org/pt/contato.html) do site do
CapivaraOS, descrevendo:

- O componente afetado (ex: um kickstart específico, o RPM
  `capivaraos-branding`, um script de build);
- Passos para reproduzir o problema;
- O impacto potencial (ex: execução de código durante o build, instalação
  de pacotes não verificados, permissões incorretas no sistema final).

Não existe ainda um e-mail de segurança dedicado nem programa de
recompensas (bug bounty) — o formulário de contato é o único canal oficial
de relato neste momento.

## O que esperar

- Confirmação de recebimento em até 5 dias úteis.
- Avaliação inicial de impacto e, se aplicável, um prazo estimado de
  correção, comunicado pelo mesmo canal usado no relato.
- Pedimos que o problema não seja divulgado publicamente (issues, redes
  sociais, listas de discussão) até que uma correção esteja disponível ou
  até combinarmos um prazo de divulgação coordenada.

## Escopo

Cobre o conteúdo deste repositório: kickstarts, scripts `%post`, o pacote
RPM `capivaraos-branding` e os scripts de build (`build-rpm.sh`,
`build-all.sh`). Vulnerabilidades no Fedora em si, nas ferramentas
upstream (`livemedia-creator`, `anaconda`, `lorax`) ou em dependências de
terceiros (ex: temas WhiteSur) devem ser reportadas diretamente aos
respectivos projetos.
