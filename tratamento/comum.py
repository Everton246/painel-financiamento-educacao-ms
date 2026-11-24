"""Caminhos e utilidades do tratamento (montagem da base única em formato longo)."""
import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
BRUTOS = RAIZ / "dados_brutos"
BASE = RAIZ / "dados" / "base"
CACHE = RAIZ / "dados" / "cache"
DADOS = RAIZ / "dados"
DOCS = RAIZ / "docs"
FONTE_AB = RAIZ.parent / "04_dados_ICMS_IQE_VAAR"          # objetivos a e b: só leitura
PROC_AB = FONTE_AB / "dados_processados"
IQUEMS = RAIZ.parent.parent / "02_iquems" / "02_painel_educacao_ms"  # só leitura

COLUNAS = ["cod_ibge", "municipio", "ano", "indicador", "valor", "unidade", "fonte", "arquivo", "pagina", "observacao"]


def ler_ab(nome):
    """CSV de 04_dados_ICMS_IQE_VAAR/dados_processados (código IBGE como texto)."""
    return pd.read_csv(PROC_AB / nome, dtype={"cod_ibge": str}, encoding="utf-8-sig")


def municipios():
    return ler_ab("01_municipios_ms.csv")


def longo(df, ano_col, mapa, fonte, arquivo, pagina="", obs="", ano_fixo=None):
    """Transforma colunas de `df` em linhas (cod_ibge, ano, indicador, valor...).
    mapa = {coluna_no_df: (codigo_indicador, unidade)}. `fonte`, `arquivo`, `pagina`, `obs`: texto ou nome de coluna."""
    partes = []
    for col, (ind, unid) in mapa.items():
        if col not in df:
            raise KeyError(f"coluna {col} ausente em {arquivo}")
        p = pd.DataFrame({"cod_ibge": df["cod_ibge"].astype(str),
                          "ano": ano_fixo if ano_fixo is not None else df[ano_col],
                          "indicador": ind, "valor": pd.to_numeric(df[col], errors="coerce"), "unidade": unid})
        for campo, v in (("fonte", fonte), ("arquivo", arquivo), ("pagina", pagina), ("observacao", obs)):
            p[campo] = df[v].astype(str).values if isinstance(v, str) and v in df else v
        partes.append(p)
    return pd.concat(partes, ignore_index=True)


def confere_79(df, rotulo, por=("ano",)):
    """Cada ano (ou grupo) precisa ter os 79 municípios, sem sobras nem faltas."""
    cods = set(municipios()["cod_ibge"])
    erros = []
    for chave, g in df.groupby(list(por)) if por else [("todos", df)]:
        s = set(g["cod_ibge"])
        if s != cods:
            erros.append(f"{rotulo} {chave}: faltam {sorted(cods - s)[:5]} sobram {sorted(s - cods)[:5]}")
    return erros


def aviso(msg):
    print(msg, flush=True)


def sai(ok):
    sys.exit(0 if ok else 1)
