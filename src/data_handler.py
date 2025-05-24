import pandas as pd
import json
from pathlib import Path
import re


def standardize_dataframe(
    df: pd.DataFrame, file_name_stem: str, llm, canonical_names: dict
):
    standardized_df_original = df.copy()  # Copia para revertir en caso de error total
    original_columns = df.columns.str.strip().tolist()

    # Prompt mejorado para ser más estricto con la salida JSON
    prompt_template = f"""
    Sua tarefa é mapear colunas de um arquivo Excel para um conjunto de nomes de colunas padrão.
    O arquivo se chama '{file_name_stem}'.
    As colunas ORIGINAIS e EXATAS presentes neste arquivo são: {original_columns}. Use estes nomes EXATOS como chaves no JSON.

    Abaixo está a LISTA DE NOMES DE COLUNA PADRÃO VÁLIDOS (e suas descrições) para os quais você deve mapear as colunas originais. Use estes nomes EXATOS como valores no JSON:
    {json.dumps(canonical_names, ensure_ascii=False, indent=2)}

    Instruções CRÍTICAS para o mapeamento:
    1. Para CADA coluna da lista de colunas ORIGINAIS (`{original_columns}`), decida qual é o nome de coluna PADRÃO MAIS APROPRIADO da LISTA DE NOMES DE COLUNA PADRÃO VÁLIDOS.
    2. Dê FORTE PREFERÊNCIA a nomes padrão que sejam específicos para o tipo de arquivo (ex: se o nome do arquivo contém 'Unimed', prefira nomes padrão que contenham 'Unimed' sobre nomes genéricos, se aplicável e fizer sentido).
    3. Se uma coluna ORIGINAL NÃO TIVER um mapeamento claro, óbvio e apropriado para QUALQUER nome da LISTA DE NOMES DE COLUNA PADRÃO VÁLIDOS, você DEVE OMITIR essa coluna original do dicionário JSON de resposta. NÃO invente mapeamentos.

    Formato OBRIGATÓRIO da Resposta:
    Responda ÚNICA E EXCLUSIVAMENTE com um objeto JSON.
    As CHAVES do dicionário JSON DEVEM SER NOMES EXATOS da lista de colunas ORIGINAIS fornecida ({original_columns}).
    Os VALORES do dicionário JSON DEVEM SER NOMES EXATOS da LISTA DE NOMES DE COLUNA PADRÃO VÁLIDOS.
    NÃO inclua NENHUMA palavra, introdução, explicação, comentário, ou blocos de markdown como \`\`\`json ou \`\`\`.
    A sua resposta DEVE SER ESTRITAMENTE O DICIONÁRIO JSON, e nada mais.

    Exemplo de ÚNICA SAÍDA VÁLIDA (assumindo que as colunas originais eram ["Nome Completo do Funcionario", "Identificador CPF", "Valor da Ferramenta X", "Coluna Sem Mapeamento Claro"]):
    {{
        "Nome Completo do Funcionario": "Nome Colaborador",
        "Identificador CPF": "CPF Colaborador",
        "Valor da Ferramenta X": "Custo Mensal Github"
    }}
    (Neste exemplo, "Coluna Sem Mapeamento Claro" foi OMITIDA porque não tinha um bom mapeamento para um nome padrão VÁLIDO).
    """

    print(
        f"\n[Standardize] Solicitando mapeo de columnas al LLM para: {file_name_stem}"
    )
    response = llm.invoke(
        prompt_template
    )  # Asumiendo que llm.invoke funciona como antes

    mapping_dict = None  # Inicializar como None
    llm_output_content = (
        response.content if hasattr(response, "content") else str(response)
    )

    print(
        f"[Standardize] Resposta bruta do LLM para '{file_name_stem}':\n{llm_output_content}\n--------------------"
    )

    try:
        # Intentar extraer el JSON de la respuesta del LLM
        # 1. Buscar un bloque JSON dentro de ```json ... ``` o ``` ... ```
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
            # 2. Si no está en markdown, buscar el primer JSON object que abarca la mayor parte posible
            # Esto asume que el JSON es el objeto principal en la respuesta.
            match_direct = re.search(
                r"(\{[\s\S]*\})", llm_output_content
            )  # [\s\S]* para multilínea
            if match_direct:
                json_str = match_direct.group(1)
                print(
                    f"[Standardize] JSON extraído directamente para '{file_name_stem}': {json_str}"
                )
            else:
                # Si no se encuentra un patrón claro, se usa la respuesta tal cual,
                # esperando que el LLM haya seguido la instrucción de "SOLO JSON".
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

    # Procesamiento del DataFrame basado en mapping_dict
    if mapping_dict and isinstance(mapping_dict, dict):
        # Filtrar el mapeo para incluir solo las columnas originales que realmente existen en el DataFrame
        # y que tienen un nombre de columna estándar asignado que es un string.
        valid_rename_map = {
            original_col: standard_col
            for original_col, standard_col in mapping_dict.items()
            if original_col
            in standardized_df_original.columns  # La CLAVE del LLM es una columna original real
            and isinstance(standard_col, str)
            and standard_col  # El VALOR del LLM es un string no vacío
            and standard_col
            in canonical_names  # EL VALOR DEL LLM EXISTE EN NUESTROS CANONICAL_NAMES
        }

        if valid_rename_map:
            print(
                f"[Standardize] Mapeo válido a aplicar para '{file_name_stem}': {valid_rename_map}"
            )
            standardized_df = standardized_df_original.rename(columns=valid_rename_map)

            # Mantener solo las columnas que fueron mapeadas a un nombre estándar y existen
            final_standard_columns_set = set(valid_rename_map.values())
            existing_final_columns = [
                col
                for col in standardized_df.columns
                if col in final_standard_columns_set
            ]

            if existing_final_columns:
                # Asegurar el orden deseado si es relevante, o simplemente tomar las que existen
                # Para mantener el orden de la primera aparición de un valor estándar en el mapeo:
                ordered_final_columns = []
                seen_std_cols = set()
                for std_col_val in valid_rename_map.values():
                    if (
                        std_col_val not in seen_std_cols
                        and std_col_val in existing_final_columns
                    ):
                        ordered_final_columns.append(std_col_val)
                        seen_std_cols.add(std_col_val)

                if (
                    ordered_final_columns
                ):  # Si después de ordenar todavía tenemos columnas
                    standardized_df = standardized_df[ordered_final_columns]
                else:  # Si por alguna razón ordered_final_columns queda vacío pero existing_final_columns no lo estaba.
                    standardized_df = standardized_df[existing_final_columns]

                print(
                    f"Columnas en '{file_name_stem}' después de estandarización: {standardized_df.columns.tolist()}"
                )
            else:
                print(
                    f"Advertencia: Después del mapeo para '{file_name_stem}', ninguna de las columnas estándar resultantes existe. Usando columnas originales."
                )
                standardized_df = (
                    standardized_df_original  # Revertir si no hay columnas válidas
                )
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

    # El resto de tu lógica de strip (si aún es necesaria después del mapeo inteligente)
    cols_to_strip_data = ["CPF Colaborador", "Nome Colaborador"]  # Columnas estándar
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
