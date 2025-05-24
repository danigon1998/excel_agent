import os
from pathlib import Path
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain.agents import AgentExecutor, create_tool_calling_agent
import pandas as pd

from src import data_globals
from src.data_handler import standardize_dataframe

SYSTEM_PROMPT_AGENT_1 = """
Você é um agente especializado em padronização de dados de planilhas Excel.
Sua tarefa é receber um diretório, carregar todas as planilhas Excel (.xlsx) nele contidas,
e usar suas capacidades de IA para padronizar os nomes das colunas de cada planilha
com base em um conjunto pré-definido de nomes canônicos e suas descrições.
Após a padronização, os dados devem ser disponibilizados para um segundo agente de análise.
Use a ferramenta 'standardize_spreadsheets_tool' para realizar esta tarefa.
Explique brevemente seu plano antes de chamar a ferramenta.
"""


def _load_and_standardize_excel_files_core(
    input_dir: Path, llm_instance, canonical_names: dict
):
    if not input_dir.is_dir():
        print(f"Erro: O diretório não existe: {input_dir}")
        return {}
    excel_files = list(input_dir.glob("**/*.xlsx"))
    if not excel_files:
        print(f"Erro: Nenhum arquivo Excel encontrado em {input_dir}")
        return {}

    dataframes_dict_temp = {}
    for file_path in excel_files:
        file_name_stem = file_path.stem
        print(f"Carregando e padronizando arquivo (Agente 1): {file_name_stem}")
        try:
            df = pd.read_excel(file_path)
            if df.empty:
                print(f"Arquivo {file_name_stem} está vazio.")
                continue
            df_standardized = standardize_dataframe(
                df, file_name_stem, llm_instance, canonical_names
            )

            if df_standardized is not None and not df_standardized.empty:
                dataframes_dict_temp[file_name_stem] = df_standardized
                print(f"Arquivo {file_name_stem} padronizado com sucesso (Agente 1).")
            else:
                print(f"Falha ao padronizar {file_name_stem} ou resultado vazio.")
        except Exception as exc:
            print(f"Erro ao processar o arquivo {file_name_stem} (Agente 1): {exc}")
    return dataframes_dict_temp


@tool
def standardize_spreadsheets_tool(input_dir: str) -> str:
    """
    Carrega todos os arquivos Excel de um diretório, padroniza os nomes das colunas
    usando um LLM e armazena os DataFrames resultantes globalmente.
    Retorna uma mensagem de resumo.
    """
    print(
        f"\n[Agente 1 Ferramenta] Iniciando padronização para o diretório: {input_dir}"
    )

    if data_globals.LLM_AGENT1 is None:
        return "Erro: LLM para Agente 1 não inicializado."

    loaded_dfs = _load_and_standardize_excel_files_core(
        Path(input_dir), data_globals.LLM_AGENT1, data_globals.CANONICAL_COLUMN_NAMES
    )

    if not loaded_dfs:
        return "Nenhum arquivo Excel foi carregado ou padronizado."

    data_globals._GLOBAL_LOADED_DATAFRAMES = loaded_dfs

    summary_message = (
        f"Padronização completa. {len(loaded_dfs)} DataFrames carregados do diretório '{input_dir}': "
        f"{', '.join(loaded_dfs.keys())}. Os dados estão prontos para análise pelo Agente 2."
    )
    print(f"[Agente 1 Ferramenta] {summary_message}")
    return summary_message


def setup_standardization_agent(llm_instance, debug=False):
    """Configura e retorna o executor do Agente de Estandarização."""
    data_globals.LLM_AGENT1 = llm_instance
    tools = [standardize_spreadsheets_tool]
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT_AGENT_1),
            ("user", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    )
    agent = create_tool_calling_agent(llm_instance, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=debug,
        handle_parsing_errors=True,
    )
    return agent_executor
