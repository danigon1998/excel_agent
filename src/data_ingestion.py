import pandas as pd
from pathlib import Path
from src.data_handler import standardize_dataframe
from src import data_globals


def load_and_standardize_data_phase(
    input_dir_str: str, llm_for_mapping, canonical_names_map: dict
):
    """
    Etapa 1: Carrega todos os arquivos Excel de um diretório, padroniza os nomes das colunas
    usando o llm_for_mapping, e retorna um dicionário de DataFrames.
    """
    print(f"\n--- INICIANDO FASE 1: Carregamento e Padronização de Dados ---")
    input_dir = Path(input_dir_str)
    if not input_dir.is_dir():
        print(f"ERRO [Ingestion]: O diretório não existe: {input_dir}")
        return {}

    excel_files = list(input_dir.glob("**/*.xlsx"))
    if not excel_files:
        print(f"ERRO [Ingestion]: Nenhum arquivo Excel encontrado em {input_dir}")
        return {}

    dataframes_processed_dict = {}
    for file_path in excel_files:
        file_name_stem = file_path.stem
        print(f"\n[Ingestion] Processando arquivo: {file_name_stem}")
        try:
            df_original = pd.read_excel(file_path)
            if df_original.empty:
                print(f"[Ingestion]: Arquivo '{file_name_stem}' está vazio.")
                dataframes_processed_dict[file_name_stem] = df_original
                continue

            df_standardized = standardize_dataframe(
                df_original, file_name_stem, llm_for_mapping, canonical_names_map
            )

            if df_standardized is not None and not df_standardized.empty:
                dataframes_processed_dict[file_name_stem] = df_standardized
                print(
                    f"[Ingestion]: Arquivo '{file_name_stem}' padronizado com sucesso."
                )
            else:
                print(
                    f"ADVERTÊNCIA [Ingestion]: Falha ao padronizar '{file_name_stem}' ou resultado vazio. DataFrame original será usado (se existir)."
                )
                dataframes_processed_dict[file_name_stem] = (
                    df_original if df_original is not None else pd.DataFrame()
                )

        except Exception as exc:
            print(
                f"ERRO CRÍTICO [Ingestion]: Erro ao processar o arquivo '{file_name_stem}': {exc}"
            )
            dataframes_processed_dict[file_name_stem] = pd.DataFrame()

    print(
        f"--- FIM FASE 1: Padronização completa. {len(dataframes_processed_dict)} DataFrames processados. ---"
    )
    return dataframes_processed_dict
