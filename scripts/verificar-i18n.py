# -*- coding: utf-8 -*-
"""Confere se toda chave data-i18n usada no mockup existe nos 5 dicionarios.

Erro silencioso que este script pega: um data-i18n com chave errada nao
quebra nada visivelmente - o texto em portugues fica no HTML como fallback
e a tela parece so "nao traduzida" naquele pedaco.

Uso: python scripts/verificar-i18n.py
Saida 0 = tudo casa; 1 = ha chave faltando ou dicionario fora de sincronia.
"""
import io
import json
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOCKUP = os.path.join(RAIZ, 'mockup')
DIC = os.path.join(MOCKUP, 'assets', 'i18n')

# data-i18n="k", data-i18n-html="k" e data-i18n-attr="attr:k;attr2:k2"
PADRAO_SIMPLES = re.compile(r'data-i18n(?:-html)?="([^"]+)"')
PADRAO_ATTR = re.compile(r'data-i18n-attr="([^"]+)"')


def chaves_do_html(caminho):
    with io.open(caminho, encoding='utf-8') as f:
        texto = f.read()
    chaves = set(PADRAO_SIMPLES.findall(texto))
    for spec in PADRAO_ATTR.findall(texto):
        for par in spec.split(';'):
            partes = par.split(':')
            if len(partes) == 2:
                chaves.add(partes[1])
    return chaves


# Chave citada como string literal no JS - `app.js` e o script inline do
# login trocam `data-i18n` em tempo de execucao (contador de materiais,
# rotulo de ordenacao, "Entrando como aluno", "Ocultar senha"). Sem ler
# o JS, o aviso de "chave sem uso" acusaria essas como orfas, e um aviso
# que da falso positivo e um aviso que ninguem le.
PADRAO_JS = re.compile(r"['\"]([a-z][a-zA-Z0-9]*\.[a-zA-Z0-9]+)['\"]")


def chaves_do_js(caminho, validas):
    with io.open(caminho, encoding='utf-8') as f:
        texto = f.read()
    return {c for c in PADRAO_JS.findall(texto) if c in validas}


def main():
    dicionarios = {}
    for nome in sorted(os.listdir(DIC)):
        if nome.endswith('.json'):
            with io.open(os.path.join(DIC, nome), encoding='utf-8') as f:
                dicionarios[nome[:-5]] = json.load(f)

    problemas = []

    # 1) todos os dicionarios cobrem o mesmo conjunto de chaves
    referencia = set(dicionarios['pt-BR'])
    for codigo, dic in sorted(dicionarios.items()):
        for chave in sorted(referencia - set(dic)):
            problemas.append(u'%s.json nao tem a chave "%s"' % (codigo, chave))
        for chave in sorted(set(dic) - referencia):
            problemas.append(u'%s.json tem chave que pt-BR nao tem: "%s"' % (codigo, chave))

    # 2) toda chave usada no HTML existe
    usadas = set()
    for nome in sorted(os.listdir(MOCKUP)):
        if not nome.endswith('.html'):
            continue
        chaves = chaves_do_html(os.path.join(MOCKUP, nome))
        usadas |= chaves
        for chave in sorted(chaves - referencia):
            problemas.append(u'%s usa "%s", que nao existe no dicionario' % (nome, chave))
        usadas |= chaves_do_js(os.path.join(MOCKUP, nome), referencia)

    for nome in sorted(os.listdir(os.path.join(MOCKUP, 'assets'))):
        if nome.endswith('.js'):
            usadas |= chaves_do_js(os.path.join(MOCKUP, 'assets', nome), referencia)

    if problemas:
        for p in problemas:
            print(u'ERRO: ' + p)
        return 1

    orfas = sorted(referencia - usadas)
    print(u'ok - %d chaves em %d idiomas, todas as usadas no HTML existem'
          % (len(referencia), len(dicionarios)))
    if orfas:
        print(u'aviso - %d chaves no dicionario sem uso no HTML: %s'
              % (len(orfas), ', '.join(orfas)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
