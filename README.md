# Financiamento da Educação Municipal de Mato Grosso do Sul — painel de dados

Painel interativo (Streamlit) da pesquisa de doutorado de Everton Kunzler Bronzoni (PPGEdu/UFMS) sobre a complementação
**VAAR** do Fundeb e o **ICMS Educacional** distribuído pelo **IQE-MS** nos 79 municípios de Mato Grosso do Sul, e seus
efeitos sobre as condições materiais das redes municipais. Pesquisa em andamento; dados públicos; não é um site oficial
do governo.

## O que tem

- **Normas e linha do tempo**: 47 atos (EC 108/2020, Lei 14.113/2020 e alterações, resoluções da CIF, portarias do VAAR,
  LC 63/1990, LC 300/2022, Lei 5.941/2022, Decreto 16.225/2023, editais do IQE-MS, resoluções da Sefaz), cada um
  conferido no texto oficial; defasagem ano-base do IQE-MS → repasse.
- **ICMS Educacional (objetivo a)**: valor, ganho ou perda, componentes estrutural e de desempenho, comparação resolução ×
  normalização, mapa.
- **IQE-MS**: coeficientes por ano-base, coeficiente mínimo e resultado incompleto com o texto das notas dos editais,
  participação e proficiência no SAEMS do 2º ano (rede municipal), Inse.
- **VAAR (objetivo b)**: habilitação, condicionalidades I a V, valores e valor por matrícula, Ideb/Saeb, tabelas de
  contingência.
- **Indicador e seleção**: ordenamento dos 79, seleções principal e alternativa, sensibilidades.
- **Condições materiais (objetivo c, parcial)**: despesa em educação (Siconfi), Fundeb recebido (FNDE), infraestrutura das
  escolas municipais (Censo Escolar), remuneração docente (Inep, 2021).
- **Ficha do município** (com PDF de uma página), **Situação das fontes** e **Sobre os dados** (catálogo, conferências,
  como citar).

Toda tabela e gráfico traz fonte e ano e pode ser exportado (Excel, CSV, PNG, HTML). O endereço guarda os filtros.
Valor ausente aparece como **sem dado**. 2026 é provisório.

## Origem dos dados

Os números dos objetivos a e b vêm de `../04_dados_ICMS_IQE_VAAR` (base oficial da pesquisa), **sem recálculo**; a
conferência (`docs/conferencia.md`) mostra 0 divergências entre o painel, os CSVs de lá e a planilha final. Os dados do
Inep e do SAEMS vêm do painel do Iquems (`../../02_iquems/02_painel_educacao_ms`), sem novo download. O resto foi coletado
aqui (FNDE, Siconfi, IBGE, Planalto). Catálogo completo: `docs/catalogo_fontes.md`.

## Como usar (Windows)

- `abrir_painel.bat`: abre o painel em http://localhost:8502.
- `atualizar.bat`: baixa só o que é novo, remonta a base e confere.
- `verificar_fontes.bat` (ou `python atualizar.py --verificar`): verifica, sem baixar nada, se as fontes publicaram algo
  novo; grava `docs/verificacoes/AAAA-MM-DD.md`.
- `publicar.bat`: envia para o GitHub (ver `LEIAME.md`; ainda não publicado).

## Estrutura

```
coleta/        01_normas, 02_fundeb_fnde, 03_siope, 04_siconfi, 05_ibge (um script por fonte)
tratamento/    montar_base (base única), t03_censo_infra, normas, catalogo, fontes, conferir
dados/base/    base única (indicadores.parquet em formato longo, atributos, municipios, ordenamento, normas, catálogo)
dados/         fontes_status.csv, normas_verificacao.csv
painel/        aplicativo Streamlit (ponto de entrada: painel/app.py)
docs/          catálogo de fontes, conferência, verificações, histórico
testes/        teste automático das páginas e da ficha em PDF
```

Ordem para refazer do zero: `python atualizar.py` (coleta 01 a 05 → `t03_censo_infra` → `montar_base` → `fontes` →
`conferir`). Testes: `python testes/testar_painel.py` e `python testes/testar_pdf.py`.
