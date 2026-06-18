#!/usr/bin/env python3
"""Achata capivaraos-marsh.ks (resolve todos os "%include") num único arquivo.

Por quê: o pykickstart resolve "%include caminho/relativo.ks" em relação ao
diretório de trabalho do processo que faz o parsing — no build via
livemedia-creator --no-virt, esse processo é o anaconda dentro do
unshare/dirinstall, cujo cwd não é o diretório deste projeto, então os
%include com caminho relativo falham ("No such file or directory").

Rodando este script com cwd=kickstart/ (mesma convenção usada nos %include
de capivaraos-marsh.ks e upstream/*.ks), o pykickstart resolve todos os
includes corretamente aqui e produz um único arquivo sem %include, que pode
ser passado ao livemedia-creator de qualquer diretório.

Uso:
    cd kickstart && python3 ks-flatten.py capivaraos-marsh.ks > /var/tmp/capivaraos-marsh-flat.ks
"""
import sys

from pykickstart.parser import KickstartParser
from pykickstart.version import DEVEL, makeVersion

handler = makeVersion(DEVEL)
parser = KickstartParser(handler)
parser.readKickstart(sys.argv[1])
print(str(handler))
