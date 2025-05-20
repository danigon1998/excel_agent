from src.agent_setup import setup_agent, run_agent_interaction


from dotenv import load_dotenv

load_dotenv()


def main():
    print("--- Configurando o Agente de Análise de Custos ---")
    try:
        agent_executor = setup_agent()
        print("Agente configurado com sucesso!")
    except ValueError as e:
        print(f"Erro na configuração do agente: {e}")
        print(
            "Por favor, verifique se a variável de ambiente GROQ_API_KEY está definida."
        )
        return
    run_agent_interaction(
        agent_executor,
        initial_query="Carregue os dados de 'data/input' e me diga o custo total por colaborador. Mostre as primeiras 5 linhas do DataFrame resultante.",
    )


# def main():
#     print("Iniciando Processo")

#     input_base_dir = Path("data/input")
#     loaded_dataframes = load_excel_files(input_base_dir)

#     if not loaded_dataframes:
#         print("Erro: Não foi possivel carregar nenhum arquivo.")
#         print(f"Rota usada: {input_base_dir}")
#         return

#     print("Chaves de DataFrames disponiveis:", list(loaded_dataframes.keys()))

#     print("Iniciando processo de consolidação e cálculo de custos")

#     consolidated_df = consolidate_all_cost(loaded_dataframes)

#     if consolidated_df.empty:
#         print("Erro: DataFrame consolidado está vazio.")
#         return
#     print("Consolidação e cálculo de custos concluídos")
#     print(consolidated_df.head())
#     print("Colunas do DataFrame Consolidado")
#     print(consolidated_df.columns.to_list())

#     final_cost_df = calculate_total_cost_per_collaborator(consolidated_df)

#     print("Vista Previa")
#     print(final_cost_df.head())
#     print("Processo concluído")
#     print(final_cost_df.columns.to_list())

#     print("Guardando o DataFrame final no arquivo Excel")
#     output_dir = Path("data/output")
#     output_filename = "Relatorio custos consolidados.xlsx"
#     output_path = output_dir / output_filename

#     saved_path = save_dataframe_to_excel(final_cost_df, output_path)

#     if saved_path:
#         print(f"DataFrame salvo com sucesso em {saved_path}.")
#     else:
#         print("Erro ao salvar o DataFrame.")


if __name__ == "__main__":
    main()
