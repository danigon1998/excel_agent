import pandas as pd
from pathlib import Path
from data_handler import load_excel_files, save_dataframe_to_excel

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

    colaboradores_df_key = None
    for key in loaded_dataframes.keys():
        if "colaboradores" in key.lower():
            colaboradores_df_key = key
            break

    if colaboradores_df_key:
        df_to_save = loaded_dataframes[colaboradores_df_key]
        output_path = Path("data/output")
        output_file_name = "colaboradores_estandarizados.xlsx"
        output_file_path = output_path / output_file_name

        print(f"Tentando guardar {colaboradores_df_key} em {output_file_path}")
        saved_path = save_dataframe_to_excel(df_to_save, output_file_path)

        if saved_path:
            print(f"Arquivo salvo com sucesso em {saved_path}")
        else:
            print(
                f"Erro ao salvar o arquivo {colaboradores_df_key} em {output_file_path}"
            )
    else:
        print("Erro: DataFrame de colaboradores não encontrado.")


if __name__ == "__main__":
    main()
