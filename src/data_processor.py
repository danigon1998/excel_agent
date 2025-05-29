import pandas as pd
from src import data_globals
from src.prompts import get_display_name_from_df_key_prompt


def _get_display_name_from_llm(df_key: str, llm_instance):
    """
    Usa o LLM para gerar um nome de exibição limpo a partir de uma chave de DataFrame (nome do arquivo).
    """
    prompt_llm = get_display_name_from_df_key_prompt(df_key)
    try:
        response = llm_instance.invoke(prompt_llm)
        clean_name = response.content if hasattr(response, "content") else str(response)
        clean_name = clean_name.strip().title()

        print(f"LLM gerou display name '{clean_name}' para df_key '{df_key}'.")
        return clean_name
    except Exception as e:
        print(
            f"Erro ao chamar LLM para gerar display name para '{df_key}': {e}. Usando fallback."
        )
        return


def merge_cost_data(
    main_df: pd.DataFrame, cost_df: pd.DataFrame, display_name_for_final_column: str
):
    if main_df.empty:
        print("DataFrame principal está vazio.")
        return main_df

    final_target_cost_column_name = f"Custo Mensal {display_name_for_final_column}"

    if cost_df.empty:
        print(f"DataFrame de custo {display_name_for_final_column} está vazio.")
        main_df[f"Custo Mensal {display_name_for_final_column}"] = 0.0
        return main_df

    if "CPF Colaborador" not in main_df.columns:
        raise ValueError(
            "ERRO CRÍTICO: 'CPF Colaborador' não encontrado no DataFrame principal (main_df)."
        )
    if "CPF Colaborador" not in cost_df.columns:
        raise ValueError(
            f"ERRO CRÍTICO: 'CPF Colaborador' não encontrado no DataFrame de custo para '{display_name_for_final_column}'."
        )

    source_cost_column = "Custo Mensal do Item"
    if source_cost_column not in cost_df.columns:
        print(
            f"Aviso: A coluna de custo esperada '{source_cost_column}' não foi encontrada"
        )
        main_df[source_cost_column] = 0
        return main_df

    cost_df[source_cost_column] = pd.to_numeric(
        cost_df[source_cost_column], errors="coerce"
    ).fillna(0.0)
    cost_df_grouped = (
        cost_df.groupby("CPF Colaborador")[source_cost_column].sum().reset_index()
    )
    cost_df_grouped.rename(
        columns={source_cost_column: final_target_cost_column_name}, inplace=True
    )
    merged_df = pd.merge(
        main_df,
        cost_df_grouped,
        on="CPF Colaborador",
        how="left",
    )
    merged_df[final_target_cost_column_name] = merged_df[
        final_target_cost_column_name
    ].fillna(0.0)
    print(f"Merge realizado com sucesso para {display_name_for_final_column}")
    return merged_df


def consolidate_all_cost(dataframes_dict: dict):
    print("Iniciando a consolidação de todos os custos")

    if data_globals.LLM_AGENT2 is None:
        print(
            "ERRO CRÍTICO: LLM_AGENT2 não está configurado em data_globals. Não é possível gerar nomes de exibição via LLM."
        )
        return pd.DataFrame()

    df_colaboradores = None
    keys_to_process_as_items = list(dataframes_dict.keys())

    for key in list(dataframes_dict.keys()):
        if "colaboradores" in key.lower():
            df_colaboradores = dataframes_dict[key].copy()
            print(f"DataFrame de colaboradores principal identificado: '{key}'")
            if key in keys_to_process_as_items:
                keys_to_process_as_items.remove(key)
            break

    if df_colaboradores is None:
        print("ERRO CRÍTICO: DataFrame de colaboradores não encontrado.")
        return pd.DataFrame()
    if "CPF Colaborador" not in df_colaboradores.columns:
        print(
            "ERRO CRÍTICO: 'CPF Colaborador' não encontrado no DataFrame de colaboradores."
        )
        return pd.DataFrame()

    final_consolidated_df = df_colaboradores.copy()

    for df_key in keys_to_process_as_items:
        df_item_source = dataframes_dict[df_key]

        if df_item_source is None or df_item_source.empty:
            continue

        required_cols = ["CPF Colaborador", "Custo Mensal do Item"]
        if not all(col in df_item_source.columns for col in required_cols):
            print(
                f"AVISO (consolidate_llm): DataFrame '{df_key}' não possui '{', '.join(required_cols)}'. Ignorando."
            )
            continue

        display_name = _get_display_name_from_llm(df_key, data_globals.LLM_AGENT2)

        if not display_name:
            print(
                f"AVISO (consolidate_llm): Não foi possível gerar um nome de exibição via LLM para '{df_key}'. Ignorando este DataFrame."
            )
            continue

        print(
            f"Consolidando dados para '{display_name}' (derivado de '{df_key}' via LLM)"
        )

        final_consolidated_df = merge_cost_data(
            final_consolidated_df, df_item_source, display_name
        )

    print("Consolidação de custos (display names via LLM) concluída.")
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
