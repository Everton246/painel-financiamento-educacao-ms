"""Tratamento 03: infraestrutura das escolas MUNICIPAIS EM ATIVIDADE de MS, Censo Escolar 2021 a 2025 (objetivo c).

Lê os microdados que já estão baixados no painel do Iquems (02_iquems/02_painel_educacao_ms/dados_brutos/inep/censo,
só leitura; nada é baixado de novo). Filtro: CO_UF = 50, TP_DEPENDENCIA = 3 (municipal), TP_SITUACAO_FUNCIONAMENTO = 1
(em atividade). Para cada município e ano: número de escolas e % das escolas com cada item (o denominador é o número de
escolas com o item informado; item ausente no arquivo do ano = sem dado).
Saída: dados/cache/censo_infra_municipal.parquet (lida por montar_base.py).
"""
import re
import zipfile

import pandas as pd

from comum import CACHE, IQUEMS

ANOS = range(2021, 2026)
PASTA = IQUEMS / "dados_brutos" / "inep" / "censo"
# item do Censo -> (código do indicador, nome curto)
ITENS = {
    "IN_AGUA_POTAVEL": ("infra_agua_potavel", "água potável"),
    "IN_ESGOTO_REDE_PUBLICA": ("infra_esgoto_rede", "esgoto pela rede pública"),
    "IN_BIBLIOTECA_SALA_LEITURA": ("infra_biblioteca_sala_leitura", "biblioteca ou sala de leitura"),
    "IN_LABORATORIO_INFORMATICA": ("infra_lab_informatica", "laboratório de informática"),
    "IN_LABORATORIO_CIENCIAS": ("infra_lab_ciencias", "laboratório de ciências"),
    "IN_QUADRA_ESPORTES": ("infra_quadra", "quadra de esportes"),
    "IN_REFEITORIO": ("infra_refeitorio", "refeitório"),
    "IN_SALA_ATENDIMENTO_ESPECIAL": ("infra_sala_aee", "sala de atendimento educacional especializado"),
    "IN_INTERNET_ALUNOS": ("infra_internet_alunos", "internet para uso dos alunos"),
    "IN_BANDA_LARGA": ("infra_banda_larga", "banda larga"),
    "IN_EQUIP_MULTIMIDIA": ("infra_multimidia", "projetor multimídia"),
    "IN_ACESSIBILIDADE_INEXISTENTE": ("infra_sem_acessibilidade", "nenhum recurso de acessibilidade"),
}
SOMAS = {"QT_SALAS_UTILIZADAS": "salas", "QT_SALAS_UTILIZA_CLIMATIZADAS": "salas_climatizadas",
         "QT_DESKTOP_ALUNO": "desktop", "QT_COMP_PORTATIL_ALUNO": "portatil", "QT_TABLET_ALUNO": "tablet"}


def arquivo_escola(z):
    return [m for m in z.namelist() if re.search(r"(microdados_ed_basica_\d{4}|tabela_escola_\d{4}[^/]*)\.csv$", m, re.I)][0]


def ler_ano(ano):
    zp = PASTA / f"censo_{ano}.zip"
    z = zipfile.ZipFile(zp)
    nome = arquivo_escola(z)
    with z.open(nome) as f:
        cab = f.readline()
    cod = "utf-8" if cab.startswith(b"\xef\xbb\xbf") else "latin1"
    colunas = [c.strip().lstrip("﻿") for c in cab.decode(cod).split(";")]
    querer = ["CO_UF", "CO_MUNICIPIO", "CO_ENTIDADE", "TP_DEPENDENCIA", "TP_SITUACAO_FUNCIONAMENTO"] + list(ITENS) + list(SOMAS)
    usar = [c for c in querer if c in colunas]
    partes = []
    with z.open(nome) as f:
        for ch in pd.read_csv(f, sep=";", encoding=cod, dtype=str, chunksize=100000,
                              usecols=lambda c: c.strip().lstrip("﻿") in usar):
            ch.columns = [c.strip().lstrip("﻿") for c in ch.columns]
            partes.append(ch[(ch["CO_UF"] == "50") & (ch["TP_DEPENDENCIA"] == "3") & (ch["TP_SITUACAO_FUNCIONAMENTO"] == "1")])
    df = pd.concat(partes, ignore_index=True)
    for c in df.columns:
        if c not in ("CO_MUNICIPIO", "CO_ENTIDADE"):
            df[c] = pd.to_numeric(df[c], errors="coerce")
    df["ano"] = ano
    df.attrs["arquivo"] = f"02_iquems/02_painel_educacao_ms/dados_brutos/inep/censo/{zp.name} > {nome}"
    return df, [c for c in list(ITENS) + list(SOMAS) if c not in colunas]


def main():
    linhas = []
    for ano in ANOS:
        df, faltam = ler_ano(ano)
        arq = df.attrs["arquivo"]
        g = df.groupby("CO_MUNICIPIO")
        base = pd.DataFrame({"cod_ibge": g.size().index.astype(str), "ano": ano})
        reg = [base.assign(indicador="infra_n_escolas", valor=g.size().values, unidade="escolas")]
        for col, (ind, _) in ITENS.items():
            if col in faltam:
                continue
            pct = g[col].mean() * 100  # média de 0/1 entre as escolas com o item informado
            reg.append(base.assign(indicador=ind, valor=pct.values, unidade="% das escolas municipais"))
        if "QT_SALAS_UTILIZADAS" in df and "QT_SALAS_UTILIZA_CLIMATIZADAS" in df:
            s = g[["QT_SALAS_UTILIZADAS", "QT_SALAS_UTILIZA_CLIMATIZADAS"]].sum(min_count=1)
            reg.append(base.assign(indicador="infra_pct_salas_climatizadas",
                                   valor=(s["QT_SALAS_UTILIZA_CLIMATIZADAS"] / s["QT_SALAS_UTILIZADAS"] * 100).values,
                                   unidade="% das salas utilizadas"))
        comp = [c for c in ("QT_DESKTOP_ALUNO", "QT_COMP_PORTATIL_ALUNO", "QT_TABLET_ALUNO") if c in df]
        if comp:
            reg.append(base.assign(indicador="infra_computadores_alunos",
                                   valor=g[comp].sum(min_count=1).sum(axis=1, min_count=1).values,
                                   unidade="equipamentos (desktop, portátil e tablet para alunos)"))
        x = pd.concat(reg, ignore_index=True)
        x["fonte"] = f"Inep, microdados do Censo Escolar {ano} (escolas municipais em atividade)"
        x["arquivo"] = arq
        x["observacao"] = ("itens ausentes no arquivo do ano: " + ", ".join(faltam)) if faltam else ""
        linhas.append(x)
        print(f"[censo] {ano}: {len(df)} escolas municipais em atividade em {df['CO_MUNICIPIO'].nunique()} municípios"
              + (f"; itens ausentes: {faltam}" if faltam else ""), flush=True)
    out = pd.concat(linhas, ignore_index=True)
    CACHE.mkdir(parents=True, exist_ok=True)
    out.to_parquet(CACHE / "censo_infra_municipal.parquet", index=False)


if __name__ == "__main__":
    main()
