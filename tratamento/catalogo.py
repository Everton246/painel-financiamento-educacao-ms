"""Catálogo dos indicadores da base (dados/base/catalogo.csv): nome, objetivo, o que o "ano" significa, unidade,
fonte e definição. Gerado a partir dos códigos presentes em indicadores.parquet; código sem regra = falha."""
import re
import sys

import pandas as pd

from comum import BASE

EXERC = "exercício de repasse"
# (padrão do código, nome, objetivo, significado do ano, definição)
REGRAS = [
    (r"icms_repasse_total$", "Repasse total de ICMS ao município (R)", "a", EXERC, "Total da cota-parte do ICMS repassado no ano (valor bruto, antes da retenção de 20% ao Fundeb), Portal da Transparência MS."),
    (r"icms_iqe_coef$", "Coeficiente do IQE-MS usado no repasse", "a", EXERC, "Coeficiente final do edital do IQE-MS do ano-base t−2 (ex.: ano-base 2022 → repasse 2024)."),
    (r"icms_iqe_part$", "Participação no IQE-MS (coeficiente / soma dos 79)", "a", EXERC, "Coeficiente do município dividido pela soma dos 79 coeficientes."),
    (r"icms_iqe_indice$", "Índice IQE da resolução da Sefaz", "a", EXERC, "Coluna ÍNDICE do IQE no Anexo III da resolução (soma dos 79 = 10)."),
    (r"icms_indice_aplicado$", "Índice aplicado (participação total no ICMS)", "a", EXERC, "Índice de participação do município na cota municipal (soma dos 79 = 100). Em 2024, reconstituído pela soma das parcelas (impresso cortado no PDF)."),
    (r"icms_educacional$", "ICMS Educacional (E)", "a", EXERC, "E = R × índice IQE / índice aplicado (resolução da Sefaz do exercício)."),
    (r"icms_repasse_sem_educ$", "Repasse sem a parcela educacional (R − E)", "a", EXERC, "R − E."),
    (r"icms_fatia_demais$", "Fatia nos demais critérios", "a", EXERC, "(R − E) / soma de (R − E) dos 79."),
    (r"icms_contrafactual$", "Contrafactual (parcela educacional distribuída pelos demais critérios)", "a", EXERC, "Fatia nos demais critérios × P (P = soma de E dos 79)."),
    (r"icms_ganho_perda$", "Ganho ou perda no ICMS Educacional", "a", EXERC, "E − contrafactual. Positivo = ganho; negativo = perda (soma zero entre os 79)."),
    (r"icms_estrutural$", "Componente estrutural", "a", EXERC, "P/79 − contrafactual: depende sobretudo do porte econômico do município."),
    (r"icms_desempenho$", "Componente de desempenho", "a", EXERC, "E − P/79: afastamento da participação no IQE-MS em relação à divisão igual."),
    (r"icms_checagem$", "Conferência: estrutural + desempenho − ganho", "a", EXERC, "Deve ser zero (diferença de arredondamento)."),
    (r"icms_educacional_normalizacao$", "ICMS Educacional pela regra de normalização", "a", EXERC, "Participação no IQE × 10% × soma dos repasses (premissa de setembro/2026)."),
    (r"icms_dif_resolucao_normalizacao$", "Diferença resolução − normalização (R$)", "a", EXERC, "E pela resolução − E pela normalização."),
    (r"icms_dif_resolucao_normalizacao_pct$", "Diferença resolução − normalização (%)", "a", EXERC, "Diferença em proporção de E."),
    (r"icms_ganho_perda_normalizacao$", "Ganho ou perda pela regra de normalização", "a", EXERC, "Mesmo cálculo, com E pela normalização."),
    (r"icms_desempenho_normalizacao$", "Componente de desempenho pela normalização", "a", EXERC, "Mesmo cálculo, com E pela normalização."),
    (r"icms_desempenho_pct_total$", "2026: componente de desempenho em pontos percentuais do total repassado", "a", EXERC, "Índice IQE − média dos 79 (em pontos percentuais do total repassado aos 79 municípios, pois o índice é a participação no total do estado). Valores em R$ dependem do repasse de 2026 (pendente)."),
    (r"icms_desempenho_pct_total_normalizacao$", "2026: desempenho em pontos percentuais do total (normalização)", "a", EXERC, "(participação − 1/79) × 10 (pontos percentuais)."),
    (r"icms_soma_repasses$", "Soma dos repasses de ICMS aos 79 municípios", "a", EXERC, "Soma de R (linha do estado)."),
    (r"icms_parcela_educacional_total$", "Parcela educacional total (P)", "a", EXERC, "Soma de E dos 79 (= 10% da soma dos repasses)."),
    (r"icms_parte_estrutural_cov$", "Parte do ganho/perda explicada pelo componente estrutural (covariância)", "a", EXERC, "Decomposição por covariância (medida principal, decisão do autor)."),
    (r"icms_parte_desempenho_cov$", "Parte explicada pelo componente de desempenho (covariância)", "a", EXERC, "Decomposição por covariância."),
    (r"icms_parte_estrutural_var$", "Parte explicada pelo componente estrutural (razão de variâncias)", "a", EXERC, "Medida alternativa (só em nota de método)."),
    (r"icms_parte_desempenho_var$", "Parte explicada pelo componente de desempenho (razão de variâncias)", "a", EXERC, "Medida alternativa."),
    (r"icms_total_pdf_portal$", "Total de repasses de ICMS (linha TOTAL do PDF do Portal)", "a", EXERC, "Usado para conferir a soma dos 79."),
    (r"iqe_coef$", "Coeficiente final do IQE-MS", "IQE-MS", "ano-base do IQE-MS", "Última coluna da linha do município no edital final."),
    (r"iqe_n_valores_linha$", "Número de valores na linha do edital", "IQE-MS", "ano-base do IQE-MS", "Linhas completas têm 12 ou 13 valores; até 3 = sem resultado completo (critério descritivo do 04_dados)."),
    (r"iqe_exercicio_repasse$", "Exercício de repasse afetado", "IQE-MS", "ano-base do IQE-MS", "Ano-base + 2."),
    (r"saems2_participacao_(.+)$", "SAEMS 2º ano, rede municipal: participação ({0})", "IQE-MS (insumo)", "ano da avaliação (= ano-base do IQE-MS)", "Taxa de participação dos estudantes do 2º ano da rede municipal no SAEMS (área pública do CAEd/UFJF). Escala própria do SAEMS."),
    (r"saems2_proficiencia_(.+)$", "SAEMS 2º ano, rede municipal: proficiência média ({0})", "IQE-MS (insumo)", "ano da avaliação (= ano-base do IQE-MS)", "Proficiência média na escala do SAEMS; nunca comparar com o Saeb."),
    (r"saems2_avaliados_(.+)$", "SAEMS 2º ano, rede municipal: estudantes avaliados ({0})", "IQE-MS (insumo)", "ano da avaliação", "Número de estudantes avaliados."),
    (r"saems2_previstos_(.+)$", "SAEMS 2º ano, rede municipal: estudantes previstos ({0})", "IQE-MS (insumo)", "ano da avaliação", "Número de estudantes previstos."),
    (r"inse_media$", "Inse médio da rede municipal", "contexto", "ano da edição do Inse", "Indicador de nível socioeconômico (Inep), média das escolas da rede municipal; entra no fator de municipalização do IQE-MS."),
    (r"ideb_ef_(ai|af)$", "Ideb da rede municipal, EF {0}", "b (contexto)", "ano do Saeb/Ideb", "Ideb da rede municipal (Inep). Escala do Saeb/Ideb."),
    (r"saeb_proficiencia_(lp|mt)_ef_(ai|af)$", "Saeb, rede municipal: proficiência {0}, EF {1}", "b (contexto)", "ano do Saeb", "Proficiência média no Saeb (escala do Saeb; nunca comparar com o SAEMS)."),
    (r"vaar_valor$", "VAAR distribuído (valor do exercício)", "b", "exercício do VAAR", "Anexo V das portarias interministeriais de distribuição; 2026 = previsto (Portaria 11/2026). Zero quando não recebeu."),
    (r"vaar_coef$", "Coeficiente de distribuição do VAAR", "b", "exercício do VAAR", "Coeficiente do anexo de redes beneficiadas."),
    (r"vaar_valor_apos_ajuste$", "VAAR após ajuste", "b", "exercício do VAAR", "Valor devido após o ajuste (Portaria 3/2025 para 2024; Portaria 5/2026 para 2025). Sensibilidade."),
    (r"vaar_coef_apos_ajuste$", "Coeficiente após ajuste", "b", "exercício do VAAR", "Coeficiente do ajuste."),
    (r"vaar_bb_(bruto|deducao|liquido)_ano_civil$", "VAAR pago pelo Banco do Brasil no ano civil ({0})", "b", "ano civil de pagamento", "Informativo: inclui a parcela de janeiro do exercício anterior e ajustes."),
    (r"vaar_prev_p14_2025$", "VAAR 2026 previsto (Portaria 14/2025)", "b", "exercício do VAAR", "1ª previsão de 2026."),
    (r"vaar_prev_p6_2026$", "VAAR 2026 previsto (Portaria 6/2026)", "b", "exercício do VAAR", "2ª previsão de 2026."),
    (r"vaar_por_mat$", "VAAR por matrícula da rede municipal", "b", "exercício do VAAR", "VAAR distribuído / matrículas da rede municipal (Censo do mesmo ano; 2026 usa o Censo 2025)."),
    (r"vaar_apos_ajuste_por_mat$", "VAAR após ajuste por matrícula", "b", "exercício do VAAR", "Sensibilidade."),
    (r"icms_desempenho_por_mat$", "Componente de desempenho do ICMS Educacional por matrícula", "a+b", EXERC, "Desempenho / matrículas da rede municipal."),
    (r"indicador_selecao$", "Indicador de seleção (desempenho ICMS + VAAR, por matrícula)", "a+b", EXERC, "Componente de desempenho por matrícula + VAAR por matrícula. Instrumento de seleção do campo, não classificação de qualidade."),
    (r"indicador_selecao_apos_ajuste$", "Indicador de seleção com VAAR após ajuste", "a+b", EXERC, "Sensibilidade."),
    (r"mat_rede_municipal_sinopse$", "Matrículas da rede municipal usadas no indicador", "a+b", EXERC, "Sinopse Estatística do Censo Escolar, Tabela 1.2 (Censo do ano do repasse; 2026 usa o Censo 2025)."),
    (r"mat_(total|estadual|municipal)_sinopse(_censo)?$", "Matrículas da educação básica ({0}), sinopse do Censo", "contexto", "ano do Censo", "Sinopse Estatística da Educação Básica, Tabela 1.2."),
    (r"mat_municipal_censo_escolas$", "Matrículas da rede municipal (soma das escolas, Censo)", "c", "ano do Censo", "Soma das matrículas por escola dos microdados do Censo (painel do Iquems); 2025 não traz matrícula por escola."),
    (r"rem_docentes_n$", "Docentes da rede municipal (Censo), base da remuneração", "c", "ano", "Inep, remuneração média dos docentes, 2021."),
    (r"rem_pct_localizados_rais$", "% dos docentes localizados na RAIS", "c", "ano", "Cobertura do cálculo de remuneração."),
    (r"rem_mediana_bruta$", "Remuneração bruta mediana dos docentes da rede municipal", "c", "ano", "R$ por mês (RAIS)."),
    (r"rem_media_bruta$", "Remuneração bruta média dos docentes da rede municipal", "c", "ano", "R$ por mês (RAIS)."),
    (r"rem_carga_horaria$", "Carga horária média semanal dos docentes", "c", "ano", "Horas semanais."),
    (r"rem_media_40h$", "Remuneração média padronizada para 40 h semanais", "c", "ano", "R$ por mês, padronizado para 40 h."),
    (r"fundeb_total_liquido$", "Fundeb recebido no ano (total líquido)", "c", "ano civil de pagamento", "Soma das colunas de valores líquidos do arquivo do FNDE (contribuições + complementações)."),
    (r"fundeb_(.+)_(bruto|deducao|liquido)$", "Fundeb: {0} ({1})", "c", "ano civil de pagamento", "FNDE, valores repassados pelo Banco do Brasil por ente federado e origem de receita."),
    (r"educ_dca_(empenhada|liquidada|paga)$", "Despesa em Educação (função 12), {0}", "c", "exercício orçamentário", "Siconfi, DCA Anexo I-E."),
    (r"educ_dca_sub(\d{3})_(empenhada|liquidada|paga)$", "Despesa em Educação, subfunção {0}, {1}", "c", "exercício orçamentário", "Siconfi, DCA Anexo I-E (361 ens. fundamental; 365 ed. infantil; 362 ens. médio; 366 EJA; 367 ed. especial; 306 alimentação; 122 administração geral...)."),
    (r"educ_msc_empenhada_total$", "Despesa em Educação empenhada (MSC, função 12)", "c", "exercício orçamentário", "Matriz de Saldos Contábeis de encerramento; conferida contra a DCA I-E."),
    (r"educ_msc_paga_total$", "Despesa em Educação paga (MSC, função 12)", "c", "exercício orçamentário", "Conta 6.2.2.1.3.04."),
    (r"educ_msc_pessoal$", "Educação: pessoal e encargos (3.1)", "c (remuneração e carreira)", "exercício orçamentário", "Despesa empenhada da função 12 no grupo 3.1."),
    (r"educ_msc_material_consumo$", "Educação: material de consumo (3.3.90.30)", "c (materiais)", "exercício orçamentário", "Despesa empenhada da função 12, elemento 30."),
    (r"educ_msc_servicos_pj$", "Educação: serviços de terceiros PJ (3.3.90.39)", "c (misto)", "exercício orçamentário", "Inclui manutenção, transporte, limpeza e outros: não separável sem o Siope."),
    (r"educ_msc_obras$", "Educação: obras e instalações (4.4.90.51)", "c (infraestrutura)", "exercício orçamentário", "Despesa empenhada da função 12, elemento 51."),
    (r"educ_msc_equipamentos$", "Educação: equipamentos e material permanente (4.4.90.52)", "c (materiais/tecnologia)", "exercício orçamentário", "Despesa empenhada da função 12, elemento 52."),
    (r"educ_msc_outras$", "Educação: demais naturezas de despesa", "c", "exercício orçamentário", "Função 12, naturezas fora dos grupos acima."),
    (r"receita_total_(bruta|liquida)$", "Receita total do município ({0})", "contexto", "exercício orçamentário", "Siconfi, DCA Anexo I-C, total das receitas."),
    (r"pib$", "PIB municipal a preços correntes", "contexto", "ano", "IBGE, PIB dos municípios (tabela 5938)."),
    (r"pop_estimada$", "População estimada", "contexto", "ano", "IBGE, estimativas de população (tabela 6579)."),
    (r"pop_censo2022$", "População (Censo 2022)", "contexto", "ano", "IBGE, Censo 2022 (tabela 4709); base do porte."),
    (r"infra_n_escolas$", "Escolas municipais em atividade", "c (infraestrutura)", "ano do Censo", "Censo Escolar, escolas da rede municipal em atividade."),
    (r"infra_pct_salas_climatizadas$", "Salas climatizadas (% das salas utilizadas)", "c (infraestrutura)", "ano do Censo", "Soma das salas climatizadas / soma das salas utilizadas nas escolas municipais."),
    (r"infra_computadores_alunos$", "Computadores e tablets para alunos (total)", "c (materiais e tecnologia)", "ano do Censo", "Desktop + portátil + tablet para alunos, soma das escolas municipais."),
    (r"infra_(.+)$", "Escolas municipais com {0} (%)", "c (infraestrutura)", "ano do Censo", "Percentual das escolas municipais em atividade com o item (Censo Escolar)."),
    (r"siope_(.+)$", "Siope: {0}", "c", "exercício", "FNDE/Siope, indicadores (6º bimestre)."),
]
NOMES_ITENS = {"agua_potavel": "água potável", "esgoto_rede": "esgoto pela rede pública", "biblioteca_sala_leitura": "biblioteca ou sala de leitura",
               "lab_informatica": "laboratório de informática", "lab_ciencias": "laboratório de ciências", "quadra": "quadra de esportes",
               "refeitorio": "refeitório", "sala_aee": "sala de atendimento educacional especializado", "internet_alunos": "internet para os alunos",
               "banda_larga": "banda larga", "multimidia": "projetor multimídia", "sem_acessibilidade": "NENHUM recurso de acessibilidade"}
ROT = {"lp": "Língua Portuguesa", "lp_escrita": "LP – escrita", "mt": "Matemática", "ai": "anos iniciais", "af": "anos finais",
       "bruto": "bruto", "deducao": "dedução", "liquido": "líquido", "empenhada": "empenhada", "liquidada": "liquidada", "paga": "paga",
       "bruta": "bruta", "receita_de_contribuicoes": "receita de contribuições", "complementacao_vaaf": "complementação VAAF",
       "complementacao_vaat": "complementação VAAT", "complementacao_vaar": "complementação VAAR",
       "fomento_ao_tempo_integral": "fomento ao tempo integral"}


def main():
    ind = pd.read_parquet(BASE / "indicadores.parquet", columns=["indicador", "unidade", "fonte", "ano"])
    linhas, sem = [], []
    for cod, g in ind.groupby("indicador", observed=True):
        for pad, nome, obj, tipo_ano, defin in REGRAS:
            m = re.match(pad, cod)
            if m:
                grupos = [NOMES_ITENS.get(x, ROT.get(x, x.replace("_", " "))) for x in m.groups() if x]
                linhas.append({"indicador": cod, "nome": nome.format(*grupos), "objetivo": obj, "ano_significa": tipo_ano,
                               "unidade": g["unidade"].astype(str).mode().iloc[0], "definicao": defin,
                               "fonte": str(g["fonte"].astype(str).iloc[0])[:300],
                               "anos": f"{int(g['ano'].min())}–{int(g['ano'].max())}" if g["ano"].nunique() > 1 else str(int(g["ano"].min()))})
                break
        else:
            sem.append(cod)
    pd.DataFrame(linhas).to_csv(BASE / "catalogo.csv", index=False, encoding="utf-8-sig")
    print(f"[catálogo] {len(linhas)} indicadores; sem regra: {sem}")
    if sem:
        sys.exit(1)


if __name__ == "__main__":
    main()
