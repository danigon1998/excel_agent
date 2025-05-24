import pandas as pd

_GLOBAL_LOADED_DATAFRAMES = {}
_GLOBAL_PROCESSED_DATAFRAME = None

CANONICAL_COLUMN_NAMES = {
    "CPF Colaborador": "Identificador único do colaborador (CPF). Exemplos comuns: 'CPF', 'Documento'.",
    "Nome Colaborador": "Nome completo do colaborador. Exemplos comuns: 'Nome', 'Assinante', 'Beneficiário'.",
    "Centro de Custo": "Departamento ou centro de custo. Exemplo comum: 'Departamento'.",
    "Salario": "Salário base do colaborador.",
    "Data Ativacao": "Data de ativação de um serviço ou benefício.",
    "Custo Mensal": "Custo mensal de um item ou serviço.",
    "Data Ativacao Github": "Data de ativação específica para Github.",
    "Custo Copilot Github": "Custo da licença Copilot do Github.",
    "Custo Licenca Github": "Custo da licença base do Github.",
    "Custo Mensal Github": "Custo mensal total para Github.",
    "Custo Mensal Unimed": "Custo mensal total para Unimed.",
    "Valor Parcela": "Parte do custo mensal, mas que já se encontra dentro do custo mensal",
    "Data Ativacao Gympass": "Data de ativação específica para o benefício Gympass.",
    "Tipo Plano Gympass": "Nome ou tipo do plano Gympass (ex: Basic, Silver, Gold).",
    "Custo Mensal Gympass": "Custo mensal TOTAL e específico para o benefício Gympass. É preferível usar este em vez de 'Custo Mensal' genérico para arquivos relacionados a Gympass.",
    "Data Ativacao Google Workspace": "Data de ativação específica para serviços Google Workspace.",
    "Custo Mensal Google Workspace": "Custo mensal TOTAL e específico para Google Workspace. É preferível usar este em vez de 'Custo Mensal' genérico para arquivos relacionados a Google Workspace.",
}

LLM_AGENT1 = None
LLM_AGENT2 = None
