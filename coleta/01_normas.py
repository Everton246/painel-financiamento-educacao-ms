"""Coleta 01: normas do Fundeb/VAAR e do ICMS Educacional, conferidas na fonte oficial.

- Planalto (www.planalto.gov.br/ccivil_03; sem robots.txt, consultado em 24/11/2026): EC nº 108/2020, Lei nº 14.113/2020,
  Decreto nº 10.656/2021, LC nº 63/1990, EC nº 132/2023 e as leis que alteraram a Lei nº 14.113.
- FNDE, página "Legislação" do Fundeb (gov.br; robots.txt não restringe /fnde): listagem 2020–2026 pela interface de
  dados do portal (++api++), com título, descrição e endereço de cada ato. Baixa o PDF das resoluções da Comissão
  Intergovernamental de Financiamento para a Educação Básica de Qualidade (CIF) sobre condicionalidades e indicadores
  do VAAR.
- Normas de MS: NÃO são baixadas (portal de legislação proíbe robôs). O script só lê as cópias que já estão em
  04_dados_ICMS_IQE_VAAR/dados_brutos/legislacao e sefaz e confere número e data no texto.

Saídas: dados_brutos/normas/... (+ manifesto) e dados/normas_verificacao.csv (o que foi conferido, onde e como).
"""
import re
import sys
import unicodedata
from datetime import date
from html import unescape

import pandas as pd
import pdfplumber

from comum import BRUTOS, DADOS, FONTE_AB, baixar, get_json, log

PASTA = BRUTOS / "normas"
PLANALTO = "https://www.planalto.gov.br/ccivil_03/"
FEDERAIS = {
    "EC 108/2020": "constituicao/emendas/emc/emc108.htm",
    "Lei 14.113/2020": "_ato2019-2022/2020/lei/l14113.htm",
    "Decreto 10.656/2021": "_ato2019-2022/2021/decreto/D10656.htm",
    "LC 63/1990": "leis/lcp/Lcp63.htm",
    "EC 132/2023": "constituicao/emendas/emc/emc132.htm",
    "Lei 14.276/2021": "_ato2019-2022/2021/lei/L14276.htm",
    "Lei 14.325/2022": "_ato2019-2022/2022/lei/L14325.htm",
    "Lei 14.711/2023": "_ato2023-2026/2023/lei/L14711.htm",
    "LC 227/2026": "leis/lcp/Lcp227.htm",
}
API_FNDE = "https://www.gov.br/fnde/++api++/pt-br/acesso-a-informacao/acoes-e-programas/financiamento/fundeb/legislacao/"
ANOS_FNDE = range(2020, 2027)


def sem_acento(t):
    return unicodedata.normalize("NFKD", str(t)).encode("ascii", "ignore").decode()


def texto_html(b: bytes):
    for enc in ("utf-8", "latin-1"):
        try:
            t = b.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", t, flags=re.S | re.I)
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", t))).strip()


def texto_pdf(p, paginas=2):
    with pdfplumber.open(p) as pdf:
        return " ".join((pg.extract_text() or "") for pg in pdf.pages[:paginas])


def federais():
    regs = []
    for nome, caminho in FEDERAIS.items():
        url = PLANALTO + caminho
        arq = baixar(url, PASTA / "planalto" / caminho.split("/")[-1], "normas_planalto")
        if arq is None:
            regs.append({"norma": nome, "fonte": url, "situacao": "falha no download", "evidencia": ""})
            continue
        t = texto_html(arq.read_bytes())
        num = nome.split()[-1].split("/")[0]
        achou = num in t or num.replace(".", "") in t
        ementa = t[:400]
        dou = re.search(r"Este texto n.o substitui o publicado n[oa] (D\.?O\.?U\.?(?: de)? ?[\d\.]+\d(?: ?- ?Edi..o extra)?)", t)
        alteracoes = sorted(set(re.findall(
            r"(?:Reda..o dada pela|Inclu.d[oa] pela|Revogad[oa] pela|Vig.ncia encerrada|Vide) "
            r"((?:Lei(?: Complementar)?|Medida Provis.ria|Emenda Constitucional) n[ºo°] ?[\d\.]+(?:, de \d{4})?)", t)))
        tit = re.search(r"((?:EMENDA CONSTITUCIONAL|LEI COMPLEMENTAR|LEI|DECRETO) N[ºo°] ?[\d\.]+,? DE \d{1,2}.? DE [A-ZÇ]+ DE \d{4})", t)
        regs.append({"norma": nome, "fonte": url, "situacao": "conferida" if achou else "número não encontrado no texto",
                     "titulo_no_texto": tit.group(1) if tit else "", "evidencia": ementa[:300], "publicacao_no_texto": dou.group(1) if dou else "",
                     "alteracoes_citadas_no_texto": "; ".join(alteracoes)})
        log(f"[normas] {nome}: {'conferida' if achou else 'VERIFICAR'}; {len(alteracoes)} atos citados como alteração")
    return regs


def listagem_fnde():
    linhas = []
    for ano in ANOS_FNDE:
        try:
            d = get_json(API_FNDE + str(ano), params={"expand": "items"}, timeout=90)
        except Exception as ex:  # noqa: BLE001
            log(f"[normas] listagem FNDE {ano} falhou: {ex}")
            continue
        for it in d.get("items", []):
            linhas.append({"ano_pasta": ano, "tipo": it.get("@type"), "titulo": it.get("title", "").strip(),
                           "descricao": (it.get("description") or "").strip(), "url": it.get("@id"),
                           "consultado_em": date.today().isoformat()})
    df = pd.DataFrame(linhas)
    df.to_csv(PASTA / "fnde_legislacao_fundeb_listagem.csv", index=False, encoding="utf-8-sig")
    log(f"[normas] listagem da legislação do Fundeb (FNDE): {len(df)} atos de {ANOS_FNDE.start} a {ANOS_FNDE.stop - 1}")
    return df


def baixa_resolucoes_cif(df):
    """PDFs das resoluções e leis da listagem que tratam do VAAR (condicionalidades, indicadores) ou alteram a Lei 14.113."""
    alvo = df[df["tipo"].eq("File")].copy()
    txt = (alvo["titulo"] + " " + alvo["descricao"]).map(sem_acento).str.lower()
    m = (txt.str.contains("resolu") & txt.str.contains("condicionalidade|vaar|indicador|nivel socioeconomico|nse"))
    m |= txt.str.contains(r"altera a lei n. 14\.113") | txt.str.contains(r"regulamenta a lei n. 14\.113")
    regs = []
    for _, r in alvo[m].iterrows():
        nome = re.sub(r"[^\w\-.]+", "_", r["url"].rstrip("/").split("/")[-1])[:120]
        if not nome.lower().endswith(".pdf"):
            nome += ".pdf"
        arq = baixar(r["url"] + "/@@download/file", PASTA / "fnde" / str(r["ano_pasta"]) / nome, "normas_fnde")
        regs.append({"titulo": r["titulo"], "url": r["url"], "arquivo": arq.relative_to(BRUTOS).as_posix() if arq else ""})
    return pd.DataFrame(regs)


def estaduais():
    """Confere número e data nas cópias de 04_dados (sem baixar nada do portal de MS)."""
    leg = FONTE_AB / "dados_brutos" / "legislacao"
    casos = [
        ("LC 300/2022 (MS)", leg / "LEI_COMPLEMENTAR_300_DE_24_08_2022.pdf", ["300", "2022"]),
        ("Lei 5.941/2022 (MS)", leg / "LEI_5941_DE_24_08_2022.pdf", ["5.941", "2022"]),
        ("Decreto 16.225/2023 (MS)", leg / "DECRETO_16225_DE_07_07_2023.pdf", ["16.225", "2023"]),
        ("Resolução/SEFAZ 3.354/2023", FONTE_AB / "dados_brutos" / "sefaz" / "Resolucao_SEFAZ_3354_de_19_12_2023.pdf", ["3.354"]),
        ("Resolução/SEFAZ 3.484/2025", FONTE_AB / "dados_brutos" / "sefaz" / "Resolucao_SEFAZ_3484_de_18_12_2025.pdf", ["3.484"]),
        ("Resolução/SEFAZ 3.424/2024", FONTE_AB / "dados_brutos" / "sefaz" / "resolucao_3424_de_2024.txt", ["3.424"]),
    ]
    regs = []
    for nome, p, chaves in casos:
        if not p.exists():
            regs.append({"norma": nome, "fonte": str(p), "situacao": "arquivo ausente", "evidencia": ""})
            continue
        t = p.read_text(encoding="utf-8", errors="replace") if p.suffix == ".txt" else texto_pdf(p)
        t = re.sub(r"\s+", " ", t)
        ok = all(c in t for c in chaves)
        regs.append({"norma": nome, "fonte": "cópia local em 04_dados_ICMS_IQE_VAAR: " + p.relative_to(FONTE_AB).as_posix(),
                     "situacao": "conferida na cópia local" if ok else "VERIFICAR", "evidencia": t[:300]})
    regs.append({"norma": "LC 57/1991 (MS), texto consolidado", "fonte": "aacpdappls.net.ms.gov.br (proibido a robôs)",
                 "situacao": "não conferida: o portal proíbe acesso automatizado; a cópia em 04_dados é anterior à LC 300/2022",
                 "evidencia": ""})
    regs.append({"norma": "Instruções normativas SED/MS do IQE-MS (ex.: IN n. 1 SUPED/SED/2024, citada no edital do "
                          "ano-base 2023)", "fonte": "Diário Oficial de MS",
                 "situacao": "não conferida: texto integral não está nas pastas e o portal de legislação proíbe robôs",
                 "evidencia": ""})
    return regs


def main():
    PASTA.mkdir(parents=True, exist_ok=True)
    regs = federais()
    df = listagem_fnde()
    if len(df):
        res = baixa_resolucoes_cif(df)
        res.to_csv(PASTA / "fnde_resolucoes_baixadas.csv", index=False, encoding="utf-8-sig")
        log(f"[normas] resoluções/leis do VAAR baixadas: {res['arquivo'].ne('').sum()} de {len(res)}")
    regs += estaduais()
    out = pd.DataFrame(regs)
    out["verificado_em"] = date.today().isoformat()
    DADOS.mkdir(parents=True, exist_ok=True)
    out.to_csv(DADOS / "normas_verificacao.csv", index=False, encoding="utf-8-sig")
    falhas = out["situacao"].str.contains("falha|VERIFICAR|ausente").sum()
    log(f"[normas] {len(out)} normas registradas; {falhas} com falha ou a verificar")
    return 0


if __name__ == "__main__":
    sys.exit(main())
