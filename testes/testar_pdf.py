"""Gera a ficha em PDF de alguns municípios (fora do Streamlit) e confere que tem uma página. Uso: python testes/testar_pdf.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "painel"))
from streamlit.testing.v1 import AppTest  # noqa: E402,F401  (garante o mesmo ambiente de importação)

import estado  # noqa: E402
import ficha_pdf  # noqa: E402
import pag_c  # noqa: E402
import pdfplumber  # noqa: E402

saida = Path(__file__).resolve().parent / "saida"
saida.mkdir(exist_ok=True)
falhas = 0
for cod in ("5007976", "5002704", "5005103", "5000906"):
    o, blocos = pag_c.dados_ficha(cod)
    b = ficha_pdf.gerar(cod, estado.NOME[cod], o, blocos, "teste")
    p = saida / f"ficha_{cod}.pdf"
    p.write_bytes(b)
    with pdfplumber.open(p) as pdf:
        n = len(pdf.pages)
    print(f"{estado.NOME[cod]}: {len(b)} bytes, {n} página(s)")
    falhas += n != 1
sys.exit(1 if falhas else 0)
