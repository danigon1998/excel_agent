import pandas as pd

_GLOBAL_LOADED_DATAFRAMES = {}
_GLOBAL_PROCESSED_DATAFRAME = None

# En src/data_globals.py
CANONICAL_COLUMN_NAMES = {
    # --- IDENTIFICADORES UNIVERSAIS DE COLABORADOR ---
    "CPF Colaborador": "Identificador único do colaborador (CPF). Ex: 'CPF', 'Documento'.",
    "Nome Colaborador": "Nome completo do colaborador. Ex: 'Nome', 'Assinante', 'Beneficiário'.",
    "Centro de Custo": "Departamento ou centro de custo do colaborador. Ex: 'Departamento'.",
    "Salario": "Salário base mensal bruto do colaborador.",
    # --- ATRIBUTOS GENÉRICOS PARA QUALQUER ITEM DE CUSTO (Benefício ou Ferramenta) ---
    "Nome do Item": """Nome específico do benefício, ferramenta, licença ou serviço que está sendo atribuído ao colaborador. 
                    Exemplos: 'Plano Saúde Unimed Gold', 'Gympass Basic II', 'Licença AWS S3 Standard', 'Assinatura Zoom Pro Anual', 'Seguro de Viagem Europa Master'.
                    O LLM deve extrair este nome da planilha (de colunas como 'Descrição', 'Plano', 'Serviço') ou, como último recurso, inferi-lo a partir do nome do arquivo.""",
    "Tipo do Item": """Categoria geral do item de custo. 
                    Exemplos: 'Plano de Saúde', 'Benefício Academia', 'Serviço de Cloud', 'Software de Videoconferência', 'Seguro de Viagem', 'Licença de Software'.
                    O LLM pode tentar inferir isto a partir do 'Nome do Item' ou do nome do arquivo, ou mapeá-lo de uma coluna de 'Tipo' na planilha.""",
    "Data de Ativacao do Item": "Data em que o item (benefício/ferramenta/serviço) foi ativado ou iniciado para o colaborador.",
    "Custo Mensal do Item": "Custo mensal TOTAL atribuído ao colaborador para este 'Nome do Item' específico. Se o custo original for anual, deve ser normalizado para mensal se possível (ou indicar a frequência).",
    # "Detalhes Adicionais do Item": "Outras informações relevantes sobre o item, plano ou licença que não se encaixam nos outros campos.", # Opcional
    # --- EXEMPLO DE EXCEÇÃO: SUB-COMPONENTES MUITO ESPECÍFICOS (A SER USADO COM MODERAÇÃO) ---
    # Mantidos apenas se Github tiver uma estrutura de dados de entrada que consistentemente separa estes custos
    # e você PRECISA deles separados antes da análise. Caso contrário, poderiam ser apenas diferentes "Nome do Item".
    "Custo Copilot Github": "Custo específico da licença da ferramenta de assistência por IA Copilot no Github. Considerado um sub-item de 'Github'.",
    "Custo Licenca Base Github": "Custo da licença base de usuário para Github (excluindo Copilot). Considerado um sub-item de 'Github'.",
    # Se mantivermos os acima, "Custo Mensal Github" como entrada direta se torna menos relevante,
    # a menos que uma planilha já forneça o total consolidado de Github.
    # --- CAMPOS QUE ESTAVAM ANTES E PRECISAM SER REAVALIADOS ---
    # "Valor Parcela": "Parte do custo mensal, mas que já se encontra dentro do custo mensal"
    #   Este ainda é problemático. Se for um componente de um empréstimo ou algo assim,
    #   deveria ser modelado como um "Item" em si mesmo, ex:
    #   "Nome do Item": "Empréstimo Consignado XPTO", "Custo Mensal do Item": (valor da parcela)
    #   Não recomendo manter "Valor Parcela" como um canônico genérico com essa descrição.
}

LLM_AGENT1 = None
LLM_AGENT2 = None
