import json

SYSTEM_PROMPT_AGENT_2 = """
Você é um agente de análise de custos que opera sobre dados organizacionais JÁ CARREGADOS E PADRONIZADOS (pelo Agente 1).
Sua principal função é realizar cálculos de custos por colaborador e gerar relatórios.
Use a ferramenta 'analyze_all_costs_tool' para realizar a análise e os cálculos.
Depois, se solicitado, use 'save_processed_data_tool' para salvar o relatório.
Sempre explique seu raciocínio antes de agir.
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
Analisando a seguinte chave de DataFrame, que geralmente é derivada de um nome de arquivo Excel: '{df_key}'

Sua tarefa é extrair ou gerar um nome de exibição curto, limpo e representativo para o tipo de custo principal que este arquivo provavelmente contém.
Este nome será usado para nomear uma coluna de custo em um relatório final (ex: "Custo Mensal [Nome Gerado]").

Exemplos de como você deve pensar:
- Se a chave for 'Beneficio 1 - Unimed Seguros', um bom nome de exibição seria 'Unimed Seguros' ou 'Unimed'.
- Se a chave for 'Ferramenta XPTO - AWS Cloud Services', um bom nome seria 'AWS Cloud Services' ou 'AWS'.
- Se a chave for 'Planilha Custos Gympass Nov23', um bom nome seria 'Gympass'.
- Se a chave for 'Ferramenta 2 - Google_Workspace_Detalhes', um bom nome seria 'Google Workspace'.
- Se a chave for 'BENEFICIO_NOVO_SEGURO_VIAGEM_INTERNACIONAL', um bom nome seria 'Seguro Viagem Internacional'.

Responda APENAS com o nome de exibição limpo.
Se a chave não parecer representar um tipo de custo específico (ex: 'Backup Temporario', 'Notas Internas'), responda com 'N/A'.
Não inclua nenhuma outra palavra, introdução ou explicação.

Nome de exibição para '{df_key}':
"""
