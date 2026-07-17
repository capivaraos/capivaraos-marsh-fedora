# =============================================================================
# DIAGNÓSTICO TEMPORÁRIO — por que o repo 'updates' não contribui (BUG-29)
# =============================================================================
#
# REMOVER este %include de capivaraos-marsh.ks assim que o problema do repo
# 'updates' estiver resolvido. Não deve ir para uma ISO de lançamento.
#
# O que faz: durante o build, o anaconda registra a atividade do seu dnf em
# /tmp/packaging.log e /tmp/dnf.librepo.log (quais repos adicionou, se baixou
# metadados, se pulou algum). O livemedia-creator apaga esse /tmp ao final,
# então preservamos os logs em dois lugares:
#   1) dentro da própria imagem, em /var/log/capivaraos-compose/ (sobrevive na
#      ISO — sempre funciona, basta montar a ISO para ler);
#   2) num diretório no host, /var/tmp/capivaraos-compose-logs/ (conveniência,
#      pode não funcionar dependendo do namespace; por isso o item 1).
# Também imprime um resumo no stdout do %post (vai para o log do build).

%post --nochroot
_IMG_DIR="${ANA_INSTALL_PATH}/var/log/capivaraos-compose"
_HOST_DIR="/var/tmp/capivaraos-compose-logs"
mkdir -p "$_IMG_DIR" 2>/dev/null || true
mkdir -p "$_HOST_DIR" 2>/dev/null || true

for _l in packaging dnf.librepo dnf.rpm anaconda storage program; do
    cp -f "/tmp/${_l}.log" "$_IMG_DIR/"  2>/dev/null || true
    cp -f "/tmp/${_l}.log" "$_HOST_DIR/" 2>/dev/null || true
done

echo "===== CAPIVARA-DIAG: repos/updates vistos pelo dnf do anaconda ====="
grep -hiE "repo|mirror|updates|added|enabled|skip|unavailable|kernel-core|metadata" \
    /tmp/packaging.log /tmp/dnf.librepo.log 2>/dev/null | tail -120 || true
echo "===== CAPIVARA-DIAG: fim ====="
%end
