"""Coleta 04: Siconfi (Tesouro Nacional), API pública apidatalake.tesouro.gov.br — 79 municípios, 2021 a 2025.

- DCA, Anexo I-E (despesa por função e subfunção): despesa empenhada, liquidada e paga em Educação (função 12).
- DCA, Anexo I-C (receitas orçamentárias): receita total do município (contexto).
- MSC de encerramento (MSCE, mês 12), classe 6 (execução da despesa): despesa da função 12 por natureza (pessoal,
  material de consumo, obras e instalações, equipamentos...), base das frentes do objetivo c enquanto o Siope está fora
  do ar. A soma da MSC na função 12 é conferida contra a DCA I-E (tratamento/conferir.py).

Sem robots.txt no servidor (consultado em 29/10/2026 pelo 04_dados e em 24/11/2026). Respostas gravadas sem alteração
(JSON compactado) em dados_brutos/siconfi/. O que já foi baixado não é baixado de novo.
Uso: python coleta/04_siconfi.py [--amostra]   (amostra = Taquarussu, 2024)
"""
import gzip
import json
import sys
import time

from comum import BRUTOS, get_json, log, municipios

API = "https://apidatalake.tesouro.gov.br/ords/siconfi/tt/"
ANOS = range(2021, 2026)
PASTA = BRUTOS / "siconfi"


def todas_paginas(recurso, params):
    itens, offset = [], 0
    while True:
        d = get_json(API + recurso, params={**params, "offset": offset} if offset else params, timeout=300)
        itens += d.get("items", [])
        if not d.get("hasMore"):
            return itens
        offset += d.get("limit") or len(d.get("items", [])) or 5000


def guardar(arq, recurso, params):
    if arq.exists():
        return None
    try:
        itens = todas_paginas(recurso, params)
    except Exception as ex:  # noqa: BLE001
        log(f"[siconfi] falha {arq.name}: {ex}")
        return False
    arq.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(arq, "wt", encoding="utf-8") as f:
        json.dump({"consulta": API + recurso, "parametros": params, "baixado_em": time.strftime("%Y-%m-%d %H:%M"),
                   "items": itens}, f, ensure_ascii=False)
    time.sleep(0.3)
    return True


def main():
    amostra = "--amostra" in sys.argv
    cods = ["5007976"] if amostra else municipios()["cod_ibge"].tolist()
    anos = [2024] if amostra else list(ANOS)
    falhas = n = 0
    for ano in anos:
        for cod in cods:
            tarefas = [
                (PASTA / "dca_I-E" / f"dca_{ano}_I-E_{cod}.json.gz", "dca",
                 {"an_exercicio": ano, "no_anexo": "DCA-Anexo I-E", "id_ente": cod}),
                (PASTA / "dca_I-C" / f"dca_{ano}_I-C_{cod}.json.gz", "dca",
                 {"an_exercicio": ano, "no_anexo": "DCA-Anexo I-C", "id_ente": cod}),
                (PASTA / "msc" / f"msce_{ano}_12_classe6_{cod}.json.gz", "msc_orcamentaria",
                 {"id_ente": cod, "an_referencia": ano, "me_referencia": 12, "co_tipo_matriz": "MSCE",
                  "classe_conta": 6, "id_tv": "period_change"}),
            ]
            for arq, rec, par in tarefas:
                r = guardar(arq, rec, par)
                falhas += r is False
                n += r is True
        log(f"[siconfi] {ano}: concluído (arquivos novos até agora: {n}; falhas: {falhas})")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
