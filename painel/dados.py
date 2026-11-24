"""Carga da base e utilidades compartilhadas pelas páginas do painel (adaptado do painel do Iquems)."""
import io
import json
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

RAIZ = Path(__file__).resolve().parent.parent
BASE = RAIZ / "dados" / "base"
SEM_DADO = "sem dado"
XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

ANOS_EXERCICIO = [2024, 2025, 2026]
PORTES = ["até 10 mil", "10 a 20 mil", "20 a 50 mil", "50 a 100 mil", "mais de 100 mil"]
COR_POS, COR_NEG = "#1A7F5A", "#B3412E"       # ganho (verde) e perda (vermelho-tijolo), contraste ≥ 3:1 no branco
COR_ESTR, COR_DESEMP = "#6E9AD3", "#E0702A"   # componente estrutural e componente de desempenho
COR_SEL = {"principal": "#004F9F", "alternativa": "#9A7B00", "ambas": "#B04EA0"}

# Cores do painel, num só lugar. identidade.py transforma CORES em variáveis CSS (:root) e o tema do Streamlit
# (.streamlit/config.toml) repete as principais; ao trocar uma cor, troque nos dois.
CORES = {
    "azul": "#004F9F",          # faixa do topo, barra do rodapé, cor primária e rede estadual
    "azul_escuro": "#003D75",   # links da barra de utilidades
    "link": "#005CA9",          # links de ação
    "verde": "#007F31",         # ponto dos títulos de seção e borda dos cartões
    "texto": "#30302E",         # texto principal
    "texto_2": "#565654",       # texto secundário (contraste 7:1 sobre o fundo)
    "fundo": "#F9F9F9",         # fundo das seções
    "branco": "#FFFFFF",        # cartões, menu, gráficos
    "borda": "#EBEBEB",
    "borda_2": "#EFEFEF",
    "rodape": "#D5D5D5",        # faixa cinza do rodapé
    "sem_dado": "#EBEBEB",      # município sem dado no mapa
}
FONTE_TITULO = "'Open Sans', 'Nunito Sans', system-ui, -apple-system, 'Segoe UI', sans-serif"
FONTE_CORPO = "system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"

# cores fixas por rede (a cor acompanha a rede, nunca a posição na lista). A estadual usa o azul do painel; as
# demais foram conferidas para daltonismo (protanopia e deuteranopia) e têm contraste de pelo menos 3:1 sobre o
# branco. "Total" é a referência: cinza neutro e linha tracejada, para não depender só da cor.
COR_REDE = {"estadual": "#004F9F", "municipal": "#E0702A", "privada": "#1A9E6E", "federal": "#B04EA0",
            "publica": "#9A7B00", "total": "#565654"}
# segunda codificação (além da cor): símbolo do marcador e traço da linha por rede
SIMBOLO_REDE = {"estadual": "circle", "municipal": "square", "privada": "diamond", "federal": "triangle-up",
                "publica": "cross", "total": "x"}
TRACO_REDE = {"estadual": "solid", "municipal": "solid", "privada": "solid", "federal": "solid",
              "publica": "solid", "total": "dash"}
# escala do mapa: tons do azul do painel, do mais claro (menor valor) ao mais escuro (maior valor)
SEQUENCIAL = ["#93B4E0", "#6E9AD3", "#4A80C4", "#2766B2", "#004F9F", "#003D80", "#002B5E"]

_EIXO = dict(gridcolor=CORES["borda"], linecolor=CORES["rodape"], zeroline=False, automargin=True,
             tickfont=dict(color=CORES["texto_2"]), title_font=dict(color=CORES["texto"]))
pio.templates["painel"] = go.layout.Template(layout=dict(
    font=dict(family=FONTE_CORPO, size=13, color=CORES["texto"]),
    title=dict(font=dict(family=FONTE_TITULO, size=16, color=CORES["texto"])),
    paper_bgcolor=CORES["branco"], plot_bgcolor=CORES["branco"], xaxis=_EIXO, yaxis=_EIXO,
    legend=dict(orientation="h", y=-0.18, title_text="", font=dict(color=CORES["texto"])),
    margin=dict(l=10, r=10, t=50, b=10), separators=",.",  # decimal com vírgula, milhar com ponto
    hoverlabel=dict(bgcolor=CORES["branco"], font=dict(size=13, color=CORES["texto"]), bordercolor=CORES["texto_2"]),
    annotationdefaults=dict(font=dict(color=CORES["texto"])),
    colorway=list(COR_REDE.values())))
pio.templates.default = "painel"


ARQUIVOS_BASE = ("indicadores.parquet", "atributos.parquet", "municipios.parquet", "ordenamento.parquet", "catalogo.csv",
                 "normas.csv", "resumo.json")


def carregar():
    # a data dos arquivos entra na chave: depois de atualizar.bat, o painel relê a base sozinho
    return _carregar(tuple((BASE / a).stat().st_mtime for a in ARQUIVOS_BASE))


@st.cache_resource(show_spinner="Carregando a base…", max_entries=1)
def _carregar(versao):
    ind = pd.read_parquet(BASE / "indicadores.parquet")
    for c in ("indicador", "unidade", "fonte", "arquivo", "municipio"):
        ind[c] = ind[c].astype(str)
    at = pd.read_parquet(BASE / "atributos.parquet")
    mun = pd.read_parquet(BASE / "municipios.parquet")
    ordn = pd.read_parquet(BASE / "ordenamento.parquet")
    cat = pd.read_csv(BASE / "catalogo.csv", encoding="utf-8-sig")
    normas = pd.read_csv(BASE / "normas.csv", encoding="utf-8-sig")
    resumo = json.loads((BASE / "resumo.json").read_text(encoding="utf-8"))
    return ind, at, mun, ordn, cat, normas, resumo


def _area(anel):
    return sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(anel, anel[1:] + anel[:1])) / 2


def _rebobinar(poligono):
    # o mapa do Plotly (d3-geo) espera anel externo no sentido horário e furos no anti-horário;
    # a malha do IBGE vem no sentido contrário e, sem isso, o polígono "pinta o mundo todo"
    saida = []
    for k, anel in enumerate(poligono):
        externo = k == 0
        if (externo and _area(anel) > 0) or (not externo and _area(anel) < 0):
            anel = anel[::-1]
        saida.append(anel)
    return saida


@st.cache_resource  # só leitura; o Plotly não altera o geojson
def malha():
    # a cópia em dados/base vai junto para a versão online; dados_brutos fica só no computador
    p = BASE / "malha_ms_municipios.geojson"
    if not p.exists():
        p = RAIZ / "dados_brutos" / "ibge" / "malha_ms_municipios.geojson"
    gj = json.loads(p.read_text(encoding="utf-8"))
    for f in gj["features"]:
        g = f["geometry"]
        if g["type"] == "Polygon":
            g["coordinates"] = _rebobinar(g["coordinates"])
        elif g["type"] == "MultiPolygon":
            g["coordinates"] = [_rebobinar(p) for p in g["coordinates"]]
    return gj


def nome_ind(cat, i):
    m = cat.loc[cat["indicador"] == i, "nome"]
    return m.iloc[0] if len(m) else i


def info_ind(cat, i):
    m = cat[cat["indicador"] == i]
    return m.iloc[0].to_dict() if len(m) else {}


def legenda_fonte(df, cat=None, indicador=None):
    """Texto 'Fonte: ... | anos ...' exibido sob cada gráfico/tabela."""
    if df is None or df.empty:
        return
    partes = []
    fontes = df.assign(f=df["fonte"].astype(str).map(lambda t: t if len(t) <= 280 else t[:277] + "…"))
    for f, g in fontes.groupby("f", observed=True):
        anos = sorted(int(a) for a in g["ano"].dropna().unique())
        faixa = f"{anos[0]}–{anos[-1]}" if len(anos) > 1 else f"{anos[0]}" if anos else "?"
        partes.append(f"{f} ({faixa})")
    txt = "**Fonte:** " + " | ".join(partes[:3]) + (f" | e mais {len(partes) - 3} (ver a planilha baixada)" if len(partes) > 3 else "")
    if cat is not None and indicador:
        i = info_ind(cat, indicador)
        if i:
            txt += f" · **Unidade:** {i['unidade']} · **Ano:** {i['ano_significa']}"
    obs = df["observacao"].dropna().unique() if "observacao" in df else []
    obs = [o for o in obs if o][:4]
    if obs:
        txt += " · **Observações:** " + " | ".join(sorted(set(obs)))
    st.caption(txt)


AVISO_EXPORTACAO = ("Painel do Financiamento da Educação Municipal de MS – pesquisa de doutorado em andamento (PPGEdu/UFMS), "
                    "Everton Kunzler Bronzoni. Dados públicos; não é um site oficial do governo. 2026 é provisório.")


def com_aviso(fig):
    """Cópia do gráfico com o aviso de prova de conceito no rodapé (para as exportações em HTML e PNG)."""
    f = go.Figure(fig)
    if any(getattr(x, "text", "") == AVISO_EXPORTACAO for x in f.layout.annotations):
        return f
    f.add_annotation(text=AVISO_EXPORTACAO, xref="paper", yref="paper", x=0, y=-0.28, showarrow=False,
                     xanchor="left", yanchor="top", font=dict(size=9, color=CORES["texto_2"]))
    f.update_layout(margin=dict(b=max((f.layout.margin.b or 0), 120)))
    return f


def para_excel(abas: dict) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        pd.DataFrame({"aviso": [AVISO_EXPORTACAO]}).to_excel(w, sheet_name="aviso", index=False)
        for nome, df in abas.items():
            df.to_excel(w, sheet_name=nome[:31], index=False)
    return buf.getvalue()


def exportar_tabela(df, nome, chave):
    """Botão para baixar uma tabela em Excel e CSV."""
    if df is None or df.empty:
        return
    _baixar(nome, chave, tabela=df)


def mostrar_grafico(fig, nome, chave, dados=None, clicavel=False):
    """Mostra o gráfico (com o ícone de câmera do próprio gráfico) e o botão para baixar dados e imagem.
    `clicavel`: o clique num ponto (ou município do mapa) refaz a página e o ponto vem no retorno."""
    selecao = {"on_select": "rerun", "selection_mode": "points"} if clicavel else {}
    fig = com_aviso(fig)  # o aviso e a fonte vão junto até no PNG do ícone de câmera
    # theme=None: vale o template "painel" (o mesmo das exportações em PNG e HTML), não o tema do Streamlit
    ev = st.plotly_chart(fig, use_container_width=True, key=f"g_{chave}", theme=None,
                         config={"displaylogo": False, "locale": "pt-BR",
                                 "toImageButtonOptions": {"format": "png", "filename": nome, "scale": 2}}, **selecao)
    _baixar(nome, chave, fig=fig, tabela=dados)
    return ev


def baixar_planilha(abas, nome, chave, rotulo):
    """Botão para baixar uma planilha com várias abas (fichas)."""
    if abas:
        _baixar(nome, chave, abas=abas, rotulo=rotulo)


def fechar_downloads():
    """Chamada a cada execução completa do app (mudou filtro ou página): fecha os quadros de download abertos e
    descarta imagens geradas, para nunca oferecer um arquivo de um gráfico que já mudou."""
    for k in [k for k in st.session_state if str(k).startswith(("baixar_", "png_"))]:
        del st.session_state[k]


def _abrir(aberto):
    st.session_state[aberto] = True


@st.fragment
def _baixar(nome, chave, fig=None, tabela=None, abas=None, rotulo=None):
    """Os arquivos só são gerados quando a pessoa pede. Assim a página abre mais rápido e o servidor não guarda na
    memória planilhas e imagens que ninguém vai baixar. Por ser um fragmento, os cliques aqui não refazem a página."""
    aberto = f"baixar_{chave}"
    if not st.session_state.get(aberto):
        txt = rotulo or ("⬇ Baixar dados e gráfico" if fig is not None else "⬇ Baixar tabela")
        st.button(txt, key=f"ab_{chave}", type="tertiary", on_click=_abrir, args=(aberto,))
        return
    tem_tabela = tabela is not None and not tabela.empty
    cols = st.columns(4)
    k = 0
    if abas:
        cols[k].download_button("⬇ Planilha (Excel)", para_excel(abas), f"{nome}.xlsx", XLSX, key=f"x_{chave}",
                                on_click="ignore", use_container_width=True)
        k += 1
    if tem_tabela:
        cols[k].download_button("⬇ Planilha (Excel)", para_excel({"dados": tabela}), f"{nome}.xlsx", XLSX,
                                key=f"x_{chave}", on_click="ignore", use_container_width=True)
        csv = f"# {AVISO_EXPORTACAO}\n" + tabela.to_csv(index=False, sep=";", decimal=",")
        cols[k + 1].download_button("⬇ CSV", csv.encode("utf-8-sig"),
                                    f"{nome}.csv", "text/csv", key=f"c_{chave}", on_click="ignore",
                                    use_container_width=True)
        k += 2
    if fig is not None:
        cols[k].download_button("⬇ Gráfico (HTML)", com_aviso(fig).to_html(include_plotlyjs="cdn").encode("utf-8"),
                                f"{nome}.html", "text/html", key=f"h_{chave}", on_click="ignore",
                                use_container_width=True, help="Gráfico interativo, abre em qualquer navegador.")
        vaga = cols[k + 1].empty()
        png = st.session_state.get(f"png_{chave}")
        if png is None and vaga.button("🖼 Gerar imagem PNG", key=f"b_{chave}", use_container_width=True):
            try:
                with st.spinner("Gerando a imagem…"):
                    png = com_aviso(fig).to_image(format="png", width=1400, height=700, scale=2)
                st.session_state[f"png_{chave}"] = png
            except Exception as ex:
                st.warning(f"Não foi possível gerar o PNG aqui ({ex}). Use o ícone de câmera no canto do gráfico.")
        if png is not None:
            vaga.download_button("⬇ Imagem PNG", png, f"{nome}.png", "image/png", key=f"p_{chave}",
                                 on_click="ignore", use_container_width=True)


def tabela_com_sem_dado(df):
    """NaN vira 'sem dado' (usado nas exportações: números com precisão original)."""
    return df.astype(object).where(df.notna(), SEM_DADO)


def numero(v, casas=2, fixo=False):
    """Número no padrão brasileiro (1.234,5); ausente vira 'sem dado'. Sem `fixo`, tira os zeros à direita."""
    if v is None or pd.isna(v):
        return SEM_DADO
    t = f"{v:,.{casas}f}"
    if casas and not fixo:
        t = t.rstrip("0").rstrip(".")
    return t.replace(",", "X").replace(".", ",").replace("X", ".")


def exibir(df):
    """Para a tela: números com até 2 casas decimais e 'sem dado' nos ausentes; colunas de ano sem separador de
    milhar (2025, não 2.025)."""
    def fmt(v):
        return numero(v) if isinstance(v, float) else v

    def fmt_ano(v):
        try:
            return str(int(v)) if float(v).is_integer() else fmt(v)
        except (TypeError, ValueError):
            return v
    out = df.astype(object).where(df.notna(), SEM_DADO).map(fmt).astype(object)
    for k, c in enumerate(df.columns):
        if str(c).startswith("ano"):
            out.iloc[:, k] = out.iloc[:, k].where(df.iloc[:, k].isna(), df.iloc[:, k].map(fmt_ano))
    return out
