# Catálogo de fontes do painel

Gerado por `tratamento/fontes.py` em 24/11/2026 a partir do levantamento de 24/11/2026. A mesma informação, em tabela, está em `dados/fontes_status.csv` e na página **Situação das fontes** do painel.

Regras seguidas: só dados públicos, sem login; `robots.txt` consultado antes de qualquer download; o portal de legislação de MS (`aacpdappls.net.ms.gov.br`) proíbe acesso automatizado e nada foi baixado de lá; o que já estava em `04_dados_ICMS_IQE_VAAR` ou no painel do Iquems não foi baixado de novo.

## Objetivo / uso: a

### Normas federais do Fundeb/VAAR e do ICMS: EC 108/2020, Lei 14.113/2020 e alterações (Leis 14.276/2021, 14.325/2022, 14.711/2023, LC 227/2026), Decreto 10.656/2021, LC 63/1990, EC 132/2023

- **Para que serve:** a, b, contexto · **Entra no painel:** sim (Normas) · **Situação:** na base
- **Fonte oficial:** Presidência da República (Planalto) — https://www.planalto.gov.br/ccivil_03/
- **Período disponível:** 1990–2026 · **Periodicidade:** quando houver nova norma · **Na base:** —
- **Acesso:** download (HTML) · **Restrições:** sem robots.txt (404)
- **Já existe em:** baixadas aqui (dados_brutos/normas/planalto)
- **Observação:** Texto compilado da Lei 14.113 lista as leis que a alteraram; a verificação compara essa lista.

### LC estadual 57/1991 com a LC 300/2022; Lei 5.941/2022; Decreto 16.225/2023

- **Para que serve:** a · **Entra no painel:** sim (Normas) · **Situação:** parcial
- **Fonte oficial:** Portal de legislação de MS — https://aacpdappls.net.ms.gov.br/appls/legislacao/
- **Período disponível:** 1991–2023 · **Periodicidade:** quando houver nova norma · **Na base:** —
- **Acesso:** página interativa · **Restrições:** PROÍBE acesso automatizado: nada é baixado
- **Já existe em:** cópias em 03_doutorado/04_dados_ICMS_IQE_VAAR/dados_brutos/legislacao (LC 300, Lei 5.941, Decreto 16.225)
- **Observação:** LC 57/1991 consolidada não conferida (a cópia .doc em 04_dados é anterior à LC 300).

### Instruções normativas da SED/MS sobre o IQE-MS e o SAEMS (ex.: IN n. 1 SUPED/SED/2024, citada nas notas dos editais)

- **Para que serve:** a · **Entra no painel:** não (só citada) · **Situação:** não coletado
- **Fonte oficial:** SED/MS, Diário Oficial de MS — Diário Oficial Eletrônico de MS (endereço não conferido por script)
- **Período disponível:** 2022–2026 · **Periodicidade:** anual · **Na base:** —
- **Acesso:** Diário Oficial (busca interativa) · **Restrições:** servidor do DOE (www.spdo.ms.gov.br) sem resposta ao robots.txt em 24/11/2026: nada baixado; portal de legislação proíbe robôs
- **Já existe em:** não está nas pastas
- **Observação:** Necessária para interpretar 'coeficiente mínimo' e 'sem resultado completo'. Pedido ao autor.

### Editais de resultado do IQE-MS (preliminares e finais)

- **Para que serve:** a · **Entra no painel:** sim (IQE-MS) · **Situação:** parcial
- **Fonte oficial:** SED/MS, Diário Oficial de MS — Diário Oficial Eletrônico de MS (endereço não conferido por script)
- **Período disponível:** finais: anos-base 2022–2024; preliminar: ano-base 2025 · **Periodicidade:** anual · **Na base:** 2022–2024
- **Acesso:** PDF do Diário Oficial · **Restrições:** ver in_sed_iqe
- **Já existe em:** 03_doutorado/04_dados_ICMS_IQE_VAAR/resultados finais iqe ms e resultados prliminares iqe ms (trazidos pelo autor)
- **Observação:** Falta o edital FINAL do ano-base 2025 (repasse de 2027).

### Resoluções da Sefaz/MS com os índices de participação no ICMS (Anexos II e III)

- **Para que serve:** a · **Entra no painel:** sim (ICMS Educacional) · **Situação:** na base
- **Fonte oficial:** Sefaz/MS, Diário Oficial de MS — portal de legislação de MS / DOE
- **Período disponível:** exercícios 2024–2026 · **Periodicidade:** anual (dezembro) · **Na base:** 2024–2026
- **Acesso:** PDF/DOC · **Restrições:** portal de legislação proíbe robôs
- **Já existe em:** 03_doutorado/04_dados_ICMS_IQE_VAAR/dados_brutos/sefaz (3.354, 3.424, 3.484)
- **Observação:** A resolução do exercício de 2027 deve sair em dezembro de 2026.

### Repasses anuais de ICMS por município

- **Para que serve:** a · **Entra no painel:** sim (ICMS Educacional) · **Situação:** parcial
- **Fonte oficial:** Portal da Transparência MS — https://www.transparencia.ms.gov.br
- **Período disponível:** 2024–2025 (2026 só no início de 2027) · **Periodicidade:** anual · **Na base:** 2024–2025
- **Acesso:** página interativa (PDF salvo pelo autor) · **Restrições:** robots.txt permite; página interativa sem endpoint de dados identificado
- **Já existe em:** 03_doutorado/04_dados_ICMS_IQE_VAAR/repasses icms municipais
- **Observação:** Repasse de 2026 pendente.

### Censo Escolar: sinopse estatística (matrículas da rede municipal, Tabela 1.2)

- **Para que serve:** a, b · **Entra no painel:** sim (VAAR, Indicador) · **Situação:** na base
- **Fonte oficial:** Inep — https://download.inep.gov.br/dados_abertos/sinopses_estatisticas/
- **Período disponível:** 2024–2025 na base · **Periodicidade:** anual · **Na base:** 2024–2025
- **Acesso:** download (ZIP) · **Restrições:** sem robots.txt
- **Já existe em:** 03_doutorado/04_dados_ICMS_IQE_VAAR/dados_brutos/inep e artigo icms educação

### População: Censo 2022 (porte) e estimativas

- **Para que serve:** a, b, contexto · **Entra no painel:** sim · **Situação:** na base
- **Fonte oficial:** IBGE/SIDRA — https://apisidra.ibge.gov.br
- **Período disponível:** Censo 2022; estimativas 2021, 2024–2026 (não há estimativa em 2022 e 2023) · **Periodicidade:** anual · **Na base:** 2021–2026
- **Acesso:** API · **Restrições:** sem robots.txt (404)
- **Já existe em:** Censo 2022 em 03_doutorado/04_dados_ICMS_IQE_VAAR/dados_brutos/ibge; estimativas baixadas aqui

## Objetivo / uso: a (IQE-MS)

### SAEMS: participação e proficiência do 2º ano das redes municipais (insumo do IQE-MS)

- **Para que serve:** a (IQE-MS) · **Entra no painel:** sim (IQE-MS) · **Situação:** na base
- **Fonte oficial:** CAEd/UFJF, área pública do SAEMS — https://avaliacaoemonitoramentomatogrossodosul.caeddigital.net
- **Período disponível:** 2022–2025 · **Periodicidade:** anual · **Na base:** 2022–2025
- **Acesso:** página interativa (coletada com Playwright pelo painel do Iquems) · **Restrições:** área pública, sem login
- **Já existe em:** 02_iquems/02_painel_educacao_ms/dados/base/indicadores.parquet
- **Observação:** Atualizado pelo painel do Iquems.

## Objetivo / uso: b

### Resoluções da Comissão Intergovernamental de Financiamento (CIF) e demais atos do Fundeb

- **Para que serve:** b · **Entra no painel:** sim (Normas) · **Situação:** na base
- **Fonte oficial:** FNDE, página Legislação do Fundeb — https://www.gov.br/fnde/pt-br/acesso-a-informacao/acoes-e-programas/financiamento/fundeb/legislacao
- **Período disponível:** 2010–2026 · **Periodicidade:** várias por ano · **Na base:** —
- **Acesso:** interface de dados do portal gov.br (++api++) e download do PDF · **Restrições:** robots.txt não restringe /fnde
- **Já existe em:** baixadas aqui (dados_brutos/normas/fnde)
- **Observação:** 26 resoluções/leis sobre o VAAR baixadas em 24/11/2026.

### VAAR: anexos de redes beneficiadas e valores, ajustes, listas de habilitação/inabilitação, cronogramas, portarias interministeriais

- **Para que serve:** b · **Entra no painel:** sim (VAAR) · **Situação:** na base
- **Fonte oficial:** FNDE/MEC, página do Fundeb — https://www.gov.br/fnde/pt-br/acesso-a-informacao/acoes-e-programas/financiamento/fundeb
- **Período disponível:** exercícios 2023–2026 (2026 previsto) · **Periodicidade:** várias publicações por exercício · **Na base:** 2024–2026
- **Acesso:** ++api++ e download (PDF/XLSX) · **Restrições:** robots.txt não restringe /fnde
- **Já existe em:** 03_doutorado/04_dados_ICMS_IQE_VAAR/dados_brutos/fnde
- **Observação:** Valor de 2026 = previsto (Portaria 11/2026); a verificação procura publicação nova na pasta de 2026 ou pasta de 2027.

## Objetivo / uso: b (contexto)

### Ideb e Saeb da rede municipal (contexto das condicionalidades II e III do VAAR)

- **Para que serve:** b (contexto) · **Entra no painel:** sim (dados disponíveis na base; ficha) · **Situação:** na base
- **Fonte oficial:** Inep — https://www.gov.br/inep/pt-br/areas-de-atuacao/pesquisas-estatisticas-e-indicadores/ideb/resultados
- **Período disponível:** 2005–2025 (anos ímpares) · **Periodicidade:** bienal · **Na base:** 2019–2025
- **Acesso:** download (ZIP) · **Restrições:** sem robots.txt
- **Já existe em:** 02_iquems/02_painel_educacao_ms/dados/base/indicadores.parquet
- **Observação:** Os indicadores do VAAR do Inep (atendimento e aprendizagem) de 2026 estão em 04_dados (xlsx) e não entram no painel.

## Objetivo / uso: c

### Fundeb devido no EXERCÍCIO por ente (receita total por ente federado; ajuste da VAAT)

- **Para que serve:** c · **Entra no painel:** sim (Condições materiais: exercício × ano civil) · **Situação:** parcial
- **Fonte oficial:** FNDE/MEC, portarias interministeriais — https://www.gov.br/fnde/pt-br/acesso-a-informacao/acoes-e-programas/financiamento/fundeb
- **Período disponível:** planilhas: 2024 (só VAAT), 2025 (completo), 2026 (previsto); 2021–2023 só em PDF · **Periodicidade:** várias publicações por exercício · **Na base:** 2024–2026
- **Acesso:** ++api++ e download (XLSX) · **Restrições:** robots.txt não restringe /fnde
- **Já existe em:** baixado aqui (dados_brutos/fnde_fundeb_exercicio)
- **Observação:** Comparado com o pago no ano civil (Banco do Brasil): contribuição quase igual; complementações divergem.

### Siope: indicadores legais (% em MDE, % do Fundeb na remuneração), receitas, despesas por natureza e remuneração dos profissionais

- **Para que serve:** c · **Entra no painel:** sim, quando disponível (Condições materiais) · **Situação:** indisponível
- **Fonte oficial:** FNDE/Siope, dados abertos (OData) — https://www.fnde.gov.br/olinda-ide/servico/DADOS_ABERTOS_SIOPE/versao/v1/odata
- **Período disponível:** 2021–2025 (esperado) · **Periodicidade:** bimestral (anual no 6º bimestre) · **Na base:** —
- **Acesso:** API OData, sem login · **Restrições:** robots.txt não restringe
- **Já existe em:** não coletado
- **Observação:** Erro 500 (NullPointerException) em todas as consultas de 24/11/2026, inclusive na documentação do serviço.

### Siope: arquivos analíticos (CSV)

- **Para que serve:** c · **Entra no painel:** não (fora do período 2021–2025) · **Situação:** fora do período
- **Fonte oficial:** FNDE/Siope — https://www.gov.br/fnde/pt-br/assuntos/sistemas/siope/arquivos-dados-analiticos
- **Período disponível:** 2008–2019 · **Periodicidade:** — · **Na base:** —
- **Acesso:** download (FTP) · **Restrições:** —
- **Já existe em:** não coletado
- **Observação:** Página atualizada pela última vez em 16/08/2023.

### Siconfi: DCA Anexo I-E (despesa por função/subfunção: Educação) e I-C (receitas)

- **Para que serve:** c, contexto · **Entra no painel:** sim (Condições materiais) · **Situação:** na base
- **Fonte oficial:** Tesouro Nacional (Siconfi) — https://apidatalake.tesouro.gov.br/ords/siconfi/tt/dca
- **Período disponível:** 2021–2025 (2025 conforme entrega dos municípios) · **Periodicidade:** anual (até 30/04) · **Na base:** 2021–2025
- **Acesso:** API pública · **Restrições:** sem robots.txt
- **Já existe em:** baixado aqui (dados_brutos/siconfi)
- **Observação:** Reaproveita o método de 04_dados/scripts/13_siconfi_dca.py.

### Siconfi: Matriz de Saldos Contábeis (despesa da função Educação por natureza)

- **Para que serve:** c · **Entra no painel:** parcial (só município-ano em que confere com a DCA) · **Situação:** parcial
- **Fonte oficial:** Tesouro Nacional (Siconfi) — https://apidatalake.tesouro.gov.br/ords/siconfi/tt/msc_orcamentaria
- **Período disponível:** 2021–2025 · **Periodicidade:** mensal · **Na base:** 2021–2025
- **Acesso:** API pública · **Restrições:** sem robots.txt
- **Já existe em:** baixado aqui (dados_brutos/siconfi/msc)
- **Observação:** Na maior parte dos município-ano, o total da função 12 na MSC não confere com a DCA; a composição só entra onde confere (±0,5%).

### Siconfi: RREO Anexo 8 (MDE)

- **Para que serve:** c · **Entra no painel:** não · **Situação:** não publicado
- **Fonte oficial:** Tesouro Nacional (Siconfi) — https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rreo
- **Período disponível:** não disponível para os municípios (o anexo é gerado pelo Siope) · **Periodicidade:** bimestral · **Na base:** —
- **Acesso:** API pública · **Restrições:** sem robots.txt
- **Já existe em:** não
- **Observação:** Consulta de 24/11/2026: o RREO de Campo Grande 2024 não traz o Anexo 08.

### Censo Escolar: microdados de escola (infraestrutura das escolas municipais em atividade)

- **Para que serve:** c · **Entra no painel:** sim (Condições materiais) · **Situação:** na base
- **Fonte oficial:** Inep — https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/censo-escolar
- **Período disponível:** 2007–2025 · **Periodicidade:** anual · **Na base:** 2021–2025
- **Acesso:** download (ZIP) · **Restrições:** sem robots.txt
- **Já existe em:** 02_iquems/02_painel_educacao_ms/dados_brutos/inep/censo (sem novo download)

### Remuneração média dos docentes da educação básica por município e rede (RAIS)

- **Para que serve:** c · **Entra no painel:** sim (Condições materiais, só 2021) · **Situação:** parcial
- **Fonte oficial:** Inep — https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/indicadores-educacionais/remuneracao-media-dos-docentes
- **Período disponível:** 2014–2021 (página atualizada em 30/12/2025 sem anos novos) · **Periodicidade:** irregular · **Na base:** 2021–2021
- **Acesso:** download (ZIP) · **Restrições:** sem robots.txt
- **Já existe em:** 02_iquems/02_painel_educacao_ms/dados_brutos/inep/remuneracao
- **Observação:** 2022 em diante não publicado.

## Objetivo / uso: c (alternativa)

### Tesouro Transparente: transferências constitucionais (Fundeb por município)

- **Para que serve:** c (alternativa) · **Entra no painel:** não (o arquivo do FNDE já cobre 2021–2025) · **Situação:** não coletado
- **Fonte oficial:** Tesouro Nacional — https://www.tesourotransparente.gov.br
- **Período disponível:** — · **Periodicidade:** mensal · **Na base:** —
- **Acesso:** download · **Restrições:** robots.txt permite
- **Já existe em:** não
- **Observação:** Fonte do próprio arquivo do FNDE (sisweb.tesouro.gov.br).

## Objetivo / uso: c (correção)

### IPCA (número-índice mensal), para corrigir valores pela inflação

- **Para que serve:** c (correção) · **Entra no painel:** sim (aba corrigida pela inflação) · **Situação:** na base
- **Fonte oficial:** IBGE/SIDRA, tabela 1737 — https://apisidra.ibge.gov.br
- **Período disponível:** jan/2021–dez/2025 na base · **Periodicidade:** mensal · **Na base:** 2021–2025
- **Acesso:** API · **Restrições:** sem robots.txt (404)
- **Já existe em:** baixado aqui
- **Observação:** Média anual dos 12 meses; base: reais médios de 2025.

## Objetivo / uso: c (e b

### Fundeb por ente federado e origem de receita (contribuições, VAAF, VAAT, VAAR, tempo integral), pago pelo Banco do Brasil

- **Para que serve:** c (e b, informativo) · **Entra no painel:** sim (Condições materiais) · **Situação:** na base
- **Fonte oficial:** FNDE — https://www.gov.br/fnde/pt-br/acesso-a-informacao/acoes-e-programas/financiamento/fundeb/valores-repassados-2021-a-2025
- **Período disponível:** 2021–2025 · **Periodicidade:** anual · **Na base:** 2021–2026
- **Acesso:** ++api++ e download (XLSX) · **Restrições:** robots.txt não restringe /fnde
- **Já existe em:** 2024 e 2025 em 03_doutorado/04_dados_ICMS_IQE_VAAR/dados_brutos/fnde/repasses_bb; 2021–2023 baixados aqui
- **Observação:** Ano civil de pagamento. Há um '2024 (1)' no portal, diferente do 2024 usado (ver conferência).

## Objetivo / uso: contexto

### Indicador de nível socioeconômico (Inse) da rede municipal

- **Para que serve:** contexto · **Entra no painel:** sim (IQE-MS) · **Situação:** na base
- **Fonte oficial:** Inep — https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/indicadores-educacionais
- **Período disponível:** 2019, 2021, 2023 · **Periodicidade:** bienal · **Na base:** 2019–2023
- **Acesso:** download · **Restrições:** sem robots.txt
- **Já existe em:** 02_iquems/02_painel_educacao_ms/dados/base/indicadores.parquet

### PIB dos municípios (contexto do componente estrutural)

- **Para que serve:** contexto · **Entra no painel:** sim (Ficha) · **Situação:** na base
- **Fonte oficial:** IBGE/SIDRA, tabela 5938 — https://apisidra.ibge.gov.br
- **Período disponível:** 2002–2023 · **Periodicidade:** anual (defasagem de ~2 anos) · **Na base:** 2021–2023
- **Acesso:** API · **Restrições:** sem robots.txt (404)
- **Já existe em:** baixado aqui

## Objetivo / uso: painel

### Malha municipal de MS

- **Para que serve:** painel · **Entra no painel:** sim (mapas) · **Situação:** na base
- **Fonte oficial:** IBGE — https://servicodados.ibge.gov.br/api/v3/malhas/
- **Período disponível:** atual · **Periodicidade:** — · **Na base:** —
- **Acesso:** API · **Restrições:** —
- **Já existe em:** 02_iquems/02_painel_educacao_ms/dados/base/malha_ms_municipios.geojson (copiada)

## Normas (linha do tempo)

Lista completa em `dados/base/normas.csv` (página Normas do painel). Cada norma foi conferida no texto oficial baixado (Planalto), na página de legislação do Fundeb (FNDE) ou na cópia de 04_dados; a coluna de conferência diz qual.

| data | norma | publicação | repasse/exercício afetado | conferência |
|---|---|---|---|---|
| 1990-01-11 | Lei Complementar nº 63, de 11/01/1990 | DOU de 12/01/1990 | todos os repasses | conferida no texto |
| 2020-08-26 | Emenda Constitucional nº 108, de 26/08/2020 | DOU de 27/08/2020 | Fundeb a partir de 2021; ICMS conforme lei estadual | conferida no texto |
| 2020-12-25 | Lei nº 14.113, de 25/12/2020 | DOU de 25/12/2020 (edição extra) | VAAR a partir de 2023 | conferida no texto |
| 2021-03-22 | Decreto nº 10.656, de 22/03/2021 | DOU de 23/03/2021 | Fundeb a partir de 2021 | conferida no texto |
| 2021-12-27 | Lei nº 14.276, de 27/12/2021 | DOU de 28/12/2021 | Fundeb a partir de 2022 | conferida no texto |
| 2022-04-12 | Lei nº 14.325, de 12/04/2022 | DOU de 13/04/2022 | — | conferida no texto |
| 2022-07-27 | Resolução nº 1, de 27 de julho de 2022 | DOU (listada pelo FNDE) | VAAR de 2023 | conferida na página de legislação do Fundeb (FNDE) |
| 2022-08-24 | Lei Complementar estadual nº 300, de 24/08/2022 (MS) | Diário Oficial de MS | repasses a partir de 2024 | conferida no texto |
| 2022-08-24 | Lei estadual nº 5.941, de 24/08/2022 (MS) | Diário Oficial de MS | repasses a partir de 2024 | conferida no texto |
| 2022-10-24 | Resolução nº 4, de 24 de outubro de 2022 | DOU (listada pelo FNDE) | ver texto | conferida na página de legislação do Fundeb (FNDE) |
| 2022-11-11 | Resolução nº 5, de 11 de novembro de 2022 | DOU (listada pelo FNDE) | VAAR de 2023 | conferida na página de legislação do Fundeb (FNDE) |
| 2022-12-02 | Resolução nº 6, de 2 de dezembro de 2022 | DOU (listada pelo FNDE) | ver texto | conferida na página de legislação do Fundeb (FNDE) |
| 2023-07-07 | Decreto estadual nº 16.225, de 07/07/2023 (MS) | Diário Oficial de MS | repasses a partir de 2024 | conferida no texto |
| 2023-07-28 | Resolução nº 1, de 28 de julho de 2023 | DOU (listada pelo FNDE) | VAAR de 2024 | conferida na página de legislação do Fundeb (FNDE) |
| 2023-09-25 | Edital n. 3 IQE-MS/SED: resultado final, ano-base 2022 | DOE/MS nº 11.278, de 25/09/2023 | repasse de 2024 | conferida no texto |
| 2023-09-28 | Resolução nº 2, de 28 de Setembro de 2023 | DOU (listada pelo FNDE) | ver texto | conferida na página de legislação do Fundeb (FNDE) |
| 2023-10-30 | Lei nº 14.711, de 30/10/2023 | DOU de 31/10/2023 | — | conferida no texto |
| 2023-12-19 | Resolução/SEFAZ nº 3.354, de 19/12/2023 | DOE/MS nº 11.367, de 28/12/2023 | repasse de 2024 | conferida no texto |
| 2023-12-20 | Emenda Constitucional nº 132, de 20/12/2023 | DOU de 21/12/2023 | a partir de 2029 | conferida no texto |
| 2024-07-01 | RESOLUÇÃO Nº 3, DE 1º DE JULHO DE 2024 - RESOLUÇÃO Nº 3, DE 1º DE JULHO DE 2024 | DOU (listada pelo FNDE) | ver texto | conferida na página de legislação do Fundeb (FNDE) |
| 2024-07-26 | Resolução nº 4, de 26 de julho de 2024 - Resolução nº 4, de 26 de julho de 2024 - DOU - Imprensa Nacional.pdf | DOU (listada pelo FNDE) | VAAR de 2025 | conferida na página de legislação do Fundeb (FNDE) |
| 2024-08-29 | Resolução nº 7, de 29 de agosto de 2024 | DOU (listada pelo FNDE) | ver texto | conferida na página de legislação do Fundeb (FNDE) |
| 2024-11-25 | Edital n. 2 IQE-MS/SED: resultado final, ano-base 2023 | DOE/MS nº 11.675, de 25/11/2024 | repasse de 2025 | conferida no texto |
| 2024-12-17 | Resolução nº 10, de 17 de dezembro de 2024 (Comissão Intergovernamental de Financiamento para a Educação Básica de Qualidade) | DOU (listada pelo FNDE) | ver texto | conferida na página de legislação do Fundeb (FNDE) |
| 2024-12-17 | Resolução nº 11, de 17 de dezembro de 2024 | DOU (listada pelo FNDE) | ver texto | conferida na página de legislação do Fundeb (FNDE) |
| 2024-12-17 | Resolução nº 12, de 17 de dezembro de 2024 | DOU (listada pelo FNDE) | ver texto | conferida na página de legislação do Fundeb (FNDE) |
| 2024-12-17 | Resolução nº 13, de 17 de dezembro de 2024 | DOU (listada pelo FNDE) | VAAR de 2025 | conferida na página de legislação do Fundeb (FNDE) |
| 2024-12-19 | Resolução/SEFAZ nº 3.424, de 19/12/2024 | DOE/MS nº 11.701, de 20/12/2024 | repasse de 2025 | conferida no texto |
| 2024-12-23 | Portaria Interministerial MEC/MF nº 13, de 23/12/2024 | DOU | VAAR de 2024 | conferida no texto |
| 2025-04-28 | Portaria Interministerial MEC/MF nº 3, de 28/04/2025 | DOU | VAAR de 2024 (ajuste) | conferida em 04_dados (anexo xlsx do ajuste; ver LOG, sessão 1) |
| 2025-06-12 | RESOLUÇÃO CIF Nº 15, DE 12 DE JUNHO DE 2025 | DOU (listada pelo FNDE) | VAAR de 2025 | conferida na página de legislação do Fundeb (FNDE) |
| 2025-07-29 | Resolução CIF nº 17, de 29 de Julho de 2025 | DOU (listada pelo FNDE) | VAAR de 2026 | conferida na página de legislação do Fundeb (FNDE) |
| 2025-08-07 | Edital n. 2 IQE-MS/SED: resultado final, ano-base 2024 | DOE/MS nº 11.909, de 07/08/2025 | repasse de 2026 | conferida no texto |
| 2025-08-29 | Resolução CIF nº 18, de 29 de agosto de 2025 | DOU (listada pelo FNDE) | ver texto | conferida na página de legislação do Fundeb (FNDE) |
| 2025-12-18 | Resolução/SEFAZ nº 3.484, de 18/12/2025 | DOE/MS nº 12.031 (edição extra), de 19/12/2025 | repasse de 2026 (provisório até o fim do ano) | conferida no texto |
| 2025-12-19 | Resolução CIF nº 20, de 19 de dezembro de 2025 | DOU (listada pelo FNDE) | ver texto | conferida na página de legislação do Fundeb (FNDE) |
| 2025-12-19 | Resolução CIF nº 19, de 19 de dezembro de 2025 | DOU (listada pelo FNDE) | ver texto | conferida na página de legislação do Fundeb (FNDE) |
| 2025-12-29 | Portaria Interministerial MEC/MF nº 14, de 29/12/2025 | DOU | VAAR de 2026 (previsto) | conferida no texto |
| 2025-12-29 | Portaria Interministerial MEC/MF nº 13, de 29/12/2025 | DOU | VAAR de 2025 | conferida no texto |
| 2026-01-13 | Lei Complementar nº 227, de 13/01/2026 | DOU de 14/01/2026 | transição tributária | conferida no texto |
| 2026-04-29 | Portaria Interministerial MEC/MF nº 5, de 29/04/2026 | DOU | VAAR de 2025 (ajuste) | conferida no texto |
| 2026-04-29 | Portaria Interministerial MEC/MF nº 7, de 29/04/2026 | DOU | VAAR de 2023 (não afeta 2024–2026) | conferida no texto |
| 2026-04-29 | Portaria Interministerial MEC/MF nº 6, de 29/04/2026 | DOU | VAAR de 2026 (previsto) | conferida no texto |
| 2026-05-20 | Edital IQE-MS: resultado preliminar, ano-base 2025 | DOE/MS nº 12.162, de 20/05/2026 | repasse de 2027 | conferida no texto |
| 2026-06-15 | Resolução CIF nº 24, de 15 de junho de 2026 | DOU (listada pelo FNDE) | VAAR de 2027 | conferida na página de legislação do Fundeb (FNDE) |
| 2026-07-23 | Resolução CIF nº 25, de 23 de julho de 2026 | DOU (listada pelo FNDE) | VAAR de 2027 | conferida na página de legislação do Fundeb (FNDE) |
| 2026-08-28 | Portaria Interministerial MEC/MF nº 11, de 28/08/2026 | DOU | VAAR de 2026 (previsto) | conferida no texto |
