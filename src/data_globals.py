import pandas as pd

_GLOBAL_LOADED_DATAFRAMES = {}
_GLOBAL_PROCESSED_DATAFRAME = None

CANONICAL_COLUMN_NAMES = {
    # --- IDENTIFICADORES UNIVERSAIS DE COLABORADOR ---
    "CPF Colaborador": "Identificador único do colaborador (CPF). Colunas originais comuns: 'CPF', 'Documento', 'ID Fiscal'.",
    "Nome Colaborador": "Nome completo do colaborador. Colunas originais comuns: 'Nome', 'Assinante', 'Beneficiário', 'Funcionário'.",
    "Centro de Custo": "Departamento ou centro de custo ao qual o colaborador pertence. Colunas originais comuns: 'Departamento', 'Setor', 'CC'.",
    "Salario": "Salário base mensal bruto do colaborador. Deve ser um valor numérico. Colunas originais comuns: 'Salário Base', 'Remuneração Mensal', 'Vencimento'.",
    # --- ATRIBUTOS GENÉRICOS PARA QUALQUER ITEM DE CUSTO (Benefício ou Ferramenta) ---
    "Nome do Item": """Nome específico textual que descreve o benefício, ferramenta, licença, plano, serviço ou rubrica. 
                    Esta coluna deve conter a DESCRIÇÃO do item.
                    Exemplos de valores FINAIS que iriam nesta coluna: 'Plano Saúde Unimed Gold', 'Gympass Basic II', 'Licença AWS S3 Standard', 'Assinatura Zoom Pro Anual', 'Seguro de Viagem Europa Master', 'Mensalidade Titular Faixa Etária Plano X', 'Co-participação Farmácia Global'.
                    Colunas ORIGINAIS comuns que normalmente são mapeadas para este campo: 'Rubrica', 'Descrição do Serviço', 'Plano Contratado', 'Detalhe do Item', 'Item Name', 'Service Description', 'Plan Type'.
                    O LLM deve extrair este nome da planilha. Se a planilha inteira se referir a um único item sem uma coluna descritiva interna (ex: para um arquivo 'Ferramenta_Zoom_Pro.xlsx'), o 'Nome do Item' poderia ser derivado do nome do arquivo como 'Licença Zoom Pro'.""",
    "Tipo do Item": """Categoria geral ou classificação do item de custo. Ajuda a agrupar itens similares.
                    Exemplos de valores FINAIS que iriam nesta coluna: 'Plano de Saúde', 'Benefício Academia', 'Serviço Cloud', 'Software de Produtividade', 'Seguro de Viagem', 'Licença de Software', 'Taxa Adicional de Benefício'.
                    Colunas ORIGINAIS comuns que normalmente são mapeadas para este campo: 'Tipo de Benefício', 'Categoria do Serviço', 'Service Category', 'Product Family'.
                    O LLM pode tentar inferir isto a partir do 'Nome do Item' ou do nome do arquivo, ou mapeá-lo de uma coluna de 'Tipo' na planilha.""",
    "Data de Ativacao do Item": "Data em que o item (benefício/ferramenta/serviço) foi ativado, iniciado ou concedido para o colaborador. Colunas originais comuns: 'Data Início', 'Data de Concessão', 'Activation Date'.",
    "Custo Mensal do Item": """Valor NUMÉRICO que representa o custo mensal TOTAL atribuído ao colaborador para o 'Nome do Item' específico.
                    Esta coluna DEVE conter apenas números.
                    Se o custo original na planilha for anual ou de outra frequência, idealmente deveria ser normalizado para mensal (se a informação para fazer isso estiver disponível ou se for uma instrução).
                    Exemplos de valores FINAIS que iriam nesta coluna: 150.75, 25.00, 1200.00.
                    Colunas ORIGINAIS comuns que normalmente são mapeadas para este campo: 'Valor Mensal', 'Total Custo', 'Custo Efetivo', 'Mensalidade', 'Price per Month', 'Amount', 'Subtotal'. NÃO mapeie colunas textuais como 'Rubrica' para este campo.""",
    # --- CASOS ESPECIAIS (Exemplo: Sub-componentes de Github) ---
    "Custo Copilot Github": "Custo específico da licença da ferramenta de assistência por IA Copilot no Github. Considerado um sub-item de 'Github'. Deve ser numérico.",
    "Custo Licenca Base Github": "Custo da licença base de usuário para Github (excluindo Copilot). Considerado um sub-item de 'Github'. Deve ser numérico.",
}

LLM_AGENT1 = None
LLM_AGENT2 = None
