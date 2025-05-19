import pandas as pd
from pathlib import Path
from data_handler import load_excel_files, save_dataframe_to_excel
from data_processor import consolidate_all_cost, calculate_total_cost_per_collaborator

from dotenv import load_dotenv


GROQ_API_KEY = load_dotenv("GROQ_API_KEY")


def main():
    print("Iniciando Processo")

    input_base_dir = Path("data/input")
    loaded_dataframes = load_excel_files(input_base_dir)

    if not loaded_dataframes:
        print("Erro: Não foi possivel carregar nenhum arquivo.")
        print(f"Rota usada: {input_base_dir}")
        return

    print("Chaves de DataFrames disponiveis:", list(loaded_dataframes.keys()))

    print("Iniciando processo de consolidação e cálculo de custos")

    consolidated_df = consolidate_all_cost(loaded_dataframes)

    if consolidated_df.empty:
        print("Erro: DataFrame consolidado está vazio.")
        return
    print("Consolidação e cálculo de custos concluídos")
    print(consolidated_df.head())
    print("Colunas do DataFrame Consolidado")
    print(consolidated_df.columns.to_list())

    final_cost_df = calculate_total_cost_per_collaborator(consolidated_df)

    print("Vista Previa")
    print(final_cost_df.head())
    print("Processo concluído")
    print(final_cost_df.columns.to_list())

    print("Guardando o DataFrame final no arquivo Excel")
    output_dir = Path("data/output")
    output_filename = "Relatorio custos consolidados.xlsx"
    output_path = output_dir / output_filename

    saved_path = save_dataframe_to_excel(final_cost_df, output_path)

    if saved_path:
        print(f"DataFrame salvo com sucesso em {saved_path}.")
    else:
        print("Erro ao salvar o DataFrame.")


if __name__ == "__main__":
    main()
