"""Base carregada, filtros gerais (barra lateral e endereço) e funções comuns às páginas."""
import unicodedata

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import identidade
import textos
from dados import (ANOS_EXERCICIO, CORES, PORTES, SEM_DADO, SEQUENCIAL, carregar, exibir, legenda_fonte, malha,
                   mostrar_grafico, nome_ind, numero)

IND, AT, MUN, ORD, CAT, NORMAS, RESUMO = carregar()
NOME = dict(zip(MUN["cod_ibge"], MUN["municipio"]))
PORTE = dict(zip(MUN["cod_ibge"], MUN["porte"]))
SEL_P = {c: g for c, g in zip(MUN["cod_ibge"], MUN["selecao_principal"]) if isinstance(g, str)}
SEL_A = {c: g for c, g in zip(MUN["cod_ibge"], MUN["selecao_alternativa"]) if isinstance(g, str)}

OPC_SELECAO = {"principal": "Seleção principal (por porte)", "alternativa": "Seleção alternativa (extremos)",
               "nenhuma": "Fora das duas seleções"}
OPC_VAAR = {"beneficiado": "Habilitado e beneficiado", "hab_nao_benef": "Habilitado, não beneficiado",
            "inabilitado": "Não habilitado"}
OPC_IQE = {"minimo": "Coeficiente mínimo do ano", "sem_resultado": "Sem resultado completo", "nenhum": "Nenhum dos dois"}
PADRAO = {"f_ano": 2025, "f_mun": "", "f_porte": [], "f_selecao": [], "f_vaar": [], "f_iqe": []}


# ------------------------------------------------------------------ consulta à base

def serie(indicador, anos=None, cods=None):
    d = IND[IND["indicador"] == indicador]
    if anos is not None:
        d = d[d["ano"].isin(list(anos))]
    if cods is not None:
        d = d[d["cod_ibge"].isin(list(cods))]
    return d


def valores(indicador, ano):
    d = IND[(IND["indicador"] == indicador) & (IND["ano"] == ano)]
    return dict(zip(d["cod_ibge"], d["valor"]))


def textos_at(atributo, ano):
    d = AT[(AT["atributo"] == atributo) & (AT["ano"] == ano)]
    return dict(zip(d["cod_ibge"], d["texto"]))


def largo(indicadores, ano, cods=None, nomes=True):
    """Tabela: uma linha por município, uma coluna por indicador (valor do ano)."""
    cods = list(cods) if cods is not None else list(NOME)
    t = pd.DataFrame({"cod_ibge": cods, "Município": [NOME[c] for c in cods]})
    for ind in indicadores:
        v = valores(ind, ano)
        t[nome_ind(CAT, ind) if nomes else ind] = t["cod_ibge"].map(v)
    return t


def fontes_de(indicadores, anos, cods=None):
    d = IND[IND["indicador"].isin(indicadores) & IND["ano"].isin(list(anos))]
    if cods is not None:
        d = d[d["cod_ibge"].isin(list(cods))]
    return d


# ------------------------------------------------------------------ situações por ano (para os filtros)

def situacao_vaar(ano):
    s = textos_at("vaar_situacao_vaar", ano)
    out = {}
    for c, t in s.items():
        t = (t or "").lower()
        out[c] = "beneficiado" if t.startswith("beneficiado") else ("hab_nao_benef" if t.startswith("habilitado") else
                                                                     ("inabilitado" if t.startswith("inabilitado") else ""))
    return out


def situacao_iqe(ano_base):
    mn, sr = textos_at("iqe_coef_minimo", ano_base), textos_at("iqe_sem_resultado_completo", ano_base)
    out = {}
    for c in NOME:
        tags = set()
        if mn.get(c) == "sim":
            tags.add("minimo")
        if sr.get(c) == "sim":
            tags.add("sem_resultado")
        out[c] = tags or {"nenhum"} if c in mn else set()
    return out


def selecoes(c):
    t = set()
    if c in SEL_P:
        t.add("principal")
    if c in SEL_A:
        t.add("alternativa")
    return t or {"nenhuma"}


def recorte(ano=None):
    """Códigos dos municípios que passam nos filtros de porte, seleção, VAAR e IQE-MS (o filtro de município não
    restringe as tabelas: ele destaca o município e abre a ficha)."""
    s = st.session_state
    ano = ano or s["f_ano"]
    cods = list(NOME)
    if s.get("f_porte"):
        cods = [c for c in cods if PORTE.get(c) in s["f_porte"]]
    if s.get("f_selecao"):
        cods = [c for c in cods if selecoes(c) & set(s["f_selecao"])]
    if s.get("f_vaar"):
        sv = situacao_vaar(ano)
        cods = [c for c in cods if sv.get(c) in s["f_vaar"]]
    if s.get("f_iqe"):
        si = situacao_iqe(ano - 2)
        cods = [c for c in cods if si.get(c, set()) & set(s["f_iqe"])]
    return cods


def descricao_recorte(ano=None):
    s = st.session_state
    ano = ano or s["f_ano"]
    partes = []
    if s.get("f_porte"):
        partes.append("porte: " + ", ".join(s["f_porte"]))
    if s.get("f_selecao"):
        partes.append("seleção: " + ", ".join(OPC_SELECAO[x].lower() for x in s["f_selecao"]))
    if s.get("f_vaar"):
        partes.append(f"VAAR {ano}: " + ", ".join(OPC_VAAR[x].lower() for x in s["f_vaar"]))
    if s.get("f_iqe"):
        partes.append(f"IQE-MS ano-base {ano - 2}: " + ", ".join(OPC_IQE[x].lower() for x in s["f_iqe"]))
    n = len(recorte(ano))
    return (f"**Recorte:** {n} de 79 municípios" + (f" ({'; '.join(partes)})" if partes else " (todos)") + ".")


# ------------------------------------------------------------------ filtros: barra lateral e endereço

def _copia(v):
    return list(v) if isinstance(v, list) else v


def iniciar_filtros():
    s = st.session_state
    for k, v in PADRAO.items():
        if k not in s:
            s[k] = _copia(v)
    if "_aplicar" in s:
        for k, v in s.pop("_aplicar").items():
            s[k] = v
    if s.get("_endereco_lido"):
        return
    s["_endereco_lido"] = True
    q = st.query_params
    try:
        if int(q.get("ano", 0)) in ANOS_EXERCICIO:
            s["f_ano"] = int(q["ano"])
    except ValueError:
        pass
    if q.get("municipio") in NOME:
        s["f_mun"] = q["municipio"]
    for param, chave, validos in (("porte", "f_porte", PORTES), ("selecao", "f_selecao", OPC_SELECAO),
                                  ("vaar", "f_vaar", OPC_VAAR), ("iqe", "f_iqe", OPC_IQE)):
        if q.get(param):
            s[chave] = [x for x in q[param].split(",") if x in validos]


def gravar_endereco():
    s = st.session_state
    novo = {}
    if s["f_ano"] != PADRAO["f_ano"]:
        novo["ano"] = str(s["f_ano"])
    if s.get("f_mun"):
        novo["municipio"] = s["f_mun"]
    for param, chave in (("porte", "f_porte"), ("selecao", "f_selecao"), ("vaar", "f_vaar"), ("iqe", "f_iqe")):
        if s.get(chave):
            novo[param] = ",".join(s[chave])
    if novo != st.query_params.to_dict():
        st.query_params.from_dict(novo)


def filtros_no_padrao():
    s = st.session_state
    return all(s.get(k) == v for k, v in PADRAO.items())


def limpar_filtros():
    for k, v in PADRAO.items():
        st.session_state[k] = _copia(v)


def barra_lateral():
    sb = st.sidebar
    sb.header("Filtros")
    sb.selectbox("Ano (exercício de repasse)", ANOS_EXERCICIO, key="f_ano",
                 format_func=lambda a: f"{a} (PROVISÓRIO)" if a == 2026 else str(a),
                 help="Ano do repasse do ICMS e do VAAR. O IQE-MS usado é o do ano-base dois anos antes. 2026 é provisório.")
    sb.selectbox("Município", [""] + sorted(NOME, key=lambda c: NOME[c]), key="f_mun",
                 format_func=lambda c: NOME.get(c, "Todos os municípios"),
                 help="Destaca o município nas tabelas e gráficos e abre a ficha. Digite parte do nome para buscar.")
    sb.multiselect("Porte populacional (Censo 2022)", PORTES, key="f_porte", placeholder="Todos os portes", help="Sem nenhum marcado, valem todos.")
    sb.multiselect("Seleção de campo", list(OPC_SELECAO), format_func=OPC_SELECAO.get, key="f_selecao", placeholder="Todos",
                   help="Seleção principal (por porte) e alternativa (extremos), do script 09 do 04_dados. A escolha "
                        "final é do autor.")
    sb.multiselect("Situação no VAAR (no ano escolhido)", list(OPC_VAAR), format_func=OPC_VAAR.get, key="f_vaar", placeholder="Todas")
    sb.multiselect("Situação no IQE-MS (ano-base = ano − 2)", list(OPC_IQE), format_func=OPC_IQE.get, key="f_iqe", placeholder="Todas")
    sb.button("Limpar filtros", on_click=limpar_filtros, use_container_width=True, disabled=filtros_no_padrao(),
              help="Volta ao padrão: 2025, todos os municípios.")
    sb.caption("O endereço da página guarda os filtros: copie-o para compartilhar esta tela.")
    sb.divider()
    sb.caption(f"Base montada em {identidade.data_montagem(RESUMO)}. Valores ausentes aparecem como **{SEM_DADO}**.")


def ir_para(pagina, municipio=None):
    s = st.session_state
    if municipio:
        s["f_mun"] = municipio
    s["_ir"] = pagina


def trocar_pagina(chave):
    s = st.session_state
    s["_aplicar"] = {k: _copia(s[k]) for k in PADRAO if k in s}
    st.switch_page(identidade.PAGINAS[chave])


# ------------------------------------------------------------------ peças de página

def aviso_2026(ano=None):
    if (ano or st.session_state["f_ano"]) == 2026:
        st.warning(textos.PROVISORIO, icon="⚠️")


def sem_dado(motivo):
    st.info(f"**{SEM_DADO.capitalize()}** — {motivo}\n\n{textos.SEM_DADO_EXPLICA}")


def tabela(df, nome, chave, fonte_df=None, indicador=None, clicavel=True, altura=None):
    """Tabela formatada ('sem dado' nos ausentes), com fonte e botão de exportação. Clicar numa linha abre a ficha."""
    from dados import exportar_tabela, tabela_com_sem_dado
    mostrar = df.drop(columns=["cod_ibge"], errors="ignore")
    ev = st.dataframe(exibir(mostrar), hide_index=True, use_container_width=True, key=f"t_{chave}", height=altura,
                      on_select="rerun" if clicavel and "cod_ibge" in df else "ignore", selection_mode="single-row")
    if clicavel and "cod_ibge" in df and ev and ev.selection.rows:
        cod = df.iloc[ev.selection.rows[0]]["cod_ibge"]
        st.button(f"Abrir a ficha de {NOME.get(cod, cod)} ↗", key=f"ab_ficha_{chave}", type="tertiary",
                  on_click=ir_para, args=("municipio",), kwargs={"municipio": cod})
    if fonte_df is not None:
        legenda_fonte(fonte_df, CAT, indicador)
    exportar_tabela(tabela_com_sem_dado(df), nome, chave)


def mapa(valores_cod, titulo, nome, chave, divergente=False, sufixo="", casas=0, fonte_df=None, indicador=None):
    """Mapa coroplético dos 79 municípios. Sem valor = cinza claro ('sem dado'). Clique leva à ficha."""
    gj = malha()
    cods = list(NOME)
    v = [valores_cod.get(c) for c in cods]
    df = pd.DataFrame({"cod_ibge": cods, "municipio": [NOME[c] for c in cods], "valor": v})
    tem = df.dropna(subset=["valor"])
    fig = go.Figure()
    fig.add_trace(go.Choropleth(geojson=gj, locations=df["cod_ibge"], z=[0] * len(df), featureidkey="properties.codarea",
                                colorscale=[[0, CORES["sem_dado"]], [1, CORES["sem_dado"]]], showscale=False,
                                marker_line_color="white", marker_line_width=0.5, hoverinfo="skip"))
    if len(tem):
        if divergente:
            m = max(abs(tem["valor"].min()), abs(tem["valor"].max())) or 1
            escala, zmin, zmax = [[0, "#B3412E"], [0.5, "#F4F1EA"], [1, "#1A7F5A"]], -m, m
        else:
            escala, zmin, zmax = [[i / (len(SEQUENCIAL) - 1), c] for i, c in enumerate(SEQUENCIAL)], tem["valor"].min(), tem["valor"].max()
        fig.add_trace(go.Choropleth(geojson=gj, locations=tem["cod_ibge"], z=tem["valor"], featureidkey="properties.codarea",
                                    colorscale=escala, zmin=zmin, zmax=zmax, marker_line_color="white", marker_line_width=0.5,
                                    customdata=[[n, numero(x, casas, fixo=True) + sufixo] for n, x in zip(tem["municipio"], tem["valor"])],
                                    hovertemplate="%{customdata[0]}: %{customdata[1]}<extra></extra>",
                                    colorbar=dict(title=dict(text=sufixo.strip() or ""), thickness=12)))
    mun_sel = st.session_state.get("f_mun")
    if mun_sel:
        fig.add_trace(go.Choropleth(geojson=gj, locations=[mun_sel], z=[0], featureidkey="properties.codarea",
                                    colorscale=[[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]], showscale=False,
                                    marker_line_color="#000000", marker_line_width=2.5, hoverinfo="skip"))
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(title=titulo, height=520, margin=dict(l=0, r=0, t=50, b=0))
    ev = mostrar_grafico(fig, nome, chave, dados=df.rename(columns={"valor": titulo}), clicavel=True)
    try:
        pts = ev.selection.points if ev else []
        if pts:
            cod = pts[0].get("location")
            if cod in NOME:
                st.button(f"Abrir a ficha de {NOME[cod]} ↗", key=f"mapa_ficha_{chave}", type="tertiary",
                          on_click=ir_para, args=("municipio",), kwargs={"municipio": cod})
    except AttributeError:
        pass
    st.caption(f"Municípios em cinza claro: **{SEM_DADO}** (ou fora do recorte dos filtros)." if len(tem) < 79 else
               "Clique num município para abrir a ficha.")
    if fonte_df is not None:
        legenda_fonte(fonte_df, CAT, indicador)


def sem_acento(t):
    return unicodedata.normalize("NFKD", str(t)).encode("ascii", "ignore").decode().lower()


def busca_global():
    q = st.text_input("Buscar município", key="busca_g", placeholder="Ex.: taquarussu, ponta pora, 5002704",
                      help="Sem acento, com parte do nome ou o código IBGE. Escolha o resultado para abrir a ficha.")
    termos = sem_acento(q).split()
    if not termos:
        return
    achados = [(c, n) for c, n in sorted(NOME.items(), key=lambda x: x[1]) if all(t in sem_acento(f"{n} {c}") for t in termos)][:8]
    if not achados:
        st.caption(f"Nenhum município com “{q}”.")
    for c, n in achados:
        st.button(f"🏙 {n} — ficha do município", key=f"bm_{c}", type="tertiary", on_click=_abrir_busca, args=(c,))


def _abrir_busca(c):
    st.session_state["busca_g"] = ""
    ir_para("municipio", municipio=c)


def reais(v, casas=2):
    return SEM_DADO if v is None or pd.isna(v) else "R$ " + numero(v, casas, fixo=True)
