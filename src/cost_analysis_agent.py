import pandas as pd
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain.agents import AgentExecutor, create_tool_calling_agent
from src import data_globals
from src.data_processor import (
    consolidate_all_cost,
    calculate_total_cost_per_collaborator,
)
from src.prompts import SYSTEM_PROMPT_AGENT_2


@tool
def consolidate_all_data_tool():
    """
    PASSO 1 da análise: Consolida todos os DataFrames de itens de custo em uma tabela principal.
    Usa o LLM internamente para gerar nomes de exibição para cada tipo de custo,
    resultando em colunas de custo específicas (ex: "Custo Mensal Unimed").
    O resultado intermediário é armazenado globalmente para o próximo passo.
    Deve ser chamado antes de calcular os custos totais.
    """
    print(
        f"\n[Agente 2 Ferramenta]: Iniciando consolidação de dados (consolidate_all_data_tool)..."
    )
    if not data_globals._GLOBAL_LOADED_DATAFRAMES:
        return "Erro Crítico: Nenhum DataFrame (saída da Etapa 1 de padronização) encontrado."

    consolidated_df = consolidate_all_cost(data_globals._GLOBAL_LOADED_DATAFRAMES)

    if consolidated_df.empty:
        data_globals._CONSOLIDATED_DF_PRE_TOTALS = pd.DataFrame()
        return "Falha na consolidação de dados ou nenhum dado para consolidar. DataFrame intermediário está vazio."

    data_globals._CONSOLIDATED_DF_PRE_TOTALS = consolidated_df

    colab_df_key = next(
        (
            key
            for key in data_globals._GLOBAL_LOADED_DATAFRAMES
            if "colaboradores" in key.lower()
        ),
        None,
    )
    num_colab_cols = 0
    if colab_df_key and colab_df_key in data_globals._GLOBAL_LOADED_DATAFRAMES:
        num_colab_cols = len(
            data_globals._GLOBAL_LOADED_DATAFRAMES[colab_df_key].columns
        )
        if (
            "Salario"
            not in data_globals._GLOBAL_LOADED_DATAFRAMES[colab_df_key].columns
        ):
            num_colab_cols += 1

    num_cost_item_cols = len(consolidated_df.columns) - num_colab_cols

    return f"Consolidação de dados completa. {num_cost_item_cols if num_cost_item_cols > 0 else 'Nenhum novo'} tipo(s) de custo de item foi(ram) consolidados. O DataFrame intermediário está pronto para o cálculo do custo total."


@tool
def calculate_employee_total_cost_tool():
    """
    PASSO 2 da análise: Calcula o 'Custo Total Colaborador' com base no DataFrame
    consolidado globalmente (que já inclui Salário e colunas de custo específicas por item).
    O resultado final é armazenado globalmente para ser salvo pelo sistema principal.
    """
    print(f"\n[Agente 2 Ferramenta]: Calculando custo total por colaborador...")
    if (
        data_globals._CONSOLIDATED_DF_PRE_TOTALS is None
        or data_globals._CONSOLIDATED_DF_PRE_TOTALS.empty
    ):
        return "Erro: DataFrame consolidado (pré-totais) não encontrado ou vazio. Execute a ferramenta de consolidação ('consolidate_all_data_tool') primeiro."

    final_df = calculate_total_cost_per_collaborator(
        data_globals._CONSOLIDATED_DF_PRE_TOTALS
    )

    if final_df.empty:
        data_globals._GLOBAL_PROCESSED_DATAFRAME = pd.DataFrame()
        return "Cálculo do custo total não produziu resultados. DataFrame final está vazio."

    data_globals._GLOBAL_PROCESSED_DATAFRAME = final_df
    summary = "Cálculo do custo total por colaborador concluído. O DataFrame final está pronto para ser salvo. " "As primeiras 3 linhas do DataFrame resultante são:\n" + final_df.head(
        3
    ).to_markdown(
        index=False
    )
    return summary


def setup_cost_analysis_agent(llm_instance, debug=False):
    """Configura e retorna o executor do Agente de Análise de Custos."""
    data_globals.LLM_AGENT2 = llm_instance
    tools = [consolidate_all_data_tool, calculate_employee_total_cost_tool]
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
