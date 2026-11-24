"""Coleta 03: Siope (FNDE), dados abertos por município de MS — indicadores legais, despesas e remuneração.

Fonte: serviço OData do FNDE (Olinda), https://www.fnde.gov.br/olinda-ide/servico/DADOS_ABERTOS_SIOPE/versao/v1/odata
(recursos Indicadores_Siope, Despesas_Siope, Despesas_Funcao_Educacao_Siope, Receita_Siope, Remuneracao_Siope;
parâmetros Ano_Consulta, Num_Peri = bimestre 1–6, Sig_UF). Os nomes dos recursos foram tirados da documentação do
pacote R `tesouror` (CRAN), porque a página de documentação do próprio serviço também respondia com erro.
robots.txt de www.fnde.gov.br: não restringe /olinda-ide (consultado em 24/11/2026).

Situação em 24/11/2026: o serviço respondeu "500 Internal Server Error" (java.lang.NullPointerException) a todas as
consultas, inclusive à página de documentação. Os arquivos analíticos do Siope no portal do FNDE só vão até 2019.
O script tenta de novo a cada atualização: primeiro uma amostra (Taquarussu, 2024, 6º bimestre); se ela vier, baixa
o 6º bimestre de 2021 a 2025 de MS. Se falhar, registra e sai sem interromper as outras fontes.
"""
import gzip
import json
import sys

from comum import BRUTOS, get_json, log

SERVICO = "https://www.fnde.gov.br/olinda-ide/servico/DADOS_ABERTOS_SIOPE/versao/v1/odata/"
RECURSOS = ["Indicadores_Siope", "Despesas_Funcao_Educacao_Siope", "Despesas_Siope", "Receita_Siope"]
ANOS = range(2021, 2026)
PASTA = BRUTOS / "siope"


def consulta(recurso, ano, bimestre=6, filtro=None, top=None):
    url = SERVICO + f"{recurso}(Ano_Consulta=@Ano_Consulta,Num_Peri=@Num_Peri,Sig_UF=@Sig_UF)"
    p = {"@Ano_Consulta": ano, "@Num_Peri": bimestre, "@Sig_UF": "'MS'", "$format": "json"}
    if filtro:
        p["$filter"] = filtro
    if top:
        p["$top"] = top
    return get_json(url, params=p, timeout=180).get("value", [])


def main():
    try:
        amostra = consulta("Indicadores_Siope", 2024, filtro="COD_MUNI eq 5007976", top=50)
    except Exception as ex:  # noqa: BLE001
        log(f"[siope] serviço indisponível (amostra Taquarussu 2024): {ex}")
        return 1
    log(f"[siope] amostra OK: {len(amostra)} linhas")
    PASTA.mkdir(parents=True, exist_ok=True)
    falhas = 0
    for rec in RECURSOS:
        for ano in ANOS:
            arq = PASTA / f"{rec}_{ano}_bim6_MS.json.gz"
            if arq.exists():
                continue
            try:
                v = consulta(rec, ano)
                with gzip.open(arq, "wt", encoding="utf-8") as f:
                    json.dump(v, f, ensure_ascii=False)
                log(f"[siope] {rec} {ano}: {len(v)} linhas")
            except Exception as ex:  # noqa: BLE001
                falhas += 1
                log(f"[siope] {rec} {ano} falhou: {ex}")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
