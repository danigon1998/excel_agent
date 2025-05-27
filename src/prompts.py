import json

SYSTEM_PROMPT_AGENT_2 = """
Você é um orquestrador de análise de custos de RH. Siga EXATAMENTE ESTES PASSOS:

1. Consolidar dados usando `consolidate_all_data_tool`
   - Usar IA para nomes de colunas específicas
   - Gerar DataFrame intermediário

2. Calcular custos totais com `calculate_employee_total_cost_tool`

**REGRAS ABSOLUTAS:**
- Execute APENAS essas 2 ferramentas NA ORDEM
- Após o passo 2, ENCERRE IMEDIATAMENTE com "FINAL ANSWER"
- Nunca tente acessar dados diretamente
- Não adicione comentários após o cálculo final

Exemplo correto:
Usuário: Analise os custos
Pensamento: Primeiro consolidar dados...
Ação: consolidate_all_data_tool
Observação: Consolidação completa
Pensamento: Agora calcular totais...
Ação: calculate_employee_total_cost_tool
Observação: Cálculo finalizado
**FINAL ANSWER**: Análise concluída. Resultados prontos para exportação.
"""


def get_standardize_dataframe_prompt(
    file_name_stem: str, original_columns: list, canonical_names: dict
) -> str:
    canonical_names_json_string = json.dumps(
        canonical_names, ensure_ascii=False, indent=2
    )
    first_original_column_example = (
        original_columns[0] if original_columns else "a_coluna_original_apropriada"
    )

    return f"""
Sua tarefa é mapear as colunas ORIGINAIS do arquivo Excel '{file_name_stem}' (colunas: {original_columns}) para os NOMES DE COLUNA PADRÃO VÁLIDOS listados abaixo.

LISTA DE NOMES DE COLUNA PADRÃO VÁLIDOS (com descrições):
{canonical_names_json_string}

Instruções de Mapeamento:
1.  Identifique a natureza do arquivo ('{file_name_stem}') e use as descrições dos nomes padrão para guiar seu mapeamento.
2.  Para arquivos de BENEFÍCIOS/FERRAMENTAS:
    a.  "Nome do Item": Mapeie uma coluna ORIGINAL descritiva (ex: 'Plano Contratado', 'Rubrica') para "Nome do Item". Para arquivos de item único (ex: 'Planilha Google Workspace') sem coluna descritiva explícita, você DEVE mapear uma coluna original existente (ex: '{first_original_column_example}') para "Nome do Item"; o sistema usará o nome do arquivo '{file_name_stem}' para popular o valor posteriormente se necessário. Se o arquivo não for um benefício/ferramenta (ex: 'Dados Colaboradores'), omita "Nome do Item".
    b.  "Tipo do Item": Similarmente, mapeie uma coluna de tipo ou infira e use um placeholder de coluna original se necessário.
    c.  "Data de Ativacao do Item": Para datas de ativação/início.
    d.  "Custo Mensal do Item": Para colunas de CUSTO MENSAL/TOTAL numérico (ex: 'Valor Mensal', 'Total').
3.  CASOS ESPECIAIS (ex: Github):
    # Mantenha esta seção SE você ainda usa "Custo Copilot Github", etc., como canônicos.
    # Se Github usa o modelo genérico "Nome do Item" (ex: "Github - Copilot"), esta seção precisa refletir isso.
    * Para arquivos 'Github' com colunas de custo para 'Copilot' ou 'Licença Base', use os canônicos específicos "Custo Copilot Github" ou "Custo Licenca Base Github" SE ELES EXISTIREM na lista de nomes padrão acima. Caso contrário, trate-os como outros itens genéricos para "Nome do Item" e "Custo Mensal do Item".
4.  DADOS DO COLABORADOR: Mapeie para "CPF Colaborador", "Nome Colaborador", "Centro de Custo", "Salario".
5.  OMISSÃO: Se uma coluna ORIGINAL não tiver um mapeamento claro para um nome padrão válido, OMITE-A do JSON.

FORMATO JSON OBRIGATÓRIO - CRÍTICO:
- As CHAVES DEVEM ser os nomes das colunas ORIGINAIS (de: {original_columns}).
- Os VALORES DEVEM ser NOMES DE COLUNA PADRÃO VÁLIDOS (da lista acima).
- Responda APENAS com o objeto JSON. SEM texto adicional, comentários ou markdown.

Mapeamento JSON para '{file_name_stem}':
"""


def get_display_name_from_df_key_prompt(df_key: str):
    return f"""
Extraia o nome principal de '{df_key}' para nomear colunas de custo.

**Instruções:**
1. Foco em marcas/produtos (ex: Unimed, AWS)
2. Remova termos genéricos (Planilha, Benefício, Ferramenta, etc.)
3. Seja conciso - omita datas/versões

Exemplos:
- 'Benefício 1 - Unimed Seguros' → 'Unimed'
- 'Ferramenta AWS Cloud Services' → 'AWS'
- 'Custos Zoom 2023' → 'Zoom'

Responda APENAS com o nome ou 'N/A' se não identificável.
Nome para '{df_key}':
"""
