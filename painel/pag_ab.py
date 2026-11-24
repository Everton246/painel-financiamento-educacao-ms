"""Páginas dos objetivos a e b: ICMS Educacional, IQE-MS, VAAR, Indicador e seleção.
Todos os números vêm de dados/base (lidos de 04_dados_ICMS_IQE_VAAR, sem recálculo)."""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import identidade
import textos
from dados import COR_DESEMP, COR_ESTR, COR_NEG, COR_POS, COR_SEL, CORES, SEM_DADO, legenda_fonte, mostrar_grafico, numero
from estado import (AT, CAT, IND, NOME, ORD, PORTE, SEL_A, SEL_P, aviso_2026, descricao_recorte, fontes_de, largo, mapa,
                    recorte, reais, sem_dado, serie, tabela, textos_at, valores)
from identidade import como_ler

ICMS_COLS = ["icms_repasse_total", "icms_iqe_coef", "icms_iqe_part", "icms_educacional", "icms_contrafactual",
             "icms_ganho_perda", "icms_estrutural", "icms_desempenho", "icms_checagem"]


def _destaque(cods):
    m = st.session_state.get("f_mun")
    return [("#000000" if c == m else "rgba(0,0,0,0)") for c in cods]


# ------------------------------------------------------------------------------------------------ ICMS

def pagina_icms():
    st.title("ICMS Educacional (objetivo a)")
    como_ler("icms", CAT, ["icms_educacional", "icms_ganho_perda", "icms_estrutural", "icms_desempenho"])
    ano = st.session_state["f_ano"]
    aviso_2026(ano)
    cods = recorte(ano)
    st.markdown(descricao_recorte(ano))
    if ano == 2026:
        _icms_2026(cods)
        return
    P = valores("icms_parcela_educacional_total", ano).get("50")
    ganho = valores("icms_ganho_perda", ano)
    est_cov = valores("icms_parte_estrutural_cov", ano).get("50")
    identidade.cartoes([
        (f"ICMS Educacional distribuído em {ano} (P)", reais(P, 0), "Soma dos 79; 10% da soma dos repasses de ICMS"),
        ("Municípios com ganho", str(sum(1 for v in ganho.values() if v > 0)), f"de 79 · exercício {ano}"),
        ("Municípios com perda", str(sum(1 for v in ganho.values() if v < 0)), f"de 79 · exercício {ano}"),
        ("Parte do ganho/perda explicada pelo componente estrutural",
         None if est_cov is None else numero(est_cov * 100, 1, fixo=True) + "%", "Decomposição por covariância (04_dados)"),
    ])
    st.subheader(f"Ganho ou perda por município, {ano}")
    t = largo(ICMS_COLS, ano, cods)
    t = t.sort_values(t.columns[7], ascending=False)
    fig = go.Figure()
    for ind, cor, rot in (("icms_estrutural", COR_ESTR, "Componente estrutural"), ("icms_desempenho", COR_DESEMP, "Componente de desempenho")):
        v = valores(ind, ano)
        fig.add_bar(x=[NOME[c] for c in t["cod_ibge"]], y=[v.get(c) for c in t["cod_ibge"]], name=rot, marker_color=cor)
    g = valores("icms_ganho_perda", ano)
    fig.add_scatter(x=[NOME[c] for c in t["cod_ibge"]], y=[g.get(c) for c in t["cod_ibge"]], mode="markers", name="Ganho ou perda (total)",
                    marker=dict(color="#000000", symbol="diamond", size=7))
    fig.update_layout(barmode="relative", title=f"Ganho ou perda no ICMS Educacional e seus componentes, {ano} (R$)", height=520,
                      xaxis=dict(tickangle=-60, tickfont=dict(size=9)), yaxis_title="R$")
    mostrar_grafico(fig, f"icms_ganho_perda_{ano}", f"icms_bar_{ano}", dados=t.drop(columns=["cod_ibge"]))
    legenda_fonte(fontes_de(["icms_ganho_perda"], [ano], cods), CAT, "icms_ganho_perda")
    st.caption("Barras: componente estrutural (azul) e de desempenho (laranja), empilhados; losango: o total. Estrutural + "
               "desempenho = ganho ou perda (coluna de conferência na tabela abaixo, sempre ≈ 0). Os três municípios com mais de "
               "100 mil habitantes dominam a escala (componente estrutural muito negativo): para ver os demais, use o "
               "filtro de porte.")
    st.subheader("Tabela dos municípios")
    tabela(t, f"icms_{ano}", f"icms_tab_{ano}", fontes_de(ICMS_COLS, [ano], cods))
    st.subheader("Mapa")
    opc = {"icms_ganho_perda": "Ganho ou perda (R$)", "icms_desempenho": "Componente de desempenho (R$)",
           "icms_estrutural": "Componente estrutural (R$)", "icms_educacional": "ICMS Educacional (R$)"}
    ind = st.selectbox("Indicador do mapa", list(opc), format_func=opc.get, key="icms_mapa_ind")
    v = {c: x for c, x in valores(ind, ano).items() if c in cods}
    mapa(v, f"{opc[ind]}, {ano}", f"mapa_{ind}_{ano}", f"icms_mapa_{ano}", divergente=ind != "icms_educacional",
         fonte_df=fontes_de([ind], [ano], cods), indicador=ind)
    st.subheader("Componente estrutural × componente de desempenho")
    e, d = valores("icms_estrutural", ano), valores("icms_desempenho", ano)
    fig = go.Figure(go.Scatter(x=[e.get(c) for c in cods], y=[d.get(c) for c in cods], mode="markers",
                               text=[NOME[c] for c in cods], hovertemplate="%{text}<br>estrutural R$ %{x:,.0f}<br>desempenho R$ %{y:,.0f}<extra></extra>",
                               marker=dict(color=CORES["azul"], size=8, line=dict(color=_destaque(cods), width=2))))
    fig.update_layout(title=f"Estrutural × desempenho, {ano} (R$)", xaxis_title="Componente estrutural (R$)",
                      yaxis_title="Componente de desempenho (R$)", height=460)
    mostrar_grafico(fig, f"icms_estrutural_desempenho_{ano}", f"icms_disp_{ano}")
    st.caption("O componente estrutural varia muito mais que o de desempenho: os coeficientes do IQE-MS variam em faixa "
               "estreita, e o resultado em reais depende sobretudo do porte econômico (valor adicionado).")
    st.subheader(f"Comparação: resolução da Sefaz × regra de normalização, {ano}")
    st.markdown("A pesquisa calcula o ICMS Educacional pela resolução da Sefaz (índice IQE / índice aplicado). A regra de "
                "normalização (participação no IQE × 10% × soma dos repasses) foi a premissa de setembro de 2026; as duas "
                "ficam lado a lado para mostrar que a diferença é de arredondamento.")
    c = largo(["icms_educacional", "icms_educacional_normalizacao", "icms_dif_resolucao_normalizacao",
               "icms_dif_resolucao_normalizacao_pct", "icms_ganho_perda", "icms_ganho_perda_normalizacao"], ano, cods)
    tabela(c, f"icms_comparacao_{ano}", f"icms_comp_{ano}", fontes_de(["icms_educacional_normalizacao"], [ano], cods))


def _icms_2026(cods):
    st.markdown("Para 2026 já há os **índices** da Resolução/SEFAZ nº 3.484/2025 e o IQE-MS do ano-base 2024, mas **não o "
                "repasse anual** (sai no início de 2027). Por isso o painel mostra só a participação e o componente de "
                "desempenho em pontos percentuais do total repassado aos 79; valores em reais: **sem dado** até lá.")
    cols = ["icms_iqe_coef", "icms_iqe_part", "icms_iqe_indice", "icms_indice_aplicado", "icms_desempenho_pct_total",
            "icms_desempenho_pct_total_normalizacao"]
    t = largo(cols, 2026, cods).sort_values(largo(cols, 2026, cods).columns[6], ascending=False)
    tabela(t, "icms_2026_parcial", "icms_tab_2026", fontes_de(cols, [2026], cods))
    v = {c: x for c, x in valores("icms_desempenho_pct_total", 2026).items() if c in cods}
    mapa(v, "2026 (provisório): desempenho em p.p. do total", "mapa_desempenho_2026", "icms_mapa_2026", divergente=True,
         sufixo=" p.p.", casas=4, fonte_df=fontes_de(["icms_desempenho_pct_total"], [2026], cods), indicador="icms_desempenho_pct_total")


# ------------------------------------------------------------------------------------------------ IQE-MS

def pagina_iqe():
    st.title("IQE-MS: coeficientes, casos especiais e participação no SAEMS")
    como_ler("iqe", CAT, ["iqe_coef", "saems2_participacao_lp"])
    ano = st.session_state["f_ano"]
    cods = recorte(ano)
    st.markdown(descricao_recorte(ano) + f" O filtro de situação no IQE-MS usa o ano-base {ano - 2} (repasse de {ano}).")
    st.subheader("Coeficiente final por ano-base")
    t = pd.DataFrame({"cod_ibge": cods, "Município": [NOME[c] for c in cods]})
    for ab in (2022, 2023, 2024):
        t[f"Coeficiente {ab} (repasse {ab + 2})"] = t["cod_ibge"].map(valores("iqe_coef", ab))
    t["Coeficiente 2025 (repasse 2027)"] = None
    tabela(t, "iqe_coeficientes", "iqe_tab", fontes_de(["iqe_coef"], [2022, 2023, 2024], cods))
    st.caption("Ano-base 2025: só há o resultado PRELIMINAR (DOE/MS nº 12.162, de 20/05/2026), que não foi extraído pela "
               "base da pesquisa; o final ainda não está nas pastas — **sem dado**.")
    fig = go.Figure()
    for c in cods:
        y = [valores("iqe_coef", ab).get(c) for ab in (2022, 2023, 2024)]
        dest = c == st.session_state.get("f_mun")
        fig.add_scatter(x=["2022", "2023", "2024"], y=y, mode="lines+markers", name=NOME[c], showlegend=dest,
                        line=dict(color="#000000" if dest else "rgba(0,79,159,0.25)", width=3 if dest else 1))
    fig.update_layout(title="Coeficiente do IQE-MS por ano-base (cada linha é um município)", xaxis_title="Ano-base",
                      yaxis_title="Coeficiente", height=440)
    mostrar_grafico(fig, "iqe_coeficientes", "iqe_linhas", dados=t.drop(columns=["cod_ibge"]))
    st.subheader("Coeficiente mínimo e resultado incompleto, com o texto das notas dos editais")
    linhas = []
    for ab in (2022, 2023, 2024):
        mn, sr = textos_at("iqe_coef_minimo", ab), textos_at("iqe_sem_resultado_completo", ab)
        nm, nt = textos_at("iqe_nota_marca", ab), textos_at("iqe_nota_texto", ab)
        for c in cods:
            if mn.get(c) == "sim" or sr.get(c) == "sim" or nm.get(c):
                linhas.append({"cod_ibge": c, "Município": NOME[c], "Ano-base": ab, "Repasse afetado": ab + 2,
                               "Coeficiente": valores("iqe_coef", ab).get(c), "Coeficiente mínimo do ano": mn.get(c, ""),
                               "Sem resultado completo": sr.get(c, ""), "Nota (marca)": nm.get(c, ""), "Texto da nota no edital": nt.get(c, "") or "—"})
    if linhas:
        tabela(pd.DataFrame(linhas), "iqe_casos", "iqe_casos", fontes_de(["iqe_coef"], [2022, 2023, 2024], cods))
        st.caption("Critério descritivo (04_dados, sessão 4): mínimo = igual ao menor coeficiente do ano; sem resultado "
                   "completo = linha com até 3 valores. Em 2024, Maracaju e Sidrolândia têm o mínimo e linha incompleta SEM "
                   "nota no edital; Dois Irmãos do Buriti tem nota ¹ em 2024, mas coeficiente normal.")
    else:
        sem_dado("nenhum caso no recorte escolhido.")
    st.subheader("Participação e proficiência das redes municipais no SAEMS, 2º ano (insumo do IQE-MS)")
    disc = st.radio("Componente", ["lp", "lp_escrita"], horizontal=True, key="iqe_disc",
                    format_func={"lp": "Língua Portuguesa (leitura)", "lp_escrita": "Língua Portuguesa (escrita)"}.get)
    anos = [2022, 2023, 2024, 2025]
    t = pd.DataFrame({"cod_ibge": cods, "Município": [NOME[c] for c in cods]})
    for a in anos:
        t[f"Participação {a} (%)"] = t["cod_ibge"].map(valores(f"saems2_participacao_{disc}", a))
    for a in anos:
        t[f"Proficiência {a} (escala SAEMS)"] = t["cod_ibge"].map(valores(f"saems2_proficiencia_{disc}", a))
    tabela(t, f"saems_2ano_{disc}", "iqe_saems", fontes_de([f"saems2_participacao_{disc}", f"saems2_proficiencia_{disc}"], anos, cods))
    a_sel = ano - 2 if ano - 2 in anos else 2024
    p = valores(f"saems2_participacao_{disc}", a_sel)
    q = valores("iqe_coef", a_sel)
    fig = go.Figure(go.Scatter(x=[p.get(c) for c in cods], y=[q.get(c) for c in cods], mode="markers", text=[NOME[c] for c in cods],
                               hovertemplate="%{text}<br>participação %{x:.1f}%<br>coeficiente %{y:.5f}<extra></extra>",
                               marker=dict(color=CORES["azul"], size=8, line=dict(color=_destaque(cods), width=2))))
    fig.add_vline(x=80, line_dash="dash", line_color=COR_NEG, annotation_text="80%", annotation_position="top")
    fig.update_layout(title=f"Participação no SAEMS (2º ano, rede municipal) × coeficiente do IQE-MS, ano-base {a_sel}",
                      xaxis_title="Participação no SAEMS (%) — CAEd/UFJF, área pública", yaxis_title="Coeficiente do IQE-MS", height=460)
    mostrar_grafico(fig, f"iqe_participacao_{a_sel}", "iqe_part_disp")
    st.caption("A participação mostrada é a publicada na área pública do SAEMS; a SED pode ter usado outra taxa (o LOG do "
               "04_dados registra 0,79 para Maracaju e 0,78 para Sidrolândia em 2024). Proficiência do SAEMS: escala própria, "
               "nunca comparada ao Saeb.")
    st.subheader("Nível socioeconômico (Inse) da rede municipal")
    t = pd.DataFrame({"cod_ibge": cods, "Município": [NOME[c] for c in cods]})
    for a in (2019, 2021, 2023):
        t[f"Inse médio {a}"] = t["cod_ibge"].map(valores("inse_media", a))
    tabela(t, "inse_rede_municipal", "iqe_inse", fontes_de(["inse_media"], [2019, 2021, 2023], cods))


# ------------------------------------------------------------------------------------------------ VAAR

def pagina_vaar():
    st.title("VAAR: habilitação, condicionalidades e valores (objetivo b)")
    como_ler("vaar", CAT, ["vaar_valor", "vaar_por_mat"])
    ano = st.session_state["f_ano"]
    aviso_2026(ano)
    cods = recorte(ano)
    st.markdown(descricao_recorte(ano))
    sit = textos_at("vaar_situacao_vaar", ano)
    hab = textos_at("vaar_habilitado", ano)
    val = valores("vaar_valor", ano)
    identidade.cartoes([
        (f"Redes habilitadas ({ano})", str(sum(1 for c in NOME if hab.get(c) == "sim")), "Listas do FNDE (79 redes municipais)"),
        (f"Redes beneficiadas ({ano})", str(sum(1 for c in NOME if (val.get(c) or 0) > 0)), "Valor > 0 no anexo de redes beneficiadas"),
        (f"VAAR das redes municipais ({ano})" + (" – previsto" if ano == 2026 else ""), reais(sum(v for v in val.values() if pd.notna(v)), 0),
         "Portaria 11/2026 (previsto)" if ano == 2026 else "Anexo V da portaria do exercício"),
        ("Inabilitados na lista que receberam", str(sum(1 for c in NOME if hab.get(c) == "não" and (val.get(c) or 0) > 0)),
         "Todos com inclusão tardia: " + (", ".join(NOME[c] for c in NOME if "tardiamente" in (sit.get(c) or "")) or "nenhum")),
    ])
    st.subheader(f"Situação de cada rede municipal, {ano}")
    t = pd.DataFrame({"cod_ibge": cods, "Município": [NOME[c] for c in cods]})
    t["Situação"] = t["cod_ibge"].map(sit)
    t["Habilitado (lista FNDE)"] = t["cod_ibge"].map(hab)
    for k in ("I", "II", "III", "IV", "V"):
        t[f"Cond. {k}"] = t["cod_ibge"].map(textos_at(f"vaar_cond_{k}_cumpriu", ano))
    t["Condicionalidades descumpridas"] = t["cod_ibge"].map(textos_at("vaar_condicionalidades_descumpridas", ano))
    t["Evoluiu nos indicadores"] = t["cod_ibge"].map(textos_at("vaar_evoluiu_indicadores", ano))
    for ind in ("vaar_valor", "vaar_por_mat", "vaar_valor_apos_ajuste", "mat_rede_municipal_sinopse"):
        t[ind] = t["cod_ibge"].map(valores(ind, ano))
    t = t.rename(columns={"vaar_valor": "VAAR (R$)" + (" previsto" if ano == 2026 else ""), "vaar_por_mat": "VAAR por matrícula (R$)",
                          "vaar_valor_apos_ajuste": "VAAR após ajuste (R$)", "mat_rede_municipal_sinopse": "Matrículas da rede municipal"})
    tabela(t, f"vaar_{ano}", f"vaar_tab_{ano}", fontes_de(["vaar_valor", "vaar_por_mat"], [ano], cods))
    st.caption("Cond. I: gestor escolar por mérito/desempenho ou com participação da comunidade; II: participação ≥ 80% no "
               "Saeb; III: redução das desigualdades; IV: ICMS Educacional em lei estadual (regime de colaboração); V: "
               "referenciais curriculares alinhados à BNCC (Lei nº 14.113/2020, art. 14, § 1º). 2025: lista de inabilitados "
               "versão B (decisão do autor; na versão A só Anaurilândia muda).")
    st.subheader("Condicionalidades descumpridas (contagem de redes)")
    cont = {k: sum(1 for c in cods if textos_at(f"vaar_cond_{k}_cumpriu", ano).get(c) == "não") for k in ("I", "II", "III", "IV", "V")}
    fig = go.Figure(go.Bar(x=[f"Cond. {k}" for k in cont], y=list(cont.values()), marker_color=COR_NEG, text=list(cont.values()),
                           textposition="outside"))
    fig.update_layout(title=f"Redes municipais que descumpriram cada condicionalidade, {ano} (recorte)", yaxis_title="redes", height=380)
    mostrar_grafico(fig, f"vaar_condicionalidades_{ano}", f"vaar_cond_{ano}",
                    dados=pd.DataFrame({"condicionalidade": list(cont), "redes que descumpriram": list(cont.values())}))
    st.caption(f"Fonte: FNDE, listas de redes inabilitadas por motivo e de beneficiários ({ano}), via 04_dados (07_vaar.csv).")
    st.subheader("Mapa")
    opc = {"vaar_por_mat": "VAAR por matrícula (R$)", "vaar_valor": "VAAR (R$)"}
    ind = st.selectbox("Indicador do mapa", list(opc), format_func=opc.get, key="vaar_mapa_ind")
    mapa({c: x for c, x in valores(ind, ano).items() if c in cods}, f"{opc[ind]}, {ano}", f"mapa_{ind}_{ano}", f"vaar_mapa_{ano}",
         fonte_df=fontes_de([ind], [ano], cods), indicador=ind)
    st.subheader("Ideb e Saeb da rede municipal (contexto das condicionalidades II e III)")
    st.markdown("O Inep afere a participação no Saeb (cond. II) e a redução das desigualdades (cond. III) a partir do Saeb. "
                "Abaixo, o Ideb e a proficiência no Saeb da rede municipal, por edição. Os indicadores próprios do VAAR "
                "(atendimento e aprendizagem, planilha do Inep para 2026) estão em 04_dados e ainda não entram no painel.")
    etapa = st.radio("Etapa", ["ai", "af"], horizontal=True, key="vaar_etapa",
                     format_func={"ai": "Anos iniciais do EF", "af": "Anos finais do EF"}.get)
    ed = [2019, 2021, 2023, 2025]
    t = pd.DataFrame({"cod_ibge": cods, "Município": [NOME[c] for c in cods]})
    for a in ed:
        t[f"Ideb {a}"] = t["cod_ibge"].map(valores(f"ideb_ef_{etapa}", a))
    for a in ed:
        t[f"Saeb LP {a}"] = t["cod_ibge"].map(valores(f"saeb_proficiencia_lp_ef_{etapa}", a))
    for a in ed:
        t[f"Saeb MT {a}"] = t["cod_ibge"].map(valores(f"saeb_proficiencia_mt_ef_{etapa}", a))
    tabela(t, f"ideb_saeb_{etapa}", f"vaar_ideb_{etapa}",
           fontes_de([f"ideb_ef_{etapa}", f"saeb_proficiencia_lp_ef_{etapa}"], ed, cods))
    st.caption("Escala do Saeb/Ideb (Inep), nunca comparada ao SAEMS. Rede municipal sem Ideb na edição = *sem dado* "
               "(ex.: participação insuficiente ou poucos estudantes). Fonte: Inep, via base do painel do Iquems.")
    st.subheader("Tabelas de contingência: VAAR × ICMS Educacional e IQE-MS")
    st.markdown("Contagem de municípios (todos os 79; o recorte dos filtros não se aplica, porque as tabelas são as do "
                "04_dados). Estatística descritiva: os 79 são a população inteira.")
    _contingencia(ano)


def _contingencia(ano):
    from dados import BASE
    if ano == 2026:
        sem_dado("as tabelas de contingência do 04_dados cobrem 2024 e 2025 (em 2026 não há ganho ou perda em reais).")
        return
    c = pd.read_parquet(BASE / "contingencia.parquet")
    c = c[c["ano"] == ano]
    rot = {"habilitado_contingencia": "Habilitado (contingência)", "beneficiado": "Beneficiado"}
    for var in c["variavel_vaar"].unique():
        d = c[c["variavel_vaar"] == var]
        pv = d.pivot_table(index="valor_vaar", columns=["variavel_icms", "categoria_icms"], values="municipios", aggfunc="sum", fill_value=0)
        pv.columns = [f"{a.replace('icms_resultado', 'ICMS Educ.').replace('iqe_posicao', 'IQE-MS')}: {b}" for a, b in pv.columns]
        pv = pv.reset_index().rename(columns={"valor_vaar": rot.get(var, var.replace("_cumpriu", " cumprida").replace("cond_", "Cond. "))})
        st.markdown(f"**{rot.get(var, var.replace('_cumpriu', ' cumprida').replace('cond_', 'Cond. '))}**")
        st.dataframe(pv, hide_index=True, use_container_width=True)
    g = pd.read_parquet(BASE / "comparacao_grupos.parquet")
    g = g[g["ano"] == ano]
    st.markdown("**Comparação entre grupos (médias)**")
    tabela(g.rename(columns={"grupo": "variável", "valor": "grupo", "municipios": "municípios"}).drop(columns=["ano"]),
           f"vaar_grupos_{ano}", f"vaar_grupos_{ano}", clicavel=False)
    st.caption(f"Fonte: 04_dados_ICMS_IQE_VAAR/dados_processados/09_contingencia.csv e 09_comparacao_grupos.csv (script 09), {ano}. "
               "Antônio João conta como habilitado em 2024 e 2025 (decisão do autor); as condicionalidades individuais seguem a lista.")


# ------------------------------------------------------------------------------------------------ Indicador e seleção

def pagina_indicador():
    st.title("Indicador de seleção e ordenamento dos 79 municípios")
    st.warning(textos.ORDENAMENTO_NAO_E_QUALIDADE, icon="ℹ️")
    como_ler("indicador", CAT, ["indicador_selecao"])
    cods = recorte(2025)
    st.markdown(descricao_recorte())
    o = ORD[ORD["cod_ibge"].isin(cods)].sort_values("posicao")
    t = pd.DataFrame({"cod_ibge": o["cod_ibge"], "Posição": o["posicao"], "Município": o["municipio"],
                      "População 2022": o["populacao_2022"], "Porte": o["porte"],
                      "Desempenho ICMS/mat. 2024": o["desemp_por_mat_2024"], "VAAR/mat. 2024": o["vaar_por_mat_2024"],
                      "Indicador 2024": o["indicador_2024"], "Desempenho ICMS/mat. 2025": o["desemp_por_mat_2025"],
                      "VAAR/mat. 2025": o["vaar_por_mat_2025"], "Indicador 2025": o["indicador_2025"],
                      "Acumulado 2024+2025 (R$/mat.)": o["acumulado_2024_2025"],
                      "Posição com VAAR após ajuste": o["posicao_ajust"],
                      "Posição com VAAR 2026 previsto (provisório)": o["posicao_com_vaar2026_prov"],
                      "Seleção principal": o["selecao_principal"], "Seleção alternativa": o["selecao_alternativa"],
                      "IQE-MS: mínimo ou sem resultado": o["iqe_minimo_ou_sem_resultado"]})
    st.subheader("Ordenamento (indicador acumulado 2024 + 2025)")
    fig = go.Figure()
    cor = []
    for c in o["cod_ibge"]:
        cor.append(COR_SEL["ambas"] if c in SEL_P and c in SEL_A else COR_SEL["principal"] if c in SEL_P else
                   COR_SEL["alternativa"] if c in SEL_A else "#BFC7D1")
    fig.add_bar(x=o["municipio"], y=o["acumulado_2024_2025"], marker_color=cor,
                customdata=o[["posicao"]], hovertemplate="%{x} (%{customdata[0]}º)<br>R$ %{y:,.2f} por matrícula<extra></extra>")
    fig.update_layout(title="Indicador acumulado 2024 + 2025 (R$ por matrícula da rede municipal)", height=520,
                      xaxis=dict(tickangle=-60, tickfont=dict(size=9)), yaxis_title="R$ por matrícula")
    mostrar_grafico(fig, "indicador_ordenamento", "ind_bar", dados=t.drop(columns=["cod_ibge"]))
    st.caption("Azul: seleção principal; amarelo-escuro: alternativa; roxo: nas duas; cinza: nenhuma. Fonte: 04_dados, "
               "scripts/09_indicador.py (09_indicador_ordenamento.csv). O componente estrutural não entra no indicador.")
    tabela(t, "indicador_ordenamento", "ind_tab", fontes_de(["indicador_selecao"], [2024, 2025], cods))
    st.subheader("As duas seleções de campo")
    c1, c2 = st.columns(2)
    for col, campo, tit in ((c1, "selecao_principal", "Principal (por porte)"), (c2, "selecao_alternativa", "Alternativa (extremos)")):
        s = ORD[ORD[campo].notna()].sort_values("posicao")
        with col:
            st.markdown(f"**{tit}**")
            st.dataframe(s[["posicao", "municipio", "porte", "acumulado_2024_2025", campo]].rename(columns={
                "posicao": "Posição", "municipio": "Município", "porte": "Porte", "acumulado_2024_2025": "Acumulado (R$/mat.)",
                campo: "Grupo"}), hide_index=True, use_container_width=True)
    st.caption("Seleção principal (decisão do autor, 29/10/2026): melhor e pior das faixas 'até 20 mil' e 'mais de 20 mil' "
               "habitantes (Censo 2022) e as 39ª e 40ª posições. Medianos: Maracaju e Ponta Porã ficaram praticamente "
               "empatados na 40ª posição (diferença de R$ 0,03 por matrícula) — decisão do autor.")
    st.subheader("Sensibilidade do ordenamento")
    fig = go.Figure()
    fig.add_scatter(x=o["posicao"], y=o["posicao_com_vaar2026_prov"], mode="markers", name="Com VAAR 2026 previsto (provisório)",
                    text=o["municipio"], marker=dict(color=COR_DESEMP, size=7))
    fig.add_scatter(x=o["posicao"], y=o["posicao_ajust"], mode="markers", name="Com VAAR após ajuste",
                    text=o["municipio"], marker=dict(color=COR_ESTR, size=7, symbol="square"))
    fig.add_scatter(x=[1, 79], y=[1, 79], mode="lines", name="mesma posição", line=dict(color="#999", dash="dot"))
    fig.update_layout(title="Posição principal × posição nas sensibilidades", xaxis_title="Posição principal (2024+2025)",
                      yaxis_title="Posição na sensibilidade", height=460)
    mostrar_grafico(fig, "indicador_sensibilidade", "ind_sens")
    st.caption("LOG do 04_dados: com VAAR após ajuste, a ordem é idêntica (correlação de postos 1,00); somando o VAAR previsto "
               "de 2026, a correlação de postos é 0,88.")
