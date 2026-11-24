"""Ficha do município em PDF de uma página (A4), com fpdf2. Fonte padrão do PDF (latin-1): caracteres fora dela viram
equivalentes. Adaptado do painel do Iquems."""
import re

import pandas as pd
from fpdf import FPDF

from dados import SEM_DADO
import textos

TROCAS = {"–": "-", "—": "-", "≥": ">=", "≤": "<=", "·": "-", "“": '"', "”": '"', "’": "'", "−": "-", "…": "...",
          "≈": "~", "ª": "a", "º": "o", "¹": "1", "²": "2", "³": "3"}


def _t(texto):
    s = re.sub(r"\*+", "", str(texto))
    for a, b in TROCAS.items():
        s = s.replace(a, b)
    return s.encode("latin-1", "replace").decode("latin-1")


def _v(v, coluna=""):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return SEM_DADO
    if isinstance(v, (int, float)) and str(coluna).startswith(("Ano", "Repasse")):
        return str(int(v))
    if isinstance(v, (int, float)) and 0 < abs(v) < 0.1:
        return f"{v:.6f}".replace(".", ",").rstrip("0")
    if isinstance(v, (int, float)):
        if abs(v) >= 1000:
            return f"{v:,.0f}".replace(",", ".")
        if float(v).is_integer():
            return f"{int(v)}"
        return f"{v:,.4f}".replace(",", "X").replace(".", ",").replace("X", ".").rstrip("0").rstrip(",")
    return str(v)


class _Ficha(FPDF):
    def __init__(self, base_txt):
        super().__init__(format="A4")
        self.base_txt = base_txt
        self.set_auto_page_break(True, margin=14)
        self.set_margins(10, 10, 10)

    def header(self):
        self.set_fill_color(0, 79, 159)
        self.rect(0, 0, 210, 14, "F")
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 10)
        self.set_xy(10, 4)
        self.cell(0, 6, _t(textos.TITULO + " - ficha do município"))
        self.set_text_color(48, 48, 46)
        self.set_y(17)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "", 6.5)
        self.set_text_color(86, 86, 84)
        self.multi_cell(0, 3, _t(f"Base de {self.base_txt}. {textos.RODAPE} 2026 é provisório (ICMS sem repasse anual; VAAR previsto). "
                                 "Fontes: Sefaz/MS, SED/MS, Portal da Transparência MS, FNDE/MEC, Inep, Siconfi, IBGE."))


def _tabela(pdf, df, titulo):
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(0, 61, 117)
    pdf.cell(0, 5, _t(titulo), new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(48, 48, 46)
    cols = list(df.columns)
    larg_total = 190
    primeira = 62 if len(cols) > 3 else 95
    outras = (larg_total - primeira) / max(1, len(cols) - 1)
    larguras = [primeira] + [outras] * (len(cols) - 1)
    pdf.set_font("Helvetica", "B", 6.5)
    pdf.set_fill_color(239, 239, 239)
    for c, w in zip(cols, larguras):
        pdf.cell(w, 4.2, _t(str(c))[:int(w * 0.8)], border=1, fill=True)
    pdf.ln()
    pdf.set_font("Helvetica", "", 6.5)
    for _, r in df.iterrows():
        for c, w in zip(cols, larguras):
            pdf.cell(w, 4, _t(_v(r[c], c))[:int(w * 0.8)], border=1)
        pdf.ln()
    pdf.ln(1.5)


def gerar(cod, nome, o, blocos, base_txt):
    pdf = _Ficha(base_txt)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 7, _t(f"{nome} (IBGE {cod})"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 8)
    sp = o["selecao_principal"] if isinstance(o["selecao_principal"], str) else "não"
    sa = o["selecao_alternativa"] if isinstance(o["selecao_alternativa"], str) else "não"
    pdf.multi_cell(0, 4, _t(f"População (Censo 2022): {_v(o['populacao_2022'])} - porte {o['porte']} - posição no ordenamento "
                            f"(acumulado 2024+2025): {int(o['posicao'])}º de 79 - seleção principal: {sp} - alternativa: {sa}. "
                            "O ordenamento é instrumento de seleção do campo, não classificação de qualidade."),
                   new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    for tit, df in blocos.items():
        if tit == "IQE-MS":
            df = df.drop(columns=["Nota do edital"])
        _tabela(pdf, df, tit)
    notas = blocos["IQE-MS"]["Nota do edital"]
    notas = [f"{a}: {n}" for a, n in zip(blocos["IQE-MS"]["Ano-base"], notas) if n and n != "—"]
    if notas:
        pdf.set_font("Helvetica", "I", 6.5)
        pdf.multi_cell(0, 3.2, _t("Notas dos editais do IQE-MS - " + " | ".join(notas)), new_x="LMARGIN", new_y="NEXT")
    return bytes(pdf.output())
