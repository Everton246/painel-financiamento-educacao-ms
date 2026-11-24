# LEIA-ME — Painel do Financiamento da Educação Municipal de MS

Guia para o autor: como abrir, como atualizar, de onde vem cada dado, o que validar e como publicar.

## 1. Abrir o painel

Dê dois cliques em `abrir_painel.bat`. O navegador abre em http://localhost:8502. Para fechar, feche a janela preta.
Na primeira vez, o arquivo instala os pacotes do `requirements.txt` (precisa de Python 3.11 ou mais novo).

## 2. Usar

- **Menu** sob a faixa azul: 10 páginas. Cada uma tem o quadro **Como ler esta página** (o que mede, como ler, limites).
- **Filtros** (barra lateral): ano do repasse (2024, 2025, 2026 provisório), município, porte populacional, seleção de campo
  (principal, alternativa, fora das duas), situação no VAAR e situação no IQE-MS. O filtro de município destaca o
  município e abre a ficha; os demais restringem os municípios mostrados. **Limpar filtros** volta ao padrão.
- **Endereço**: guarda os filtros; copie o link para abrir a mesma tela depois.
- **Busca** no topo: digite parte do nome do município (sem acento) e clique no resultado para abrir a ficha.
- **Exportação**: em toda tabela e gráfico, "⬇ Baixar…" gera Excel e CSV (e HTML e PNG para gráficos). A ficha do
  município baixa em Excel (com todos os dados e fontes) e em PDF de uma página.
- Clique numa linha de tabela ou num município do mapa para abrir a ficha dele.

## 3. Atualizar

- `atualizar.bat`: baixa só o que é novo (normas, Fundeb, Siope, Siconfi, IBGE), remonta a base, atualiza o catálogo de
  fontes e roda a conferência. Leva alguns minutos; a primeira coleta do Siconfi leva cerca de 40 minutos.
- `atualizar.bat --so-base`: só remonta e confere (sem internet). Use depois de rodar de novo os scripts do
  `04_dados_ICMS_IQE_VAAR`: o painel lê de lá e não recalcula nada dos objetivos a e b.
- `verificar_fontes.bat`: não baixa nada. Para cada fonte, verifica se ela publicou período mais novo que o da base e grava
  `docs/verificacoes/AAAA-MM-DD.md`. Feito para a tarefa agendada mensal; cada consulta tem limite de 20 segundos e uma fonte
  fora do ar não interrompe as outras.

Para agendar a verificação mensal no Windows: Agendador de Tarefas → Criar tarefa básica → mensal → Iniciar um programa →
`verificar_fontes.bat` desta pasta (em "Iniciar em", informe a pasta).

### Quando chegar o repasse de ICMS de 2026 (início de 2027)

O caminho é o de sempre no `04_dados_ICMS_IQE_VAAR` (pôr o PDF em `repasses icms municipais\`, incluir no script 04 e rodar
os scripts de lá). Depois, `atualizar.bat --so-base` aqui. O painel passa a mostrar 2026 em reais automaticamente.

## 4. Fontes (resumo; completo em `docs/catalogo_fontes.md` e na página Situação das fontes)

| Dado | Fonte | Onde estava / como veio |
|---|---|---|
| ICMS Educacional, IQE-MS, VAAR, indicador, seleções | 04_dados_ICMS_IQE_VAAR (Sefaz, SED, Portal da Transparência, FNDE) | lido de `dados_processados`, sem recálculo |
| Normas federais | Planalto | baixadas (`dados_brutos/normas/planalto`) |
| Resoluções da CIF e legislação do Fundeb | FNDE | listagem e PDFs baixados (`dados_brutos/normas/fnde`) |
| Normas de MS | cópias em 04_dados | o portal de legislação de MS proíbe robôs |
| Fundeb por município 2021–2025 | FNDE (valores repassados pelo BB) | 2024–2025 de 04_dados; 2021–2023 baixados |
| Despesa em educação e receita total | Siconfi (DCA I-E e I-C), 2021–2025 | API do Tesouro |
| Despesa em educação por natureza | Siconfi (Matriz de Saldos Contábeis) | API do Tesouro; só onde confere com a DCA |
| Infraestrutura das escolas municipais | Censo Escolar 2021–2025 (microdados) | arquivos do painel do Iquems |
| SAEMS 2º ano, Ideb, Saeb, Inse | Inep e CAEd | base do painel do Iquems |
| Remuneração docente | Inep, 2021 (último publicado) | arquivo do painel do Iquems |
| População e PIB | IBGE/SIDRA | API |
| Siope | FNDE | **fora do ar** em 24/11/2026 (o coletor tenta de novo a cada atualização) |

## 5. O que validar (lista para o autor)

1. **Página Normas**: as descrições de "o que muda" e "repasse afetado" das normas (são resumos meus; a fonte é o texto).
2. ~~Frentes~~ e 3. ~~Matriz de Saldos Contábeis~~: aprovadas pelo autor em 24/11/2026 (correspondência natureza →
   frente; composição mantida só onde confere com a DCA, ±0,5%).
4. **Valores por matrícula na página de condições materiais**: matrículas da sinopse (2024–2025) e soma das escolas do Censo
   (2021–2023); a conferência mostra que as duas coincidem em 2024 nos 79 municípios.
5. **Correção pela inflação** (pedida em 24/11/2026): aba à parte, com o IPCA médio de cada ano e valores em reais médios
   de 2025. Conferir se prefere outro índice ou o IPCA de dezembro.
6. **Fundeb**: a página mostra o pago no ano civil e, ao lado, o devido no exercício (2024 só VAAT; 2025 completo). A
   contribuição quase coincide; as complementações divergem (ver conferência).
7. **Filtro "Situação no IQE-MS"**: usa os critérios descritivos do 04_dados (mínimo = menor coeficiente do ano; sem
   resultado completo = linha com até 3 valores).
8. **Textos do Início** (resumo do pré-projeto) e dos quadros "Como ler" (`painel/textos.py`).
9. O e-mail de contato no topo e no rodapé é o mesmo do painel do Iquems (`painel/identidade.py`, `CONTATO_EMAIL`): troque
   ou retire antes de publicar, se preferir.
10. Abrir 3 ou 4 fichas de municípios que você conhece e conferir com as fontes originais (sugestão: Taquarussu, Jateí,
   Antônio João, Campo Grande).

## 6. Como publicar (quando você decidir)

Nada foi publicado. O repositório git é local (sem GitHub ligado). Passo a passo:

1. Crie um repositório **vazio** no GitHub (ex.: `painel-financiamento-educacao-ms`), público ou privado.
2. Nesta pasta, abra o terminal e rode (trocando o endereço):
   `git remote add origin https://github.com/<seu-usuario>/painel-financiamento-educacao-ms.git`
   e depois `git push -u origin main`.
3. No Streamlit Community Cloud (share.streamlit.io), "New app" → escolha o repositório → arquivo principal
   `painel/app.py`. O `requirements.txt` da raiz é usado na instalação.
4. Depois de publicado, ponha o endereço em `painel/textos.py` (`ENDERECO = "https://..."`): ele entra na citação ABNT.
5. Nas próximas vezes: `atualizar.bat` e depois `publicar.bat` (ele roda a conferência antes e cancela se houver divergência).

Vai para o GitHub: código, `dados/base/` (base pronta, ~1 MB), `dados/*.csv`, `docs/`. **Não vai**: `dados_brutos/`
(arquivos baixados), `dados/cache/`, `coleta.log`, `testes/saida/` e qualquer pasta `Claude outputs/` (ver `.gitignore`).
Atenção: o painel publicado lê só `dados/base` e `dados/*.csv`; ele não precisa de `04_dados` nem do painel do Iquems.
