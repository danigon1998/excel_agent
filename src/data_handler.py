import pandas as pd
from pathlib import Path


COLUNA_MAPEIO_GERAL = {
    # Identificadores principais
    "CPF": "CPF Colaborador",
    "Documento": "CPF Colaborador",
    "Nome": "Nome Colaborador",
    "Assinante": "Nome Colaborador",
    "Beneficiário": "Nome Colaborador",
    # Outros dados generais
    "Departamento": "Centro de Custo",
    "Salario": "Salario",
    "Data Ativacao": "Data Ativacao",
    "Valor Mensal": "Custo Mensal",
    "Valor": "Custo",
    "Plano": "Tipo de Plano",
    "Licença": "Tipo de Licenca",
    "Total": "Custo Total Geral",
    # Campos de beneficios
    "Idade": "Idade",
    "Dependência": "Dependencia",
    "Data Limite": "Data Limite",
    "Data Inclusão": "Data Inclusao",
    "Data Exclusão": "Data Exclusao",
    "Rubrica": "Rubrica",
    "Outros": "Outros Custos",
    "Parcela": "Parcela",
    "Valor Parcela": "Valor Parcela",
    "Coparticipacao": "Coparticipacao",
    "Valor Desconto": "Valor Desconto",
}

# Mapeio específico baseado numa palabra chave no nome do arquivo (sem extensão).
COLUNA_MAPEIO_POR_TIPO = {
    "colaboradores": {  # Para planilha "Ddos Colaboradores.xlsx"
        "Nome": "Nome Colaborador",
        "CPF": "CPF Colaborador",
        "Departamento": "Centro de Custo",
        "Salario": "Salario",
    },
    "github": {  # Para planilha "Ferramenta 1 - Github.xlsx"
        "Assinante": "Nome Colaborador",
        "Documento": "CPF Colaborador",
        "Data Ativacao": "Data Ativacao Github",
        "Copilot": "Custo Copilot Github",
        "Licença": "Custo Licenca Github",
        "Valor Mensal": "Custo Mensal Github",
    },
    "google workspace": {  # Para planilha "Ferramenta 2 - Google workspace.xlsx"
        "Assinante": "Nome Colaborador",
        "Documento": "CPF Colaborador",
        "Data Ativacao": "Data Ativacao Google Workspace",
        "Valor Mensal": "Custo Mensal Google Workspace",
    },
    "unimed": {  # Para planilha "Beneficio 1 - Unimed.xlsx"
        "Código": "Codigo Beneficio Unimed",
        "Beneficiário": "Nome Colaborador",
        "CPF": "CPF Colaborador",
        "Tipo": "Tipo Beneficio Unimed",
        "Idade": "Idade Beneficiario Unimed",
        "Dependência": "Dependencia Beneficiario Unimed",
        "Data Limite": "Data Limite Beneficio Unimed",
        "Data Inclusão": "Data Inclusao Beneficio Unimed",
        "Data Exclusão": "Data Exclusao Beneficio Unimed",
        "Rubrica": "Rubrica Beneficio Unimed",
        "Outros": "Outros Custos Beneficio Unimed",
        "Total": "Custo Mensal Unimed",
    },
    "gympass": {  # Para planilha "Beneficio 2 - Gympass.xlsx"
        "Assinante": "Nome Colaborador",
        "Documento": "CPF Colaborador",
        "Data Ativacao": "Data Ativacao Gympass",
        "Plano": "Plano Gympass",
        "Parcela": "Parcela Gympass",
        "Valor Parcela": "Valor Parcela Gympass",
        "Coparticipacao": "Coparticipacao Gympass",
        "Valor Desconto": "Valor Desconto Gympass",
        "Valor Mensal": "Custo Mensal Gympass",
    },
}


def standardize_dataframe(df: pd.DataFrame, file_name_stem: str):

    standardized_df = df.copy()

    standardized_df.columns = standardized_df.columns.str.strip()

    applied_specific_map = False
    for keyword, mapping in COLUNA_MAPEIO_POR_TIPO.items():
        if keyword in file_name_stem.lower():
            rename_dict = {col_orig: col_std for col_orig, col_std in mapping.items()}
            if rename_dict:
                standardized_df = standardized_df.rename(columns=rename_dict)
                print(
                    f"Aplicado mapeio específico para '{keyword}' ({', '.join(rename_dict.keys())}) ao arquivo '{file_name_stem}'."
                )
            applied_specific_map = True
            break

    if not applied_specific_map:
        rename_dict = {
            col_orig: col_std for col_orig, col_std in COLUNA_MAPEIO_GERAL.items()
        }
        if rename_dict:
            standardized_df = standardized_df.rename(columns=rename_dict)
            print(
                f"Aplicado mapeio geral ({', '.join(rename_dict.keys())}) ao arquivo '{file_name_stem}'."
            )

    cols_to_strip_data = ["CPF Colaborador", "Nome Colaborador"]
    for col in cols_to_strip_data:
        if col in standardized_df.columns and standardized_df[col].dtype == "object":
            try:
                standardized_df[col] = standardized_df[col].astype(str).str.strip()
            except Exception as e:
                print(
                    f"Advertencia: Não se aplicou strip() na coluna '{col}'. Error: {e}"
                )

    return standardized_df


def load_excel_files(input_dir: Path):

    if not input_dir.is_dir():
        print(f"Erro: O endereço não existe ou não é do tipo Path: {input_dir}")
        return {}

    excel_files = list(input_dir.glob("**/*.xlsx"))

    if not excel_files:
        print(f"Erro: Nenhum arquivo Excel encontrado em {input_dir}")
        return {}

    dataframes_dict = {}
    for file_path in excel_files:
        file_name_stem = file_path.stem
        print(f"Carregando arquivo: {file_name_stem}")
        try:
            df = pd.read_excel(file_path)
            if df.empty:
                print(f"Arquivo {file_name_stem} está vazio.")
                continue
            df_standardized = standardize_dataframe(df, file_name_stem)
            print(f"Colunas processadas para estandarização")
            dataframes_dict[file_name_stem] = df_standardized
            print(f"Arquivo {file_name_stem} carregado com sucesso.")
        except Exception as exc:
            print(f"Erro ao carregar o arquivo {file_name_stem}: {exc}")

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
