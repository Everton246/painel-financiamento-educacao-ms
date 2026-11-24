"""Coleta 06: Fundeb por EXERCÍCIO (valor devido ao ente no exercício), para comparar com o valor pago no ano civil
(arquivo do Banco do Brasil, coleta 02).

Exercício financeiro = ano civil (1º/jan a 31/dez). A diferença está no registro: as portarias do FNDE/MEC trazem o valor
que cabe ao ente NO EXERCÍCIO; o arquivo do Banco do Brasil traz o que foi PAGO no ano (a última parcela das
complementações de um exercício é paga em janeiro do ano seguinte, e os ajustes do exercício saem em abril/maio do ano
seguinte).

Planilhas disponíveis em formato de dados no portal do FNDE (consulta de 24/11/2026; pastas listadas com b_size=1000):
- exercício 2025: "1. Receita total do Fundeb por ente federado", 6ª publicação (Portaria Interministerial MEC/MF nº 5,
  de 29/04/2026, que também traz o ajuste do VAAR de 2025): contribuição + VAAF + VAAT + VAAR por ente.
- exercício 2026 (PREVISTO): mesma tabela da 3ª publicação (Portaria nº 11/2026).
- exercício 2024: Anexo II da Portaria nº 3/2025 (ajuste da complementação VAAT: devida × distribuída, por ente). A
  receita da contribuição de 2024 por ente só está em PDF (não coletada); o VAAR devido de 2024 já está na base (04_dados).
- exercícios 2021–2023: só PDFs de previsão no portal; não coletados.
"""
import sys

from comum import BRUTOS, baixar, log

B = "https://www.gov.br/fnde/pt-br/acesso-a-informacao/acoes-e-programas/financiamento/fundeb"
PASTA = BRUTOS / "fnde_fundeb_exercicio"
ARQS = {
    "1.ReceitatotaldoFundebporentefederado_2025_P5-2026.xlsx":
        "/2025-1/6-publicacao-2013-portaria-mec-mf-n-5-de-29-de-abril-de-2026/1.ReceitatotaldoFundebporentefederado.xlsx",
    "1-receita-total-do-fundeb-por-ente-federado-p-11_2026.xlsx":
        "/2026-1/publicacoes-2026/3-publicacoes/1-receita-total-do-fundeb-por-ente-federado-p-11.xlsx",
    "AjustedaComplementaoVAAT_2024_P3-2025.xlsx": "/2025-1/AjustedaComplementaoVAAT.xlsx",
}


def main():
    falhas = 0
    for nome, cam in ARQS.items():
        arq = baixar(B + cam + "/@@download/file", PASTA / nome, "fnde_fundeb_exercicio",
                     obs=f"nome no portal: {cam.split('/')[-1]}")
        falhas += arq is None
        log(f"[fundeb exercício] {nome}: {'ok' if arq else 'FALHA'}")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
