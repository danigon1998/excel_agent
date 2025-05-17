import pandas as pd
from pathlib import Path


def load_excel_files(input_dir: Path):
    excel_files = list(input_dir.glob("*.xlsx"))

    dataframes_dict = {}
    for file_path in excel_files:
        file_name = file_path.stem
        try:
            df = pd.read_excel(file_path)
            dataframes_dict[file_name] = df
            print(f"Arquivo {file_name} carregado com sucesso.")
        except Exception as exc:
            print(f"Erro ao carregar o arquivo {file_name}: {exc}")

    return dataframes_dict


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

    try:
        df.to_excel(output_path, sheet_name=sheet_name, index=index)
        print(f"DataFrame salvo com sucesso em {output_path}.")
        return output_path
    except Exception as e:
        print(f"Erro ao salvar o DataFrame em {output_path}: {e}")
        return None
