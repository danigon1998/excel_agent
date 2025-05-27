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


def save_dataframe_to_excel(
    df: pd.DataFrame,
    output_path: Path,
    sheet_name: str = "Resultado_Agente",
    index: bool = False,
):
    if not isinstance(df, pd.DataFrame):
        print(f"O objeto {df} não é um DataFrame.")
        return None

    if not isinstance(output_path, Path):
        try:
            output_path = Path(output_path)
        except Exception as e:
            print(f"O objeto {output_path} não é um Path.")
            return None

    output_dir = output_path.parent

    if not output_dir.exists():
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            print(f"Diretório {output_dir} criado com sucesso.")
        except Exception as e:
            print(f"Erro ao criar o diretório {output_dir}: {e}")
            return None

    if output_path.exists():
        base_name = output_path.stem
        extension = output_path.suffix
        i = 1
        while True:
            new_name = f"{base_name}_{i}{extension}"
            new_path = output_dir / new_name
            if not new_path.exists():
                output_path = new_path
                break
            i += 1

    try:
        df.to_excel(output_path, sheet_name=sheet_name, index=index)
        print(f"DataFrame salvo com sucesso em {output_path}.")
        return output_path
    except Exception as e:
        print(f"Erro ao salvar o DataFrame em {output_path}: {e}")
        return None
