import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

from src import data_globals
from src.standardization_agent import setup_standardization_agent
from src.cost_analysis_agent import setup_cost_analysis_agent


def setup_llm_instance(
    temperature=0.0,
    model="llama3-8b-8192",
):
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY não definida.")
    return ChatGroq(
        temperature=temperature, groq_api_key=groq_api_key, model_name=model
    )


def run_two_agent_pipeline(input_dir: str, output_file: str, debug: bool = True):
    """
    Executa o pipeline de dois agentes: Estandarização e Análise de Custos.
    """
    print("--- Configurando LLMs e Agentes ---")
    load_dotenv()

    llm_for_agent1 = setup_llm_instance(
        model="llama-3.3-70b-versatile", temperature=0.1
    )
    llm_for_agent2 = setup_llm_instance()

    agent_executor_std = setup_standardization_agent(llm_for_agent1, debug=debug)
    agent_executor_analysis = setup_cost_analysis_agent(llm_for_agent2, debug=debug)

    print(f"\n--- Etapa 1: Agente de Estandarização ---")
    std_agent_input = (
        f"Carregue e padronize todas as planilhas do diretório '{input_dir}'."
    )
    std_response = agent_executor_std.invoke({"input": std_agent_input})
    print(f"\nResposta do Agente de Estandarização: {std_response['output']}")

    if not data_globals._GLOBAL_LOADED_DATAFRAMES:
        print("\nFalha na etapa de estandarização. Abortando.")
        return

    print(f"\n--- Etapa 2: Agente de Análise de Custos ---")
    analysis_agent_input = f"Realize a análise de custos completa com os dados preparados e salve o relatório em '{output_file}'."

    analysis_response = agent_executor_analysis.invoke({"input": analysis_agent_input})
    print(f"\nResposta do Agente de Análise de Custos: {analysis_response['output']}")

    print("\n--- Pipeline de Dois Agentes Concluído ---")


if __name__ == "__main__":

    INPUT_DATA_DIR = "data/input"
    OUTPUT_REPORT_FILE = "data/output/relatorio_final_agentes.xlsx"

    run_two_agent_pipeline(INPUT_DATA_DIR, OUTPUT_REPORT_FILE, debug=True)
