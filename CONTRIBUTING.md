# Contribuindo com o CapivaraOS Marsh

Obrigado pelo interesse em contribuir! Este repositório contém o kickstart,
os scripts de build e o pacote RPM de branding usados para gerar a ISO do
**CapivaraOS Marsh** (Fedora 44 + KDE Plasma).

## Antes de abrir uma issue

- **Problemas ao usar o CapivaraOS instalado** (algo não funciona no
  sistema, no visual, num aplicativo): abra uma
  [issue](../../issues/new/choose) com o template de relato de bug. Você
  **não precisa** saber construir a ISO para reportar — no campo de
  ambiente, informe apenas a versão da ISO que instalou (veja em
  *Configurações do Sistema → Sobre este Sistema*) e o modelo da máquina.
- **Bugs e problemas de build** (você está gerando a própria ISO): mesmo
  template, mas inclua a versão do Fedora da máquina de build, o comando
  exato executado e os logs relevantes (veja "Logs úteis" no `README.md`).
- **Sugestões de pacote, tema ou funcionalidade**: abra uma issue com o
  template de solicitação de funcionalidade.
- **Dúvidas gerais, "como faço para...", ideias em aberto**: use as
  [Discussions](../../discussions) em vez de issues — issues ficam
  reservadas para itens de trabalho rastreáveis.
- **Vulnerabilidades de segurança**: não abra uma issue pública — siga o
  processo descrito em [`SECURITY.md`](SECURITY.md).

## O que acontece depois que você abre uma issue

Queremos que ninguém fique no escuro esperando resposta, então o processo é
este:

1. **Registro automático.** Assim que a issue é aberta, ela é espelhada no
   nosso rastreador interno e você recebe um comentário de confirmação. Isso
   é automático e não significa que alguém já leu o conteúdo.
2. **Triagem.** Um mantenedor lê a issue e decide se ela é aceita, precisa
   de mais informação, ou está fora de escopo. É aqui que perguntamos
   detalhes que faltaram — sem eles, muita coisa não é reproduzível.
3. **Priorização.** Issues aceitas entram na fila. Nem tudo que é aceito é
   feito logo: corrigir algo que quebra o sistema para muita gente passa na
   frente de um ajuste visual.
4. **Resolução.** Quando a correção sai, a issue é fechada com uma
   referência à mudança e à versão em que ela chega.

Sobre expectativas, sendo honestos: o CapivaraOS é mantido por uma equipe
muito pequena. Não prometemos prazo de resposta. Uma issue pode ficar aberta
um bom tempo sem que isso signifique rejeição — e uma issue bem escrita, com
passos de reprodução claros, sempre anda mais rápido que um relato vago.

**O que ajuda a sua issue a andar:**

- Passos que reproduzem o problema numa instalação limpa.
- O que você esperava que acontecesse e o que aconteceu.
- Se o problema aparece logo após instalar ou só depois de atualizar.
- Fotos da tela quando o problema é visual ou acontece no boot.

**O que atrasa:** relatos como "não funciona", várias reclamações diferentes
empilhadas numa issue só, ou pedidos de suporte que caberiam melhor nas
Discussions.

## Como contribuir com código

1. Dê um fork no repositório e crie uma branch a partir de `main`.
2. Siga a estrutura já documentada no `README.md` (kickstart, branding,
   rpm) — mudanças em branding (wallpapers, ícones, temas) entram em
   `branding/` e são empacotadas via `rpm/capivaraos-branding.spec`.
3. Teste sua mudança localmente sempre que possível:
   - Para mudanças no RPM de branding: rode `rpm/build-rpm.sh` e confirme
     que o pacote é gerado sem erros.
   - Para mudanças no kickstart: gere a ISO com `livemedia-creator` (veja
     o `README.md`) e valide em uma VM (`qemu-system-x86_64`).
4. Abra um Pull Request descrevendo a mudança e como foi testada. Use o
   template de PR como guia.
5. Um mantenedor vai revisar e pode pedir ajustes antes do merge.

## Fluxo de trabalho — branch + PR (regra do projeto)

Para **qualidade, rastreabilidade e auditoria**, todo o trabalho — **inclusive dos
mantenedores** — segue o mesmo fluxo. Não se faz `push` direto no branch padrão.

1. **Crie um branch** a partir do branch padrão, com nome descritivo
   (`feat/…`, `fix/…`, `chore/…`, `docs/…`).
2. **Commits pequenos e coesos**, explicando _o quê_ e _porquê_; referencie o
   ticket do Jira quando houver.
3. **Abra um Pull Request.** Deixe o CI verde (quando houver) antes de mesclar.
4. **O branch padrão fica sempre coerente e "releasável".** Um _release_ é uma
   **tag** + a **imagem (ISO) publicada** (SourceForge/site) — nunca "o que
   estiver no branch padrão".
5. **Segurança:** nunca commitar segredos/chaves; o histórico é varrido
   (gitleaks) e a push protection está ativa.

> O branch padrão é protegido: PRs são o único caminho de entrada — vale também
> para os mantenedores. É o que sustenta a auditabilidade do projeto.

## Licença

Ao contribuir, você concorda que sua contribuição será licenciada sob a
[GPLv3](LICENSE), a mesma licença do projeto.

Este projeto segue o [Código de Conduta](CODE_OF_CONDUCT.md) do
CapivaraOS.
