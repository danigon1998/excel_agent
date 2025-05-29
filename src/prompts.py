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
        canonical_names, ensure_ascii=False, separators=(",", ":")
    )

    return f"""
Mapeie colunas de '{file_name_stem}' para nomes padrão usando estas regras:

**COLUNAS ORIGINAIS:** {original_columns}
**NOMES VÁLIDOS (JSON):** {canonical_names_json_string}

**REGRAS ABSOLUTAS:**
1. Para BENEFÍCIOS/FERRAMENTAS:
   - "Nome do Item": Mapeie coluna descritiva OU primeira coluna
   - "Custo Mensal do Item": SÓ para custos recorrentes (ex: 'Valor Mensal')
   - Ignore: parcelas, descontos e custos únicos

2. Para COLABORADORES:
   - Mapeie para: CPF, Nome, Centro de Custo, Salario

3. Casos especiais (GitHub):
   - Use nomes específicos se existirem

4. Se não houver mapeamento claro: OMITA a coluna

**EXEMPLOS CRÍTICOS:**
- 'Valor Mensal' → "Custo Mensal do Item" (✔️)
- 'Valor Parcela' → OMITA (❌ a menos que seja recorrente)
- 'Total' → "Custo Mensal do Item" (✔️ se mensal)

**FORMATO:** {{"Coluna_Original": "Nome_Padrao"}}

APENAS JSON para '{file_name_stem}':
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
