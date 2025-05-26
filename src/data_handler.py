from pathlib import Path
import pandas as pd
import json
import re
from src.prompts import get_standardize_dataframe_prompt


def _extract_json_from_llm_output(llm_output_content: str, file_name_stem: str):
    """
    Extrai e parseia o JSON da string de resposta bruta do LLM.
    Inclui limpeza de comentários e vírgulas finais.
    """
    mapping_dict = None
    json_str = ""
    print(f"[JSON Extractor] Processando resposta para '{file_name_stem}'.")

    match_markdown = re.search(
        r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", llm_output_content
    )
    if match_markdown:
        json_str = match_markdown.group(1)
    else:
        match_direct = re.search(r"(\{[\s\S]*\})", llm_output_content)
        if match_direct:
            json_str = match_direct.group(1)
        else:
            json_str = llm_output_content.strip()

    if json_str:
        json_str_cleaned = re.sub(r"//.*", "", json_str)
        json_str_cleaned = re.sub(r",\s*([\}\]])", r"\1", json_str_cleaned.strip())

        try:
            mapping_dict = json.loads(json_str_cleaned)
        except json.JSONDecodeError as e:
            print(
                f"ERRO [JSON Extractor]: Erro ao decodificar JSON para '{file_name_stem}': {e}. String (limpa): '{json_str_cleaned}'"
            )
            mapping_dict = None
    else:
        print(
            f"ADVERTÊNCIA [JSON Extractor]: Não foi possível extrair uma string JSON da resposta do LLM para '{file_name_stem}'."
        )

    return mapping_dict


def _build_valid_rename_map(
    mapping_dict: dict, original_df_columns: list, canonical_names_keys: set
):
    """
    Constrói um mapa de renomeação válido a partir do dicionário do LLM,
    filtrando por colunas originais existentes e nomes canônicos válidos.
    """
    if not isinstance(mapping_dict, dict):
        print("ADVERTÊNCIA [Map Validator]: mapping_dict não é um dicionário.")
        return {}

    valid_map = {
        original_col: standard_col
        for original_col, standard_col in mapping_dict.items()
        if original_col in original_df_columns
        and isinstance(standard_col, str)
        and standard_col
        and standard_col in canonical_names_keys
    }
    return valid_map


def _apply_mapping_and_select_final_columns(
    original_df: pd.DataFrame, valid_rename_map: dict
):
    """
    Aplica o valid_rename_map ao DataFrame original, e então seleciona
    um conjunto único e ordenado de colunas canônicas.
    Retorna o DataFrame processado ou None se a seleção final de colunas falhar.
    """
    if not valid_rename_map:
        print("[Column Selector] Mapa de renomeação válido está vazio.")
        return None

    df_renamed = original_df.rename(columns=valid_rename_map)

    unique_target_columns_in_order = list(
        dict.fromkeys(
            std_col
            for std_col in valid_rename_map.values()
            if std_col in df_renamed.columns
        )
    )

    if unique_target_columns_in_order:
        processed_df = df_renamed[unique_target_columns_in_order]
        return processed_df
    else:
        return None


def _strip_data_from_selected_columns(df: pd.DataFrame, cols_to_strip: list):
    """
    Aplica strip em colunas de string especificadas do DataFrame.
    """
    df_stripped = df.copy()
    for col in cols_to_strip:
        if col in df_stripped.columns and df_stripped[col].dtype == "object":
            try:
                df_stripped[col] = df_stripped[col].astype(str).str.strip()
            except Exception as e:
                print(
                    f"ADVERTÊNCIA [Data Stripper]: Não se aplicou strip() na coluna '{col}'. Error: {e}"
                )
    return df_stripped


def standardize_dataframe(
    df: pd.DataFrame,
    file_name_stem: str,
    llm,
    canonical_names: dict,
):
    standardized_df_original = df.copy()
    original_columns = df.columns.str.strip().tolist()

    # 1. Obter o Prompt
    prompt_text = get_standardize_dataframe_prompt(
        file_name_stem, original_columns, canonical_names
    )
    print(
        f"\n[Standardize] Solicitando mapeio das colunas ao LLM para: {file_name_stem}"
    )

    # 2. Invocar o LLM
    response = llm.invoke(prompt_text)
    llm_output_content = (
        response.content if hasattr(response, "content") else str(response)
    )
    print(
        f"[Standardize] Resposta bruta do LLM para '{file_name_stem}':\n{llm_output_content}\n--------------------"
    )

    # 3. Extrair e Parsear JSON da resposta do LLM
    mapping_dict = _extract_json_from_llm_output(llm_output_content, file_name_stem)

    final_df = standardized_df_original

    if mapping_dict:
        # 4. Construir Mapa de Renomeação Válido
        valid_rename_map = _build_valid_rename_map(
            mapping_dict, original_columns, set(canonical_names.keys())
        )

        if valid_rename_map:
            # 5. Aplicar Mapeamento e Selecionar Colunas Finais
            processed_df = _apply_mapping_and_select_final_columns(
                standardized_df_original, valid_rename_map
            )

            if processed_df is not None and not processed_df.empty:
                final_df = processed_df
                print(
                    f"Colunas em '{file_name_stem}' depois da estandarização e seleção: {final_df.columns.tolist()}"
                )
            else:
                print(
                    f"ADVERTÊNCIA [Standardize]: Processamento do mapeio (rename/select) não produziu um DataFrame válido para '{file_name_stem}'. Usando DataFrame original (pode ter sido renomeado parcialmente se _apply_mapping falhou internamente mas devolveu original). Idealmente, revertemos ao 100% original."
                )
                final_df = standardized_df_original
        else:
            print(
                f"ADVERTÊNCIA [Standardize]: Não foi possível construir um mapa de renomeio válido para '{file_name_stem}' a partir da resposta do LLM. Usando DataFrame original."
            )
    else:
        print(
            f"ADVERTÊNCIA [Standardize]: Não foi recebido nenhum mapeio válido do LLM para '{file_name_stem}' (JSON malformado ou extração falhou). Usando DataFrame original."
        )

    cols_to_strip = ["CPF Colaborador", "Nome Colaborador"]
    final_df = _strip_data_from_selected_columns(final_df, cols_to_strip)

    return final_df


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
