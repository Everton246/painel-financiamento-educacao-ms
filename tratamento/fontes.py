"""Etapa A: catálogo de fontes. Gera dados/fontes_status.csv e docs/catalogo_fontes.md a partir da lista FONTES abaixo
(levantamento feito em 24/11/2026) e do que está de fato na base (anos mínimo e máximo de cada fonte).

A coluna `verificacao` diz como `atualizar.py --verificar` confere se a fonte publicou período mais novo
("manual" = não há forma automática permitida; o autor confere).
A coluna `ultima_verificacao` é preenchida por atualizar.py --verificar (preservada entre execuções).
"""
from datetime import date

import pandas as pd

from comum import BASE, DADOS, DOCS

AB = "03_doutorado/04_dados_ICMS_IQE_VAAR"
IQ = "02_iquems/02_painel_educacao_ms"
# id, item, objetivo, fonte oficial, endereço, período disponível, periodicidade, acesso, restrições, já existe em,
# entra no painel, prefixos de indicador na base, situação, verificação, observação
FONTES = [
    ("normas_federais", "Normas federais do Fundeb/VAAR e do ICMS: EC 108/2020, Lei 14.113/2020 e alterações (Leis 14.276/2021, "
     "14.325/2022, 14.711/2023, LC 227/2026), Decreto 10.656/2021, LC 63/1990, EC 132/2023", "a, b, contexto", "Presidência da República (Planalto)",
     "https://www.planalto.gov.br/ccivil_03/", "1990–2026", "quando houver nova norma", "download (HTML)", "sem robots.txt (404)",
     "baixadas aqui (dados_brutos/normas/planalto)", "sim (Normas)", "", "na base", "planalto_lei14113",
     "Texto compilado da Lei 14.113 lista as leis que a alteraram; a verificação compara essa lista."),
    ("fnde_legislacao", "Resoluções da Comissão Intergovernamental de Financiamento (CIF) e demais atos do Fundeb", "b", "FNDE, página Legislação do Fundeb",
     "https://www.gov.br/fnde/pt-br/acesso-a-informacao/acoes-e-programas/financiamento/fundeb/legislacao", "2010–2026", "várias por ano",
     "interface de dados do portal gov.br (++api++) e download do PDF", "robots.txt não restringe /fnde", "baixadas aqui (dados_brutos/normas/fnde)",
     "sim (Normas)", "", "na base", "fnde_legislacao", "26 resoluções/leis sobre o VAAR baixadas em 24/11/2026."),
    ("normas_ms", "LC estadual 57/1991 com a LC 300/2022; Lei 5.941/2022; Decreto 16.225/2023", "a", "Portal de legislação de MS",
     "https://aacpdappls.net.ms.gov.br/appls/legislacao/", "1991–2023", "quando houver nova norma", "página interativa",
     "PROÍBE acesso automatizado: nada é baixado", f"cópias em {AB}/dados_brutos/legislacao (LC 300, Lei 5.941, Decreto 16.225)",
     "sim (Normas)", "", "parcial", "manual", "LC 57/1991 consolidada não conferida (a cópia .doc em 04_dados é anterior à LC 300)."),
    ("in_sed_iqe", "Instruções normativas da SED/MS sobre o IQE-MS e o SAEMS (ex.: IN n. 1 SUPED/SED/2024, citada nas notas dos editais)", "a",
     "SED/MS, Diário Oficial de MS", "Diário Oficial Eletrônico de MS (endereço não conferido por script)", "2022–2026", "anual", "Diário Oficial (busca interativa)",
     "servidor do DOE (www.spdo.ms.gov.br) sem resposta ao robots.txt em 24/11/2026: nada baixado; portal de legislação proíbe robôs", "não está nas pastas", "não (só citada)",
     "", "não coletado", "manual", "Necessária para interpretar 'coeficiente mínimo' e 'sem resultado completo'. Pedido ao autor."),
    ("editais_iqe", "Editais de resultado do IQE-MS (preliminares e finais)", "a", "SED/MS, Diário Oficial de MS", "Diário Oficial Eletrônico de MS (endereço não conferido por script)",
     "finais: anos-base 2022–2024; preliminar: ano-base 2025", "anual", "PDF do Diário Oficial", "ver in_sed_iqe",
     f"{AB}/resultados finais iqe ms e resultados prliminares iqe ms (trazidos pelo autor)", "sim (IQE-MS)", "iqe_", "parcial", "manual",
     "Falta o edital FINAL do ano-base 2025 (repasse de 2027)."),
    ("sefaz_resolucoes", "Resoluções da Sefaz/MS com os índices de participação no ICMS (Anexos II e III)", "a", "Sefaz/MS, Diário Oficial de MS",
     "portal de legislação de MS / DOE", "exercícios 2024–2026", "anual (dezembro)", "PDF/DOC", "portal de legislação proíbe robôs",
     f"{AB}/dados_brutos/sefaz (3.354, 3.424, 3.484)", "sim (ICMS Educacional)", "icms_iqe_indice", "na base", "manual",
     "A resolução do exercício de 2027 deve sair em dezembro de 2026."),
    ("repasses_icms", "Repasses anuais de ICMS por município", "a", "Portal da Transparência MS", "https://www.transparencia.ms.gov.br",
     "2024–2025 (2026 só no início de 2027)", "anual", "página interativa (PDF salvo pelo autor)", "robots.txt permite; página interativa sem endpoint de dados identificado",
     f"{AB}/repasses icms municipais", "sim (ICMS Educacional)", "icms_repasse_total", "parcial", "manual", "Repasse de 2026 pendente."),
    ("fnde_vaar", "VAAR: anexos de redes beneficiadas e valores, ajustes, listas de habilitação/inabilitação, cronogramas, portarias interministeriais",
     "b", "FNDE/MEC, página do Fundeb", "https://www.gov.br/fnde/pt-br/acesso-a-informacao/acoes-e-programas/financiamento/fundeb",
     "exercícios 2023–2026 (2026 previsto)", "várias publicações por exercício", "++api++ e download (PDF/XLSX)", "robots.txt não restringe /fnde",
     f"{AB}/dados_brutos/fnde", "sim (VAAR)", "vaar_", "na base", "fnde_vaar_2026",
     "Valor de 2026 = previsto (Portaria 11/2026); a verificação procura publicação nova na pasta de 2026 ou pasta de 2027."),
    ("fnde_fundeb_bb", "Fundeb por ente federado e origem de receita (contribuições, VAAF, VAAT, VAAR, tempo integral), pago pelo Banco do Brasil",
     "c (e b, informativo)", "FNDE", "https://www.gov.br/fnde/pt-br/acesso-a-informacao/acoes-e-programas/financiamento/fundeb/valores-repassados-2021-a-2025",
     "2021–2025", "anual", "++api++ e download (XLSX)", "robots.txt não restringe /fnde",
     f"2024 e 2025 em {AB}/dados_brutos/fnde/repasses_bb; 2021–2023 baixados aqui", "sim (Condições materiais)", "fundeb_", "na base", "fnde_fundeb_bb",
     "Ano civil de pagamento. Há um '2024 (1)' no portal, diferente do 2024 usado (ver conferência)."),
    ("siope_odata", "Siope: indicadores legais (% em MDE, % do Fundeb na remuneração), receitas, despesas por natureza e remuneração dos profissionais",
     "c", "FNDE/Siope, dados abertos (OData)", "https://www.fnde.gov.br/olinda-ide/servico/DADOS_ABERTOS_SIOPE/versao/v1/odata",
     "2021–2025 (esperado)", "bimestral (anual no 6º bimestre)", "API OData, sem login", "robots.txt não restringe",
     "não coletado", "sim, quando disponível (Condições materiais)", "siope_", "indisponível", "siope",
     "Erro 500 (NullPointerException) em todas as consultas de 24/11/2026, inclusive na documentação do serviço."),
    ("siope_arquivos", "Siope: arquivos analíticos (CSV)", "c", "FNDE/Siope", "https://www.gov.br/fnde/pt-br/assuntos/sistemas/siope/arquivos-dados-analiticos",
     "2008–2019", "—", "download (FTP)", "—", "não coletado", "não (fora do período 2021–2025)", "", "fora do período", "manual",
     "Página atualizada pela última vez em 16/08/2023."),
    ("siconfi_dca", "Siconfi: DCA Anexo I-E (despesa por função/subfunção: Educação) e I-C (receitas)", "c, contexto", "Tesouro Nacional (Siconfi)",
     "https://apidatalake.tesouro.gov.br/ords/siconfi/tt/dca", "2021–2025 (2025 conforme entrega dos municípios)", "anual (até 30/04)", "API pública", "sem robots.txt",
     "baixado aqui (dados_brutos/siconfi)", "sim (Condições materiais)", "educ_dca_", "na base", "siconfi_dca",
     "Reaproveita o método de 04_dados/scripts/13_siconfi_dca.py."),
    ("siconfi_msc", "Siconfi: Matriz de Saldos Contábeis (despesa da função Educação por natureza)", "c", "Tesouro Nacional (Siconfi)",
     "https://apidatalake.tesouro.gov.br/ords/siconfi/tt/msc_orcamentaria", "2021–2025", "mensal", "API pública", "sem robots.txt",
     "baixado aqui (dados_brutos/siconfi/msc)", "parcial (só município-ano em que confere com a DCA)", "educ_msc_", "parcial", "siconfi_dca",
     "Na maior parte dos município-ano, o total da função 12 na MSC não confere com a DCA; a composição só entra onde confere (±0,5%)."),
    ("siconfi_rreo8", "Siconfi: RREO Anexo 8 (MDE)", "c", "Tesouro Nacional (Siconfi)", "https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rreo",
     "não disponível para os municípios (o anexo é gerado pelo Siope)", "bimestral", "API pública", "sem robots.txt", "não", "não", "",
     "não publicado", "manual", "Consulta de 24/11/2026: o RREO de Campo Grande 2024 não traz o Anexo 08."),
    ("censo_microdados", "Censo Escolar: microdados de escola (infraestrutura das escolas municipais em atividade)", "c", "Inep",
     "https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/censo-escolar", "2007–2025", "anual", "download (ZIP)", "sem robots.txt",
     f"{IQ}/dados_brutos/inep/censo (sem novo download)", "sim (Condições materiais)", "infra_", "na base", "inep_censo", ""),
    ("censo_sinopse", "Censo Escolar: sinopse estatística (matrículas da rede municipal, Tabela 1.2)", "a, b", "Inep",
     "https://download.inep.gov.br/dados_abertos/sinopses_estatisticas/", "2024–2025 na base", "anual", "download (ZIP)", "sem robots.txt",
     f"{AB}/dados_brutos/inep e artigo icms educação", "sim (VAAR, Indicador)", "mat_municipal_sinopse_censo", "na base", "inep_sinopse", ""),
    ("inep_remuneracao", "Remuneração média dos docentes da educação básica por município e rede (RAIS)", "c", "Inep",
     "https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/indicadores-educacionais/remuneracao-media-dos-docentes",
     "2014–2021 (página atualizada em 30/12/2025 sem anos novos)", "irregular", "download (ZIP)", "sem robots.txt",
     f"{IQ}/dados_brutos/inep/remuneracao", "sim (Condições materiais, só 2021)", "rem_", "parcial", "inep_remuneracao", "2022 em diante não publicado."),
    ("saems", "SAEMS: participação e proficiência do 2º ano das redes municipais (insumo do IQE-MS)", "a (IQE-MS)", "CAEd/UFJF, área pública do SAEMS",
     "https://avaliacaoemonitoramentomatogrossodosul.caeddigital.net", "2022–2025", "anual", "página interativa (coletada com Playwright pelo painel do Iquems)",
     "área pública, sem login", f"{IQ}/dados/base/indicadores.parquet", "sim (IQE-MS)", "saems2_", "na base", "manual",
     "Atualizado pelo painel do Iquems."),
    ("ideb_saeb", "Ideb e Saeb da rede municipal (contexto das condicionalidades II e III do VAAR)", "b (contexto)", "Inep",
     "https://www.gov.br/inep/pt-br/areas-de-atuacao/pesquisas-estatisticas-e-indicadores/ideb/resultados", "2005–2025 (anos ímpares)", "bienal", "download (ZIP)",
     "sem robots.txt", f"{IQ}/dados/base/indicadores.parquet", "sim (dados disponíveis na base; ficha)", "ideb_", "na base", "manual",
     "Os indicadores do VAAR do Inep (atendimento e aprendizagem) de 2026 estão em 04_dados (xlsx) e não entram no painel."),
    ("inse", "Indicador de nível socioeconômico (Inse) da rede municipal", "contexto", "Inep", "https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/indicadores-educacionais", "2019, 2021, 2023", "bienal",
     "download", "sem robots.txt", f"{IQ}/dados/base/indicadores.parquet", "sim (IQE-MS)", "inse_", "na base", "manual", ""),
    ("ibge_pop", "População: Censo 2022 (porte) e estimativas", "a, b, contexto", "IBGE/SIDRA", "https://apisidra.ibge.gov.br",
     "Censo 2022; estimativas 2021, 2024–2026 (não há estimativa em 2022 e 2023)", "anual", "API", "sem robots.txt (404)", f"Censo 2022 em {AB}/dados_brutos/ibge; estimativas baixadas aqui",
     "sim", "pop_", "na base", "ibge_pop", ""),
    ("ibge_pib", "PIB dos municípios (contexto do componente estrutural)", "contexto", "IBGE/SIDRA, tabela 5938", "https://apisidra.ibge.gov.br",
     "2002–2023", "anual (defasagem de ~2 anos)", "API", "sem robots.txt (404)", "baixado aqui", "sim (Ficha)", "pib", "na base", "ibge_pib", ""),
    ("ibge_malha", "Malha municipal de MS", "painel", "IBGE", "https://servicodados.ibge.gov.br/api/v3/malhas/", "atual", "—", "API",
     "—", f"{IQ}/dados/base/malha_ms_municipios.geojson (copiada)", "sim (mapas)", "", "na base", "manual", ""),
    ("tesouro_transferencias", "Tesouro Transparente: transferências constitucionais (Fundeb por município)", "c (alternativa)", "Tesouro Nacional",
     "https://www.tesourotransparente.gov.br", "—", "mensal", "download", "robots.txt permite", "não", "não (o arquivo do FNDE já cobre 2021–2025)", "",
     "não coletado", "manual", "Fonte do próprio arquivo do FNDE (sisweb.tesouro.gov.br)."),
]
COLS = ["id", "item", "objetivo", "fonte_oficial", "endereco", "periodo_disponivel", "periodicidade", "acesso", "restricoes",
        "ja_existe_em", "entra_no_painel", "prefixo_na_base", "situacao", "verificacao", "observacao"]


def main():
    df = pd.DataFrame(FONTES, columns=COLS)
    ind = pd.read_parquet(BASE / "indicadores.parquet", columns=["indicador", "ano", "valor"]).dropna(subset=["valor"])
    ind["indicador"] = ind["indicador"].astype(str)
    ini, fim = [], []
    for p in df["prefixo_na_base"]:
        if not p:
            ini.append(""), fim.append("")
            continue
        a = ind.loc[ind["indicador"].str.startswith(p), "ano"]
        ini.append(str(int(a.min())) if len(a) else ""), fim.append(str(int(a.max())) if len(a) else "")
    df["ano_inicial_na_base"], df["ano_final_na_base"] = ini, fim
    antigo = DADOS / "fontes_status.csv"
    if antigo.exists():
        a = pd.read_csv(antigo, encoding="utf-8-sig", dtype=str)
        if "ultima_verificacao" in a:
            df = df.merge(a[["id", "ultima_verificacao", "resultado_verificacao"]], on="id", how="left")
    for c in ("ultima_verificacao", "resultado_verificacao"):
        if c not in df:
            df[c] = ""
    df["levantamento_em"] = "2026-11-24"
    df.to_csv(antigo, index=False, encoding="utf-8-sig")
    md = ["# Catálogo de fontes do painel", "",
          f"Gerado por `tratamento/fontes.py` em {date.today():%d/%m/%Y} a partir do levantamento de 24/11/2026. A mesma "
          "informação, em tabela, está em `dados/fontes_status.csv` e na página **Situação das fontes** do painel.", "",
          "Regras seguidas: só dados públicos, sem login; `robots.txt` consultado antes de qualquer download; o portal de "
          "legislação de MS (`aacpdappls.net.ms.gov.br`) proíbe acesso automatizado e nada foi baixado de lá; o que já "
          "estava em `04_dados_ICMS_IQE_VAAR` ou no painel do Iquems não foi baixado de novo.", ""]
    for obj, g in df.groupby(df["objetivo"].str.split(",").str[0].str.strip()):
        md.append(f"## Objetivo / uso: {obj}\n")
        for _, r in g.iterrows():
            md.append(f"### {r['item']}\n")
            md.append(f"- **Para que serve:** {r['objetivo']} · **Entra no painel:** {r['entra_no_painel']} · **Situação:** {r['situacao']}")
            md.append(f"- **Fonte oficial:** {r['fonte_oficial']} — {r['endereco']}")
            md.append(f"- **Período disponível:** {r['periodo_disponivel']} · **Periodicidade:** {r['periodicidade']} · "
                      f"**Na base:** {(r['ano_inicial_na_base'] + '–' + r['ano_final_na_base']) if r['ano_final_na_base'] else '—'}")
            md.append(f"- **Acesso:** {r['acesso']} · **Restrições:** {r['restricoes']}")
            md.append(f"- **Já existe em:** {r['ja_existe_em']}")
            if r["observacao"]:
                md.append(f"- **Observação:** {r['observacao']}")
            md.append("")
    normas = pd.read_csv(BASE / "normas.csv", encoding="utf-8-sig")
    md.append("## Normas (linha do tempo)\n")
    md.append("Lista completa em `dados/base/normas.csv` (página Normas do painel). Cada norma foi conferida no texto oficial "
              "baixado (Planalto), na página de legislação do Fundeb (FNDE) ou na cópia de 04_dados; a coluna de conferência "
              "diz qual.\n")
    md.append("| data | norma | publicação | repasse/exercício afetado | conferência |\n|---|---|---|---|---|")
    for _, r in normas.iterrows():
        md.append(f"| {r['data']} | {r['norma']} | {r['publicacao']} | {r['repasse_afetado']} | {r['situacao_conferencia']} |")
    DOCS.mkdir(parents=True, exist_ok=True)
    (DOCS / "catalogo_fontes.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"[fontes] {len(df)} fontes; situação: {df['situacao'].value_counts().to_dict()}")


if __name__ == "__main__":
    main()
