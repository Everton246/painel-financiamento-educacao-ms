"""Monta a base única do painel em dados/base/ (formato longo) a partir das fontes já coletadas.

Objetivos a e b: lidos de 04_dados_ICMS_IQE_VAAR/dados_processados (fonte oficial; NADA é recalculado aqui).
IQE-MS, VAAR e contexto do Inep: 04_dados e base do painel do Iquems (só leitura).
Objetivo c (parcial): Fundeb por município (FNDE), Siconfi (DCA e MSC), Censo Escolar (infraestrutura), remuneração
docente (Inep, 2021) e, quando o serviço voltar, Siope.

Saídas em dados/base/:
  indicadores.parquet  cod_ibge, municipio, ano, indicador, valor, unidade, fonte, arquivo, pagina, observacao
  atributos.parquet    textos por município e ano (situação no VAAR, condicionalidades, notas do IQE-MS, seleção...)
  municipios.parquet   cadastro: código IBGE, nome, população (Censo 2022), porte, faixa de porte, seleções
  ordenamento.parquet  ordenamento e seleções (cópia de 09_indicador_ordenamento.csv e das seleções do 04_dados)
  catalogo.csv         cada indicador: nome, unidade, objetivo, significado do "ano", fonte e definição
  normas.csv           linha do tempo das normas (tratamento/normas.py)
  malha_ms_municipios.geojson (cópia da malha do painel do Iquems), resumo.json
"""
import gzip
import json
import re
import shutil
import subprocess
import sys
import unicodedata
import zipfile
from datetime import datetime
from pathlib import Path

import pandas as pd

from comum import BASE, BRUTOS, CACHE, DADOS, FONTE_AB, IQUEMS, PROC_AB, ler_ab, longo, municipios

AB = "04_dados_ICMS_IQE_VAAR/dados_processados/"
ATRIB = []   # (cod_ibge, ano, atributo, texto, fonte)


def atributos(df, ano_col, cols, fonte, ano_fixo=None):
    for c in cols:
        p = pd.DataFrame({"cod_ibge": df["cod_ibge"].astype(str), "ano": ano_fixo if ano_fixo is not None else df[ano_col],
                          "atributo": c, "texto": df[c].astype("string")})
        p["fonte"] = df[fonte].astype(str).values if fonte in df else fonte
        ATRIB.append(p)


# ------------------------------------------------------------------------------------------------ objetivo a

def objetivo_a():
    partes = []
    for ano in (2024, 2025):
        d = ler_ab(f"05_icms_educacional_{ano}.csv")
        res = ler_ab(f"02_sefaz_anexo3_{ano}.csv")[["cod_ibge", "fonte"]].rename(columns={"fonte": "resolucao"})
        d = d.merge(res, on="cod_ibge")
        d["fonte_txt"] = ("Cálculo de 04_dados (script 05): repasse do Portal da Transparência MS; índices da "
                          + d["resolucao"] + "; coeficiente do " + d["fonte_iqe"] + ". Método: " + d["metodo"])
        m = {"R": ("icms_repasse_total", "R$"), "iqe_coef": ("icms_iqe_coef", "coeficiente"),
             "iqe_part": ("icms_iqe_part", "proporção"), "iqe_indice": ("icms_iqe_indice", "índice (%)"),
             "indice_aplicado": ("icms_indice_aplicado", "índice (%)"), "E": ("icms_educacional", "R$"),
             "R_menos_E": ("icms_repasse_sem_educ", "R$"), "fatia_demais": ("icms_fatia_demais", "proporção"),
             "contrafactual": ("icms_contrafactual", "R$"), "ganho_perda": ("icms_ganho_perda", "R$"),
             "estrutural": ("icms_estrutural", "R$"), "desempenho": ("icms_desempenho", "R$"),
             "checagem": ("icms_checagem", "R$")}
        partes.append(longo(d, "exercicio", m, "fonte_txt", AB + f"05_icms_educacional_{ano}.csv"))
        c = ler_ab(f"05_comparacao_{ano}.csv")
        c["ano"] = ano
        mc = {"E_normalizacao": ("icms_educacional_normalizacao", "R$"), "dif_reais": ("icms_dif_resolucao_normalizacao", "R$"),
              "dif_pct": ("icms_dif_resolucao_normalizacao_pct", "% (diferença / E pela resolução × 100)"),
              "ganho_perda_normalizacao": ("icms_ganho_perda_normalizacao", "R$"),
              "desempenho_normalizacao": ("icms_desempenho_normalizacao", "R$")}
        partes.append(longo(c, "ano", mc, "Cálculo de 04_dados (script 05): comparação resolução × regra de normalização "
                            "(participação no IQE × 10% × soma dos repasses)", AB + f"05_comparacao_{ano}.csv"))
    d = ler_ab("05_icms_educacional_2026.csv")
    res = ler_ab("02_sefaz_anexo3_2026.csv")[["cod_ibge", "fonte"]].rename(columns={"fonte": "resolucao"})
    d = d.merge(res, on="cod_ibge")
    d["fonte_txt"] = "Índices da " + d["resolucao"] + "; coeficiente do " + d["fonte_iqe"] + ". " + d["metodo"]
    m = {"iqe_coef": ("icms_iqe_coef", "coeficiente"), "iqe_part": ("icms_iqe_part", "proporção"),
         "iqe_indice": ("icms_iqe_indice", "índice (%)"), "indice_aplicado": ("icms_indice_aplicado", "índice (%)"),
         "desempenho_pct_total": ("icms_desempenho_pct_total", "pontos percentuais do total repassado aos 79"),
         "desempenho_pct_total_normalizacao": ("icms_desempenho_pct_total_normalizacao", "pontos percentuais do total repassado aos 79")}
    partes.append(longo(d, "exercicio", m, "fonte_txt", AB + "05_icms_educacional_2026.csv",
                        obs="2026 PROVISÓRIO: repasse anual pendente (só no início de 2027); valores em R$ não calculados"))
    # resumo da decomposição (estado) -> linha com cod_ibge 50
    r = ler_ab("05_resumo_decomposicao.csv").assign(cod_ibge="50")
    mr = {"soma_R": ("icms_soma_repasses", "R$"), "P": ("icms_parcela_educacional_total", "R$"),
          "estrutural_cov": ("icms_parte_estrutural_cov", "proporção"), "desempenho_cov": ("icms_parte_desempenho_cov", "proporção"),
          "estrutural_var": ("icms_parte_estrutural_var", "proporção"), "desempenho_var": ("icms_parte_desempenho_var", "proporção")}
    partes.append(longo(r, "exercicio", mr, "Cálculo de 04_dados (script 05): resumo da decomposição", AB + "05_resumo_decomposicao.csv"))
    tot = ler_ab("04_totais_pdf.csv").assign(cod_ibge="50")
    partes.append(longo(tot, "ano", {"total_pdf": ("icms_total_pdf_portal", "R$")}, "Portal da Transparência MS: linha TOTAL do PDF",
                        "04_dados_ICMS_IQE_VAAR/" + tot["arquivo"]))
    return pd.concat(partes, ignore_index=True)


# ------------------------------------------------------------------------------------------------ IQE-MS

def iqe():
    d = ler_ab("03_iqe_editais_finais.csv")
    d["arq"] = "04_dados_ICMS_IQE_VAAR/" + d["arquivo"]
    d["pag"] = "p. " + d["pagina"].astype(str) + " do PDF"
    d["obs"] = "ano = ano-base; o coeficiente define o repasse de " + d["exercicio_repasse"].astype(str)
    m = {"iqe_coef": ("iqe_coef", "coeficiente"), "n_valores": ("iqe_n_valores_linha", "valores na linha do edital"),
         "exercicio_repasse": ("iqe_exercicio_repasse", "ano")}
    lg = longo(d, "ano_base", m, "fonte", "arq", "pag", "obs")
    d["coef_minimo_txt"] = d["coef_minimo_do_ano"].map({True: "sim", False: "não"})
    d["sem_resultado_txt"] = d["sem_resultado_completo"].map({True: "sim", False: "não"})
    for c in ("nota", "nota_texto"):
        d[c] = d[c].fillna("")
    atributos(d.rename(columns={"coef_minimo_txt": "iqe_coef_minimo", "sem_resultado_txt": "iqe_sem_resultado_completo",
                                "nota": "iqe_nota_marca", "nota_texto": "iqe_nota_texto"}),
              "ano_base", ["iqe_coef_minimo", "iqe_sem_resultado_completo", "iqe_nota_marca", "iqe_nota_texto"], "fonte")
    return lg


# ------------------------------------------------------------------------------------------------ objetivo b

def objetivo_b():
    v = ler_ab("07_vaar.csv")
    m = {"valor_distribuido": ("vaar_valor", "R$"), "coef_distribuido": ("vaar_coef", "coeficiente"),
         "valor_apos_ajuste": ("vaar_valor_apos_ajuste", "R$"), "coef_apos_ajuste": ("vaar_coef_apos_ajuste", "coeficiente"),
         "bb_vaar_bruto": ("vaar_bb_bruto_ano_civil", "R$"), "bb_vaar_deducao": ("vaar_bb_deducao_ano_civil", "R$"),
         "bb_vaar_liquido": ("vaar_bb_liquido_ano_civil", "R$"), "valor_prev_p14_2025": ("vaar_prev_p14_2025", "R$"),
         "valor_prev_p6_2026": ("vaar_prev_p6_2026", "R$")}
    v["obs"] = v["ano"].map(lambda a: "2026 PROVISÓRIO: valor previsto (Portaria Interministerial MEC/MF nº 11/2026)" if a == 2026 else "")
    lg = [longo(v, "ano", {k: m[k] for k in ("valor_distribuido", "coef_distribuido")}, "fonte_distribuido", AB + "07_vaar.csv", obs="obs"),
          longo(v, "ano", {k: m[k] for k in ("valor_apos_ajuste", "coef_apos_ajuste")}, "fonte_apos_ajuste", AB + "07_vaar.csv"),
          longo(v, "ano", {k: m[k] for k in ("bb_vaar_bruto", "bb_vaar_deducao", "bb_vaar_liquido")},
                "FNDE, valores repassados pelo Banco do Brasil (ano civil: inclui a parcela de janeiro do exercício anterior "
                "e ajustes; não coincide com o valor do exercício)", AB + "07_vaar.csv"),
          longo(v, "ano", {"valor_prev_p14_2025": m["valor_prev_p14_2025"]}, "fonte_prev_p14_2025", AB + "07_vaar.csv"),
          longo(v, "ano", {"valor_prev_p6_2026": m["valor_prev_p6_2026"]}, "fonte_prev_p6_2026", AB + "07_vaar.csv")]
    txt = ["habilitado", "situacao_vaar", "condicionalidades_descumpridas", "cond_I_cumpriu", "cond_II_cumpriu",
           "cond_III_cumpriu", "cond_IV_cumpriu", "cond_V_cumpriu", "evoluiu_indicadores", "evoluiu_atendimento",
           "evoluiu_aprendizagem", "beneficiado", "condicionalidades_descumpridas_versaoA", "primeiro_mes_pagamento",
           "fonte_habilitacao", "fonte_distribuido", "fonte_cronograma"]
    vv = v.copy()
    for c in txt:
        vv[c] = vv[c].fillna("")
    atributos(vv.rename(columns={c: f"vaar_{c}" for c in txt}), "ano", [f"vaar_{c}" for c in txt], "fonte_habilitacao")
    # base do indicador por ano (matrículas, valores por matrícula, indicador)
    b = ler_ab("09_base_indicador_por_ano.csv")
    b["obs"] = b["ano"].map(lambda a: "2026 PROVISÓRIO (VAAR previsto; matrículas do Censo 2025; desempenho em R$ pendente)"
                            if a == 2026 else "")
    mb = {"mat_municipal": ("mat_rede_municipal_sinopse", "matrículas"), "vaar_por_mat": ("vaar_por_mat", "R$ por matrícula"),
          "vaar_ajust_por_mat": ("vaar_apos_ajuste_por_mat", "R$ por matrícula"),
          "desemp_por_mat": ("icms_desempenho_por_mat", "R$ por matrícula"), "indicador": ("indicador_selecao", "R$ por matrícula"),
          "indicador_ajust": ("indicador_selecao_apos_ajuste", "R$ por matrícula")}
    lg.append(longo(b, "ano", mb, "Cálculo de 04_dados (script 09): componente de desempenho do ICMS Educacional por "
                    "matrícula + VAAR por matrícula da rede municipal (Censo do mesmo ano; 2026 usa o Censo 2025)",
                    AB + "09_base_indicador_por_ano.csv", obs="obs"))
    atributos(b.rename(columns={"habilitado_contingencia": "vaar_habilitado_contingencia"}), "ano",
              ["vaar_habilitado_contingencia"], "Decisão do autor (LOG 04_dados, sessão 3): Antônio João conta como "
              "habilitado em 2024 e 2025 nas tabelas de contingência")
    mat = ler_ab("08_matriculas.csv")
    lg.append(longo(mat, "ano_censo", {"mat_total": ("mat_total_sinopse", "matrículas"), "mat_estadual": ("mat_estadual_sinopse", "matrículas"),
                                       "mat_municipal": ("mat_municipal_sinopse_censo", "matrículas")},
                    "fonte_matriculas", AB + "08_matriculas.csv"))
    return pd.concat(lg, ignore_index=True)


def ordenamento():
    o = ler_ab("09_indicador_ordenamento.csv")
    for nome, rot in (("09_selecao_principal_porte.csv", "selecao_principal"), ("09_selecao_alternativa_extremos.csv", "selecao_alternativa")):
        s = ler_ab(nome)[["cod_ibge", "grupo"]].rename(columns={"grupo": rot})
        o = o.merge(s, on="cod_ibge", how="left")
    o["fonte"] = AB + "09_indicador_ordenamento.csv, 09_selecao_principal_porte.csv, 09_selecao_alternativa_extremos.csv (script 09)"
    return o


# ------------------------------------------------------------------------------------------------ Inep (Iquems)

def inep_iquems(cods):
    ind = pd.read_parquet(IQUEMS / "dados" / "base" / "indicadores.parquet",
                          filters=[("nivel", "==", "municipio"), ("rede", "==", "municipal")])
    ind = ind[ind["ano"].between(2019, 2025)].copy()
    for c in ("indicador", "fonte", "etapa", "serie", "disciplina", "unidade"):
        ind[c] = ind[c].astype(str)
    sel = []
    # SAEMS 2º ano (insumo do IQE-MS) – rede municipal
    s = ind[ind["indicador"].isin(["saems_participacao", "saems_proficiencia", "saems_avaliados", "saems_previstos"])
            & (ind["serie"] == "2º ano EF")].copy()
    s["codigo"] = "saems2_" + s["indicador"].str.replace("saems_", "") + "_" + s["disciplina"].str.lower()
    sel.append(s)
    e = ind[ind["indicador"].isin(["ideb", "saeb_proficiencia_lp", "saeb_proficiencia_mt"]) & ind["etapa"].isin(["EF_AI", "EF_AF"])].copy()
    e["codigo"] = e["indicador"] + "_" + e["etapa"].str.lower()
    sel.append(e)
    n = ind[ind["indicador"].isin(["inse_media"])].copy()
    n["codigo"] = "inse_media"
    sel.append(n)
    mt = ind[(ind["indicador"] == "matriculas") & (ind["etapa"] == "TODAS")].copy()
    mt["codigo"] = "mat_municipal_censo_escolas"
    sel.append(mt)
    x = pd.concat(sel, ignore_index=True)
    x = x[x["cod_municipio"].isin(cods)]
    return pd.DataFrame({"cod_ibge": x["cod_municipio"].astype(str), "ano": x["ano"].astype(int), "indicador": x["codigo"],
                         "valor": x["valor"], "unidade": x["unidade"], "fonte": x["fonte"] + " (via painel do Iquems)",
                         "arquivo": "02_iquems/02_painel_educacao_ms/dados/base/indicadores.parquet",
                         "pagina": "", "observacao": x["observacao"].fillna("").astype(str)})


def remuneracao_inep(cods):
    zp = IQUEMS / "dados_brutos" / "inep" / "remuneracao" / "remuneracao_municipios_2021.zip"
    z = zipfile.ZipFile(zp)
    nome = [m for m in z.namelist() if m.lower().endswith(".xlsx")][0]
    d = pd.read_excel(z.open(nome), header=8, dtype={"CO_MUNICIPIO": str})
    d = d[(d["SG_UF"] == "MS") & (d["NO_DEPENDENCIA"] == "Municipal") & (d["NO_CATEGORIA"] == "Total")].copy()
    d["cod_ibge"] = d["CO_MUNICIPIO"].astype(str)
    d = d[d["cod_ibge"].isin(cods)]
    m = {"ED_BAS_CAT1": ("rem_docentes_n", "docentes (Censo Escolar)"), "ED_BAS_CAT2": ("rem_pct_localizados_rais", "%"),
         "ED_BAS_CAT4": ("rem_mediana_bruta", "R$ por mês"), "ED_BAS_CAT5": ("rem_media_bruta", "R$ por mês"),
         "ED_BAS_CAT8": ("rem_carga_horaria", "horas semanais"), "ED_BAS_CAT9": ("rem_media_40h", "R$ por mês (40 h semanais)")}
    return longo(d, "NU_ANO_CENSO", m, "Inep, Remuneração média dos docentes em exercício na educação básica, por município "
                 "(rede municipal, total), 2021", f"02_iquems/02_painel_educacao_ms/dados_brutos/inep/remuneracao/{zp.name} > {nome}",
                 obs="último ano publicado pelo Inep (página consultada em 24/11/2026)")


# ------------------------------------------------------------------------------------------------ objetivo c e contexto

def _slug(t):
    t = unicodedata.normalize("NFKD", str(t)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "_", t).strip("_")


def fundeb_bb(cods):
    """Arquivos do FNDE com o Fundeb por ente e origem de receita (2021–2023 desta pasta; 2024 e 2025 do 04_dados)."""
    arqs = {}
    for p in sorted((BRUTOS / "fnde_fundeb").glob("*.xlsx")) + sorted((FONTE_AB / "dados_brutos" / "fnde" / "repasses_bb").glob("*.xlsx")):
        if "(1)" in p.name:
            continue  # segunda versão de 2024 publicada no portal: comparada em conferir.py
        ano = int(re.search(r"(\d{4})\.xlsx$", unicodedata.normalize("NFC", p.name)).group(1))
        arqs[ano] = p
    partes = []
    for ano, p in sorted(arqs.items()):
        raw = pd.read_excel(p, header=None)
        lin = raw.index[raw.iloc[:, 0].astype(str).str.strip().eq("UF")][0]
        grupo = raw.iloc[lin].ffill()
        sub = raw.iloc[lin + 1]
        dados = raw.iloc[lin + 2:].copy()
        dados = dados[dados.iloc[:, 0].astype(str).str.strip().eq("MS")]
        dados["cod_ibge"] = dados.iloc[:, 2].astype(str).str.replace(r"\.0$", "", regex=True)
        dados = dados[dados["cod_ibge"].isin(cods)]
        rel = p.relative_to(FONTE_AB.parent.parent).as_posix() if FONTE_AB.parent.parent in p.parents else p.as_posix()
        if "05_painel_financiamento_ms" in rel:
            rel = "05_painel_financiamento_ms/dados_brutos/fnde_fundeb/" + p.name
        for j in range(3, raw.shape[1]):
            g, s = str(grupo.iloc[j]).strip(), str(sub.iloc[j]).strip()
            if g == "nan" or s == "nan":
                continue
            tipo = {"valor bruto": "bruto", "dedução": "deducao", "deducao": "deducao", "valores líquidos": "liquido"}.get(s.lower(), _slug(s))
            partes.append(pd.DataFrame({"cod_ibge": dados["cod_ibge"].values, "ano": ano,
                                        "indicador": f"fundeb_{_slug(g)}_{tipo}", "valor": pd.to_numeric(dados.iloc[:, j], errors="coerce").values,
                                        "unidade": "R$", "fonte": f"FNDE, Valores repassados pelo Banco do Brasil por ente federado e "
                                        f"origem de receita, exercício de {ano} (ano civil de pagamento); coluna '{g} – {s}'",
                                        "arquivo": rel, "pagina": "", "observacao": ""}))
    out = pd.concat(partes, ignore_index=True)
    tots = []
    for tipo, rot in (("liquido", "líquidos"), ("bruto", "brutos")):
        sel = out[out["indicador"].str.endswith("_" + tipo)]
        tot = sel.groupby(["cod_ibge", "ano"], as_index=False)["valor"].sum(min_count=1)
        tots.append(tot.assign(indicador=f"fundeb_total_{tipo}", unidade="R$",
                               fonte=f"Soma das colunas de valores {rot} do arquivo do FNDE do ano (contribuições + complementações)",
                               arquivo="(derivado)", pagina="", observacao="soma feita pelo painel; ano civil de pagamento"))
    return pd.concat([out] + tots, ignore_index=True)


def _cod(serie):
    return serie.astype(str).str.replace(r"\.0$", "", regex=True)


def fundeb_exercicio(cods):
    """Fundeb devido no EXERCÍCIO (portarias do FNDE/MEC), para comparar com o pago no ano civil (Banco do Brasil)."""
    pasta = BRUTOS / "fnde_fundeb_exercicio"
    partes = []
    cols = ["fundeb_exerc_contribuicao", "fundeb_exerc_vaaf", "fundeb_exerc_vaat", "fundeb_exerc_vaar",
            "fundeb_exerc_complementacao_total", "fundeb_exerc_total"]
    for ano, nome, obs in ((2025, "1.ReceitatotaldoFundebporentefederado_2025_P5-2026.xlsx",
                            "última publicação do exercício (Portaria nº 5/2026, que traz também o ajuste do VAAR de 2025)"),
                           (2026, "1-receita-total-do-fundeb-por-ente-federado-p-11_2026.xlsx",
                            "2026 PROVISÓRIO: receita prevista (Portaria nº 11/2026)")):
        p = pasta / nome
        if not p.exists():
            continue
        raw = pd.read_excel(p, header=None)
        titulo = str(raw.iloc[7, 0]).strip()
        d = raw[raw.iloc[:, 0].astype(str).str.strip().eq("MS")].copy()
        d["cod_ibge"] = _cod(d.iloc[:, 1])
        d = d[d["cod_ibge"].isin(cods)]
        for j, ind in zip(range(3, 9), cols):
            rot = " ".join(str(raw.iloc[9, j]).split())
            partes.append(pd.DataFrame({"cod_ibge": d["cod_ibge"].values, "ano": ano, "indicador": ind,
                                        "valor": pd.to_numeric(d.iloc[:, j], errors="coerce").values, "unidade": "R$",
                                        "fonte": f"FNDE/MEC, tabela '{titulo}', coluna '{rot}'",
                                        "arquivo": "dados_brutos/fnde_fundeb_exercicio/" + nome, "pagina": "",
                                        "observacao": obs}))
    p = pasta / "AjustedaComplementaoVAAT_2024_P3-2025.xlsx"
    if p.exists():
        raw = pd.read_excel(p, header=None)
        d = raw[raw.iloc[:, 0].astype(str).str.strip().eq("MS")].copy()
        d["cod_ibge"] = _cod(d.iloc[:, 2])
        for j, ind in ((3, "fundeb_exerc_vaat"), (4, "fundeb_exerc_vaat_distribuida"), (5, "fundeb_exerc_vaat_ajuste")):
            v = dict(zip(d["cod_ibge"], pd.to_numeric(d.iloc[:, j], errors="coerce")))
            rot = " ".join(str(raw.iloc[6, j]).split())
            cs = sorted(cods)
            partes.append(pd.DataFrame({"cod_ibge": cs, "ano": 2024, "indicador": ind,
                                        "valor": [v.get(c, 0.0) for c in cs], "unidade": "R$",
                                        "fonte": "FNDE/MEC, Portaria Interministerial nº 3, de 28/04/2025, Anexo II (ajuste da "
                                                 f"complementação VAAT de 2024), coluna '{rot}'",
                                        "arquivo": "dados_brutos/fnde_fundeb_exercicio/" + p.name, "pagina": "",
                                        "observacao": ["" if c in v else "não consta no anexo: não recebeu VAAT em 2024 (valor 0)"
                                                       for c in cs]}))
    if not partes:
        return pd.DataFrame(columns=["cod_ibge", "ano", "indicador", "valor", "unidade", "fonte", "arquivo", "pagina", "observacao"])
    return pd.concat(partes, ignore_index=True)


def _abre(p):
    return json.load(gzip.open(p, "rt", encoding="utf-8"))


def siconfi(cods):
    pasta = BRUTOS / "siconfi"
    regs = []
    for p in sorted((pasta / "dca_I-E").glob("*.json.gz")):
        _, ano, _, cod = p.name.replace(".json.gz", "").split("_")
        if cod not in cods:
            continue
        itens = _abre(p)["items"]
        rot = {x["rotulo"] for x in itens}
        alvo = "Total Geral da Despesa por Função" if "Total Geral da Despesa por Função" in rot else None
        for x in itens:
            if alvo and x["rotulo"] != alvo:
                continue
            mm = re.match(r"^12(?:\.(\d{3}))? - (.*)$", x["conta"].strip())
            if not mm:
                continue
            col = {"Despesas Empenhadas": "empenhada", "Despesas Liquidadas": "liquidada", "Despesas Pagas": "paga"}.get(x["coluna"])
            if not col:
                continue
            ind = f"educ_dca_{col}" if not mm.group(1) else f"educ_dca_sub{mm.group(1)}_{col}"
            regs.append({"cod_ibge": cod, "ano": int(ano), "indicador": ind, "valor": x["valor"], "unidade": "R$",
                         "fonte": f"Siconfi/Tesouro, DCA {ano}, Anexo I-E (despesa por função), conta '{x['conta']}', coluna '{x['coluna']}'",
                         "arquivo": "dados_brutos/siconfi/dca_I-E/" + p.name, "pagina": "", "observacao": ""})
    for p in sorted((pasta / "dca_I-C").glob("*.json.gz")):
        _, ano, _, cod = p.name.replace(".json.gz", "").split("_")
        if cod not in cods:
            continue
        tot = {}
        for x in _abre(p)["items"]:
            if x["cod_conta"] == "TotalReceitas":
                tot[x["coluna"]] = tot.get(x["coluna"], 0) + x["valor"]
        if "Receitas Brutas Realizadas" in tot:
            bruta = tot["Receitas Brutas Realizadas"]
            ded = sum(v for k, v in tot.items() if k.lower().startswith("dedu"))
            for ind, v in (("receita_total_bruta", bruta), ("receita_total_liquida", bruta - ded)):
                regs.append({"cod_ibge": cod, "ano": int(ano), "indicador": ind, "valor": v, "unidade": "R$",
                             "fonte": f"Siconfi/Tesouro, DCA {ano}, Anexo I-C, 'TOTAL DAS RECEITAS' ("
                             + ("receitas brutas realizadas" if ind.endswith("bruta") else "brutas menos deduções: " + ", ".join(k for k in tot if k.lower().startswith('dedu'))) + ")",
                             "arquivo": "dados_brutos/siconfi/dca_I-C/" + p.name, "pagina": "", "observacao": ""})
    # MSC: despesa da função 12 por natureza (empenhada = movimento líquido das contas 6.2.2.1.3.xx no ano)
    grupos = {"pessoal": ("3.1 Pessoal e encargos sociais", lambda n: n.startswith("31")),
              "material_consumo": ("3.3.90.30 Material de consumo", lambda n: n[:2] == "33" and n[4:6] == "30"),
              "servicos_pj": ("3.3.90.39 Outros serviços de terceiros – pessoa jurídica", lambda n: n[:2] == "33" and n[4:6] == "39"),
              "obras": ("4.4.90.51 Obras e instalações", lambda n: n[:2] == "44" and n[4:6] == "51"),
              "equipamentos": ("4.4.90.52 Equipamentos e material permanente", lambda n: n[:2] == "44" and n[4:6] == "52")}
    for p in sorted((pasta / "msc").glob("*.json.gz")):
        partes_nome = p.name.replace(".json.gz", "").split("_")
        ano, cod = int(partes_nome[1]), partes_nome[-1]
        if cod not in cods:
            continue
        itens = [x for x in _abre(p)["items"] if x.get("funcao") == "12" and str(x.get("conta_contabil", "")).startswith("62213")]
        if not itens:
            continue
        df = pd.DataFrame(itens)
        df["v"] = df["valor"].where(df["natureza_conta"] == "D", -df["valor"])
        df["nat"] = df["natureza_despesa"].astype(str)
        total = df["v"].sum()
        pago = df.loc[df["conta_contabil"].astype(str).str.startswith("6221304"), "v"].sum()
        base = {"cod_ibge": cod, "ano": ano, "unidade": "R$", "arquivo": "dados_brutos/siconfi/msc/" + p.name, "pagina": "",
                "observacao": "empenhada = movimento líquido (débito − crédito) das contas 6.2.2.1.3.xx no ano, função 12"}
        fonte = f"Siconfi/Tesouro, Matriz de Saldos Contábeis de encerramento (MSCE) {ano}, mês 12, classe 6, função 12"
        regs.append({**base, "indicador": "educ_msc_empenhada_total", "valor": total, "fonte": fonte})
        regs.append({**base, "indicador": "educ_msc_paga_total", "valor": pago, "fonte": fonte + " (conta 6.2.2.1.3.04)"})
        usado = pd.Series(False, index=df.index)
        for g, (rot, f) in grupos.items():
            mk = df["nat"].map(f)
            usado |= mk
            regs.append({**base, "indicador": f"educ_msc_{g}", "valor": df.loc[mk, "v"].sum(), "fonte": f"{fonte}; natureza {rot}"})
        regs.append({**base, "indicador": "educ_msc_outras", "valor": df.loc[~usado, "v"].sum(),
                     "fonte": f"{fonte}; demais naturezas de despesa"})
    return pd.DataFrame(regs)


def valida_msc(s, tol=0.005):
    """A composição por natureza (MSC) só fica onde o total da função 12 na MSC confere com a DCA I-E (±0,5%).
    Nos demais município-ano, as linhas de natureza saem (o painel mostra 'sem dado') e o total da MSC fica com aviso."""
    if s.empty:
        return s
    dca = s[s["indicador"] == "educ_dca_empenhada"].set_index(["cod_ibge", "ano"])["valor"]
    msc = s[s["indicador"] == "educ_msc_empenhada_total"].set_index(["cod_ibge", "ano"])["valor"]
    r = (msc / dca).dropna()
    ok = set(r[(r - 1).abs() <= tol].index)
    chave = list(zip(s["cod_ibge"], s["ano"]))
    e_msc = s["indicador"].str.startswith("educ_msc_")
    natureza = e_msc & ~s["indicador"].isin(["educ_msc_empenhada_total", "educ_msc_paga_total"])
    valido = pd.Series([k in ok for k in chave], index=s.index)
    s = s[~(natureza & ~valido)].copy()
    tot = s["indicador"].isin(["educ_msc_empenhada_total", "educ_msc_paga_total"])
    s.loc[tot & ~valido.loc[s.index], "observacao"] = ("NÃO CONFERE com a DCA I-E (diferença acima de 0,5%): composição por "
                                                        "natureza omitida neste município-ano")
    print(f"[base] MSC: composição por natureza aceita em {len(ok)} de {len(r)} município-ano (total da MSC = DCA ±0,5%)")
    return s


def ibge(cods):
    regs = []
    for nome, ind, unid, mult in (("pib_municipios_sidra5938.json", "pib", "R$", 1000),
                                  ("estimativa_populacao_sidra6579_2021_2024_2025_2026.json", "pop_estimada", "pessoas", 1)):
        p = BRUTOS / "ibge" / nome
        if not p.exists():
            continue
        d = json.loads(p.read_text(encoding="utf-8"))[1:]
        for x in d:
            if x["D1C"] in cods:
                v = pd.to_numeric(x["V"], errors="coerce")
                regs.append({"cod_ibge": x["D1C"], "ano": int(x["D3C"]), "indicador": ind, "valor": v * mult if pd.notna(v) else v,
                             "unidade": unid, "fonte": f"IBGE/SIDRA, tabela {nome.split('sidra')[1].split('.')[0]} ({x['D2N']})",
                             "arquivo": "dados_brutos/ibge/" + nome, "pagina": "",
                             "observacao": "PIB publicado em mil reais; multiplicado por 1.000" if ind == "pib" else ""})
    p = BRUTOS / "ibge" / "ipca_numero_indice_sidra1737_2021_2025.json"
    if p.exists():
        d = pd.DataFrame(json.loads(p.read_text(encoding="utf-8"))[1:])
        d["ano"] = d["D3C"].str[:4].astype(int)
        d["v"] = pd.to_numeric(d["V"], errors="coerce")
        media = d.groupby("ano")["v"].agg(["mean", "count"])
        base = media.loc[2025, "mean"]
        for ano, r in media.iterrows():
            regs.append({"cod_ibge": "50", "ano": int(ano), "indicador": "ipca_media_anual", "valor": r["mean"],
                         "unidade": "número-índice (dez/1993 = 100)",
                         "fonte": "IBGE/SIDRA, tabela 1737 (IPCA, número-índice), média dos 12 meses",
                         "arquivo": "dados_brutos/ibge/" + p.name, "pagina": "", "observacao": f"{int(r['count'])} meses"})
            regs.append({"cod_ibge": "50", "ano": int(ano), "indicador": "ipca_fator_reais_2025", "valor": base / r["mean"],
                         "unidade": "multiplicador", "fonte": "IPCA médio de 2025 ÷ IPCA médio do ano (IBGE/SIDRA, tabela 1737)",
                         "arquivo": "dados_brutos/ibge/" + p.name, "pagina": "",
                         "observacao": "valor do ano × fator = valor em reais médios de 2025 (cálculo do painel)"})
    pop = ler_ab("09_populacao.csv")
    for _, r in pop.iterrows():
        regs.append({"cod_ibge": r["cod_ibge"], "ano": 2022, "indicador": "pop_censo2022", "valor": r["populacao_2022"],
                     "unidade": "pessoas", "fonte": "IBGE/SIDRA, tabela 4709, Censo 2022 (via 04_dados)",
                     "arquivo": AB + "09_populacao.csv", "pagina": "", "observacao": ""})
    return pd.DataFrame(regs)


def siope(cods):
    """Lê os arquivos do Siope se o serviço tiver respondido; senão, nada (a página mostra 'sem dado')."""
    arqs = sorted((BRUTOS / "siope").glob("Indicadores_Siope_*_bim6_MS.json.gz"))
    regs = []
    for p in arqs:
        ano = int(p.name.split("_")[2])
        for x in _abre(p):
            cod = str(x.get("COD_MUNI") or x.get("CO_MUNICIPIO") or "")[:7]
            if cod in cods and x.get("VAL_INDI") is not None:
                regs.append({"cod_ibge": cod, "ano": ano, "indicador": "siope_" + _slug(x.get("NOM_INDI", ""))[:60],
                             "valor": x.get("VAL_INDI"), "unidade": "%", "fonte": f"FNDE/Siope, Indicadores, {ano}, 6º bimestre",
                             "arquivo": "dados_brutos/siope/" + p.name, "pagina": "", "observacao": ""})
    return pd.DataFrame(regs)


# ------------------------------------------------------------------------------------------------ montagem

def main():
    BASE.mkdir(parents=True, exist_ok=True)
    mun = municipios()
    cods = set(mun["cod_ibge"])
    blocos = {"objetivo a": objetivo_a(), "IQE-MS": iqe(), "objetivo b": objetivo_b(), "Inep (Iquems)": inep_iquems(cods),
              "remuneração 2021": remuneracao_inep(cods), "Fundeb por município": fundeb_bb(cods),
              "Fundeb por exercício": fundeb_exercicio(cods), "Siconfi": siconfi(cods),
              "IBGE": ibge(cods), "Siope": siope(cods)}
    blocos["Siconfi"] = valida_msc(blocos["Siconfi"])
    infra = CACHE / "censo_infra_municipal.parquet"
    if not infra.exists():
        subprocess.check_call([sys.executable, str(Path(__file__).parent / "t03_censo_infra.py")])
    c = pd.read_parquet(infra)
    c["pagina"] = ""
    blocos["Censo (infraestrutura)"] = c
    for k, v in blocos.items():
        print(f"[base] {k}: {len(v)} linhas, {v['indicador'].nunique() if len(v) else 0} indicadores", flush=True)
    ind = pd.concat([b for b in blocos.values() if len(b)], ignore_index=True)
    nomes = dict(zip(mun["cod_ibge"], mun["municipio"]))
    nomes["50"] = "Mato Grosso do Sul (total dos 79)"
    ind["cod_ibge"] = ind["cod_ibge"].astype(str)
    ind["municipio"] = ind["cod_ibge"].map(nomes)
    ind["ano"] = ind["ano"].astype(int)
    for col in ("fonte", "arquivo", "pagina", "observacao", "unidade"):
        ind[col] = ind[col].fillna("").astype(str).replace("nan", "")
    ind = ind[["cod_ibge", "municipio", "ano", "indicador", "valor", "unidade", "fonte", "arquivo", "pagina", "observacao"]]
    ind = ind.sort_values(["indicador", "ano", "cod_ibge"]).reset_index(drop=True)
    for col in ("indicador", "unidade", "fonte", "arquivo", "municipio"):
        ind[col] = ind[col].astype("category")
    ind.to_parquet(BASE / "indicadores.parquet", index=False)
    at = pd.concat(ATRIB, ignore_index=True)
    at["municipio"] = at["cod_ibge"].map(nomes)
    at["texto"] = at["texto"].fillna("").astype(str)
    at.to_parquet(BASE / "atributos.parquet", index=False)
    # cadastro
    pop = ler_ab("09_populacao.csv")
    o = ordenamento()
    cad = mun[["cod_ibge", "municipio"]].merge(pop, on="cod_ibge", how="left")
    cad = cad.merge(o[["cod_ibge", "faixa_porte", "selecao_principal", "selecao_alternativa"]], on="cod_ibge", how="left")
    cad.to_parquet(BASE / "municipios.parquet", index=False)
    o.to_parquet(BASE / "ordenamento.parquet", index=False)
    # tabelas de contingência e comparação entre grupos do 04_dados (script 09), copiadas sem alteração
    ler_ab("09_contingencia.csv").to_parquet(BASE / "contingencia.parquet", index=False)
    ler_ab("09_comparacao_grupos.csv").to_parquet(BASE / "comparacao_grupos.parquet", index=False)
    malha = IQUEMS / "dados" / "base" / "malha_ms_municipios.geojson"
    shutil.copyfile(malha, BASE / "malha_ms_municipios.geojson")
    subprocess.check_call([sys.executable, str(Path(__file__).parent / "normas.py")])
    subprocess.check_call([sys.executable, str(Path(__file__).parent / "catalogo.py")])
    resumo = {"montado_em": datetime.now().strftime("%Y-%m-%d %H:%M"), "linhas": int(len(ind)),
              "indicadores": int(ind["indicador"].nunique()), "municipios": int(ind.loc[ind["cod_ibge"] != "50", "cod_ibge"].nunique()),
              "anos": [int(ind["ano"].min()), int(ind["ano"].max())],
              "siope_disponivel": bool(len(blocos["Siope"]))}
    (BASE / "resumo.json").write_text(json.dumps(resumo, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[base] indicadores.parquet: {len(ind)} linhas; atributos: {len(at)}; municípios: {resumo['municipios']}")


if __name__ == "__main__":
    main()
