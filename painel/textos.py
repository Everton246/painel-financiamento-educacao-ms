"""Textos do painel, num só lugar, para revisar sem mexer no código das páginas.

O conteúdo de método vem do pré-projeto (03_doutorado/02_pre_projeto), do CLAUDE.md e do LOG.md de
04_dados_ICMS_IQE_VAAR e de dados/base/catalogo.csv. Ao mudar o método lá, ajuste aqui também.
"""

TITULO = "Financiamento da Educação Municipal de Mato Grosso do Sul"
SUBTITULO = ("ICMS Educacional (IQE-MS), complementação VAAR do Fundeb e condições materiais das redes municipais dos "
             "79 municípios: normas, valores, indicadores e fontes")
AUTOR = "Everton Kunzler Bronzoni"
ENDERECO = ""  # preencher quando o painel for publicado (ex.: https://<nome>.streamlit.app)
RODAPE = ("Responsável: Everton Kunzler Bronzoni. Pesquisa de doutorado em andamento (PPGEdu/UFMS). Dados públicos; "
          "não é um site oficial do governo.")
AVISO = RODAPE

FONTES = ("Sefaz/MS (resoluções dos índices do ICMS) · SED/MS (editais do IQE-MS) · Portal da Transparência MS (repasses "
          "de ICMS) · FNDE e MEC (portarias do VAAR, listas de habilitação, Fundeb por município) · Inep (Censo Escolar, "
          "Saeb/Ideb, Inse, remuneração docente) · SAEMS (CAEd/UFJF) · Tesouro Nacional (Siconfi) · IBGE")

REGRAS = ("Valor que a fonte não traz aparece como <b>sem dado</b>. Nenhuma estimativa sem marca: a única é a do "
          "ICMS Educacional, feita pela pesquisa com as resoluções da Sefaz. 2026 é provisório. Avaliações diferentes "
          "(SAEMS, Saeb) nunca ficam no mesmo eixo.")

SEM_DADO_EXPLICA = ("Quer dizer que a fonte não publicou o valor para esse recorte (ou que ele ainda não foi coletado: veja "
                    "a página Situação das fontes). Nada é estimado para preencher a lacuna.")

PROVISORIO = ("**2026 é provisório em tudo:** o repasse anual de ICMS de 2026 só sai no início de 2027 (por isso os valores "
              "em reais do ICMS Educacional de 2026 ainda não existem) e o VAAR de 2026 é o valor PREVISTO na Portaria "
              "Interministerial MEC/MF nº 11/2026.")

ORDENAMENTO_NAO_E_QUALIDADE = ("O ordenamento é um **instrumento de seleção** dos municípios para o trabalho de campo "
                               "(objetivo c). Ele mede quanto cada rede recebeu ou deixou de receber das duas políticas "
                               "por causa dos seus resultados, por matrícula. **Não é classificação da qualidade das "
                               "redes** nem ranking de desempenho educacional.")

RESUMO_PESQUISA = (
    "A pesquisa analisa a complementação **VAAR** do Fundeb e suas condicionalidades em Mato Grosso do Sul, com "
    "aprofundamento no **ICMS Educacional**, distribuído pelo **Índice de Qualidade da Educação de MS (IQE-MS)**. Parte "
    "da contradição de um mecanismo que pretende induzir qualidade pela competição por resultados, mas redistribui, em "
    "**soma zero**, recursos em sua maior parte não vinculados à educação, e responsabiliza as redes municipais por "
    "fatores de desempenho que elas não controlam integralmente.\n\n"
    "**Objetivos específicos** (pré-projeto, versão final de 29/09/2026):\n\n"
    "- **a)** estimar, para os 79 municípios, nos repasses de 2024 a 2026, o valor recebido a título de ICMS Educacional "
    "e o ganho ou a perda relativa dele decorrente, separado em componente **estrutural** e componente de **desempenho**;\n"
    "- **b)** verificar o cumprimento das condicionalidades do VAAR e o valor recebido, e selecionar, por um indicador "
    "que reúne as duas políticas, os municípios do trabalho de campo;\n"
    "- **c)** investigar, nos municípios selecionados, como o ganho ou a perda e o recebimento ou não do VAAR se "
    "traduzem em **condições materiais** nas escolas (remuneração e carreira, infraestrutura, materiais), comparando o "
    "período anterior (2021–2023) com o de vigência (2024–2026).\n\n"
    "Este painel reúne os dados públicos dos objetivos a e b (lidos da base oficial da pesquisa, sem recalcular nada) "
    "e, em parte, os do objetivo c. O trabalho de campo e o formulário às secretarias não estão aqui.")

# (chave, título, pergunta que a página responde)
PAGINAS_GUIA = [
    ("normas", "Normas e linha do tempo", "Que normas regem o VAAR e o ICMS Educacional, quando mudaram e qual repasse cada uma afeta?"),
    ("icms", "ICMS Educacional (objetivo a)", "Quanto cada município recebeu de ICMS Educacional, quanto ganhou ou perdeu, e quanto disso é estrutural ou desempenho?"),
    ("iqe", "IQE-MS", "Qual o coeficiente de cada município em cada ano-base, quem ficou com o mínimo ou sem resultado, e como foi a participação no SAEMS?"),
    ("vaar", "VAAR (objetivo b)", "Quem foi habilitado, que condicionalidades foram descumpridas, quem recebeu e quanto, por matrícula?"),
    ("indicador", "Indicador e seleção", "Como os 79 municípios se ordenam pelo indicador que reúne as duas políticas, e quais foram selecionados para o campo?"),
    ("condicoes", "Condições materiais (objetivo c, parcial)", "O que os dados públicos mostram sobre despesa em educação, Fundeb, infraestrutura e remuneração, antes e durante a vigência?"),
    ("municipio", "Ficha do município", "Tudo o que o painel tem sobre um município, numa página (com PDF)."),
    ("fontes", "Situação das fontes", "O que já está na base, até que ano, o que ainda não foi publicado e quando foi a última verificação?"),
    ("sobre", "Sobre os dados", "De onde vem cada indicador, como foi conferido e como citar?"),
]

PAGINAS = {
    "inicio": {"mede": "Visão geral da pesquisa e dos números centrais.", "ler": "Os cartões trazem totais dos 79 municípios por ano, com a fonte.",
               "limites": "2026 é provisório."},
    "normas": {
        "mede": "As normas federais e estaduais do Fundeb/VAAR e do ICMS Educacional, as resoluções da Comissão "
                "Intergovernamental (CIF), as portarias do VAAR, os editais do IQE-MS e as resoluções da Sefaz.",
        "ler": "Cada linha diz o que a norma muda e qual repasse afeta. A coluna 'conferência' diz onde o texto foi "
               "conferido (Planalto, página de legislação do FNDE ou cópia em 04_dados). A defasagem é central: o IQE-MS "
               "do ano-base N vira coeficiente no edital de N+1, entra na resolução da Sefaz de dezembro de N+1 e define "
               "o repasse de N+2.",
        "limites": "O portal de legislação de MS proíbe acesso automatizado: a LC nº 57/1991 consolidada e as instruções "
                   "normativas da SED sobre o IQE-MS não foram conferidas por script. 'O que muda' é resumo para leitura; "
                   "a fonte é sempre o texto da norma."},
    "icms": {
        "mede": "Para cada município e exercício: repasse total de ICMS (R), ICMS Educacional (E = R × índice IQE / índice "
                "aplicado, pela resolução da Sefaz), o contrafactual (a mesma parcela distribuída pelos demais critérios), o "
                "ganho ou perda (E − contrafactual) e sua decomposição em componente estrutural (P/79 − contrafactual) e de "
                "desempenho (E − P/79).",
        "ler": "Ganho positivo = o município recebeu mais do que receberia sem o critério educacional. Como o mecanismo "
               "é de soma zero, a soma dos ganhos e perdas dos 79 é zero. O componente estrutural depende sobretudo do "
               "porte econômico; o de desempenho, da posição no IQE-MS. A conferência estrutural + desempenho − ganho "
               "deve dar zero.",
        "limites": "O Portal da Transparência divulga só o total repassado; o ICMS Educacional é uma ESTIMATIVA da "
                   "pesquisa (método da resolução, conferido contra a regra de normalização). O ganho não é vinculado à "
                   "educação. 2026: sem os valores em reais (repasse anual pendente)."},
    "iqe": {
        "mede": "O coeficiente final do IQE-MS por ano-base (editais da SED/MS), os casos de coeficiente mínimo e de "
                "resultado incompleto, com o texto das notas, e a participação e a proficiência das redes municipais no "
                "SAEMS do 2º ano, insumo do índice.",
        "ler": "O ano-base N define o repasse de N+2. 'Coeficiente mínimo' = igual ao menor do ano; 'sem resultado "
               "completo' = linha do edital com até 3 valores. Participação abaixo de 80% leva à menor nota apurada "
               "(Decreto nº 16.225/2023).",
        "limites": "Os critérios de 'mínimo' e 'sem resultado' são descritivos (a instrução normativa não está nas "
                   "pastas). O SAEMS tem escala própria e nunca é comparado ao Saeb. A participação do SAEMS vem da área "
                   "pública do CAEd e pode não coincidir com a taxa usada pela SED no cálculo."},
    "vaar": {
        "mede": "Habilitação, condicionalidades I a V, evolução nos indicadores, situação (beneficiado, habilitado e não "
                "beneficiado, inabilitado), valor e valor por matrícula do VAAR das redes municipais, 2024 a 2026, e as "
                "tabelas de contingência com o ICMS Educacional e a posição no IQE-MS.",
        "ler": "Uma rede pode ser habilitada e não receber, por não evoluir nos indicadores. As tabelas de contingência "
               "contam municípios: os 79 são a população inteira, então a leitura é só descritiva (sem testes de "
               "significância).",
        "limites": "2026 é PREVISTO (Portaria nº 11/2026). Antônio João aparece como inabilitado nas listas de 2024 e 2025, "
                   "mas recebeu (inclusão tardia sem motivo conhecido); nas contingências conta como habilitado (decisão do "
                   "autor). O valor pago pelo Banco do Brasil é do ano civil e não coincide com o do exercício."},
    "indicador": {
        "mede": "O indicador de seleção: componente de desempenho do ICMS Educacional por matrícula + VAAR por matrícula, "
                "por ano e acumulado (2024 + 2025), o ordenamento dos 79 e as duas seleções de campo.",
        "ler": "Posição 1 = a rede que mais recebeu (ou menos deixou de receber) das duas políticas por seus resultados. "
               "Seleção principal: por porte (melhor e pior de até 20 mil e de mais de 20 mil habitantes, mais os dois "
               "em torno da mediana). Alternativa: extremos do ordenamento geral. Sensibilidades: VAAR após ajuste e VAAR "
               "previsto de 2026.",
        "limites": "O indicador por matrícula amplia os valores dos municípios pequenos. O componente estrutural não entra "
                   "no indicador. A escolha final dos seis municípios é do autor."},
    "condicoes": {
        "mede": "O que há de dado público sobre as condições materiais das redes municipais: despesa em educação (Siconfi), "
                "Fundeb recebido (FNDE), infraestrutura das escolas municipais (Censo Escolar) e remuneração docente (Inep).",
        "ler": "Compare o período anterior (2021–2023) com o de vigência (2024–2026). Use o filtro 'Seleção de campo' para "
               "ver só os seis municípios. As três frentes do pré-projeto aparecem como aproximação pela natureza da "
               "despesa (pessoal; obras; material de consumo e equipamentos), marcada como decisão pendente do autor.",
        "limites": "O Siope (fonte prevista no pré-projeto) estava fora do ar na coleta (24/11/2026). A composição da despesa "
                   "por natureza (Matriz de Saldos Contábeis) só aparece onde o total confere com a DCA. A remuneração do "
                   "Inep só vai até 2021. Os valores estão em reais correntes (sem correção pela inflação). Associação no "
                   "tempo não é efeito: o desenho não isola o ICMS Educacional de outros fatores."},
    "municipio": {"mede": "Tudo o que a base tem sobre um município.", "ler": "Escolha o município no filtro lateral ou na busca.",
                  "limites": "Mesmos limites das páginas de origem. 2026 é provisório."},
    "fontes": {"mede": "Cada fonte usada ou investigada: o que é, para que objetivo serve, período disponível, forma de acesso, "
                       "restrições e até que ano está na base.",
               "ler": "A coluna 'situação' resume: na base, parcial, indisponível, não publicado ou não coletado. A data da "
                      "última verificação vem de atualizar.py --verificar.",
               "limites": "A verificação automática compara o período mais recente publicado com o da base; ela não "
                          "substitui a leitura das notas da fonte."},
    "sobre": {"mede": "Catálogo dos indicadores, conferências, como citar e histórico.", "ler": "—", "limites": "—"},
}
