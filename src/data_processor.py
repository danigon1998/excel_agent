import pandas as pd


def merge_cost_data(main_df: pd.DataFrame, cost_df: pd.DataFrame, cost_type_name: str):
    if main_df.empty:
        print("DataFrame principal está vazio.")
        return main_df
    if cost_df.empty:
        print(f"DataFrame de custo {cost_type_name} está vazio.")
        main_df[f"Custo Mensal {cost_type_name}"] = 0
        return main_df

    if "CPF Colaborador" not in main_df.columns:
        raise ValueError(
            "Coluna 'CPF Colaborador' não encontrada no DataFrame principal."
        )
    if "CPF Colaborador" not in cost_df.columns:
        raise ValueError(
            f"Coluna 'CPF Colaborador' não encontrada no DataFrame de custo {cost_type_name}."
        )

    cost_column_name = f"Custo Mensal {cost_type_name}"
    if cost_column_name not in cost_df.columns:
        print(
            f"Aviso: A coluna de custo esperada '{cost_column_name}' não foi encontrada"
        )
        main_df[cost_column_name] = 0
        return main_df

    cols_to_merge = ["CPF Colaborador", cost_column_name]
    cost_df_grouped = (
        cost_df.groupby("CPF Colaborador")[cost_column_name].sum().reset_index()
    )
    cost_df_grouped.rename(columns={cost_column_name: cost_column_name}, inplace=True)
    merged_df = pd.merge(
        main_df,
        cost_df_grouped,
        on="CPF Colaborador",
        how="left",
        suffixes=(
            "",
            f"_{cost_type_name}_x",
        ),  # Sufixo vazio para o main_df, sufixo para o cost_df (se houver colisão)
    )
    merged_df[cost_column_name] = merged_df[cost_column_name].fillna(0)
    print(f"Merge realizado com sucesso para {cost_type_name}")
    return merged_df


def consolidate_all_cost(dataframes_dict: dict):
    print("Iniciando a consolidação de todos os custos")

    df_colaborares = None
    for key, df in dataframes_dict.items():
        if "colaboradores" in key.lower():
            df_colaborares = df.copy()
            break

    if df_colaborares is None:
        print("Erro: DataFrame de colaboradores não encontrado.")
        return pd.DataFrame()

    cost_types = {
        "github": "Github",
        "google workspace": "Google Workspace",
        "unimed": "Unimed",
        "gympass": "Gympass",
    }

    final_consolidated_df = df_colaborares
    for key_in_dict, display_name in cost_types.items():
        actual_df_key = None
        for loaded_key in dataframes_dict.keys():
            if key_in_dict in loaded_key.lower():
                actual_df_key = loaded_key
                print(actual_df_key)
                break

        if actual_df_key and dataframes_dict.get(actual_df_key) is not None:
            print(
                f"Consolidando dados de: {display_name} (chave original: {actual_df_key})"
            )
            df_cost_source = dataframes_dict[actual_df_key]
            final_consolidated_df = merge_cost_data(
                final_consolidated_df, df_cost_source, display_name
            )
        else:
            print(
                f"Aviso: DataFrame para '{display_name}' não encontrado no dicionario"
            )
            if f"Custo Mensal {display_name}" not in final_consolidated_df.columns:
                final_consolidated_df[f"Custo Mensal {display_name}"] = 0.0

    print("Consolidação de todos os custos concluída")
    return final_consolidated_df


def calculate_total_cost_per_collaborator(consolidated_df: pd.DataFrame):
    if consolidated_df.empty:
        print("DataFrame consolidado está vazio")
        return consolidated_df

    print("Calculando custo total por colaborador")

    cost_columns = [
        col
        for col in consolidated_df.columns
        if col.startswith("Custo Mensal") or col == "Salario"
    ]

    if not cost_columns:
        print(
            "Aviso: Nenhuma coluna de custo mensal padronizada encontrada no DataFrame"
        )
        consolidated_df["Custo Total Colaborador"] = 0.0
        return consolidated_df

    consolidated_df["Custo Total Colaborador"] = (
        consolidated_df[cost_columns]
        .sum(
            axis=1,
            skipna=True,
            numeric_only=True,
        )
        .round(2)
    )

    print("Custo total por colaborador calculado")
    return consolidated_df


def perform_full_cost_analysis(dataframes_dict: dict):
    consolidated_df = consolidate_all_cost(dataframes_dict)
    if consolidated_df.empty:
        print("Erro: DataFrame consolidado está vazio.")
        return pd.DataFrame()
    consolidated_df = calculate_total_cost_per_collaborator(consolidated_df)
    return consolidated_df
