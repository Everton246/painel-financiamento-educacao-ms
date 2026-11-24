"""Coleta 02: Fundeb por ente federado e origem de receita (FNDE, valores repassados pelo Banco do Brasil).

Pasta do portal: .../financiamento/fundeb/valores-repassados-2021-a-2025 (gov.br; robots.txt não restringe /fnde).
Traz, por município: receita de contribuições (fundo estadual), complementações da União VAAF, VAAT e VAAR (bruto,
dedução, líquido) e, em 2025, fomento ao tempo integral. Ano civil de pagamento (inclui ajustes de anos anteriores):
não é o "valor do exercício" das portarias.

Os arquivos de 2024 e 2025 já estão em 04_dados_ICMS_IQE_VAAR/dados_brutos/fnde/repasses_bb e NÃO são baixados de
novo (o tratamento lê de lá). Baixa 2021, 2022, 2023 e qualquer arquivo novo que apareça na pasta (ex.: 2026), e o
"2024 (1)" do portal, para registrar se difere do 2024 usado no 04_dados.
"""
import sys
import unicodedata

from comum import BRUTOS, FONTE_AB, baixar, get_json, log, salvar_json, sha256

API = ("https://www.gov.br/fnde/++api++/pt-br/acesso-a-informacao/acoes-e-programas/financiamento/fundeb/"
       "valores-repassados-2021-a-2025")
PASTA = BRUTOS / "fnde_fundeb"
JA_EXISTEM = FONTE_AB / "dados_brutos" / "fnde" / "repasses_bb"


def nfc(t):
    """O portal e o Windows gravam o acento de 'Exercício' de formas diferentes; compara na forma NFC."""
    return unicodedata.normalize("NFC", t)


def main():
    try:
        d = get_json(API, params={"expand": "items"})
    except Exception as ex:  # noqa: BLE001
        log(f"[fundeb] listagem falhou: {ex}")
        return 1
    salvar_json([{k: it.get(k) for k in ("title", "@id", "modified")} for it in d.get("items", [])],
                PASTA / "listagem_portal.json")
    existentes = {nfc(p.name): p for p in JA_EXISTEM.glob("*.xlsx")}
    falhas = 0
    for it in d.get("items", []):
        if it.get("@type") != "File":
            continue
        nome = nfc(it["title"].strip())
        if nome in existentes:
            log(f"[fundeb] já existe em 04_dados, não baixado: {nome}")
            continue
        arq = baixar(it["@id"] + "/@@download/file", PASTA / nome, "fnde_fundeb")
        if arq is None:
            falhas += 1
            continue
        irmao = existentes.get(nome.replace(" (1)", ""))
        if irmao is not None:
            igual = sha256(irmao) == sha256(arq)
            log(f"[fundeb] {nome} {'é idêntico' if igual else 'DIFERE'} de {irmao.name} (04_dados)")
    log(f"[fundeb] concluído; falhas: {falhas}")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
