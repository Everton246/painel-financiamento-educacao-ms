# PROGRESSO — Painel do Financiamento da Educação Municipal de MS

Diário de trabalho e decisões. Pedido de origem: `03_doutorado/pedidos_claude_code/2026-11-24_pedido_painel_financiamento.md`.

## Sessão 1 — 24/11/2026 (Claude Code, trabalho autônomo)

### O que ficou pronto

**Etapa A — levantamento (completa)**
- `docs/catalogo_fontes.md` e `dados/fontes_status.csv`: 24 fontes (normas, valores, indicadores, objetivo c), com objetivo,
  fonte oficial, endereço, período, periodicidade, acesso, restrições, onde já existiam e se entram no painel. Gerados por
  `tratamento/fontes.py`.
- Normas: `dados/base/normas.csv`, linha do tempo com 47 atos, **todos conferidos** (`tratamento/normas.py` procura um
  trecho de cada um no texto oficial): Planalto (EC 108/2020, Lei 14.113/2020, Leis 14.276/2021, 14.325/2022, 14.711/2023,
  LC 227/2026, Decreto 10.656/2021, LC 63/1990, EC 132/2023); página de legislação do Fundeb do FNDE (resoluções da CIF de
  2022 a 2026); cópias de 04_dados (LC 300/2022, Lei 5.941/2022, Decreto 16.225/2023, editais do IQE-MS, resoluções da
  Sefaz, portarias do VAAR). Registro do que foi conferido e como: `dados/normas_verificacao.csv`.
- Achado: a **LC nº 227, de 13/01/2026** (Comitê Gestor do IBS) deu nova redação ao art. 3º da LC 63/1990 (valor adicionado
  ≥ 65%; até 35% por lei estadual, com ≥ 10 p.p. por aprendizagem e equidade) e incluiu o IBS na Lei 14.113/2020. Não está
  no pré-projeto; vale ler.

**Etapa B — coleta** (`coleta/`, manifesto em `dados_brutos/manifesto_downloads.csv` com endereço, data, tamanho, sha256)
- 01_normas: 9 páginas do Planalto e 26 PDFs de resoluções/leis do VAAR (FNDE). Nada baixado do portal de MS.
- 02_fundeb_fnde: Fundeb por ente e origem de receita 2021, 2022, 2023 (2024 e 2025 já estavam no 04_dados e são lidos de
  lá). Também baixado o "2024 (1)" do portal: arquivo diferente, mas mesmo total líquido nos 79 municípios.
- 03_siope: **falhou** (ver abaixo).
- 04_siconfi: DCA I-E e I-C e Matriz de Saldos Contábeis (MSCE, dezembro, classe 6) dos 79 municípios, 2021–2025
  (1.185 arquivos, ~30 MB compactados). Amostra (Taquarussu 2024) conferida antes de escalar.
- 05_ibge: PIB 2021–2023 e estimativas de população 2021, 2024, 2025, 2026.
- Inep (Censo, Ideb, Saeb, Inse, remuneração) e SAEMS: **nada baixado**; lidos dos arquivos do painel do Iquems. Os
  microdados do Censo 2021–2025 cobrem as escolas municipais; a remuneração por município e rede só vai até 2021 no Inep.

**Etapa C — base** (`tratamento/montar_base.py` → `dados/base/`)
- `indicadores.parquet` (formato longo: município, código IBGE, ano, indicador, valor, unidade, fonte, arquivo, página,
  observação): 32 mil valores, 144 indicadores, 79 municípios. `atributos.parquet` (textos: situação no VAAR,
  condicionalidades, notas dos editais). `municipios.parquet`, `ordenamento.parquet`, `catalogo.csv`, `normas.csv`,
  contingências do 04_dados.
- `tratamento/conferir.py` → `docs/conferencia.md`: **0 divergências** entre o painel e os CSVs do 04_dados (62 colunas) e
  a planilha `icms_educacional_vaar_ms.xlsx` (89 colunas); 79 municípios em todas as bases dos objetivos a e b; somas
  (repasses = TOTAL do PDF; E = 10%; soma dos ganhos = 0; estrutural + desempenho = ganho; VAAR = totais do LOG; Fundeb
  bruto + dedução = líquido); amostra relida ao vivo (Siconfi, IBGE) e com outra biblioteca (planilha do FNDE).
- Ranking provisório × ordenamento do script 09: **mesmas posições nos 79**, mesmo acumulado (diferença 5×10⁻¹²) e mesma
  seleção principal. O painel usa o script 09. O xlsx do ranking tem ainda a aba "Comparativo Fundeb", que não existe no
  pipeline e não entra no painel.

**Etapa D — painel** (`painel/app.py`; identidade visual do painel do Iquems)
- 10 páginas: Início, Normas, ICMS Educacional, IQE-MS, VAAR, Indicador e seleção, Condições materiais, Ficha do
  município (com PDF de uma página), Situação das fontes, Sobre os dados. Faixa azul, menu horizontal, "Como ler esta
  página", fonte e ano sob cada gráfico e tabela, "sem dado" explícito, exportação (Excel, CSV, PNG, HTML), endereço que
  guarda os filtros, busca de município, "Limpar filtros", rodapé pedido.
- Teste automático (`testes/testar_painel.py`): 10 páginas × 6 combinações de filtros (+ 6 temas da página de condições)
  = 66 execuções, **0 erros**. `testes/testar_pdf.py`: ficha em PDF de 4 municípios, uma página cada.

**Etapa E — atualização e publicação**
- `atualizar.py` / `atualizar.bat` (coleta só do que é novo → base → catálogo de fontes → conferência);
  `atualizar.py --verificar` / `verificar_fontes.bat` (8 segundos; não baixa nada; tolerante a fonte fora do ar; grava
  `docs/verificacoes/2026-11-24.md`). `abrir_painel.bat`, `publicar.bat` (confere antes de enviar; não roda sem remoto),
  `requirements.txt`, `README.md`, `LEIAME.md`, `CITATION.cff`, `.gitignore`.
- **Não publicado** (nem GitHub nem Streamlit Cloud). Repositório git local, com o primeiro commit.

### O que falta

- Siope (fonte central do objetivo c no pré-projeto): só quando o serviço do FNDE voltar. O coletor e o painel já estão
  preparados; a verificação mensal avisa.
- Repasse de ICMS de 2026 (início de 2027), via 04_dados.
- Edital FINAL do IQE-MS do ano-base 2025 (repasse de 2027); o preliminar (DOE 12.162) não foi extraído pela base.
- Indicadores do VAAR do Inep (atendimento e aprendizagem, `Indicadores Atendimento Aprendizagem VAAR 2026 II.xlsx` em
  04_dados) não entram no painel; o painel mostra Ideb/Saeb como contexto.
- Remuneração docente após 2021 (Inep não publicou).
- Instruções normativas da SED sobre o IQE-MS (texto não está nas pastas).

### Fontes que falharam e por quê

| Fonte | O que aconteceu |
|---|---|
| Siope, serviço OData do FNDE | erro 500 (NullPointerException) em todas as consultas de 24/11/2026, inclusive na página de documentação; arquivos analíticos do portal só até 2019 |
| Siconfi, RREO Anexo 8 (MDE) | não existe para os municípios no Siconfi (é gerado pelo Siope) |
| Siconfi, Matriz de Saldos Contábeis | baixada, mas o total da função Educação só confere com a DCA em 90 de 363 município-ano (há valores negativos e zerados, por diferença de registro entre prefeituras): a composição por natureza só entra onde confere |
| Siconfi, DCA I-E | Caracol (2022) e Douradina (2024) declararam a DCA sem a função Educação: *sem dado* |
| Diário Oficial de MS | o servidor não respondeu ao robots.txt; nada foi baixado (as instruções normativas da SED ficam pendentes) |
| Portal de legislação de MS | proíbe robôs: nada baixado (regra do pedido) |

### Decisões tomadas aqui (conservadoras e reversíveis)

1. Objetivos a e b: nada recalculado; tudo lido de 04_dados. Unidades mantidas como no CSV (ex.: diferença resolução ×
   normalização em %, desempenho de 2026 em pontos percentuais do total repassado aos 79).
2. Infraestrutura do Censo: só escolas municipais **em atividade** (TP_SITUACAO_FUNCIONAMENTO = 1), lidas direto dos
   microdados do Iquems (o recorte pronto do Iquems não separa escolas paralisadas).
3. Matriz de Saldos Contábeis: só entra onde confere com a DCA (±0,5%).
4. Valores por matrícula na página de condições materiais: calculados pelo painel e marcados como tal.
5. Médias 2021–2023 e 2024–2025 na página de condições: calculadas pelo painel só com os anos completos (se faltar um ano,
   *sem dado*).
6. Fundeb por município do FNDE: total líquido = soma das colunas líquidas do arquivo (marcado como derivado).
7. O porte e as seleções vêm do 04_dados (Censo 2022; decisão do autor de 29/10/2026).

### Decisões pendentes do autor

1 a 4: resolvidas na sessão 2 (abaixo). Resta: índice da correção (IPCA médio anual × IPCA de dezembro) e se o Fundeb de
2021–2023 por exercício deve ser extraído dos PDFs do FNDE.
5. Incluir no painel os indicadores do VAAR do Inep (atendimento e aprendizagem) e as tabelas da aba "Comparativo Fundeb"
   do ranking provisório (hoje fora do pipeline).
6. Transformar o ranking provisório em script no 04_dados (pendência já registrada lá) ou aposentá-lo: o painel mostra que
   ele coincide com o script 09.

### O que o autor deve validar

Ver `LEIAME.md`, seção 5 (lista de 10 itens).

## Sessão 2 — 24/11/2026 (respostas do autor)

Respostas: 1 aprovado (frentes); 2 manter a Matriz de Saldos Contábeis onde confere com a DCA; 3 aba à parte corrigida pela
inflação; 4 procurar o valor de cada exercício e ver se diverge; 5 ok; 6 manter o mesmo e-mail; 7 publicar.

- **Inflação:** `coleta/05_ibge.py` baixa o IPCA mensal (SIDRA 1737), 2021–2025; a base guarda o IPCA médio anual e o fator
  para reais médios de 2025. Na página de condições materiais, todo tema em reais tem duas abas: valores correntes e
  corrigidos. Decisão de método tomada aqui (conservadora, reversível): IPCA médio do ano, base 2025.
- **Fundeb por exercício** (`coleta/06_fundeb_exercicio.py`): exercício financeiro = ano civil, mas as fontes registram
  coisas diferentes (portarias: valor devido no exercício; Banco do Brasil: valor pago no ano, que inclui a última parcela e
  os ajustes do exercício anterior). Em planilha, o FNDE publica o exercício de 2025 completo (Portaria nº 5/2026), o
  previsto de 2026 (Portaria nº 11/2026) e a VAAT devida de 2024 (Portaria nº 3/2025); 2021–2023 só em PDF (não coletados).
  Resultado (2025, 79 municípios): receita da contribuição quase igual (até 0,4% por município); VAAT do exercício 27% menor
  que a paga no ano; VAAR do exercício 18% menor que o pago no ano; total 0,4% menor (até 2,9% por município). O VAAR do
  exercício de 2025 na tabela do FNDE é idêntico ao VAAR após ajuste do 04_dados nos 79 municípios.
- **Frentes e MSC:** textos do painel atualizados para "aprovado pelo autor".

### Pendências registradas sobre 04_dados (sem alterar nada lá)

- Nenhum erro encontrado nos dados dos objetivos a e b (0 divergências). Observações: o Leia-me do
  `ranking_provisorio_icms_vaar_ms.xlsx` diz "versão de 04/11/2026", embora o arquivo seja de 09/11/2026, 12h45; o
  `Lei Complementar 57 de 1991 - FPM.doc` segue sendo o texto antigo.
