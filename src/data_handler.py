import pandas as pd
import json
from pathlib import Path
import re
from src.prompts import get_standardize_dataframe_prompt


def standardize_dataframe(
    df: pd.DataFrame, file_name_stem: str, llm, canonical_names: dict
):
    standardized_df_original = df.copy()
    original_columns = df.columns.str.strip().tolist()

    prompt_template = get_standardize_dataframe_prompt(
        file_name_stem, original_columns, canonical_names
    )

    print(
        f"\n[Standardize] Solicitando mapeo de columnas al LLM para: {file_name_stem}"
    )
    response = llm.invoke(prompt_template)

    mapping_dict = None
    llm_output_content = (
        response.content if hasattr(response, "content") else str(response)
    )

    print(
        f"[Standardize] Resposta bruta do LLM para '{file_name_stem}':\n{llm_output_content}\n--------------------"
    )

    try:
        match_markdown = re.search(
            r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", llm_output_content
        )
        json_str = ""
        if match_markdown:
            json_str = match_markdown.group(1)
            print(
                f"[Standardize] JSON extraído de bloque markdown para '{file_name_stem}': {json_str}"
            )
        else:
            match_direct = re.search(r"(\{[\s\S]*\})", llm_output_content)
            if match_direct:
                json_str = match_direct.group(1)
                print(
                    f"[Standardize] JSON extraído directamente para '{file_name_stem}': {json_str}"
                )
            else:
                json_str = llm_output_content.strip()
                print(
                    f"[Standardize] Usando contenido bruto (strip) como JSON para '{file_name_stem}': {json_str}"
                )

        if json_str:
            mapping_dict = json.loads(json_str)
            print(
                f"[Standardize] Mapeo decodificado del LLM para '{file_name_stem}': {mapping_dict}"
            )
        else:
            print(
                f"Advertencia: No se pudo extraer una cadena JSON de la respuesta del LLM para '{file_name_stem}'."
            )

    except json.JSONDecodeError as e:
        print(
            f"Erro ao decodificar JSON da resposta do LLM para '{file_name_stem}': {e}. String que se intentó parsear: '{json_str}'"
        )
    except Exception as e:
        print(
            f"Erro inesperado ao processar resposta do LLM para '{file_name_stem}': {e}"
        )
    if mapping_dict and isinstance(mapping_dict, dict):
        valid_rename_map = {
            original_col: standard_col
            for original_col, standard_col in mapping_dict.items()
            if original_col in standardized_df_original.columns
            and isinstance(standard_col, str)
            and standard_col
            and standard_col in canonical_names
        }

        if valid_rename_map:
            print(
                f"[Standardize] Mapeo válido a aplicar para '{file_name_stem}': {valid_rename_map}"
            )
            standardized_df = standardized_df_original.rename(columns=valid_rename_map)

            final_standard_columns_set = set(valid_rename_map.values())
            existing_final_columns = [
                col
                for col in standardized_df.columns
                if col in final_standard_columns_set
            ]

            if existing_final_columns:
                ordered_final_columns = []
                seen_std_cols = set()
                for std_col_val in valid_rename_map.values():
                    if (
                        std_col_val not in seen_std_cols
                        and std_col_val in existing_final_columns
                    ):
                        ordered_final_columns.append(std_col_val)
                        seen_std_cols.add(std_col_val)

                if ordered_final_columns:
                    standardized_df = standardized_df[ordered_final_columns]
                else:
                    standardized_df = standardized_df[existing_final_columns]

                print(
                    f"Columnas en '{file_name_stem}' después de estandarización: {standardized_df.columns.tolist()}"
                )
            else:
                print(
                    f"Advertencia: Después del mapeo para '{file_name_stem}', ninguna de las columnas estándar resultantes existe. Usando columnas originales."
                )
                standardized_df = standardized_df_original
        else:
            print(
                f"Advertencia: No se generó un mapeo válido a partir de la respuesta del LLM para '{file_name_stem}'. Usando columnas originales."
            )
            standardized_df = standardized_df_original
    else:
        print(
            f"Advertencia: No se recibió ningún mapeo (o no es un diccionario) del LLM para '{file_name_stem}' o hubo un error de parseo. Usando columnas originales."
        )
        standardized_df = standardized_df_original

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
