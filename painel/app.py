"""Painel do Financiamento da Educação Municipal de Mato Grosso do Sul (pesquisa de doutorado, PPGEdu/UFMS).

Rodar: abrir_painel.bat  (ou: python -m streamlit run painel/app.py)
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st  # noqa: E402
import streamlit.components.v1 as components  # noqa: E402

st.set_page_config(page_title="Financiamento da educação municipal – MS", page_icon="📊", layout="wide")

import identidade  # noqa: E402
from dados import fechar_downloads  # noqa: E402

identidade.estilos()
fechar_downloads()

with st.sidebar:  # o Streamlit marca a página como inglês e o navegador tenta "traduzir" os textos
    components.html("""<script>
const d = window.parent.document;
d.documentElement.lang = "pt-BR";
d.documentElement.setAttribute("translate", "no");
if (!d.querySelector('meta[name="google"]')) {
  const m = d.createElement("meta"); m.name = "google"; m.content = "notranslate"; d.head.appendChild(m);
}
</script>""", height=0)

try:
    import estado  # noqa: E402  (carrega a base)
except FileNotFoundError:
    st.error("A base ainda não foi montada. Rode **atualizar.bat** (ou `python tratamento/montar_base.py`).")
    st.stop()

import pag_ab  # noqa: E402
import pag_c  # noqa: E402
import pag_geral  # noqa: E402

_INICIAL = os.environ.get("PAINEL_TESTE_PAGINA", "inicio")  # só para o teste automático (testes/testar_painel.py)
identidade.PAGINAS.update({
    "inicio": st.Page(pag_geral.pagina_inicio, title="Início", default=_INICIAL == "inicio"),
    "normas": st.Page(pag_geral.pagina_normas, title="Normas e linha do tempo", url_path="normas", default=_INICIAL == "normas"),
    "icms": st.Page(pag_ab.pagina_icms, title="ICMS Educacional", url_path="icms-educacional", default=_INICIAL == "icms"),
    "iqe": st.Page(pag_ab.pagina_iqe, title="IQE-MS", url_path="iqe-ms", default=_INICIAL == "iqe"),
    "vaar": st.Page(pag_ab.pagina_vaar, title="VAAR", url_path="vaar", default=_INICIAL == "vaar"),
    "indicador": st.Page(pag_ab.pagina_indicador, title="Indicador e seleção", url_path="indicador", default=_INICIAL == "indicador"),
    "condicoes": st.Page(pag_c.pagina_condicoes, title="Condições materiais", url_path="condicoes-materiais", default=_INICIAL == "condicoes"),
    "municipio": st.Page(pag_c.pagina_ficha, title="Ficha do município", url_path="municipio", default=_INICIAL == "municipio"),
    "fontes": st.Page(pag_geral.pagina_fontes, title="Situação das fontes", url_path="fontes", default=_INICIAL == "fontes"),
    "sobre": st.Page(pag_geral.pagina_sobre, title="Sobre os dados", url_path="sobre", default=_INICIAL == "sobre"),
})
pg = st.navigation(list(identidade.PAGINAS.values()), position="hidden")
estado.iniciar_filtros()
estado.barra_lateral()
if st.session_state.get("_ir"):
    estado.trocar_pagina(st.session_state.pop("_ir"))
estado.gravar_endereco()
identidade.cabecalho(estado.RESUMO)
identidade.menu(pg)
estado.busca_global()
pg.run()
identidade.rodape(estado.RESUMO)
