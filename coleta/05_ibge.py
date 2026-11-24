"""Coleta 05: IBGE — contexto dos municípios (componente estrutural do ICMS Educacional).

- PIB dos municípios a preços correntes (SIDRA, tabela 5938, variável 37, mil reais), 2021 a 2023 (último publicado
  em 24/11/2026: 2023).
- Estimativas de população (SIDRA, tabela 6579, variável 9324), 2021, 2024, 2025 e 2026 (não há estimativa em 2022 e 2023,
  anos do Censo e da contagem: a pesquisa usa a população do Censo 2022, já baixada pelo 04_dados).
- IPCA (SIDRA, tabela 1737, variável 2266, número-índice), jan/2021 a dez/2025, para a aba de valores corrigidos.
- Malha municipal: não é baixada; o tratamento copia a do painel do Iquems (dados/base/malha_ms_municipios.geojson).
apisidra.ibge.gov.br: robots.txt inexistente (404, consultado em 24/11/2026).
"""
import sys

from comum import BRUTOS, baixar, log

PASTA = BRUTOS / "ibge"
CONSULTAS = {
    "pib_municipios_sidra5938.json": "https://apisidra.ibge.gov.br/values/t/5938/n6/in%20n3%2050/v/37/p/2021,2022,2023",
    "estimativa_populacao_sidra6579_2021_2024_2025_2026.json":
        "https://apisidra.ibge.gov.br/values/t/6579/n6/in%20n3%2050/v/9324/p/2021,2024,2025,2026",
    # IPCA, número-índice mensal (dez/1993 = 100), jan/2021 a dez/2025: correção pela inflação (página de condições)
    "ipca_numero_indice_sidra1737_2021_2025.json":
        "https://apisidra.ibge.gov.br/values/t/1737/n1/all/v/2266/p/" + ",".join(f"{a}{m:02d}" for a in range(2021, 2026) for m in range(1, 13)),
}


def main():
    falhas = 0
    for nome, url in CONSULTAS.items():
        arq = baixar(url, PASTA / nome, "ibge")
        falhas += arq is None
        log(f"[ibge] {nome}: {'ok' if arq else 'FALHA'}")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
