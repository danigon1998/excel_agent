import pandas as pd
from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain.agents import AgentExecutor, create_tool_calling_agent
from src import data_globals
from src.data_handler import (
    save_dataframe_to_excel,
)
from src.data_processor import perform_full_cost_analysis


SYSTEM_PROMPT_AGENT_2 = """
Você é um agente de análise de custos que opera sobre dados organizacionais JÁ CARREGADOS E PADRONIZADOS.
Sua principal função é realizar cálculos de custos por colaborador e gerar relatórios.
Você não carrega dados brutos; você trabalha com os dados que o Agente de Estandarização preparou.
Sempre explique seu raciocínio antes de agir.

Exemplo de Interação:
Usuário: Analise os custos totais por pessoa e salve os resultados em 'data/output/relatorio_final.xlsx'.

Pensamento: Os dados já foram carregados e padronizados pelo Agente 1. Preciso calcular os custos por pessoa.
Ação: analyze_all_costs_tool
Observação: Análise de custos concluída. Custo total por colaborador calculado.
Pensamento: O usuário pediu para salvar os resultados, então agora devo executar a ferramenta de salvamento.
Ação: save_processed_data_tool (com output_path='data/output/relatorio_final.xlsx')
Observação: Arquivo salvo em 'data/output/relatorio_final.xlsx'.
Pensamento: A tarefa foi concluída com sucesso.
"""


@tool
def analyze_all_costs_tool() -> str:
    """
    Realiza a análise completa de custos com base nos DataFrames padronizados
    que foram carregados e processados globalmente.
    Calcula o custo TOTAL por colaborador.
    Esta ferramenta deve ser usada APÓS os dados terem sido padronizados e carregados globalmente.
    """
    print(f"\n[Agente 2 Ferramenta] Iniciando análise de custos.")
    if not data_globals._GLOBAL_LOADED_DATAFRAMES:
        return "Erro: Nenhum DataFrame padronizado encontrado. Execute o Agente de Estandarização primeiro."

    result_df = perform_full_cost_analysis(data_globals._GLOBAL_LOADED_DATAFRAMES)

    if result_df.empty:
        data_globals._GLOBAL_PROCESSED_DATAFRAME = pd.DataFrame()
        return "A análise de custos não produziu resultados. O DataFrame consolidado está vazio."

    data_globals._GLOBAL_PROCESSED_DATAFRAME = result_df

    summary = (
        "Análise de custos concluída. O custo total por colaborador foi calculado. "
        "As primeiras 3 linhas do DataFrame resultante são:\n"
        + result_df.head(3).to_markdown(index=False)
    )
    print(f"[Agente 2 Ferramenta] {summary}")
    return summary


@tool
def save_processed_data_tool(output_path: str) -> str:
    """
    Salva o DataFrame processado globalmente (resultado da análise de custos)
    em um arquivo Excel (.xlsx) no caminho especificado.
    """
    print(f"\n[Agente 2 Ferramenta] Salvando dados processados em: {output_path}")
    if (
        data_globals._GLOBAL_PROCESSED_DATAFRAME is None
        or data_globals._GLOBAL_PROCESSED_DATAFRAME.empty
    ):
        return "Erro: Nenhum DataFrame processado para salvar. Execute a análise de custos primeiro."

    path_obj = Path(output_path)
    saved_path = save_dataframe_to_excel(
        data_globals._GLOBAL_PROCESSED_DATAFRAME, path_obj
    )

    if saved_path is None:
        return f"Erro ao salvar o DataFrame em {output_path}."

    success_msg = f"DataFrame salvo com sucesso em {saved_path}"
    print(f"[Agente 2 Ferramenta] {success_msg}")
    return success_msg


def setup_cost_analysis_agent(llm_instance, debug=False):
    """Configura e retorna o executor do Agente de Análise de Custos."""
    data_globals.LLM_AGENT2 = llm_instance
    tools = [analyze_all_costs_tool, save_processed_data_tool]
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT_AGENT_2),
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
