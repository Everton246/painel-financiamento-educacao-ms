"""Páginas gerais: Início, Normas e linha do tempo, Situação das fontes, Sobre os dados."""
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import identidade
import textos
from dados import BASE, CORES, SEM_DADO, exibir, exportar_tabela, mostrar_grafico, numero, tabela_com_sem_dado
from estado import CAT, IND, NOME, NORMAS, RESUMO, reais, valores
from identidade import como_ler

RAIZ = Path(__file__).resolve().parent.parent


def cartao_pagina(k, chave, titulo, texto):
    with st.container(key=f"ms_cartao_pg_{k}"):
        st.markdown(f"#### {titulo}")
        st.markdown(texto)
        st.page_link(identidade.PAGINAS[chave], label="Abrir a página")


def pagina_inicio():
    st.title("Visão geral")
    st.markdown(textos.RESUMO_PESQUISA)
    st.warning(textos.PROVISORIO, icon="⚠️")
    st.subheader("Números centrais por ano")
    for ano in (2024, 2025, 2026):
        P = valores("icms_parcela_educacional_total", ano).get("50")
        g = valores("icms_ganho_perda", ano)
        v = valores("vaar_valor", ano)
        ben = sum(1 for x in v.values() if pd.notna(x) and x > 0)
        est = valores("icms_parte_estrutural_cov", ano).get("50")
        st.markdown(f"**{ano}**" + (" — PROVISÓRIO" if ano == 2026 else ""))
        identidade.cartoes([
            ("ICMS Educacional distribuído (P)", None if P is None or pd.isna(P) else reais(P, 0),
             "Soma dos 79 · Sefaz/MS e Portal da Transparência" if ano < 2026 else "repasse anual de 2026 pendente (início de 2027)"),
            ("Municípios com ganho / perda", f"{sum(1 for x in g.values() if x > 0)} / {sum(1 for x in g.values() if x < 0)}" if g else None,
             "ganho ou perda no ICMS Educacional" if g else "sem valores em reais em 2026"),
            ("Parte explicada pelo componente estrutural", None if est is None or pd.isna(est) else numero(est * 100, 1, fixo=True) + "%",
             "decomposição por covariância"),
            ("VAAR das redes municipais" + (" (previsto)" if ano == 2026 else ""), reais(sum(x for x in v.values() if pd.notna(x)), 0),
             f"{ben} redes beneficiadas · portarias MEC/MF"),
        ])
    st.caption("Todos os números vêm de 04_dados_ICMS_IQE_VAAR (base oficial dos objetivos a e b), sem recálculo; a "
               "conferência com a planilha final está em Sobre os dados.")
    st.subheader("Como ler o painel")
    for i in range(0, len(textos.PAGINAS_GUIA), 3):
        cols = st.columns(3)
        for col, (k, (chave, titulo, pergunta)) in zip(cols, enumerate(textos.PAGINAS_GUIA[i:i + 3], start=i)):
            with col:
                cartao_pagina(k, chave, titulo, pergunta)
    c = st.columns(2)
    with c[0].container(key="ms_cartao_regra_sem_dado"):
        st.markdown("#### A regra do *sem dado*")
        st.markdown("Quando a fonte não traz um valor, o painel mostra **sem dado**. Nada é estimado para preencher a "
                    "lacuna. A única estimativa é a da própria pesquisa: o ICMS Educacional, calculado com as resoluções da "
                    "Sefaz porque o Portal da Transparência só divulga o total repassado.")
    with c[1].container(key="ms_cartao_regra_escalas"):
        st.markdown("#### Avaliações diferentes nunca no mesmo eixo")
        st.markdown("O SAEMS (avaliação estadual, base do IQE-MS) e o Saeb (base do Ideb e do VAAR) têm escalas próprias. "
                    "O painel nunca os põe na mesma escala ou no mesmo gráfico.")


def pagina_normas():
    st.title("Normas e linha do tempo")
    como_ler("normas")
    st.subheader("A defasagem entre o ano-base do IQE-MS e o repasse")
    fig = go.Figure()
    etapas = [("Ano-base N: SAEMS do 2º ano", 0), ("Edital final do IQE-MS (ano N+1)", 1),
              ("Resolução da Sefaz com os índices (dez. de N+1)", 2), ("Repasse do ICMS (ano N+2)", 3)]
    exemplos = {"N = 2022": ["2022", "DOE 11.278 (25/09/2023)", "Res. 3.354 (19/12/2023)", "2024"],
                "N = 2023": ["2023", "DOE 11.675 (25/11/2024)", "Res. 3.424 (19/12/2024)", "2025"],
                "N = 2024": ["2024", "DOE 11.909 (07/08/2025)", "Res. 3.484 (18/12/2025)", "2026 (provisório)"],
                "N = 2025": ["2025", "preliminar: DOE 12.162 (20/05/2026)", "a publicar (dez. 2026)", "2027"]}
    for k, (rot, x) in enumerate(etapas):
        fig.add_annotation(x=x, y=4.6, text=f"<b>{rot}</b>", showarrow=False, font=dict(size=11))
    for j, (lin, vals) in enumerate(exemplos.items()):
        y = 3.5 - j
        fig.add_scatter(x=[0, 1, 2, 3], y=[y] * 4, mode="lines+markers+text", text=vals, textposition="bottom center",
                        name=lin, line=dict(color=CORES["azul"] if j < 3 else "#9A9A9A", dash="solid" if j < 3 else "dot"),
                        marker=dict(size=10), textfont=dict(size=10))
        fig.add_annotation(x=-0.45, y=y, text=lin, showarrow=False, xanchor="right")
    fig.update_layout(height=380, showlegend=False, xaxis=dict(visible=False, range=[-0.9, 3.5]), yaxis=dict(visible=False, range=[-0.2, 5]),
                      title="IQE-MS do ano-base N → repasse de N+2 (LC nº 63/1990: índices valem a partir de 1º de janeiro seguinte)")
    mostrar_grafico(fig, "defasagem_iqe_repasse", "normas_defasagem")
    st.caption("Fonte: editais finais do IQE-MS e resoluções da Sefaz (04_dados); defasagem conferida pelo 04_dados (o VALOR do "
               "IQE na Resolução nº 3.424 é idêntico ao coeficiente do edital do ano-base 2023 nos 79 municípios).")
    st.subheader("Linha do tempo")
    pol = st.multiselect("Política", sorted(NORMAS["politica"].unique()), key="normas_pol", placeholder="Todas", help="Sem nenhuma marcada, valem todas.")
    n = NORMAS if not pol else NORMAS[NORMAS["politica"].isin(pol)]
    fig = go.Figure()
    cores = {"Fundeb/VAAR": CORES["azul"], "Fundeb/VAAR (CIF)": "#6E9AD3", "ICMS": "#E0702A", "ICMS (transição)": "#9A7B00",
             "Fundeb/VAAR e ICMS": "#1A7F5A", "ICMS e Fundeb (transição)": "#B04EA0"}
    for p, g in n.groupby("politica"):
        fig.add_scatter(x=pd.to_datetime(g["data"]), y=[p] * len(g), mode="markers", name=p, text=g["norma"],
                        marker=dict(size=11, color=cores.get(p, "#565654")), hovertemplate="%{text}<br>%{x|%d/%m/%Y}<extra></extra>")
    fig.update_layout(title="Normas por data e política", height=360, yaxis_title="", showlegend=False)
    mostrar_grafico(fig, "linha_do_tempo_normas", "normas_tl", dados=n)
    t = n.rename(columns={"data": "Data", "politica": "Política", "norma": "Norma", "publicacao": "Publicação",
                          "o_que_muda": "O que muda", "repasse_afetado": "Repasse/exercício afetado",
                          "situacao_conferencia": "Conferência", "arquivo_conferido": "Onde foi conferida"})
    st.dataframe(t, hide_index=True, use_container_width=True, height=520)
    exportar_tabela(t, "normas_linha_do_tempo", "normas_tab")
    st.caption("Normas federais conferidas no texto do Planalto; resoluções da CIF, pela página oficial de legislação do Fundeb "
               "(FNDE), com título e descrição publicados; normas de MS, nas cópias de 04_dados (o portal de legislação de MS "
               "proíbe robôs). Lista completa da página do FNDE: dados_brutos/normas/fnde_legislacao_fundeb_listagem.csv.")
    v = RAIZ / "dados" / "normas_verificacao.csv"
    if v.exists():
        with st.expander("Verificação das normas (o que foi conferido e como)"):
            st.dataframe(pd.read_csv(v, encoding="utf-8-sig"), hide_index=True, use_container_width=True)


def pagina_fontes():
    st.title("Situação das fontes")
    como_ler("fontes")
    p = RAIZ / "dados" / "fontes_status.csv"
    if not p.exists():
        st.info(f"**{SEM_DADO}**: dados/fontes_status.csv ainda não foi gerado.")
        return
    f = pd.read_csv(p, encoding="utf-8-sig")
    resumo = f["situacao"].value_counts()
    identidade.cartoes([(s, str(n), "fontes") for s, n in resumo.items()][:6])
    obj = st.multiselect("Objetivo", sorted(f["objetivo"].unique()), key="fontes_obj", placeholder="Todos")
    if obj:
        f = f[f["objetivo"].isin(obj)]
    st.dataframe(f, hide_index=True, use_container_width=True, height=620)
    exportar_tabela(f, "fontes_status", "fontes_tab")
    ver = sorted((RAIZ / "docs" / "verificacoes").glob("*.md"))
    if ver:
        with st.expander(f"Última verificação automática ({ver[-1].stem})"):
            st.markdown(ver[-1].read_text(encoding="utf-8"))
    cat = RAIZ / "docs" / "catalogo_fontes.md"
    if cat.exists():
        with st.expander("Catálogo de fontes (texto completo)"):
            st.markdown(cat.read_text(encoding="utf-8"))


def pagina_sobre():
    st.title("Sobre os dados")
    como_ler("sobre")
    st.subheader("Como citar")
    st.markdown(identidade.citacao(RESUMO), unsafe_allow_html=True)
    st.markdown("Para citar os dados dos objetivos a e b, cite também a base da pesquisa: planilha "
                "`icms_educacional_vaar_ms.xlsx` (04_dados_ICMS_IQE_VAAR), gerada pelos scripts 01 a 13.")
    st.subheader("Catálogo dos indicadores")
    st.dataframe(CAT, hide_index=True, use_container_width=True, height=480)
    exportar_tabela(CAT, "catalogo_indicadores", "sobre_cat")
    for arq, tit in (("conferencia.md", "Conferência da base (objetivos a e b, somas, fontes, ranking provisório)"),
                     ("historico.md", "Histórico de mudanças")):
        p = RAIZ / "docs" / arq
        if p.exists():
            with st.expander(tit, expanded=arq == "conferencia.md"):
                st.markdown(p.read_text(encoding="utf-8"))
    st.subheader("Base completa")
    st.markdown(f"{RESUMO.get('linhas', 0):,} valores, {RESUMO.get('indicadores')} indicadores, 79 municípios, anos "
                f"{RESUMO.get('anos', ['?', '?'])[0]}–{RESUMO.get('anos', ['?', '?'])[1]}. Cada valor traz fonte, arquivo e "
                "página de origem.".replace(",", "."))
    if st.button("Preparar o download da base completa (CSV)", key="sobre_base"):
        st.download_button("⬇ indicadores.csv", IND.to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig"),
                           "indicadores.csv", "text/csv", key="sobre_base_dl")
