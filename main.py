import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from pathlib import Path
from src import data_globals
from src.data_ingestion import load_and_standardize_data_phase
from src.cost_analysis_agent import setup_cost_analysis_agent
from src.data_handler import save_dataframe_to_excel


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


def run_processing_pipeline(input_dir: str, output_file: str, debug: bool = True):
    """
    Executa o pipeline de dois agentes: Estandarização e Análise de Custos.
    """
    print("--- Configurando LLMs e Agentes ---")
    load_dotenv()

    llm_for_mapping = setup_llm_instance(
        model="llama-3.3-70b-versatile", temperature=0.1
    )
    llm_for_analysis_agent = setup_llm_instance()

    data_globals.LLM_AGENT2 = llm_for_analysis_agent

    loaded_and_standardized_data = load_and_standardize_data_phase(
        input_dir, llm_for_mapping, data_globals.CANONICAL_COLUMN_NAMES
    )
    if not loaded_and_standardized_data:
        print("\nFalha na etapa de carregamento e padronização de dados. Abortando.")
        return

    data_globals._GLOBAL_LOADED_DATAFRAMES = loaded_and_standardized_data

    if not data_globals._GLOBAL_LOADED_DATAFRAMES:
        print("\nFalha na etapa de estandarização. Abortando.")
        return

    summary_keys = list(loaded_and_standardized_data.keys())
    print(
        f"INFO [Pipeline]: {len(loaded_and_standardized_data)} DataFrames carregados e padronizados: {summary_keys}"
    )
    print("Os dados estão prontos para análise pelo Agente de Análise de Custos.")

    print(f"\n--- Etapa 2: Agente de Análise de Custos ---")
    cost_analysis_agent_executor = setup_cost_analysis_agent(
        llm_for_analysis_agent, debug=debug
    )

    analysis_agent_input = f"Realize a análise de custos completa com os dados preparados e salve o relatório em '{output_file}'."

    analysis_response = cost_analysis_agent_executor.invoke(
        {"input": analysis_agent_input}
    )
    print(f"\nResposta do Agente de Análise de Custos: {analysis_response['output']}")
    if (
        data_globals._GLOBAL_PROCESSED_DATAFRAME is not None
        and not data_globals._GLOBAL_PROCESSED_DATAFRAME.empty
    ):
        print(f"\n--- Etapa 3: Salvando Relatório Final em '{output_file}' ---")

        saved_path = save_dataframe_to_excel(
            data_globals._GLOBAL_PROCESSED_DATAFRAME, Path(output_file)
        )
        if saved_path:
            print(f"Relatório final salvo com sucesso em: {saved_path}")
        else:
            print(f"Falha ao salvar o relatório final em: {output_file}")
    else:
        print("AVISO [Pipeline]: Nenhum DataFrame processado encontrado para salvar.")

    print("\n--- Pipeline Concluído ---")


if __name__ == "__main__":

    INPUT_DATA_DIR = "data/input"
    OUTPUT_REPORT_FILE = "data/output/relatorio_final_agentes.xlsx"

    run_processing_pipeline(INPUT_DATA_DIR, OUTPUT_REPORT_FILE, debug=True)
