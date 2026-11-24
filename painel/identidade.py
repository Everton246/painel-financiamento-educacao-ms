"""Identidade visual do painel: estilos, cabeçalho, menu, rodapé, cartões de números e o quadro "Como ler esta página".

O visual segue o padrão de sites de serviço público (barra de utilidades, faixa azul no topo, menu branco, títulos de
seção com ponto verde, cartões com borda verde à esquerda, rodapé cinza com barra azul), sem nome, marca, brasão ou
contato de nenhum órgão: o painel é um projeto independente. As cores vêm de dados.CORES, viram variáveis CSS num
só lugar (:root, abaixo) e são repetidas no tema de .streamlit/config.toml.
"""
import datetime as dt
import html

import streamlit as st

import textos
from dados import CORES, FONTE_CORPO, FONTE_TITULO, SEM_DADO, info_ind

RESPONSAVEL = textos.AUTOR
CONTATO_EMAIL = "evertonbronzoni@gmail.com"  # troque aqui: o contato muda no cabeçalho e no rodapé de todas as páginas
AVISO = textos.AVISO


def versao_codigo():
    """Commit do código em uso (lido de .git, sem precisar do programa git); '' se não houver."""
    from pathlib import Path
    g = Path(__file__).resolve().parent.parent / ".git"
    try:
        ref = (g / "HEAD").read_text().strip()
        if ref.startswith("ref:"):
            nome = ref.split(" ", 1)[1]
            arq = g / nome
            if arq.exists():
                return arq.read_text().strip()[:7]
            for linha in (g / "packed-refs").read_text().splitlines():
                if linha.endswith(nome):
                    return linha[:7]
            return ""
        return ref[:7]
    except OSError:
        return ""

# preenchido por app.py: chave -> st.Page. Usado pelo menu e pelos links entre páginas (fichas, Iquems).
PAGINAS = {}
# ordem e rótulos do menu do topo (o título completo de cada página continua no st.Page)
MENU = [("inicio", "Início"), ("normas", "Normas"), ("icms", "ICMS Educacional"), ("iqe", "IQE-MS"),
        ("vaar", "VAAR"), ("indicador", "Indicador e seleção"), ("condicoes", "Condições materiais"),
        ("municipio", "Ficha do município"), ("fontes", "Situação das fontes"), ("sobre", "Sobre os dados")]

MESES = ["jan.", "fev.", "mar.", "abr.", "maio", "jun.", "jul.", "ago.", "set.", "out.", "nov.", "dez."]
# MS não tem horário de verão desde 2019: UTC−4 o ano todo (e não depende do tzdata no Windows)
FUSO_MS = dt.timezone(dt.timedelta(hours=-4))

_VARIAVEIS = "\n".join(f"  --ms-{k.replace('_', '-')}: {v};" for k, v in CORES.items())

_CSS = f"""
<style>
@import url("https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600;700&display=swap");
:root {{
{_VARIAVEIS}
  --ms-fonte-titulo: {FONTE_TITULO};
  --ms-fonte-corpo: {FONTE_CORPO};
  --ms-margem: 2.5rem;          /* margem lateral do conteúdo; as faixas "sangram" até a borda */
}}
@media (max-width: 640px) {{ :root {{ --ms-margem: 1rem; }} }}

/* ---------- estrutura ---------- */
[data-testid="stMainBlockContainer"] {{ padding: 0 var(--ms-margem) 0 !important; max-width: 100%; }}
/* a barra do Streamlit (menu ⋮ e botão da barra lateral) fica transparente, por cima da barra de utilidades */
header[data-testid="stHeader"] {{ background: transparent; pointer-events: none; }}
header[data-testid="stHeader"] * {{ pointer-events: auto; }}
[data-testid="stSidebar"] {{ border-right: 1px solid var(--ms-borda); }}
.ms-sangria {{ margin-left: calc(-1 * var(--ms-margem)); margin-right: calc(-1 * var(--ms-margem));
              padding-left: var(--ms-margem); padding-right: var(--ms-margem); }}

/* ---------- títulos (Open Sans; seções com ponto verde) ---------- */
h1, h2, h3, h4 {{ font-family: var(--ms-fonte-titulo) !important; color: var(--ms-texto); }}
[data-testid="stHeading"] h1 {{ font-size: clamp(1.75rem, 1.2rem + 2vw, 2.5rem); font-weight: 700; padding-top: 1.5rem; }}
[data-testid="stHeading"] h2 {{ font-size: clamp(1.4rem, 1rem + 1.4vw, 1.9rem); font-weight: 700; }}
[data-testid="stHeading"] h3 {{ font-size: clamp(1.35rem, 1rem + 1.2vw, 2rem); font-weight: 700; padding-top: 1.25rem; }}
[data-testid="stHeading"] h3::before {{ content: ""; display: inline-block; width: 0.42em; height: 0.42em;
  border-radius: 50%; background: var(--ms-verde); margin-right: 0.45em; vertical-align: 0.12em; }}

/* ---------- foco visível e links ---------- */
a:focus-visible, button:focus-visible, [role="tab"]:focus-visible, [role="radio"]:focus-visible,
summary:focus-visible, input:focus-visible, [tabindex]:focus-visible {{
  outline: 3px solid var(--ms-azul) !important; outline-offset: 2px; }}
.ms-faixa a:focus-visible, .ms-rodape-azul a:focus-visible {{ outline-color: var(--ms-branco) !important; }}
/* campos de seleção: borda com contraste de pelo menos 3:1 */
[data-baseweb="select"] > div, [data-baseweb="input"], [data-baseweb="base-input"] {{ border-color: #8A8A87 !important; }}
/* barras de rolagem sempre visíveis nas listas de opções e na barra lateral: o Streamlit usa uma barra de 6 px
   que só aparece com o mouse em cima, e quem abre uma lista longa não vê que dá para rolar */
[data-baseweb="popover"] ul, [data-baseweb="popover"] ul > div, [data-baseweb="popover"] [role="listbox"],
[data-testid="stSidebarContent"] {{ scrollbar-width: auto; scrollbar-color: #8A8A87 var(--ms-borda-2); }}
[data-baseweb="popover"] ::-webkit-scrollbar, [data-testid="stSidebarContent"]::-webkit-scrollbar {{
  width: 12px; background: var(--ms-borda-2); }}
[data-baseweb="popover"] ::-webkit-scrollbar-thumb, [data-testid="stSidebarContent"]::-webkit-scrollbar-thumb {{
  background: #8A8A87; border-radius: 6px; border: 2px solid var(--ms-borda-2); }}

/* ---------- barra de utilidades ---------- */
/* links à esquerda: à direita ficam os botões do Streamlit (Share, Deploy, ⋮), que variam conforme quem vê */
.ms-util {{ background: var(--ms-branco); display: flex; justify-content: flex-start; align-items: center;
           flex-wrap: wrap; gap: 0.25rem 1.25rem; min-height: 3.75rem; font-size: 0.8rem;
           padding-right: var(--ms-margem) !important; padding-left: calc(var(--ms-margem) + 2.5rem) !important; }}
.ms-util a {{ color: var(--ms-azul-escuro); text-decoration: none; }}
.ms-util a:hover {{ text-decoration: underline; }}
.ms-pular {{ position: absolute; left: -9999px; }}
.ms-pular:focus {{ position: static; }}

/* ---------- faixa azul ---------- */
.ms-faixa {{ background: var(--ms-azul); color: var(--ms-branco); min-height: 96px; display: flex;
            align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 0.5rem 2rem;
            padding-top: 0.9rem; padding-bottom: 0.9rem; }}
.ms-titulo {{ font-family: var(--ms-fonte-titulo); font-weight: 700; font-size: clamp(1.15rem, 0.9rem + 1vw, 1.6rem);
             line-height: 1.25; color: var(--ms-branco); }}
.ms-sub {{ font-size: 0.88rem; color: #E8EEF6; margin-top: 0.3rem; max-width: 48rem; line-height: 1.4; }}
.ms-resp {{ font-size: 0.85rem; color: #E8EEF6; line-height: 1.4; }}
.ms-resp b {{ color: var(--ms-branco); font-weight: 600; }}

/* ---------- menu ---------- */
.st-key-ms_menu, .st-key-ms_menu_celular {{ background: var(--ms-branco); border-bottom: 1px solid var(--ms-borda);
  margin: -1rem calc(-1 * var(--ms-margem)) 0 !important; padding: 0.2rem var(--ms-margem) !important;
  width: calc(100% + 2 * var(--ms-margem)) !important; max-width: none !important; box-sizing: border-box; }}
.st-key-ms_menu [data-testid="stHorizontalBlock"] {{ flex-wrap: wrap; gap: 0 0.15rem; }}
.st-key-ms_menu [data-testid="stColumn"] {{ flex: 0 0 auto !important; width: auto !important; min-width: 0 !important; }}
.st-key-ms_menu a[data-testid="stPageLink-NavLink"], .st-key-ms_menu_celular a[data-testid="stPageLink-NavLink"] {{
  background: transparent !important; border-radius: 0; padding: 0.45rem 0.6rem; border-bottom: 3px solid transparent; }}
.st-key-ms_menu a[data-testid="stPageLink-NavLink"] p, .st-key-ms_menu_celular a[data-testid="stPageLink-NavLink"] p {{
  color: var(--ms-texto); font-size: 0.92rem; }}
.st-key-ms_menu a[data-testid="stPageLink-NavLink"]:hover {{ border-bottom-color: var(--ms-borda); }}
.ms-menu-atual {{ display: inline-block; padding: 0.45rem 0.6rem; font-size: 0.92rem; font-weight: 700;
                 color: var(--ms-azul); border-bottom: 3px solid var(--ms-azul); line-height: 1.6; }}
.st-key-ms_menu_celular {{ display: none; }}
.st-key-ms_menu_celular [data-testid="stExpander"] details {{ border: 0; }}
.st-key-ms_menu_celular [data-testid="stExpanderDetails"] [data-testid="stVerticalBlock"] {{ gap: 0; }}
@media (max-width: 640px) {{
  .st-key-ms_menu {{ display: none; }}
  .st-key-ms_menu_celular {{ display: block; }}
}}

/* ---------- cartões (borda verde à esquerda, sem cantos nem sombra) ---------- */
.ms-cartoes {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;
              margin: 0.25rem 0 0.5rem; }}
.ms-cartao {{ background: var(--ms-branco); border-left: 8px solid var(--ms-verde); padding: 1rem 1.1rem; }}
.ms-cartao .rot {{ font-family: var(--ms-fonte-titulo); font-weight: 700; font-size: 1.125rem; color: var(--ms-texto);
                  line-height: 1.3; }}
.ms-cartao .val {{ font-size: 2rem; font-weight: 600; color: var(--ms-texto); line-height: 1.2; margin: 0.35rem 0; }}
.ms-cartao .val.sem {{ font-size: 1.15rem; font-weight: 500; color: var(--ms-texto-2); padding: 0.45rem 0; }}
.ms-cartao .fon {{ font-size: 0.78rem; color: var(--ms-texto-2); line-height: 1.35; }}
/* cartões feitos com st.container(key="ms_cartao_..."): mesma cara, com o link de ação e a seta ↗ no canto */
[class*="st-key-ms_cartao"] {{ background: var(--ms-branco); border-left: 8px solid var(--ms-verde);
  padding: 1rem 1.1rem 0.6rem; position: relative; height: 100%; gap: 0.4rem; }}
/* o Streamlit puxa o bloco seguinte 1rem para cima (margem negativa); o padding de baixo compensa */
[class*="st-key-ms_cartao"] h4 {{ font-size: 1.125rem !important; font-weight: 700; padding: 0 1.5rem 1rem 0 !important;
  margin: 0; line-height: 1.3; }}
[class*="st-key-ms_cartao"] [data-testid="stHeaderActionElements"] {{ display: none; }}
[class*="st-key-ms_cartao"] p {{ color: var(--ms-texto); }}
[class*="st-key-ms_cartao_pg"]::after {{ content: "↗"; position: absolute; top: 0.8rem; right: 1rem;
  color: var(--ms-link); font-size: 1.1rem; font-weight: 700; }}
[class*="st-key-ms_cartao"] a[data-testid="stPageLink-NavLink"] {{ padding-left: 0; background: transparent !important; }}
[class*="st-key-ms_cartao"] a[data-testid="stPageLink-NavLink"] p {{ color: var(--ms-link); font-weight: 600; }}
[class*="st-key-ms_cartao"] a[data-testid="stPageLink-NavLink"]:hover p {{ text-decoration: underline; }}
[data-testid="stColumn"]:has([class*="st-key-ms_cartao"]) > div {{ height: 100%; }}

/* botões de ação com cara de link (ficha do município, ficha Iquems) */
[class*="st-key-ms_acao"] button {{ color: var(--ms-link) !important; font-weight: 600; padding-left: 0; }}
[class*="st-key-ms_acao"] button p {{ font-weight: 600; }}
[class*="st-key-ms_acao"] button:hover p {{ text-decoration: underline; }}

/* ---------- dados da escola/Iquems (rótulo + valor) ---------- */
.ms-dados {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 0.75rem 1.25rem;
            margin: 0.25rem 0 0.5rem; }}
.ms-dados .rot {{ font-size: 0.85rem; color: var(--ms-texto-2); }}
.ms-dados .val {{ font-size: 1.1rem; font-weight: 700; color: var(--ms-texto); line-height: 1.3; }}

/* ---------- quadro "Como ler" e expansores ---------- */
[data-testid="stExpander"] details {{ background: var(--ms-branco); border-color: var(--ms-borda); }}

/* ---------- rodapé ---------- */
.ms-rodape {{ margin-top: 3rem; font-size: 0.82rem; line-height: 1.55; }}
.ms-rodape-cinza {{ background: var(--ms-rodape); color: var(--ms-texto); padding-top: 1.5rem; padding-bottom: 1.25rem;
                   display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1rem 2.5rem; }}
.ms-rodape-cinza h4 {{ font-size: 0.95rem !important; font-weight: 700; margin: 0 0 0.35rem; padding: 0; }}
.ms-rodape-cinza p {{ margin: 0 0 0.45rem; }}
.ms-rodape-cinza a {{ color: var(--ms-azul-escuro); }}
.ms-rodape-azul {{ background: var(--ms-azul); color: var(--ms-branco); padding-top: 0.8rem; padding-bottom: 0.8rem;
                  font-size: 0.82rem; }}
</style>
"""


def estilos():
    # só <style>: o Streamlit põe fora do fluxo da página, sem ocupar espaço
    st.html(_CSS)


def data_montagem(resumo):
    """'2026-10-21 20:22' → '21/10/2026, às 20:22' (ou o texto original, se vier noutro formato)."""
    txt = str(resumo.get("montado_em", ""))
    try:
        d = dt.datetime.strptime(txt, "%Y-%m-%d %H:%M")
    except ValueError:
        return txt or "data desconhecida"
    return d.strftime("%d/%m/%Y, às %H:%M")


def citacao(resumo):
    """Referência no padrão ABNT (NBR 6023), com a data de acesso de hoje."""
    hoje = dt.datetime.now(FUSO_MS)
    ano = str(resumo.get("montado_em", ""))[:4] or str(hoje.year)
    return (f"{textos.AUTOR.split()[-1].upper()}, {' '.join(textos.AUTOR.split()[:-1])}. "
            f"<b>{textos.TITULO}</b>. Painel de dados. [S. l.], {ano}."
            + (f" Disponível em: {textos.ENDERECO}. Acesso em: {hoje.day} {MESES[hoje.month - 1]} {hoje.year}." if textos.ENDERECO else ""))


def cabecalho(resumo=None):
    """Barra de utilidades (fundo branco) e faixa azul com o nome do painel, a data e a versão da base."""
    email = html.escape(CONTATO_EMAIL)
    v = versao_codigo()
    versao = (f"Base de {html.escape(data_montagem(resumo))}" if resumo else "") + (f" · versão {v}" if v else "")
    st.html(f"""
<div class="ms-cab">
  <nav class="ms-util ms-sangria" aria-label="Utilidades">
    <a class="ms-pular" href="#conteudo">Ir para o conteúdo</a>
    <a href="#como-citar">Como citar</a>
    <a href="mailto:{email}">Contato</a>
  </nav>
  <div class="ms-faixa ms-sangria" role="banner">
    <div>
      <div class="ms-titulo">{html.escape(textos.TITULO)}</div>
      <div class="ms-sub">{html.escape(textos.SUBTITULO)}</div>
    </div>
    <div class="ms-resp">Responsável: <b>{html.escape(RESPONSAVEL)}</b><br><span style="font-size:0.78rem">{versao}</span></div>
  </div>
</div>""")


def menu(atual):
    """Menu horizontal sob a faixa azul (no celular, recolhido num "☰ Menu"). `atual` = página em exibição.
    Os links são st.page_link: trocam de página sem recarregar, e os filtros vão junto."""
    def itens(horizontal):
        cols = st.columns(len(MENU)) if horizontal else [st.container() for _ in MENU]
        for col, (chave, rotulo) in zip(cols, MENU):
            with col:
                if PAGINAS.get(chave) is atual:
                    st.markdown(f'<span class="ms-menu-atual" aria-current="page">{html.escape(rotulo)}</span>',
                                unsafe_allow_html=True)
                else:
                    st.page_link(PAGINAS[chave], label=rotulo)
    with st.container(key="ms_menu"):
        itens(True)
    with st.container(key="ms_menu_celular"):
        with st.expander(f"☰ Menu · {atual.title}"):
            itens(False)
            st.caption("Os **filtros** (ano, município, porte, seleção, VAAR e IQE-MS) ficam no painel lateral: "
                       "toque em **›** no canto superior esquerdo.")
    st.html('<div id="conteudo" tabindex="-1"></div>')


def rodape(resumo):
    email = html.escape(CONTATO_EMAIL)
    st.html(f"""
<footer class="ms-rodape ms-sangria" style="padding:0">
  <div class="ms-rodape-cinza ms-sangria" style="margin:0">
    <div>
      <h4>Fontes e data da base</h4>
      <p>{html.escape(textos.FONTES)}. Período de cada fonte na página Situação das fontes.</p>
      <p><b>Base montada em {html.escape(data_montagem(resumo))}{(" · versão do código " + versao_codigo()) if versao_codigo() else ""}.</b> {textos.REGRAS}</p>
    </div>
    <div id="como-citar">
      <h4>Como citar</h4>
      <p>{citacao(resumo)}</p>
    </div>
    <div>
      <h4>Responsável e contato</h4>
      <p>{html.escape(textos.RODAPE)}</p>
      <p><a href="mailto:{email}">{email}</a></p>
    </div>
  </div>
  <div class="ms-rodape-azul ms-sangria" style="margin:0">{html.escape(AVISO)}</div>
</footer>""")


def cartoes(itens):
    """Cartões de números-chave: cada item = (rótulo, valor já formatado ou None, fonte e ano)."""
    partes = []
    for rotulo, valor, fonte in itens:
        val = (f'<div class="val sem">{SEM_DADO}</div>' if valor is None
               else f'<div class="val">{html.escape(valor)}</div>')
        partes.append(f'<div class="ms-cartao"><div class="rot">{html.escape(rotulo)}</div>{val}'
                      f'<div class="fon">{html.escape(fonte)}</div></div>')
    st.html(f'<div class="ms-cartoes">{"".join(partes)}</div>')


def dados_chave(itens):
    """Linha de rótulo + valor (cabeçalho da ficha da escola e da ficha Iquems). Valores já formatados."""
    partes = "".join(f'<div><div class="rot">{html.escape(str(r))}</div><div class="val">{html.escape(str(v))}</div></div>'
                     for r, v in itens)
    st.html(f'<div class="ms-dados">{partes}</div>')


def como_ler(pagina, cat=None, indicadores=()):
    """Quadro recolhível com o que a página mede, como ler e os limites (textos.py), mais a definição de cada indicador
    principal da página (dados/base/catalogo.csv)."""
    t = textos.PAGINAS[pagina]
    with st.expander("ℹ️ Como ler esta página: o que mede, como ler e limites"):
        st.markdown(f"**O que mede.** {t['mede']}\n\n**Como ler.** {t['ler']}\n\n**Limites.** {t['limites']}")
        for ind in dict.fromkeys(i for i in indicadores if i):
            i = info_ind(cat, ind) if cat is not None else {}
            if i:
                st.markdown(f"**{i['nome']}** — {i['definicao']} Unidade: {i['unidade']}. O ano significa: "
                            f"{i['ano_significa']}.")
