"""Condições materiais (objetivo c, parcial) e ficha do município."""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import identidade
import textos
from dados import (BASE, COR_DESEMP, COR_ESTR, COR_NEG, COR_POS, CORES, SEM_DADO, baixar_planilha, legenda_fonte,
                   mostrar_grafico, nome_ind, numero)
from estado import (AT, CAT, IND, NOME, ORD, PORTE, RESUMO, SEL_A, SEL_P, aviso_2026, descricao_recorte, fontes_de, mapa,
                    recorte, reais, sem_dado, tabela, textos_at, valores)
from identidade import como_ler

ANOS_C = [2021, 2022, 2023, 2024, 2025]
TEMAS = {
    "despesa": "Despesa em educação (Siconfi, DCA)",
    "frentes": "Frentes do pré-projeto: composição da despesa por natureza (Siconfi, MSC)",
    "fundeb": "Fundeb recebido (FNDE)",
    "infra": "Infraestrutura das escolas municipais (Censo Escolar)",
    "remuneracao": "Remuneração docente (Inep)",
    "siope": "Siope (FNDE)",
}
FRENTES = {"educ_msc_pessoal": "Remuneração e carreira ≈ pessoal e encargos (3.1)",
           "educ_msc_obras": "Infraestrutura ≈ obras e instalações (4.4.90.51)",
           "educ_msc_material_consumo": "Materiais ≈ material de consumo (3.3.90.30)",
           "educ_msc_equipamentos": "Materiais e tecnologia ≈ equipamentos e material permanente (4.4.90.52)",
           "educ_msc_servicos_pj": "Misto: serviços de terceiros PJ (3.3.90.39), inclui manutenção",
           "educ_msc_outras": "Demais naturezas"}


def matriculas(cod, ano):
    """Matrículas da rede municipal para expressar valores por matrícula: sinopse do Censo (2024–2025, 04_dados) ou
    soma das escolas dos microdados (2021–2023, painel do Iquems). A conferência mostra que as duas coincidem em 2024."""
    v = valores("mat_municipal_sinopse_censo", ano).get(cod)
    if v is None or pd.isna(v):
        v = valores("mat_municipal_censo_escolas", ano).get(cod)
    return v


def _series(indicador, cods, por_mat=False):
    linhas = []
    for c in cods:
        for a in ANOS_C:
            v = valores(indicador, a).get(c)
            if por_mat and v is not None and pd.notna(v):
                m = matriculas(c, a)
                v = v / m if m else None
            linhas.append({"cod_ibge": c, "Município": NOME[c], "ano": a, "valor": v})
    return pd.DataFrame(linhas)


def _grafico_series(s, titulo, unidade, nome, chave):
    fig = go.Figure()
    fig.add_vrect(x0=2020.5, x1=2023.5, fillcolor="#EEF2F7", line_width=0, layer="below",
                  annotation_text="anterior (2021–2023)", annotation_position="top left")
    fig.add_vrect(x0=2023.5, x1=2025.5, fillcolor="#FDF1E7", line_width=0, layer="below",
                  annotation_text="vigência (2024–2026)", annotation_position="top left")
    muitos = s["cod_ibge"].nunique() > 12
    m = st.session_state.get("f_mun")
    for c, g in s.groupby("cod_ibge"):
        dest = c == m
        fig.add_scatter(x=g["ano"], y=g["valor"], mode="lines+markers", name=NOME[c], showlegend=not muitos or dest,
                        line=dict(width=3 if dest else (1 if muitos else 2), color="#000000" if dest else (
                            "rgba(0,79,159,0.25)" if muitos else None)))
    if muitos:
        med = s.groupby("ano")["valor"].median()
        fig.add_scatter(x=med.index, y=med.values, mode="lines+markers", name="mediana do recorte",
                        line=dict(color=COR_DESEMP, width=3, dash="dash"))
    fig.update_layout(title=titulo, yaxis_title=unidade, xaxis=dict(tickmode="array", tickvals=ANOS_C), height=480)
    mostrar_grafico(fig, nome, chave, dados=s.pivot_table(index="Município", columns="ano", values="valor").reset_index())


def _tabela_periodos(s, nome, chave, fonte):
    t = s.pivot_table(index=["cod_ibge", "Município"], columns="ano", values="valor", dropna=False).reset_index()
    t.columns = [str(c) for c in t.columns]
    ant = [str(a) for a in (2021, 2022, 2023) if str(a) in t]
    vig = [str(a) for a in (2024, 2025) if str(a) in t]
    t["Média 2021–2023 (calculada pelo painel)"] = t[ant].mean(axis=1, skipna=False) if ant else None
    t["Média 2024–2025 (calculada pelo painel)"] = t[vig].mean(axis=1, skipna=False) if vig else None
    t["Variação entre as médias (%)"] = (t.iloc[:, -1] / t.iloc[:, -2] - 1) * 100
    tabela(t, nome, chave, fonte)
    st.caption("Médias e variação calculadas pelo painel com os anos que a fonte traz; se faltar um ano no período, a média "
               "fica *sem dado*. Valores em reais correntes (sem correção pela inflação).")


def pagina_condicoes():
    st.title("Condições materiais das redes municipais (objetivo c, parcial)")
    como_ler("condicoes", CAT, ["educ_dca_empenhada", "fundeb_total_liquido", "infra_n_escolas"])
    cods = recorte()
    st.markdown(descricao_recorte() + " Dica: no filtro **Seleção de campo**, marque a seleção principal para ver só os "
                "seis municípios.")
    tema = st.radio("Tema", list(TEMAS), format_func=TEMAS.get, key="c_tema")
    if tema == "despesa":
        por_mat = st.toggle("Por matrícula da rede municipal", value=True, key="c_desp_mat",
                            help="Despesa empenhada em educação ÷ matrículas da rede municipal (Censo). Cálculo do painel.")
        ind = st.selectbox("Despesa", ["educ_dca_empenhada", "educ_dca_liquidada", "educ_dca_paga", "educ_dca_sub361_empenhada",
                                       "educ_dca_sub365_empenhada"], format_func=lambda i: nome_ind(CAT, i), key="c_desp_ind")
        s = _series(ind, cods, por_mat)
        un = "R$ por matrícula" if por_mat else "R$"
        _grafico_series(s, f"{nome_ind(CAT, ind)}{' por matrícula' if por_mat else ''}", un, f"condicoes_{ind}", "c_desp")
        _tabela_periodos(s, f"condicoes_{ind}", "c_desp_tab", fontes_de([ind], ANOS_C, cods))
        anos_ok = sorted(IND.loc[IND["indicador"] == ind, "ano"].unique())
        if 2025 not in anos_ok:
            st.caption("DCA 2025: **sem dado** para os municípios que ainda não a entregaram ao Siconfi (prazo: 30/04/2026) "
                       "ou cuja entrega não constava na consulta de 24/11/2026.")
    elif tema == "frentes":
        st.info("**Decisão pendente do autor.** O pré-projeto prevê as frentes (remuneração e carreira; infraestrutura; "
                "materiais didáticos, pedagógicos e tecnológicos) com os indicadores de despesa do **Siope**, que estava fora "
                "do ar. Aqui, como aproximação, a despesa da função Educação vem da **Matriz de Saldos Contábeis** (Siconfi) "
                "por natureza de despesa. A correspondência natureza → frente é uma proposta para o autor validar. A "
                "composição só aparece nos município-ano em que o total da matriz confere com a DCA (±0,5%).", icon="⚠️")
        ind = st.selectbox("Natureza de despesa (frente)", list(FRENTES), format_func=FRENTES.get, key="c_frente")
        por_mat = st.toggle("Por matrícula da rede municipal", value=True, key="c_fr_mat")
        s = _series(ind, cods, por_mat)
        if s["valor"].notna().sum() == 0:
            sem_dado("a matriz não confere com a DCA nos município-ano deste recorte, ou o Siconfi não trouxe a matriz.")
        else:
            _grafico_series(s, FRENTES[ind], "R$ por matrícula" if por_mat else "R$", f"condicoes_{ind}", "c_fr")
        _tabela_periodos(s, f"condicoes_{ind}", "c_fr_tab", fontes_de([ind], ANOS_C, cods))
        ok = IND[(IND["indicador"] == "educ_msc_pessoal") & IND["cod_ibge"].isin(cods)]
        st.caption(f"Município-ano com composição validada no recorte: {len(ok)} de {len(cods) * len(ANOS_C)}.")
    elif tema == "fundeb":
        ind = st.selectbox("Origem", ["fundeb_total_liquido", "fundeb_receita_de_contribuicoes_liquido", "fundeb_complementacao_vaaf_liquido",
                                      "fundeb_complementacao_vaat_liquido", "fundeb_complementacao_vaar_liquido"],
                           format_func=lambda i: nome_ind(CAT, i), key="c_fundeb_ind")
        por_mat = st.toggle("Por matrícula da rede municipal", value=False, key="c_fundeb_mat")
        s = _series(ind, cods, por_mat)
        _grafico_series(s, nome_ind(CAT, ind) + (" por matrícula" if por_mat else ""), "R$ por matrícula" if por_mat else "R$",
                        f"condicoes_{ind}", "c_fundeb")
        _tabela_periodos(s, f"condicoes_{ind}", "c_fundeb_tab", fontes_de([ind], ANOS_C, cods))
        st.caption("Ano civil de pagamento (inclui ajustes de exercícios anteriores). A complementação VAAR começou em 2023. "
                   "A receita de contribuições é a parte do fundo estadual que cabe à rede; não é recurso novo do município.")
    elif tema == "infra":
        itens = [i for i in CAT["indicador"] if str(i).startswith("infra_")]
        ind = st.selectbox("Item", itens, format_func=lambda i: nome_ind(CAT, i), key="c_infra_ind",
                           index=itens.index("infra_internet_alunos") if "infra_internet_alunos" in itens else 0)
        s = _series(ind, cods)
        _grafico_series(s, nome_ind(CAT, ind), CAT.set_index("indicador").loc[ind, "unidade"], f"condicoes_{ind}", "c_infra")
        _tabela_periodos(s, f"condicoes_{ind}", "c_infra_tab", fontes_de([ind], ANOS_C, cods))
        st.caption("Escolas da rede municipal em atividade (Censo Escolar, microdados de escola). Percentual entre as escolas "
                   "com o item informado. Os microdados vêm do painel do Iquems (sem novo download).")
    elif tema == "remuneracao":
        st.markdown("O Inep publica a remuneração média dos docentes por município e rede (a partir da RAIS) só até **2021** "
                    "(página consultada em 24/11/2026). É a linha de base do período anterior; 2022 em diante: **sem dado** "
                    "até nova publicação. O Siope traria a remuneração dos profissionais por mês, mas estava fora do ar.")
        cols = ["rem_docentes_n", "rem_pct_localizados_rais", "rem_media_bruta", "rem_mediana_bruta", "rem_carga_horaria", "rem_media_40h"]
        t = pd.DataFrame({"cod_ibge": cods, "Município": [NOME[c] for c in cods]})
        for i in cols:
            t[nome_ind(CAT, i)] = t["cod_ibge"].map(valores(i, 2021))
        tabela(t, "remuneracao_docente_2021", "c_rem", fontes_de(cols, [2021], cods))
        mapa({c: x for c, x in valores("rem_media_40h", 2021).items() if c in cods}, "Remuneração média padronizada para 40 h, 2021 (R$)",
             "mapa_rem_40h_2021", "c_rem_mapa", fonte_df=fontes_de(["rem_media_40h"], [2021], cods), indicador="rem_media_40h")
    else:
        disp = RESUMO.get("siope_disponivel")
        if not disp:
            sem_dado("o serviço de dados abertos do Siope (FNDE) respondeu com erro 500 em todas as consultas de 24/11/2026, e os "
                     "arquivos analíticos publicados no portal do FNDE só vão até 2019. O coletor (coleta/03_siope.py) tenta "
                     "de novo a cada atualização; quando o serviço voltar, os indicadores do Siope (% aplicado em MDE, % do "
                     "Fundeb na remuneração, despesas por natureza e remuneração) entram aqui.")
        else:
            si = [i for i in CAT["indicador"] if str(i).startswith("siope_")]
            ind = st.selectbox("Indicador do Siope", si, format_func=lambda i: nome_ind(CAT, i), key="c_siope")
            s = _series(ind, cods)
            _grafico_series(s, nome_ind(CAT, ind), "%", f"condicoes_{ind}", "c_siope")
            _tabela_periodos(s, f"condicoes_{ind}", "c_siope_tab", fontes_de([ind], ANOS_C, cods))


# ------------------------------------------------------------------------------------------------ ficha do município

def _linha(cod, ind, anos):
    return [valores(ind, a).get(cod) for a in anos]


def dados_ficha(cod):
    """Blocos da ficha (usados na tela, no Excel e no PDF)."""
    o = ORD[ORD["cod_ibge"] == cod].iloc[0]
    blocos = {}
    a3 = [2024, 2025, 2026]
    icms = pd.DataFrame({"Item": [nome_ind(CAT, i) for i in ("icms_repasse_total", "icms_iqe_coef", "icms_educacional", "icms_ganho_perda",
                                                               "icms_estrutural", "icms_desempenho", "icms_desempenho_por_mat")]})
    for a in a3:
        icms[str(a) + (" (provisório)" if a == 2026 else "")] = [valores(i, a).get(cod) for i in
                                                                 ("icms_repasse_total", "icms_iqe_coef", "icms_educacional", "icms_ganho_perda",
                                                                  "icms_estrutural", "icms_desempenho", "icms_desempenho_por_mat")]
    blocos["ICMS Educacional"] = icms
    iqe = pd.DataFrame({"Ano-base": [2022, 2023, 2024], "Repasse": [2024, 2025, 2026],
                        "Coeficiente": _linha(cod, "iqe_coef", [2022, 2023, 2024]),
                        "Coef. mínimo do ano": [textos_at("iqe_coef_minimo", a).get(cod, "") for a in (2022, 2023, 2024)],
                        "Sem result. completo": [textos_at("iqe_sem_resultado_completo", a).get(cod, "") for a in (2022, 2023, 2024)],
                        "Nota do edital": [textos_at("iqe_nota_texto", a).get(cod, "") or "—" for a in (2022, 2023, 2024)],
                        "Particip. SAEMS 2º LP (%)": _linha(cod, "saems2_participacao_lp", [2022, 2023, 2024])})
    blocos["IQE-MS"] = iqe
    vaar = pd.DataFrame({"Ano": a3, "Situação": [textos_at("vaar_situacao_vaar", a).get(cod, "") for a in a3],
                         "Cond. descumpridas": [textos_at("vaar_condicionalidades_descumpridas", a).get(cod, "") or "—" for a in a3],
                         "VAAR (R$)": _linha(cod, "vaar_valor", a3), "VAAR/matrícula (R$)": _linha(cod, "vaar_por_mat", a3),
                         "Matrículas": _linha(cod, "mat_rede_municipal_sinopse", a3)})
    blocos["VAAR"] = vaar
    ind = pd.DataFrame({"Item": ["Indicador 2024 (R$/mat.)", "Indicador 2025 (R$/mat.)", "Acumulado 2024+2025 (R$/mat.)", "Posição (1 = melhor)",
                                 "Posição com VAAR 2026 previsto", "Seleção principal", "Seleção alternativa"],
                        "Valor": [o["indicador_2024"], o["indicador_2025"], o["acumulado_2024_2025"], o["posicao"], o["posicao_com_vaar2026_prov"],
                                  o["selecao_principal"] if isinstance(o["selecao_principal"], str) else "não",
                                  o["selecao_alternativa"] if isinstance(o["selecao_alternativa"], str) else "não"]})
    blocos["Indicador e seleção"] = ind
    cond_inds = ["educ_dca_empenhada", "fundeb_total_liquido", "infra_n_escolas", "infra_internet_alunos",
                 "infra_biblioteca_sala_leitura", "infra_sem_acessibilidade", "receita_total_bruta", "pib"]
    cond = pd.DataFrame({"Item": [nome_ind(CAT, i) for i in cond_inds]})
    for a in ANOS_C:
        cond[str(a)] = [valores(i, a).get(cod) for i in cond_inds]
    rem = pd.DataFrame([["Remuneração média dos docentes (40 h), R$", valores("rem_media_40h", 2021).get(cod)] + [None] * 4],
                       columns=cond.columns)
    cond = pd.concat([cond, rem], ignore_index=True)
    blocos["Condições materiais e contexto"] = cond
    return o, blocos


def pagina_ficha():
    st.title("Ficha do município")
    como_ler("municipio")
    cod = st.session_state.get("f_mun")
    if not cod:
        st.info("Escolha um município no filtro **Município** (barra lateral) ou na busca do topo.")
        return
    ano = st.session_state["f_ano"]
    o, blocos = dados_ficha(cod)
    st.header(NOME[cod])
    sel = ", ".join(x for x in (("principal: " + SEL_P[cod]) if cod in SEL_P else "", ("alternativa: " + SEL_A[cod]) if cod in SEL_A else "") if x) or "não selecionado"
    identidade.dados_chave([("Código IBGE", cod), ("População (Censo 2022)", numero(o["populacao_2022"], 0)), ("Porte", PORTE.get(cod)),
                            ("Posição no ordenamento", f"{int(o['posicao'])}º de 79"), ("Seleção de campo", sel)])
    identidade.cartoes([
        ("Ganho ou perda no ICMS Educacional 2024", reais(valores("icms_ganho_perda", 2024).get(cod), 0), "04_dados, script 05"),
        ("Ganho ou perda no ICMS Educacional 2025", reais(valores("icms_ganho_perda", 2025).get(cod), 0), "04_dados, script 05"),
        ("VAAR 2024 + 2025", reais(sum(v for v in (valores("vaar_valor", 2024).get(cod), valores("vaar_valor", 2025).get(cod)) if v is not None), 0),
         "Portarias de distribuição (Anexo V)"),
        ("Indicador acumulado 2024+2025", "R$ " + numero(o["acumulado_2024_2025"], 2, fixo=True) + "/mat.", "04_dados, script 09"),
    ])
    aviso_2026(2026)
    for tit, df in blocos.items():
        st.subheader(tit)
        from dados import exibir
        st.dataframe(exibir(df), hide_index=True, use_container_width=True)
    d = IND[IND["cod_ibge"] == cod]
    legenda_fonte(d[d["indicador"].isin(["icms_educacional", "vaar_valor", "iqe_coef", "educ_dca_empenhada", "fundeb_total_liquido"])], CAT)
    c1, c2 = st.columns(2)
    with c1:
        baixar_planilha({**blocos, "todos os dados (longo)": d.drop(columns=["municipio"])}, f"ficha_{cod}", "ficha_xlsx",
                        "⬇ Baixar a ficha (Excel, com todos os dados e fontes)")
    with c2:
        if st.button("📄 Gerar a ficha em PDF (uma página)", key="ficha_pdf_bt"):
            import ficha_pdf
            st.session_state["ficha_pdf"] = (cod, ficha_pdf.gerar(cod, NOME[cod], o, blocos, identidade.data_montagem(RESUMO)))
        p = st.session_state.get("ficha_pdf")
        if p and p[0] == cod:
            st.download_button("⬇ Baixar o PDF", p[1], f"ficha_{cod}.pdf", "application/pdf", key="ficha_pdf_dl")
