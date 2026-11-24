"""Teste automático do painel: roda cada página sem navegador (Streamlit AppTest), com combinações de filtros, e
falha se alguma página mostrar erro. Uso: python testes/testar_painel.py"""
import os
import sys
from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parent.parent / "painel" / "app.py")
PAGINAS = ["inicio", "normas", "icms", "iqe", "vaar", "indicador", "condicoes", "municipio", "fontes", "sobre"]
CENARIOS = [{}, {"f_ano": 2026}, {"f_ano": 2024, "f_mun": "5007976"}, {"f_selecao": ["principal"]},
            {"f_vaar": ["inabilitado"], "f_iqe": ["minimo"]}, {"f_porte": ["mais de 100 mil"], "f_mun": "5002704"}]
TEMAS = ["despesa", "frentes", "fundeb", "infra", "remuneracao", "siope"]

falhas = 0
for pag in PAGINAS:
    os.environ["PAINEL_TESTE_PAGINA"] = pag
    cen = CENARIOS + ([{"c_tema": t, "f_selecao": ["principal"]} for t in TEMAS] if pag == "condicoes" else [])
    for c in cen:
        at = AppTest.from_file(APP, default_timeout=180)
        for k, v in c.items():
            at.session_state[k] = v
        at.run()
        erros = [str(e.value)[:300] for e in at.exception]
        if erros:
            falhas += 1
            print(f"FALHA {pag} {c}: {erros}")
        else:
            print(f"ok    {pag} {c}")
print(f"\n{falhas} falhas")
sys.exit(1 if falhas else 0)
