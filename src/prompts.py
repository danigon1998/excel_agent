import json

SYSTEM_PROMPT_AGENT_1 = """
Você é um agente especializado em padronização de dados de planilhas Excel.
Sua tarefa é receber um diretório, carregar todas as planilhas Excel (.xlsx) nele contidas,
e usar suas capacidades de IA para padronizar os nomes das colunas de cada planilha
com base em um conjunto pré-definido de nomes canônicos e suas descrições.
Após a padronização, os dados devem ser disponibilizados para um segundo agente de análise.
Use a ferramenta 'standardize_spreadsheets_tool' para realizar esta tarefa.
Explique brevemente seu plano antes de chamar a ferramenta.
"""

SYSTEM_PROMPT_AGENT_2 = """
Você é um agente de análise de custos que opera sobre dados organizacionais JÁ CARREGADOS E PADRONIZADOS (pelo Agente 1).
Sua principal função é realizar cálculos de custos por colaborador e gerar relatórios.
Use a ferramenta 'analyze_all_costs_tool' para realizar a análise e os cálculos.
Depois, se solicitado, use 'save_processed_data_tool' para salvar o relatório.
Sempre explique seu raciocínio antes de agir.
"""


def get_standardize_dataframe_prompt(
    file_name_stem: str, original_columns: list, canonical_names: dict
):

    canonical_names_json_string = json.dumps(
        canonical_names, ensure_ascii=False, indent=2
    )

    return f"""
Sua tarefa é extrair informações relevantes de colunas de um arquivo Excel e mapeá-las para um conjunto de NOMES DE COLUNA PADRÃO VÁLIDOS.
O arquivo se chama: '{file_name_stem}'.
As colunas ORIGINAIS e EXATAS neste arquivo são: {original_columns}. Use estes nomes EXATOS como chaves no JSON de resposta.

Abaixo está a LISTA DE NOMES DE COLUNA PADRÃO VÁLIDOS (e suas descrições) para os quais você deve mapear as colunas originais. Use estes nomes EXATOS como valores no JSON:
{canonical_names_json_string}

Instruções CRÍTICAS para o mapeamento:
1.  Primeiro, identifique a natureza geral do arquivo (Salário, Benefício, Ferramenta, etc.) a partir do nome do arquivo ('{file_name_stem}') e das colunas originais.

2.  MAPEAMENTO PADRÃO PARA A MAIORIA DOS ARQUIVOS DE BENEFÍCIOS E FERRAMENTAS:
    a.  Para colunas que descrevem o nome específico do plano, serviço ou licença (ex: 'Plano Dental Prata', 'Licença Photoshop CC', 'AWS EC2 Instance m5.large'), mapeie para "Nome do Item". Use também o nome do arquivo '{file_name_stem}' para ajudar a formar um 'Nome do Item' descritivo (ex: "Unimed - Plano Prata", "AWS - EC2 Instance m5.large").
    b.  Para colunas que indicam o tipo geral do benefício ou ferramenta (ex: 'Plano de Saúde', 'Software', 'Serviço Cloud'), mapeie para "Tipo do Item". Se não houver coluna de tipo, tente inferir um tipo geral a partir do 'Nome do Item' ou do nome do arquivo.
    c.  Para colunas de data de início ou ativação, mapeie para "Data de Ativacao do Item".
    d.  Para colunas que representam o CUSTO MENSAL principal ou TOTAL do item descrito (geralmente chamadas 'Valor Mensal', 'Total', 'Custo Total', 'Montante Final', 'Mensalidade'), mapeie para "Custo Mensal do Item". Certifique-se que esta coluna seja puramente numérica e represente o valor monetário.

3.  CASOS ESPECIAIS (use com moderação, somente se aplicável):
    # * Se o arquivo for claramente sobre 'Github' e contiver colunas distintas para custos de 'Copilot' e 'Licença Base', 

4.  DADOS DO COLABORADOR: Para colunas de identificação (CPF, Nome), departamento e salário base, use "CPF Colaborador", "Nome Colaborador", "Centro de Custo", "Salario".

5.  OMISSÃO: Se uma coluna ORIGINAL não se encaixar claramente em NENHUM dos nomes padrão válidos conforme as instruções acima, OMITE-A do dicionário JSON. Não invente mapeamentos.

Formato OBRIGATÓRIO da Resposta:
Responda ÚNICA E EXCLUSIVAMENTE com um objeto JSON.
As CHAVES do dicionário JSON DEVEM SER NOMES EXATOS da lista de colunas ORIGINAIS fornecida ({original_columns}).
Os VALORES do dicionário JSON DEVEM SER NOMES EXATOS da LISTA DE NOMES DE COLUNA PADRÃO VÁLIDOS.
NÃO inclua NENHUMA palavra, introdução, explicação, comentário, ou blocos de markdown.
A sua resposta DEVE SER ESTRITAMENTE O DICIONÁRIO JSON, e nada mais.

Exemplo (arquivo 'Beneficio_Plano_Saude_Empresa.xlsx', colunas originais ['Matrícula', 'Nome Completo', 'Plano Contratado', 'Valor Mensalidade', 'Obs']):
{{
    "Nome Completo": "Nome Colaborador",
    "Plano Contratado": "Nome do Item","
    "Valor Mensalidade": "Custo Mensal do Item"
}}
(Neste exemplo, 'Matrícula' e 'Obs' foram omitidas. 'Tipo do Item' poderia ser inferido como 'Plano de Saúde').
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
