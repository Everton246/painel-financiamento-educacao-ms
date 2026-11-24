"""Linha do tempo das normas (dados/base/normas.csv), com conferência automática de cada entrada.

Cada norma traz um trecho que precisa aparecer no texto oficial baixado (Planalto), no título publicado na página de
legislação do Fundeb do FNDE, ou na cópia local em 04_dados_ICMS_IQE_VAAR. Se o trecho não for encontrado, a linha
fica marcada "NÃO CONFERIDA" (e aparece assim no painel). As descrições ("o que muda") são resumos para leitura; a
fonte é sempre o texto da norma.
"""
import re
import unicodedata

import pandas as pd
import pdfplumber

from comum import BASE, BRUTOS, FONTE_AB

PLAN = BRUTOS / "normas" / "planalto"
LISTA = BRUTOS / "normas" / "fnde_legislacao_fundeb_listagem.csv"


def norm(t):
    t = unicodedata.normalize("NFKD", str(t)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", t)


_cache = {}


def texto(fonte):
    if fonte in _cache:
        return _cache[fonte]
    p = fonte
    if p.suffix == ".htm":
        b = p.read_bytes()
        try:
            t = b.decode("utf-8")
        except UnicodeDecodeError:
            t = b.decode("latin-1")
        t = re.sub(r"<[^>]+>", " ", t)
    elif p.suffix == ".pdf":
        with pdfplumber.open(p) as pdf:
            t = " ".join((pg.extract_text() or "") for pg in pdf.pages[:6])
    else:
        t = p.read_text(encoding="utf-8", errors="replace")
    import html
    _cache[fonte] = norm(html.unescape(t))
    return _cache[fonte]


LOC = FONTE_AB / "dados_brutos"
# (data, política, norma, publicação, o que muda, exercício/repasse afetado, arquivo para conferir, trecho a conferir)
NORMAS = [
    ("1990-01-11", "ICMS", "Lei Complementar nº 63, de 11/01/1990", "DOU de 12/01/1990",
     "Critérios e prazos de crédito da cota municipal do ICMS; índices apurados em um ano valem a partir de 1º de janeiro do ano seguinte.",
     "todos os repasses", PLAN / "Lcp63.htm", "valor adicionado"),
    ("2020-08-26", "Fundeb/VAAR e ICMS", "Emenda Constitucional nº 108, de 26/08/2020", "DOU de 27/08/2020",
     "Fundeb permanente; complementação da União em três modalidades (VAAF, VAAT, VAAR); no ICMS, ao menos 10 pontos "
     "percentuais da cota municipal por indicadores de aprendizagem e equidade, com prazo de dois anos para a lei estadual.",
     "Fundeb a partir de 2021; ICMS conforme lei estadual", PLAN / "emc108.htm", "10 (dez) pontos percentuais"),
    ("2020-12-25", "Fundeb/VAAR", "Lei nº 14.113, de 25/12/2020", "DOU de 25/12/2020 (edição extra)",
     "Regulamenta o Fundeb; art. 14, § 1º: as cinco condicionalidades do VAAR (gestor escolar, participação no Saeb, "
     "redução de desigualdades, ICMS Educacional em lei estadual, referenciais curriculares alinhados à BNCC).",
     "VAAR a partir de 2023", PLAN / "l14113.htm", "condicionalidades"),
    ("2021-03-22", "Fundeb/VAAR", "Decreto nº 10.656, de 22/03/2021", "DOU de 23/03/2021",
     "Regulamenta a Lei nº 14.113/2020.", "Fundeb a partir de 2021", PLAN / "D10656.htm", "regulamenta a lei n"),
    ("2021-12-27", "Fundeb/VAAR", "Lei nº 14.276, de 27/12/2021", "DOU de 28/12/2021",
     "Altera a Lei nº 14.113/2020 (entre outros pontos, matrículas consideradas e conceito de profissionais da educação).",
     "Fundeb a partir de 2022", PLAN / "L14276.htm", "altera a lei n"),
    ("2022-04-12", "Fundeb/VAAR", "Lei nº 14.325, de 12/04/2022", "DOU de 13/04/2022",
     "Altera a Lei nº 14.113/2020 quanto aos recursos extraordinários recebidos por decisão judicial (precatórios do Fundef/Fundeb).",
     "—", PLAN / "L14325.htm", "altera a lei n"),
    ("2022-08-24", "ICMS", "Lei Complementar estadual nº 300, de 24/08/2022 (MS)", "Diário Oficial de MS",
     "Altera a LC nº 57/1991: valor adicionado no mínimo 65%; alínea g, 10% por indicadores de melhoria da aprendizagem e "
     "de aumento da equidade, considerado o nível socioeconômico dos educandos.",
     "repasses a partir de 2024", LOC / "legislacao" / "LEI_COMPLEMENTAR_300_DE_24_08_2022.pdf", "65%"),
    ("2022-08-24", "ICMS", "Lei estadual nº 5.941, de 24/08/2022 (MS)", "Diário Oficial de MS",
     "Indicadores do critério educacional da cota municipal do ICMS e criação do IQE-MS.",
     "repasses a partir de 2024", LOC / "legislacao" / "LEI_5941_DE_24_08_2022.pdf", "iqe"),
    ("2023-07-07", "ICMS", "Decreto estadual nº 16.225, de 07/07/2023 (MS)", "Diário Oficial de MS",
     "Regulamenta o IQE-MS: proficiência do 2º ano no SAEMS, padrões de desempenho, participação, aprovação e fator de "
     "municipalização (com o Inse); participação abaixo de 80% leva à menor nota apurada.",
     "repasses a partir de 2024", LOC / "legislacao" / "DECRETO_16225_DE_07_07_2023.pdf", "16.225"),
    ("2023-09-25", "ICMS", "Edital n. 3 IQE-MS/SED: resultado final, ano-base 2022", "DOE/MS nº 11.278, de 25/09/2023",
     "Coeficientes do IQE-MS do ano-base 2022.", "repasse de 2024", FONTE_AB / "resultados finais iqe ms" / "DO11278_25_09_2023.pdf", "iqe"),
    ("2023-10-30", "Fundeb/VAAR", "Lei nº 14.711, de 30/10/2023", "DOU de 31/10/2023",
     "Altera o art. 21 da Lei nº 14.113/2020 (instituição financeira para pagamento dos profissionais da educação).",
     "—", PLAN / "L14711.htm", "14.113"),
    ("2023-12-19", "ICMS", "Resolução/SEFAZ nº 3.354, de 19/12/2023", "DOE/MS nº 11.367, de 28/12/2023",
     "Índices definitivos de participação dos municípios no ICMS do exercício de 2024 (inclui a parcela do IQE-MS).",
     "repasse de 2024", LOC / "sefaz" / "Resolucao_SEFAZ_3354_de_19_12_2023.pdf", "3.354"),
    ("2023-12-20", "ICMS (transição)", "Emenda Constitucional nº 132, de 20/12/2023", "DOU de 21/12/2023",
     "Reforma tributária: o ICMS será substituído pelo IBS (alíquotas reduzidas de 2029 a 2032, extinção em 2033); a cota "
     "municipal do IBS mantém um critério educacional definido em lei estadual.", "a partir de 2029", PLAN / "emc132.htm", "aprendizagem"),
    ("2024-11-25", "ICMS", "Edital n. 2 IQE-MS/SED: resultado final, ano-base 2023", "DOE/MS nº 11.675, de 25/11/2024",
     "Coeficientes do IQE-MS do ano-base 2023.", "repasse de 2025", FONTE_AB / "resultados finais iqe ms" / "DO11675_25_11_2024.pdf", "iqe"),
    ("2024-12-19", "ICMS", "Resolução/SEFAZ nº 3.424, de 19/12/2024", "DOE/MS nº 11.701, de 20/12/2024",
     "Índices definitivos do exercício de 2025.", "repasse de 2025", LOC / "sefaz" / "resolucao_3424_de_2024.txt", "3.424"),
    ("2025-08-07", "ICMS", "Edital n. 2 IQE-MS/SED: resultado final, ano-base 2024", "DOE/MS nº 11.909, de 07/08/2025",
     "Coeficientes do IQE-MS do ano-base 2024.", "repasse de 2026", FONTE_AB / "resultados finais iqe ms" / "DO11909_07_08_2025.pdf", "iqe"),
    ("2025-12-18", "ICMS", "Resolução/SEFAZ nº 3.484, de 18/12/2025", "DOE/MS nº 12.031 (edição extra), de 19/12/2025",
     "Índices definitivos do exercício de 2026.", "repasse de 2026 (provisório até o fim do ano)",
     LOC / "sefaz" / "Resolucao_SEFAZ_3484_de_18_12_2025.pdf", "3.484"),
    ("2026-01-13", "ICMS e Fundeb (transição)", "Lei Complementar nº 227, de 13/01/2026", "DOU de 14/01/2026",
     "Institui o Comitê Gestor do IBS; dá nova redação ao art. 3º da LC nº 63/1990 (valor adicionado no mínimo 65%; até "
     "35% por lei estadual, com no mínimo 10 pontos percentuais por aprendizagem e equidade) e inclui o IBS na Lei nº 14.113/2020.",
     "transição tributária", PLAN / "Lcp227.htm", "227"),
    ("2026-05-20", "ICMS", "Edital IQE-MS: resultado preliminar, ano-base 2025", "DOE/MS nº 12.162, de 20/05/2026",
     "Resultado PRELIMINAR do IQE-MS do ano-base 2025 (o resultado final ainda não está nas pastas).", "repasse de 2027",
     FONTE_AB / "resultados prliminares iqe ms" / "DO12162_20_05_2026.pdf", "iqe"),
]
# Portarias interministeriais do VAAR (arquivos em 04_dados_ICMS_IQE_VAAR/dados_brutos/fnde)
PORTARIAS = [
    ("2024-12-23", "Portaria Interministerial MEC/MF nº 13, de 23/12/2024", "VAAR 2024: redes beneficiadas e valores (Anexo V); cronograma (Anexo VI).", "VAAR de 2024", "Portaria Interministerial MECMF nº 13, de 23 de Dezembro de 2024.pdf"),
    ("2025-04-28", "Portaria Interministerial MEC/MF nº 3, de 28/04/2025", "Ajuste do VAAR do exercício de 2024 (Anexo III).", "VAAR de 2024 (ajuste)", None),
    ("2025-12-29", "Portaria Interministerial MEC/MF nº 13, de 29/12/2025", "VAAR 2025: redes beneficiadas e valores (Anexo V).", "VAAR de 2025", "Portaria Interm. Mec MF nº 13, de 29 de Dezembro de 2025.pdf"),
    ("2025-12-29", "Portaria Interministerial MEC/MF nº 14, de 29/12/2025", "Previsão do VAAR 2026 (1ª publicação).", "VAAR de 2026 (previsto)", "Portaria Interna -  Mec MF nº 14, de 29 de Dezembro de 2025.pdf"),
    ("2026-04-29", "Portaria Interministerial MEC/MF nº 5, de 29/04/2026", "Ajuste do VAAR do exercício de 2025.", "VAAR de 2025 (ajuste)", "Portaria Interm. Mec MF nº 5, de 29 de Abril de 2026.pdf"),
    ("2026-04-29", "Portaria Interministerial MEC/MF nº 6, de 29/04/2026", "Previsão do VAAR 2026 (2ª publicação).", "VAAR de 2026 (previsto)", "Portaria Interm. Mec MF nº 6, de 29 de Abril de 2026.pdf"),
    ("2026-04-29", "Portaria Interministerial MEC/MF nº 7, de 29/04/2026", "Revisão do indicador VAAR-Aprendizagem; altera só o ajuste do exercício de 2023.", "VAAR de 2023 (não afeta 2024–2026)", "Portaria Interm. Mec MF nº 7, de 29 de Abril de 2026.pdf"),
    ("2026-08-28", "Portaria Interministerial MEC/MF nº 11, de 28/08/2026", "Previsão do VAAR 2026 (3ª publicação; a usada no painel).", "VAAR de 2026 (previsto)", "Portaria Interministerial MEC MF Nº 11, de 28 de agosto de 2026_compressed.pdf"),
]


def conferir(arquivo, trecho):
    if arquivo is None:
        return "NÃO CONFERIDA (texto não está nas pastas)", ""
    if not arquivo.exists():
        return "NÃO CONFERIDA (arquivo ausente)", str(arquivo)
    ok = norm(trecho) in texto(arquivo)
    rel = arquivo.relative_to(FONTE_AB.parent.parent).as_posix() if FONTE_AB.parent.parent in arquivo.parents else str(arquivo)
    return ("conferida no texto" if ok else "NÃO CONFERIDA (trecho não encontrado)"), rel


def main():
    linhas = []
    for data, pol, nome, pub, muda, afeta, arq, trecho in NORMAS:
        sit, rel = conferir(arq, trecho) if arq is not None else conferir(None, None)
        linhas.append({"data": data, "politica": pol, "norma": nome, "publicacao": pub, "o_que_muda": muda,
                       "repasse_afetado": afeta, "situacao_conferencia": sit, "arquivo_conferido": rel})
    pasta_port = FONTE_AB / "dados_brutos" / "fnde" / "portarias"
    for data, nome, muda, afeta, arq in PORTARIAS:
        if arq is None:
            sit, rel = "conferida em 04_dados (anexo xlsx do ajuste; ver LOG, sessão 1)", "04_dados_ICMS_IQE_VAAR/dados_brutos/fnde/vaar_2024/AjustedaComplementaoVAAR.xlsx"
        else:
            num = re.search(r"nº (\d+)", nome).group(1)
            sit, rel = conferir(pasta_port / arq, num)
        linhas.append({"data": data, "politica": "Fundeb/VAAR", "norma": nome, "publicacao": "DOU", "o_que_muda": muda,
                       "repasse_afetado": afeta, "situacao_conferencia": sit, "arquivo_conferido": rel})
    # Resoluções da Comissão Intergovernamental (CIF) sobre o VAAR, como listadas pelo FNDE (título e descrição oficiais)
    if LISTA.exists():
        l = pd.read_csv(LISTA, encoding="utf-8-sig")
        t = (l["titulo"].fillna("") + " " + l["descricao"].fillna("")).map(norm)
        cif = l[t.str.contains("resolu") & t.str.contains("condicionalidade|vaar|indicadores de nivel socioeconomico|nse")]
        meses = {m: i for i, m in enumerate(["janeiro", "fevereiro", "marco", "abril", "maio", "junho", "julho", "agosto",
                                             "setembro", "outubro", "novembro", "dezembro"], 1)}
        for _, r in cif.iterrows():
            tt = norm(r["titulo"])
            m = re.search(r"(\d{1,2})o? de ([a-z]+) de (\d{4})", tt)
            data = f"{m.group(3)}-{meses.get(m.group(2), 1):02d}-{int(m.group(1)):02d}" if m else f"{r['ano_pasta']}-01-01"
            ex = re.findall(r"(?:exercicio de|distribuicao [^.]{0,60}?em|vigencia no exercicio de) (\d{4})", norm(r["descricao"]))
            linhas.append({"data": data, "politica": "Fundeb/VAAR (CIF)", "norma": r["titulo"], "publicacao": "DOU (listada pelo FNDE)",
                           "o_que_muda": r["descricao"], "repasse_afetado": ("VAAR de " + ex[0]) if ex else "ver texto",
                           "situacao_conferencia": "conferida na página de legislação do Fundeb (FNDE)", "arquivo_conferido": r["url"]})
    df = pd.DataFrame(linhas).sort_values("data").reset_index(drop=True)
    df.to_csv(BASE / "normas.csv", index=False, encoding="utf-8-sig")
    nao = df["situacao_conferencia"].str.startswith("NÃO")
    print(f"[normas] {len(df)} normas na linha do tempo; não conferidas: {nao.sum()}")
    for _, r in df[nao].iterrows():
        print("   -", r["norma"], "|", r["situacao_conferencia"])


if __name__ == "__main__":
    main()
