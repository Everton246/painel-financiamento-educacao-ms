"""Conferências da base do painel. Relatório em docs/conferencia.md (e docs/conferencia_divergencias.csv).

1. 79 municípios em cada base (indicador × ano), sem sobras nem faltas.
2. Objetivos a e b: 0 divergências entre a base do painel (o que o painel mostra) e
   (a) os CSVs de 04_dados_ICMS_IQE_VAAR/dados_processados e (b) a planilha saidas/icms_educacional_vaar_ms.xlsx.
3. Somas e totais publicados pelas fontes.
4. Amostra de valores novos relida direto na fonte original (API do Siconfi e do IBGE, planilha do FNDE).
5. Ordenamento do script 09 × ranking provisório (saidas/ranking_provisorio_icms_vaar_ms.xlsx, que não é gerado por script).
Sai com código 1 se houver divergência nos objetivos a e b ou falha de conferência obrigatória.
"""
import gzip
import json
import sys
from datetime import datetime

import numpy as np
import openpyxl
import pandas as pd

from comum import BASE, BRUTOS, DOCS, FONTE_AB, ler_ab, municipios

TOL = 1e-6
R = []            # linhas do relatório
FALHAS = []
DIVS = []


def br(v, casas=2):
    """Número no padrão brasileiro (1.234,56)."""
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "sem dado"
    return f"{v:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def secao(t):
    R.append(f"\n## {t}\n")


def item(ok, txt, obrigatoria=True):
    R.append(f"- {'OK' if ok else ('FALHA' if obrigatoria else 'AVISO')}: {txt}")
    if not ok and obrigatoria:
        FALHAS.append(txt)


def igual(a, b):
    if (a is None or (isinstance(a, float) and np.isnan(a))) and (b is None or (isinstance(b, float) and np.isnan(b))):
        return True
    try:
        a, b = float(a), float(b)
        if np.isnan(a) and np.isnan(b):
            return True
        return abs(a - b) <= TOL * max(1.0, abs(a), abs(b))
    except (TypeError, ValueError):
        return str(a).strip() == str(b).strip()


IND = pd.read_parquet(BASE / "indicadores.parquet")
IND["indicador"] = IND["indicador"].astype(str)
ATR = pd.read_parquet(BASE / "atributos.parquet")
ORD = pd.read_parquet(BASE / "ordenamento.parquet")
COD79 = set(municipios()["cod_ibge"])


def valor(ind, ano):
    d = IND[(IND["indicador"] == ind) & (IND["ano"] == ano)]
    return dict(zip(d["cod_ibge"].astype(str), d["valor"]))


def valores_nn(ind, ano):
    return {c: v for c, v in valor(ind, ano).items() if v is not None and not np.isnan(v)}


def texto(at, ano):
    d = ATR[(ATR["atributo"] == at) & (ATR["ano"] == ano)]
    return dict(zip(d["cod_ibge"].astype(str), d["texto"]))


def compara(rotulo, base, ref):
    """base, ref: dicts cod -> valor. Registra cada divergência."""
    n = 0
    for cod in sorted(set(base) | set(ref)):
        if cod not in base or cod not in ref or not igual(base.get(cod), ref.get(cod)):
            n += 1
            DIVS.append({"conferencia": rotulo, "cod_ibge": cod, "painel": base.get(cod), "referencia": ref.get(cod)})
    return n


# ------------------------------------------------------------------ 1. 79 municípios
def conf_79():
    secao("1. 79 municípios em cada base")
    m = IND[IND["cod_ibge"] != "50"].dropna(subset=["valor"])
    c = m.groupby(["indicador", "ano"])["cod_ibge"].agg(lambda s: set(s))
    linhas = []
    for (ind, ano), s in c.items():
        sobras = s - COD79
        if sobras:
            item(False, f"{ind} {ano}: códigos fora dos 79: {sorted(sobras)}")
        if len(s) != 79:
            linhas.append((ind, ano, len(s)))
    tot = len(c)
    item(not any(s - COD79 for s in c), f"nenhuma base traz código fora dos 79 municípios ({tot} combinações indicador × ano)")
    obrig = [x for x in linhas if x[0].startswith(("icms_", "vaar_valor", "vaar_coef", "vaar_por_mat", "indicador_selecao",
                                                    "iqe_", "mat_rede", "fundeb_", "infra_n_escolas", "pop_", "pib"))
             and not x[0].startswith(("icms_parte", "icms_soma", "icms_parcela", "icms_total"))]
    item(not obrig, "objetivos a e b, IQE-MS, Fundeb, Censo e IBGE: 79 municípios em todos os anos com dado"
         + (f" — exceções: {obrig}" if obrig else ""))
    if linhas:
        R.append("\nCombinações com menos de 79 municípios com valor (o restante aparece como *sem dado*):\n")
        R.append("| indicador | ano | municípios com valor |\n|---|---|---|")
        for ind, ano, n in sorted(linhas)[:80]:
            R.append(f"| {ind} | {ano} | {n} |")
        if len(linhas) > 80:
            R.append(f"| … | | (+{len(linhas) - 80}) |")


# ------------------------------------------------------------------ 2a. CSVs do 04_dados
def conf_csv():
    secao("2. Objetivos a e b: base do painel × CSVs de 04_dados (dados_processados)")
    total = 0
    pares = []
    for ano in (2024, 2025):
        d = ler_ab(f"05_icms_educacional_{ano}.csv")
        for col, ind in (("R", "icms_repasse_total"), ("E", "icms_educacional"), ("ganho_perda", "icms_ganho_perda"),
                         ("estrutural", "icms_estrutural"), ("desempenho", "icms_desempenho"), ("contrafactual", "icms_contrafactual"),
                         ("iqe_coef", "icms_iqe_coef"), ("iqe_part", "icms_iqe_part"), ("indice_aplicado", "icms_indice_aplicado")):
            pares.append((f"05_icms_educacional_{ano}.{col}", ind, ano, dict(zip(d["cod_ibge"], d[col]))))
        c = ler_ab(f"05_comparacao_{ano}.csv")
        for col, ind in (("E_normalizacao", "icms_educacional_normalizacao"), ("dif_reais", "icms_dif_resolucao_normalizacao")):
            pares.append((f"05_comparacao_{ano}.{col}", ind, ano, dict(zip(c["cod_ibge"], c[col]))))
    d = ler_ab("05_icms_educacional_2026.csv")
    pares.append(("05_icms_educacional_2026.desempenho_pct_total", "icms_desempenho_pct_total", 2026,
                  dict(zip(d["cod_ibge"], d["desempenho_pct_total"]))))
    v = ler_ab("07_vaar.csv")
    b = ler_ab("09_base_indicador_por_ano.csv")
    for ano in (2024, 2025, 2026):
        vv, bb = v[v["ano"] == ano], b[b["ano"] == ano]
        for col, ind in (("valor_distribuido", "vaar_valor"), ("valor_apos_ajuste", "vaar_valor_apos_ajuste"), ("coef_distribuido", "vaar_coef")):
            pares.append((f"07_vaar.{col} {ano}", ind, ano, dict(zip(vv["cod_ibge"], vv[col]))))
        for col, ind in (("vaar_por_mat", "vaar_por_mat"), ("desemp_por_mat", "icms_desempenho_por_mat"), ("indicador", "indicador_selecao"),
                         ("mat_municipal", "mat_rede_municipal_sinopse")):
            pares.append((f"09_base_indicador_por_ano.{col} {ano}", ind, ano, dict(zip(bb["cod_ibge"], bb[col]))))
    q = ler_ab("03_iqe_editais_finais.csv")
    for ab in (2022, 2023, 2024):
        qq = q[q["ano_base"] == ab]
        pares.append((f"03_iqe_editais_finais.iqe_coef {ab}", "iqe_coef", ab, dict(zip(qq["cod_ibge"], qq["iqe_coef"]))))
    for rot, ind, ano, ref in pares:
        n = compara("CSV: " + rot, valor(ind, ano), ref)
        total += n
    # textos
    for ano in (2024, 2025, 2026):
        vv = v[v["ano"] == ano].fillna("")
        for col in ("situacao_vaar", "habilitado", "condicionalidades_descumpridas", "beneficiado"):
            total += compara(f"CSV: 07_vaar.{col} {ano}", texto(f"vaar_{col}", ano), dict(zip(vv["cod_ibge"], vv[col].astype(str))))
    o = ler_ab("09_indicador_ordenamento.csv")
    for col in ("acumulado_2024_2025", "posicao", "posicao_ajust", "posicao_com_vaar2026_prov"):
        total += compara(f"CSV: 09_indicador_ordenamento.{col}", dict(zip(ORD["cod_ibge"], ORD[col])), dict(zip(o["cod_ibge"], o[col])))
    item(total == 0, f"{len(pares) + 15} colunas comparadas, 79 municípios cada: {total} divergências")


# ------------------------------------------------------------------ 2b. planilha final
def planilha(aba):
    wb = openpyxl.load_workbook(FONTE_AB / "saidas" / "icms_educacional_vaar_ms.xlsx", data_only=True, read_only=True)
    ws = wb[aba]
    linhas = list(ws.iter_rows(values_only=True))
    cab = linhas[5]
    dados = [r for r in linhas[6:] if r and r[0] and str(r[0]).isdigit() and len(str(r[0])) == 7]
    return pd.DataFrame(dados, columns=[str(c) if c else f"col{i}" for i, c in enumerate(cab)])


def conf_xlsx():
    secao("3. Objetivos a e b: base do painel × planilha final (saidas/icms_educacional_vaar_ms.xlsx)")
    total, ncols = 0, 0
    mapa_icms = {"Repasse total de ICMS {a} (R$) [R]": "icms_repasse_total", "Coeficiente IQE-MS ano-base {b}": "icms_iqe_coef",
                 "Participação no IQE (coef./soma)": "icms_iqe_part", "ICMS Educacional (R$) [E]": "icms_educacional",
                 "Repasse sem a parcela educacional (R$) [R−E]": "icms_repasse_sem_educ", "Fatia nos demais critérios": "icms_fatia_demais",
                 "Contrafactual (R$)": "icms_contrafactual", "Ganho ou perda (R$)": "icms_ganho_perda",
                 "Componente estrutural (R$)": "icms_estrutural", "Componente de desempenho (R$)": "icms_desempenho"}
    for ano in (2024, 2025):
        p = planilha(f"ICMS {ano}")
        for col, ind in mapa_icms.items():
            col = col.format(a=ano, b=ano - 2)
            total += compara(f"xlsx ICMS {ano}: {col}", valor(ind, ano), dict(zip(p.iloc[:, 0].astype(str), p[col])))
            ncols += 1
        res = [c for c in p.columns if c.startswith("Índice IQE (Res.")][0]
        apl = [c for c in p.columns if c.startswith("Índice aplicado (Res.")][0]
        total += compara(f"xlsx ICMS {ano}: {res}", valor("icms_iqe_indice", ano), dict(zip(p.iloc[:, 0].astype(str), p[res])))
        total += compara(f"xlsx ICMS {ano}: {apl}", valor("icms_indice_aplicado", ano), dict(zip(p.iloc[:, 0].astype(str), p[apl])))
        ncols += 2
        c = planilha(f"Comparação {ano}")
        for col, ind in ((f"ICMS Educacional pela regra de normalização (R$)", "icms_educacional_normalizacao"),
                         ("Diferença (R$) resolução − normalização", "icms_dif_resolucao_normalizacao"),
                         ("Diferença (%)", "icms_dif_resolucao_normalizacao_pct"),
                         ("Componente de desempenho pela normalização (R$)", "icms_desempenho_normalizacao")):
            ref = dict(zip(c.iloc[:, 0].astype(str), c[col]))
            if col == "Diferença (%)":  # a planilha guarda proporção (formatada em %); a base, em % (CSV do 04_dados)
                ref = {k: x * 100 for k, x in ref.items()}
            total += compara(f"xlsx Comparação {ano}: {col}", valor(ind, ano), ref)
            ncols += 1
    p = planilha("ICMS 2026")
    for col, ind in (("Coeficiente IQE-MS ano-base 2024", "icms_iqe_coef"), ("Participação no IQE (coef./soma)", "icms_iqe_part"),
                     ("Componente de desempenho em % do total repassado [(índice IQE − média dos 79) / 100]", "icms_desempenho_pct_total")):
        ref = dict(zip(p.iloc[:, 0].astype(str), p[col]))
        if ind == "icms_desempenho_pct_total":  # planilha: proporção; base: pontos percentuais (CSV do 04_dados)
            ref = {k: x * 100 for k, x in ref.items()}
        total += compara(f"xlsx ICMS 2026: {col}", valor(ind, 2026), ref)
        ncols += 1
    v = planilha("VAAR")
    v["Ano"] = v["Ano"].astype(int)
    for ano in (2024, 2025, 2026):
        vv = v[v["Ano"] == ano]
        ids = vv.iloc[:, 0].astype(str)
        for col, ind in (("Coeficiente VAAR", "vaar_coef"), ("VAAR distribuído (R$) [2026: previsto]", "vaar_valor"),
                         ("VAAR após ajuste (R$)", "vaar_valor_apos_ajuste"), ("Matrículas da rede municipal", "mat_rede_municipal_sinopse"),
                         ("VAAR por matrícula (R$)", "vaar_por_mat"), ("VAAR após ajuste por matrícula (R$)", "vaar_apos_ajuste_por_mat"),
                         ("Desempenho por matrícula (R$)", "icms_desempenho_por_mat")):
            ref = dict(zip(ids, vv[col]))
            base = valor(ind, ano)
            if ind == "icms_desempenho_por_mat" and ano == 2026:
                ref = {k: (np.nan if x in (None, "") else x) for k, x in ref.items()}
            total += compara(f"xlsx VAAR {ano}: {col}", base, ref)
            ncols += 1
        for col, at in (("Situação no VAAR (lista + anexo + cronograma)", "vaar_situacao_vaar"), ("Habilitado (lista do FNDE)", "vaar_habilitado"),
                        ("Condicionalidades descumpridas", "vaar_condicionalidades_descumpridas"),
                        ("Habilitado para contingência (inclusão tardia = sim)", "vaar_habilitado_contingencia")):
            ref = {k: ("" if x is None else str(x)) for k, x in zip(ids, vv[col])}
            total += compara(f"xlsx VAAR {ano}: {col}", texto(at, ano), ref)
            ncols += 1
    i = planilha("Indicador")
    ids = i.iloc[:, 0].astype(str)
    for col, (ind, ano) in (("2024: desempenho ICMS Educ. por matrícula", ("icms_desempenho_por_mat", 2024)),
                            ("2024: VAAR por matrícula", ("vaar_por_mat", 2024)), ("2024: indicador", ("indicador_selecao", 2024)),
                            ("2025: desempenho ICMS Educ. por matrícula", ("icms_desempenho_por_mat", 2025)),
                            ("2025: VAAR por matrícula", ("vaar_por_mat", 2025)), ("2025: indicador", ("indicador_selecao", 2025)),
                            ("2026 (PROVISÓRIO): VAAR previsto por matrícula", ("vaar_por_mat", 2026))):
        total += compara(f"xlsx Indicador: {col}", valor(ind, ano), dict(zip(ids, i[col])))
        ncols += 1
    for col, oc in (("Acumulado 2024+2025 (PRINCIPAL)", "acumulado_2024_2025"), ("Posição (1 = melhor)", "posicao"),
                    ("SENSIBILIDADE: acumulado + VAAR 2026 previsto (provisório)", "acumulado_com_vaar2026_prov"),
                    ("Posição na sensibilidade com 2026", "posicao_com_vaar2026_prov"),
                    ("SENSIBILIDADE: acumulado com VAAR após ajuste", "acumulado_2024_2025_ajust"),
                    ("Posição na sensibilidade após ajuste", "posicao_ajust")):
        total += compara(f"xlsx Indicador: {col}", dict(zip(ORD["cod_ibge"], ORD[oc])), dict(zip(ids, i[col])))
        ncols += 1
    s = planilha("Seleção")
    # aba Seleção: duas tabelas lado a lado (principal à esquerda, alternativa à direita)
    wb = openpyxl.load_workbook(FONTE_AB / "saidas" / "icms_educacional_vaar_ms.xlsx", data_only=True, read_only=True)
    todas = list(wb["Seleção"].iter_rows(values_only=True))
    cab = todas[5]
    ic = [k for k, c in enumerate(cab) if c == "Código IBGE"]
    ig = [k for k, c in enumerate(cab) if c == "Grupo"]
    rows = [r for r in todas[6:] if r]
    princ = {str(r[ic[0]]): r[ig[0]] for r in rows if r[ic[0]]}
    alt = {str(r[ic[1]]): r[ig[1]] for r in rows if len(r) > ic[1] and r[ic[1]]}
    total += compara("xlsx Seleção principal (município e grupo)", {c: g for c, g in zip(ORD["cod_ibge"], ORD["selecao_principal"]) if isinstance(g, str)}, princ)
    total += compara("xlsx Seleção alternativa (município e grupo)", {c: g for c, g in zip(ORD["cod_ibge"], ORD["selecao_alternativa"]) if isinstance(g, str)}, alt)
    q = planilha("IQE situações")
    ids = q.iloc[:, 0].astype(str)
    for ab in (2022, 2023, 2024):
        total += compara(f"xlsx IQE situações: {ab} coeficiente", valor("iqe_coef", ab), dict(zip(ids, q[f"{ab}: coeficiente (edital)"])))
        total += compara(f"xlsx IQE situações: {ab} nota (texto)", texto("iqe_nota_texto", ab),
                         {k: ("" if x is None else str(x)) for k, x in zip(ids, q[f"{ab}: nota (texto do edital)"])})
        ncols += 2
    item(total == 0, f"{ncols + 2} colunas da planilha comparadas (79 municípios cada; tolerância relativa {TOL:g}): {total} divergências")


# ------------------------------------------------------------------ 3. somas e totais
def conf_somas():
    secao("4. Somas e totais que as fontes trazem")
    for ano in (2024, 2025):
        s = sum(valor("icms_repasse_total", ano).values())
        t = valor("icms_total_pdf_portal", ano).get("50")
        item(abs(s - t) < 0.01, f"{ano}: soma dos repasses de ICMS dos 79 (R$ {br(s)}) = TOTAL do PDF do Portal (R$ {br(t)})")
        e = sum(valor("icms_educacional", ano).values())
        item(abs(e / s - 0.10) < 1e-9, f"{ano}: soma do ICMS Educacional = 10% da soma dos repasses ({e / s:.10f})")
        g = sum(valor("icms_ganho_perda", ano).values())
        item(abs(g) < 1.0, f"{ano}: soma dos ganhos e perdas = 0 (soma zero; resultado R$ {br(g, 4)})")
        est, des, gp = valor("icms_estrutural", ano), valor("icms_desempenho", ano), valor("icms_ganho_perda", ano)
        mx = max(abs(est[c] + des[c] - gp[c]) for c in gp)
        item(mx < 1e-4, f"{ano}: estrutural + desempenho = ganho ou perda em todos os municípios (diferença máxima {mx:.2e})")
    for ano in (2024, 2025, 2026):
        p = sum(valor("icms_iqe_part", ano).values())
        item(abs(p - 1) < 1e-9, f"{ano}: participações no IQE-MS somam 1 ({p:.12f})")
        ia = sum(valor("icms_indice_aplicado", ano).values())
        item(abs(ia - 100) < 0.01, f"{ano}: índices aplicados somam 100 ({ia:.4f})")
    reg = {2024: 34375560.80, 2025: 21083973.89, 2026: 46635585.04}
    for ano, ref in reg.items():
        s = sum(v for v in valor("vaar_valor", ano).values() if pd.notna(v))
        item(abs(s - ref) < 0.01, f"VAAR {ano}: soma das redes municipais de MS R$ {br(s)} = total registrado no LOG do 04_dados (R$ {br(ref)})")
    # Fundeb: líquido = bruto + dedução (dedução vem negativa no arquivo)
    f = IND[IND["indicador"].str.match(r"fundeb_.+_(bruto|deducao|liquido)$")
            & ~IND["indicador"].str.startswith(("fundeb_total_", "fundeb_exerc_"))].copy()
    f["origem"] = f["indicador"].str.rsplit("_", n=1).str[0]
    f["tipo"] = f["indicador"].str.rsplit("_", n=1).str[1]
    pv = f.pivot_table(index=["cod_ibge", "ano", "origem"], columns="tipo", values="valor", aggfunc="first").dropna()
    mx = (pv["bruto"] + pv["deducao"] - pv["liquido"]).abs().max()
    item(mx < 0.02, f"Fundeb (FNDE): valor bruto + dedução = valor líquido em todas as {len(pv)} linhas (diferença máxima R$ {mx:.2f})")
    # DCA I-E × MSC (função 12, empenhada)
    dca, msc = IND[IND["indicador"] == "educ_dca_empenhada"], IND[IND["indicador"] == "educ_msc_empenhada_total"]
    m = dca.merge(msc, on=["cod_ibge", "ano"], suffixes=("_dca", "_msc"))
    m["dif"] = (m["valor_dca"] - m["valor_msc"]).abs()
    ok = (m["dif"] <= 1.0).sum()
    item(ok == len(m), f"Siconfi: despesa empenhada em Educação da MSC = DCA Anexo I-E em {ok} de {len(m)} município-ano "
         f"(diferença até R$ 1,00)", obrigatoria=False)
    if ok < len(m):
        R.append("\n  Município-ano com diferença (a página de condições materiais mostra os dois valores):\n")
        for _, r in m[m["dif"] > 1.0].sort_values("dif", ascending=False).head(15).iterrows():
            R.append(f"  - {r['municipio_dca']} {r['ano']}: DCA R$ {br(r['valor_dca'])}; MSC R$ {br(r['valor_msc'])}")
    # Fundeb: VAAR devido no exercício de 2025 (FNDE, Portaria 5/2026) × VAAR após ajuste de 2025 (04_dados)
    a, b = valores_nn("fundeb_exerc_vaar", 2025), valores_nn("vaar_valor_apos_ajuste", 2025)
    dif = [c for c in b if c in a and abs(a[c] - b[c]) > 0.01]
    item(len(a) == 79 and not dif, f"VAAR do exercício de 2025 na tabela de receita total do FNDE (Portaria nº 5/2026) = VAAR "
         f"após ajuste do 04_dados em {79 - len(dif)} de 79 municípios", obrigatoria=False)
    for ano, ex, bb, rot in ((2025, "fundeb_exerc_total", "fundeb_total_bruto", "total"),
                             (2025, "fundeb_exerc_contribuicao", "fundeb_receita_de_contribuicoes_bruto", "receita da contribuição"),
                             (2025, "fundeb_exerc_vaat", "fundeb_complementacao_vaat_bruto", "VAAT"),
                             (2025, "fundeb_exerc_vaar", "fundeb_complementacao_vaar_bruto", "VAAR"),
                             (2024, "fundeb_exerc_vaat", "fundeb_complementacao_vaat_bruto", "VAAT")):
        a, b = valores_nn(ex, ano), valores_nn(bb, ano)
        cs = [c for c in a if c in b]
        sa, sb = sum(a[c] for c in cs), sum(b[c] for c in cs)
        n1 = sum(1 for c in cs if b[c] and abs(a[c] / b[c] - 1) > 0.01) + sum(1 for c in cs if not b[c] and a[c])
        item(True, f"Fundeb {ano}, {rot}: devido no exercício R$ {br(sa)} × pago no ano civil R$ {br(sb)} "
             f"({br((sa / sb - 1) * 100 if sb else 0)}%); municípios com diferença acima de 1%: {n1} de {len(cs)} "
             "(informativo: as fontes medem coisas diferentes)", obrigatoria=False)
    # matrículas: soma das escolas (Iquems) × sinopse (04_dados), 2024
    a, b = valor("mat_municipal_censo_escolas", 2024), valor("mat_municipal_sinopse_censo", 2024)
    iguais = sum(1 for c in b if c in a and abs(a[c] - b[c]) < 0.5)
    item(iguais == len(b), f"Matrículas da rede municipal 2024: soma das escolas (painel do Iquems) = sinopse (04_dados) em {iguais} de {len(b)} municípios",
         obrigatoria=False)
    # Fundeb 2024: arquivo do 04_dados × "2024 (1)" publicado depois no portal
    p1 = BRUTOS / "fnde_fundeb" / "Valores repassados pelo Banco do Brasil por ente federado e origem de receita - Exercício de 2024 (1).xlsx"
    if p1.exists():
        raw = pd.read_excel(p1, header=None)
        lin = raw.index[raw.iloc[:, 0].astype(str).str.strip().eq("UF")][0]
        d = raw.iloc[lin + 2:]
        d = d[d.iloc[:, 0].astype(str).str.strip().eq("MS")]
        cod = d.iloc[:, 2].astype(str).str.replace(r"\.0$", "", regex=True)
        liq = d.iloc[:, [5, 8, 11, 14]].apply(pd.to_numeric, errors="coerce").sum(axis=1)
        ref = dict(zip(cod, liq))
        base = valor("fundeb_total_liquido", 2024)
        dif = [c for c in base if c in ref and abs(base[c] - ref[c]) > 0.01]
        item(not dif, f"Fundeb 2024: o arquivo '2024 (1)' do portal tem o mesmo total líquido do arquivo usado em "
             f"{79 - len(dif)} dos 79 municípios" + (f"; diferem: {len(dif)}" if dif else ""), obrigatoria=False)


# ------------------------------------------------------------------ 4. releitura na fonte
def conf_fonte():
    secao("5. Amostra de valores novos relida direto na fonte original")
    import requests
    import truststore
    truststore.inject_into_ssl()
    amostra = [("5007976", 2023), ("5002704", 2022), ("5003702", 2024)]
    for cod, ano in amostra:
        try:
            r = requests.get("https://apidatalake.tesouro.gov.br/ords/siconfi/tt/dca",
                             params={"an_exercicio": ano, "no_anexo": "DCA-Anexo I-E", "id_ente": cod}, timeout=120).json()
            v = sum(x["valor"] for x in r["items"] if x["conta"].startswith("12 - ") and x["coluna"] == "Despesas Empenhadas"
                    and x["rotulo"] == "Total Geral da Despesa por Função")
            b = valor("educ_dca_empenhada", ano).get(cod)
            item(b is not None and abs(v - b) < 0.01, f"Siconfi (consulta ao vivo) DCA {ano} I-E, Educação empenhada, {cod}: "
                 f"API R$ {br(v)} × painel R$ {b if b is None else br(b)}", obrigatoria=False)
        except Exception as ex:  # noqa: BLE001
            item(False, f"Siconfi indisponível para a releitura ({cod} {ano}): {ex}", obrigatoria=False)
    try:
        r = requests.get("https://apisidra.ibge.gov.br/values/t/5938/n6/5002209/v/37/p/2023", timeout=60).json()
        v = float(r[1]["V"]) * 1000
        b = valor("pib", 2023).get("5002209")
        item(abs(v - b) < 1, f"IBGE (consulta ao vivo) PIB 2023 de Bonito: R$ {br(v, 0)} × painel R$ {br(b, 0)}", obrigatoria=False)
    except Exception as ex:  # noqa: BLE001
        item(False, f"IBGE indisponível para a releitura: {ex}", obrigatoria=False)
    p = BRUTOS / "fnde_fundeb" / "Valores repassados pelo Banco do Brasil por ente federado e origem de receita - Exercício de 2022.xlsx"
    wb = openpyxl.load_workbook(p, read_only=True, data_only=True)
    for row in wb.worksheets[0].iter_rows(values_only=True):
        if row and str(row[2]).startswith("5003702"):
            v = row[5]
            b = valor("fundeb_receita_de_contribuicoes_liquido", 2022).get("5003702")
            item(abs(v - b) < 0.01, f"FNDE (planilha original, outra biblioteca de leitura) Fundeb 2022 de Dourados, receita de "
                 f"contribuições líquida: R$ {br(v)} × painel R$ {br(b)}", obrigatoria=False)
            break
    c = IND[(IND["indicador"] == "infra_n_escolas") & (IND["ano"] == 2025)]["valor"].sum()
    item(True, f"Censo 2025: {c:.0f} escolas municipais em atividade nos 79 municípios (contagem dos microdados)", obrigatoria=False)


# ------------------------------------------------------------------ 5. ranking provisório
def conf_ranking():
    secao("6. Ordenamento do script 09 (usado no painel) × ranking provisório (xlsx feito fora do pipeline)")
    p = FONTE_AB / "saidas" / "ranking_provisorio_icms_vaar_ms.xlsx"
    wb = openpyxl.load_workbook(p, data_only=True, read_only=True)
    rows = list(wb["Ranking"].iter_rows(values_only=True))
    cab = rows[3]
    d = pd.DataFrame([r for r in rows[4:] if r and r[2]], columns=cab)
    d["Código IBGE"] = d["Código IBGE"].astype(str)
    m = ORD.merge(d, left_on="cod_ibge", right_on="Código IBGE", how="outer")
    pos_dif = m[m["posicao"] != m["Posição"]]
    m["dif_acum"] = (m["acumulado_2024_2025"] - m["Acumulado (R$/matrícula)"]).abs()
    R.append(f"\nArquivo: `{p.relative_to(FONTE_AB.parent.parent)}` (versão de 09/11/2026, 12h45; o Leia-me dele diz 'versão de 04/11/2026').")
    item(len(d) == 79, f"o ranking provisório tem {len(d)} municípios", obrigatoria=False)
    item(pos_dif.empty, f"posições iguais ao ordenamento do script 09 em {79 - len(pos_dif)} dos 79 municípios", obrigatoria=False)
    item(m["dif_acum"].max() < 1e-6, f"acumulado 2024+2025 igual em todos (maior diferença {m['dif_acum'].max():.2e} R$/matrícula)", obrigatoria=False)
    sel = m[["cod_ibge", "municipio", "selecao_principal", "Seleção principal"]].copy()
    sel["a"] = sel["selecao_principal"].fillna("")
    sel["b"] = sel["Seleção principal"].fillna("")
    dsel = sel[sel["a"] != sel["b"]]
    item(dsel.empty, "seleção principal: mesma marcação nos dois arquivos" + ("" if dsel.empty else f" — diferem: {dsel[['municipio', 'a', 'b']].values.tolist()}"),
         obrigatoria=False)
    if not pos_dif.empty:
        R.append("\n| município | posição (script 09) | posição (ranking provisório) |\n|---|---|---|")
        for _, r in pos_dif.iterrows():
            R.append(f"| {r['municipio']} | {r['posicao']} | {r['Posição']} |")
    R.append("\nO ranking provisório também traz a aba 'Comparativo Fundeb' (ICMS Educacional por matrícula × Fundeb), que "
             "não existe no pipeline; o painel não a usa. Para o ranking ficar reprodutível, é preciso transformar em script "
             "o que foi feito nele (pendência registrada no 04_dados).")


def main():
    R.append(f"# Conferência da base do painel\n\nGerado por `tratamento/conferir.py` em {datetime.now():%d/%m/%Y %H:%M}. "
             "OK = conferência cumprida; FALHA = conferência obrigatória não cumprida; AVISO = diferença registrada que não "
             "impede o uso (explicada no texto).")
    for f in (conf_79, conf_csv, conf_xlsx, conf_somas, conf_fonte, conf_ranking):
        try:
            f()
        except Exception as ex:  # noqa: BLE001
            item(False, f"{f.__name__} não rodou: {ex!r}")
    secao("Resumo")
    R.append(f"- Divergências nos objetivos a e b (painel × CSVs × planilha): **{len(DIVS)}**")
    R.append(f"- Falhas em conferências obrigatórias: **{len(FALHAS)}**" + ("".join(f"\n  - {x}" for x in FALHAS)))
    DOCS.mkdir(parents=True, exist_ok=True)
    (DOCS / "conferencia.md").write_text("\n".join(R) + "\n", encoding="utf-8")
    pd.DataFrame(DIVS, columns=["conferencia", "cod_ibge", "painel", "referencia"]).to_csv(
        DOCS / "conferencia_divergencias.csv", index=False, encoding="utf-8-sig")
    print("\n".join(x for x in R if x.startswith(("- FALHA", "- AVISO", "- Diverg", "- Falhas"))))
    print(f"[conferir] divergências a/b: {len(DIVS)}; falhas obrigatórias: {len(FALHAS)}")
    return 1 if (DIVS or FALHAS) else 0


if __name__ == "__main__":
    sys.exit(main())
